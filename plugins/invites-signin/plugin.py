# -*- coding: utf-8 -*-
"""药丸论坛（invites.fun）自动签到 · TgtoDrive Python 插件

移植自 MoviePilot 三方插件仓库 thsrite/MoviePilot-Plugins 的「药丸签到」（v3.0.1，原作者 thsrite），
由 a2695154202 按 TgtoDrive 插件协议改写：单次同步 run(params, context)，不含常驻定时器。

能力
  * 自动签到：先用 Cookie 向站点换取新的 Flarum session，再执行签到；
    失败回退「用户名 + 密码」登录签到（与原始插件一致的双通道策略）。
  * 仅用 Cookie 签到 / 仅用账号密码签到 / 仅查询签到状态 / 查看本地签到历史。
  * 签到成功或失败后，通过 TgtoDrive 已配置的 Telegram 通知机器人推送结果；
    可在「通知机器人」下拉框指定使用哪一个，默认自动选主通知机器人。
  * 可选地，同时通过「企业微信通知」插件（wecom-notify）发送**微信通知**：
    走 TgtoDrive OpenAPI 的插件运行接口调用该插件，企业 ID / Secret 等凭据与收件人
    沿用它在插件里已保存的设置，本插件只传要发送的内容；支持文本与带图卡片两种形式。
  * 诊断功能：读取 TgtoDrive 通知机器人列表、发送测试通知。
  * 运行结果内嵌「运行日志」窗口；清单提供「运行一次」按钮，
    点击后立即执行当前选中的功能，并强制把本次结果通知出去。

运行环境
  * 仅使用标准库 + 容器已装依赖（requests；可选 curl_cffi 做浏览器指纹请求）。
  * 不安装依赖、不创建虚拟环境、不导入 TgtoDrive 内部模块、不读写项目数据库。

定时执行
  * 由「实用工具 → 我的插件 → 定时执行」配置 cron，本插件内部不做定时循环。
  * 推荐：cron = 5 8 * * *（每天 08:05 北京时间），func = auto，timeout = 300。

凭据与安全
  * Cookie / 密码只通过清单参数传入，日志与返回值中一律不回显。
  * 通知所需的 OpenAPI 地址与令牌优先取插件表单里的可选项，其次取环境变量
    TGTO_OPENAPI_BASE_URL / TGTO_OPENAPI_TOKEN；插件包内不写任何真实令牌，
    日志与返回值中也不回显令牌。
"""

# ---------------------------------------------------------------------------
# 关于插件清单
# ---------------------------------------------------------------------------
# 本文件是**插件包内入口**：清单写在同目录的 plugin.json 里，这里不写
# PLUGIN_MANIFEST。打包时 scripts/package_plugin.py 会把 plugin.json 的内容
# 内联到 dist/invites-signin.py 的开头，生成可单独导入的单文件版。
#
# 若把本文件当作「Python 单文件」单独导入，TgtoDrive 会报
#   「Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典」
# 这是预期行为，不是插件损坏。请改用下面两种产物之一：
#   * dist/invites-signin.py   单文件，顶层内联 PLUGIN_MANIFEST
#   * dist/invites-signin.zip  插件包（plugin.json + plugin.py + README.md）
# 两者都由 scripts/package_plugin.py 生成，随 Release 分发。

import json
import os
import re
import time
from datetime import datetime, timedelta
from http.cookies import SimpleCookie
from pathlib import Path

# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_SITE_BASE = "https://invites.fun"
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0"
)
ACCEPT_HTML = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,"
    "image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7"
)
CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30
TELEGRAM_API = "https://api.telegram.org"
NOTIFY_TITLE = "【💊药丸签到】任务完成"

# 微信通知：通过 TgtoDrive OpenAPI 调用「企业微信通知」插件（wecom-notify）发送。
# 调用方式见该插件的 CALLING.md：POST /api/toolbox/plugins/wecom-notify/run
WECOM_PLUGIN_ID = "wecom-notify"
WECOM_TITLE = "【💊药丸签到】"
WECOM_CARD_TITLE = "💊 药丸签到"
# 提交任务后轮询结果的次数与间隔（拿不到 job_id 或超时都不影响签到本身）
WECOM_JOB_POLL_ATTEMPTS = 3
WECOM_JOB_POLL_INTERVAL = 2

FUNC_LABELS = {
    "auto": "自动签到（Cookie 优先，失败回退账号密码）",
    "cookie": "仅用 Cookie 签到",
    "login": "仅用账号密码登录签到",
    "status": "仅查询签到状态（不签到）",
    "history": "查看签到历史（本地记录）",
    "bots": "读取通知机器人列表（不签到）",
    "test_notify": "发送测试通知（不签到）",
}
VALID_FUNCS = tuple(FUNC_LABELS)

# 通知机器人下拉框：ttd 的清单由 AST 静态读取，选项无法在打开页面时动态生成，
# 因此按「序号」选择项目机器人列表中的第 N 个，选中值随插件设置一起保存。
NOTIFY_BOT_MAX_INDEX = 8
NOTIFY_BOT_AUTO = "auto"

# Telegram 机器人令牌形如 1234567890:AAE...（用于在项目配置里安全识别）
BOT_TOKEN_RE = re.compile(r"^\d{6,}:[A-Za-z0-9_-]{30,}$")
REMEMBER_RE = re.compile(r"flarum_remember=([^;]+)")
SESSION_RE = re.compile(r"flarum_session=([^;]+)")
CSRF_HTML_RE = re.compile(r'"csrfToken":"(.*?)"')
USERID_HTML_RE = re.compile(r'"userId":(\d+)')

HISTORY_FILE = "history.json"

# 机器人条目里可能出现的可读名称键、以及「主机器人」的命名特征
NAME_KEYS = ("name", "title", "label", "remark", "alias", "nickname",
             "bot_name", "tag", "desc", "description")
PRIMARY_HINTS = ("主", "默认", "全局", "primary", "main", "default", "admin")
CONTAINER_HINTS = ("bot", "notify", "telegram", "tg", "list", "items",
                   "data", "accounts", "robot", "推送", "通知")


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

class _Logger:
    """同时写入标准输出（TgtoDrive 运行日志）和内存缓冲区（结果内日志窗口）。"""

    MAX_LINES = 2000

    def __init__(self):
        self.lines = []

    def _emit(self, level, message):
        line = "[%s] [%s] %s" % (datetime.now().strftime("%H:%M:%S"), level, message)
        if len(self.lines) < self.MAX_LINES:
            self.lines.append(line)
        try:
            print(line, flush=True)
        except Exception:
            pass

    def info(self, message):
        self._emit("INFO", message)

    def warn(self, message):
        self._emit("WARN", message)

    def error(self, message):
        self._emit("ERROR", message)

    def text(self, limit=20000):
        raw = "\n".join(self.lines)
        if len(raw) <= limit:
            return raw
        head = limit // 2
        tail = limit - head
        return raw[:head] + "\n...（日志已截断）...\n" + raw[-tail:]


# ---------------------------------------------------------------------------
# HTTP 适配层：requests 为主，可选 curl_cffi 浏览器指纹
# ---------------------------------------------------------------------------

class _Resp(object):
    __slots__ = ("status", "text", "cookies", "headers", "json_data", "error")

    def __init__(self, status=None, text="", cookies=None, headers=None,
                 json_data=None, error=None):
        self.status = status
        self.text = text or ""
        self.cookies = cookies or {}
        self.headers = headers or {}
        self.json_data = json_data
        self.error = error

    @property
    def ok(self):
        return self.status is not None and 200 <= self.status < 300

    def header(self, name):
        target = name.lower()
        for key, value in self.headers.items():
            if str(key).lower() == target:
                return value
        return None


def _normalize_response(resp):
    status = getattr(resp, "status_code", None)
    try:
        text = getattr(resp, "text", "") or ""
    except Exception:
        text = ""

    headers = {}
    try:
        for key, value in dict(resp.headers).items():
            headers[key] = value
    except Exception:
        pass

    cookies = {}
    try:
        jar = getattr(resp, "cookies", None)
        if jar is not None:
            if hasattr(jar, "get_dict"):
                cookies = dict(jar.get_dict())
            elif hasattr(jar, "items"):
                cookies = {k: v for k, v in jar.items()}
            else:
                cookies = {c.name: c.value for c in jar}
    except Exception:
        cookies = {}

    data = None
    try:
        data = resp.json()
    except Exception:
        data = None

    return _Resp(status, text, cookies, headers, data)


def _as_bool(value, default=False):
    """宽容地把表单值转成布尔：支持真布尔、数字与常见字符串写法。"""
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in ("1", "true", "yes", "on", "y", "t", "是", "开启")


def _mask_proxy(url):
    """隐藏代理地址中的用户名密码，仅保留主机信息用于日志。"""
    if not url:
        return ""
    return re.sub(r"//[^/@\s]+@", "//***@", str(url))


def _mask(value, head=3, tail=3):
    text = str(value or "")
    if not text:
        return "（未填写）"
    if len(text) <= head + tail:
        return text[0] + "*" * max(len(text) - 1, 0)
    return "%s…%s" % (text[:head], text[-tail:])


# 网络库在抛异常时会回显**完整 URL**，而凭据恰恰藏在 URL 里：
# 本插件的 Telegram bot token 在路径中（/bot<id>:<token>/sendMessage），
# 企业微信的 corpsecret 在查询串中。不脱敏就会把密钥原样写进运行日志。
SENSITIVE_QUERY_RE = re.compile(
    r"(?i)\b(corpsecret|corpid|appsecret|access_token|encodingaeskey|secret|token)"
    r"=([^&\s'\"),\]]+)"
)
BOT_TOKEN_PATH_RE = re.compile(r"(/bot)(\d{4,}):([A-Za-z0-9_\-]{20,})")


def scrub_text(text, secrets=()):
    """抹掉文本中的凭据，返回可安全打印的字符串。

    三道防线：先按**已知明文**精确替换、再处理 ``key=value`` 查询串、
    最后处理 URL 路径里的 Telegram bot token。
    """
    if text is None:
        return ""
    result = str(text)
    for value in secrets:
        plain = str(value or "")
        if len(plain) >= 8:
            result = result.replace(plain, _mask(plain))
    result = SENSITIVE_QUERY_RE.sub(
        lambda match: "%s=%s" % (match.group(1), _mask(match.group(2))), result)
    return BOT_TOKEN_PATH_RE.sub(
        lambda match: "%s%s:%s" % (match.group(1), _mask(match.group(2)), _mask(match.group(3))),
        result)


# ---------------------------------------------------------------------------
# TgtoDrive 通知：读取项目已配置的通知机器人并推送
# ---------------------------------------------------------------------------

class _TtdClient(object):
    """通过 OpenAPI Bearer 令牌读取/调用 TgtoDrive 自身接口。

    地址与令牌优先取插件表单填写值，其次取环境变量
    TGTO_OPENAPI_BASE_URL / TGTO_OPENAPI_TOKEN。令牌仅用于请求，从不回显。
    """

    DEFAULT_BASE = "http://127.0.0.1:12366"

    def __init__(self, log, base_override="", token_override=""):
        self.log = log
        base_override = str(base_override or "").strip()
        token_override = str(token_override or "").strip()
        env_base = (os.environ.get("TGTO_OPENAPI_BASE_URL") or "").strip()
        env_token = (os.environ.get("TGTO_OPENAPI_TOKEN") or "").strip()

        self.base = (base_override or env_base).rstrip("/")
        self.token = token_override or env_token
        self.base_source = "插件设置" if base_override else ("环境变量" if env_base else "")
        self.token_source = "插件设置" if token_override else ("环境变量" if env_token else "")

        if self.token and not self.base:
            self.base = self.DEFAULT_BASE
            self.base_source = "同容器默认地址"
            log.info("未填写 TgtoDrive 地址，按同容器默认值使用 %s" % self.base)

    @property
    def configured(self):
        return bool(self.base and self.token)

    def describe(self):
        if not self.configured:
            return "未配置"
        return "%s（地址来源：%s，令牌来源：%s）" % (
            self.base, self.base_source or "未知", self.token_source or "未知")

    def get_json(self, path, timeout=(5, 20)):
        import requests

        try:
            resp = requests.get(
                self.base + path,
                headers={"Authorization": "Bearer " + self.token},
                timeout=timeout,
                allow_redirects=False,
            )
        except Exception as exc:
            raise RuntimeError("调用 TgtoDrive 接口失败（%s）：%s" % (path, exc))
        if not 200 <= resp.status_code < 300:
            raise RuntimeError("调用 TgtoDrive 接口失败（%s）：HTTP %s" % (path, resp.status_code))
        try:
            return resp.json()
        except Exception:
            raise RuntimeError("TgtoDrive 接口 %s 未返回 JSON" % path)


def _walk(node):
    """深度遍历 dict/list，产出 (key, value) 对。"""
    if isinstance(node, dict):
        for key, value in node.items():
            yield str(key), value
            for item in _walk(value):
                yield item
    elif isinstance(node, list):
        for value in node:
            for item in _walk(value):
                yield item


def _looks_like_token(value):
    return bool(isinstance(value, str) and BOT_TOKEN_RE.match(value.strip()))


def _extract_bot_config(payload):
    """从项目配置响应里找出单个机器人的 token / 推送目标 / 代理。

    规范中该接口的返回结构标记为 generic，字段名不做保证，
    因此这里只按「键名语义 + 取值形态」做保守识别，不猜测具体字段。
    """
    token = None
    chat_id = None
    proxy = None

    for key, value in _walk(payload):
        low = key.lower()
        if isinstance(value, (dict, list)):
            continue

        if token is None and isinstance(value, str) and _looks_like_token(value):
            token = value.strip()
            continue

        if token is None and isinstance(value, str) and value.strip():
            if ("token" in low) and ("bot" in low or "tg" in low or "telegram" in low):
                token = value.strip()
                continue

        if chat_id is None and ("id" in low or "chat" in low):
            if "admin" in low or "chat" in low or "tg" in low or "telegram" in low:
                text = str(value).strip()
                if re.fullmatch(r"-?\d{4,20}", text):
                    chat_id = text
                    continue

        if proxy is None and "proxy" in low and isinstance(value, str) and value.strip():
            lowered = value.strip().lower()
            if lowered.startswith(("http://", "https://", "socks4://", "socks5://",
                                   "socks4h://", "socks5h://")):
                proxy = value.strip()
                continue

    return token, chat_id, proxy


def _pick_name(node):
    """从机器人条目里挑一个可读名称，取不到则返回空串。"""
    if not isinstance(node, dict):
        return ""
    for key in NAME_KEYS:
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:40]
    for key, value in node.items():
        low = str(key).lower()
        if ("name" in low or "title" in low or "label" in low) \
                and isinstance(value, str) and value.strip():
            return value.strip()[:40]
    return ""


def _is_primary_name(name):
    low = str(name or "").lower()
    return any(hint in low for hint in PRIMARY_HINTS)


def _list_bot_entries(payload):
    """在配置响应中找出「机器人列表」的候选集合，键名更相关的排在前面。"""
    found = []

    def walk(node, depth):
        if depth > 3:
            return
        if isinstance(node, list):
            items = [item for item in node if isinstance(item, dict)]
            if items:
                found.append(items)
            return
        if isinstance(node, dict):
            hinted = []
            others = []
            nested = []
            for key, value in node.items():
                if isinstance(value, list):
                    if not any(isinstance(item, dict) for item in value):
                        continue
                    low = str(key).lower()
                    if any(hint in low for hint in CONTAINER_HINTS):
                        hinted.append(value)
                    else:
                        others.append(value)
                elif isinstance(value, dict):
                    nested.append(value)
            for value in hinted + others + nested:
                walk(value, depth + 1)

    walk(payload, 0)
    return found


def _collect_bots(payload, source):
    """把配置响应整理成机器人条目列表，序号按发现顺序重新编号。"""
    bots = []
    seen = set()

    def push(item):
        if not isinstance(item, dict):
            return
        token, chat_id, proxy = _extract_bot_config(item)
        name = _pick_name(item) or "机器人 #%d" % (len(bots) + 1)
        key = (token or "", chat_id or "", name)
        if key in seen:
            return
        seen.add(key)
        bots.append({
            "name": name,
            "token": token,
            "chat_id": chat_id,
            "proxy": proxy,
            "source": source,
            "index": len(bots) + 1,
        })

    for items in _list_bot_entries(payload):
        for item in items:
            push(item)

    if not bots:
        token, chat_id, proxy = _extract_bot_config(payload)
        if token or chat_id:
            bots.append({
                "name": _pick_name(payload) or "默认机器人",
                "token": token,
                "chat_id": chat_id,
                "proxy": proxy,
                "source": source,
                "index": 1,
            })
    return bots


def _mask_id(value):
    """推送目标 ID 只保留末 4 位，避免日志与结果里出现完整标识。"""
    text = str(value or "")
    if not text:
        return "-"
    if len(text) <= 4:
        return "*" * len(text)
    return "***%s" % text[-4:]


def _notify_bot_label(value):
    value = str(value or NOTIFY_BOT_AUTO)
    if value == NOTIFY_BOT_AUTO:
        return "自动：优先主通知机器人"
    if value.startswith("index:"):
        return "列表第 %s 个机器人" % value.split(":", 1)[1]
    return value


# ---------------------------------------------------------------------------
# 药丸签到执行体
# ---------------------------------------------------------------------------

class _SigninRunner(object):

    def __init__(self, params, context):
        self.p = dict(params or {})
        self.log = _Logger()
        self.data_dir = Path(context["data_dir"])
        self.plugin_dir = Path(context["plugin_dir"])
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        self.func = str(self.p.get("func") or "auto").strip()
        self.site_base = (str(self.p.get("site_base") or "").strip().rstrip("/")
                          or DEFAULT_SITE_BASE)
        self.cookie_raw = str(self.p.get("cookie") or "").strip()
        self.username = str(self.p.get("username") or "").strip()
        self.password = str(self.p.get("user_password") or "")
        self.notify_enabled = bool(self.p.get("notify", True))
        self.notify_bot = str(self.p.get("notify_bot") or NOTIFY_BOT_AUTO).strip() or NOTIFY_BOT_AUTO
        if self.notify_bot != NOTIFY_BOT_AUTO and not self.notify_bot.startswith("index:"):
            self.notify_bot = NOTIFY_BOT_AUTO
        self.tgto_base_url = str(self.p.get("tgto_base_url") or "").strip()
        self.tgto_token = str(self.p.get("tgto_token") or "").strip()

        # 微信通知：通过 OpenAPI 调用 wecom-notify 插件
        self.wecom_notify = _as_bool(self.p.get("wecom_notify"), False)
        self.wecom_msgtype = str(self.p.get("wecom_msgtype") or "text").strip() or "text"
        if self.wecom_msgtype not in ("text", "template_card"):
            self.wecom_msgtype = "text"
        self.wecom_touser = str(self.p.get("wecom_touser") or "").strip()
        self.wecom_card_image = str(self.p.get("wecom_card_image") or "").strip()
        self._wecom_state = "not-called"
        self._wecom_error = ""
        self.use_proxy = bool(self.p.get("use_proxy", True))
        self.use_fingerprint = bool(self.p.get("use_browser_fingerprint", False))
        self.history_days = self._as_int(self.p.get("history_days"), 30, 1, 3650, "历史记录保留天数")
        self.retry_count = self._as_int(self.p.get("retry_count"), 2, 1, 10, "失败重试次数")
        self.retry_interval = self._as_int(self.p.get("retry_interval"), 10, 0, 300, "重试间隔（秒）")

        self._proxy = None
        self._proxy_ready = False
        self._client = None
        self._bots = []
        self._last_bot_name = ""
        self._last_bot_index = None

    # -- 参数工具 ----------------------------------------------------------

    @staticmethod
    def _as_int(value, default, low, high, label):
        if value is None or value == "":
            value = default
        if isinstance(value, bool):
            raise ValueError("%s 必须是整数" % label)
        try:
            number = int(value)
        except (TypeError, ValueError):
            raise ValueError("%s 必须是整数" % label)
        if not low <= number <= high:
            raise ValueError("%s 必须在 %d ~ %d 之间" % (label, low, high))
        return number

    # -- TgtoDrive 客户端 --------------------------------------------------

    def _tdd_client(self):
        if self._client is None:
            self._client = _TtdClient(self.log, self.tgto_base_url, self.tgto_token)
        return self._client

    def _read_bots(self):
        """读取项目已配置的通知机器人列表。

        返回 (bots, client, 失败原因)；bots 按发现顺序编号，序号即下拉框取值。
        """
        client = self._tdd_client()
        if not client.configured:
            self.log.warn(
                "未配置 TgtoDrive 地址或 OpenAPI 令牌，无法读取通知机器人。"
                "可在插件「通知与接口」页填写地址与令牌，或设置容器环境变量 "
                "TGTO_OPENAPI_BASE_URL / TGTO_OPENAPI_TOKEN 后重启服务。"
            )
            return [], client, "openapi-not-configured"

        self.log.info("读取 TgtoDrive 通知机器人配置：%s" % client.describe())
        bots = []
        seen = set()
        for path in ("/api/notify-bots", "/api/proxy_settings"):
            try:
                payload = client.get_json(path)
            except Exception as exc:
                self.log.warn("读取 %s 失败：%s" % (path, exc))
                continue
            for bot in _collect_bots(payload, path):
                key = (bot.get("token") or "", bot.get("chat_id") or "", bot.get("name") or "")
                if key in seen:
                    continue
                seen.add(key)
                bots.append(bot)
            usable = [b for b in bots if b.get("token") and b.get("chat_id")]
            if usable:
                self.log.info("已从 %s 读取到 %d 个机器人条目（%d 个可用）"
                              % (path, len(bots), len(usable)))
                break

        for position, bot in enumerate(bots, 1):
            bot["index"] = position
        if bots:
            self._bots = bots
        self.log.info("通知机器人列表读取完成，共 %d 条" % len(bots))
        return bots, client, "" if bots else "bot-not-found"

    def _select_bot(self, bots):
        """按「通知机器人」参数挑选要使用的机器人。"""
        usable = [b for b in bots if b.get("token") and b.get("chat_id")]
        selection = self.notify_bot

        if selection.startswith("index:"):
            try:
                wanted = int(selection.split(":", 1)[1])
            except (TypeError, ValueError):
                wanted = 0
            target = next((b for b in bots if b.get("index") == wanted), None)
            if target and target.get("token") and target.get("chat_id"):
                return target
            if target is not None:
                self.log.warn("「列表第 %d 个机器人」（%s）缺少 Token 或推送目标 ID，"
                              "改用主通知机器人" % (wanted, target.get("name") or "-"))
            else:
                self.log.warn("配置中只有 %d 个机器人条目，不存在「列表第 %d 个」，"
                              "改用主通知机器人" % (len(bots), wanted))

        primary = next((b for b in usable if _is_primary_name(b.get("name"))), None)
        if primary is not None:
            return primary
        return usable[0] if usable else None

    # -- 网络基础 ----------------------------------------------------------

    def _resolve_proxy(self):
        if self._proxy_ready:
            return self._proxy
        self._proxy_ready = True
        if not self.use_proxy:
            self.log.info("未启用代理")
            return None

        for key in ("HTTPS_PROXY", "https_proxy", "ALL_PROXY", "all_proxy",
                    "HTTP_PROXY", "http_proxy"):
            value = (os.environ.get(key) or "").strip()
            if value:
                self.log.info("使用容器环境变量代理 %s：%s" % (key, _mask_proxy(value)))
                self._proxy = value
                return value

        client = self._tdd_client()
        if client.configured:
            try:
                payload = client.get_json("/api/proxy_settings")
                _, _, proxy = _extract_bot_config(payload)
                if proxy:
                    self.log.info("使用 TgtoDrive 全局代理：%s" % _mask_proxy(proxy))
                    self._proxy = proxy
                    return proxy
                self.log.info("TgtoDrive 全局设置中未找到可用代理")
            except Exception as exc:
                self.log.warn("读取 TgtoDrive 全局代理失败：%s" % exc)
        else:
            self.log.info("未配置 TgtoDrive 地址或令牌，跳过读取 TgtoDrive 全局代理")
        return None

    def _proxies_arg(self):
        proxy = self._resolve_proxy()
        if not proxy:
            return None
        return {"http": proxy, "https": proxy}

    def _http(self, method, url, headers=None, cookies=None, json_body=None,
              allow_redirects=True, log_quiet=False):
        proxies = self._proxies_arg()
        timeout = (CONNECT_TIMEOUT, READ_TIMEOUT)

        if self.use_fingerprint:
            try:
                from curl_cffi import requests as curl_requests

                kwargs = {
                    "headers": headers or {},
                    "timeout": timeout,
                    "allow_redirects": allow_redirects,
                    "impersonate": "chrome",
                }
                if cookies:
                    kwargs["cookies"] = cookies
                if proxies:
                    kwargs["proxies"] = proxies
                if json_body is not None:
                    kwargs["json"] = json_body
                resp = curl_requests.request(method, url, **kwargs)
                return _normalize_response(resp)
            except ImportError:
                self.log.warn("容器内未找到 curl_cffi，回退标准 requests 请求")
            except Exception as exc:
                return _Resp(error="%s" % exc)

        try:
            import requests

            resp = requests.request(
                method,
                url,
                headers=headers or {},
                cookies=cookies or None,
                json=json_body,
                timeout=timeout,
                allow_redirects=allow_redirects,
                proxies=proxies,
            )
            return _normalize_response(resp)
        except Exception as exc:
            if not log_quiet:
                self.log.warn("请求异常：%s %s → %s" % (method, url, exc))
            return _Resp(error="%s" % exc)

    # -- Cookie / 会话 -----------------------------------------------------

    def _remember_from_cookie(self):
        match = REMEMBER_RE.search(self.cookie_raw or "")
        return match.group(1).strip() if match else None

    @staticmethod
    def _parse_cookie_pair(cookie_str):
        cookies = {}
        try:
            jar = SimpleCookie()
            jar.load(cookie_str or "")
            for name in ("flarum_remember", "flarum_session"):
                if name in jar:
                    cookies[name] = jar[name].value
        except Exception:
            pass
        if "flarum_remember" not in cookies:
            match = REMEMBER_RE.search(cookie_str or "")
            if match:
                cookies["flarum_remember"] = match.group(1).strip()
        if "flarum_session" not in cookies:
            match = SESSION_RE.search(cookie_str or "")
            if match:
                cookies["flarum_session"] = match.group(1).strip()
        return cookies

    def _mint_session(self, remember):
        """用 flarum_remember 换取新的 flarum_session。"""
        headers = {
            "Cookie": "flarum_remember=%s" % remember,
            "User-Agent": USER_AGENT,
            "Upgrade-Insecure-Requests": "1",
            "Accept": ACCEPT_HTML,
            "Accept-Language": "zh-CN,zh;q=0.9",
        }
        resp = self._http("GET", self.site_base + "/", headers=headers,
                          allow_redirects=False)
        if resp.error and resp.status is None:
            self.log.error("刷新 session 请求失败：%s" % resp.error)
            return None

        session = resp.cookies.get("flarum_session")
        if not session:
            set_cookie = resp.header("Set-Cookie") or ""
            match = SESSION_RE.search(set_cookie)
            if match:
                session = match.group(1).strip()
        if session:
            self.log.info("已刷新 flarum_session（HTTP %s）" % resp.status)
        else:
            self.log.error("未能从响应中取得 flarum_session（HTTP %s）" % resp.status)
        return session

    def _session_from_cookie(self):
        """返回 {'cookie':..., 'user_id':..., 'csrf':...} 或 (None, 原因)。"""
        cookie_str = self.cookie_raw
        if not cookie_str:
            return None, "未填写 Cookie"
        remember = self._remember_from_cookie()
        if not remember:
            return None, "Cookie 中未找到 flarum_remember 值"

        session = self._mint_session(remember)
        if not session:
            return None, "刷新 flarum_session 失败（Cookie 可能已失效）"

        final_cookie = "flarum_remember=%s; flarum_session=%s" % (remember, session)
        return self._fetch_csrf_and_user(final_cookie)

    def _fetch_csrf_and_user(self, cookie_str):
        headers = {
            "Cookie": cookie_str,
            "User-Agent": USER_AGENT,
            "Accept": ACCEPT_HTML,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Upgrade-Insecure-Requests": "1",
        }
        resp = self._http("GET", self.site_base + "/", headers=headers)
        if resp.status is None:
            return None, "请求站点首页失败：%s" % (resp.error or "无响应")
        if resp.status != 200:
            return None, "请求站点首页失败：HTTP %s" % resp.status

        html = resp.text or ""
        csrf_match = CSRF_HTML_RE.search(html)
        if not csrf_match:
            return None, "首页未解析到 csrfToken（登录态可能已失效）"
        user_match = USERID_HTML_RE.search(html)
        if not user_match:
            return None, "首页未解析到 userId（登录态可能已失效）"

        csrf = csrf_match.group(1).strip()
        user_id = user_match.group(1).strip()
        self.log.info("已取得会话信息，userId=%s" % user_id)
        return {"cookie": cookie_str, "user_id": user_id, "csrf": csrf}, None

    def _session_from_login(self):
        """用户名 + 密码登录，返回会话信息。"""
        if not self.username or not self.password:
            return None, "未填写用户名或密码"

        get_headers = {
            "Accept": ACCEPT_HTML,
            "Accept-Language": "zh-CN,zh;q=0.9",
            "User-Agent": USER_AGENT,
            "Upgrade-Insecure-Requests": "1",
        }
        resp = self._http("GET", self.site_base + "/", headers=get_headers)
        if resp.status is None:
            return None, "获取初始会话失败：%s" % (resp.error or "无响应")
        if resp.status != 200:
            return None, "获取初始会话失败：HTTP %s" % resp.status

        session = resp.cookies.get("flarum_session")
        csrf = resp.header("x-csrf-token")
        if not session:
            return None, "未获取到 flarum_session"
        if not csrf:
            return None, "未获取到 x-csrf-token"

        login_headers = {
            "Accept": "*/*",
            "Content-Type": "application/json; charset=UTF-8",
            "Origin": self.site_base,
            "Referer": self.site_base + "/",
            "x-csrf-token": csrf,
            "User-Agent": USER_AGENT,
        }
        login_body = {
            "identification": self.username,
            "password": self.password,
            "remember": True,
        }
        login = self._http(
            "POST",
            self.site_base + "/login",
            headers=login_headers,
            cookies={"flarum_session": session},
            json_body=login_body,
        )
        if login.status is None:
            return None, "登录请求失败：%s" % (login.error or "无响应")
        if login.status != 200:
            return None, "登录失败：HTTP %s" % login.status

        remember = login.cookies.get("flarum_remember")
        new_session = login.cookies.get("flarum_session")
        new_csrf = login.header("X-CSRF-Token") or csrf
        if not remember or not new_session:
            return None, "登录后未获取到有效 Cookie（账号或密码可能不正确）"

        user_id = None
        if isinstance(login.json_data, dict):
            user_id = login.json_data.get("userId")
        if not user_id:
            return None, "登录响应中未取到 userId"

        self.log.info("账号密码登录成功，userId=%s" % user_id)
        cookie_str = "flarum_remember=%s; flarum_session=%s" % (remember, new_session)
        return {"cookie": cookie_str, "user_id": str(user_id), "csrf": str(new_csrf)}, None

    # -- 签到状态 ----------------------------------------------------------

    def _api_headers(self, csrf):
        return {
            "accept": "*/*",
            "accept-language": "zh-CN,zh-Hans;q=0.9",
            "origin": self.site_base,
            "referer": self.site_base + "/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-csrf-token": csrf,
            "user-agent": USER_AGENT,
        }

    @staticmethod
    def _extract_state(payload):
        if not isinstance(payload, dict):
            return {}
        data = payload.get("data")
        if not isinstance(data, dict):
            return {}
        attrs = data.get("attributes")
        if not isinstance(attrs, dict):
            return {}
        return {
            "user_id": str(data.get("id") or ""),
            "canCheckin": attrs.get("canCheckin"),
            "lastCheckinTime": attrs.get("lastCheckinTime") or "",
            "totalContinuousCheckIn": attrs.get("totalContinuousCheckIn"),
            "money": attrs.get("money"),
        }

    @staticmethod
    def _is_today(state):
        last = str((state or {}).get("lastCheckinTime") or "")
        return bool(last and last.startswith(datetime.now().strftime("%Y-%m-%d")))

    @staticmethod
    def _error_from(resp):
        if resp is None:
            return "无响应"
        if isinstance(resp.json_data, dict):
            errors = resp.json_data.get("errors")
            if isinstance(errors, list):
                messages = []
                for item in errors:
                    if not isinstance(item, dict):
                        continue
                    message = item.get("detail") or item.get("title") or item.get("code")
                    if message:
                        messages.append(str(message))
                if messages:
                    return "；".join(messages)
        text = (resp.text or "").strip()
        if text:
            return text[:200]
        return "HTTP %s" % resp.status

    def _fetch_state(self, session):
        cookies = self._parse_cookie_pair(session["cookie"])
        resp = self._http(
            "GET",
            "%s/api/users/%s" % (self.site_base, session["user_id"]),
            headers=self._api_headers(session["csrf"]),
            cookies=cookies,
        )
        if resp.status != 200:
            self.log.warn("查询签到状态失败：HTTP %s" % resp.status)
            return {}
        return self._extract_state(resp.json_data or {})

    # -- 签到主流程 --------------------------------------------------------

    def _perform_checkin(self, session, channel):
        cookies = self._parse_cookie_pair(session["cookie"])
        if not cookies.get("flarum_remember") or not cookies.get("flarum_session"):
            return {"ok": False, "reason": "Cookie 缺少 flarum_remember 或 flarum_session"}

        before = self._fetch_state(session)
        if before and before.get("canCheckin") is False and self._is_today(before):
            self.log.info("站点状态显示今日已签到，跳过重复签到")
            return {"ok": True, "already": True, "state": before, "channel": channel}

        resp = self._http(
            "POST",
            self.site_base + "/api/checkin",
            headers=self._api_headers(session["csrf"]),
            cookies=cookies,
        )
        if resp.status is None:
            return {"ok": False, "reason": "签到请求无响应（%s）" % (resp.error or "未知错误")}
        if resp.status != 200:
            detail = self._error_from(resp)
            self.log.warn("签到接口返回 HTTP %s：%s" % (resp.status, detail))
            after = self._fetch_state(session)
            if after and after.get("canCheckin") is False and self._is_today(after):
                self.log.info("站点状态显示今日已签到")
                return {"ok": True, "already": True, "state": after, "channel": channel}
            return {"ok": False, "reason": "HTTP %s：%s" % (resp.status, detail)}

        state = self._extract_state(resp.json_data or {})
        if not state:
            return {"ok": False, "reason": "签到响应缺少用户状态数据"}
        if state.get("canCheckin") is not False or not self._is_today(state):
            return {"ok": False, "reason": "签到响应未确认今日已签到"}

        self.log.info("签到成功")
        return {"ok": True, "already": False, "state": state, "channel": channel}

    def _checkin_with_cookie(self):
        session, reason = self._session_from_cookie()
        if not session:
            return {"ok": False, "reason": reason}
        return self._perform_checkin(session, "cookie")

    def _checkin_with_login(self):
        session, reason = self._session_from_login()
        if not session:
            return {"ok": False, "reason": reason}
        return self._perform_checkin(session, "login")

    # -- 本地历史 ----------------------------------------------------------

    def _history_path(self):
        return self.data_dir / HISTORY_FILE

    def _load_history(self):
        try:
            raw = json.loads(self._history_path().read_text(encoding="utf-8"))
            return raw if isinstance(raw, list) else []
        except (OSError, ValueError, TypeError):
            return []

    def _save_history(self, records):
        try:
            self._history_path().write_text(
                json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        except OSError as exc:
            self.log.warn("写入签到历史失败：%s" % exc)

    def _record_history(self, state, status, func, detail=""):
        when = str((state or {}).get("lastCheckinTime") or "")
        if not when:
            when = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        day = when[:10]

        records = [r for r in self._load_history() if isinstance(r, dict)]
        records = [r for r in records if not str(r.get("date", "")).startswith(day)]
        records.append({
            "date": when,
            "status": status,
            "func": func,
            "totalContinuousCheckIn": (state or {}).get("totalContinuousCheckIn"),
            "money": (state or {}).get("money"),
            "detail": detail,
        })

        cutoff = datetime.now() - timedelta(days=self.history_days)
        kept = []
        for record in records:
            try:
                if datetime.strptime(str(record["date"])[:19], "%Y-%m-%d %H:%M:%S") >= cutoff:
                    kept.append(record)
            except Exception:
                continue
        kept.sort(key=lambda r: str(r.get("date") or ""), reverse=True)
        self._save_history(kept)
        return kept

    # -- 通知 --------------------------------------------------------------

    def _notify(self, body):
        """通过 TgtoDrive 已配置的通知机器人推送消息。"""
        if not self.notify_enabled:
            self.log.info("已关闭结果通知，跳过推送")
            return False, "disabled"

        bots, _, failure = self._read_bots()
        if failure:
            return False, failure
        if not bots:
            self.log.warn("TgtoDrive 配置中未读取到任何通知机器人，本次跳过通知")
            return False, "bot-not-found"

        bot = self._select_bot(bots)
        if bot is None:
            self.log.warn("读取到的机器人条目都缺少 Token 或推送目标 ID，本次跳过通知")
            return False, "bot-not-found"

        self.log.info("使用通知机器人「%s」（列表第 %s 项，来源 %s）"
                      % (bot.get("name"), bot.get("index"), bot.get("source") or "-"))
        proxy = bot.get("proxy") or self._resolve_proxy()
        proxies = {"http": proxy, "https": proxy} if proxy else None
        text = "%s\n%s" % (NOTIFY_TITLE, body)

        try:
            import requests

            resp = requests.post(
                "%s/bot%s/sendMessage" % (TELEGRAM_API, bot["token"]),
                json={
                    "chat_id": bot["chat_id"],
                    "text": text,
                    "disable_web_page_preview": True,
                },
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                proxies=proxies,
                allow_redirects=False,
            )
        except Exception as exc:
            self.log.warn("发送 Telegram 通知失败：%s"
                          % scrub_text(exc, [bot.get("token")]))
            return False, "send-error"

        if not 200 <= resp.status_code < 300:
            self.log.warn("发送 Telegram 通知失败：HTTP %s" % resp.status_code)
            return False, "send-http-%s" % resp.status_code
        try:
            payload = resp.json() or {}
        except Exception:
            payload = {}
        if payload.get("ok") is False:
            self.log.warn("Telegram 返回失败：%s" % payload.get("description"))
            return False, "telegram-rejected"

        self._last_bot_name = str(bot.get("name") or "")
        self._last_bot_index = bot.get("index")
        self.log.info("通知已通过「%s」发送成功" % (bot.get("name") or "通知机器人"))
        return True, "sent"

    # -- 微信通知（调用企业微信通知插件）--------------------------------------

    def _notify_wecom(self, title, items):
        """通过 TgtoDrive OpenAPI 调用「企业微信通知」插件发送一条微信通知。

        ``items`` 为 ``[(键, 值), ...]``：text 模式拼成多行文本，
        template_card 模式作为卡片的键值列表。
        企业 ID / Secret 等凭据不在这里传，由 wecom-notify 里已保存的设置提供。
        """
        if not self.wecom_notify:
            self._wecom_state = "disabled"
            return False

        base = str(self.tgto_base_url or os.environ.get("TGTO_OPENAPI_BASE_URL", "")).strip()
        token = str(self.tgto_token or os.environ.get("TGTO_OPENAPI_TOKEN", "")).strip()
        base = base.rstrip("/")
        if not base or not token:
            self.log.warn("已开启微信通知，但未配置「TgtoDrive 地址」或「OpenAPI 令牌」，"
                          "本次跳过微信通知")
            self._wecom_state = "no-endpoint"
            return False

        params = {"func": "send", "msgtype": self.wecom_msgtype}
        if self.wecom_touser:
            params["touser"] = self.wecom_touser
        if self.wecom_msgtype == "template_card":
            params["title"] = "%s %s" % (WECOM_CARD_TITLE, title)
            params["card_content"] = "\n".join("%s=%s" % (key, value) for key, value in items)
            if self.wecom_card_image:
                params["card_image"] = self.wecom_card_image
        else:
            lines = ["%s%s" % (WECOM_TITLE, title)]
            lines.extend("%s：%s" % (key, value) for key, value in items)
            params["content"] = "\n".join(lines)

        url = "%s/api/toolbox/plugins/%s/run" % (base, WECOM_PLUGIN_ID)
        self.log.info("调用「%s」插件发送微信通知（%s 类型）" % (WECOM_PLUGIN_ID, self.wecom_msgtype))
        try:
            import requests

            resp = requests.post(
                url,
                headers={"Authorization": "Bearer %s" % token},
                json={"params": params},
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                allow_redirects=False,
            )
        except Exception as exc:
            self.log.warn("调用企业微信通知插件失败：%s" % exc)
            self._wecom_state = "call-error"
            return False

        if resp.status_code not in (200, 201, 202):
            hint = ""
            if resp.status_code == 404:
                hint = ("（未找到插件「%s」：请在「实用工具 → 我的插件」确认它已安装并启用）"
                        % WECOM_PLUGIN_ID)
            elif resp.status_code in (401, 403):
                hint = "（OpenAPI 令牌无效或权限不足）"
            elif resp.status_code == 400:
                hint = "（参数被拒绝：请确认「%s」插件已更新到较新版本）" % WECOM_PLUGIN_ID
            self.log.warn("调用企业微信通知插件失败：HTTP %s%s｜%s"
                          % (resp.status_code, hint, (resp.text or "")[:160]))
            self._wecom_state = "http-%s" % resp.status_code
            return False

        try:
            payload = resp.json() or {}
        except Exception:
            payload = {}

        job_id = payload.get("job_id") or payload.get("id") or payload.get("task_id")
        if not job_id:
            self.log.info("微信通知任务已提交（响应未包含 job_id，视为已受理）")
            self._wecom_state = "submitted"
            return True

        self.log.info("微信通知任务已提交，job_id=%s" % job_id)
        ok, note = self._poll_wecom_job(base, token, job_id)
        if ok is True:
            self.log.info("微信通知发送成功")
            self._wecom_state = "sent"
            return True
        if ok is False:
            self.log.warn("微信通知发送失败：%s" % note)
            self._wecom_state = "failed"
            self._wecom_error = note
            return False
        self.log.info("未在等待时间内取到微信通知结果（任务仍在后台执行）")
        self._wecom_state = "pending"
        return True

    def _poll_wecom_job(self, base, token, job_id):
        """轮询 wecom-notify 的任务结果，返回 ``(True/False/None, 说明)``。"""
        url = "%s/api/toolbox/plugins/jobs/%s" % (base, job_id)
        headers = {"Authorization": "Bearer %s" % token}
        for attempt in range(WECOM_JOB_POLL_ATTEMPTS):
            if attempt:
                time.sleep(WECOM_JOB_POLL_INTERVAL)
            try:
                import requests

                resp = requests.get(url, headers=headers,
                                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                                    allow_redirects=False)
                data = resp.json() or {}
            except Exception:
                continue

            if not isinstance(data, dict):
                continue
            result = data.get("result")
            if not isinstance(result, dict):
                result = data
            status = str(result.get("status") or "").strip().lower()
            if status in ("ok", "success", "done", "completed"):
                return True, "sent"
            if status in ("failed", "error", "failure"):
                return False, str(result.get("error") or "发送失败")
        return None, "pending"

    # 微信通知状态 → 结果表文案。
    # 必须覆盖 _notify_wecom 会设置的**每一个**取值：漏掉一个，它就会落到兜底文案上、
    # 把真实原因吞掉（「http-404」此前被显示成「本次未发送」，导致无法定位问题）。
    WECOM_STATE_LABELS = {
        "sent": "已发送",
        "submitted": "已提交",
        "pending": "已提交（后台执行，未确认结果）",
        "no-endpoint": "未配置「TgtoDrive 地址」或「OpenAPI 令牌」（见「通知与接口」页签）",
        "call-error": "调用失败（网络错误，详见运行日志）",
        "failed": "发送失败（详见运行日志）",
        "disabled": "未启用",
        "not-called": "本次执行的功能不发送通知（仅签到会发）",
    }

    WECOM_HTTP_HINTS = {
        "404": "未找到「企业微信通知」插件 —— 请在「我的插件」确认它已安装并启用",
        "401": "OpenAPI 令牌无效或已撤销",
        "403": "OpenAPI 令牌权限不足",
        "400": "参数被拒绝 —— 通常是「企业微信通知」插件版本过旧",
        "503": "TgtoDrive 服务暂时不可用",
    }

    def _wecom_row(self):
        """结果表里的「微信通知」一行：每种原因都要能唯一显示出来。"""
        if not self.wecom_notify:
            return "未启用（勾选「同时发送微信通知」后生效）"
        state = self._wecom_state or "not-called"
        if state.startswith("http-"):
            code = state[len("http-"):]
            hint = self.WECOM_HTTP_HINTS.get(code)
            return "调用失败 HTTP %s%s" % (code, "：" + hint if hint else "")
        if state == "failed" and self._wecom_error:
            return "发送失败：%s" % str(self._wecom_error)[:120]
        label = self.WECOM_STATE_LABELS.get(state)
        if label is None:
            return "未知状态「%s」（请把这一行反馈给插件作者）" % state
        return label

    # -- 结果装配 ----------------------------------------------------------

    def _status_alert(self, ok, already, failed=False):
        if failed:
            return {"type": "alert", "text": "❌ 签到失败", "style": {"tone": "danger"}}
        if already:
            return {"type": "alert", "text": "✅ 今日已签到（无需重复）", "style": {"tone": "success"}}
        if ok:
            return {"type": "alert", "text": "✅ 签到成功", "style": {"tone": "success"}}
        return {"type": "alert", "text": "ℹ️ 执行完成", "style": {"tone": "default"}}

    def _base_ui(self, status_component, rows, table_label="本次执行详情"):
        components = [
            {"type": "heading", "text": "药丸论坛签到 · 执行结果"},
            status_component,
            {"type": "table", "label": table_label,
             "headers": ["项目", "值"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {"width": "wide", "layout": "stack", "components": components}

    def _common_rows(self):
        proxy = self._resolve_proxy()
        return [
            ["执行功能", FUNC_LABELS.get(self.func, self.func)],
            ["站点地址", self.site_base],
            ["网络代理", _mask_proxy(proxy) if proxy else "未使用"],
            ["浏览器指纹", "已启用" if self.use_fingerprint else "未启用"],
            ["通知机器人", self._notify_bot_row()],
            ["微信通知", self._wecom_row()],
        ]

    def _notify_bot_row(self):
        """结果表里的「通知机器人」一行：优先显示最近一次实际发送所用的机器人。"""
        if self._last_bot_name:
            suffix = "（列表第 %s 项）" % self._last_bot_index if self._last_bot_index else ""
            return "%s%s" % (self._last_bot_name, suffix)
        return "%s（本次未发送）" % _notify_bot_label(self.notify_bot)

    # -- 各功能入口 --------------------------------------------------------

    def _view_history(self):
        records = [r for r in self._load_history() if isinstance(r, dict)]
        records.sort(key=lambda r: str(r.get("date") or ""), reverse=True)
        displayed = records[:200]

        rows = []
        for record in displayed:
            status = {"signed": "已签到", "already": "今日已签到", "failed": "签到失败"}.get(
                str(record.get("status") or ""), str(record.get("status") or "-"))
            rows.append([
                str(record.get("date") or "-"),
                status,
                "%s 天" % (record.get("totalContinuousCheckIn")
                           if record.get("totalContinuousCheckIn") is not None else "-"),
                "%s 个" % (record.get("money") if record.get("money") is not None else "-"),
            ])
        if not rows:
            rows = [["暂无记录", "-", "-", "-"]]

        self.log.info("读取本地签到历史 %d 条" % len(displayed))
        components = [
            {"type": "heading", "text": "签到历史（本地记录）"},
            {"type": "table", "label": "最近 %d 条，保留 %d 天" % (len(rows), self.history_days),
             "headers": ["签到时间", "状态", "累计天数", "剩余药丸"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok",
            "func": self.func,
            "history_count": len(records),
            "notified": False,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def _view_bots(self):
        """读取并展示 TgtoDrive 已配置的通知机器人，供选择下拉框的序号对照。"""
        bots, _, failure = self._read_bots()

        rows = []
        for bot in bots:
            has_token = bool(bot.get("token"))
            has_target = bool(bot.get("chat_id"))
            if has_token and has_target:
                state = "可用"
            elif has_token:
                state = "缺少推送目标 ID"
            elif has_target:
                state = "缺少机器人 Token"
            else:
                state = "信息不完整"
            rows.append([
                str(bot.get("index")),
                str(bot.get("name") or "-"),
                state,
                _mask_id(bot.get("chat_id")),
                str(bot.get("source") or "-"),
            ])
        if not rows:
            rows = [["-", "未读取到机器人", "-", "-", "-"]]

        components = [{"type": "heading", "text": "TgtoDrive 通知机器人列表"}]
        if failure == "openapi-not-configured":
            components.append({
                "type": "alert",
                "text": "未配置 TgtoDrive 地址或 OpenAPI 令牌，无法读取机器人列表。"
                        "请在「通知与接口」页填写，或配置容器环境变量 "
                        "TGTO_OPENAPI_BASE_URL / TGTO_OPENAPI_TOKEN 后重启服务。",
                "style": {"tone": "warning"},
            })
        elif not bots:
            components.append({
                "type": "alert",
                "text": "接口可访问，但返回内容中没有识别到机器人条目，"
                        "请确认项目里已在「通知机器人」页面配置好机器人。",
                "style": {"tone": "warning"},
            })
        else:
            components.append({
                "type": "alert",
                "text": "表格中的「序号」就是「通知机器人」下拉框的选项值。"
                        "可直接点击下方按钮，用对应机器人发送一条测试通知。",
                "style": {"tone": "default"},
            })

        components.append({
            "type": "table",
            "label": "机器人列表（共 %d 条）" % len(bots),
            "headers": ["序号", "名称", "状态", "推送目标", "来源"],
            "rows": rows,
        })

        buttons = []
        for bot in bots[:NOTIFY_BOT_MAX_INDEX]:
            if not (bot.get("token") and bot.get("chat_id")):
                continue
            buttons.append({
                "type": "button",
                "label": "用「%s」发送测试通知" % bot.get("name"),
                "action": "run",
                "params": {
                    "func": "test_notify",
                    "notify": True,
                    "notify_bot": "index:%s" % bot.get("index"),
                },
                "style": {"tone": "default", "variant": "outline", "size": "small"},
            })
        if buttons:
            components.append({"type": "divider"})
            components.append({"type": "grid", "columns": 1, "children": buttons})

        components.append({"type": "divider"})
        components.append({"type": "heading", "text": "运行日志"})
        components.append({"type": "code", "text": self.log.text()})

        return {
            "status": "ok",
            "func": self.func,
            "bot_count": len(bots),
            "bots": [
                {
                    "index": bot.get("index"),
                    "name": bot.get("name"),
                    "usable": bool(bot.get("token") and bot.get("chat_id")),
                    "source": bot.get("source"),
                }
                for bot in bots
            ],
            "notified": False,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def _test_notify(self):
        """发送一条测试通知，用于验证通知链路与所选机器人。"""
        if not self.notify_enabled:
            self.log.info("「发送测试通知」为手动测试动作，本次忽略「发送结果通知」开关，仍然发送")
        self.notify_enabled = True
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            "━━━━━━━━━━━━━━\n"
            "✨ 本条为测试消息\n"
            "━━━━━━━━━━━━━━\n"
            "📌 来源：药丸签到插件\n"
            "🕐 时间：%s"
        ) % now

        # 勾选了「同时发送微信通知」时，测试通知也要走一遍微信链路 ——
        # 否则用户在结果表里只会看到「微信通知 本次未发送」，无从验证这条配置。
        self._notify_wecom("测试通知", [
            ("状态", "✅ 测试通知"),
            ("来源", "药丸签到插件"),
            ("时间", now),
        ])

        notified, notify_state = self._notify(body)
        if notified:
            self.log.info("测试通知发送完成")
        else:
            self.log.warn("测试通知未发送（%s）" % notify_state)

        rows = self._common_rows() + [
            ["执行结果", "测试通知已发送" if notified else "测试通知未发送"],
            ["通知状态", "已发送" if notified else "未发送（%s）" % notify_state],
        ]
        if notified:
            status_component = {"type": "alert", "text": "✅ 测试通知已发送",
                                "style": {"tone": "success"}}
        else:
            status_component = {"type": "alert", "text": "⚠️ 测试通知未发送",
                                "style": {"tone": "warning"}}
        ui = self._base_ui(status_component, rows, table_label="测试通知详情")
        return {
            "status": "ok" if notified else "failed",
            "func": self.func,
            "notified": notified,
            "notify_state": notify_state,
            "bot": self._last_bot_name or None,
            "ui": ui,
        }

    def _query_status(self):
        session = None
        channel = None
        session, reason = self._session_from_cookie()
        if session:
            channel = "cookie"
        else:
            self.log.warn("Cookie 通道不可用（%s），尝试账号密码登录" % reason)
            session, reason = self._session_from_login()
            channel = "login" if session else None

        if not session:
            return self._result_failed("无法建立登录会话：%s" % reason)

        state = self._fetch_state(session)
        if not state:
            return self._result_failed("查询签到状态失败，请检查 Cookie / 账号是否有效")

        can = state.get("canCheckin")
        today = self._is_today(state)
        self.log.info("签到状态：canCheckin=%s，lastCheckinTime=%s" % (can, state.get("lastCheckinTime")))

        rows = self._common_rows() + [
            ["会话来源", "Cookie" if channel == "cookie" else "账号密码登录"],
            ["今日是否已签到", "是" if (can is False and today) else "否"],
            ["canCheckin", str(can)],
            ["最近签到时间", str(state.get("lastCheckinTime") or "-")],
            ["累计签到天数", str(state.get("totalContinuousCheckIn"))],
            ["剩余药丸", str(state.get("money"))],
        ]
        ui = self._base_ui(
            {"type": "alert",
             "text": "📊 状态查询完成：%s" % ("今日已签到" if (can is False and today) else "今日尚未签到"),
             "style": {"tone": "success" if (can is False and today) else "warning"}},
            rows,
            table_label="签到状态",
        )
        return {
            "status": "ok",
            "func": self.func,
            "state": {
                "can_checkin": can,
                "last_checkin_time": str(state.get("lastCheckinTime") or ""),
                "total_continuous_check_in": state.get("totalContinuousCheckIn"),
                "money": state.get("money"),
            },
            "notified": False,
            "ui": ui,
        }

    def _result_failed(self, reason):
        self.log.error(reason)
        notified, notify_state = self._notify_failure(reason)
        rows = self._common_rows() + [
            ["执行结果", "失败"],
            ["失败原因", reason],
            ["通知状态", "已发送" if notified else "未发送（%s）" % notify_state],
        ]
        ui = self._base_ui(self._status_alert(False, False, failed=True), rows)
        return {
            "status": "failed",
            "func": self.func,
            "error": reason,
            "notified": notified,
            "ui": ui,
        }

    def _notify_failure(self, reason):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            "━━━━━━━━━━━━━━\n"
            "✨ 状态：❌签到失败\n"
            "━━━━━━━━━━━━━━\n"
            "❗ 原因：%s\n"
            "━━━━━━━━━━━━━━\n"
            "🕐 时间：%s"
        ) % (reason, now)
        self._notify_wecom("签到失败", [
            ("状态", "❌ 签到失败"),
            ("原因", reason),
            ("时间", now),
        ])
        return self._notify(body)

    def _notify_success(self, state, already):
        status_text = "✅今日已签到" if already else "✅已签到"
        money = (state or {}).get("money")
        continuous = (state or {}).get("totalContinuousCheckIn")
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            "━━━━━━━━━━━━━━\n"
            "✨ 状态：%s\n"
            "━━━━━━━━━━━━━━\n"
            "📊 数据统计\n"
            "💊 剩余药丸：%s\n"
            "📆 累计签到：%s天\n"
            "━━━━━━━━━━━━━━\n"
            "🕐 签到时间：%s"
        ) % (status_text, money, continuous, now)
        self._notify_wecom("今日已签到" if already else "签到成功", [
            ("状态", status_text),
            ("剩余药丸", money),
            ("累计签到", "%s 天" % continuous),
            ("时间", now),
        ])
        return self._notify(body)

    def _do_signin(self):
        use_cookie = self.func in ("auto", "cookie")
        use_login = self.func in ("auto", "login")

        if use_cookie and not self.cookie_raw:
            if self.func == "cookie":
                raise ValueError("选择「仅用 Cookie 签到」时必须填写 Cookie")
            use_cookie = False
            self.log.warn("未填写 Cookie，跳过 Cookie 通道")
        if use_login and not (self.username and self.password):
            if self.func == "login":
                raise ValueError("选择「仅用账号密码登录签到」时必须填写用户名和密码")
            use_login = False
            self.log.warn("未填写用户名或密码，跳过登录通道")
        if not use_cookie and not use_login:
            raise ValueError("Cookie 与账号密码均未配置，无法执行签到")

        last_reason = "未知原因"
        for attempt in range(1, self.retry_count + 1):
            self.log.info("第 %d/%d 次签到尝试" % (attempt, self.retry_count))

            if use_cookie:
                result = self._checkin_with_cookie()
                if result.get("ok"):
                    return self._result_success(result, "Cookie")
                last_reason = result.get("reason") or "Cookie 通道失败"
                self.log.warn("Cookie 通道失败：%s" % last_reason)

            if use_login:
                result = self._checkin_with_login()
                if result.get("ok"):
                    return self._result_success(result, "账号密码登录")
                last_reason = result.get("reason") or "登录通道失败"
                self.log.warn("账号密码登录通道失败：%s" % last_reason)

            if attempt < self.retry_count and self.retry_interval > 0:
                self.log.info("%d 秒后进入第 %d 次重试" % (self.retry_interval, attempt + 1))
                time.sleep(self.retry_interval)

        self.log.error("已重试 %d 次仍未成功" % self.retry_count)
        return self._result_failed(last_reason)

    def _result_success(self, result, channel_label):
        state = result.get("state") or {}
        already = bool(result.get("already"))
        self._record_history(state, "already" if already else "signed", self.func,
                             "通道：%s" % channel_label)

        notified, notify_state = self._notify_success(state, already)

        rows = self._common_rows() + [
            ["签到状态", "今日已签到" if already else "已签到"],
            ["使用通道", channel_label],
            ["累计签到天数", str(state.get("totalContinuousCheckIn"))],
            ["剩余药丸", str(state.get("money"))],
            ["最近签到时间", str(state.get("lastCheckinTime") or "-")],
            ["通知状态", "已发送" if notified else "未发送（%s）" % notify_state],
        ]
        ui = self._base_ui(self._status_alert(True, already), rows)
        return {
            "status": "already" if already else "success",
            "func": self.func,
            "channel": channel_label,
            "state": {
                "user_id": str(state.get("user_id") or ""),
                "last_checkin_time": str(state.get("lastCheckinTime") or ""),
                "total_continuous_check_in": state.get("totalContinuousCheckIn"),
                "money": state.get("money"),
            },
            "notified": notified,
            "ui": ui,
        }

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        if self.func not in VALID_FUNCS:
            raise ValueError("不支持的执行功能：%s" % self.func)

        self.log.info("药丸论坛签到启动，执行功能：%s" % FUNC_LABELS.get(self.func, self.func))
        self._resolve_proxy()

        if self.func == "history":
            return self._view_history()
        if self.func == "bots":
            return self._view_bots()
        if self.func == "test_notify":
            return self._test_notify()
        if self.func == "status":
            return self._query_status()
        return self._do_signin()


def run(params, context):
    """TgtoDrive 插件入口：同步执行一次签到相关工作。"""
    runner = _SigninRunner(params, context)
    return runner.execute()
