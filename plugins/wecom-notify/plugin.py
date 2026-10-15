# -*- coding: utf-8 -*-
"""企业微信通知 · TgtoDrive Python 插件

为企业微信（WeCom / 原企业号）自建应用提供「应用消息推送」能力：
按企业微信官方接口 https://developer.work.weixin.qq.com/document 实现
`GET /cgi-bin/gettoken` 与 `POST /cgi-bin/message/send`。

能力
  * 发送消息：**只支持两种类型** —— `text` 文本消息与 `news` 图文消息，
    支持发给成员、部门、标签或 @all。
  * **为什么只有这两种**：企业微信官方限制下，微信插件（原企业号）**收不到**
    markdown 与模板卡片（template_card），文本卡片（textcard）的功能又被 news 覆盖。
    既然本插件的定位是「让 TgtoDrive 能把消息发到微信」，就只保留微信确实能收到的两种。
  * **图文消息 news**：大图 + 标题 + 描述 + 点击跳转，是微信里最接近「卡片」的形态；
    图片支持 http(s) 链接、内网地址或容器内本地路径（后两者会自动上传换取可用 URL）。
  * 兼容旧调用方的「模板卡片 JSON」：把 card_content 传成模板卡片 JSON 时，
    在 news 类型下会**自动转换成图文**（标题 / 描述 / 键值 / 链接 / 图片），无需重写内容。
  * 发送测试消息（界面顶部独立按钮）：固定发一条文本 + 一条图文消息（间隔 3 秒），
    一次点击即可验证「配置 + 网络 + 收件人 + 微信可收性」。
  * 检查配置：校验必填项格式并真实获取一次 access_token，给出剩余有效期。
  * 查看发送历史：本地记录每次发送的类型、收件人、结果与错误码。
  * **查看调用方法**：输出「被其他插件调用」的参数表与示例，
    并给出仓库内 CALLING.md 的在线链接。
    教程链接在**两个位置**都可见，确保其他开发者一眼能发现：
      ① 清单 UI 的右栏，「查看调用方法」按钮**正下方**放了一个 `link` 组件
         （无需点击即可看到并直接打开）；
      ② 结果页把链接放在**最上方**（紧跟标题），点按钮后第一眼就能看到，
         不再埋在长文中段/末尾。

界面取舍
  * 界面只有一个「应用配置」页签，所有输入集中在此（含原先独立的「回调与高级」字段）。
  * 顶部三个可点项：发送测试消息、查看调用方法、以及其下的「打开调用教程」超链接。
  * 「执行功能」下拉框含 发送消息(send) / 发送测试消息(test) / 检查配置(config) /
    查看发送历史(history) / 查看调用方法(docs)。
    **send 必须留在下拉框里**：TgtoDrive 会校验 `select` 的取值是否在 options 内，
    若 send 不在 options 中，其他插件调用 `func=send` 时请求会被直接拒绝。

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

import ast
import json
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover - 仅在极简环境触发
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "https://qyapi.weixin.qq.com"
# 卡片图片的清单默认值（plugin.json → inputs.card_image.default）。
# 只被 FALLBACK_INPUT_DEFAULTS 引用（plugin.json 读不到的边缘场景）；
# 改清单里的默认图时记得同步这里。
CARD_DEFAULT_IMAGE = "http://192.168.101.100:12366/static/brand_logo.png?v=18de0d2b37259200-5d57"
DEFAULT_TGTO_BASE = "http://127.0.0.1:12366"

USER_AGENT = "TgtoDrive-WecomNotify/1.0 (+https://github.com/a2695154202/ttd-plugins)"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# 文本与图文消息的正文上限（企业微信文档：text 不超过 2048 字节）
MESSAGE_BYTE_LIMIT = 2048
# 分段后缀「\n\n（第 x/y 段）」占用的字节数上界（3 位数序号也够用）。
# 切分时必须把它从上限里预留出来：曾经按 2048 整切、拼上后缀后单段实际可达
# 2070+ 字节，突破 docstring 承诺的「每段不超 2048 字节」。
SEGMENT_SUFFIX_RESERVE = 24

# access_token 有效期 7200 秒；提前 300 秒视为过期
TOKEN_REFRESH_AHEAD = 300
TOKEN_DEFAULT_TTL = 7200

TOKEN_FILE = "token.json"
HISTORY_FILE = "history.json"
HISTORY_MAX_RECORDS = 500

# 本插件自己的 id 与表单设置文件名（供「被调用时补齐已保存配置」使用）
PLUGIN_ID = "wecom-notify"
SETTINGS_FILE = "settings.json"

# 「标准化发送内容」的契约（本插件作为通用发送模块被调用时的统一入口）。
# 调整这里必须同步更新 CALLING.md 与调用方；新增字段属于向后兼容的扩展。
ENVELOPE_VERSION = 1
ENVELOPE_KEYS = ("version", "msgtype", "touser", "content", "items",
                 "title", "url", "image", "source")

# 执行功能。``send`` 是给**其他插件调用**用的正式发送入口（药丸签到等走的
# 就是这条路径），它同样声明在清单的 inputs 里 —— TgtoDrive 会按 inputs 校验
# 「哪些键合法」与「选项取值是否在 options 内」，所以任何调用方要传的取值
# 都必须出现在 plugin.json 的 options 中，否则请求会被判为非法而拒绝。
FUNC_LABELS = {
    "send": "发送消息（供其他插件调用）",
    "test": "发送测试消息",
    "config": "检查配置",
    "history": "查看发送历史",
    "docs": "查看调用方法",
}
VALID_FUNCS = tuple(FUNC_LABELS)

# 消息类型只保留「文本」与「图文消息 news」两种：
# 这两种是**企业微信客户端与微信插件都能收到**的类型，本插件的定位就是
# 「让 TgtoDrive 能把消息发到微信」，因此不再提供 markdown / 文本卡片 /
# 模板卡片 —— 它们要么微信收不到，要么已被 news 完全覆盖。
MSGTYPE_LABELS = {
    "text": "文本消息",
    "news": "图文消息 news",
}
VALID_MSGTYPES = tuple(MSGTYPE_LABELS)

# 图文消息（news）的企业微信侧限制
NEWS_MAX_ARTICLES = 8
NEWS_TITLE_LIMIT = 60      # 企业微信按字节限 128，中文按字符取保守值
NEWS_DESC_LIMIT = 160      # 企业微信按字节限 512
NEWS_IMAGE_SPEC = "大图建议 1068×455，小图建议 150×150，JPG / PNG"

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

# 「发送测试消息」的内容已内置（界面上不再提供内容输入框）。
# 占位符 {now} / {channel} / {api_base} 会在发送前替换。
# 其他插件通过 OpenAPI 调用时可传 content / card_content 覆盖内置内容。
DEFAULT_TEST_TEXT = (
    "【企业微信通知】测试文本消息\n"
    "如果你收到这条消息，说明 TgtoDrive 的企业微信文本通知链路已经打通。\n"
    "时间：{now}\n"
    "渠道：{channel}\n"
    "接口：{api_base}"
)

DEFAULT_TEST_CARD = (
    "状态=测试成功\n"
    "渠道={channel}\n"
    "时间={now}\n"
    "提示=收到这张卡片，说明带图通知链路已打通"
)


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


# 只回显「已填写（长度 N）」的敏感字段。
# 调用方可能把凭据一并传进来，日志里绝不能原样落盘。
#
# 注意两点，都是踩过的坑：
# ① 比较的是 **归一化后** 的键名（`_norm_key` 会去掉非字母数字并转小写），
#    所以这里写 "tgtotoken" 而不是 "tgto_token" —— 写带下划线的形式永远匹配不上；
# ② 除了精确枚举，还按**片段**兜底（见 _is_sensitive_key）。这样将来新增凭据类字段时，
#    即使忘了往枚举里加，也不会把明文写进日志 —— 宁可多脱敏，不可漏。
SENSITIVE_KEYS = frozenset((
    "corpsecret", "corpidsecret", "appsecret", "corpsecretkey", "secret",
    "token", "callbacktoken", "tgtotoken", "openapitoken", "accesstoken",
    "encodingaeskey", "aeskey", "password", "passwd", "credential", "apikey",
    # 企业 ID 本身不是「凭据」，但模块 docstring 承诺过它不进运行日志 ——
    # 曾因漏了它，调用方传入 corp_id 时被原样打印（而 URL 脱敏里又把它当敏感项，
    # 两边标准不一）。agent_id 不在承诺范围内，保留原样便于排障。
    "corpid", "corpcode",
))
SENSITIVE_HINTS = ("secret", "token", "password", "passwd", "aeskey",
                   "credential", "apikey")


def _is_sensitive_key(key):
    """判断某个键名是否属于凭据类（归一化后精确枚举 + 片段兜底）。"""
    norm = _norm_key(key)
    if not norm:
        return False
    if norm in SENSITIVE_KEYS:
        return True
    return any(hint in norm for hint in SENSITIVE_HINTS)


def _redact_value(key, value):
    """敏感键只回显长度；其余原样返回，供日志渲染。"""
    if _is_sensitive_key(key):
        text = str(value)
        return "***（已填写，长度 %d）" % len(text) if text else "（空）"
    return value


def _mask_params(params, max_len=2000):
    """把一份参数渲染成**可安全写进 TTD 运行日志**的一行文本。

    为什么需要它：本插件被其他插件调用时要能看到「对方到底传了什么」
    （这是排查「任务成功但发不出去」最直接的证据），但调用方可能把凭据一起传进来，
    所以在这里统一做两件事 —— 敏感键只回显长度、过长内容截断。
    """
    if not isinstance(params, dict) or not params:
        return "（空）"
    parts = []
    for key, value in params.items():
        value = _redact_value(key, value)
        if isinstance(value, (dict, list)):
            text = json.dumps(value, ensure_ascii=False)
        else:
            text = str(value)
        text = text.replace("\n", "\\n")
        if len(text) > max_len:
            text = "%s…（共 %d 字，已截断）" % (text[:max_len], len(str(value)))
        parts.append("%s=%s" % (key, text))
    return " | ".join(parts)


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


def _parse_native_card_json(text):
    """尝试把「卡片消息内容」当作企业微信**原生 JSON** 解析。

    支持四种写法，便于从官方文档直接粘贴，不必改写成「键=值」：

    * 完整请求体（模板卡片）：``{"msgtype": "template_card", "template_card": {...}}``
    * 完整请求体（图文消息）：``{"msgtype": "news", "news": {"articles": [...]}}``
    * 仅模板卡片本身：``{"card_type": "text_notice", ...}``
    * 仅图文内容本身：``{"articles": [...]}``

    返回 ``(kind, obj)``：``kind`` 为 ``"body"`` / ``"card"`` / ``"news"`` / ``"articles"``；
    当内容不是以 ``{`` 开头的 JSON 对象时返回 ``(None, None)``，交回「键=值」解析。
    """
    text = str(text or "").strip()
    if not text.startswith("{"):
        return None, None
    try:
        obj = json.loads(text)
    except ValueError:
        return None, None
    if not isinstance(obj, dict):
        return None, None
    if isinstance(obj.get("template_card"), dict):
        return "body", obj
    if isinstance(obj.get("news"), dict):
        return "news", obj
    if "card_type" in obj:
        return "card", obj
    if isinstance(obj.get("articles"), list):
        return "articles", obj
    return None, None


def _render_items(items):
    """把调用方传来的结构化键值渲染成「键：值」多行文本。

    兼容三种写法：``[["键","值"], …]``、``[{"key":…,"value":…}, …]``、
    ``{"键": "值", …}``。无法识别的条目会被跳过（不报错），因为这里只做渲染，
    格式问题应由调用方从结果日志中发现。
    """
    if items is None:
        return ""
    if isinstance(items, dict):
        items = list(items.items())
    if not isinstance(items, (list, tuple)):
        return ""
    lines = []
    for item in items:
        key = value = None
        if isinstance(item, dict):
            for k in ("key", "name", "键", "keyname"):
                if item.get(k) not in (None, ""):
                    key = item.get(k)
                    break
            for k in ("value", "val", "值"):
                if item.get(k) not in (None, ""):
                    value = item.get(k)
                    break
        elif isinstance(item, (list, tuple)) and len(item) >= 2:
            key, value = item[0], item[1]
        if key in (None, "") or value in (None, ""):
            continue
        lines.append("%s：%s" % (key, value))
    return "\n".join(lines)


def _kv_to_lines(text):
    """把「键=值」多行文本转成「键：值」多行文本，供图文消息的描述使用。

    与模板卡片时代的解析不同：这里不做键 ≤5 字 / 值 ≤30 字的截断
    （那是模板卡片的限制），图文消息的描述是自由文本。
    """
    lines = []
    for raw_line in str(text or "").replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s*[=：:]\s*|\s*\|\s*", line, maxsplit=1)
        if len(parts) == 2 and parts[0].strip():
            lines.append("%s：%s" % (parts[0].strip(), parts[1].strip()))
        else:
            lines.append(line)
    return "\n".join(lines)


def _template_card_to_news(card):
    """把模板卡片结构降级成图文消息（news）。

    用途：模板卡片在企业微信里好看，但**微信插件收不到**。当用户把「消息类型」
    改成「图文消息 news」时，直接把原卡片 JSON 里的标题、描述、键值列表、跳转链接
    与图片提取出来组成图文，就不必重写内容。

    返回 ``{"articles": [article]}``，无法提取出任何内容时返回 ``None``。
    """
    if not isinstance(card, dict):
        return None

    title = ""
    descs = []

    main = card.get("main_title")
    if isinstance(main, dict):
        title = str(main.get("title") or "")
        if main.get("desc"):
            descs.append(str(main["desc"]))
    if not title:
        source = card.get("source")
        if isinstance(source, dict) and source.get("desc"):
            title = str(source["desc"])

    emphasis = card.get("emphasis_content")
    if isinstance(emphasis, dict):
        pair = "：".join(str(emphasis.get(k)) for k in ("title", "desc") if emphasis.get(k))
        if pair:
            descs.append(pair)

    if card.get("sub_title_text"):
        descs.append(str(card["sub_title_text"]))

    for item in card.get("horizontal_content_list") or []:
        if isinstance(item, dict) and item.get("keyname"):
            descs.append("%s：%s" % (item["keyname"], item.get("value", "")))

    for item in card.get("vertical_content_list") or []:
        if isinstance(item, dict) and (item.get("title") or item.get("desc")):
            descs.append("：".join(str(item.get(k)) for k in ("title", "desc") if item.get(k)))

    if not (title or descs):
        return None

    article = {"title": title or "通知"}
    if descs:
        article["description"] = "\n".join(descs)

    action = card.get("card_action")
    if isinstance(action, dict) and action.get("url"):
        article["url"] = str(action["url"])

    image = card.get("card_image")
    if isinstance(image, dict) and image.get("url"):
        article["picurl"] = str(image["url"])

    return {"articles": [article]}


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
            response = requests.get(
                url, timeout=timeout, stream=True,
                headers={"User-Agent": USER_AGENT},
                # 卡片图多是内网地址，且下载失败只会降级用原地址 —— 不显式禁用
                # 环境代理的话，容器里的全局代理会把内网图片请求送出去而失败。
                proxies={"http": None, "https": None})
            if response.status_code != 200:
                return None, "HTTP %s" % response.status_code
            data = response.content
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)
    else:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            # ProxyHandler({})：禁用环境变量代理（与 requests 分支语义一致）
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=timeout[1]) as response:
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
            # 把「本次到底把请求发到了哪里」写进错误里：配了转发代理却不生效时，
            # 这一行能直接说明问题（默认地址 = 代理没被用上），不用再去翻运行日志。
            parts.append("本次请求实际发往：%s%s"
                         % (self.api_base,
                            "（默认地址，转发代理未生效）" if self.api_base == DEFAULT_API_BASE
                            else "（转发代理）"))
            parts.append(
                "处理方式二选一：① 到企业微信管理后台「应用管理 → 自建应用 → 企业可信IP」"
                "把上述 IP 加入白名单（配置后约 1 分钟生效）；"
                "② 在「应用配置 → 代理地址」填写转发代理地址并**保存**，"
                "由代理的固定 IP 调用接口（被其他插件调用时同样生效）"
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

    def visible_members(self):
        """读取应用可见范围内的成员（根部门 + 子部门），返回 ``(list, error)``。"""
        token, error = self.get_token()
        if error:
            return None, error
        status, text, data, error = _http_request(
            "GET", self.url("/cgi-bin/user/list"),
            params={"access_token": token, "department_id": 1, "fetch_child": 1},
            use_proxy=self.use_proxy,
        )
        if error:
            return None, "请求 user/list 失败：%s" % error
        if not isinstance(data, dict):
            return None, "user/list 返回非 JSON（HTTP %s）：%s" % (status, (text or "")[:160])
        if data.get("errcode") not in (0, None):
            return None, self.describe_error(data.get("errcode"), data.get("errmsg", ""),
                                             stage="user/list")
        users = data.get("userlist")
        return (users if isinstance(users, list) else []), None

    def verify_recipients(self, touser):
        """发送前判断收件人是否真的收得到。

        企业微信在「收件人不在应用可见范围内」时，**通常仍返回 ``errcode=0`` 与 msgid，
        但消息不会投递** —— 只凭接口返回值会把这种情况误判成发送成功。

        返回 ``(status, message)``：

        * ``"ok"``      —— 收件人都在可见范围内
        * ``"empty"``   —— 可见范围为空，``@all`` 无人可投
        * ``"missing"`` —— 有收件人不在可见范围
        * ``"unknown"`` —— 没有通讯录权限或查询失败，无法判定（不影响发送）
        """
        users, error = self.visible_members()
        if error:
            return "unknown", error

        visible = {str(u.get("userid")) for u in users if u.get("userid")}
        if str(touser or "").strip() == "@all":
            if not visible:
                return "empty", ("应用可见范围内没有任何成员，@all 无人可投 —— "
                                 "请到管理后台该应用的「可见范围」里添加接收人")
            return "ok", "应用可见成员共 %d 人" % len(visible)

        wanted = [x for x in _split_ids(touser) if x and x != "@all"]
        missing = [x for x in wanted if x not in visible]
        if missing:
            return "missing", ("以下收件人不在应用可见范围内：%s —— "
                               "企业微信会接受请求但不投递" % "、".join(missing[:8]))
        return "ok", "收件人均在可见范围内（可见成员共 %d 人）" % len(visible)


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
                response = requests.get(
                    url, headers=headers,
                    timeout=(CONNECT_TIMEOUT, READ_TIMEOUT),
                    # ttd 是同容器 / 内网管理端：显式禁用环境代理，
                    # 否则容器里的全局代理（为出网配的）会把请求送出去而失败
                    proxies={"http": None, "https": None})
                if response.status_code != 200:
                    return None, "HTTP %s" % response.status_code
                return response.json(), None
            except Exception as exc:
                return None, "%s: %s" % (type(exc).__name__, exc)
        request = urllib.request.Request(url, headers=headers)
        try:
            opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
            with opener.open(request, timeout=READ_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8", "replace")), None
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)

    def read(self):
        """返回 ``(config_dict, note)``；config_dict 为空表示没有读到可用配置。

        顺序：**本插件自己的已保存设置**优先（字段名就是我们自己的 inputs，最可靠），
        再退回 TgtoDrive 项目设置的启发式匹配。
        """
        payload, error = self._get("/api/toolbox/plugins/%s/settings" % PLUGIN_ID)
        if error:
            self.log.info("读取本插件已保存设置失败（%s），改从项目设置查找" % error)
        else:
            found = self._from_own_settings(payload)
            if found:
                self.log.info("已从「%s」已保存的设置里读取到企业微信配置" % PLUGIN_ID)
                return found, "来自本插件已保存的设置（settings.json）"

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

    @staticmethod
    def _from_own_settings(payload):
        """把本插件 settings 接口的响应直接映射成配置（字段名与我们自己的 inputs 一致）。"""
        params = _extract_settings_params(payload)
        if not params:
            return {}
        config = {
            "corp_id": _scalar(params.get("corp_id")),
            "corp_secret": _scalar(params.get("corp_secret")),
            "agent_id": _scalar(params.get("agent_id")),
            "token": _scalar(params.get("token")),
            "encoding_aes_key": _scalar(params.get("encoding_aes_key")),
            "api_base": _scalar(params.get("api_base")),
        }
        if config["corp_id"] or (config["corp_secret"] and config["agent_id"]):
            return config
        return {}

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


def _own_settings_candidates(plugin_dir):
    """列出可能存放「本插件已保存设置」的 settings.json 路径。

    TgtoDrive 把表单参数存到**插件目录**下的 settings.json，但 `context["plugin_dir"]`
    指向的是「当前版本的代码目录」，两者可能是同一层也可能差一层，因此这里逐级探测。
    """
    root = Path(str(plugin_dir or "").strip() or ".")
    seen = []
    for candidate in (root / SETTINGS_FILE,
                      root.parent / SETTINGS_FILE,
                      root.parent.parent / SETTINGS_FILE):
        if candidate not in seen:
            seen.append(candidate)
    return seen


def _extract_settings_params(payload):
    """从 settings.json / settings 接口的响应里取出「参数对象」。

    接口文档只说会返回 ``settings.params``，没有给 schema（inferred），
    因此这里兼容三种形态：``{"params": {...}}``、``{"settings": {"params": {...}}}``
    以及直接就是一张参数表。
    """
    if not isinstance(payload, dict):
        return {}
    for node in (payload, payload.get("settings"), payload.get("data")):
        if isinstance(node, dict):
            params = node.get("params") or node.get("values")
            if isinstance(params, dict) and params:
                return params
    # 直接是参数表的情况：排除掉明显的元信息键
    meta = {"saved_at", "readable", "success", "message", "error", "updated_at"}
    flat = {k: v for k, v in payload.items() if k not in meta}
    return flat if flat else {}


def _manifest_input_defaults(plugin_dir):
    """返回本插件清单里各 input 的默认值 ``{name: default}``。

    存在的原因见 :meth:`_NotifyRunner._merge_own_settings`：TgtoDrive 的运行接口
    会把所有 inputs 按默认值填齐，插件必须认得这些默认值，才能把「默认值」
    与「调用方显式传的值」区分开。

    读取顺序（任一成功即返回）：
    1. 插件包安装：``plugin_dir`` 及其上级目录下的 ``plugin.json``；
    2. 单文件安装：解析自身源码顶层的 ``PLUGIN_MANIFEST`` 字面量；
    3. 内置兜底表（与 ``plugin.json`` 保持一致，改清单时记得同步）。
    """
    # 1) 插件包：plugin.json
    root = Path(str(plugin_dir or "").strip() or ".")
    for base in (root, root.parent, root.parent.parent):
        manifest = base / "plugin.json"
        try:
            if not manifest.is_file():
                continue
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        defaults = _defaults_from_manifest(data)
        if defaults:
            return defaults

    # 2) 单文件：源码顶层的 PLUGIN_MANIFEST
    try:
        source = Path(__file__).read_text(encoding="utf-8")
        tree = ast.parse(source)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "PLUGIN_MANIFEST"
                    for t in node.targets):
                defaults = _defaults_from_manifest(ast.literal_eval(node.value))
                if defaults:
                    return defaults
                break
    except Exception:
        pass

    # 3) 内置兜底表
    return dict(FALLBACK_INPUT_DEFAULTS)


def _defaults_from_manifest(manifest):
    """从清单字典里提取 ``{input_name: default}``。"""
    if not isinstance(manifest, dict):
        return {}
    result = {}
    for item in manifest.get("inputs") or []:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            result[item["name"].strip()] = item.get("default")
    return result


# 内置兜底表：与 plugin.json 的 inputs 默认值保持一致（改清单时同步更新）。
# 只有「默认值非空」的字段才有意义，但列全更稳妥。
# ⚠️ 曾漏了 card_image（三个非空默认值之一）、func 也写错（清单是 test）——
# 这张表只在「plugin.json 与源码内 PLUGIN_MANIFEST 都读不到」的边缘场景生效，
# 一旦与清单漂移，默认值顶替防护就会在那里静默失效。
FALLBACK_INPUT_DEFAULTS = {
    "func": "test",
    "msgtype": "text",
    "touser": "@all",
    "card_image": CARD_DEFAULT_IMAGE,
    "channel_name": "企业微信",
    "api_base": DEFAULT_API_BASE,
    "proxy_mode": "off",
    "split_long": True,
    "history_days": 30,
}


def _read_own_settings_disk(plugin_dir, logger):
    """从磁盘读取本插件已保存的表单设置，返回 ``(params, 说明)``。

    找不到文件时必须把**找过哪些路径**写进日志：这条链路是「其他插件经 OpenAPI
    调用本插件」时唯一能拿到用户凭据与「代理地址」的地方， silently 失败会让
    「网页里发得好好的、被调用时就露馅」这类问题完全看不出原因。
    """
    candidates = _own_settings_candidates(plugin_dir)
    for path in candidates:
        try:
            if not path.is_file():
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        params = _extract_settings_params(payload)
        if params:
            return params, "本插件已保存的设置（%s）" % path.name
    if logger is not None:
        logger.info("未找到本插件已保存的设置文件，探测过：%s"
                    % "、".join(str(p) for p in candidates))
    return {}, ""


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

class _NotifyRunner(object):

    def __init__(self, params, context):
        context = context if isinstance(context, dict) else {}
        self.params = params if isinstance(params, dict) else {}
        self.data_dir = context.get("data_dir") or "."
        self.plugin_dir = context.get("plugin_dir") or ""
        self.log = _Logger()
        self.settings_note = ""

        # 把「调用方实际传进来的参数」原样记进 TTD 运行日志。
        # 排查「任务已受理但发不出去」时，这一行就是最直接的证据：
        # 对方到底传了哪些键、正文是什么、有没有传收件人，一眼可见。
        # 敏感键只回显长度 —— 调用方有可能会把凭据一起传进来。
        self.incoming_params = dict(self.params)
        if self.incoming_params:
            self.log.info("收到调用参数（共 %d 个键，敏感项已脱敏）：%s"
                          % (len(self.incoming_params), _mask_params(self.incoming_params)))
        else:
            self.log.info("本次未收到任何调用参数（将完全使用本插件已保存的设置）")

        # 补齐「调用方没有传」的字段。
        #
        # TgtoDrive 的运行接口只把 params 原样交给插件，**不会**把用户在插件表单里
        # 保存的设置合并进来。所以其他插件调用本插件时若只传正文，凭据与收件人就是空的，
        # 发送必然失败 —— 而且失败发生在后台任务里，调用方很难看到原因。
        # 这里先把本插件已保存的设置补齐进来（调用方显式传的值优先）。
        self._merge_own_settings()

        # 再把调用方传来的「标准化发送内容」覆盖上去（envelope 优先级最高）。
        # 这一步让本插件成为**通用发送模块**：调用方只准备一份标准化内容，
        # 内容完全来自调用方，不使用本插件自己的预设内容。
        #
        # func 先解析：envelope **只在本次调用显式传入时**应用 —— 用户表单里
        # 粘贴保存过的 envelope 不参与设置补齐（见 _merge_own_settings），
        # 否则之后每次「只传 content」的调用都会被陈旧 envelope 覆盖正文，
        # 界面点「发送测试消息」也会发出陈旧内容。
        self.func = _s(self.params, "func", "send") or "send"
        self.envelope_source = ""
        if self.func != "test":
            # func=test 用**内置**测试内容，与 envelope 无关（CALLING.md 原话）。
            self._apply_envelope(self.params.get("envelope"))
        elif str(self.params.get("envelope") or "").strip():
            self.log.info("func=test 使用内置测试内容，忽略本次传入的「标准化发送内容」")

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
        # 投递校验结果（收件人是否真的在应用可见范围内）
        self._delivery_status = ""
        self._delivery_note = ""
        self._recipients = None
        self._invalid_users = []

        self.touser = _s(self.params, "touser")
        self.toparty = _s(self.params, "toparty")
        self.totag = _s(self.params, "totag")
        self.title = _s(self.params, "title")
        self.url = _s(self.params, "url")
        self.content = _s(self.params, "content")

        # 图文消息与卡片图片相关
        self.card_image = _s(self.params, "card_image")
        # 图文消息的描述来源之一（「消息内容」为空时用它）；兼容早期字段名 card_items
        self.card_content = _s(self.params, "card_content") or _s(self.params, "card_items")

        self.split_long = _b(self.params, "split_long", True)
        self.history_days = max(_i(self.params, "history_days", 30), 1)

        self.tgto_base_url = _s(self.params, "tgto_base_url")
        self.tgto_token = _s(self.params, "tgto_token")

        self.config_source = "插件表单"
        self.client = None

    # -- 参数补齐 ----------------------------------------------------------

    def _merge_own_settings(self):
        """把本插件已保存的表单设置补齐到本次参数（调用方显式传的值优先）。

        这是「其他插件调用本插件只传正文」能成功的前提：凭据、收件人、
        分段开关等都从用户自己保存的设置里取，调用方不必也无法提供。

        **关键坑（实测踩到）**：TgtoDrive 的运行接口会把清单里**所有 inputs 按默认值
        填齐**后再交给插件 —— 调用方只传 ``func`` + ``envelope`` 两个键，插件却会
        收到 25 个键，没传的全是默认值。因此：

        * ``corp_id`` 这类**默认值为空**的字段，旧逻辑能正确顶上；
        * ``api_base``（默认 ``https://qyapi.weixin.qq.com``）、``touser``
          （默认 ``@all``）、``card_image``（默认品牌图）这类**默认值非空**的字段，
          会被默认值永久顶掉 —— 表现为「用户在表单里配了转发代理地址，
          被其他插件调用时却从服务器真实 IP 直连，报 60020」，且毫无线索。

        所以这里把「值等于该输入的清单默认值」同样判定为**调用方没有显式传**，
        让已保存的设置顶上（``func`` 与 ``msgtype`` 除外：调用方对这两个字段
        有明确意图，``msgtype`` 会被 ``envelope`` 覆盖，显式传的 text/news 必须保留）。
        """
        saved, note = _read_own_settings_disk(self.plugin_dir, self.log)
        if not saved:
            return
        defaults = _manifest_input_defaults(self.plugin_dir)
        filled, skipped = [], []
        for key, value in saved.items():
            if not isinstance(key, str) or value in (None, "", [], {}):
                continue
            if key in ("func", "msgtype", "envelope"):
                # func 必须由调用方决定（表单里通常存的是 test，沿用它会让外部调用
                # 变成「发一条测试消息」）；msgtype 由调用方/envelope 决定；
                # **envelope 只在本次调用显式传入时应用** —— 用户表单里粘贴保存过的
                # envelope 一旦参与补齐，之后每次「只传 content」的调用都会被那份
                # 陈旧内容覆盖正文（CALLING.md 承诺「界面留空无副作用」）。
                skipped.append(key)
                continue
            current = self.params.get(key)
            if current in (None, ""):
                self.params[key] = value
                filled.append(key)
                continue
            if key in defaults and current == defaults.get(key):
                # 值恰好是清单默认值 → 视为调用方没传，用已保存的设置顶掉
                self.params[key] = value
                filled.append("%s（顶掉默认值 %s）" % (key, current))
        if filled:
            self.settings_note = note
            self.log.info("已从%s补齐 %d 项未传参数：%s"
                          % (note, len(filled), "、".join(sorted(filled))))
        if skipped:
            self.log.info("沿用调用方指定的 %s（未采用表单中保存的值）" % "、".join(skipped))

    # -- 「标准化发送内容」适配 --------------------------------------------

    def _apply_envelope(self, raw):
        """把调用方传来的「标准化发送内容」（JSON）映射到本插件的字段上。

        这是本插件作为**通用发送模块**被调用时的统一入口：调用方只准备一份结构化内容，
        本插件负责把它翻译成企业微信要的请求体。设计要点：

        * **只认已声明的键**：出现未知键就报错并列出允许的键 —— 既不猜、也不静默忽略，
          否则调用方写错字段时会得到「发出去了但内容不对」这种最难查的故障；
        * **覆盖语义明确**：envelope 里给了的字段会覆盖其它来源
          （优先级：envelope > 其它传入参数 > 本插件已保存的设置 > 内置默认）；
        * **不使用本插件预设内容**：正文只来自调用方，内置内容只服务 `func=test`。
        """
        text = str(raw or "").strip()
        if not text:
            return
        try:
            data = json.loads(text)
        except Exception as exc:
            raise ValueError(
                "「标准化发送内容」不是合法 JSON（%s）。它应当是对象，例如 "
                '{"version":1,"msgtype":"text","content":"要发送的正文"}' % exc)
        if not isinstance(data, dict):
            raise ValueError("「标准化发送内容」必须是 JSON 对象，当前是 %s"
                             % type(data).__name__)

        version = data.get("version", ENVELOPE_VERSION)
        try:
            version_ok = int(version) == ENVELOPE_VERSION
        except (TypeError, ValueError):
            version_ok = False
        if not version_ok:
            raise ValueError("「标准化发送内容」的 version 不支持：%r（本插件支持 %d）"
                             % (version, ENVELOPE_VERSION))

        unknown = sorted(k for k in data if k not in ENVELOPE_KEYS)
        if unknown:
            raise ValueError(
                "「标准化发送内容」里有不认识的字段：%s（允许的字段：%s）"
                % ("、".join(unknown), "、".join(ENVELOPE_KEYS)))

        applied = []

        def take(name, target):
            value = data.get(name)
            if value in (None, ""):
                return
            self.params[target] = value
            applied.append(target)

        take("msgtype", "msgtype")
        take("touser", "touser")
        take("title", "title")
        take("url", "url")
        take("image", "card_image")

        # 正文 = content + items 渲染出的「键：值」多行；两者都给时都要
        body_parts = []
        content = data.get("content")
        if isinstance(content, str) and content.strip():
            body_parts.append(content.strip())
        items_text = _render_items(data.get("items"))
        if items_text:
            body_parts.append(items_text)
        if body_parts:
            self.params["content"] = "\n\n".join(body_parts)
            applied.append("content")
        elif "content" in data:
            # 显式给了空正文：按调用方意图清空，避免沿用本插件设置里的旧内容
            self.params["content"] = ""
            applied.append("content(空)")

        source = data.get("source")
        if isinstance(source, str) and source.strip():
            self.envelope_source = source.strip()[:40]

        self.log.info("已应用调用方传入的「标准化发送内容」（version=%s%s）：%s"
                      % (version, "，来源：%s" % self.envelope_source if self.envelope_source
                         else "", "、".join(applied) or "仅占位"))

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
            "接口地址 %s%s｜企业ID %s｜AgentId %s｜Secret %s｜网络 %s"
            % (self.client.masked_base(),
               "（默认地址，未走转发代理）" if self.api_base == DEFAULT_API_BASE
               else "（转发代理）",
               _mask(self.corp_id), self.agent_id or "（未填写）",
               _filled(self.corp_secret),
               "跟随环境变量代理" if self.use_proxy else "直连（不走代理）")
        )
        # 必填项兜底校验：缺凭据时给出**可直接照做**的提示，
        # 不要把请求发出去、最后让企业微信返回一条难懂的 40013。
        missing = [name for name, value in (
            ("企业 ID", self.corp_id), ("应用 AgentId", self.agent_id),
            ("应用 Secret", self.corp_secret)) if not str(value or "").strip()]
        if missing:
            raise ValueError(
                "缺少必填配置：%s —— 请在「应用配置 → ① 应用凭据」中填写"
                "（或在 TgtoDrive 项目设置中保存微信渠道配置）" % "、".join(missing))

    def validate_news(self):
        """图文消息至少要有一项内容，避免发出一张空白卡片。"""
        if self.title or self.content or self.card_content or self.card_image:
            return
        raise ValueError(
            "消息类型为「图文消息」时，至少需要填写「卡片标题」「消息内容」"
            "「卡片消息内容」或「卡片图片」中的一项")

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
        """确定收件人；三项都为空时回退到「管理员白名单」。

        结果会缓存：本方法在一次执行里会被调用多次（构造请求体、生成结果文案、
        投递校验），不缓存会把同一行日志重复打印好几遍。

        ⚠️ ``@all`` 兜底**只在三个收件人字段都为空时**才用。曾经一上来就
        ``touser = self.touser or "@all"``：平台会把 touser 的清单默认值（``@all``）
        填齐，于是「只传 toparty / totag」的调用（文档明确支持的用法）里 touser
        恒为 ``@all`` —— 企业微信的规则是 touser 与 toparty/totag **互斥**，
        build_payload 随即丢掉部门/标签，消息发给**全体可见成员**。
        想只发部门/标签的调用方，实际造成了群发。
        """
        if self._recipients is not None:
            return self._recipients
        touser, toparty, totag = self.touser, self.toparty, self.totag
        if not touser and not toparty and not totag:
            admins = _split_ids(self.admin_users)
            if admins:
                touser = "|".join(admins)
                self.log.info("未填写接收成员/部门/标签，改用「管理员白名单」作为收件人：%s"
                              % "、".join(admins))
            else:
                touser = "@all"
                self.log.info("未填写任何收件人，默认发送给应用全体可见成员（@all）")
        self.log.info("接收人：成员 %s｜部门 %s｜标签 %s"
                      % (touser or "（无）", toparty or "（无）", totag or "（无）"))
        self._recipients = (touser, toparty, totag)
        return self._recipients

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

    def _resolve_card_image(self, value=None):
        """确定图片 URL。

        规则：容器内本地文件 → 上传；内网 http(s) 地址（企业微信服务器访问不到）
        → 先下载再上传换取可用 URL；公网 http(s) 地址 → 直接使用。

        ``value`` 为 None 时取「卡片图片」设置；也可显式传入其它来源的图片地址
        （例如从模板卡片 JSON 里提取出的 picurl）。
        """
        value = self.card_image if value is None else value
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

    def build_news(self, content_override=None):
        """组装图文消息（news）。

        news 是**企业微信客户端与微信插件都能收到**、且**带图**的类型 ——
        在不支持模板卡片的微信里，它是最接近「带图卡片」的形态：
        大图 + 标题 + 描述 + 点击跳转。
        """
        title = self.title or ("【%s】通知" % self.channel_name)
        body = self.content if content_override is None else content_override
        if not body:
            # 「消息内容」为空时，允许用「卡片消息内容」的「键=值」列表作描述
            body = _kv_to_lines(self.card_content)
            if body:
                self.log.info("「消息内容」为空，已用「卡片消息内容」作为图文描述")

        article = {}
        short_title, title_cut = _clip(title, NEWS_TITLE_LIMIT)
        article["title"] = short_title
        if title_cut:
            self.log.warn("图文标题超过 %d 字，已截断（企业微信侧按 128 字节截断）"
                          % NEWS_TITLE_LIMIT)

        if body:
            short_body, body_cut = _clip(body, NEWS_DESC_LIMIT)
            article["description"] = short_body
            if body_cut:
                self.log.warn("图文描述超过 %d 字，已截断（企业微信侧按 512 字节截断）；"
                              "完整内容可放到「卡片跳转链接」指向的页面"
                              % NEWS_DESC_LIMIT)

        url = self.url
        if not url:
            url = CARD_DEFAULT_ACTION_URL
            self.log.warn("图文消息的 url 为空，已回退为 %s（企业微信要求 url 与小程序二选一）"
                          % CARD_DEFAULT_ACTION_URL)
        article["url"] = url

        image_url = self._resolve_card_image()
        if image_url:
            article["picurl"] = image_url
            self.log.info("图文消息已附带图片（%s）" % NEWS_IMAGE_SPEC)
        else:
            self.log.info("图文消息未带图（「卡片图片」为空或上传失败），仍会正常发送")

        return {"articles": [article]}

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
        elif self.msgtype == "news":
            kind, native = _parse_native_card_json(self.card_content)
            if kind == "news":
                self.log.info("「图文消息描述」识别为完整的企业微信请求体 JSON（含 news），直接使用")
                merged = dict(native)
                merged.setdefault("msgtype", "news")
                for key in ("touser", "toparty", "totag", "agentid"):
                    if key in payload:
                        merged.setdefault(key, payload[key])
                payload = merged
            elif kind == "articles":
                self.log.info("「图文消息描述」识别为图文消息 JSON（articles），直接使用")
                payload["news"] = native
            elif kind in ("card", "body"):
                # 兼容从旧版「卡片通知」迁过来的调用方：不必重写内容，
                # 自动提取标题 / 描述 / 键值 / 链接 / 图片，转成图文消息。
                card = native.get("template_card") if kind == "body" else native
                converted = _template_card_to_news(card)
                if converted is None:
                    raise ValueError(
                        "「图文消息描述」是模板卡片 JSON，但未能从中提取出标题或内容。"
                        "请至少提供 main_title.title、sub_title_text 或 "
                        "horizontal_content_list 中的一项，或改用「键=值」写法。")
                article = converted["articles"][0]
                picurl = article.pop("picurl", "")
                if picurl:
                    resolved = self._resolve_card_image(picurl)
                    if resolved:
                        article["picurl"] = resolved
                self.log.info("「图文消息描述」是模板卡片 JSON，已自动转换为图文消息 news")
                payload["news"] = converted
            else:
                payload["news"] = self.build_news(content)
        else:
            raise ValueError("不支持的「消息类型」：%s" % self.msgtype)

        return payload

    def do_send(self, content_override=None, ignore_content=False):
        """发送消息，必要时分段。返回结果字典。"""
        if ignore_content:
            content = content_override or ""
        else:
            content = self.content
            if not content and self.msgtype != "news":
                raise ValueError("「消息内容」为空，请填写后再发送")

        self.validate_encoding_key()
        if self.msgtype == "news":
            self.validate_news()
            return self._dispatch([content], segmented=False)

        chunks = _split_content(content, MESSAGE_BYTE_LIMIT - SEGMENT_SUFFIX_RESERVE)
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
        self._verify_delivery()
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
            if invalid:
                # 企业微信对「不存在 / 不在可见范围」的收件人不报错，只把它列进
                # invaliduser —— 这是自建转发地址下唯一可用的投递校验。
                for uid in _split_ids(invalid):
                    if uid and uid not in self._invalid_users:
                        self._invalid_users.append(uid)
                self.log.warn("⚠ 企业微信报告以下收件人无效（不在应用可见范围或不存在），"
                              "消息不会送达：%s" % invalid)
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
        """实际收件人的可读描述 —— 必须与真正发出去的一致。

        此前直接读 `self.touser`，而没填收件人时会回退成 `@all` 或「管理员白名单」，
        导致结果表显示「（未指定）」而实际发给了全体可见成员，无从对照。
        """
        touser, toparty, totag = self.resolve_recipients()
        if touser == "@all":
            return "全体可见成员（@all）"
        parts = []
        if touser:
            parts.append("成员 %s" % touser)
        if toparty:
            parts.append("部门 %s" % toparty)
        if totag:
            parts.append("标签 %s" % totag)
        return "；".join(parts) or "（未指定）"

    def _verify_delivery(self):
        """发送前校验收件人是否真的收得到。

        企业微信在「收件人不在应用可见范围内」时通常仍返回 errcode=0 与 msgid，
        但消息不投递 —— 只看返回值会把这种情况误判成功。
        """
        touser, _toparty, _totag = self.resolve_recipients()
        self._delivery_status, self._delivery_note = self.client.verify_recipients(touser)
        if self._delivery_status == "ok":
            self.log.info("投递校验：%s" % self._delivery_note)
        elif self._delivery_status == "unknown":
            # 自建转发地址通常只代理 gettoken / message/send，user/list 会 404，
            # 这属于正常降级，不是问题；真正有效的兜底是 message/send 返回的 invaliduser。
            self.log.info("投递校验跳过（该接口在自建转发地址上通常不可用）：%s"
                          % self._delivery_note)
        else:
            self.log.warn("⚠ 投递校验：%s" % self._delivery_note)

    def do_test(self):
        """发送测试消息：内容已内置，点一下即可验证整条链路。

        固定发**两条** —— 一条文本、一条图文消息 news（间隔 3 秒），
        这正是本插件支持的两种类型，也是微信插件都能收到的两种，
        所以一次点击就能同时验证「配置 + 网络 + 收件人 + 微信可收性」。

        内容取 :data:`DEFAULT_TEST_TEXT` / :data:`DEFAULT_TEST_CARD`；
        其他插件调用时可传 ``content`` / ``card_content`` 覆盖。
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # 占位符只对**内置模板**做替换；调用方传入的 content / card_content
        # 原样发送。曾经对用户内容也调 .format()：正文里出现 {foo} 抛 KeyError、
        # {} 抛 IndexError、单个 { 抛 ValueError，异常穿透 run() 直达平台，
        # 用户看到一串 Python 异常而不是可读提示（把 JSON / 代码片段当测试内容
        # 就会撞上）。
        def _fill(template, fallback):
            if template.strip():
                return template
            return fallback.format(now=now, channel=self.channel_name,
                                   api_base=self.client.masked_base())

        text_body = _fill(self.content, DEFAULT_TEST_TEXT)
        news_body = _fill(self.card_content, DEFAULT_TEST_CARD)
        self.log.info("使用内置测试内容：文本 %d 字、图文描述 %d 行"
                      % (len(text_body), len(news_body.splitlines())))

        plans = [
            ("text", "文本消息 text", text_body),
            ("news", "图文消息 news", news_body),
        ]
        self.log.info("发送测试消息：共 %d 条（%s）"
                      % (len(plans), "、".join(plan[1] for plan in plans)))
        self.log.info("两条之间间隔 %d 秒发送" % TEST_SEND_GAP_SECONDS)

        original_msgtype = self.msgtype
        original_card_content = self.card_content
        original_content = self.content
        outcomes = []
        failures = []
        try:
            for index, (kind, label, body) in enumerate(plans):
                if index:
                    self.log.info("等待 %d 秒后发送下一条…" % TEST_SEND_GAP_SECONDS)
                    time.sleep(TEST_SEND_GAP_SECONDS)

                self.msgtype = kind
                if kind == "news":
                    # 图文消息用「键=值」列表作为描述，正文留空以免重复
                    self.card_content = news_body
                    self.title = self.title or "【%s】测试消息" % self.channel_name
                    self.url = self.url or CARD_DEFAULT_ACTION_URL
                    self.content = ""
                    send_body = ""
                else:
                    send_body = body

                self.log.info("→ 发送%s" % label)
                outcome = self._dispatch([send_body], segmented=False)
                outcomes.append((label, kind, outcome))
                if outcome.get("status") != "ok":
                    failures.append("%s：%s" % (label, outcome.get("error") or "发送失败"))
                elif outcome.get("delivery_ok") is False:
                    # **接口返回成功 ≠ 投递成功**：收件人不在应用可见范围时，企业微信
                    # 仍返回 errcode=0 + msgid，但消息不会送达。「发送测试消息」这个按钮
                    # 的用途就是验证「配置 + 网络 + 收件人 + 可收性」，曾经只看 status，
                    # 结果顶部显示「两条都已发送成功」、实际无人收到 —— 自检工具给出假成功。
                    detail = str(outcome.get("delivery_note") or "投递校验未通过")
                    invalid = outcome.get("invalid_users") or []
                    if invalid:
                        detail = "%s；无效收件人：%s" % (detail, "、".join(invalid[:5]))
                    failures.append("%s：接口已受理但没有投递（%s）—— 请检查管理后台"
                                    "该应用的「可见范围」是否包含收件人"
                                    % (label, detail))
        finally:
            self.msgtype = original_msgtype
            self.card_content = original_card_content
            self.content = original_content

        rows = []
        msgids = []
        for label, kind, outcome in outcomes:
            msgids.extend(outcome.get("msgids") or [])
            if outcome.get("status") != "ok":
                verdict = "失败"
            elif outcome.get("delivery_ok") is False:
                verdict = "已受理未投递"
            else:
                verdict = "成功"
            rows.append([
                label,
                MSGTYPE_LABELS.get(kind, kind),
                verdict,
                "、".join(outcome.get("msgids") or []) or (outcome.get("error") or "-")[:60],
            ])
        ok = not failures
        if not ok:
            summary = failures[0]
        else:
            summary = ("两条通知都已发送成功（间隔 %d 秒）。"
                       "文本与图文消息在微信插件里都能收到。" % TEST_SEND_GAP_SECONDS)

        components = [
            {"type": "heading", "text": "发送测试消息"},
            {"type": "alert", "text": summary,
             "style": {"tone": "success" if ok else "danger"}},
            {"type": "table", "label": "本次发送（内置内容，共 %d 条）" % len(plans),
             "headers": ["内容", "消息类型", "结果", "msgid / 错误"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        delivery_states = [o.get("delivery_status") for _, _, o in outcomes]
        return {
            "status": "ok" if ok else "failed",
            "func": self.func,
            "batches_total": len(plans),
            "batches_ok": len([o for _, _, o in outcomes if o.get("status") == "ok"]),
            "msgids": msgids,
            # 投递结论一并返回：调用方若用 func=test 做链路自检，只看 status 会把
            # 「受理了但没人收到」当成成功（曾经就是这个坑）。
            "delivery_ok": all(o.get("delivery_ok") is not False for _, _, o in outcomes),
            "delivery_status": "/".join(s for s in delivery_states if s) or None,
            "invalid_users": sorted({u for _, _, o in outcomes
                                     for u in (o.get("invalid_users") or [])}),
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

    def do_history(self):
        """列出本地发送历史：时间、类型、收件人、结果与 msgid。"""
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
            ["func", "必填", "send 正式发送（调用方用这个）/ test 测试消息 / config 自检 / history 查历史 / docs 本文档"],
            ["msgtype", "必填", "text 文本 / news 图文消息 —— **只有这两种**，它们微信插件都能收到"],
            ["touser", "常用", "UserID，多个用 | 分隔；@all 表示该应用全体可见成员"],
            ["toparty / totag", "可选", "部门 ID / 标签 ID，touser 为 @all 时被忽略"],
            ["content", "常用", "正文：text 的消息内容；news 的图文描述。send 时必填，test 不传则用内置测试文本"],
            ["title", "可选", "标题：news 使用；留空时自动取「渠道名称 + 通知」"],
            ["url", "可选", "点击跳转链接（news 使用）；留空时回退官方站点"],
            ["card_image", "可选", "主图：http(s) 链接、内网地址或容器内本地路径（内网/本地会先上传换成企业微信可用 URL）"],
            ["card_content", "可选", "news 的图文描述备用来源：每行一条「键=值」，或直接粘贴企业微信原生 JSON（news / articles / 模板卡片，模板卡片会被自动转成图文）"],
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
            "        \"msgtype\": \"news\",\n"
            "        \"touser\": \"@all\",\n"
            "        \"title\": \"新入库剧集：示例标题\",\n"
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
            # 链接放在最前面：点「查看调用方法」后，用户最先看到的就是这个可点击的教程入口，
            # 不用再往下翻（历史 bug：链接埋在长文中间，其他开发者找不到）。
            {"type": "link", "label": "📄 打开完整调用教程（CALLING.md）", "href": DOCS_URL,
             "style": {"tone": "primary", "size": "large", "align": "center"}},
            {"type": "text", "text": "上方链接会在新标签页打开仓库里的 CALLING.md；下面是本页速查。",
             "style": {"tone": "muted", "size": "small", "align": "center"}},
            {"type": "markdown", "text": (
                "本插件可以通过 TgtoDrive OpenAPI 被**其他插件或脚本**调用，"
                "用于发送企业微信通知。消息类型只有**两种**：\n\n"
                "- `text` 文本消息 —— 纯文本，微信插件可收；\n"
                "- `news` 图文消息 —— 大图 + 标题 + 描述 + 点击跳转，微信插件同样可收。\n\n"
                "这两种都是微信插件能收到的类型，调用方按需二选一即可。\n\n"
                "调用入口：`POST /api/toolbox/plugins/wecom-notify/run`")},
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
        if self.envelope_source:
            # 让调用方一眼确认「我传的内容被用上了」
            components[2]["rows"].append(["内容来源", "调用方「%s」传入" % self.envelope_source])
        if error:
            components.append({"type": "alert", "text": error, "style": {"tone": "danger"}})

        # 投递校验：收件人不在应用可见范围时，企业微信会「接受请求但不投递」
        if self._delivery_status in ("empty", "missing"):
            components.append({
                "type": "alert",
                "text": "投递校验：%s" % self._delivery_note,
                "style": {"tone": "warning"},
            })

        # 企业微信在返回里列出的无效收件人（自建转发地址下唯一可用的投递校验）
        if self._invalid_users:
            components.append({
                "type": "alert",
                "text": ("企业微信报告以下收件人无效（不在应用可见范围或不存在），"
                         "消息不会送达：%s。请到管理后台该应用的「可见范围」里加入他们。"
                         % "、".join(self._invalid_users[:8])),
                "style": {"tone": "danger"},
            })

        if status == "ok":
            # 本插件只提供文本与图文消息 —— 这两种微信插件都能收到。
            # 收不到时几乎都是「配置」问题，所以把最容易被忽略的三处列出来。
            components.append({
                "type": "text",
                "text": ("本插件只发送**微信插件能收到**的两种类型（文本 / 图文消息）。"
                         "「%s」已同时投递给企业微信客户端。**若微信里仍收不到**，"
                         "请按顺序检查三处：\n"
                         "1. 管理后台 → 该应用 →「可见范围」是否包含收件人；\n"
                         "2. 管理后台 → 该应用 → 是否勾选了「**在微工作台中始终进入主页**」——"
                         "勾选后应用在微信端**只能收到文本消息**（其他类型会被转成"
                         "「到企业微信查看」的提示），这一项最容易被忽略；\n"
                         "3. 微信 → 通讯录 → 本企业 → 微信插件 → 右上角 → 设置 →"
                         "「接收应用消息」是否已打开。"
                         % MSGTYPE_LABELS.get(self.msgtype, self.msgtype)),
                "style": {"tone": "muted"},
            })

        components.extend([
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ])
        # 投递是否可信：企业微信在「收件人不在应用可见范围」时**仍返回 errcode=0 与 msgid**，
        # 只是不投递。调用方若只看 status 会把「请求成功但没人收到」误判为成功，
        # 因此这里把收件人与投递校验结论一并结构化返回，让调用方能如实告知用户。
        # "unknown" 表示查不到通讯录（如自建转发地址），此时不作判定，避免误报。
        delivery_ok = (self._delivery_status in ("ok", "unknown")
                       and not self._invalid_users)
        return {
            "status": status,
            "func": self.func,
            "msgtype": self.msgtype,
            "sent": sent,
            "total": total,
            "msgids": [m for m in msgids if m],
            "error": error,
            "recipient": recipient_note,
            "delivery_ok": delivery_ok,
            "delivery_status": self._delivery_status,
            "delivery_note": self._delivery_note,
            "invalid_users": list(self._invalid_users),
            "envelope_source": self.envelope_source or None,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        if self.func not in VALID_FUNCS:
            raise ValueError("不支持的执行功能：%s" % self.func)
        if self.msgtype not in VALID_MSGTYPES:
            raise ValueError("不支持的消息类型：%s" % self.msgtype)

        self.log.info("企业微信通知启动，执行功能：%s" % FUNC_LABELS.get(self.func, self.func))
        if self.envelope_source:
            self.log.info("本次由「%s」调用，正文与参数取自它传入的「标准化发送内容」"
                          % self.envelope_source)
        # 「最终会用什么发」也记一行：把「收到的参数」与「实际生效的值」对照起来看，
        # 才能分清是对方没传、还是本插件没接住。
        self.log.info("本次将发送：消息类型=%s｜收件人=%s｜标题=%s｜正文 %d 字%s"
                      % (MSGTYPE_LABELS.get(self.msgtype, self.msgtype),
                         self.touser or "（未指定，按下面规则兜底）",
                         self.title or "（无）", len(self.content or ""),
                         "｜内容来自调用方「%s」" % self.envelope_source
                         if self.envelope_source else "｜内容来自本插件设置"))
        if self.func == "docs":
            # 纯文档输出，不需要任何配置与网络请求
            return self.do_docs()

        self.prepare_config()

        if self.func == "config":
            return self.do_config_check()
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
