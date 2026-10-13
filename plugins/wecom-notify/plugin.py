# -*- coding: utf-8 -*-
"""企业微信通知 · TgtoDrive Python 插件

为企业微信（WeCom / 原企业号）自建应用提供「应用消息推送」能力：
按企业微信官方接口 https://developer.work.weixin.qq.com/document 实现
`GET /cgi-bin/gettoken` 与 `POST /cgi-bin/message/send`。

能力
  * 发送消息：文本 / markdown / 文本卡片 / **卡片通知（模板卡片）** 四种类型，
    支持发给成员、部门、标签或 @all。
  * **卡片通知**：支持带图（图片 URL，或容器内本地图片自动上传换取 URL）、
    来源名称与图标、键值列表（最多 6 条）、点击跳转链接；
    可选文本通知型 text_notice 与图文展示型 news_notice。
  * 发送测试消息（界面顶部独立按钮）：按「文本消息内容」与「卡片消息内容」两个
    输入框自动决定发送条数 —— 两个都有内容就依次发送（间隔 3 秒，共两条通知），
    只有一条就只发一条，都没有则报错。
  * 检查配置：校验必填项格式并真实获取一次 access_token，给出剩余有效期。
  * 查询应用可见范围成员：拉取部门与成员列表，便于填写 UserID。
  * 查看发送历史：本地记录每次发送的类型、收件人、结果与错误码。
  * **查看调用方法**：输出「被其他插件调用」的参数表与示例，
    并给出仓库内 CALLING.md 的在线链接。

被其他插件调用
  * 入口：`POST {TGTO_OPENAPI_BASE_URL}/api/toolbox/plugins/wecom-notify/run`
    （Bearer 令牌鉴权，请求体 `{"params": {...}}`），结果通过
    `GET /api/toolbox/plugins/jobs/{job_id}` 查询。
  * 完整参数表、返回值结构、错误处理与可直接粘贴的示例见同目录 CALLING.md。

实现要点
  * access_token 按「代理地址 + 企业ID」缓存在 data_dir/token.json，
    提前 300 秒视为过期，避免频繁调用 gettoken 被限流。
  * 超长正文按行边界自动分段（每段不超 2048 字节，不切断 UTF-8 字符）。
  * 命中 60020（调用 IP 不在「企业可信IP」名单）时，从 errmsg 中提取实际出口 IP
    并给出「加入可信IP 或 填写代理地址」的处理建议。
  * 企业 ID / Secret 留空时，可选地从 TgtoDrive 已保存的项目设置中启发式读取微信渠道
    配置作为兜底（字段名不对外承诺，读不到时提示手工填写）。

运行环境
  * 仅标准库 + 容器已装的 requests（不可用时回退 urllib）。
  * 不安装依赖、不建虚拟环境、不导入 TgtoDrive 内部模块、不写插件源码目录。

凭据与安全
  * 企业 ID / Secret / EncodingAESKey / OpenAPI 令牌一律不写入运行日志与返回值，
    仅以「已填写（长度 N）」形式提示；返回值中的 corp_id 做掩码处理。
"""

# ---------------------------------------------------------------------------
# 关于插件清单
# ---------------------------------------------------------------------------
# 本文件是**插件包内入口**：清单写在同目录的 plugin.json 里，这里不写
# PLUGIN_MANIFEST。打包时 scripts/package_plugin.py 会把 plugin.json 的内容
# 内联到 dist/wecom-notify.py 的开头，生成可单独导入的单文件版。
#
# 若把本文件当作「Python 单文件」单独导入，TgtoDrive 会报
#   「Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典」
# 这是预期行为，不是插件损坏。请改用 dist/wecom-notify.py 或 dist/wecom-notify.zip。

import json
import re
import socket
import ssl
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

DEFAULT_API_BASE = "https://qyapi.weixin.qq.com"
DEFAULT_TGTO_BASE = "http://127.0.0.1:12366"

USER_AGENT = "TgtoDrive-WecomNotify/1.0 (+https://github.com/a2695154202/ttd-plugins)"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# 文本与 markdown 正文上限（企业微信文档：不超过 2048 字节）
MESSAGE_BYTE_LIMIT = 2048
# 文本卡片标题上限 128 字节，描述按 512 字节控制
TEXTCARD_TITLE_LIMIT = 128
TEXTCARD_DESC_LIMIT = 512

# access_token 有效期 7200 秒；提前 300 秒视为过期
TOKEN_REFRESH_AHEAD = 300
TOKEN_DEFAULT_TTL = 7200

TOKEN_FILE = "token.json"
HISTORY_FILE = "history.json"
HISTORY_MAX_RECORDS = 500

FUNC_LABELS = {
    "send": "发送消息",
    "test": "发送测试消息",
    "config": "检查配置",
    "users": "查询应用可见范围成员",
    "history": "查看发送历史",
    "docs": "查看调用方法",
}
VALID_FUNCS = tuple(FUNC_LABELS)

MSGTYPE_LABELS = {
    "text": "文本",
    "markdown": "markdown",
    "textcard": "文本卡片",
    "template_card": "卡片通知（模板卡片）",
}
VALID_MSGTYPES = tuple(MSGTYPE_LABELS)

CARD_TYPE_LABELS = {
    "text_notice": "文本通知型 text_notice（大图 + 键值列表）",
    "news_notice": "图文展示型 news_notice（大图 + 竖排图文）",
}
VALID_CARD_TYPES = tuple(CARD_TYPE_LABELS)

# 模板卡片各字段的企业微信侧建议上限；超出会被企业微信自行截断，
# 这里主动截断并在日志中说明，避免用户以为内容完整送达。
CARD_TITLE_LIMIT = 26
CARD_TITLE_DESC_LIMIT = 30
CARD_SOURCE_DESC_LIMIT = 20
CARD_SUB_TITLE_LIMIT = 112
CARD_KEYNAME_LIMIT = 5
CARD_VALUE_LIMIT = 30
CARD_ITEMS_MAX = 6
CARD_VERTICAL_MAX = 4
CARD_ASPECT_MIN = 1.3
CARD_ASPECT_MAX = 2.25
CARD_ASPECT_DEFAULT = 2.25
# card_action 在模板卡片中是必填项，缺省时回退到官方站点
CARD_DEFAULT_ACTION_URL = "https://work.weixin.qq.com"

# 被其他插件调用的方法说明（随仓库分发，供「查看调用方法」按钮指向）
DOCS_URL = ("https://github.com/a2695154202/ttd-plugins/blob/main/"
            "plugins/wecom-notify/CALLING.md")
DOCS_RAW_HINT = ("https://github.com/a2695154202/ttd-plugins/tree/main/"
                 "plugins/wecom-notify")

# 组装成 UTF-8 摘要出现在结果里的错误提示；errmsg 原样附在后面
ERRCODE_HINTS = {
    40001: "应用 Secret 不正确，或该应用的 Secret 已被重置，请重新复制「应用 Secret」",
    40013: "企业 ID（corpid）不正确，请核对管理后台「我的企业 → 企业信息」中的企业 ID",
    40014: "access_token 无效，请重试；若持续出现请点「检查配置」重新获取",
    41001: "缺少 access_token 参数",
    42001: "access_token 已过期，插件会自动重新获取后重试",
    45009: "接口调用超过限制，请降低发送频率（每应用每天有人次上限，单成员每分钟不超过 30 条）",
    60011: "没有权限操作指定的成员 / 部门 / 标签，请确认它们在该应用的可见范围内",
    60020: "调用 IP 不在该应用的「企业可信IP」名单内",
    81013: "成员 / 部门 / 标签参数不合法，请检查 UserID、部门 ID 与标签 ID",
    82001: "指定的接收者不存在或不在应用可见范围内",
    301002: "无权限，请确认应用已启用且可见范围包含接收者",
}

# 60020 的 errmsg 形如：
#   not allow to access from your ip, hint: [xxx], from ip: 1.2.3.4, more info at ...
FROM_IP_RE = re.compile(r"from ip:\s*([0-9a-fA-F:.]+)", re.IGNORECASE)

# EncodingAESKey 固定 43 位 Base64 字符
AES_KEY_RE = re.compile(r"^[A-Za-z0-9+/]{43}$")

# 企业 ID 常见形态：以 ww / wx 开头，总长 18 位左右；只做温和提示，不做硬校验
CORP_ID_RE = re.compile(r"^w[a-z0-9]{10,}$", re.IGNORECASE)

# 「发送测试消息」同时发送文本与卡片时，两条之间的间隔（秒）。
# 这是同一个任务内的发送间隔，不是等待下次执行，符合插件协议。
TEST_SEND_GAP_SECONDS = 3


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

class _Logger(object):
    """同时写入标准输出（TgtoDrive 运行日志）与内存缓冲区（结果内日志窗口）。"""

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
# 参数解析
# ---------------------------------------------------------------------------

def _s(params, key, default=""):
    value = params.get(key)
    if value is None:
        return default
    return str(value).strip()


def _b(params, key, default=False):
    value = params.get(key)
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in ("1", "true", "yes", "on", "y", "t", "是", "开启")


def _i(params, key, default):
    value = params.get(key)
    if value is None or value == "":
        return default
    try:
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def _f(params, key, default):
    value = params.get(key)
    if value is None or value == "":
        return default
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def _mask(value, head=3, tail=3):
    text = str(value or "")
    if not text:
        return "（未填写）"
    if len(text) <= head + tail:
        return text[0] + "*" * max(len(text) - 1, 0)
    return "%s…%s" % (text[:head], text[-tail:])


def _filled(value):
    text = str(value or "")
    return "已填写（长度 %d）" % len(text) if text else "（未填写）"


def _normalize_base(url):
    """规范化接口基础地址：补协议头、去尾部斜杠。"""
    text = str(url or "").strip()
    if not text:
        return DEFAULT_API_BASE
    if not re.match(r"^https?://", text, re.IGNORECASE):
        text = "https://" + text
    return text.rstrip("/")


# ---------------------------------------------------------------------------
# 脱敏与连通性自检
# ---------------------------------------------------------------------------

# 企业微信的接口把凭据放在 URL 查询串里（corpid / corpsecret / access_token），
# 而 requests 在抛异常时会**回显完整 URL** —— 不处理就会把应用 Secret 原样写进运行日志。
# 下面这条正则对所有 ``key=value`` 形式的敏感查询参数做兜底脱敏。
SENSITIVE_QUERY_RE = re.compile(
    r"(?i)\b(corpsecret|corpid|appsecret|access_token|encodingaeskey|secret|token)"
    r"=([^&\s'\"),\]]+)"
)

# Telegram 的 bot token 放在 URL **路径**里：/bot<数字>:<token>/sendMessage。
# 本插件不发 Telegram，但脱敏函数按通用实现，便于在多个插件间保持一致。
BOT_TOKEN_PATH_RE = re.compile(r"(/bot)(\d{4,}):([A-Za-z0-9_\-]{20,})")


def scrub_text(text, secrets=()):
    """抹掉文本中的凭据，返回可安全打印的字符串。

    三道防线：先按**已知明文**精确替换（可覆盖出现在任意位置的密钥），
    再处理 ``key=value`` 形式的查询串（corpid / corpsecret / access_token），
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


# 判断是否为网络层失败（而非企业微信返回的业务错误），用于决定是否值得做连通性自检
NETWORK_ERROR_HINTS = (
    "sslerror", "ssl:", "connectionerror", "connecttimeout", "readtimeout",
    "proxyerror", "newconnectionerror", "maxretries", "connectionrefused",
    "connectionreseterror", "connection aborted", "unexpected_eof",
    "name or service not known", "temporary failure in name resolution",
    "nodename nor servname", "certificate verify", "urlopen error",
    "getaddrinfo", "timed out",
)


def looks_like_network_error(error):
    text = str(error or "").lower()
    return any(hint in text for hint in NETWORK_ERROR_HINTS)


def probe_endpoint(api_base, timeout=6):
    """分层探测接口地址，定位问题卡在 DNS / TCP / TLS 的哪一层。

    返回若干行中文结论。仅在网络类失败时调用，把一句 ``SSLError``
    变成「卡在哪、为什么、下一步怎么办」。
    """
    parsed = urllib.parse.urlsplit(_normalize_base(api_base))
    host = parsed.hostname or ""
    scheme = (parsed.scheme or "https").lower()
    port = parsed.port or (443 if scheme == "https" else 80)

    if not host:
        return ["接口地址里解析不出主机名：%s" % api_base]

    lines = []
    try:
        infos = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
        ips = sorted({info[4][0] for info in infos})
        lines.append("DNS 解析成功（%s → %s）" % (host, "、".join(ips[:3])))
    except Exception as exc:
        lines.append("DNS 解析失败（%s）—— 容器内无法解析该域名，先确认地址拼写与 DNS" % exc)
        return lines

    try:
        with socket.create_connection((host, port), timeout=timeout):
            lines.append("TCP 连接成功（%s:%d）" % (host, port))
    except Exception as exc:
        lines.append("TCP 连接失败（%s:%d，%s）—— 端口不通或被防火墙拦截" % (host, port, exc))
        return lines

    if scheme == "https":
        try:
            context = ssl.create_default_context()
            with socket.create_connection((host, port), timeout=timeout) as raw:
                with context.wrap_socket(raw, server_hostname=host) as tls:
                    lines.append("TLS 握手成功（%s）" % (tls.version() or "未知协议版本"))
        except Exception as exc:
            lines.append("TLS 握手失败（%s: %s）—— TCP 能连上，但 HTTPS 建不起来"
                         % (type(exc).__name__, exc))
            lines.append("常见原因：该端口上并不是 HTTPS 服务（反向代理只监听 HTTP 或尚未就绪）、"
                         "证书不被信任，或中间设备按 SNI 切断了连接。")
            lines.append("若该地址实际只提供 HTTP，请把「接口地址」改成 http://%s" % host)
    return lines


def _write_text(path, text):
    """以 UTF-8 + LF 写入文本。

    不使用 ``Path.write_text(newline=...)``：该参数需要 Python 3.10+，
    而本插件声明的运行环境是 3.9+。
    """
    with open(str(path), "w", encoding="utf-8", newline="\n") as handle:
        handle.write(text)


def _split_ids(value):
    """把「a|b c,d」这类输入拆成 ID 列表。"""
    if not value:
        return []
    parts = re.split(r"[|,，;；\s]+", str(value).strip())
    return [p.strip() for p in parts if p.strip()]


def _split_content(text, limit_bytes=MESSAGE_BYTE_LIMIT):
    """按行边界把正文切成若干块，每块 UTF-8 字节数不超过 limit_bytes。"""
    normalized = str(text or "").replace("\r\n", "\n").replace("\r", "\n")
    if len(normalized.encode("utf-8")) <= limit_bytes:
        return [normalized]

    chunks = []
    current = ""
    for line in normalized.split("\n"):
        candidate = line if not current else current + "\n" + line
        if len(candidate.encode("utf-8")) <= limit_bytes:
            current = candidate
            continue
        if current:
            chunks.append(current)
            current = ""
        if len(line.encode("utf-8")) <= limit_bytes:
            current = line
            continue
        piece = ""
        for char in line:
            if len((piece + char).encode("utf-8")) > limit_bytes:
                chunks.append(piece)
                piece = char
            else:
                piece += char
        current = piece
    if current:
        chunks.append(current)
    return chunks or [""]


def _clip(text, limit):
    """按字符数截断，返回 (截断后的值, 是否发生过截断)。"""
    value = str(text or "").strip()
    if len(value) <= limit:
        return value, False
    return value[:limit], True


def _parse_card_items(text, limit=CARD_ITEMS_MAX):
    """把多行「键=值」文本解析成模板卡片的 horizontal_content_list。

    支持 ``键=值``、``键:值``、``键：值``，也支持用 ``|`` 分隔；空行与
    ``#`` 开头的行会被忽略。返回 ``(items, notes)``，notes 为需要写入日志的说明。
    """
    items = []
    notes = []
    for raw_line in str(text or "").replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s*[=：:]\s*|\s*\|\s*", line, maxsplit=1)
        if len(parts) < 2:
            notes.append("忽略无法解析的行（应为「键=值」）：%s" % line[:40])
            continue
        key = parts[0].strip()
        value = parts[1].strip()
        if not key:
            notes.append("忽略缺少键的行：%s" % line[:40])
            continue
        if len(items) >= limit:
            notes.append("键值条目超过 %d 条，已丢弃「%s」" % (limit, key))
            continue
        short_key, key_cut = _clip(key, CARD_KEYNAME_LIMIT)
        short_value, value_cut = _clip(value, CARD_VALUE_LIMIT)
        if key_cut:
            notes.append("键「%s」超过 %d 字，截断为「%s」"
                         % (key, CARD_KEYNAME_LIMIT, short_key))
        if value_cut:
            notes.append("「%s」的值超过 %d 字，已截断（企业微信侧同样会截断）"
                         % (short_key, CARD_VALUE_LIMIT))
        items.append({"keyname": short_key, "value": short_value})
    return items, notes


def _looks_like_url(value):
    return bool(re.match(r"^https?://", str(value or "").strip(), re.IGNORECASE))


def _is_private_host(url):
    """判断 URL 是否指向内网 / 本机地址。

    企业微信服务器无法访问这类地址，卡片图片必须先由插件下载后上传换取可用 URL。
    """
    try:
        host = (urllib.parse.urlparse(str(url or "")).hostname or "").lower()
    except ValueError:
        return False
    if not host:
        return False
    if host in ("localhost", "127.0.0.1", "::1", "0.0.0.0"):
        return True
    if host.endswith(".local") or host.endswith(".lan") or host.endswith(".internal"):
        return True
    match = re.match(r"^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$", host)
    if not match:
        return False
    first, second = int(match.group(1)), int(match.group(2))
    if first == 10:
        return True
    if first == 192 and second == 168:
        return True
    if first == 172 and 16 <= second <= 31:
        return True
    if first == 169 and second == 254:
        return True
    return False


def _http_download(url, max_bytes=2 * 1024 * 1024, timeout=None):
    """下载 URL 内容并限制大小（企业微信上传图片上限 2 MB）。返回 (bytes, error)。"""
    timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
    if requests is not None:
        try:
            response = requests.get(url, timeout=timeout, stream=True,
                                    headers={"User-Agent": USER_AGENT})
            if response.status_code != 200:
                return None, "HTTP %s" % response.status_code
            data = response.content
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)
    else:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout[1]) as response:
                data = response.read(max_bytes + 1)
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)

    if len(data) > max_bytes:
        return None, "图片超过 %d KB" % (max_bytes // 1024)
    if not data:
        return None, "下载到的内容为空"
    return data, None


# ---------------------------------------------------------------------------
# HTTP
# ---------------------------------------------------------------------------

def _http_request(method, url, params=None, body=None, timeout=None, use_proxy=False):
    """发起一次 HTTP 请求。

    返回 ``(status, text, data, error)``；``data`` 仅在响应体是 JSON 时非 None，
    ``error`` 仅在网络层失败时非 None（**已脱敏**）。

    ``use_proxy=False``（默认）会**显式绕过容器环境变量里的代理**：企业微信自建应用
    常配合只允许特定地区访问的转发地址，请求被送去代理会直接连不通
    （典型表现是 SSL 握手阶段的 ``UNEXPECTED_EOF_WHILE_READING``）。
    """
    timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
    # 必须显式给出这两个键（值为 None 也要给）：requests 合并环境代理时用的是
    # setdefault，键存在才不会被 HTTP_PROXY / HTTPS_PROXY 覆盖。
    proxies = None if use_proxy else {"http": None, "https": None}

    if requests is not None:
        try:
            response = requests.request(
                method, url, params=params, json=body,
                timeout=timeout, headers={"User-Agent": USER_AGENT},
                proxies=proxies,
            )
            text = response.text or ""
            data = None
            try:
                data = response.json()
            except ValueError:
                data = None
            return response.status_code, text, data, None
        except Exception as exc:
            return None, "", None, scrub_text("%s: %s" % (type(exc).__name__, exc))

    target = url
    if params:
        target = url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    payload = None
    headers = {"User-Agent": USER_AGENT}
    if body is not None:
        payload = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers["Content-Type"] = "application/json; charset=utf-8"

    request = urllib.request.Request(target, data=payload, headers=headers, method=method)
    # ProxyHandler({}) 会禁用环境变量代理；需要走代理时才用默认的 opener
    opener = (urllib.request.build_opener() if use_proxy
              else urllib.request.build_opener(urllib.request.ProxyHandler({})))
    try:
        with opener.open(request, timeout=timeout[1]) as response:
            raw = response.read().decode("utf-8", "replace")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    except Exception as exc:
        return None, "", None, scrub_text("%s: %s" % (type(exc).__name__, exc))

    data = None
    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    return status, raw, data, None


def _http_upload(url, file_path, timeout=None, use_proxy=False):
    """以 multipart/form-data 上传本地文件（字段名 ``media``）。

    返回结构同 :func:`_http_request`。用于把容器内的本地图片换成企业微信可用的图片 URL。
    ``use_proxy`` 语义同 :func:`_http_request`。
    """
    timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
    proxies = None if use_proxy else {"http": None, "https": None}
    path = Path(file_path)
    try:
        content = path.read_bytes()
    except OSError as exc:
        return None, "", None, "读取本地图片失败：%s" % exc

    suffix = path.suffix.lower().lstrip(".") or "jpg"
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
            "png": "image/png", "gif": "image/gif"}.get(suffix, "application/octet-stream")
    filename = path.name or ("image." + suffix)

    if requests is not None:
        try:
            response = requests.post(
                url, files={"media": (filename, content, mime)},
                timeout=timeout, headers={"User-Agent": USER_AGENT},
                proxies=proxies,
            )
            text = response.text or ""
            try:
                data = response.json()
            except ValueError:
                data = None
            return response.status_code, text, data, None
        except Exception as exc:
            return None, "", None, scrub_text("%s: %s" % (type(exc).__name__, exc))

    boundary = "----TgtoDriveWecomNotify%s" % int(time.time() * 1000)
    body = b"".join([
        ("--%s\r\n" % boundary).encode("utf-8"),
        ('Content-Disposition: form-data; name="media"; filename="%s"\r\n'
         % filename).encode("utf-8"),
        ("Content-Type: %s\r\n\r\n" % mime).encode("utf-8"),
        content,
        ("\r\n--%s--\r\n" % boundary).encode("utf-8"),
    ])
    request = urllib.request.Request(
        url, data=body, method="POST",
        headers={"User-Agent": USER_AGENT,
                 "Content-Type": "multipart/form-data; boundary=%s" % boundary},
    )
    opener = (urllib.request.build_opener() if use_proxy
              else urllib.request.build_opener(urllib.request.ProxyHandler({})))
    try:
        with opener.open(request, timeout=timeout[1]) as response:
            raw = response.read().decode("utf-8", "replace")
            status = response.status
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", "replace")
        status = exc.code
    except Exception as exc:
        return None, "", None, scrub_text("%s: %s" % (type(exc).__name__, exc))

    try:
        data = json.loads(raw)
    except ValueError:
        data = None
    return status, raw, data, None


# ---------------------------------------------------------------------------
# 企业微信客户端
# ---------------------------------------------------------------------------

class _WecomClient(object):
    """企业微信自建应用接口客户端：access_token 缓存 + 应用消息发送。"""

    def __init__(self, api_base, corp_id, corp_secret, agent_id, logger, data_dir,
                 use_proxy=False):
        self.api_base = _normalize_base(api_base)
        self.corp_id = str(corp_id or "").strip()
        self.corp_secret = str(corp_secret or "").strip()
        self.agent_id = str(agent_id or "").strip()
        self.log = logger
        self.token_path = Path(data_dir) / TOKEN_FILE
        self.cache_key = "%s|%s" % (self.api_base, self.corp_id)
        # 是否跟随容器环境变量里的代理；默认直连（原因见 _http_request 的说明）
        self.use_proxy = bool(use_proxy)

    # -- 地址 --------------------------------------------------------------

    def url(self, path):
        return self.api_base + path

    def masked_base(self):
        return self.api_base

    # -- access_token ------------------------------------------------------

    def _read_cache(self):
        try:
            if not self.token_path.is_file():
                return {}
            data = json.loads(self.token_path.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {}
        except (OSError, ValueError):
            return {}

    def _write_cache(self, token, expires_at):
        payload = {
            "key": self.cache_key,
            "access_token": token,
            "expires_at": expires_at,
            "saved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }
        try:
            _write_text(self.token_path, json.dumps(payload, ensure_ascii=False, indent=2))
        except OSError as exc:
            self.log.warn("access_token 缓存写入失败（不影响本次发送）：%s" % exc)

    def clear_cache(self):
        try:
            if self.token_path.is_file():
                self.token_path.unlink()
        except OSError:
            pass

    def cached_token(self):
        """返回仍有效的缓存 token 与剩余秒数，没有则返回 (None, 0)。"""
        cached = self._read_cache()
        if cached.get("key") != self.cache_key:
            return None, 0
        remain = int(cached.get("expires_at") or 0) - int(time.time())
        if remain > TOKEN_REFRESH_AHEAD:
            return cached.get("access_token"), remain
        return None, 0

    def get_token(self, force=False):
        """返回 ``(access_token, error)``。"""
        if not self.corp_id:
            return None, "未填写「企业 ID」，请在「应用配置」页签填写"
        if not self.corp_secret:
            return None, "未填写「应用 Secret」，请在「应用配置」页签填写"

        if not force:
            token, remain = self.cached_token()
            if token:
                self.log.info("复用本地缓存的 access_token（剩余 %d 秒）" % remain)
                return token, None

        status, text, data, error = _http_request(
            "GET", self.url("/cgi-bin/gettoken"),
            params={"corpid": self.corp_id, "corpsecret": self.corp_secret},
            use_proxy=self.use_proxy,
        )
        if error:
            message = "请求 gettoken 失败：%s（接口地址 %s，%s）" % (
                scrub_text(error, [self.corp_secret, self.corp_id]),
                self.api_base,
                "跟随环境变量代理" if self.use_proxy else "已绕过代理直连")
            if looks_like_network_error(error):
                lines = probe_endpoint(self.api_base)
                message += "\n连通性自检（直连，不经过代理）：\n  - " + "\n  - ".join(lines)
                if self.use_proxy and lines and not any("失败" in line for line in lines):
                    message += ("\n注意：直连探测全部通过，而本次请求走了代理 —— "
                                "失败很可能是代理访问不了该地址造成的，"
                                "可把「网络代理」改成「不使用代理（直连）」。")
            return None, message
        if not isinstance(data, dict):
            return None, "gettoken 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:200])

        errcode = data.get("errcode")
        if errcode not in (0, None):
            return None, self.describe_error(errcode, data.get("errmsg", ""), stage="gettoken")

        token = data.get("access_token")
        if not token:
            return None, "gettoken 未返回 access_token：%s" % (text or "")[:200]

        try:
            ttl = int(data.get("expires_in") or TOKEN_DEFAULT_TTL)
        except (TypeError, ValueError):
            ttl = TOKEN_DEFAULT_TTL
        self._write_cache(token, int(time.time()) + ttl)
        self.log.info("获取 access_token 成功，有效期 %d 秒" % ttl)
        return token, None

    # -- 错误解释 ----------------------------------------------------------

    @staticmethod
    def _norm_code(errcode):
        try:
            return int(errcode)
        except (TypeError, ValueError):
            return None

    def describe_error(self, errcode, errmsg, stage=""):
        """把 errcode / errmsg 转成一句中文可读的失败原因。"""
        errmsg = str(errmsg or "")
        code = self._norm_code(errcode)
        parts = []
        if stage:
            parts.append("在 %s 阶段失败" % stage)
        parts.append("errcode=%s" % errcode)

        hint = ERRCODE_HINTS.get(code)
        if hint:
            parts.append(hint)

        if code == 60020:
            match = FROM_IP_RE.search(errmsg)
            if match:
                parts.append("检测到本次调用的出口 IP 为 %s" % match.group(1))
            parts.append(
                "处理方式二选一：① 到企业微信管理后台「应用管理 → 自建应用 → 企业可信IP」"
                "把上述 IP 加入白名单（配置后约 1 分钟生效）；"
                "② 在「应用配置 → 代理地址」填写转发代理地址，由代理的固定 IP 调用接口"
            )
        if code == 60011:
            parts.append("可在「应用管理 → 自建应用 → 可见范围」中把接收者加进去")

        if errmsg:
            parts.append("原始信息：%s" % errmsg)
        return "；".join(parts)

    # -- 发送 --------------------------------------------------------------

    def send(self, payload):
        """发送一条应用消息。返回 ``(result_dict, error)``。"""
        token, error = self.get_token()
        if error:
            return None, error

        result, failure = self._post_send(token, payload)
        if failure is None:
            return result, None

        # token 失效类错误：清缓存重取一次
        if self._norm_code(failure[0]) in (40014, 41001, 42001):
            self.log.warn("access_token 已失效，清除缓存后重试一次")
            self.clear_cache()
            token, error = self.get_token(force=True)
            if error:
                return None, error
            result, failure = self._post_send(token, payload)
            if failure is None:
                return result, None

        return None, self.describe_error(failure[0], failure[1], stage="message/send")

    def _post_send(self, token, payload):
        status, text, data, error = _http_request(
            "POST", self.url("/cgi-bin/message/send"),
            params={"access_token": token}, body=payload,
            use_proxy=self.use_proxy,
        )
        if error:
            return None, (None, "请求 message/send 失败：%s" % error)
        if not isinstance(data, dict):
            return None, (None, "message/send 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:200]))
        errcode = data.get("errcode")
        if errcode not in (0, None):
            return None, (errcode, data.get("errmsg", ""))
        return data, None

    # -- 素材 --------------------------------------------------------------

    def upload_image(self, file_path):
        """把本地图片上传到企业微信换取图片 URL。返回 ``(url, error)``。"""
        token, error = self.get_token()
        if error:
            return None, error
        status, text, data, error = _http_upload(
            self.url("/cgi-bin/media/uploadimg"), file_path, use_proxy=self.use_proxy)
        if error:
            return None, "上传本地图片失败：%s" % error
        if not isinstance(data, dict):
            return None, "uploadimg 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:200])
        if data.get("errcode") not in (0, None):
            return None, self.describe_error(data.get("errcode"), data.get("errmsg", ""),
                                             stage="media/uploadimg")
        url = data.get("url")
        if not url:
            return None, "uploadimg 未返回 url：%s" % (text or "")[:200]
        return str(url), None

    # -- 通讯录 ------------------------------------------------------------

    def department_list(self):
        """获取部门列表，返回 ``(list, error)``。"""
        token, error = self.get_token()
        if error:
            return None, error
        status, text, data, error = _http_request(
            "GET", self.url("/cgi-bin/department/list"), params={"access_token": token},
            use_proxy=self.use_proxy,
        )
        if error:
            return None, "请求 department/list 失败：%s" % error
        if not isinstance(data, dict):
            return None, "department/list 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:200])
        if data.get("errcode") not in (0, None):
            return None, self.describe_error(data.get("errcode"), data.get("errmsg", ""),
                                             stage="department/list")
        departments = data.get("department")
        return (departments if isinstance(departments, list) else []), None

    def user_simplelist(self, department_id):
        """获取指定部门的成员，返回 ``(list, error)``。"""
        token, error = self.get_token()
        if error:
            return None, error
        status, text, data, error = _http_request(
            "GET", self.url("/cgi-bin/user/simplelist"),
            params={"access_token": token, "department_id": department_id},
            use_proxy=self.use_proxy,
        )
        if error:
            return None, "请求 user/simplelist 失败：%s" % error
        if not isinstance(data, dict):
            return None, "user/simplelist 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:200])
        if data.get("errcode") not in (0, None):
            return None, self.describe_error(data.get("errcode"), data.get("errmsg", ""),
                                             stage="user/simplelist")
        users = data.get("userlist")
        return (users if isinstance(users, list) else []), None


# ---------------------------------------------------------------------------
# TgtoDrive 项目设置兜底读取
# ---------------------------------------------------------------------------

# 规范化后的键名（去掉非字母数字并小写）
CORP_ID_KEYS = {"corpid", "wecomcorpid", "qycorpid", "enterpriseid", "companyid", "wxcorpid"}
CORP_SECRET_KEYS = {"corpsecret", "wecomcorpsecret", "qycorpsecret", "appsecret", "corpappsecret"}
AGENT_ID_KEYS = {"agentid", "wecomagentid", "qyagentid", "corpagentid"}
TOKEN_KEYS = {"token", "callbacktoken", "wecomtoken", "qytoken"}
AES_KEY_KEYS = {"encodingaeskey", "wecomencodingaeskey", "qyencodingaeskey", "aeskey"}
API_BASE_KEYS = {"proxyurl", "apiurl", "baseurl", "proxyaddress", "wecomapi", "wecomurl"}


def _norm_key(key):
    return re.sub(r"[^a-z0-9]", "", str(key).lower())


def _scalar(value):
    if isinstance(value, bool):
        return ""
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        return value.strip()
    return ""


def _pick_keys(node, names):
    for key, value in node.items():
        if _norm_key(key) in names:
            text = _scalar(value)
            if text:
                return text
    return ""


def _walk_dicts(node, depth=0):
    """深度优先遍历出所有 dict（含嵌套），最多 6 层、最多 500 个节点。"""
    if depth > 6:
        return
    stack = [(node, 0)]
    seen = 0
    while stack:
        current, level = stack.pop()
        if isinstance(current, dict):
            seen += 1
            if seen > 500:
                return
            yield current
            if level < 6:
                for value in current.values():
                    if isinstance(value, (dict, list)):
                        stack.append((value, level + 1))
        elif isinstance(current, list) and level < 6:
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append((item, level + 1))


class _TtdConfigReader(object):
    """从 TgtoDrive 项目设置中启发式读取企业微信渠道配置（作为表单留空时的兜底）。

    TgtoDrive 未公开该接口的响应字段，因此这里只做「保守匹配」：
    必须同时出现 corpid 或（corpsecret + agentid）特征键才认，避免误用其它渠道的密钥。
    """

    def __init__(self, base_url, token, logger):
        base = str(base_url or "").strip() or DEFAULT_TGTO_BASE
        if not re.match(r"^https?://", base, re.IGNORECASE):
            base = "http://" + base
        self.base_url = base.rstrip("/")
        self.token = str(token or "").strip()
        self.log = logger

    def _get(self, path):
        url = self.base_url + path
        headers = {"Authorization": "Bearer %s" % self.token} if self.token else {}
        if requests is not None:
            try:
                response = requests.get(url, headers=headers,
                                        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
                if response.status_code != 200:
                    return None, "HTTP %s" % response.status_code
                return response.json(), None
            except Exception as exc:
                return None, "%s: %s" % (type(exc).__name__, exc)
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=READ_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8", "replace")), None
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)

    def read(self):
        """返回 ``(config_dict, note)``；config_dict 为空表示没有读到可用配置。"""
        for path in ("/api/proxy_settings", "/api/notify-bots"):
            payload, error = self._get(path)
            if error:
                self.log.warn("读取 TgtoDrive %s 失败：%s" % (path, error))
                continue
            found = self._search(payload)
            if found:
                self.log.info("已从 TgtoDrive %s 读取到企业微信渠道配置" % path)
                return found, "来自 TgtoDrive 项目设置（%s）" % path
        return {}, ""

    def _search(self, payload):
        for node in _walk_dicts(payload):
            corp_id = _pick_keys(node, CORP_ID_KEYS)
            secret = _pick_keys(node, CORP_SECRET_KEYS)
            agent_id = _pick_keys(node, AGENT_ID_KEYS)
            if not corp_id and not (secret and agent_id):
                continue
            config = {
                "corp_id": corp_id,
                "corp_secret": secret,
                "agent_id": agent_id,
                "token": _pick_keys(node, TOKEN_KEYS),
                "encoding_aes_key": _pick_keys(node, AES_KEY_KEYS),
                "api_base": _pick_keys(node, API_BASE_KEYS),
            }
            if config["corp_id"] or config["corp_secret"]:
                return config
        return {}


# ---------------------------------------------------------------------------
# 本地历史
# ---------------------------------------------------------------------------

def _history_path(data_dir):
    return Path(data_dir) / HISTORY_FILE


def _load_history(data_dir):
    path = _history_path(data_dir)
    try:
        if not path.is_file():
            return []
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if isinstance(data, dict):
        records = data.get("records")
    else:
        records = data
    return [r for r in records if isinstance(r, dict)] if isinstance(records, list) else []


def _save_history(data_dir, records, keep_days):
    cutoff = datetime.now() - timedelta(days=max(keep_days, 1))
    kept = []
    for record in records:
        try:
            moment = datetime.strptime(str(record.get("time") or ""), "%Y-%m-%d %H:%M:%S")
        except ValueError:
            continue
        if moment >= cutoff:
            kept.append(record)
    kept = kept[-HISTORY_MAX_RECORDS:]
    try:
        _write_text(_history_path(data_dir),
                    json.dumps({"records": kept}, ensure_ascii=False, indent=2))
    except OSError as exc:
        print("[WARN] 发送历史写入失败：%s" % exc)
    return kept


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

class _NotifyRunner(object):

    def __init__(self, params, context):
        context = context if isinstance(context, dict) else {}
        self.params = params if isinstance(params, dict) else {}
        self.data_dir = context.get("data_dir") or "."
        self.log = _Logger()

        self.func = _s(self.params, "func", "send") or "send"
        self.msgtype = (_s(self.params, "msgtype", "text") or "text").lower()
        self.channel_name = _s(self.params, "channel_name", "企业微信") or "企业微信"

        self.corp_id = _s(self.params, "corp_id")
        self.agent_id = _s(self.params, "agent_id")
        self.corp_secret = _s(self.params, "corp_secret")
        self.api_base = _s(self.params, "api_base", DEFAULT_API_BASE) or DEFAULT_API_BASE
        # 网络代理：默认「不使用代理」。企业微信自建应用常配合只允许特定地区访问的
        # 转发地址，若跟随容器的 HTTP_PROXY / HTTPS_PROXY，请求会被送去代理而连不通。
        self.use_proxy = _s(self.params, "proxy_mode", "off").lower() == "env"
        self.token = _s(self.params, "token")
        self.encoding_aes_key = _s(self.params, "encoding_aes_key")
        self.admin_users = _s(self.params, "admin_users")

        self.touser = _s(self.params, "touser")
        self.toparty = _s(self.params, "toparty")
        self.totag = _s(self.params, "totag")
        self.safe = _b(self.params, "safe", False)
        self.title = _s(self.params, "title")
        self.url = _s(self.params, "url")
        self.content = _s(self.params, "content")

        # 模板卡片（卡片通知）相关
        self.card_type = (_s(self.params, "card_type", "text_notice") or "text_notice").lower()
        self.card_image = _s(self.params, "card_image")
        # 「卡片消息内容」；同时兼容早期字段名 card_items
        self.card_content = _s(self.params, "card_content") or _s(self.params, "card_items")
        self.card_items = self.card_content
        self.card_source = _s(self.params, "card_source")
        self.card_source_icon = _s(self.params, "card_source_icon")
        self.card_sub_title = _s(self.params, "card_sub_title")
        self.card_aspect_ratio = _f(self.params, "card_aspect_ratio", CARD_ASPECT_DEFAULT)

        self.split_long = _b(self.params, "split_long", True)
        self.history_days = max(_i(self.params, "history_days", 30), 1)

        self.tgto_base_url = _s(self.params, "tgto_base_url")
        self.tgto_token = _s(self.params, "tgto_token")

        self.config_source = "插件表单"
        self.client = None

    # -- 配置准备 ----------------------------------------------------------

    def prepare_config(self):
        """解析配置来源：表单优先，留空时尝试从 TgtoDrive 项目设置兜底。"""
        missing = not self.corp_id or not self.corp_secret or not self.agent_id
        if missing:
            reader = _TtdConfigReader(
                self.tgto_base_url or _env("TGTO_OPENAPI_BASE_URL") or DEFAULT_TGTO_BASE,
                self.tgto_token or _env("TGTO_OPENAPI_TOKEN"),
                self.log,
            )
            config, note = reader.read()
            if config:
                self.corp_id = self.corp_id or config.get("corp_id", "")
                self.corp_secret = self.corp_secret or config.get("corp_secret", "")
                self.agent_id = self.agent_id or config.get("agent_id", "")
                self.token = self.token or config.get("token", "")
                self.encoding_aes_key = self.encoding_aes_key or config.get("encoding_aes_key", "")
                if config.get("api_base") and self.api_base == DEFAULT_API_BASE:
                    self.api_base = config["api_base"]
                self.config_source = note or "TgtoDrive 项目设置"
            else:
                self.log.info("未从 TgtoDrive 项目设置读到企业微信配置，使用插件表单中的值")

        self.client = _WecomClient(
            self.api_base, self.corp_id, self.corp_secret,
            self.agent_id, self.log, self.data_dir,
            use_proxy=self.use_proxy,
        )
        if self.config_source != "插件表单":
            self.log.info("配置来源：%s" % self.config_source)
        self.log.info(
            "接口地址 %s｜企业ID %s｜AgentId %s｜Secret %s｜网络 %s"
            % (self.client.masked_base(), _mask(self.corp_id), self.agent_id or "（未填写）",
               _filled(self.corp_secret),
               "跟随环境变量代理" if self.use_proxy else "直连（不走代理）")
        )

    def validate_textcard(self):
        if not self.title:
            raise ValueError("消息类型为「文本卡片」时必须填写「卡片标题」")
        if not self.url:
            raise ValueError("消息类型为「文本卡片」时必须填写「卡片跳转链接」")

    def validate_encoding_key(self):
        """EncodingAESKey 只做格式提示，不阻塞流程。"""
        if self.encoding_aes_key and not AES_KEY_RE.match(self.encoding_aes_key):
            self.log.warn(
                "「EncodingAESKey」不是标准的 43 位 Base64 字符串（当前长度 %d），"
                "请核对企业微信「接收消息」配置页；本插件不做回调收发，此项不影响消息发送。"
                % len(self.encoding_aes_key)
            )
        if self.corp_id and not CORP_ID_RE.match(self.corp_id):
            self.log.warn("「企业 ID」看起来不是 ww 开头的形态，请确认没有填成其它内容")

    # -- 收件人 ------------------------------------------------------------

    def resolve_recipients(self):
        """确定收件人；三项都为空时回退到「管理员白名单」。"""
        touser = self.touser or "@all"
        if not self.touser and not self.toparty and not self.totag:
            admins = _split_ids(self.admin_users)
            if admins:
                touser = "|".join(admins)
                self.log.info("未填写接收成员/部门/标签，改用「管理员白名单」作为收件人：%s"
                              % "、".join(admins))
            else:
                touser = "@all"
                self.log.info("未填写任何收件人，默认发送给应用全体可见成员（@all）")
        return touser, self.toparty, self.totag

    # -- 各功能 ------------------------------------------------------------

    def _relay_private_image(self, image_url):
        """把内网图片下载后上传到企业微信，换取企业微信可访问的图片 URL。"""
        data, error = _http_download(image_url)
        if error:
            self.log.warn("下载内网图片失败：%s" % error)
            return ""

        suffix = ".png" if ".png" in image_url.lower() else ".jpg"
        target = Path(self.data_dir) / "_tmp" / ("card_image" + suffix)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        except OSError as exc:
            self.log.warn("临时图片写入失败：%s" % exc)
            return ""

        try:
            new_url, error = self.client.upload_image(str(target))
        finally:
            try:
                target.unlink()
            except OSError:
                pass

        if error:
            self.log.warn("内网图片上传失败：%s" % error)
            return ""
        self.log.info("内网图片已搬运到企业微信，卡片将使用该 URL")
        return new_url

    def _resolve_card_image(self):
        """确定卡片图片 URL。

        规则：容器内本地文件 → 上传；内网 http(s) 地址（企业微信服务器访问不到）
        → 先下载再上传换取可用 URL；公网 http(s) 地址 → 直接使用。
        """
        value = self.card_image
        if not value:
            return ""
        if _looks_like_url(value):
            if not _is_private_host(value):
                return value
            self.log.warn("卡片图片是内网地址（企业微信服务器无法访问），"
                          "正在下载后上传以换取可用 URL：%s" % value)
            relayed = self._relay_private_image(value)
            if relayed:
                return relayed
            self.log.warn("搬运失败，仍使用原地址 —— 卡片上的图片可能显示不出来")
            return value
        path = Path(value)
        if path.is_file():
            self.log.info("卡片图片是本地文件，正在上传以换取企业微信图片 URL：%s" % value)
            url, error = self.client.upload_image(str(path))
            if error:
                self.log.warn("本地图片上传失败，卡片将不带图：%s" % error)
                return ""
            self.log.info("本地图片上传成功")
            return url
        self.log.warn("「卡片图片」既不是 http(s) 链接、也不是存在的本地文件，"
                      "卡片将不带图：%s" % value)
        return ""

    def build_template_card(self, content):
        """组装 template_card 结构（文本通知型 / 图文展示型）。"""
        card_type = self.card_type if self.card_type in VALID_CARD_TYPES else "text_notice"
        title, title_cut = _clip(self.title, CARD_TITLE_LIMIT)
        title_desc, desc_cut = _clip(self.card_sub_title, CARD_TITLE_DESC_LIMIT)
        body, body_cut = _clip(str(content or "").replace("\n", " ").strip(),
                               CARD_SUB_TITLE_LIMIT)
        if title_cut:
            self.log.warn("卡片标题超过 %d 字，已截断" % CARD_TITLE_LIMIT)
        if desc_cut:
            self.log.warn("卡片副标题超过 %d 字，已截断" % CARD_TITLE_DESC_LIMIT)
        if body_cut:
            self.log.warn("「消息内容」超过 %d 字，卡片正文已截断" % CARD_SUB_TITLE_LIMIT)
        if not title and not title_desc and not body:
            raise ValueError(
                "卡片通知至少需要填写「卡片标题」或「消息内容」其中之一")

        image_url = self._resolve_card_image()
        ratio = min(max(self.card_aspect_ratio, CARD_ASPECT_MIN), CARD_ASPECT_MAX)
        if self.card_aspect_ratio != ratio:
            self.log.warn("图片比例需在 %.1f–%.1f 之间，已调整为 %.2f"
                          % (CARD_ASPECT_MIN, CARD_ASPECT_MAX, ratio))
        action_url = self.url
        if not action_url:
            action_url = CARD_DEFAULT_ACTION_URL
            self.log.warn("模板卡片的 card_action 为必填项，「卡片跳转链接」为空，"
                          "已回退为 %s" % CARD_DEFAULT_ACTION_URL)

        if card_type == "news_notice" and not image_url:
            self.log.warn("图文展示型需要卡片图片，「卡片图片」为空，已自动改用文本通知型")
            card_type = "text_notice"

        card = {"card_type": card_type}
        if self.card_source:
            source = {"desc": _clip(self.card_source, CARD_SOURCE_DESC_LIMIT)[0]}
            if self.card_source_icon:
                source["icon_url"] = self.card_source_icon
            card["source"] = source

        if card_type == "news_notice":
            main = {"title": title or title_desc or "通知"}
            if title_desc and title:
                main["desc"] = title_desc
            card["main_title"] = main
            card["card_image"] = {"url": image_url, "aspect_ratio": ratio}
            if body:
                card["vertical_content_list"] = [{"title": "内容", "desc": body}]
        else:
            main = {}
            if title:
                main["title"] = title
            if title_desc:
                main["desc"] = title_desc
            if main:
                card["main_title"] = main
            if body and (title or title_desc):
                card["sub_title_text"] = body
            elif body:
                card["sub_title_text"] = body
            if image_url:
                card["card_image"] = {"url": image_url, "aspect_ratio": ratio}
            items, notes = _parse_card_items(self.card_items)
            for note in notes:
                self.log.warn(note)
            if items:
                card["horizontal_content_list"] = items
                self.log.info("卡片键值列表 %d 条：%s"
                              % (len(items), "、".join(i["keyname"] for i in items)))

        card["card_action"] = {"type": 1, "url": action_url}
        return card

    def build_payload(self, content_override=None):
        """按当前设置组装一条 message/send 请求体。"""
        try:
            agent_id_int = int(self.agent_id)
        except (TypeError, ValueError):
            raise ValueError("「应用 AgentId」必须是整数，当前值为 %r" % self.agent_id)

        touser, toparty, totag = self.resolve_recipients()
        content = self.content if content_override is None else content_override

        payload = {
            "msgtype": self.msgtype,
            "agentid": agent_id_int,
        }
        if touser:
            payload["touser"] = touser
        if toparty and touser != "@all":
            payload["toparty"] = toparty
        if totag and touser != "@all":
            payload["totag"] = totag

        if self.msgtype == "text":
            payload["text"] = {"content": content}
        elif self.msgtype == "markdown":
            payload["markdown"] = {"content": content}
        elif self.msgtype == "textcard":
            payload["textcard"] = {
                "title": self.title[:TEXTCARD_TITLE_LIMIT],
                "description": content[:TEXTCARD_DESC_LIMIT],
                "url": self.url,
                "btntxt": "查看详情",
            }
        elif self.msgtype == "template_card":
            payload["template_card"] = self.build_template_card(content)
        else:
            raise ValueError("不支持的「消息类型」：%s" % self.msgtype)

        if self.safe:
            if self.msgtype in ("text", "markdown"):
                payload["safe"] = 1
            else:
                self.log.warn("「%s」类型不支持保密消息（safe），该项已忽略"
                              % MSGTYPE_LABELS.get(self.msgtype, self.msgtype))
        return payload

    def do_send(self, content_override=None, ignore_content=False):
        """发送消息，必要时分段。返回结果字典。"""
        if ignore_content:
            content = content_override or ""
        else:
            content = self.content
            if not content and self.msgtype != "template_card":
                raise ValueError("「消息内容」为空，请填写后再发送")

        self.validate_encoding_key()
        if self.msgtype in ("textcard", "template_card"):
            if self.msgtype == "textcard":
                self.validate_textcard()
            return self._dispatch([content], segmented=False)

        chunks = _split_content(content)
        if len(chunks) > 1:
            if not self.split_long:
                chunks = chunks[:1]
                self.log.warn("正文超过 %d 字节，已截断为一段发送（可开启「超长消息自动分段」）"
                              % MESSAGE_BYTE_LIMIT)
            else:
                self.log.info("正文超过 %d 字节，自动分为 %d 段依次发送"
                              % (MESSAGE_BYTE_LIMIT, len(chunks)))
        return self._dispatch(chunks, segmented=len(chunks) > 1)

    def _dispatch(self, chunks, segmented):
        total = len(chunks)
        records = []
        failures = []
        for index, chunk in enumerate(chunks, start=1):
            body = chunk
            if segmented:
                body = "%s\n\n（第 %d/%d 段）" % (chunk, index, total)
            payload = self.build_payload(content_override=body)
            result, error = self.client.send(payload)
            if error:
                failures.append(error)
                self.log.error("第 %d/%d 段发送失败：%s" % (index, total, error))
                self._record("failed", "", error)
                break
            msgid = str(result.get("msgid") or "")
            invalid = str(result.get("invaliduser") or "")
            self.log.info("第 %d/%d 段发送成功，msgid=%s%s"
                          % (index, total, msgid or "-",
                             "，无效接收者：%s" % invalid if invalid else ""))
            records.append(msgid)
            self._record("sent", msgid, "", invalid=invalid)

        ok = not failures
        return self._result(
            status="ok" if ok else "failed",
            sent=len(records),
            total=total,
            msgids=records,
            error=failures[0] if failures else "",
            recipient_note=self._recipient_note(),
        )

    def _recipient_note(self):
        if self.touser == "@all":
            return "全体可见成员（@all）"
        parts = []
        if self.touser:
            parts.append("成员 %s" % self.touser)
        if self.toparty:
            parts.append("部门 %s" % self.toparty)
        if self.totag:
            parts.append("标签 %s" % self.totag)
        return "；".join(parts) or "（未指定）"

    def do_test(self):
        """发送测试消息：按「文本消息内容」与「卡片消息内容」两个输入框发送。

        - 两个都有内容 → 先发文本，间隔 3 秒再发卡片（共两条通知）
        - 只有一个有内容 → 只发那一条
        - 两个都为空 → 报错
        """
        text_body = self.content.strip()
        card_body = self.card_content.strip()
        if not text_body and not card_body:
            raise ValueError(
                "「文本消息内容」与「卡片消息内容」都为空，请至少填写一个再发送")

        # 文本消息的具体类型沿用「消息类型」设置（只取纯文本类，卡片单独处理）
        text_kind = self.msgtype if self.msgtype in ("text", "markdown", "textcard") else "text"

        plans = []
        if text_body:
            plans.append((text_kind, "文本消息", text_body))
        if card_body:
            plans.append(("template_card", "卡片消息", card_body))

        self.log.info("发送测试消息：共 %d 条（%s）"
                      % (len(plans), "、".join(plan[1] for plan in plans)))
        if len(plans) > 1:
            self.log.info("两条之间间隔 %d 秒发送" % TEST_SEND_GAP_SECONDS)

        original_msgtype = self.msgtype
        outcomes = []
        failures = []
        try:
            for index, (kind, label, body) in enumerate(plans):
                if index:
                    self.log.info("等待 %d 秒后发送下一条…" % TEST_SEND_GAP_SECONDS)
                    time.sleep(TEST_SEND_GAP_SECONDS)

                self.msgtype = kind
                if kind == "template_card":
                    self.title = self.title or "【%s】测试消息" % self.channel_name
                    self.url = self.url or CARD_DEFAULT_ACTION_URL
                    self.card_source = self.card_source or ("%s 测试消息" % self.channel_name)

                self.log.info("→ 发送%s" % label)
                outcome = self._dispatch([body], segmented=False)
                outcomes.append((label, kind, outcome))
                if outcome.get("status") != "ok":
                    failures.append("%s：%s" % (label, outcome.get("error") or "发送失败"))
        finally:
            self.msgtype = original_msgtype

        rows = []
        msgids = []
        for label, kind, outcome in outcomes:
            msgids.extend(outcome.get("msgids") or [])
            rows.append([
                label,
                MSGTYPE_LABELS.get(kind, kind),
                "成功" if outcome.get("status") == "ok" else "失败",
                "、".join(outcome.get("msgids") or []) or (outcome.get("error") or "-")[:60],
            ])
        while len(rows) < 2:
            rows.append(["-", "-", "未填写，已跳过", "-"])

        ok = not failures
        if not ok:
            summary = failures[0]
        elif len(outcomes) > 1:
            summary = "两条通知都已发送成功（间隔 %d 秒）。" % TEST_SEND_GAP_SECONDS
        else:
            summary = "测试通知已发送成功。"

        components = [
            {"type": "heading", "text": "发送测试消息"},
            {"type": "alert", "text": summary,
             "style": {"tone": "success" if ok else "danger"}},
            {"type": "table", "label": "本次发送（按内容框自动决定条数）",
             "headers": ["内容框", "消息类型", "结果", "msgid / 错误"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok" if ok else "failed",
            "func": self.func,
            "batches_total": len(plans),
            "batches_ok": len([o for _, _, o in outcomes if o.get("status") == "ok"]),
            "msgids": msgids,
            "error": failures[0] if failures else "",
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def do_config_check(self):
        """配置自检：格式校验 + 真实获取一次 access_token。"""
        rows = []
        problems = []

        def row(name, value, ok, note=""):
            rows.append([name, value, "✅ 正常" if ok else "⚠️ 待确认", note])

        row("通知渠道名称", self.channel_name, True)
        row("企业 ID", _mask(self.corp_id), bool(self.corp_id),
            "" if self.corp_id else "必填，请填写 ww 开头的企业 ID")
        if not self.corp_id:
            problems.append("缺少「企业 ID」")
        elif not CORP_ID_RE.match(self.corp_id):
            row("企业 ID 形态", "非 ww 开头", False, "请确认没有把 Secret 或 AgentId 填到这里")

        agent_ok = bool(self.agent_id) and self.agent_id.isdigit()
        row("应用 AgentId", self.agent_id or "（未填写）", agent_ok,
            "" if agent_ok else "必填，且必须是纯数字")
        if not agent_ok:
            problems.append("「应用 AgentId」缺失或不是纯数字")

        row("应用 Secret", _filled(self.corp_secret), bool(self.corp_secret),
            "" if self.corp_secret else "必填")
        if not self.corp_secret:
            problems.append("缺少「应用 Secret」")

        row("接口地址", self.client.masked_base(), True)
        if self.api_base == DEFAULT_API_BASE:
            rows.append(["接口地址说明", "官方地址", "ℹ️ 提示",
                         "若报 60020，请改用转发代理地址或配置企业可信IP"])

        if self.encoding_aes_key:
            aes_ok = bool(AES_KEY_RE.match(self.encoding_aes_key))
            row("EncodingAESKey", _filled(self.encoding_aes_key), aes_ok,
                "" if aes_ok else "应为 43 位 Base64；本插件不做回调收发，不影响发送")
        row("配置来源", self.config_source, True)

        token_note = ""
        token_ok = False
        if not problems:
            token, error = self.client.get_token(force=True)
            if error:
                token_note = error
                self.log.error("获取 access_token 失败：%s" % error)
            else:
                token_ok = True
                _, remain = self.client.cached_token()
                token_note = "有效期剩余约 %d 秒" % remain
                self.log.info("配置自检通过，access_token 获取成功")
        else:
            token_note = "前置配置不完整，已跳过"
        row("access_token", "已获取" if token_ok else "未获取", token_ok, token_note)

        components = [
            {"type": "heading", "text": "配置自检"},
            {"type": "table", "label": "共 %d 项" % len(rows),
             "headers": ["检查项", "当前值", "结果", "说明"], "rows": rows},
        ]
        if problems:
            components.append({"type": "alert",
                               "text": "以下必填项需要补全：%s。填写后点顶部「发送测试消息」验证。"
                                       % "、".join(problems),
                               "style": {"tone": "warning"}})
        elif token_ok:
            components.append({"type": "alert",
                               "text": "配置完整且已成功获取 access_token，可以点顶部「发送测试消息」验证通知链路。",
                               "style": {"tone": "success"}})
        else:
            components.append({"type": "alert",
                               "text": "配置项本身完整，但获取 access_token 失败，详见下方日志。",
                               "style": {"tone": "danger"}})
        components.extend([
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ])

        return {
            "status": "ok" if token_ok else "failed",
            "func": self.func,
            "config_ok": not problems,
            "token_ok": token_ok,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def do_users(self):
        """列出应用可见范围的部门与成员，方便填写 UserID。"""
        departments, error = self.client.department_list()
        if error:
            return self._failure_result("查询部门列表失败", error)

        dept_rows = []
        user_rows = []
        for department in departments[:100]:
            if not isinstance(department, dict):
                continue
            dept_id = department.get("id")
            name = str(department.get("name") or "")
            dept_rows.append([str(dept_id if dept_id is not None else "-"), name])

        # 只对前若干个部门取成员，避免接口调用过多
        for department in departments[:10]:
            if not isinstance(department, dict):
                continue
            dept_id = department.get("id")
            if dept_id is None:
                continue
            users, error = self.client.user_simplelist(dept_id)
            if error:
                self.log.warn("获取部门 %s 成员失败：%s" % (dept_id, error))
                continue
            for user in users[:200]:
                if not isinstance(user, dict):
                    continue
                user_rows.append([
                    str(user.get("userid") or "-"),
                    str(user.get("name") or "-"),
                    str(dept_id),
                ])

        if not dept_rows:
            dept_rows = [["（无）", "该应用可见范围内没有部门"]]
        if not user_rows:
            user_rows = [["（无）", "未取到成员，请确认应用可见范围", "-"]]

        self.log.info("读取到 %d 个部门、%d 名成员" % (len(dept_rows), len(user_rows)))
        components = [
            {"type": "heading", "text": "应用可见范围"},
            {"type": "table", "label": "部门（最多 100 个）",
             "headers": ["部门 ID", "部门名称"], "rows": dept_rows},
            {"type": "table", "label": "成员（前 10 个部门，最多各 200 人）",
             "headers": ["UserID", "姓名", "部门 ID"], "rows": user_rows},
            {"type": "alert",
             "text": "把「UserID」填进「接收成员」，多个用 | 分隔；部门 ID 填入「接收部门」。"
                     "成员姓名在部分应用类型下不返回，属正常现象。",
             "style": {"tone": "muted"}},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok",
            "func": self.func,
            "department_count": len(dept_rows),
            "user_count": len(user_rows),
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def do_history(self):
        records = _load_history(self.data_dir)
        records.sort(key=lambda r: str(r.get("time") or ""), reverse=True)
        displayed = records[:200]

        rows = []
        for record in displayed:
            rows.append([
                str(record.get("time") or "-"),
                MSGTYPE_LABELS.get(str(record.get("msgtype") or ""), str(record.get("msgtype") or "-")),
                str(record.get("recipient") or "-"),
                "成功" if record.get("status") == "sent" else "失败",
                str(record.get("msgid") or record.get("error") or "-")[:80],
            ])
        if not rows:
            rows = [["暂无记录", "-", "-", "-", "-"]]

        self.log.info("读取本地发送历史 %d 条" % len(displayed))
        components = [
            {"type": "heading", "text": "发送历史（本地记录）"},
            {"type": "table", "label": "最近 %d 条，保留 %d 天" % (len(rows), self.history_days),
             "headers": ["时间", "类型", "收件人", "结果", "msgid / 错误"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok",
            "func": self.func,
            "history_count": len(records),
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def do_docs(self):
        """展示「被其他插件调用」的方法说明与在线文档链接。"""
        self.log.info("输出被调用方法说明；完整文档：%s" % DOCS_URL)

        params_rows = [
            ["func", "必填", "send 发送 / test 测试 / config 自检 / users 查成员 / history 查历史"],
            ["msgtype", "必填", "text / markdown / textcard / template_card（卡片通知）"],
            ["touser", "常用", "UserID，多个用 | 分隔；@all 表示该应用全体可见成员"],
            ["toparty / totag", "可选", "部门 ID / 标签 ID，touser 为 @all 时被忽略"],
            ["title", "卡片", "卡片标题（template_card 与 textcard 使用）"],
            ["content", "常用", "文本消息内容；「发送消息」按「消息类型」发送本框，「发送测试消息」会连同下框一起处理"],
            ["card_content", "卡片", "卡片消息内容：每行一条「键=值」（最多 6 条）；非键值格式则整段作为卡片正文"],
            ["card_image", "卡片", "卡片主图：http(s) 链接、内网地址或容器内本地路径（都会先换成企业微信可用 URL）"],
            ["card_source", "卡片", "卡片来源名称，例如「站点 1PTBA 消息」"],
            ["card_source_icon", "卡片", "来源图标 URL"],
            ["card_type", "卡片", "text_notice（默认，大图+键值列表）/ news_notice（图文展示型）"],
            ["url", "卡片", "卡片点击跳转链接；模板卡片的 card_action 为必填项"],
        ]

        sample = (
            "import requests\n"
            "\n"
            "BASE  = \"http://127.0.0.1:12366\"   # TgtoDrive 地址（同容器常用该地址）\n"
            "TOKEN = \"YOUR_OPENAPI_TOKEN\"       # 调用方自行读取，勿硬编码\n"
            "\n"
            "resp = requests.post(\n"
            "    BASE + \"/api/toolbox/plugins/wecom-notify/run\",\n"
            "    headers={\"Authorization\": \"Bearer \" + TOKEN},\n"
            "    json={\"params\": {\n"
            "        \"func\": \"send\",\n"
            "        \"msgtype\": \"template_card\",\n"
            "        \"touser\": \"@all\",\n"
            "        \"title\": \"新入库剧集：示例标题\",\n"
            "        \"card_source\": \"站点 1PTBA 消息\",\n"
            "        \"card_image\": \"https://example.com/cover.jpg\",\n"
            "        \"card_content\": \"时间=2026-10-13 18:04\\n分类=日番\\n评分=8.5/10\",\n"
            "        \"url\": \"https://example.com/detail\",\n"
            "    }},\n"
            "    timeout=(5, 30),\n"
            ")\n"
            "job = resp.json()          # 含 job_id\n"
            "# 需要结果时轮询：\n"
            "# GET {BASE}/api/toolbox/plugins/jobs/{job_id}\n"
        )

        components = [
            {"type": "heading", "text": "被其他插件调用"},
            {"type": "markdown", "text": (
                "本插件可以通过 TgtoDrive OpenAPI 被**其他插件或脚本**调用，"
                "用于发送企业微信通知（文本、markdown、文本卡片或带图卡片）。\n\n"
                "**完整调用说明（参数表 / 返回值 / 错误处理 / 完整示例）：**\n\n"
                "- [plugins/wecom-notify/CALLING.md](%s)\n\n"
                "调用入口：`POST /api/toolbox/plugins/wecom-notify/run`" % DOCS_URL)},
            {"type": "table", "label": "常用参数（完整列表见 CALLING.md）",
             "headers": ["参数", "场景", "说明"], "rows": params_rows},
            {"type": "heading", "text": "最小示例（Python）"},
            {"type": "code", "text": sample},
            {"type": "alert", "text": (
                "令牌请由调用方自行读取（环境变量 TGTO_OPENAPI_TOKEN 或自己的插件设置），"
                "不要写进插件包或日志。被调用时同样遵守插件协议：单次同步执行、"
                "返回值 ≤1 MiB、到 timeout 即结束。"),
             "style": {"tone": "muted"}},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok",
            "func": self.func,
            "docs_url": DOCS_URL,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    # -- 历史与结果 --------------------------------------------------------

    def _record(self, status, msgid, error="", invalid=""):
        records = _load_history(self.data_dir)
        records.append({
            "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "msgtype": self.msgtype,
            "recipient": self._recipient_note(),
            "status": status,
            "msgid": msgid,
            "error": error,
            "invaliduser": invalid,
        })
        _save_history(self.data_dir, records, self.history_days)

    def _failure_result(self, title, error):
        self.log.error("%s：%s" % (title, error))
        components = [
            {"type": "heading", "text": title},
            {"type": "alert", "text": error, "style": {"tone": "danger"}},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "failed",
            "func": self.func,
            "error": error,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def _result(self, status, sent, total, msgids, error, recipient_note):
        if status == "ok":
            title = "发送成功" if total <= 1 else "发送成功（分 %d 段）" % total
            alert_text = "已通过「%s」发送给：%s" % (self.channel_name, recipient_note)
            tone = "success"
        else:
            title = "发送失败"
            alert_text = error
            tone = "danger"

        components = [
            {"type": "heading", "text": title},
            {"type": "alert", "text": alert_text, "style": {"tone": tone}},
            {"type": "table", "label": "发送详情",
             "headers": ["项目", "值"],
             "rows": [
                 ["消息类型", MSGTYPE_LABELS.get(self.msgtype, self.msgtype)],
                 ["收件人", recipient_note],
                 ["接口地址", self.client.masked_base()],
                 ["分段", "%d 段，成功 %d 段" % (total, sent)],
                 ["msgid", "、".join(m for m in msgids if m) or "-"],
             ]},
        ]
        if error:
            components.append({"type": "alert", "text": error, "style": {"tone": "danger"}})
        components.extend([
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ])
        return {
            "status": status,
            "func": self.func,
            "msgtype": self.msgtype,
            "sent": sent,
            "total": total,
            "msgids": [m for m in msgids if m],
            "error": error,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        if self.func not in VALID_FUNCS:
            raise ValueError("不支持的执行功能：%s" % self.func)
        if self.msgtype not in VALID_MSGTYPES:
            raise ValueError("不支持的消息类型：%s" % self.msgtype)

        self.log.info("企业微信通知启动，执行功能：%s" % FUNC_LABELS.get(self.func, self.func))
        if self.func == "docs":
            # 纯文档输出，不需要任何配置与网络请求
            return self.do_docs()

        self.prepare_config()

        if self.func == "config":
            return self.do_config_check()
        if self.func == "users":
            return self.do_users()
        if self.func == "history":
            return self.do_history()
        if self.func == "test":
            return self.do_test()
        return self.do_send()


def _env(name):
    try:
        import os
        return os.environ.get(name, "").strip()
    except Exception:
        return ""


def run(params, context):
    """TgtoDrive 插件入口：同步执行一次企业微信通知相关操作。"""
    return _NotifyRunner(params, context).execute()
