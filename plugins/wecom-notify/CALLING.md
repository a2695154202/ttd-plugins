# 如何在其他插件中调用「企业微信通知」

本文件说明**怎样才能让别的 TgtoDrive 插件把消息发到企业微信** —— 不必重复实现企业微信接口，
把内容交给 `wecom-notify` 发送即可。

- 插件 id：`wecom-notify`
- 调用入口：`POST /api/toolbox/plugins/wecom-notify/run`
- 结果查询：`GET /api/toolbox/plugins/jobs/{job_id}`
- 本文档在线地址：<https://github.com/a2695154202/ttd-plugins/blob/main/plugins/wecom-notify/CALLING.md>

> 在插件界面点右上角「查看调用方法」可以直接看到本文件的链接与参数速查表。

---

## 一、调用前的前提

1. TgtoDrive 已安装并**启用** `wecom-notify`；
2. 该插件中已经填好「企业 ID / 应用 AgentId / 应用 Secret」（以及必要时的「代理地址」），
   并且在插件里点过「发送测试消息」能成功收到消息 —— 其余插件复用的就是这份已保存的配置；
3. 调用方持有 TgtoDrive 的 **OpenAPI 令牌**，通常来自环境变量：

   | 环境变量 | 说明 |
   | --- | --- |
   | `TGTO_OPENAPI_BASE_URL` | TgtoDrive 地址，同容器常见 `http://127.0.0.1:12366` |
   | `TGTO_OPENAPI_TOKEN` | 以 `Bearer` 方式放进请求头 |

   令牌**不要**写进插件包、日志或返回值。

---

## 二、最小可用调用

`params` 里只需放本次真正变化的字段；未传的字段沿用插件里已保存的设置。

```python
import os
import requests


def notify_via_wecom(content, title="TgtoDrive 通知"):
    """把一条文本通知发到企业微信。返回 (ok, 说明)。"""
    base = os.environ.get("TGTO_OPENAPI_BASE_URL", "http://127.0.0.1:12366").rstrip("/")
    token = os.environ.get("TGTO_OPENAPI_TOKEN", "")
    if not token:
        return False, "未配置 TGTO_OPENAPI_TOKEN"

    response = requests.post(
        base + "/api/toolbox/plugins/wecom-notify/run",
        headers={"Authorization": "Bearer " + token},
        json={"params": {
            "func": "send",
            "msgtype": "markdown",
            "touser": "@all",
            "title": title,
            "content": content,
        }},
        timeout=(5, 30),
        allow_redirects=False,
    )
    if response.status_code not in (200, 201, 202):
        return False, "提交失败：HTTP %s %s" % (response.status_code, response.text[:200])

    payload = response.json()
    return True, payload
```

> 只要你不需要「发完再确认结果」，到这里就够用了：任务提交成功即返回。

---

## 三、请求参数（完整）

`POST /api/toolbox/plugins/{plugin_id}/run` 的请求体：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `params` | 是 | 对象；键名必须与插件 `inputs` 一致，**未知参数会被拒绝** |
| `save_settings` | 否 | 默认不保存。**调用方请勿传 `true`**，否则会把本次调用参数写进用户的插件设置 |

`params` 支持的全部键（与本插件表单一致）：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `func` | string | `send` 发送 / `test` 测试 / `config` 自检 / `users` 查成员 / `history` 查历史 / `docs` 查看调用方法。`test` 会按 `content` 与 `card_content` 依次发送（都有内容时中间间隔 3 秒） |
| `msgtype` | string | `text` / `markdown` / `textcard` / `template_card`（卡片通知） |
| `touser` | string | 成员 UserID，多个用 `\|` 分隔；`@all` 表示该应用全体可见成员 |
| `toparty` / `totag` | string | 部门 ID / 标签 ID，`touser` 为 `@all` 时被忽略 |
| `content` | string | 正文；`text`/`markdown` 上限 2048 字节，超出按 `split_long` 分段 |
| `safe` | bool | 仅 `text` / `markdown` 支持，`true` 时不可分享并带水印 |
| `title` | string | 卡片标题（`textcard`、`template_card`） |
| `url` | string | 卡片跳转链接（`textcard` 必填；`template_card` 的 `card_action` 必填，留空会回退官方站点） |
| `card_type` | string | `text_notice`（默认）/ `news_notice` |
| `card_image` | string | 卡片主图：http(s) 链接，**或容器内已存在的本地图片路径**（插件会先上传换取 URL） |
| `card_source` | string | 卡片来源名称，例如「站点 1PTBA 消息」 |
| `card_source_icon` | string | 来源图标 URL |
| `card_sub_title` | string | 卡片副标题（≤30 字） |
| `card_content` | string | 卡片消息内容。**优先识别企业微信原生 JSON**：含 `template_card` 或 `card_type` 时原样放进请求体（不解析、不截断）；否则按每行一条 `键=值`（最多 6 条）生成键值列表，整段不是键值格式时作为卡片正文（≤112 字）。兼容旧字段名 `card_items` |
| `card_aspect_ratio` | number | 图片比例 1.3–2.25，默认 2.25 |
| `split_long` | bool | 超长正文是否自动分段，默认 `true` |
| `channel_name` / `corp_id` / `agent_id` / `corp_secret` / `api_base` / `token` / `encoding_aes_key` / `admin_users` / `history_days` / `tgto_base_url` / `tgto_token` | — | 配置类字段，**一般不必传**，沿用用户已保存的设置 |

### 卡片键值列表的书写格式

```
时间=2026-10-13 18:04:48
季集=S01E15 第 15 集
分类=日番
评分=8.5/10
```

- 每行一条，`=`、`:`、`：`、`|` 都可以分隔键与值；
- **最多 6 条**，超出会被丢弃并在运行日志中说明；
- 企业微信限制键 ≤5 字、值 ≤30 字，插件会主动截断并记日志（否则企业微信也会自行截断，且用户看不到提示）。

---

## 四、返回值

提交成功后响应的典型结构（字段名以实际响应为准）：

```json
{
  "job_id": "…",
  "status": "queued"
}
```

任务结果通过 `GET /api/toolbox/plugins/jobs/{job_id}` 查询，本插件返回的 `result` 形如：

```json
{
  "status": "ok",
  "func": "send",
  "msgtype": "template_card",
  "sent": 1,
  "total": 1,
  "msgids": ["MSGID…"],
  "error": "",
  "ui": { "width": "wide", "layout": "stack", "components": [ "…" ] }
}
```

| 字段 | 说明 |
| --- | --- |
| `status` | `ok` 表示全部成功；`failed` 表示失败（原因见 `error`） |
| `sent` / `total` | 成功段数 / 总段数（长文本分段时 `total > 1`） |
| `msgids` | 企业微信返回的消息 ID，便于排查 |
| `error` | 失败原因（中文，含 `errcode` 与处理建议） |
| `ui` | 结果界面组件，调用方可忽略 |

---

## 五、需要等待结果的写法

```python
import time

def notify_and_wait(content, timeout=60):
    ok, payload = notify_via_wecom(content)
    if not ok:
        return False, payload
    job_id = payload.get("job_id") or payload.get("id")
    if not job_id:
        return True, "已提交（未取到 job_id，视为异步执行）"

    base = os.environ["TGTO_OPENAPI_BASE_URL"].rstrip("/")
    headers = {"Authorization": "Bearer " + os.environ["TGTO_OPENAPI_TOKEN"]}
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(base + "/api/toolbox/plugins/jobs/" + job_id,
                            headers=headers, timeout=(5, 30))
        data = resp.json()
        result = data.get("result") or {}
        if result.get("status") in ("ok", "failed"):
            return result["status"] == "ok", result.get("error") or "发送成功"
        time.sleep(2)
    return False, "等待结果超时"
```

> 轮询接口的响应字段在不同版本可能略有差异，建议用 `.get()` 取值并做兜底，
> 不要假定固定的 `status` 字面量。

---

## 六、常见场景

### 1. 纯文本通知

```python
{"func": "send", "msgtype": "text", "touser": "@all", "content": "任务已完成"}
```

### 2. markdown 通知（排版更好）

```python
{"func": "send", "msgtype": "markdown", "touser": "@all",
 "content": "## 下载完成\n> 影片：**示例影片**\n> 时间：2026-10-13 18:04"}
```

### 3. 带图卡片通知（对应 text_notice 样式）

```python
{
  "func": "send",
  "msgtype": "template_card",
  "touser": "@all",
  "title": "新入库剧集：遭到流放的转生重骑士",
  "card_source": "站点 1PTBA 消息",
  "card_image": "https://example.com/cover.jpg",
  "card_content": "时间=2026-10-13 18:04:48\n季集=S01E15 第 15 集\n分类=日番\n评分=8.5/10",
  "url": "https://example.com/detail",
}
```

### 4. 用容器内的本地图片当卡片图

```python
{"func": "send", "msgtype": "template_card", "title": "本地封面",
 "card_image": "/media/posters/example.jpg",
 "url": "https://example.com/detail"}
```

插件会先把图片上传到企业微信（`/cgi-bin/media/uploadimg`）换取图片 URL 再发卡片。

**内网地址也是可以的**：因为企业微信服务器访问不到 `192.168.x.x` / `10.x.x.x` / `127.0.0.1`
这类地址，插件检测到内网图片链接时会先自行下载，再上传换取企业微信可访问的 URL：

```python
{"func": "send", "msgtype": "template_card", "title": "带图卡片",
 "card_image": "http://192.168.101.100:12366/static/brand_logo.png",
 "url": "https://example.com/detail"}
```

上传失败时会退回使用原地址并给出警告（此时卡片上的图片可能显示不出来）。

### 5. 内容驱动的一键测试

```python
{"func": "test",
 "content": "文本测试内容",
 "card_content": "状态=测试成功\n类型=卡片通知"}
```

`test` 会检查 `content` 与 `card_content` 两个内容框：

- 两个都有内容 → 先发文本消息，**间隔 3 秒**再发卡片消息（共两条通知）；
- 只有一个有内容 → 只发这一条；
- 两个都为空 → 报错 `「文本消息内容」与「卡片消息内容」都为空`。

单条测试：

```python
{"func": "test", "content": "只测文本"}
```

---

## 七、错误处理

调用失败时 `result["error"]` 已经是中文可读文案，例如：

| 场景 | 提示要点 |
| --- | --- |
| `60020` | 调用 IP 不在「企业可信IP」名单，文案里会带上实际出口 IP 与两种处理方式 |
| `40001` / `40013` | Secret / 企业 ID 不正确 |
| `42001` / `40014` | access_token 过期（插件会自动清缓存重取并重试一次） |
| `60011` / `82001` | 收件人不在应用可见范围内 |
| `45009` | 触发频率限制（每应用每天有人次上限；单成员每分钟 ≤30 条） |

调用方建议：**把 `error` 原文记进自己的日志**，不要吞掉；同时捕获网络异常并设置超时。

---

## 八、注意事项

- **不要传 `save_settings: true`**：会把调用参数写进用户在该插件里的设置。
- 本插件与所有插件共用一套任务队列：同一插件同时只能有一个未完成任务，队列满时提交会失败，请做重试或降级处理。
- 插件 `timeout` 为 120 秒；被调用时同样受此限制，长文本分段发送也在这一时限内完成。
- 插件返回的 `result` 会被包装后返回，整体 **≤1 MiB**；不要指望从中读到大段日志。
- 高频调用请自行节流：企业微信侧对同一成员有 30 次/分钟、1000 次/小时的限制。
- 本插件的凭据（Secret 等）**不对外提供读取接口**，`GET /api/toolbox/plugins/wecom-notify/settings`
  可能返回用户保存的配置，调用方**不应**依赖它，更不要把它写进日志。

---

## 九、相关文件

| 文件 | 说明 |
| --- | --- |
| [`plugin.json`](plugin.json) | 插件清单：inputs 定义与界面结构，调用参数的权威来源 |
| [`plugin.py`](plugin.py) | 插件实现；`_NotifyRunner.build_payload` 是参数到企业微信接口的映射 |
| [`README.md`](README.md) | 面向使用者的配置与排错说明 |
