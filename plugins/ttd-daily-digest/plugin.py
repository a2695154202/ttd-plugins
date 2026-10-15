# -*- coding: utf-8 -*-
"""TTD每日推送 · TgtoDrive Python 插件

把 TgtoDrive 的媒体库数据每天汇总成一条消息，推到 Telegram / 微信。

数据全部来自 TgtoDrive 自身的 OpenAPI（只读），**不需要填 Emby 地址或密钥**：
  * ``GET /api/emby/dashboard``    媒体库总量、总播放次数、活跃用户
  * ``GET /api/emby/latest``       最近入库媒体（用于「今日入库」与「新增数量统计」）
  * ``GET /api/emby/recent``       最近播放记录
  * ``GET /api/media/calendar``    追剧日历（当天播出的剧集）
  * ``GET /api/emby/trend``        播放趋势

通知渠道
  * **Telegram**：读 ``GET /api/notify-bots`` 拿已配置的通知机器人，直连 Bot API
    ``sendMessage``（凭据不落在本插件里）。
  * **微信**：通过 ``POST /api/toolbox/plugins/{wecom_plugin_id}/run`` 调用
    「企业微信通知」插件，走它的 ``envelope`` 契约；企业 ID / Secret / 收件人
    全部由那个插件自己保管，本插件不持有、也不传这些凭据。

两个渠道各自独立发送、各自报告结果：一个失败不影响另一个。

界面
  * 左侧 4 个分组卡片（通知渠道 / 推送板块 / 版式与条数 / 执行与接口），
    右侧 1 列放快捷按钮（发送测试推送、只预览不发送、正式推送一次、查看推送历史）。
  * 「执行操作」下拉框覆盖全部动作；按钮通过 ``params`` 覆盖它（两者是同一入口）。

实现要点
  * 只读：本插件**不调用任何写接口**，不会修改媒体库、不会改项目设置。
  * 板块独立容错：单个接口失败只影响该板块，会在报告末尾集中列出失败原因，
    其余板块照常推送 —— 绝不因为一个接口抖动就整天不发。
  * 微信侧文本消息不解析 Markdown，markdown 版式会自动清理标记后再发。
  * 推送记录写在 ``context["data_dir"]``，不写插件源码目录。

运行环境
  * python:3.13-slim 容器；仅标准库 + 容器已装的 ``requests``（不可用时回退 ``urllib``）。
  * 不安装依赖、不建虚拟环境、不导入 TgtoDrive 内部模块、不注册常驻服务。
"""

# ---------------------------------------------------------------------------
# 关于插件清单
# ---------------------------------------------------------------------------
# 本文件是**插件包内入口**：清单写在同目录的 plugin.json 里，这里不写
# PLUGIN_MANIFEST。打包时 scripts/package_plugin.py 会把 plugin.json 的内容
# 内联到 dist/ttd-daily-digest.py 的开头，生成可单独导入的单文件版。
#
# 若把本文件当作「Python 单文件」单独导入，TgtoDrive 会报
#   「Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典」
# 这是预期行为，不是插件损坏。请改用 dist/ttd-daily-digest.py 或 .zip。

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover - 仅在极简环境触发
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PLUGIN_ID = "ttd-daily-digest"
PLUGIN_NAME = "TTD每日推送"
SETTINGS_FILE = "settings.json"

DEFAULT_TGTO_BASE = "http://127.0.0.1:12366"
TELEGRAM_API = "https://api.telegram.org"

CONNECT_TIMEOUT = 8
READ_TIMEOUT = 20
TG_READ_TIMEOUT = 30

HISTORY_FILE = "history.json"
HISTORY_MAX_RECORDS = 400

# 北京时间（容器时区不保证，cron 也固定 Asia/Shanghai）
BEIJING = timezone(timedelta(hours=8))

USER_AGENT = "TgtoDrive-DailyDigest/1.0 (+https://github.com/a2695154202/ttd-plugins)"

VALID_FUNCS = ("digest", "preview", "test", "config", "history")

# 数据源定义：(键, 标题, 接口路径, 说明)
SECTION_DEFS = (
    ("stats", "媒体库总览", "/api/emby/dashboard"),
    ("added", "最近入库", "/api/emby/latest"),
    ("recent", "最近播放", "/api/emby/recent"),
    ("calendar", "追剧日历", "/api/media/calendar"),
    ("trend", "播放趋势", "/api/emby/trend"),
)

# 板块参数名 -> 板块键（清单里的开关）
SECTION_INPUTS = {
    "section_stats": "stats",
    "section_added": "added",
    "section_counts": "counts",
    "section_recent": "recent",
    "section_calendar": "calendar",
    "section_trend": "trend",
}


# ---------------------------------------------------------------------------
# 日志器
# ---------------------------------------------------------------------------

class _Log(object):
    """把日志同时打印到运行日志（stdout）并存进内存供结果页展示。"""

    def __init__(self, keep=400):
        self.lines = []
        self.keep = keep

    def _emit(self, level, message):
        line = "[%s] %s" % (level, message)
        print(line, flush=True)
        self.lines.append(line)
        if len(self.lines) > self.keep:
            del self.lines[: len(self.lines) - self.keep]

    def info(self, message):
        self._emit("INFO", message)

    def warn(self, message):
        self._emit("WARN", message)

    def error(self, message):
        self._emit("ERROR", message)

    def text(self):
        return "\n".join(self.lines) if self.lines else "（无日志）"


# ---------------------------------------------------------------------------
# 凭据脱敏
# ---------------------------------------------------------------------------

_SECRET_KEY_RE = re.compile(
    r"(?i)\b(corpsecret|corpid|appsecret|access_token|encodingaeskey|secret|token|password|passwd|pwd|apikey|api_key)\b"
    r"(\s*[=:]\s*)([^\s&\"',]+)"
)
_BOT_TOKEN_RE = re.compile(r"(/bot)(\d+:[A-Za-z0-9_\-]{10,})")


def scrub_text(value, secrets=()):
    """把文本里的凭据抹掉。

    网络库（requests / urllib）抛异常时会把**完整 URL** 写进错误消息：
    Telegram 的 bot token 在路径里（``/bot<id>:<token>/sendMessage``）、
    OpenAPI 令牌常在请求头或查询串里。这些都必须先脱敏再进日志。
    """
    text = str(value)
    for secret in secrets:
        if secret and len(str(secret)) >= 6:
            text = text.replace(str(secret), "***")
    text = _SECRET_KEY_RE.sub(lambda m: "%s%s***" % (m.group(1), m.group(2)), text)
    text = _BOT_TOKEN_RE.sub(lambda m: "%s%s:***" % (m.group(1), m.group(2)[:3]), text)
    return text


def mask_id(value, keep_head=4, keep_tail=2):
    """把企业 ID 之类的标识做掩码，便于在结果页确认「填的哪个」但不泄露全值。"""
    text = str(value or "")
    if len(text) <= keep_head + keep_tail:
        return "***" if text else ""
    return "%s***%s" % (text[:keep_head], text[-keep_tail:])


# ---------------------------------------------------------------------------
# 参数读取工具
# ---------------------------------------------------------------------------

def _s(params, key, default=""):
    value = params.get(key)
    if value is None:
        return default
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _b(params, key, default=False):
    value = params.get(key)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ("1", "true", "yes", "on", "是", "开")


def _i(params, key, default, low, high):
    value = params.get(key)
    if value is None or value == "":
        return default
    try:
        number = int(float(value))
    except (TypeError, ValueError):
        raise ValueError("参数 %s 必须是整数" % key)
    if not low <= number <= high:
        raise ValueError("参数 %s 必须在 %d ~ %d 之间" % (key, low, high))
    return number


def _list(params, key, default=None):
    value = params.get(key)
    if value is None or value == "":
        return list(default or [])
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    return [part.strip() for part in str(value).split(",") if part.strip()]


def _first_env_proxy():
    """取容器里配置的第一个代理地址（大小写都看），没有则返回空字符串。"""
    for key in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy",
                "HTTP_PROXY", "http_proxy"):
        value = (os.environ.get(key) or "").strip()
        if value:
            return value
    return ""


def mask_proxy(value):
    """代理地址脱敏：只保留协议与主机，隐藏可能的账号密码。

    两种形态都要认：``http://user:pass@host:port`` 与无协议的
    ``user:pass@host:port``（部分代理工具导出这种）。曾经只处理带 ``://`` 的形态，
    无协议地址原样返回，账号密码直接进运行日志。
    """
    text = str(value or "")
    if "@" in text:
        scheme, sep, rest = text.partition("://")
        if not sep:
            scheme, rest = "", text          # 无协议形态
        if rest:
            return "%s***@%s" % ("%s://" % scheme if scheme else "",
                                 rest.split("@", 1)[1])
    return text


# ---------------------------------------------------------------------------
# HTTP 工具：直连（显式绕过容器环境代理）
# ---------------------------------------------------------------------------

class _MaybeSentError(RuntimeError):
    """请求**可能已经送达对方**（读超时 / 响应中断）。

    连接被拒、连接超时 → 确定没发出去，换下一个代理重试安全；
    但**读超时**意味着请求已经到达 Telegram、消息可能已经发出，只是响应没在读回 ——
    这时换代理重发 = 用户收到两条。调用方遇到它必须**停止尝试**，按「状态未知」报告。
    """


def _is_read_timeout(exc):
    """判断异常是不是「读超时」—— 请求已送达对方、只是没读到响应。

    ``ConnectTimeout``（连接阶段失败）**不算**：那种情况确定没发出去，换代理重试安全。
    requests 的 ``ReadTimeout``、以及 urllib 路径的 ``socket.timeout`` /
    ``TimeoutError`` 都算（urllib 的 timeout 不区分连接与读取，保守按读超时处理）。
    """
    if requests is not None:
        try:
            if isinstance(exc, requests.exceptions.ConnectTimeout):
                return False
            if isinstance(exc, requests.exceptions.ReadTimeout):
                return True
        except Exception:
            pass
    return isinstance(exc, (TimeoutError, ))


class _Http(object):
    """极简 HTTP 客户端。

    为什么自己写：需要**显式绕开容器环境变量代理**。``requests`` 默认会读
    ``HTTP_PROXY`` / ``HTTPS_PROXY``，把请求送去代理后在 TLS 阶段被中断
    （表现为 ``SSLError ... UNEXPECTED_EOF_WHILE_READING``）。绕过的正确写法是
    给 ``proxies`` 同时给出 ``http`` 与 ``https`` 两个键（值哪怕是 ``None``）——
    requests 合并环境代理用的是 ``setdefault``，键存在才不会被覆盖。
    """

    def __init__(self, log, use_env_proxy=False):
        self.log = log
        self.use_env_proxy = use_env_proxy
        self._session = None

    def _proxies(self):
        if not self.use_env_proxy:
            return {"http": None, "https": None}
        return None

    def describe_mode(self):
        return "跟随环境变量代理" if self.use_env_proxy else "直连（绕过环境代理）"

    def request(self, method, url, headers=None, body=None, timeout=None,
                secrets=(), raw=False, proxy_override=None):
        """发一个请求，返回 (status, data)。

        ``data``：``raw=False`` 时为解析后的 JSON（失败给 None），
        ``raw=True`` 时为响应正文文本。
        网络异常会抛 ``RuntimeError``，消息已脱敏。

        ``proxy_override``：本次请求强制使用的代理地址；空字符串表示**强制直连**；
        ``None``（默认）表示按本客户端的 ``use_env_proxy`` 设置。Telegram 需要
        与 ttd 接口分开判断连通方式，因此单独提供这个口子。
        """
        timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
        if requests is not None:
            return self._request_requests(method, url, headers, body, timeout,
                                          secrets, raw, proxy_override)
        return self._request_urllib(method, url, headers, body, timeout,
                                    secrets, raw, proxy_override)

    def _override_proxies(self, proxy_override):
        """把 proxy_override 翻译成 requests 的 proxies 参数。"""
        if proxy_override is None:
            return self._proxies()
        if proxy_override == "":
            return {"http": None, "https": None}
        return {"http": proxy_override, "https": proxy_override}

    def _request_requests(self, method, url, headers, body, timeout,
                          secrets, raw, proxy_override=None):
        try:
            response = requests.request(
                method, url,
                headers=headers or {},
                data=body,
                timeout=timeout,
                proxies=self._override_proxies(proxy_override),
                allow_redirects=False,
            )
        except Exception as exc:
            # **读超时**要单独识别：请求已送达对方，重发会造成重复推送。
            # ConnectTimeout 是连接阶段失败（确定没发出去），归入普通 RuntimeError。
            if _is_read_timeout(exc):
                raise _MaybeSentError(scrub_text(
                    "%s: %s" % (type(exc).__name__, exc), secrets))
            raise RuntimeError(scrub_text("%s: %s" % (type(exc).__name__, exc),
                                          secrets))
        return self._parse(response.status_code, response.text, raw, secrets)

    def _request_urllib(self, method, url, headers, body, timeout,
                        secrets, raw, proxy_override=None):
        # urllib：ProxyHandler({}) 会禁用环境变量代理
        if proxy_override:
            handlers = [urllib.request.ProxyHandler(
                {"http": proxy_override, "https": proxy_override})]
        elif proxy_override == "" or not self.use_env_proxy:
            handlers = [urllib.request.ProxyHandler({})]
        else:
            handlers = []
        opener = urllib.request.build_opener(*handlers)
        request = urllib.request.Request(url, data=body, method=method)
        for key, value in (headers or {}).items():
            request.add_header(key, value)
        try:
            with opener.open(request, timeout=timeout[1]) as response:
                text = response.read().decode("utf-8", "replace")
                status = getattr(response, "status", 200)
        except urllib.error.HTTPError as exc:
            return self._parse(exc.code, exc.read().decode("utf-8", "replace"),
                               raw, secrets)
        except Exception as exc:
            # urllib 的 timeout 不区分连接/读取阶段，保守起见按「可能已送达」处理 ——
            # 宁可少换一档代理，也不能重复推送。
            message = scrub_text("%s: %s" % (type(exc).__name__, exc), secrets)
            if _is_read_timeout(exc):
                raise _MaybeSentError(message)
            raise RuntimeError(message)
        return self._parse(status, text, raw, secrets)

    @staticmethod
    def _parse(status, text, raw, secrets):
        if raw:
            return status, scrub_text(text, secrets)
        try:
            return status, json.loads(text)
        except Exception:
            return status, None


# ---------------------------------------------------------------------------
# TgtoDrive 客户端
# ---------------------------------------------------------------------------

class _Tdd(object):
    """TgtoDrive OpenAPI 客户端（只读 + 调用其他插件）。"""

    def __init__(self, log, base_url, token, http):
        self.log = log
        self.base_url = (base_url or DEFAULT_TGTO_BASE).rstrip("/")
        self.token = token or ""
        self.http = http

    @property
    def configured(self):
        return bool(self.token)

    def describe(self):
        token_note = ("令牌已填写（长度 %d）" % len(self.token)) if self.token \
            else "令牌未填写"
        return "%s ｜ %s" % (self.base_url, token_note)

    def _headers(self, json_body=False):
        headers = {
            "Authorization": "Bearer " + self.token,
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        }
        if json_body:
            headers["Content-Type"] = "application/json"
        return headers

    def get_json(self, path, params=None):
        """GET 一个 /api/... 接口，返回 (status, payload)。"""
        if not self.configured:
            raise RuntimeError("未配置 OpenAPI 令牌，无法调用 TgtoDrive 接口")
        url = self.base_url + path
        if params:
            clean = {k: v for k, v in params.items() if v not in (None, "")}
            if clean:
                url += "?" + urllib.parse.urlencode(clean)
        status, data = self.http.request(
            "GET", url, headers=self._headers(), secrets=[self.token])
        return status, data

    def post_json(self, path, payload):
        if not self.configured:
            raise RuntimeError("未配置 OpenAPI 令牌，无法调用 TgtoDrive 接口")
        status, data = self.http.request(
            "POST", self.base_url + path,
            headers=self._headers(json_body=True),
            body=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            secrets=[self.token],
        )
        return status, data

    def run_plugin(self, plugin_id, params):
        """提交一次插件运行任务，返回 (status, payload)。"""
        return self.post_json("/api/toolbox/plugins/%s/run" % plugin_id,
                              {"params": params})

    def plugin_job(self, job_id):
        """查询插件任务结果。"""
        return self.get_json("/api/toolbox/plugins/jobs/%s" % job_id)

    def plugin_manifest(self, plugin_id):
        """读取目标插件清单（用于发送前预校验参数是否被它接受）。"""
        status, data = self.get_json("/api/toolbox/plugins")
        if status != 200 or not isinstance(data, dict):
            return None
        items = data.get("plugins")
        if not isinstance(items, list):
            items = data.get("data") if isinstance(data.get("data"), list) else []
        for item in items:
            if isinstance(item, dict) and item.get("id") == plugin_id:
                return item
        return None


# ---------------------------------------------------------------------------
# 任务结果逐层下沉
# ---------------------------------------------------------------------------

def descend_result(data, depth=5):
    """把任务查询响应一路下沉到**最内层**的插件结果。

    ``GET /api/toolbox/plugins/jobs/{id}`` 没有响应 schema，任务对象可能被包在
    ``result`` / ``job`` / ``data`` / ``task`` 里的任意一层（甚至多层）。只取一层
    会读到「包裹本身」，把 ``delivery_ok`` 这类字段全丢掉 —— 历史上有两个插件
    因此把「没送达」显示成「已发送」。这里逐层下沉到底，并限制层数防止自引用。
    """
    node = data if isinstance(data, dict) else {}
    for _ in range(depth):
        child = None
        for key in ("result", "job", "data", "task"):
            value = node.get(key)
            if isinstance(value, dict) and value:
                child = value
                break
        if child is None:
            break
        node = child
    return node


# ---------------------------------------------------------------------------
# 数据采集
# ---------------------------------------------------------------------------

def _payload_data(payload):
    """从接口响应里取出数据主体（ttd 统一包在 ``data`` 里）。"""
    if isinstance(payload, dict):
        if "data" in payload:
            return payload.get("data")
        return payload
    return payload


class _Collector(object):
    """按板块采集数据。每个板块独立容错：失败只记录，不让整份报告失败。"""

    def __init__(self, log, tdd, options):
        self.log = log
        self.tdd = tdd
        self.opt = options
        self.data = {}
        self.errors = []      # [(板块标题, 原因)]
        self.empty = []       # 成功但无内容的板块标题

    # -- 单个接口 --------------------------------------------------------

    def _fetch(self, label, path, params=None):
        """取一个接口，返回 data（失败抛 RuntimeError，消息已可读）。"""
        try:
            status, payload = self.tdd.get_json(path, params)
        except Exception as exc:
            raise RuntimeError(str(exc))
        if status == 401:
            raise RuntimeError("HTTP 401：OpenAPI 令牌无效或未填写")
        if status == 403:
            raise RuntimeError("HTTP 403：令牌权限不足（该接口不可用）")
        if status != 200:
            raise RuntimeError("HTTP %s" % status)
        if payload is None:
            raise RuntimeError("响应不是 JSON（可能被重定向到登录页）")
        if isinstance(payload, dict) and payload.get("status") == "error":
            message = payload.get("message") or payload.get("error") or "接口返回错误"
            raise RuntimeError(str(message)[:200])
        return _payload_data(payload)

    # -- 各板块 ----------------------------------------------------------

    def collect_stats(self):
        data = self._fetch("媒体库总览", "/api/emby/dashboard")
        if not isinstance(data, dict):
            raise RuntimeError("响应结构不是对象")
        library = data.get("library") if isinstance(data.get("library"), dict) else {}
        return {
            "movie": _num(library.get("movie")),
            "series": _num(library.get("series")),
            "episode": _num(library.get("episode")),
            "total_plays": _num(data.get("total_plays")),
            "active_users": _num(data.get("active_users")),
            "total_duration": _num(data.get("total_duration")),
        }

    def collect_added(self):
        limit = self.opt["added_limit"]
        data = self._fetch("最近入库", "/api/emby/latest",
                           {"limit": str(limit)})
        rows = data if isinstance(data, list) else []
        items = []
        for row in rows[:limit]:
            if not isinstance(row, dict):
                continue
            items.append({
                "title": _series_title(row),
                "episode": _episode_label(row),
                "kind": _kind_of(row.get("Type")),
                "year": str(row.get("Year") or "").strip(),
            })
        return {"items": items, "total": len(items)}

    def collect_counts(self, added):
        """基于已取的「最近入库」按类型统计，不额外请求接口。"""
        movies = [x for x in added.get("items", []) if x["kind"] == "movie"]
        episodes = [x for x in added.get("items", []) if x["kind"] == "episode"]
        series = []
        for item in episodes:
            name = item["title"]
            if name and name not in series:
                series.append(name)
        return {
            "movie": len(movies),
            "series": len(series),
            "episode": len(episodes),
        }

    def collect_recent(self):
        limit = self.opt["list_limit"]
        data = self._fetch("最近播放", "/api/emby/recent")
        rows = data if isinstance(data, list) else []
        items = []
        for row in rows[:limit]:
            if not isinstance(row, dict):
                continue
            items.append({
                "name": str(row.get("DisplayName") or "").strip(),
                "user": str(row.get("UserName") or "").strip(),
            })
        return {"items": items, "total": len(items)}

    def collect_calendar(self):
        days = self.opt["calendar_days"]
        data = self._fetch("追剧日历", "/api/media/calendar", {"days": str(days)})
        if not isinstance(data, dict):
            raise RuntimeError("响应结构不是对象")
        if data.get("feed_status") and data.get("feed_status") != "ready":
            reason = data.get("feed_block_reason") or data.get("configuration_message") \
                or data.get("feed_status")
            raise RuntimeError("影视发现未就绪：%s" % str(reason)[:120])
        rows = data.get("items")
        rows = rows if isinstance(rows, list) else []
        limit = self.opt["list_limit"]
        items = []
        seen = set()
        for row in rows:
            if not isinstance(row, dict):
                continue
            title = str(row.get("title") or "").strip()
            if not title:
                continue
            key = (title, str(row.get("calendar_date") or ""))
            if key in seen:
                continue
            seen.add(key)
            episode = row.get("calendar_episode") \
                if isinstance(row.get("calendar_episode"), dict) else {}
            genres = row.get("genres") if isinstance(row.get("genres"), list) else []
            items.append({
                "title": title,
                "date": str(row.get("calendar_date") or "").strip(),
                "season": episode.get("season_number"),
                "episode": episode.get("episode_number"),
                "score": row.get("score"),
                "network": str(row.get("network") or "").strip(),
                "genres": [str(g) for g in genres][:3],
            })
            if len(items) >= limit:
                break
        return {"items": items, "total": len(items)}

    def collect_trend(self):
        data = self._fetch("播放趋势", "/api/emby/trend",
                           {"dimension": self.opt["trend_dimension"]})
        if not isinstance(data, dict):
            raise RuntimeError("响应结构不是对象")
        pairs = []
        for key, value in data.items():
            if isinstance(value, (int, float)):
                # 必须走 _num()：Python 的 json 默认接受 NaN / Infinity 字面量，
                # 直接 int() 会抛 ValueError / OverflowError —— 那不是 RuntimeError，
                # 会逃逸板块的 except 把整份日报炸掉（_num 的 docstring 专门防这个坑）。
                number = _num(value)
                if number is not None:
                    pairs.append((str(key), number))
        pairs.sort(key=lambda x: x[0])
        return {"items": pairs[-7:], "total": len(pairs)}

    # -- 采集全部 --------------------------------------------------------

    def run(self, enabled):
        """按启用的板块逐个采集，返回 ``self.data``。

        采集顺序有讲究：``counts``（新增数量统计）**依赖** ``added``（最近入库）
        的数据，所以先取 added，再就地补算 counts —— 不额外发一次请求。
        """
        self.log.info("开始采集数据，已启用板块：%s"
                      % "、".join(_label_of(key) for key in enabled))

        order = [k for k in ("added", "stats", "recent",
                             "calendar", "trend") if k in enabled]
        for key in order:
            label = _label_of(key)
            try:
                value = getattr(self, "collect_" + key)()
            except Exception as exc:
                # 兜 Exception 而不是只兜 RuntimeError：单个板块出**任何**意外
                #（NaN 转 int 的 ValueError、字段结构变化的 KeyError…）都不该把
                # 整份日报拖垮 —— 其余板块照常采集、推送。
                self.log.warn("板块「%s」数据获取失败：%s" % (label, exc))
                self.errors.append((label, str(exc)))
                continue
            self.data[key] = value
            if _is_empty(key, value):
                self.empty.append(label)
                self.log.info("板块「%s」暂无内容，报告中省略" % label)
            else:
                self.log.info("板块「%s」采集完成" % label)

        # 「新增数量统计」由「最近入库」就地补算，不额外请求接口
        if "counts" in enabled:
            label = _label_of("counts")
            added = self.data.get("added")
            if added is None and "added" not in enabled:
                # counts 勾了、added 没勾：**静默补采**一次（不进报告、不计入板块）。
                # 曾经直接挂一条错误「依赖最近入库但没取到」—— 两个开关在 UI 上
                # 相互独立，帮助文本还写着「不额外请求接口」，用户没义务知道这层依赖；
                # 叠加 only_when_content 时更会把配置错误伪装成「所有板块都没有内容」。
                self.log.info("「%s」需要「最近入库」的数据，本次顺带采集（不计入报告）"
                              % label)
                try:
                    added = self.collect_added()
                except Exception as exc:
                    self.log.warn("顺带采集「最近入库」失败：%s" % exc)
            if added is None:
                self.log.warn("板块「%s」跳过：它依赖「最近入库」，而后者没取到"
                              % label)
                self.errors.append((label, "依赖「最近入库」，但该板块没取到数据"))
            else:
                self.data["counts"] = self.collect_counts(added)
                if _is_empty("counts", self.data["counts"]):
                    self.empty.append(label)
                    self.log.info("板块「%s」暂无内容，报告中省略" % label)
                else:
                    self.log.info("板块「%s」采集完成：电影 %d 部、剧集 %d 部 / %d 集"
                                  % (label, self.data["counts"]["movie"],
                                     self.data["counts"]["series"],
                                     self.data["counts"]["episode"]))
        return self.data


def _num(value):
    """把接口里的数字字段转成 int，任何异常输入都退回 0。

    注意 ``float('nan')`` / ``float('inf')``：``int()`` 对它们会抛
    ``ValueError`` / ``OverflowError``（不是 TypeError），这里必须一并兜住 ——
    否则接口返回 NaN 时会在渲染阶段（``"%d" % value``）炸掉整份报告。
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        try:
            if value != value or value in (float("inf"), float("-inf")):
                return 0
            return int(value)
        except (ValueError, OverflowError, TypeError):
            return 0
    text = str(value or "").strip()
    if not text:
        return 0
    try:
        return int(text)
    except (TypeError, ValueError):
        pass
    # 再去掉千分位逗号 / 全角逗号后试一次（"1,234" -> 1234）
    compact = text.replace(",", "").replace("，", "")
    try:
        return int(compact)
    except (TypeError, ValueError):
        pass
    # 最后取前缀数字（"12abc" -> 12；"3.9 部" -> 3）
    match = re.match(r"[-+]?\d+(?:\.\d+)?", compact)
    if match:
        try:
            return int(float(match.group(0)))
        except (TypeError, ValueError, OverflowError):
            return 0
    return 0


def _kind_of(kind):
    text = str(kind or "").strip().lower()
    if text in ("movie", "movies", "电影"):
        return "movie"
    if text in ("episode", "episodes", "剧集", "单集"):
        return "episode"
    if text in ("series", "tvshows", "show"):
        return "series"
    return text or "other"


def _series_title(row):
    """入库条目的「标题」：剧集取 SeriesName，电影取 Name。"""
    kind = _kind_of(row.get("Type"))
    series = str(row.get("SeriesName") or "").strip()
    name = str(row.get("Name") or "").strip()
    if kind == "episode" and series:
        return series
    return name or series


def _episode_label(row):
    """从入库条目里提取集号，取不到就回退到原始 Name（截断）。"""
    kind = _kind_of(row.get("Type"))
    if kind != "episode":
        return ""
    name = str(row.get("Name") or "").strip()
    match = re.search(r"S(\d{1,2})E(\d{1,3})", name, re.I)
    if match:
        return "S%sE%s" % (match.group(1).zfill(2), match.group(2).zfill(2))
    match = re.search(r"第\s*(\d{1,4})\s*[集话話期]", name)
    if match:
        return "第%s集" % match.group(1)
    match = re.search(r"\bE(\d{1,3})\b", name, re.I)
    if match:
        return "E%s" % match.group(1).zfill(2)
    return name[:24]


def _label_of(key):
    if key == "counts":
        return "新增数量统计"
    for section_key, label, _path in SECTION_DEFS:
        if section_key == key:
            return label
    return key


def _is_empty(key, value):
    if value is None:
        return True
    if key in ("stats",):
        return not any(value.get(k) for k in ("movie", "series", "episode",
                                              "total_plays"))
    if key in ("counts",):
        return not any(value.get(k) for k in ("movie", "series", "episode"))
    if isinstance(value, dict):
        items = value.get("items")
        if isinstance(items, (list, tuple)):
            return len(items) == 0
    return False


def _report_has_body(report):
    """渲染结果里除标题行 / 分隔线 / 空行外，是否还有**正文**。

    第一行是标题（插件名 + 时间），不算正文。用于纠正「数据非空 ≠ 有内容可读」：
    compact 版式下列表类板块不渲染明细，只勾这些板块时 raw 数据非空、渲染出来
    却只有标题行 + 分隔线 —— 这种「空壳日报」推出去不如跳过。
    """
    lines = str(report or "").split("\n")
    for text in lines[1:]:
        text = text.strip()
        if not text:
            continue
        if set(text) <= set("─—━-_=* "):     # 分隔线
            continue
        return True
    return False


# ---------------------------------------------------------------------------
# 报告渲染
# ---------------------------------------------------------------------------

class _Renderer(object):
    """把采集到的数据渲染成消息文本。

    三种版式：
      * ``text``     —— 纯文本 + 分隔线，任何渠道都不错乱（默认）
      * ``markdown`` —— Telegram 排版好看；微信侧发送前会清理标记
      * ``compact``  —— 只保留统计数字，不展开明细
    """

    def __init__(self, options):
        self.opt = options
        self.fmt = options["msg_format"]

    # -- 基础样式 --------------------------------------------------------

    def _h(self, text):
        """小标题。"""
        if self.fmt == "markdown":
            return "**%s**" % text
        return "【%s】" % text

    def _kv(self, key, value):
        if self.fmt == "markdown":
            return "- %s：%s" % (key, value)
        return "· %s：%s" % (key, value)

    def _item(self, text):
        if self.fmt == "markdown":
            return "- %s" % text
        return "· %s" % text

    def _rule(self):
        return "──────────"

    # -- 头部 ------------------------------------------------------------

    def header(self, sections_count):
        now = datetime.now(BEIJING)
        title = self.opt["title_prefix"] or PLUGIN_NAME
        line = title
        if self.opt["include_time"]:
            line += " · %s" % now.strftime("%m-%d %H:%M")
        else:
            line += " · %s" % now.strftime("%m-%d")
        return line

    # -- 各板块 ----------------------------------------------------------

    def stats(self, data):
        lines = [self._h("媒体库总览")]
        lines.append(self._kv("电影", "%d 部" % data["movie"]))
        lines.append(self._kv("剧集", "%d 部" % data["series"]))
        lines.append(self._kv("单集", "%d 集" % data["episode"]))
        if data.get("total_plays"):
            lines.append(self._kv("总播放", "%d 次" % data["total_plays"]))
        if data.get("active_users"):
            lines.append(self._kv("活跃用户", "%d 人" % data["active_users"]))
        return lines

    def counts(self, data):
        # 标题必须如实：这个板块统计的是 /api/emby/latest 返回的**最近 N 条入库**
        # （N=added_limit，默认 10），既没按入库日期过滤、也不受「今天」约束 ——
        # 写成「今日新增」是假数据（当天零入库也可能推出「今日新增 3 部」）。
        # 插件自己的帮助文本承诺过「不会谎称是今日新增」，这里不能再犯。
        lines = [self._h("最近入库统计")]
        lines.append(self._kv("电影", "%d 部" % data["movie"]))
        lines.append(self._kv("剧集", "%d 部（新增 %d 集）"
                              % (data["series"], data["episode"])))
        return lines

    def added(self, data):
        items = data.get("items") or []
        if self.fmt == "compact":
            return []
        lines = [self._h("最近入库（%d 条）" % len(items))]
        for item in items:
            text = item["title"] or "（未命名）"
            if item["episode"]:
                text += " · %s" % item["episode"]
            if item["year"]:
                text += "（%s）" % item["year"]
            lines.append(self._item(text))
        return lines

    def recent(self, data):
        items = data.get("items") or []
        if self.fmt == "compact":
            return []
        lines = [self._h("最近播放")]
        for item in items:
            text = item["name"] or "（未命名）"
            if item["user"]:
                text += " — %s" % item["user"]
            lines.append(self._item(text))
        return lines

    def calendar(self, data):
        items = data.get("items") or []
        if self.fmt == "compact":
            return []
        lines = [self._h("今日更新（%d 部）" % len(items))]
        for item in items:
            text = item["title"]
            season, episode = item.get("season"), item.get("episode")
            if episode is not None:
                # season 为 0 或 None 时（动漫常用「第0季」表示单季/特别篇）
                # 只显示集号，避免出现 S00E80 这种别扭的写法
                if season in (None, 0, "0"):
                    text += " · 第%s集" % episode
                else:
                    text += " · S%sE%s" % (str(season).zfill(2),
                                           str(episode).zfill(2))
            extra = []
            if item.get("score"):
                extra.append("评分 %s" % item["score"])
            if item.get("network"):
                extra.append(item["network"])
            if item.get("genres"):
                extra.append("/".join(item["genres"]))
            if extra:
                text += "（%s）" % " · ".join(extra)
            lines.append(self._item(text))
        return lines

    def trend(self, data):
        items = data.get("items") or []
        if self.fmt == "compact":
            return []
        lines = [self._h("播放趋势")]
        for key, value in items:
            lines.append(self._item("%s：%d" % (key, value)))
        return lines

    # -- 组装 ------------------------------------------------------------

    def render(self, collected, enabled, errors):
        blocks = []
        # 固定顺序，保证每天版式一致
        order = ("stats", "counts", "added", "calendar",
                 "recent", "trend")
        for key in order:
            if key not in enabled or key not in collected:
                continue
            method = getattr(self, key, None)
            if method is None:
                continue
            try:
                lines = method(collected[key])
            except Exception as exc:  # 渲染失败不该毁掉整份报告
                lines = [self._h(_label_of(key)), self._item("渲染失败：%s" % exc)]
            if lines:
                blocks.append("\n".join(lines))

        body = ("\n" + self._rule() + "\n").join(blocks)
        head = self.header(len(blocks))
        text = head + "\n" + self._rule() + "\n" + body

        if errors:
            notes = [self._h("未取到的板块")]
            for label, reason in errors:
                notes.append(self._item("%s：%s" % (label, reason)))
            text += "\n" + self._rule() + "\n" + "\n".join(notes)
        if self.fmt == "markdown":
            pass
        return text


_MD_MARKS = (
    ("**", ""),
    ("__", ""),
    ("```", ""),
    ("`", ""),
)


def strip_markdown(text):
    """把 Markdown 标记清掉（微信文本消息不解析 Markdown，留着会显示 `**`）。"""
    out = text
    for source, target in _MD_MARKS:
        out = out.replace(source, target)
    # 行首的 "- " 列表符号换成更通用的圆点
    out = re.sub(r"(?m)^-\s+", "· ", out)
    return out


# ---------------------------------------------------------------------------
# 通知渠道
# ---------------------------------------------------------------------------

def _collect_bots(payload, source):
    """从 /api/notify-bots（或 /api/proxy_settings）的响应里启发式找出机器人。

    该接口的响应规范标 ``generic``（字段名不确定），历史上确认过几种形态：
    顶层列表、``data.list``、``settings`` 包裹、扁平对象。这里统一兼容，
    并从各种可能的键名里取 Token 与推送目标。
    """
    bots = []
    skipped = []

    def consider(node, index):
        if not isinstance(node, dict):
            return
        name = None
        for key in ("name", "remark", "title", "label", "bot_name"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                name = value.strip()
                break
        token = None
        for key in ("token", "bot_token", "botToken", "tg_token", "telegram_token"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                token = value.strip()
                break
        chat_id = None
        for key in ("chat_id", "chatId", "user_id", "admin_user_id", "target",
                    "target_id", "to", "receiver"):
            value = node.get(key)
            if value not in (None, "") and not isinstance(value, (dict, list)):
                chat_id = str(value).strip()
                break
        proxy = None
        for key in ("proxy", "proxy_url", "proxyUrl"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                proxy = value.strip()
                break
        kind = str(node.get("type") or node.get("bot_type")
                   or node.get("provider") or "").strip().lower()
        if not name:
            name = "机器人 %d" % index
        if not token or not chat_id:
            skipped.append(name)
            return
        # 类型明确写着非 Telegram（如企业微信）时排除
        if kind and ("wecom" in kind or "wechat" in kind or "work" in kind
                     or "qy" in kind):
            skipped.append(name)
            return
        if token and ":" not in token:
            # Telegram bot token 形如 123456:ABC-DEF...；不带冒号的通常不是
            skipped.append(name)
            return
        bots.append({"name": name, "token": token, "chat_id": chat_id,
                     "proxy": proxy, "type": kind, "source": source})

    if isinstance(payload, list):
        for index, node in enumerate(payload, 1):
            consider(node, index)
    elif isinstance(payload, dict):
        candidates = []
        for key in ("list", "bots", "items", "data", "settings", "notify_bots"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates = value
                break
            if isinstance(value, dict):
                inner = None
                for inner_key in ("list", "bots", "items"):
                    if isinstance(value.get(inner_key), list):
                        inner = value.get(inner_key)
                        break
                if inner is not None:
                    candidates = inner
                    break
        if not candidates and any(
                isinstance(payload.get(k), str) and payload.get(k)
                for k in ("token", "bot_token", "botToken")):
            candidates = [payload]
        for index, node in enumerate(candidates, 1):
            consider(node, index)
    return bots, skipped


def _is_primary_name(name):
    text = str(name or "").strip().lower()
    return text in ("主", "主机器人", "main", "primary", "默认", "default") \
        or "主" in text


class _TelegramChannel(object):
    """直接调用 Telegram Bot API 发送（凭据来自 ttd 已配置的机器人）。"""

    key = "tg"
    label = "Telegram"

    def __init__(self, log, tdd, options, http):
        self.log = log
        self.tdd = tdd
        self.opt = options
        self.http = http

    def candidates(self):
        bots = []
        skipped = []
        seen = set()
        for path in ("/api/notify-bots", "/api/proxy_settings"):
            try:
                status, payload = self.tdd.get_json(path)
            except Exception as exc:
                self.log.warn("读取 %s 失败：%s" % (path, exc))
                continue
            if status != 200 or payload is None:
                self.log.warn("读取 %s 返回 HTTP %s" % (path, status))
                continue
            found, dropped = _collect_bots(payload, path)
            for bot in found:
                key = (bot["token"], bot["chat_id"])
                if key in seen:
                    continue
                seen.add(key)
                bots.append(bot)
            for name in dropped:
                if name not in skipped:
                    skipped.append(name)
            if bots:
                break
        for index, bot in enumerate(bots, 1):
            bot["index"] = index
        return bots, skipped

    def ttd_proxy(self):
        """读 ttd「网络代理」设置里实际生效的代理地址。

        ttd 的 ``/api/proxy_settings`` 会给出 ``effective_proxy`` / ``runtime``，
        这是用户真正配好、通常能通 Telegram 的那个代理（常与容器的环境变量
        代理**不是同一个**）。容器环境里的 ``HTTP_PROXY`` 往往是平台侧注入的
        内部代理，未必能出网到 ``api.telegram.org``，所以必须优先用 ttd 自己的。
        读不到就返回空字符串。
        """
        for path in ("/api/proxy_settings", "/api/proxy-settings"):
            try:
                status, payload = self.tdd.get_json(path)
            except Exception as exc:
                self.log.warn("读取 %s 失败：%s" % (path, exc))
                continue
            if status != 200 or not isinstance(payload, dict):
                continue
            node = payload
            data = payload.get("data")
            if isinstance(data, dict):
                node = data
            for key in ("effective_proxy", "web_proxy", "proxy", "proxy_url"):
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    return value.strip()
            for key in ("runtime", "proxies"):
                block = node.get(key)
                if isinstance(block, dict):
                    for sub in ("https", "http"):
                        value = block.get(sub)
                        if isinstance(value, str) and value.strip():
                            return value.strip()
        return ""

    def select(self, bots):
        """按「Telegram 机器人」参数挑选。"""
        usable = [b for b in bots if b["token"] and b["chat_id"]]
        selection = self.opt["notify_bot"]

        if selection.startswith("index:"):
            try:
                wanted = int(selection.split(":", 1)[1])
            except (TypeError, ValueError):
                wanted = 0
            target = next((b for b in bots if b["index"] == wanted), None)
            if target and target["token"] and target["chat_id"]:
                return target
            if target is not None:
                self.log.warn("「列表第 %d 个」机器人（%s）缺少 Token 或推送目标，"
                              "改用主机器人" % (wanted, target.get("name") or "-"))
            else:
                self.log.warn("配置中只有 %d 个机器人，不存在「列表第 %d 个」，"
                              "改用主机器人" % (len(bots), wanted))

        primary = next((b for b in usable if _is_primary_name(b["name"])), None)
        if primary is not None:
            return primary
        return usable[0] if usable else None

    def send(self, text):
        """返回 (ok, 说明)。"""
        bots, skipped, read_errors = self.candidates()
        if skipped:
            self.log.info("已排除 %d 个非 Telegram / 缺凭据的条目：%s"
                          % (len(skipped), "、".join(skipped[:6])))
        if not bots:
            if read_errors:
                return False, ("读取 ttd 的「通知机器人」接口失败（%s）—— "
                               "无法确认有没有配机器人；这通常是 ttd 接口暂时不可达"
                               "或令牌问题，不是没配机器人"
                               % "；".join(read_errors[:2]))
            return False, ("在 ttd 里没读到可用的 Telegram 通知机器人"
                           "（检查「通知机器人」设置是否配了 Token 与推送目标）")
        bot = self.select(bots)
        if bot is None:
            return False, "读到的机器人条目都缺少 Token 或推送目标"
        self.log.info("使用 Telegram 机器人「%s」（列表第 %s 项，来源 %s）"
                      % (bot["name"], bot["index"], bot["source"]))

        payload = json.dumps({
            "chat_id": bot["chat_id"],
            "text": text,
            "disable_web_page_preview": True,
            "disable_notification": False,
        }, ensure_ascii=False).encode("utf-8")

        # Telegram 的连通策略与 ttd 接口**不同**，要分开判断：
        #   * ttd 地址通常是内网/本机（如 192.168.x.x:12366），必须直连 —— 走代理会失败；
        #   * api.telegram.org 在多数中国大陆网络下**必须经代理**才能访问。
        # 因此这里不沿用「网络代理」开关，而是按下面的顺序择优：
        #   ① ttd「网络代理」设置里生效的代理（用户真正配好、最可能通 Telegram 的）
        #   ② 机器人自带代理  →  ③ 容器环境变量代理  →  ④ 直连
        # 「① vs ③」的区别很重要：容器里的 HTTP_PROXY 常是平台侧注入的内部代理，
        # 未必能出网；ttd 自己配的代理才是用户确认过能用的。
        attempts = []
        bot_proxy = (bot.get("proxy") or "").strip()
        ttd_proxy = self.ttd_proxy()
        env_proxy = _first_env_proxy()

        def _push(proxy, label):
            if proxy and all(proxy != item[0] for item in attempts):
                attempts.append((proxy, label))

        if ttd_proxy:
            _push(ttd_proxy, "ttd 网络代理设置")
        if bot_proxy:
            _push(bot_proxy, "机器人自带代理")
        if self.opt["proxy_mode"] == "env":
            _push(env_proxy, "容器环境变量代理（按你的设置）")
        elif env_proxy:
            # 默认「直连」指的是 ttd 接口直连；Telegram 仍优先尝试环境代理，
            # 因为本机直连 Telegram 常被重置（WinError 10054）
            _push(env_proxy, "容器环境变量代理")
        # 直连始终作为最后一档兜底（哪怕设了「网络代理」，多试一次好过直接报错）
        attempts.append(("", "直连"))

        self.log.info("Telegram 连通方式备选 %d 种：%s"
                      % (len(attempts), " → ".join(label for _, label in attempts)))

        # 这几个状态码来自代理/网关本身，说明请求**没到 Telegram**，
        # 换下一个代理重试是安全的（不会重复推送）。
        proxy_layer_status = (407, 502, 503, 504, 520, 521, 522, 523, 524)

        last_error = ""
        for proxy, label in attempts:
            if proxy:
                self.log.info("尝试经「%s」访问 Telegram（%s）" % (mask_proxy(proxy), label))
            else:
                self.log.info("尝试直连 Telegram（不走代理）")
            try:
                status, data = self.http.request(
                    "POST", "%s/bot%s/sendMessage" % (TELEGRAM_API, bot["token"]),
                    headers={"Content-Type": "application/json",
                             "User-Agent": USER_AGENT},
                    body=payload,
                    timeout=(CONNECT_TIMEOUT, TG_READ_TIMEOUT),
                    secrets=[bot["token"]],
                    proxy_override=proxy,
                )
            except _MaybeSentError as exc:
                # 读超时：请求已到达 Telegram，消息**可能已经发出** —— 绝不能换代理
                # 重发（那会重复推送），也不能再试直连。按「状态未知」如实报告。
                self.log.warn("经「%s」发送时读超时（请求可能已送达，不重试）：%s"
                              % (label, exc))
                return None, ("状态未知：请求已发出但在 %d 秒内没有读到 Telegram 的响应"
                              "（经%s）—— 消息可能已送达，请先到 Telegram 确认，"
                              "不要直接重试（重复推送）" % (TG_READ_TIMEOUT, label))
            except RuntimeError as exc:
                # 连接失败 / 连接超时：确定没发出去，换下一种方式重试。
                last_error = "%s（%s）" % (exc, label)
                self.log.warn("经「%s」发送失败：%s" % (label, exc))
                continue
            # 已经拿到 HTTP 响应，但要区分两种情况：
            #   * 代理/网关层错误（502/503/504/407）—— 说明**没到 Telegram**，
            #     换下一个代理再试是安全的；
            #   * Telegram 自己的响应（200/400/401/403/429…）—— 必须立刻停，
            #     换代理重发会造成重复推送。
            if status in proxy_layer_status:
                where = "来自代理/网关" if proxy else "网关层（直连也被中间设备拦下）"
                last_error = "HTTP %s（%s，%s）" % (status, label, where)
                self.log.warn("经「%s」访问 Telegram 返回 HTTP %s（代理层错误），换下一种方式"
                              % (label, status))
                continue
            return self._interpret(status, data, bot)

        hint = ""
        if not ttd_proxy:
            hint = ("；提示：ttd「设置 → 网络代理」里没配代理，若你的网络需要代理才能访问 "
                    "Telegram，请先在 ttd 里配好")
        return False, "连接 Telegram 失败，已依次尝试 %d 种方式：%s%s" \
                      % (len(attempts), last_error, hint)

    @staticmethod
    def _interpret(status, data, bot):
        """把 Telegram 的响应翻译成 (ok, 说明)。

        **HTTP 200 也必须校验响应体**：透明代理 /  captive portal 会返回 200 + HTML，
        ``_parse`` 解析不出 JSON 时 data 为 None —— 曾经这种情况直接判「已发送」，
        用户永远收不到日报却显示成功。Telegram 的正常响应一定带 ``ok`` 字段，
        收不到它就是没发成。
        """
        if status != 200:
            description = ""
            if isinstance(data, dict):
                description = str(data.get("description") or "")[:160]
            hint = ""
            if status == 401:
                hint = "（Token 无效）"
            elif status == 400 and "chat not found" in description.lower():
                hint = "（推送目标 ID 不对，或该用户未与机器人对话过）"
            elif status == 403:
                hint = "（机器人被用户屏蔽，或无法主动发起对话）"
            return False, "Telegram 返回 HTTP %s%s %s" % (status, hint, description)
        if not isinstance(data, dict) or "ok" not in data:
            return False, ("Telegram 返回了无法解析的响应（HTTP 200，非 JSON）—— "
                           "按失败处理：可能是代理捕获页，消息并未送达")
        if data.get("ok") is not True:
            return False, "Telegram 拒绝了这条消息：%s" % str(
                data.get("description") or "")[:160]
        message_id = ""
        result = data.get("result")
        if isinstance(result, dict):
            message_id = str(result.get("message_id") or "")
        return True, "已发送（机器人「%s」%s）" % (
            bot["name"], "message_id=%s" % message_id if message_id else "")


class _WecomChannel(object):
    """通过调用「企业微信通知」插件发送（凭据由对方保管）。"""

    key = "wecom"
    label = "微信"

    def __init__(self, log, tdd, options, http):
        self.log = log
        self.tdd = tdd
        self.opt = options
        self.http = http

    def send(self, text):
        """返回 (ok, 说明)。"""
        plugin_id = self.opt["wecom_plugin_id"] or "wecom-notify"

        # 发送前先读目标插件清单，确认它装了、启用、且支持 envelope
        manifest = None
        read_error = ""
        try:
            manifest = self.tdd.plugin_manifest(plugin_id)
        except Exception as exc:
            # 读不到清单 ≠ 插件没装：OpenAPI 临时不可达、令牌失效都会走到这。
            # 曾经统称「没在 ttd 里找到插件」，用户按提示去重装，方向完全错误。
            read_error = str(exc)[:160]
            self.log.warn("读取插件清单失败（继续尝试发送）：%s" % read_error)

        if manifest is None:
            if read_error:
                return False, ("读取插件「%s」的清单失败（%s）—— 无法确认它是否安装；"
                               "这通常是 ttd 接口暂时不可达或令牌问题，不是插件没装"
                               % (plugin_id, read_error))
            return False, ("没在 ttd 里找到插件「%s」—— 请确认已安装并启用"
                           "（或把「微信通知插件 id」改成你实际用的那个）" % plugin_id)
        if manifest.get("enabled") is False:
            return False, "插件「%s」已安装但处于停用状态，请先启用" % plugin_id

        names = manifest.get("inputs") or []
        declared = {item.get("name") for item in names if isinstance(item, dict)}
        if "envelope" not in declared:
            return False, ("插件「%s」不支持 envelope 参数（版本过旧）—— "
                           "请到插件市场把它更新到最新版" % plugin_id)

        envelope = {
            "version": 1,
            "msgtype": "text",
            "content": strip_markdown(text) if self.opt["msg_format"] != "text"
                       else text,
            "source": PLUGIN_NAME,
        }
        # 只在用户确实填了非空值时才传 touser，否则沿用对方的设置
        # （传空值会被平台的「默认值填齐」行为顶成 @all）
        touser = (self.opt["wecom_touser"] or "").strip()
        if touser:
            envelope["touser"] = touser
            self.log.info("本次将覆盖微信收件人为：%s" % touser)
        else:
            self.log.info("未指定微信收件人，沿用「%s」里已保存的设置" % plugin_id)

        params = {"func": "send", "envelope": json.dumps(envelope,
                                                         ensure_ascii=False)}
        # 平台的队列限制：同一插件同时只能有一个未完成任务，忙碌时返回 409。
        # 这里做有限重试（最多 3 次、间隔 3 秒），因为对方的任务通常很快结束。
        status, payload = 0, None
        for attempt in range(3):
            try:
                status, payload = self.tdd.run_plugin(plugin_id, params)
            except Exception as exc:
                return False, "提交任务失败：%s" % exc
            if status != 409:
                break
            detail = ""
            if isinstance(payload, dict):
                detail = str(payload.get("error") or payload.get("message") or "")
            if attempt < 2:
                self.log.warn("目标插件正忙（HTTP 409：%s），3 秒后重试（第 %d/3 次）"
                              % (detail or "队列忙", attempt + 2))
                time.sleep(3)
            else:
                return False, ("目标插件持续处于忙碌状态（HTTP 409：%s）—— "
                               "它的上一个任务还没跑完，稍后再试"
                               % (detail or "队列忙"))

        if status == 404:
            return False, "目标插件未找到（HTTP 404）—— 未安装或未启用"
        if status in (401, 403):
            return False, ("HTTP %s：OpenAPI 令牌无效或权限不足" % status)
        if status == 400:
            detail = ""
            if isinstance(payload, dict):
                detail = str(payload.get("message") or payload.get("error") or "")[:160]
            return False, ("HTTP 400：参数被拒（%s）—— "
                           "通常是目标插件版本过旧" % (detail or "未知参数"))
        if status == 503:
            return False, "HTTP 503：插件队列已满或对方有未完成任务，稍后重试"
        if status not in (200, 201, 202):
            return False, "提交任务返回 HTTP %s" % status
        if not isinstance(payload, dict):
            return False, "任务响应不是 JSON"

        job_id = payload.get("job_id") or payload.get("id") or payload.get("jobId")
        if not job_id:
            # 有些版本会把任务对象包一层，这里也试着下沉一次
            inner = descend_result(payload)
            if inner is not payload:
                job_id = inner.get("job_id") or inner.get("id") or inner.get("jobId")
        if not job_id:
            return True, "任务已受理（未取到 job_id，无法确认投递结果）"

        self.log.info("微信通知任务已提交，job_id=%s，开始等待结果…" % job_id)
        deadline = time.time() + 60
        last = ""
        seen_state = ""
        while time.time() < deadline:
            try:
                code, job = self.tdd.plugin_job(job_id)
            except Exception as exc:
                last = "查询任务失败：%s" % exc
                time.sleep(2)
                continue
            if code != 200 or not isinstance(job, dict):
                last = "查询任务返回 HTTP %s" % code
                time.sleep(2)
                continue
            result = descend_result(job)
            state = str(result.get("status") or result.get("state") or "").lower()
            if state:
                seen_state = state
            if state in ("ok", "success", "failed", "error", "timeout"):
                if state not in ("ok", "success"):
                    return False, "目标插件执行失败：%s" % (
                        str(result.get("error") or result.get("message")
                            or "未说明原因")[:200])
                # 必须看投递结论：企业微信对不可见收件人仍返回成功
                if result.get("delivery_ok") is False:
                    detail = result.get("delivery_note") or ""
                    invalid = result.get("invalid_users") or []
                    if invalid:
                        detail = "收件人不在可见范围：%s" % "、".join(
                            str(x) for x in invalid[:5])
                    return False, "已受理但未投递：%s" % (detail or "收件人无效")
                recipient = result.get("recipient") or "未知"
                delivery = str(result.get("delivery_status") or "")
                sent = _num(result.get("sent"))
                total = _num(result.get("total"))
                seg = ""
                if total:
                    seg = "，成功 %d/%d 段" % (sent if sent is not None else total, total)

                # 投递结论要分三态说清楚，别把「已投递」说成不确认：
                #   ok        → 对方按可见范围逐人核对过（wecom-notify 的真实词表：
                #               ok / empty / missing / unknown，**没有 confirmed** ——
                #               曾经判 "confirmed" 是死代码，「已送达」永不出现）；
                #   unknown   → 对方用了自建转发地址，user/list 不可用，
                #               **校验做不了**，但 msgid 已拿到、参数里也没人无效；
                #   failed    → 上面 delivery_ok is False 分支已拦掉。
                invalid = result.get("invalid_users") or []
                if delivery in ("ok", "confirmed") and not invalid:
                    note = "已送达（收件人：%s%s）" % (recipient, seg)
                elif invalid:
                    note = "已发送，但以下收件人不可见、实际未投递：%s（收件人：%s）" % (
                        "、".join(str(x) for x in invalid[:5]), recipient)
                elif delivery == "unknown":
                    note = ("已由「%s」发送（收件人：%s%s）；该接口无法逐人核对"
                            "投递情况（对方用的是自建转发地址），以微信端是否收到为准"
                            % (result.get("channel_name") or "微信", recipient, seg))
                else:
                    note = "已发送（收件人：%s%s）" % (recipient, seg)

                if not any(k in result for k in ("delivery_ok", "delivery_status",
                                                 "recipient", "msgids")):
                    note = "任务已受理（对方未回传投递结论，可能版本过旧）"
                return True, note
            time.sleep(2)
        # 超时时**不能直接判失败**：任务可能仍在跑、也可能消息已经发出去了，
        # 判成失败会把人引去排查一件其实已经成功的事。如实说「结果未知」。
        if seen_state in ("running", "pending", "queued", "started", "processing"):
            return False, ("等待结果超时（60 秒）：任务仍在运行（状态 %s）—— "
                           "消息可能已发出，请到微信端确认；若没收到再重试" % seen_state)
        if last:
            return False, "等待结果超时（60 秒）：%s" % last
        return False, ("等待结果超时（60 秒）：任务状态未知 —— "
                       "消息可能已发出，请到微信端确认")


# ---------------------------------------------------------------------------
# 历史记录
# ---------------------------------------------------------------------------

class _History(object):
    def __init__(self, log, data_dir, keep_days):
        self.log = log
        self.path = Path(data_dir) / HISTORY_FILE
        self.keep_days = keep_days
        self.records = []

    def load(self):
        if not self.path.is_file():
            self.records = []
            return self.records
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
        except Exception as exc:
            self.log.warn("读取推送历史失败（将重建）：%s" % exc)
            self.records = []
            return self.records
        records = data.get("records") if isinstance(data, dict) else data
        self.records = records if isinstance(records, list) else []
        return self.records

    def add(self, entry):
        self.load()
        self.records.append(entry)
        cutoff = time.time() - self.keep_days * 86400
        kept = []
        for record in self.records:
            try:
                when = float(record.get("ts") or 0)
            except (TypeError, ValueError):
                when = 0
            if when >= cutoff:
                kept.append(record)
        self.records = kept[-HISTORY_MAX_RECORDS:]
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps({"records": self.records}, ensure_ascii=False,
                           indent=2) + "\n",
                encoding="utf-8", newline="\n")
        except Exception as exc:
            self.log.warn("写入推送历史失败：%s" % exc)


# ---------------------------------------------------------------------------
# 选项
# ---------------------------------------------------------------------------

def build_options(params):
    """把原始 params 归一成一份显式选项（所有默认值在这里定，便于测试）。"""
    channels = _list(params, "channels", ["tg"])
    valid_channels = [c for c in channels if c in ("tg", "wecom")]
    enabled = []
    for input_name, key in SECTION_INPUTS.items():
        if _b(params, input_name, False):
            enabled.append(key)
    return {
        "func": _s(params, "func", "digest") or "digest",
        "channels": valid_channels,
        # 保留原始取值（含非法项），供校验阶段给出「取值无效」这类准确提示
        "channels_raw": [c for c in channels if c not in ("tg", "wecom")],
        "notify_bot": _s(params, "notify_bot", "auto") or "auto",
        "wecom_plugin_id": _s(params, "wecom_plugin_id", "wecom-notify") or "wecom-notify",
        "wecom_touser": _s(params, "wecom_touser", ""),
        "msg_format": _s(params, "msg_format", "text") or "text",
        "enabled_sections": enabled,
        "trend_dimension": _s(params, "trend_dimension", "day") or "day",
        "added_limit": _i(params, "added_limit", 10, 1, 100),
        "calendar_days": _i(params, "calendar_days", 1, 1, 30),
        "list_limit": _i(params, "list_limit", 8, 1, 50),
        "only_when_content": _b(params, "only_when_content", True),
        "title_prefix": _s(params, "title_prefix", PLUGIN_NAME),
        "include_time": _b(params, "include_time", True),
        "tgto_base_url": _s(params, "tgto_base_url", ""),
        "tgto_token": _s(params, "tgto_token", ""),
        "proxy_mode": _s(params, "proxy_mode", "off") or "off",
        "history_days": _i(params, "history_days", 30, 1, 365),
    }


def resolve_base_url(opt):
    if opt["tgto_base_url"]:
        return opt["tgto_base_url"].rstrip("/")
    env = (os.environ.get("TGTO_OPENAPI_BASE_URL") or "").strip()
    if env:
        return env.rstrip("/")
    return DEFAULT_TGTO_BASE


def resolve_token(opt):
    if opt["tgto_token"]:
        return opt["tgto_token"].strip()
    return (os.environ.get("TGTO_OPENAPI_TOKEN") or "").strip()


# ---------------------------------------------------------------------------
# 结果 UI
# ---------------------------------------------------------------------------

def _table(headers, rows):
    return {"type": "table", "headers": headers,
            "rows": [[str(cell) for cell in row] for row in rows]}


def result_ui(log, report, channels_result, extra=None, skipped_reason=""):
    """结果页：状态表 + 报告全文 + 运行日志。

    ``channels_result`` 为空时**不渲染**渠道表（例如「检查配置」「查看历史」
    这类不含发送动作的操作），避免出现一张写着「未发送」的无意义表格。

    ``extra`` 是一张表的完整行列表，**第一行是表头**（见 :func:`channel_table`
    / :func:`sections_table` / ``do_config`` 里的 ``rows``）。
    """
    components = []
    if channels_result or skipped_reason:
        rows = [["渠道", "结果", "说明"]]
        for item in channels_result:
            # 三态渲染：ok=None 是「状态未知」（如 Telegram 读超时——消息可能已送达），
            # 既不能算成功也不能算失败，显示成 ❓ 并提示不要盲目重试。
            if item["ok"]:
                mark = "✅ 成功"
            elif item["ok"] is None:
                mark = "❓ 状态未知"
            else:
                mark = "❌ 失败"
            rows.append([item["label"], mark, item["note"]])
        if len(rows) == 1:
            rows.append(["—", "—", skipped_reason or "未发送"])
        components.append({"type": "heading", "text": "推送结果"})
        components.append(_table(rows[0], rows[1:]))

    if extra:
        components.append(_table(extra[0], extra[1:]))

    if report:
        components.append({"type": "divider"})
        components.append({"type": "heading", "text": "消息内容"})
        components.append({"type": "code", "text": report})

    components.append({"type": "divider"})
    components.append({"type": "heading", "text": "运行日志"})
    components.append({"type": "code", "text": log.text()})
    return {"ui": {"width": "wide", "layout": "stack", "components": components}}


def channel_table(options):
    """渠道启用表：返回完整行列表，第一行是表头。"""
    names = {"tg": "Telegram", "wecom": "微信"}
    rows = [[names[k], "是"] for k in options["channels"]]
    return [["渠道", "启用"]] + (rows or [["—", "（未选任何渠道）"]])


def sections_table(options):
    """板块启用表：返回完整行列表，第一行是表头。"""
    rows = []
    for _key, label, _path in SECTION_DEFS:
        on = _key in options["enabled_sections"]
        rows.append([label, "✅ 已启用" if on else "— 未启用"])
    rows.append(["新增数量统计", "✅ 已启用"
                 if "counts" in options["enabled_sections"] else "— 未启用"])
    return [["板块", "状态"]] + rows


# ---------------------------------------------------------------------------
# 主运行器
# ---------------------------------------------------------------------------

class _Digest(object):

    def __init__(self, params, context):
        self.log = _Log()
        self.context = context or {}
        self.data_dir = self.context.get("data_dir") or "."
        self.plugin_dir = self.context.get("plugin_dir") or "."
        self.options = build_options(params or {})
        self.base_url = resolve_base_url(self.options)
        self.token = resolve_token(self.options)

    # -- 入口 ------------------------------------------------------------

    def run(self):
        func = self.options["func"]
        if func not in VALID_FUNCS:
            raise ValueError("不支持的执行操作：%s（可用：%s）"
                             % (func, " / ".join(VALID_FUNCS)))
        self.log.info("%s 启动，本次操作：%s" % (PLUGIN_NAME, _func_label(func)))
        self.log.info("TgtoDrive 地址：%s" % self.base_url)
        self.log.info("OpenAPI 令牌：%s"
                      % ("已填写（长度 %d）" % len(self.token) if self.token
                         else "未填写（也无法从环境变量读到）"))

        if func == "history":
            return self.do_history()

        http = _Http(self.log, use_env_proxy=(self.options["proxy_mode"] == "env"))
        self.log.info("网络：%s" % http.describe_mode())
        tdd = _Tdd(self.log, self.base_url, self.token, http)
        if not tdd.configured:
            raise ValueError(
                "未配置 OpenAPI 令牌：请在「执行与接口」里填写，或设置容器环境变量 "
                "TGTO_OPENAPI_TOKEN 后重启服务。"
                "（令牌需要在 TgtoDrive 的「设置 → OpenAPI」里生成）")

        if func == "config":
            return self.do_config(tdd, http)

        return self.do_digest(tdd, http, func)

    # -- 日报 ------------------------------------------------------------

    def do_digest(self, tdd, http, func):
        enabled = self.options["enabled_sections"]
        is_test = (func == "test")
        dry_run = (func == "preview")

        # 校验顺序有讲究：**先查渠道，再查板块**。
        # 反过来的话，用户「没勾渠道」或「渠道值非法」时会看到「没勾板块」的提示，
        # 去翻板块设置怎么都找不到问题（历史 bug）。另外「只预览」不发送，
        # 不需要渠道，也不该被板块校验拦住 —— 空跑一次看版式是正当用法。
        channels = self.options["channels"]
        if not dry_run and not channels:
            raw = self.options.get("channels_raw") or []
            if raw:
                raise ValueError(
                    "通知渠道取值无效：%s —— 请只勾选 Telegram 或 微信。"
                    % "、".join(str(x) for x in raw))
            raise ValueError("没有选择通知渠道 —— 请至少勾选 Telegram 或 微信。")

        if not enabled and not is_test and not dry_run:
            raise ValueError("没有勾选任何推送板块 —— 请至少启用一个，"
                             "或在结果页点「发送测试推送」验证渠道。")

        collector = _Collector(self.log, tdd, self.options)
        collected = collector.run(enabled) if enabled else {}

        renderer = _Renderer(self.options)
        report = renderer.render(collected, enabled, collector.errors) if enabled else ""
        if is_test:
            report = self._test_banner() + ("\n" + report if report else "")
        self.log.info("报告渲染完成，共 %d 字" % len(report))

        if dry_run:
            self.log.info("按「只预览不发送」执行，未发送任何消息")
            return result_ui(
                self.log, report, [],
                extra=channel_table(self.options),
                skipped_reason="预览模式：未发送",
            )

        # 没有内容时不打扰
        if self.options["only_when_content"] and not is_test:
            empty = (not collected or all(_is_empty(k, v) for k, v in collected.items()))
            if not empty and not _report_has_body(report):
                # **数据非空 ≠ 有内容可读**：compact 版式下列表类板块（最近入库 /
                # 最近播放 / 日历 / 趋势）不渲染明细，只勾这些板块时 raw 数据非空、
                # 渲染出来却只有标题行 + 分隔线 —— 这时每天推一条空消息，不如跳过。
                empty = True
                self.log.info("各板块数据非空，但渲染结果没有正文"
                              "（compact 版式下游标类板块不输出明细），按无内容跳过")
            if empty:
                self.log.info("所有板块都没有内容，按「没有新内容时不推送」跳过本次发送")
                return result_ui(
                    self.log, report, [],
                    extra=channel_table(self.options),
                    skipped_reason="无新内容，已跳过（可在设置里取消该限制）",
                )

        results = []
        for key in channels:
            channel = (_TelegramChannel(self.log, tdd, self.options, http)
                       if key == "tg" else
                       _WecomChannel(self.log, tdd, self.options, http))
            payload = strip_markdown(report) \
                if key == "wecom" and self.options["msg_format"] != "text" else report
            self.log.info("开始发送到 %s…" % channel.label)
            try:
                ok, note = channel.send(payload)
            except Exception as exc:
                ok, note = False, "发送异常：%s" % scrub_text(
                    exc, [self.token])
            self.log.info("%s 发送%s：%s" % (channel.label,
                                            "成功" if ok else "失败", note))
            results.append({"key": key, "label": channel.label,
                            "ok": ok, "note": note})

        self._record(results, report, func)

        # **先装配结果页，再决定成败**：曾经 ok_count==0 时在装配前就 raise，
        # 用户只看到一句裸错误，报告全文、运行日志、渠道明细全部丢失 ——
        # 违反「结果页必须先于通知结论存在」的既定约定。现在失败信息随结果页
        # 一起返回，另加 status=failed 让定时侧能标记这次运行失败。
        ui = result_ui(self.log, report, results,
                       extra=channel_table(self.options))
        ok_count = sum(1 for r in results if r["ok"])
        if ok_count == 0:
            self.log.warn("所有渠道都发送失败：%s"
                          % "；".join("%s %s" % (r["label"], r["note"])
                                      for r in results))
            ui["status"] = "failed"
        return ui

    def _test_banner(self):
        now = datetime.now(BEIJING)
        return ("%s\n这是一条【测试推送】，用于验证推送链路。\n"
                "生成时间：%s" % (PLUGIN_NAME, now.strftime("%Y-%m-%d %H:%M:%S")))

    # -- 配置检查 --------------------------------------------------------

    def do_config(self, tdd, http):
        self.log.info("开始检查配置与数据源连通性")

        rows = [["检查项", "结果", "说明"]]
        rows.append(["OpenAPI 地址", "✅", self.base_url])
        rows.append(["OpenAPI 令牌", "✅" if self.token else "❌",
                     "已填写（长度 %d）" % len(self.token) if self.token
                     else "未填写（也无法从环境变量读到）"])
        rows.append(["网络模式", "✅", http.describe_mode()])

        # 逐个数源探测
        probes = (
            ("媒体库总览", "/api/emby/dashboard", {}),
            ("最近入库", "/api/emby/latest", {"limit": "1"}),
            ("最近播放", "/api/emby/recent", {}),
            ("追剧日历", "/api/media/calendar", {"days": "1"}),
            ("播放趋势", "/api/emby/trend", {"dimension": "day"}),
        )
        for label, path, query in probes:
            try:
                status, payload = tdd.get_json(path, query)
            except Exception as exc:
                rows.append([label, "❌", str(exc)[:120]])
                continue
            if status == 200 and payload is not None:
                rows.append([label, "✅", "HTTP 200，正常返回数据"])
            elif status == 200:
                rows.append([label, "⚠️", "HTTP 200，但响应不是 JSON"])
            else:
                rows.append([label, "❌", "HTTP %s" % status])

        # 通知渠道探测
        tg = _TelegramChannel(self.log, tdd, self.options, http)
        try:
            bots, skipped, read_errors = tg.candidates()
        except Exception as exc:
            bots, skipped, read_errors = [], [], []
            rows.append(["Telegram 机器人", "❌", str(exc)[:120]])
        if bots:
            chosen = tg.select(bots) or {}
            rows.append(["Telegram 机器人", "✅",
                         "读到 %d 个可用；本次将使用「%s」（列表第 %s 项）"
                         % (len(bots), chosen.get("name"), chosen.get("index"))])
        elif read_errors:
            rows.append(["Telegram 机器人", "❌",
                         "读取「通知机器人」接口失败：%s（不是没配机器人，是接口没读到）"
                         % "；".join(read_errors[:2])[:120]])
        else:
            rows.append(["Telegram 机器人", "❌",
                         "未读到可用条目（检查 ttd「通知机器人」设置）"])

        plugin_id = self.options["wecom_plugin_id"]
        manifest = None
        try:
            manifest = tdd.plugin_manifest(plugin_id)
        except Exception as exc:
            rows.append(["微信通知插件", "❌", str(exc)[:120]])
        if manifest is not None:
            names = {i.get("name") for i in (manifest.get("inputs") or [])
                     if isinstance(i, dict)}
            state = "已停用" if manifest.get("enabled") is False else "已启用"
            ok = manifest.get("enabled") is not False and "envelope" in names
            rows.append(["微信通知插件", "✅" if ok else "❌",
                         "%s · %s · 版本 %s%s"
                         % (plugin_id, state, manifest.get("version") or "?",
                            "" if "envelope" in names
                            else " · 不支持 envelope，需更新")])
        elif not any(r[0] == "微信通知插件" for r in rows):
            rows.append(["微信通知插件", "❌", "未找到插件「%s」" % plugin_id])

        rows.append(["推送历史", "✅",
                     "本地已记录 %d 条" % len(_History(
                         self.log, self.data_dir,
                         self.options["history_days"]).load())])

        self.log.info("检查完成")
        return result_ui(self.log, "", [], extra=rows)

    # -- 历史 ------------------------------------------------------------

    def do_history(self):
        history = _History(self.log, self.data_dir, self.options["history_days"])
        records = history.load()
        self.log.info("读取推送历史：%d 条（保留 %d 天）"
                      % (len(records), self.options["history_days"]))
        if not records:
            return result_ui(self.log, "", [],
                             extra=[["时间", "操作", "渠道", "结果"],
                                    ["—", "—", "—", "暂无推送记录"]])

        rows = [["时间", "操作", "渠道", "结果"]]
        for record in reversed(records[-50:]):
            when = record.get("time") or "—"
            channels = "、".join(
                "%s%s" % (r.get("label", "?"),
                          "✅" if r.get("ok") else "❌")
                for r in (record.get("channels") or []))
            rows.append([when, record.get("func") or "—",
                         channels or "—", record.get("summary") or "—"])
        return result_ui(self.log, "", [], extra=rows)

    # -- 记录 ------------------------------------------------------------

    def _record(self, results, report, func):
        ok_count = sum(1 for r in results if r["ok"])
        history = _History(self.log, self.data_dir, self.options["history_days"])
        # 只存「渠道 + 成败」，**不存 note**：note 里常带收件人账号（如
        # 「成员 CaiShenYeDeXinTouBao」），持久化到磁盘没有必要，而且
        # 400 条记录下会把文件撑到几十 KB。查看历史只用到 label 与 ok。
        history.add({
            "ts": time.time(),
            "time": datetime.now(BEIJING).strftime("%Y-%m-%d %H:%M:%S"),
            "func": _func_label(func),
            "channels": [{"label": r["label"], "ok": bool(r["ok"])}
                         for r in results],
            "summary": "成功 %d / 共 %d ｜ 报告 %d 字"
                       % (ok_count, len(results), len(report)),
        })
        self.log.info("本次推送已记入历史（成功 %d / 共 %d）" % (ok_count, len(results)))


def _func_label(func):
    return {
        "digest": "正式推送",
        "preview": "只预览不发送",
        "test": "发送测试推送",
        "config": "检查配置",
        "history": "查看推送历史",
    }.get(func, func)


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------

def run(params, context):
    digest = _Digest(params or {}, context or {})
    return digest.run()


if __name__ == "__main__":  # 便于本地直接调试：python plugin.py
    import sys as _sys
    _payload = json.loads(_sys.argv[1]) if len(_sys.argv) > 1 else {"func": "preview"}
    print(json.dumps(run(_payload, {"plugin_dir": ".", "data_dir": "./_data"}),
                     ensure_ascii=False, indent=2))
