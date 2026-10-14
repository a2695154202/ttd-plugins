# 如何在其他插件中调用「企业微信通知」

本文件说明**怎样才能让别的 TgtoDrive 插件把消息发到企业微信** —— 不必重复实现企业微信接口，
把内容交给 `wecom-notify` 发送即可。

- 插件 id：`wecom-notify`
- 调用入口：`POST /api/toolbox/plugins/wecom-notify/run`
- 结果查询：`GET /api/toolbox/plugins/jobs/{job_id}`
- 本文档在线地址：<https://github.com/a2695154202/ttd-plugins/blob/main/plugins/wecom-notify/CALLING.md>

> **「由其他插件传入参数触发运行」是受支持的调用方式**：该运行接口的用途就是
> 「按插件 `inputs` 提交参数 → 启动独立进程执行插件」，在 OpenAPI 里以 `bearerAuth` 暴露，
> 且明确「Bearer 调用无需浏览器的 X-Toolbox-Request 请求头」。唯一相关的禁令是
> 「避免递归调用**自身**运行接口」—— 调用**别的**插件没有问题。
> 判断是否被接受，看首个响应：**HTTP 202 + `job_id` ＝ 已被接受并在执行**；
> 404 未安装、400 参数被拒、401/403 令牌问题、503 队列忙。

> 在插件界面点右上角「查看调用方法」可以直接看到本文件的链接与参数速查表。

---

## 一、调用前的前提

1. TgtoDrive 已安装并**启用** `wecom-notify`；
2. 该插件中已经填好「企业 ID / 应用 AgentId / 应用 Secret」（以及必要时的「代理地址」），
   并且在插件里点过「发送测试消息」能成功收到消息；
3. 调用方持有 TgtoDrive 的 **OpenAPI 令牌**，通常来自环境变量：

   | 环境变量 | 说明 |
   | --- | --- |
   | `TGTO_OPENAPI_BASE_URL` | TgtoDrive 地址，同容器常见 `http://127.0.0.1:12366` |
   | `TGTO_OPENAPI_TOKEN` | 以 `Bearer` 方式放进请求头 |

   令牌**不要**写进插件包、日志或返回值。

### 凭据与收件人由本插件自己补齐（调用方不必传）

TgtoDrive 的运行接口只把 `params` **原样**交给插件，**不会**把用户在本插件表单里保存的
设置合并进来。因此本插件在执行前会先从**自己已保存的设置**里补齐调用方没传的字段：

```text
优先级：调用方在 params 里显式传的值  >  本插件已保存的设置（settings.json）  >  内置默认值
```

它有这些含义：

- **调用方只需传内容**：`func` / `msgtype` / `content`（或 `card_content`）就够，
  `corp_id` / `agent_id` / `corp_secret` / `api_base` / `proxy_mode` / `touser` 等
  都从用户已保存的设置里取 —— 调用方既不需要、也不应该持有这些凭据；
- **`func` 不参与补齐**：表单里通常存的是 `test`，若沿用它会让外部调用变成「发一条测试消息」，
  因此 `func` 始终以调用方传入的为准（不传则默认 `send`）；
- 运行日志会打印一行 `已从本插件已保存的设置（settings.json）补齐 N 项未传参数：…`，
  便于确认实际用了哪些值；
- 若用户**从未保存过**凭据、调用方也没传，插件会明确报错
  `缺少必填配置：企业 ID、应用 AgentId、应用 Secret` —— 不会静默发出空凭据。

> 这也是「任务显示已提交、但微信里收不到」的常见原因：调用方只传了正文，凭据却是空的。
> 本插件会自动补齐，但**前提是用户已在插件表单里填好并保存过凭据**。

> **坑：平台会把清单默认值填齐，别被「传了值」的假象骗了**
>
> TgtoDrive 的运行接口并**不是**只把调用方传的键交给插件 —— 它会按插件清单把所有
> `inputs` 都用**默认值**填齐（实测：调用方只传 `func` + `envelope`，插件却收到 25 个键）。
> 于是「值为空」不再等于「调用方没传」：
>
> - `corp_id` / `corp_secret` 这类**默认值为空**的字段，旧逻辑能正确顶上；
> - `api_base`（默认 `https://qyapi.weixin.qq.com`）、`touser`（默认 `@all`）、
>   `card_image`（默认品牌图）这类**默认值非空**的字段，会被默认值永久顶掉 ——
>   表现为「用户在表单里配了转发代理地址，被调用时却从服务器真实 IP 直连报 `60020`」。
>
> 因此本插件把「**值等于该输入在清单里的默认值**」同样判定为调用方没有显式传，
> 让已保存的设置顶掉它（`func` 与 `msgtype` 例外：调用方对这两个字段有明确意图）。
> 调用方若确实想显式指定 `touser` / `api_base`，传一个**与默认值不同**的值即可。

---

## 二、⚠️ 两条硬约束（调用失败几乎都是踩了这两条）

TgtoDrive 在处理 `POST /api/toolbox/plugins/{id}/run` 时，会**按目标插件的 `inputs` 清单校验参数**：

1. **键必须在清单里** —— `params` 中出现的每个键，都必须是 `wecom-notify` 的 `inputs` 里
   已声明的字段，否则请求会被判为「未知参数」直接拒绝（HTTP 400）。
2. **`select` 字段的取值必须在该字段的 `options` 里** —— 例如 `func` 只能是
   `send` / `test` / `config` / `history` / `docs`；`msgtype` 只能是 `text` / `news`。
   取值不在选项内同样会被拒绝。

> 因此：**不要传本文件没列出的参数**，也不要传**已移除**的取值 ——
> `markdown`（已移除）、`textcard`（已移除）、`template_card`（已移除）。
> 修改本插件清单（增删输入）时，必须同步更新所有调用方，
> 否则调用会静默变成 400。

---

## 三、标准化发送内容（envelope）—— 推荐用法

调用方**只需准备一份标准化的内容**，发送逻辑全部由本插件负责：把它交给本插件的 `envelope` 输入，
本插件按它发送，**不使用本插件的预设内容**。这样调用方不必了解企业微信的请求体结构，
也不会随着消息类型的变化而反复改代码。

```json
{
  "version": 1,
  "msgtype": "text",
  "touser": "zhangsan|lisi",
  "content": "正文或描述",
  "items": [["状态", "✅ 成功"], {"key": "剩余药丸", "value": 12}],
  "title": "图文标题",
  "url": "https://example.com/detail",
  "image": "https://example.com/cover.jpg",
  "source": "调用方插件名"
}
```

### 字段结构

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `version` | 否 | 契约版本，目前固定 `1`（缺省按 1 处理；填其它值会被明确拒绝） |
| `msgtype` | 否 | `text` / `news`；覆盖本插件的「消息类型」设置 |
| `touser` | 否 | 收件人 UserID（多个用 `\|` 分隔）或 `@all`；**覆盖**本插件已保存的收件人 |
| `content` | 否 | `text` 的正文 / `news` 的描述 |
| `items` | 否 | 结构化键值，渲染成「键：值」多行并**追加在 `content` 之后**。支持 `[["键","值"]]`、`[{"key":…,"value":…}]`、`{"键":"值"}` 三种写法 |
| `title` | 否 | `news` 的标题 |
| `url` | 否 | `news` 的点击跳转链接 |
| `image` | 否 | `news` 的主图（http(s) / 内网地址 / 容器内本地路径均可） |
| `source` | 否 | 调用方名称，只写进运行日志与返回值，便于追溯「这条是谁发的」 |

> **只认已声明的字段**：出现未知字段会**报错并列出允许的字段**，不会被静默忽略 ——
> 否则调用方写错字段名时会得到「发出去了但内容不对」这种最难排查的故障。
> 新增字段属于向后兼容的扩展，届时只改本插件的清单与本文档，调用方无需改动。

### 参数传递方式

把上面的对象序列化成字符串，放进 `params.envelope`：

```json
{"params": {"func": "send", "envelope": "{\"version\":1,\"content\":\"要发送的正文\",\"source\":\"我的插件\"}"}}
```

即：**调用参数只有 `func` 与 `envelope` 两个键**，不必再逐个传 `msgtype` / `touser` / `title` 等
（那些字段仍然保留，见第六节，用于兼容与简单场景）。

### 调用方内容如何覆盖本插件的默认内容

优先级从高到低：

```text
envelope 里的字段  >  其它传入参数（msgtype / touser / content / title / url / card_image）
                   >  本插件已保存的设置（表单里填的那份）
                   >  本插件的内置默认值
```

- **envelope 优先**：它是调用方最明确的一次表达，给了就覆盖其它来源；
- **没给的不覆盖**：例如 envelope 里没有 `touser`，就沿用本插件已保存的收件人
  （也就是用户在插件里点「发送测试消息」能收到的那份配置）；
- **显式给空值表示清空**：例如 `"content": ""` 会清空正文，而不是回退到旧内容；
- `func=test` 用的是**本插件内置的测试内容**，与 envelope 无关；`func=send` 只用调用方的内容。

### 配置加载的触发时机

| 时机 | 由谁加载 | 加载什么 |
| --- | --- | --- |
| **本插件每次 `run()` 开始时**（也就是平台为本次调用新起的那个进程里） | **本插件自己** | `context["data_dir"]` 定位到的 `settings.json`（企业 ID / AgentId / Secret / 代理地址 / 收件人等），随后按需兜底读项目设置 |
| 调用方进程内 | 不加载 | 调用方**不需要、也不应该**持有这些凭据；它只准备内容 |
| 修改凭据后 | 需重新保存 | 设置以文件为准，下次 `run()` 时生效；界面改完点保存即可 |

**关键点**：只有在**本插件自己的进程**里，才能拿到**本插件自己的 `data_dir`** —— 这是它读到自己配置的唯一途径。
这也决定了「被其他插件调用」必须走运行接口，而不是导入代码（见第十二节）。

---

## 四、最小可用调用

`params` 里只需放本次真正需要的字段；未传的字段沿用插件里已保存的设置。

```python
import os
import requests


def notify_via_wecom(content, title="TgtoDrive 通知", msgtype="text"):
    """发一条企业微信通知。返回 (ok, 说明)。"""
    base = os.environ.get("TGTO_OPENAPI_BASE_URL", "http://127.0.0.1:12366").rstrip("/")
    token = os.environ.get("TGTO_OPENAPI_TOKEN", "")
    if not token:
        return False, "未配置 TGTO_OPENAPI_TOKEN"

    response = requests.post(
        base + "/api/toolbox/plugins/wecom-notify/run",
        headers={"Authorization": "Bearer " + token},
        json={"params": {
            "func": "send",
            "msgtype": msgtype,          # "text" 或 "news"
            "touser": "@all",
            "title": title,              # news 使用
            "content": content,          # text 的正文 / news 的描述
        }},
        timeout=(5, 30),
        allow_redirects=False,
    )
    if response.status_code not in (200, 201, 202):
        return False, "提交失败：HTTP %s %s" % (response.status_code, response.text[:200])

    return True, response.json()
```

> 只要你不需要「发完再确认结果」，到这里就够用了：任务提交成功即返回。

---

## 五、消息类型只有两种

本插件**只发送两种类型**，它们都是**微信插件能收到**的类型：

| 值 | 名称 | 形态 | 说明 |
| --- | --- | --- | --- |
| `text` | 文本消息 | 纯文本 | 正文上限 2048 字节（约 680 汉字），超出按 `split_long` 分段 |
| `news` | 图文消息 | 大图 + 标题 + 描述 + 点击跳转 | 微信里最接近「卡片」的形态；`title` / `url` / `card_image` 都对它生效 |

**已移除的类型**（不要再用）：`markdown`（微工作台不支持展示）、
`textcard`（功能被 `news` 覆盖）、`template_card`（微信插件官方明确收不到）。

> 兼容处理：如果你的内容本来就是**模板卡片 JSON**，把它放进 `card_content` 并指定
> `msgtype="news"`，插件会**自动转换成图文消息**（提取标题 / 描述 / 键值 / 链接 / 图片），
> 不需要重写内容。

---

## 六、请求参数（完整）

`POST /api/toolbox/plugins/{plugin_id}/run` 的请求体：

| 字段 | 必填 | 说明 |
| --- | --- | --- |
| `params` | 是 | 对象；键名必须与插件 `inputs` 一致，**未知参数会被拒绝** |
| `save_settings` | 否 | 默认不保存。**调用方请勿传 `true`**，否则会把本次调用参数写进用户的插件设置 |

`params` 支持的全部键（与本插件清单一致）：

| 参数 | 类型 | 说明 |
| --- | --- | --- |
| `func` | select | `send` **正式发送（调用方用这个）** / `test` 测试（内容可省略）/ `config` 自检 / `history` 查历史 / `docs` 查看调用方法。<br>注：`send` 已声明在清单的 `options` 里 —— TgtoDrive 会校验选项取值，不声明就无法被调用 |
| `msgtype` | select | `text` / `news`，**只有这两种** |
| `envelope` | textarea | **标准化发送内容（推荐）**：JSON 字符串，见第三节。给了它就用它，**覆盖**其它内容类参数 —— 调用方只需传 `func` + `envelope` 两个键 |
| `touser` | text | 成员 UserID，多个用 `\|` 分隔；`@all` 表示该应用全体可见成员 |
| `toparty` / `totag` | text | 部门 ID / 标签 ID，`touser` 为 `@all` 时被忽略 |
| `content` | textarea | `text` 的正文，也是 `news` 的描述。**`msgtype=text` + `func=send` 时必传**；`msgtype=news` 时可省略（描述改由 `card_content` 提供）；`func=test` 时可省略（用内置测试文本）。<br>注：正文按 2048 字节分段，中文约 680 字。 |
| `card_content` | textarea | `news` 描述的备用来源（`content` 为空时使用）。三种写法：① 每行一条「键=值」（`=`、`:`、`：`、`\|` 分隔）；② 企业微信原生 JSON（含 `news` / `articles` 直接使用，含 `card_type` 自动转图文）；③ 省略。兼容旧字段名 `card_items` |
| `title` | text | `news` 的标题。企业微信侧上限 128 字节，**插件按 60 字符保守截断**并在日志说明；留空时取「渠道名称 + 通知」 |
| `url` | text | `news` 的点击跳转链接；留空时回退官方站点（企业微信要求 `url` 与小程序二选一） |
| `card_image` | text | `news` 的主图：http(s) 链接，**或容器内已存在的本地图片路径 / 内网地址**（后两者会先下载再上传换取企业微信可用 URL） |
| `split_long` | boolean | 超长正文是否自动分段，默认 `true` |
| `channel_name` / `corp_id` / `agent_id` / `corp_secret` / `api_base` / `proxy_mode` / `token` / `encoding_aes_key` / `admin_users` / `history_days` / `tgto_base_url` / `tgto_token` | — | 配置类字段，**一般不必传**，沿用用户已保存的设置 |

### 描述内容的书写格式

`content` 或 `card_content` 里用「键=值」时：

```
时间=2026-10-13 18:04:48
季集=S01E15 第 15 集
分类=日番
评分=8.5/10
```

- 每行一条，`=`、`:`、`：`、`|` 都可以分隔键与值；
- 图文消息的描述由企业微信按 512 字节截断，插件会提前截断并在运行日志中说明。

---

## 七、返回值

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
  "msgtype": "news",
  "sent": 1,
  "total": 1,
  "msgids": ["MSGID…"],
  "error": "",
  "recipient": "成员 zhangsan",
  "delivery_ok": true,
  "delivery_status": "ok",
  "delivery_note": "收件人均在可见范围内（可见成员共 3 人）",
  "invalid_users": [],
  "ui": { "width": "wide", "layout": "stack", "components": [ "…" ] }
}
```

| 字段 | 说明 |
| --- | --- |
| `status` | `ok` 表示**请求被企业微信受理**；`failed` 表示发送失败（原因见 `error`） |
| `sent` / `total` | 成功段数 / 总段数（长文本分段时 `total > 1`） |
| `msgids` | 企业微信返回的消息 ID，便于排查 |
| `error` | 失败原因（中文，含 `errcode` 与处理建议） |
| `recipient` | **实际收件人**的可读描述（没填收件人时会写「全体可见成员（@all）」等回退结果） |
| `delivery_ok` | **投递是否可信**。见下方「必须检查 delivery_ok」 |
| `delivery_status` | `ok` 收件人都在可见范围 / `empty` 可见范围为空 / `missing` 有收件人不在范围 / `unknown` 查不到通讯录（自建转发地址常见），无法判定 |
| `delivery_note` | 上述校验的可读结论 |
| `invalid_users` | 企业微信在返回里点名的无效收件人（`invaliduser`） |
| `ui` | 结果界面组件，调用方可忽略 |

### ⚠️ 必须检查 `delivery_ok`，不能只看 `status`

企业微信有个必须知道的坑：**收件人不在应用可见范围时，它仍然返回 `errcode=0` 与 msgid，
但消息不会投递**。只按 `status == "ok"` 判断，就会出现「接口说成功、用户什么都没收到」。

因此请这样判断：

```python
if result.get("status") == "ok" and result.get("delivery_ok") is not False:
    ok = True                     # 真的送到了
else:
    reason = result.get("delivery_note") or result.get("invalid_users") or result.get("error")
```

- `delivery_ok` 为 `false` → **不要报告成功**，把 `delivery_note` / `invalid_users` 原文展示给用户，
  并提示他们到管理后台该应用的「可见范围」里加入收件人；
- `delivery_status == "unknown"` 时 `delivery_ok` 为 `true` —— 这表示查不到通讯录（自建转发地址
  通常不代理 `user/list`），**不是**投递失败，不要误报。

### 自测：一条命令确认「企业微信到底收没收到」

在容器里执行（把 `touser` 换成你自己的 UserID，`TOKEN` 换成 OpenAPI 令牌）：

```bash
TOKEN=<你的OpenAPI令牌>
BASE=http://127.0.0.1:12366

# 1) 提交一条发送任务
JOB=$(curl -sS -X POST "$BASE/api/toolbox/plugins/wecom-notify/run" \
  -H "Authorization: Bearer $TOKEN" -H 'Content-Type: application/json' \
  -d '{"params":{"func":"send","msgtype":"text","touser":"<你的UserID>","content":"投递自测"}}' \
  | sed -n 's/.*"job_id"[: ]*"\([^"]*\)".*/\1/p')

# 2) 读结果：重点看 delivery_ok / delivery_status / invalid_users / recipient
sleep 3
curl -sS "$BASE/api/toolbox/plugins/jobs/$JOB" \
  -H "Authorization: Bearer $TOKEN" | python3 -c "
import json,sys
d=json.load(sys.stdin); r=d.get('result') or d
for k in ('status','recipient','delivery_ok','delivery_status','delivery_note','invalid_users','msgids','error'):
    print('%-16s %s' % (k, r.get(k)))
"
```

对照结果：

| 看到什么 | 结论与处理 |
| --- | --- |
| `delivery_ok=True` 且 `delivery_status=ok` | 收件人确实在可见范围内，**消息应已送达**。若手机仍没有，问题在微信侧：见 `README.md`「仍收不到时逐项检查」（尤其「在微工作台中始终进入主页」是否被勾选） |
| `delivery_ok=False` + `invalid_users=[...]` | 收件人**不在应用可见范围** → 到管理后台该应用的「可见范围」里加入他们 |
| `delivery_status=empty` | 该应用的可见范围是空的，`@all` 无人可投 → 先加人 |
| `delivery_status=unknown` | 查不到通讯录（自建转发地址常见），**无法判定**；以企业微信返回的 `invaliduser` 为准 |
| `status=failed` | 请求本身失败，看 `error` 原文（如 `40013` 企业 ID 不对、`60020` IP 不在可信名单） |

> 这一步能区分「插件没发出去」与「企业微信收下了但没投递」——
> 后者只看 `status` 是发现不了的。

---

## 八、需要等待结果的写法

> ⚠️ 注意这里**必须同时检查 `delivery_ok`** —— 只判断 `status` 就会把
> 「请求被受理但没人收到」当成成功，这正是本插件存在 `delivery_ok` 的原因。

```python
import time


def notify_and_wait(content, timeout=60):
    """返回 ``(ok, 说明)``。ok 为 True 才表示消息**真的送到了**。"""
    ok, payload = notify_via_wecom(content)
    if not ok:
        return False, payload
    job_id = payload.get("job_id") or payload.get("id")
    if not job_id:
        return True, "已提交（未取到 job_id，视为异步执行，无法确认投递）"

    base = os.environ["TGTO_OPENAPI_BASE_URL"].rstrip("/")
    headers = {"Authorization": "Bearer " + os.environ["TGTO_OPENAPI_TOKEN"]}
    deadline = time.time() + timeout
    while time.time() < deadline:
        resp = requests.get(base + "/api/toolbox/plugins/jobs/" + job_id,
                            headers=headers, timeout=(5, 30))
        data = resp.json()
        result = data.get("result") or {}
        status = result.get("status") or result.get("state")
        if status in ("ok", "success", "failed", "error", "timeout"):
            if status not in ("ok", "success"):
                return False, result.get("error") or "发送失败"
            # 这一步不能省：企业微信在收件人不在可见范围时仍返回 errcode=0
            if result.get("delivery_ok") is False:
                return False, (result.get("delivery_note")
                               or "收件人可能不在应用可见范围内")
            return True, "发送成功（收件人：%s）" % (result.get("recipient") or "未知")
        time.sleep(2)
    return False, "等待结果超时"
```

> 轮询接口的响应字段在不同版本可能略有差异，建议用 `.get()` 取值并做兜底，
> 不要假定固定的 `status` 字面量。

---

## 九、常见场景

### 1. 纯文本通知（最常用）

```python
{"func": "send", "msgtype": "text", "touser": "@all", "content": "任务已完成"}
```

### 2. 图文消息通知（带图，微信里最接近卡片）

```json
{
  "func": "send",
  "msgtype": "news",
  "touser": "CaiShenYeDeXinTouBao",
  "title": "订单服务可用率告警",
  "content": "2026-10-13 23:05 触发\n当前可用率：92.4%",
  "url": "https://grafana.example.com/d/order",
  "card_image": "https://example.com/cover.jpg"
}
```

### 3. 图文消息 + 键值列表描述

```json
{
  "func": "send",
  "msgtype": "news",
  "touser": "@all",
  "title": "新入库剧集：遭到流放的转生重骑士",
  "card_content": "时间=2026-10-13 18:04:48\n季集=S01E15 第 15 集\n分类=日番\n评分=8.5/10",
  "card_image": "https://example.com/cover.jpg",
  "url": "https://example.com/detail"
}
```

### 4. 把已有的模板卡片 JSON 直接发出去（自动转图文）

```json
{
  "func": "send",
  "msgtype": "news",
  "card_content": "{\"card_type\": \"text_notice\", \"main_title\": {\"title\": \"告警\"}, \"card_action\": {\"type\": 1, \"url\": \"https://example.com\"}}"
}
```

### 5. 用容器内的本地图片 / 内网图片当主图

```python
{"func": "send", "msgtype": "news", "title": "本地封面",
 "card_image": "/media/posters/example.jpg",
 "url": "https://example.com/detail"}
```

```python
{"func": "send", "msgtype": "news", "title": "内网图片",
 "card_image": "http://192.168.101.100:12366/static/brand_logo.png",
 "url": "https://example.com/detail"}
```

内网地址（`192.168.x.x` / `10.x.x.x` / `127.0.0.1`）企业微信服务器访问不到，
插件检测到后会先自行下载，再上传（`/cgi-bin/media/uploadimg`）换取可访问的 URL。
上传失败时会退回使用原地址并给出警告（此时卡片上的图片可能显示不出来）。

### 6. 一键测试（内容可省略）

```python
{"func": "test"}
```

`test` 固定发送**两条**通知：先发内置文本消息，**间隔 3 秒**再发内置图文消息。
需要自定义内容时传 `content` / `card_content` 覆盖对应的内置内容：

```python
{"func": "test", "content": "自定义文本", "card_content": "状态=自定义\n类型=图文"}
```

---

## 十、错误处理

调用失败时 `result["error"]` 已经是中文可读文案，例如：

| 场景 | 提示要点 |
| --- | --- |
| **HTTP 202 + `job_id`** | **触发已被接受、插件已开始执行** —— 这是正常的成功响应形状；后续成败用任务查询接口读取。若你怀疑「插件不支持被传入参数触发运行」，看这一行即可否定：拿到 `job_id` 就说明触发被接受了 |
| `60020` | 调用 IP 不在「企业可信IP」名单，文案里会带上实际出口 IP 与两种处理方式 |
| `40001` / `40013` | Secret / 企业 ID 不正确 |
| `42001` / `40014` | access_token 过期（插件会自动清缓存重取并重试一次） |
| `60011` / `82001` | 收件人不在应用可见范围内 |
| `45009` | 触发频率限制（每应用每天有人次上限；单成员每分钟 ≤30 条） |
| HTTP 400（**提交阶段**） | 参数被拒：出现了未声明的键，或 `select` 取值不在选项内（如用了已移除的 `markdown` / `template_card`）。**先核对第五、六节的列表** |
| HTTP 404 | 本插件未安装或未启用 |

调用方建议：**把 `error` 原文记进自己的日志**，不要吞掉；同时捕获网络异常并设置超时。

---

## 十一、注意事项

- **本插件会把收到的参数写进 TTD 运行日志**（`我的插件 → 企业微信通知 → 运行记录` 可见），
  便于排查「任务已受理但没收到」这类问题 —— 你能直接看到对方到底传了哪些键、正文是什么、
  有没有传收件人。**凭据类字段只显示「已填写（长度 N）」**：判断依据是键名归一化后含
  `secret` / `token` / `password` / `aeskey` / `credential` / `apikey` 等片段，
  所以**不要在与内容无关的字段名里用这些词**（例如把正文键命名为 `content_token`），否则它的值不会出现在日志里。
  单行内容超过 2000 字会截断并标注。
- **不要传 `save_settings: true`**：会把调用参数写进用户在该插件里的设置。
- **本插件没有常驻进程，也不需要「提前启动」或「保活」**：TgtoDrive 的插件是**一次性进程** ——
  你每调用一次，平台就新起一个进程执行本插件的 `run()`，跑完即结束（超时会被清理）。
  平台明确规定插件**不能注册常驻服务、守护线程或后台定时循环**，
  所以「先把它跑起来、之后才收得到调用」这种模型在这里并不存在。
  若你的场景里出现过「有时收不到」，请按上面的 `delivery_ok` / HTTP 状态码排查，
  而不是去找一个并不存在的「运行状态」。
- 本插件与所有插件共用一套任务队列：同一插件同时只能有一个未完成任务，队列满时提交会失败，请做重试或降级处理。
  （注意本插件的 `func=test` 会**间隔 3 秒发两条**消息，这期间它处于「运行中」，
  此时再调用可能被拒或排队 —— 这也是「偶尔失败」的常见来源。）
- 插件 `timeout` 为 120 秒；被调用时同样受此限制，长文本分段发送也在这一时限内完成。
- 插件返回的 `result` 会被包装后返回，整体 **≤1 MiB**；不要指望从中读到大段日志。
- 高频调用请自行节流：企业微信侧对同一成员有 30 次/分钟、1000 次/小时的限制。
- 本插件的凭据（Secret 等）**不会**通过返回值或日志泄露给调用方，也**不提供**凭据读取的对外契约：
  插件内部在补齐配置时会读自己的 `settings.json`（或 `GET /api/toolbox/plugins/wecom-notify/settings`），
  但这属于实现细节 —— 调用方**不应**自行调用该接口，更不要把它写进日志。

---

## 十二、为什么不是「加载对方代码」

有时会想到另一种做法：让调用方**直接加载本插件的配置与代码**，在调用方自己的进程里调用发送函数。
这个目标（不重复实现发送逻辑）是对的，但**机制上在这里做不到**，原因有三条，且第一条是决定性的：

| 原因 | 说明 |
| --- | --- |
| **① 读者拿不到被调用方的 `data_dir`**（决定性） | 插件的「身份」由平台传入的 `context` 决定：`context` **只有** `plugin_dir` 与 `data_dir` 两个键，而 `data_dir` 是**该插件自己的**持久目录。调用方在自己进程里 import 别人代码时，**给不了对方它自己的 `data_dir`**，对方就读不到自己保存的凭据 —— 结果正好回到「凭据为空、任务提交成功但发不出去」这个故障上 |
| **② 代码目录会随更新被替换** | 规范明确 `plugin_dir`「更新会替换」，另一个插件的版本目录名与层级并未公开；按路径 import 一旦对方更新就会断 |
| **③ 会把对方的顶层代码放进你的进程执行** | 插件的设计是隔离运行、各自一次性进程。跨插件 import 会把对方模块级代码、依赖与异常都带进你的进程，出问题难以界定 |

**因此本插件采用的机制是**：

- **代码不搬**：发送逻辑留在本插件里，通过**运行接口**调用 —— 由平台为本插件新起进程，
  它自然就拿到了**自己的 `context`**，也就能读到自己的配置；
- **配置按需只读**：调用方若需要展示「会发给谁」，可以读 `GET /api/toolbox/plugins/wecom-notify/settings`
  里的**非密字段**（如 `touser`），但**不应**读取或转发凭据；
- **契约统一**：调用方只准备第三节的「标准化发送内容」，
  新增能力不会再要求调用方跟着改（这正是本次改造要解决的问题）。

---

## 十三、相关文件

| 文件 | 说明 |
| --- | --- |
| [`plugin.json`](plugin.json) | 插件清单：`inputs` 定义与界面结构，**调用参数的权威来源** |
| [`plugin.py`](plugin.py) | 插件实现；`_NotifyRunner.build_payload` 是参数到企业微信接口的映射 |
| [`README.md`](README.md) | 面向使用者的配置与排错说明 |
