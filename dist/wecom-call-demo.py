# -*- coding: utf-8 -*-
# 由 scripts/package_plugin.py 依据 plugins/wecom-call-demo/ 自动生成，请勿直接编辑。
# 单文件插件：顶层唯一的 PLUGIN_MANIFEST 常量字典 + 入口源码。

PLUGIN_MANIFEST = {
  'schema_version': 1,
  'id': 'wecom-call-demo',
  'name': '微信通知调用示例',
  'version': '1.0.0',
  'description': '演示「一个 TgtoDrive 插件如何调用另一个插件」的最小可用范例：本插件通过 OpenAPI 运行接口调用「企业微信通知」插件（wecom-notify）发送消息。界面分为「文本消息」与「卡片消息」两个互相独立的子页面，各自配置收件人与内容，点对应的按钮即发出。发送前会先读取目标插件的清单，校验本次要传的参数「键是否已声明、下拉取值是否在选项内」，因此不会出现难懂的 HTTP 400；发送后会轮询任务结果，并区分「请求被受理」与「消息真的送达」（delivery_ok），避免把没收到的消息报成成功。目标插件 id 可配置，便于扩展或换用其它通知插件。',
  'author': 'a2695154202',
  'entry': 'plugin.py',
  'timeout': 120,
  'inputs': [
    {
      'name': 'func',
      'label': '执行操作',
      'type': 'select',
      'default': 'send_text',
      'options': [
        {
          'label': '发送文本消息',
          'value': 'send_text',
        },
        {
          'label': '发送卡片消息',
          'value': 'send_card',
        },
      ],
      'help': '决定本次要执行的动作。页面右侧的两个按钮会**覆盖**这里的取值（点「发送文本消息」就是 send_text），所以你通常不用改它；需要从接口调用本插件时，用它指定动作。\n\n新增动作的做法见 README「如何新增一种通知」。',
    },
    {
      'name': 'text_touser',
      'label': '收件人（UserID，留空沿用目标插件设置）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 用「企业微信通知」里已配好的收件人；也可填 @all 或 zhangsan|lisi',
      'help': '传给「企业微信通知」插件的 `touser`：成员 UserID，多个用 | 分隔；`@all` 表示该应用全体可见成员。\n\n**留空（默认）＝ 沿用目标插件里已保存的收件人** —— 推荐这样，因为「企业微信通知」插件自己测试能收到，用的就是那份配置；一旦在这里填了值，就会**覆盖**它。\n\n如果填了收件人却收不到，最可能是该 UserID 不在该应用的「可见范围」内（企业微信会接受请求但不投递），结果页会明确提示。\n\n本字段只对「文本消息」子页面生效。',
    },
    {
      'name': 'text_content',
      'label': '消息正文',
      'type': 'textarea',
      'default': '',
      'placeholder': '你好，这是一条来自「微信通知调用示例」的文本消息。\n时间：{now}',
      'help': '文本消息的正文（对应目标插件的 `content`）。\n\n支持两个占位符，会在发送前替换：\n• `{now}` → 当前时间\n• `{source}` → 本插件名称\n\n留空时点发送会给出提示而不是静默失败。',
    },
    {
      'name': 'card_touser',
      'label': '收件人（UserID，留空沿用目标插件设置）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 用「企业微信通知」里已配好的收件人；也可填 @all 或 zhangsan|lisi',
      'help': '传给「企业微信通知」插件的 `touser`。本字段只对「卡片消息」子页面生效，与文本页的收件人互相独立。\n\n**留空（默认）＝ 沿用目标插件里已保存的收件人**；填了值就会**覆盖**它。',
    },
    {
      'name': 'card_title',
      'label': '卡片标题',
      'type': 'text',
      'default': '示例卡片消息',
      'placeholder': '示例卡片消息',
      'help': '卡片标题（对应目标插件的 `title`）。企业微信侧上限 128 字节，目标插件会按 60 字符保守截断并在日志中说明。',
    },
    {
      'name': 'card_content',
      'label': '卡片内容',
      'type': 'textarea',
      'default': '状态=✅ 示例通知\n来源={source}\n时间={now}\n说明=这条卡片由本示例插件通过「企业微信通知」插件发送',
      'placeholder': '状态=✅ 示例通知\n来源=微信通知调用示例',
      'help': '已预填一段示例内容，点「发送卡片消息」即可直接验证链路。\n\n两种写法都支持：\n① 每行一条「键=值」（`=`、`:`、`：`、`|` 分隔）—— 目标插件会渲染成图文的描述；\n② 直接粘贴企业微信原生 JSON（含 `news` / `articles` 原样发送；含 `card_type` 会自动转成图文）。\n\n支持 `{now}` / `{source}` 占位符，发送前替换。',
    },
    {
      'name': 'card_url',
      'label': '点击跳转链接',
      'type': 'text',
      'default': 'https://github.com/a2695154202/ttd-plugins',
      'placeholder': 'https://example.com/detail（留空则回退官方站点）',
      'help': '图文的点击跳转地址，需带 http/https 协议头。留空时目标插件会回退到官方站点，并在日志中说明。',
    },
    {
      'name': 'card_image',
      'label': '卡片主图',
      'type': 'text',
      'default': '',
      'placeholder': 'https://example.com/cover.jpg（留空则发送不带图的图文）',
      'help': '图文消息的主图，可填 http(s) 链接、内网地址或容器内本地图片路径（后两者由目标插件自动下载后上传换取可用 URL）。留空则发送不带图的图文消息，仍然是有效的通知。',
    },
    {
      'name': 'tgto_base_url',
      'label': 'TgtoDrive 地址',
      'type': 'text',
      'default': 'http://127.0.0.1:12366',
      'placeholder': 'http://127.0.0.1:12366',
      'help': '调用目标插件用的服务地址。本插件与 TgtoDrive 在同一容器，因此通常就是 http://127.0.0.1:12366。\n\n留空时读容器环境变量 `TGTO_OPENAPI_BASE_URL`。',
    },
    {
      'name': 'tgto_token',
      'label': 'OpenAPI 令牌',
      'type': 'password',
      'default': '',
      'help': '调用目标插件所需的 Bearer 令牌，在「实用工具 → OpenAPI」页面创建。\n\n留空时读容器环境变量 `TGTO_OPENAPI_TOKEN`。令牌不会出现在运行日志、结果页或返回值中；本插件的设置以明文 JSON 保存在服务器插件目录，更在意安全时请改用环境变量并让此项留空。',
    },
    {
      'name': 'wecom_plugin_id',
      'label': '目标插件 id',
      'type': 'text',
      'default': 'wecom-notify',
      'placeholder': 'wecom-notify',
      'help': '要调用的插件 id，默认是「企业微信通知」(`wecom-notify`)。\n\n这是本示例的**扩展点**：只要目标插件同样支持「收件人 + 内容」这套输入，改成本插件 id 即可换成别的通知出口，无需改代码。',
    },
    {
      'name': 'wait_for_result',
      'label': '等待并校验投递结果',
      'type': 'boolean',
      'default': True,
      'help': '开启时：提交任务后轮询目标插件的执行结果，读取「实际收件人」与「投递是否可信」，据此判断消息到底有没有送达。\n\n关闭时：提交成功即返回，不再确认结果（适合不想等待的场景，但无法区分「已受理」与「已送达」）。',
    },
  ],
  'ui': {
    'width': 'wide',
    'layout': 'stack',
    'components': [
      {
        'type': 'heading',
        'text': '🧪 微信通知调用示例',
      },
      {
        'type': 'markdown',
        'text': '本插件**不直接对接企业微信**，而是演示**插件之间如何互相调用**：它把内容交给「企业微信通知」插件（`wecom-notify`）发送。\n\n两个子页面**互相独立**：左边切到「**文本消息**」或「**卡片消息**」，填好各自的内容后，点右侧对应的按钮即可。',
      },
      {
        'type': 'alert',
        'text': '前提：「企业微信通知」插件已安装并启用，且已填好企业 ID / 应用 AgentId / 应用 Secret。另外需要在「连接设置」里填 OpenAPI 令牌（或用容器环境变量 TGTO_OPENAPI_TOKEN）。缺少任一项时，点发送会在结果页明确告诉你是哪一步不满足，不会静默失败。',
        'style': {
          'tone': 'warning',
        },
      },
      {
        'type': 'grid',
        'columns': 4,
        'children': [
          {
            'type': 'group',
            'style': {
              'span': 3,
            },
            'children': [
              {
                'type': 'tabs',
                'children': [
                  {
                    'type': 'card',
                    'label': '文本消息',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '发送一条**纯文本**通知（对应目标插件的 `msgtype=text`）。文本在微信插件与企业微信客户端里都能完整显示。',
                      },
                      {
                        'type': 'field',
                        'name': 'text_touser',
                      },
                      {
                        'type': 'field',
                        'name': 'text_content',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '卡片消息',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '发送一条**带图文**的通知（对应目标插件的 `msgtype=news`）。企业微信官方限制下，微信插件收不到模板卡片，所以「卡片效果」用**图文消息**实现：大图 + 标题 + 描述 + 点击跳转 —— 微信里同样能收到。',
                      },
                      {
                        'type': 'field',
                        'name': 'card_touser',
                      },
                      {
                        'type': 'field',
                        'name': 'card_title',
                      },
                      {
                        'type': 'field',
                        'name': 'card_content',
                      },
                      {
                        'type': 'field',
                        'name': 'card_url',
                      },
                      {
                        'type': 'field',
                        'name': 'card_image',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '连接设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '两个子页面共用这部分配置。填好后建议先点右侧按钮发一条，结果页会列出「实际发出的参数」与「投递校验结论」，便于对照。',
                      },
                      {
                        'type': 'field',
                        'name': 'tgto_base_url',
                      },
                      {
                        'type': 'field',
                        'name': 'tgto_token',
                      },
                      {
                        'type': 'field',
                        'name': 'wecom_plugin_id',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'wait_for_result',
                      },
                    ],
                  },
                ],
              },
            ],
          },
          {
            'type': 'group',
            'style': {
              'span': 1,
            },
            'children': [
              {
                'type': 'field',
                'name': 'func',
              },
              {
                'type': 'button',
                'label': '发送文本消息',
                'action': 'run',
                'params': {
                  'func': 'send_text',
                },
                'style': {
                  'tone': 'primary',
                  'size': 'large',
                  'variant': 'solid',
                },
              },
              {
                'type': 'button',
                'label': '发送卡片消息',
                'action': 'run',
                'params': {
                  'func': 'send_card',
                },
                'style': {
                  'tone': 'success',
                  'size': 'large',
                  'variant': 'solid',
                },
              },
            ],
          },
        ],
      },
      {
        'type': 'divider',
      },
      {
        'type': 'text',
        'text': '发出去的参数只包含内容类字段（func / msgtype / touser / content / title / url / card_image）；企业 ID、Secret、代理地址等由「企业微信通知」插件从它自己已保存的设置里补齐 —— 调用方不需要、也不应该持有这些凭据。',
        'style': {
          'tone': 'muted',
        },
      },
      {
        'type': 'text',
        'text': '扩展：目标插件 id 可改（「连接设置」里的 wecom_plugin_id），动作清单也可按 README 的说明增加一项。',
        'style': {
          'tone': 'muted',
        },
      },
    ],
  },
}


# -*- coding: utf-8 -*-
"""微信通知调用示例 · TgtoDrive 插件

**用途：演示「一个插件如何调用另一个插件」。**

本插件不直接对接企业微信，而是通过 TgtoDrive 的 OpenAPI 运行接口，
调用「企业微信通知」插件（默认 id `wecom-notify`）把消息发出去。
把「插件互调」需要的要素都摆出来：

  1. 目标地址与令牌 —— 读取容器环境变量 ``TGTO_OPENAPI_BASE_URL`` /
     ``TGTO_OPENAPI_TOKEN``，也允许在本插件表单里单独填写；
  2. 目标插件的清单 —— 先 ``GET /api/toolbox/plugins`` 读出它的 ``inputs``，
     校验本次要传的**键是否都已声明**、**下拉取值是否都在 ``options`` 内**。
     这两条是 TgtoDrive 服务端会强校验的，提前挡住可以避免难懂的 HTTP 400；
  3. 提交运行任务 —— ``POST /api/toolbox/plugins/<id>/run``，
     请求体 ``{"params": {...}}``（**不要**传 ``save_settings``）；
  4. 轮询任务结果 —— ``GET /api/toolbox/plugins/jobs/<job_id>``；
     该接口在规范里没有响应 schema（``inferred``），因此任务 ID 与状态都做容错读取；
  5. 区分「请求被受理」与「消息真的送达」—— 企业微信在收件人不在应用可见范围时
     仍返回 ``errcode=0``，所以这里读取目标插件返回的 ``delivery_ok`` / ``recipient`` /
     ``invalid_users``，据此报告，避免把没收到的消息说成成功。

界面分「文本消息」「卡片消息」两个互相独立的子页面，各自配置收件人与内容。
新增一种通知的做法见同目录 README.md。
"""

import json
import os
import re
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover - 仅在极简环境触发
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PLUGIN_NAME = "微信通知调用示例"

DEFAULT_TARGET_PLUGIN = "wecom-notify"
DEFAULT_BASE_URL = "http://127.0.0.1:12366"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# 轮询目标插件结果的次数与间隔（拿不到 job_id 或超时都不影响「消息已提交」这个事实）
JOB_POLL_ATTEMPTS = 5
JOB_POLL_INTERVAL = 2

API_PLUGINS = "/api/toolbox/plugins"
API_RUN = "/api/toolbox/plugins/%s/run"
API_JOB = "/api/toolbox/plugins/jobs/%s"

# 动作 → 人类可读名称。新增动作时：这里加一项 + plugin.json 的 func 选项加一项 + 补一个处理方法。
ACTIONS = {
    "send_text": "发送文本消息",
    "send_card": "发送卡片消息",
}
VALID_ACTIONS = tuple(ACTIONS)

# 两个子页面各自独立；下面这张表把「动作」映射到「用哪一页的字段」与「发给目标插件的 msgtype」。
# 想再加一种通知，通常只需要在这里加一行、再写一个 _send_xxx 方法。
ACTION_SPEC = {
    "send_text": {"label": "文本消息", "msgtype": "text",
                  "touser_key": "text_touser", "content_key": "text_content"},
    "send_card": {"label": "卡片消息", "msgtype": "news",
                  "touser_key": "card_touser", "content_key": "card_content"},
}

# 目标插件的「执行功能」取值（企业微信通知插件的契约）
TARGET_FUNC_SEND = "send"

# 「标准化发送内容」的版本号。调用方只需准备这份结构，发送逻辑全在目标插件里 ——
# 契约一旦稳定，新增发送能力不需要改调用方（详见 README「标准化发送内容」）。
ENVELOPE_VERSION = 1

# 正文里可用的占位符，发送前替换
PLACEHOLDER_NOW = "{now}"
PLACEHOLDER_SOURCE = "{source}"

MASK_RE = re.compile(r"(\d{4,}):([A-Za-z0-9_\-]{20,})")


# ---------------------------------------------------------------------------
# 日志
# ---------------------------------------------------------------------------

class _Logger(object):
    """同时写入标准输出（TgtoDrive 运行日志）与内存缓冲区（结果页内日志窗口）。"""

    MAX_LINES = 2000

    def __init__(self):
        self.lines = []

    def _emit(self, level, message):
        text = "[%s] [%s] %s" % (datetime.now().strftime("%H:%M:%S"), level, message)
        self.lines.append(text)
        if len(self.lines) > self.MAX_LINES:
            del self.lines[:len(self.lines) - self.MAX_LINES]
        try:
            print(text, flush=True)
        except Exception:
            pass

    def info(self, message):
        self._emit("INFO", message)

    def warn(self, message):
        self._emit("WARN", message)

    def error(self, message):
        self._emit("ERROR", message)

    def text(self, limit=20000):
        return "\n".join(self.lines)[-limit:]


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------

def _as_bool(value, default=False):
    """把表单/JSON 传进来的值折成布尔（与其它插件保持一致的宽松口径）。"""
    if value is None or value == "":
        return default
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in ("1", "true", "yes", "on", "y", "是", "真"):
        return True
    if text in ("0", "false", "no", "off", "n", "否", "假"):
        return False
    return default


def scrub_text(text, secrets=()):
    """把日志/返回里可能出现的凭据抹掉（本插件只回显目标插件的响应，仍做一层防护）。"""
    out = str(text or "")
    for secret in secrets:
        secret = str(secret or "")
        if len(secret) >= 6:
            out = out.replace(secret, "***")
    out = MASK_RE.sub(r"\1:***", out)
    return out


def _walk_dicts(node, max_depth=6, limit=500):
    """深度优先遍历出所有 dict（含嵌套），用于容错解析字段名不保证的响应。"""
    seen = 0
    stack = [(node, 0)]
    while stack:
        current, level = stack.pop()
        if isinstance(current, dict):
            seen += 1
            if seen > limit:
                return
            yield current
            if level < max_depth:
                for value in current.values():
                    if isinstance(value, (dict, list)):
                        stack.append((value, level + 1))
        elif isinstance(current, list) and level < max_depth:
            for item in current:
                if isinstance(item, (dict, list)):
                    stack.append((item, level + 1))


def _safe_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None


def _http_json(method, url, headers=None, body=None):
    """发一个 JSON 请求，返回 ``(status, text, data)``；网络异常时 status 为 None。"""
    headers = dict(headers or {})
    if requests is not None:
        try:
            response = requests.request(
                method, url, headers=headers, json=body,
                timeout=(CONNECT_TIMEOUT, READ_TIMEOUT), allow_redirects=False,
            )
            text = response.text or ""
            return response.status_code, text, _safe_json(text)
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc), None

    # requests 不可用时的标准库回退
    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with urllib.request.urlopen(request, timeout=READ_TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
            return response.status, text, _safe_json(text)
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        return exc.code, text, _safe_json(text)
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc), None


def _entry_id(node):
    """从插件条目里取 id（该响应无 schema，字段名不保证）。"""
    for key in ("id", "plugin_id", "pluginId", "slug", "name"):
        value = node.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _find_plugin_entry(payload, plugin_id):
    """在 ``GET /api/toolbox/plugins`` 的响应里找到目标插件条目。"""
    wanted = str(plugin_id or "").strip().lower()
    if not wanted:
        return None
    for node in _walk_dicts(payload):
        if _entry_id(node).lower() == wanted:
            return node
    return None


def _inputs_of(entry):
    """取出插件的 inputs 定义：``{name: 定义}``；取不到返回空字典。"""
    raw = entry.get("inputs") if isinstance(entry, dict) else None
    if not isinstance(raw, list):
        return {}
    result = {}
    for item in raw:
        if isinstance(item, dict) and isinstance(item.get("name"), str):
            result[item["name"].strip()] = item
    return result


def _has_plugin_collection(payload):
    """判断响应里是否真的带了「插件集合」。

    用来区分两种「找不到目标插件」：

    * 带了集合但里面没有目标 → **确定**没安装，可以直接拦住不发请求；
    * 完全没有集合（空对象、字段名变了、返回了别的东西）→ 无法判断，只提示、不阻断。

    少了这一层，`{}` 这种合法但没有内容的响应会被误判成「插件没装」。
    """
    if not isinstance(payload, dict):
        return False
    for key in ("plugins", "list", "items", "data", "result", "records"):
        value = payload.get(key)
        if isinstance(value, list):
            return True
        if isinstance(value, dict) and _has_plugin_collection(value):
            return True
    return False


def _enabled_of(entry):
    """判断插件是否启用；字段名/取值不保证，识别不出时返回 ``None``（不误判）。"""
    if not isinstance(entry, dict):
        return None
    for key in ("enabled", "enable", "active", "is_enabled", "running"):
        if key in entry and isinstance(entry[key], bool):
            return entry[key]
    for key in ("status", "state"):
        value = entry.get(key)
        if isinstance(value, str):
            low = value.strip().lower()
            if low in ("enabled", "active", "on", "running", "normal", "ok"):
                return True
            if low in ("disabled", "inactive", "off", "stopped", "paused"):
                return False
    return None


def _find_job_id(payload):
    """从运行接口的响应里容错取任务 ID（该响应无 schema，字段名不保证）。"""
    id_keys = ("jobid", "taskid", "id", "uuid")
    wrapper_keys = ("job", "jobs", "task", "tasks", "data", "result", "payload", "info")

    def norm(key):
        return str(key).lower().replace("_", "").replace("-", "")

    def pick(node):
        if not isinstance(node, dict):
            return ""
        for key, value in node.items():
            if norm(key) in id_keys and isinstance(value, (str, int)) \
                    and str(value).strip():
                return str(value).strip()
        return ""

    def walk(node, depth):
        if depth > 3:
            return ""
        found = pick(node)
        if found:
            return found
        items = node if isinstance(node, list) else [node]
        for item in items:
            if not isinstance(item, dict):
                continue
            found = pick(item)
            if found:
                return found
            for key, value in item.items():
                if norm(key) in wrapper_keys:
                    found = walk(value, depth + 1)
                    if found:
                        return found
        return ""

    if not isinstance(payload, dict):
        return ""
    return walk(payload, 0)


# ---------------------------------------------------------------------------
# 执行体
# ---------------------------------------------------------------------------

class _DemoRunner(object):

    def __init__(self, params, context):
        context = context if isinstance(context, dict) else {}
        self.p = dict(params or {})
        self.log = _Logger()
        self.data_dir = Path(str(context.get("data_dir") or "."))
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        self.action = str(self.p.get("func") or "send_text").strip().lower()
        base = str(self.p.get("tgto_base_url") or "").strip() \
            or str(os.environ.get("TGTO_OPENAPI_BASE_URL") or "").strip()
        self.base_url = (base or DEFAULT_BASE_URL).rstrip("/")
        self.base_from_form = bool(str(self.p.get("tgto_base_url") or "").strip())
        self.token = str(self.p.get("tgto_token") or "").strip() \
            or str(os.environ.get("TGTO_OPENAPI_TOKEN") or "").strip()
        self.target_id = str(self.p.get("wecom_plugin_id") or "").strip() \
            or DEFAULT_TARGET_PLUGIN
        self.wait_result = _as_bool(self.p.get("wait_for_result"), True)

        # 本次调用的过程信息，供结果页展示
        self.target_entry = None
        self.target_inputs = {}
        self.job_id = ""
        self.sent_params = {}
        self.envelope = {}

    # -- 基础 --------------------------------------------------------------

    def _expand(self, text):
        """替换正文里的占位符。"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return str(text or "").replace(PLACEHOLDER_NOW, now).replace(PLACEHOLDER_SOURCE, PLUGIN_NAME)

    def _headers(self):
        return {"Authorization": "Bearer %s" % self.token} if self.token else {}

    def _require_endpoint(self):
        """确认「地址 + 令牌」齐备；缺什么就明确说缺什么。"""
        if not self.token:
            raise ValueError(
                "未配置 OpenAPI 令牌：请在「连接设置」里填写「OpenAPI 令牌」，"
                "或为容器配置环境变量 TGTO_OPENAPI_TOKEN 后重启服务。"
                "令牌在「实用工具 → OpenAPI」页面创建。")
        if not re.match(r"^https?://", self.base_url, re.IGNORECASE):
            raise ValueError("「TgtoDrive 地址」需要带 http:// 或 https:// 前缀，当前为 %r"
                             % self.base_url)

    # -- 读取目标插件清单（前提校验） ---------------------------------------

    def _load_target(self):
        """读取目标插件条目与其 inputs。

        返回 ``(entry, inputs, 原因, 结论是否确定)``。最后一位很关键：
        「列表读到了、但里面没有这个插件」是**确定**的结论（没装），应当直接拦住；
        而「列表本身没读到」是不确定的（可能是权限或响应格式问题），只提示、不阻断。
        """
        status, text, data = _http_json("GET", self.base_url + API_PLUGINS,
                                        headers=self._headers())
        if status is None:
            return None, {}, "请求失败：%s" % scrub_text(text, [self.token]), False
        if not 200 <= status < 300:
            return None, {}, ("HTTP %s：%s"
                              % (status, scrub_text((text or "")[:200], [self.token]))), False
        if not isinstance(data, dict):
            return None, {}, "响应不是 JSON 对象", False
        entry = _find_plugin_entry(data, self.target_id)
        if entry is None:
            # 只有在「响应确实带了插件集合」时，才能断定是没安装；
            # 否则（空对象、字段名变了）无法判断，交给调用方继续尝试。
            conclusive = _has_plugin_collection(data)
            return None, {}, ("插件列表里没有 id 为 %r 的插件" % self.target_id), conclusive
        return entry, _inputs_of(entry), "", False

    def _preflight(self, target_params):
        """在发出请求前，按目标插件的清单校验本次参数。

        返回 ``(问题列表, 提示列表)``；问题非空表示「不该发出去」。
        """
        problems, notes = [], []
        entry, inputs, reason, conclusive = self._load_target()
        if entry is None:
            if conclusive:
                problems.append(
                    "%s —— 请到「我的插件」确认它已安装并启用，"
                    "或修正「连接设置 → 目标插件 id」（当前为 %r）。"
                    % (reason, self.target_id))
                self.log.error("目标插件不存在，未发出任何请求：%s" % reason)
                return problems, notes
            # 读不到清单不等于调用一定失败（例如接口权限受限），因此只提示、不阻断
            notes.append("未能读取目标插件清单（%s），已跳过参数预校验，直接尝试调用。" % reason)
            self.log.warn(notes[-1])
            return problems, notes

        self.target_entry = entry
        self.target_inputs = inputs
        version = entry.get("version")
        self.log.info("目标插件：%s%s，声明了 %d 个输入"
                      % (self.target_id, (" v%s" % version) if version else "", len(inputs)))

        enabled = _enabled_of(entry)
        if enabled is False:
            problems.append("目标插件「%s」当前**未启用**，请先到「我的插件」里启用它。" % self.target_id)

        if inputs:
            unknown = sorted(k for k in target_params if k not in inputs)
            if "envelope" in unknown:
                problems.append(
                    "目标插件「%s」不支持「标准化发送内容」（它的清单里没有 envelope 输入）。"
                    "请到「我的插件」把它更新到支持 envelope 的版本。" % self.target_id)
                unknown.remove("envelope")
            if unknown:
                problems.append(
                    "以下参数键不在目标插件的 inputs 里，服务端会判为「未知参数」直接拒绝：%s"
                    % "、".join(unknown))
            for key, value in target_params.items():
                spec = inputs.get(key) or {}
                if spec.get("type") in ("select", "radio"):
                    options = [o.get("value") for o in (spec.get("options") or [])
                               if isinstance(o, dict)]
                    if options and value not in options:
                        problems.append(
                            "参数 %s=%r 不在目标插件该字段的选项内（可选：%s）"
                            % (key, value, "、".join(str(o) for o in options)))
            missing = []
            for name, spec in inputs.items():
                if not spec.get("required"):
                    continue
                if target_params.get(name) in (None, ""):
                    missing.append(name)
            if missing:
                problems.append("目标插件的必填项没有提供：%s" % "、".join(sorted(missing)))
        else:
            notes.append("目标插件条目里没有可读的 inputs 定义，已跳过参数预校验。")
            self.log.warn(notes[-1])
        return problems, notes

    # -- 调用目标插件 ------------------------------------------------------

    def _submit(self, target_params):
        """提交运行任务，返回 ``(job_id, 说明, 原始响应片段)``。"""
        url = self.base_url + API_RUN % self.target_id
        self.sent_params = dict(target_params)
        self.log.info("提交任务：POST %s" % url)
        self.log.info("本次参数：%s" % json.dumps(target_params, ensure_ascii=False)[:600])
        status, text, data = _http_json("POST", url, headers=self._headers(),
                                        body={"params": target_params})
        if status is None:
            raise ValueError("调用目标插件失败：%s" % scrub_text(text, [self.token]))
        snippet = scrub_text((text or "")[:200], [self.token])
        if status not in (200, 201, 202):
            hint = ""
            if status == 400:
                hint = "（参数被拒绝：请核对目标插件的 inputs 与下拉选项）"
            elif status == 404:
                hint = "（未找到该插件：请在「我的插件」确认它已安装并启用）"
            elif status in (401, 403):
                hint = "（OpenAPI 令牌无效或权限不足）"
            elif status == 503:
                hint = "（服务暂时不可用，或目标插件已有未完成的任务）"
            raise ValueError("目标插件返回 HTTP %s%s｜%s" % (status, hint, snippet))

        job_id = _find_job_id(data) if isinstance(data, dict) else ""
        if job_id:
            self.log.info("任务已提交，job_id=%s" % job_id)
            return job_id, "已提交", snippet
        self.log.warn("响应里没取到任务 ID，无法确认执行结果；响应体：%s" % snippet)
        return "", "已提交（未取到任务 ID，未确认结果）", snippet

    def _poll(self, job_id):
        """轮询任务结果，返回 ``(状态, 结果字典)``；状态取 ``ok``/``failed``/``pending``。"""
        url = self.base_url + API_JOB % job_id
        for attempt in range(JOB_POLL_ATTEMPTS):
            if attempt:
                time.sleep(JOB_POLL_INTERVAL)
            status, text, data = _http_json("GET", url, headers=self._headers())
            if status is None or not isinstance(data, dict):
                continue
            # 任务对象可能在 result / job / data 任一层（该接口无 schema）
            result = None
            for key in ("result", "job", "data"):
                node = data.get(key)
                if isinstance(node, dict) and node:
                    result = node
                    break
            if result is None:
                result = data
            state = str(result.get("status") or result.get("state") or "").strip().lower()
            if state in ("ok", "success", "done", "completed", "finished"):
                return "ok", result
            if state in ("failed", "error", "failure", "timeout"):
                return "failed", result
        return "pending", {}

    # -- 两个动作 ----------------------------------------------------------

    def _build_envelope(self, spec):
        """准备「标准化发送内容」—— 调用方只负责这一步，发送交给目标插件。

        字段结构见 README「标准化发送内容」，与「企业微信通知」插件的 `envelope` 输入一致；
        只放**本次真正需要**的键：没填的收件人之类一律不放，交回目标插件用它自己的配置。
        """
        envelope = {
            "version": ENVELOPE_VERSION,
            "msgtype": spec["msgtype"],
            "source": PLUGIN_NAME,
        }
        touser = str(self.p.get(spec["touser_key"]) or "").strip()
        if touser:
            envelope["touser"] = touser       # 填了才覆盖目标插件的收件人
        content = self._expand(self.p.get(spec["content_key"]))
        if content.strip():
            envelope["content"] = content
        return envelope

    def _build_params(self, spec):
        """兼容用：把标准化内容装进调用参数（只传内容，不传凭据）。"""
        envelope = self._build_envelope(spec)
        self.envelope = envelope
        return {
            "func": TARGET_FUNC_SEND,
            "envelope": json.dumps(envelope, ensure_ascii=False),
        }, str(envelope.get("touser") or ""), str(envelope.get("content") or "")

    def _build_card_extras(self, envelope):
        """卡片页的标题 / 链接 / 图片：同样走标准化内容。"""
        title = self._expand(self.p.get("card_title")).strip()
        url = str(self.p.get("card_url") or "").strip()
        image = str(self.p.get("card_image") or "").strip()
        if title:
            envelope["title"] = title
        if url:
            envelope["url"] = url
        if image:
            envelope["image"] = image
        return envelope

    def _send_envelope(self, spec, envelope):
        """统一下发入口：内容已备好，剩下的（凭据、发送、投递校验）全交给目标插件。"""
        self.envelope = envelope
        self.sent_params = {
            "func": TARGET_FUNC_SEND,
            "envelope": json.dumps(envelope, ensure_ascii=False),
        }
        return self._send(spec, self.sent_params, str(envelope.get("touser") or ""))

    def _send_text(self):
        spec = ACTION_SPEC["send_text"]
        envelope = self._build_envelope(spec)
        if not str(envelope.get("content") or "").strip():
            raise ValueError("「文本消息」的正文为空，请先在「文本消息」子页面填写内容再发送。")
        return self._send_envelope(spec, envelope)

    def _send_card(self):
        spec = ACTION_SPEC["send_card"]
        envelope = self._build_card_extras(self._build_envelope(spec))
        if not (envelope.get("content") or envelope.get("title") or envelope.get("image")):
            raise ValueError("「卡片消息」的标题、内容、图片至少要填一项。")
        return self._send_envelope(spec, envelope)

    # -- 汇总 --------------------------------------------------------------

    def _send(self, spec, params, touser):
        self._require_endpoint()
        problems, notes = self._preflight(params)
        if problems:
            self.log.error("参数预校验未通过，未发出任何请求：%s" % "；".join(problems))
            return self._result(
                ok=False, title="未发送：目标插件的调用前提不满足",
                alert="；".join(problems), tone="danger",
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("收件人", touser or "（沿用目标插件设置）"), ("结果", "✘ 未发送")],
                notes=notes,
            )

        try:
            job_id, submit_note, snippet = self._submit(params)
        except ValueError as exc:
            self.log.error(str(exc))
            return self._result(
                ok=False, title="未发送：调用目标插件失败", alert=str(exc), tone="danger",
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("收件人", touser or "（沿用目标插件设置）"), ("结果", "✘ 失败")],
                notes=notes,
            )

        self.job_id = job_id
        if not job_id or not self.wait_result:
            reason = ("响应里没有任务 ID，无法确认结果" if not job_id
                      else "已按设置跳过结果确认")
            self.log.info("不等待结果：%s" % reason)
            return self._result(
                ok=True, title="任务已提交", tone="default",
                alert="任务已提交（%s）。" % reason,
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("收件人", touser or "（沿用目标插件设置）"), ("结果", "已提交")],
                notes=notes, submit_snippet=snippet,
            )

        state, result = self._poll(job_id)
        if state == "pending":
            self.log.warn("未在等待时间内取到结果，任务可能仍在后台执行")
            return self._result(
                ok=True, title="任务已提交（未确认结果）", tone="default",
                alert="在等待时间内没有取到执行结果，任务可能仍在后台执行。"
                      "可稍后到「我的插件」里查看「%s」的运行记录。" % self.target_id,
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("收件人", touser or "（沿用目标插件设置）"), ("结果", "未确认")],
                notes=notes, job_id=job_id, submit_snippet=snippet,
            )

        if state == "failed":
            reason = str(result.get("error") or result.get("message") or "目标插件执行失败")
            self.log.error("目标插件执行失败：%s" % reason)
            return self._result(
                ok=False, title="发送失败", alert=reason, tone="danger",
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("收件人", touser or "（沿用目标插件设置）"), ("结果", "✘ 失败")],
                notes=notes, job_id=job_id, submit_snippet=snippet,
            )

        # 到这里：目标插件报告成功。但企业微信「收件人不在可见范围」时仍会返回成功，
        # 所以必须再看目标插件给出的投递结论，否则会把没收到的消息说成发送成功。
        recipient = str(result.get("recipient") or "").strip()
        delivery_ok = result.get("delivery_ok")
        delivery_status = str(result.get("delivery_status") or "").strip().lower()
        invalid = [str(u) for u in (result.get("invalid_users") or []) if u]
        delivery_note = str(result.get("delivery_note") or "").strip()
        if recipient:
            self.log.info("目标插件报告的实际收件人：%s" % recipient)
        if delivery_ok is False:
            reason = delivery_note or ("企业微信报告收件人无效：%s" % "、".join(invalid[:8]))
            self.log.warn("目标插件已受理，但投递校验未通过：%s" % reason)
            return self._result(
                ok=False, title="已受理，但消息没有投递出去", tone="warning",
                alert="目标插件（%s）报告请求已被企业微信受理，但**收件人收不到**：%s\n\n"
                      "常见原因是收件人不在该应用的「可见范围」内。"
                      "请到企业微信管理后台 → 该应用 →「可见范围」里加入收件人，"
                      "或把本子页面的「收件人」改成正确的 UserID 后重试。"
                      % (self.target_id, reason),
                stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                       ("实际收件人", recipient or "（未知）"), ("结果", "⚠ 未投递")],
                notes=notes, job_id=job_id, submit_snippet=snippet,
                extra_rows=[("投递校验", delivery_status or "-"),
                            ("无效收件人", "、".join(invalid[:8]) or "-"),
                            ("接收人", recipient or "-")],
            )

        self.log.info("发送成功%s" % ("（收件人：%s）" % recipient if recipient else ""))
        # 成功时也要给「显示成功但手机没响」的可能原因 —— 这正是最让人困惑的情况：
        # 企业微信确认收件人在可见范围内了，剩下的问题只可能出在微信插件侧。
        if delivery_status == "unknown":
            hint = ("目标插件所在环境查不到通讯录（自建转发地址常见），"
                    "因此**无法确认投递**，只知请求已被企业微信受理。"
                    "若手机上没收到，请按「企业微信通知」插件 README 第七节逐项检查。")
        else:
            hint = ("企业微信已确认收件人在应用可见范围内。**若手机上仍没收到**，问题在微信侧，"
                    "按顺序检查三处：\n"
                    "1. 管理后台 → 该应用 → 是否勾选了「**在微工作台中始终进入主页**」"
                    "（勾选后微信端只能收到文本消息，图文会被转成「到企业微信查看」的提示）；\n"
                    "2. 微信 → 通讯录 → 本企业 → 微信插件 → 右上角 → 设置 →"
                    "「**接收应用消息**」是否已打开；\n"
                    "3. 是否已关注本企业的「**微信插件**」（企业微信客户端能收到、微信收不到，"
                    "通常就是这三处之一）。")
        hint += ("\n\n**想核对这次是否真的发出去了**：看下面明细表里的 `msgid`（有值即企业微信已接收受理），"
                 "或到「我的插件 → %s」的最近运行记录里看它自己的日志"
                 "（会显示「执行功能：发送消息（供其他插件调用）」与「第 N/M 段发送成功，msgid=…」）。"
                 % self.target_id)
        return self._result(
            ok=True, title="发送成功", tone="success",
            alert="「%s」已发送给：%s%s"
                  % (spec["label"], recipient or touser or "（沿用目标插件设置）",
                     "。" + delivery_note if delivery_note else ""),
            stats=[("目标插件", self.target_id), ("动作", spec["label"]),
                   ("实际收件人", recipient or touser or "（沿用目标插件设置）"),
                   ("结果", "✔ 已发送")],
            notes=notes, job_id=job_id, submit_snippet=snippet,
            hint=hint, extra_rows=[("投递校验", delivery_status or "-"),
                                   ("接收人", recipient or "-"),
                                   ("内容来源", (str(result.get("envelope_source") or "")
                                                and "已确认由「%s」传入" % result.get("envelope_source"))
                                    or "-"),
                                   ("msgid", "、".join(str(m) for m in (result.get("msgids") or [])) or "-")],
        )

    # -- 结果装配 ----------------------------------------------------------

    def _stat_cards(self, stats):
        children = []
        for label, value in stats:
            children.append({"type": "card", "label": str(label),
                             "children": [{"type": "heading", "text": str(value)}]})
        if not children:
            return None
        return {"type": "grid", "columns": min(max(len(children), 1), 4), "children": children}

    def _result(self, ok, title, alert, tone, stats, notes=None, job_id="",
                submit_snippet="", hint="", extra_rows=None):
        components = [
            # 标题要真的渲染出来：它承载了「成功 / 未发送 / 已受理但未投递」这些关键结论
            {"type": "heading", "text": "🧪 %s · %s" % (PLUGIN_NAME, title)},
            {"type": "alert", "text": alert, "style": {"tone": tone}},
        ]
        cards = self._stat_cards(stats)
        if cards:
            components.append(cards)
        for note in (notes or []):
            components.append({"type": "alert", "text": note, "style": {"tone": "warning"}})
        if hint:
            components.append({"type": "text", "text": hint, "style": {"tone": "muted"}})
        components.append({"type": "divider"})

        rows = [
            ["目标插件", self.target_id],
            ["服务地址", self.base_url],
            ["消息类型", ACTION_SPEC[self.action]["msgtype"]],
            ["任务 ID", job_id or "-"],
            ["等待结果", "是" if self.wait_result else "否"],
        ]
        rows.extend([list(r) for r in (extra_rows or [])])
        if submit_snippet:
            rows.append(["提交响应", submit_snippet])
        components.append({"type": "table", "label": "本次调用详情",
                           "headers": ["项目", "值"], "rows": rows})

        if self.envelope:
            components.append({"type": "heading", "text": "① 本插件准备好的「标准化发送内容」"})
            components.append({"type": "code",
                               "text": json.dumps(self.envelope, ensure_ascii=False, indent=2)})
        if self.sent_params:
            components.append({"type": "heading", "text": "② 发给目标插件的调用参数"})
            components.append({"type": "code",
                               "text": json.dumps(self.sent_params, ensure_ascii=False, indent=2)})
        if self.target_inputs:
            components.append({
                "type": "text",
                "text": "预校验依据：目标插件 `%s` 的清单声明了 %d 个输入；"
                        "本次参数的键与下拉取值都已逐一核对。" % (self.target_id, len(self.target_inputs)),
                "style": {"tone": "muted"},
            })

        components.append({"type": "divider"})
        components.append({"type": "heading", "text": "运行日志"})
        components.append({"type": "code", "text": self.log.text()})
        return {
            "status": "ok" if ok else "failed",
            "action": self.action,
            "target_plugin": self.target_id,
            "msgtype": ACTION_SPEC[self.action]["msgtype"],
            "job_id": job_id or None,
            "sent_params": self.sent_params,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        if self.action not in VALID_ACTIONS:
            raise ValueError("不支持的操作：%s（可选：%s）"
                             % (self.action, " / ".join(VALID_ACTIONS)))
        self.log.info("%s 启动，本次操作：%s（消息类型 %s）"
                      % (PLUGIN_NAME, ACTIONS[self.action],
                         ACTION_SPEC[self.action]["msgtype"]))
        self.log.info("目标插件：%s｜地址：%s｜令牌：%s"
                      % (self.target_id, self.base_url,
                         "已配置（长度 %d）" % len(self.token) if self.token
                         else "未配置（将尝试环境变量 TGTO_OPENAPI_TOKEN）"))
        handlers = {
            "send_text": self._send_text,
            "send_card": self._send_card,
        }
        return handlers[self.action]()


def run(params, context):
    """TgtoDrive 插件入口：同步执行一次演示调用。"""
    return _DemoRunner(params, context).execute()
