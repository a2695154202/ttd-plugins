# 药丸论坛签到 · TgtoDrive 插件

移植改写自 [thsrite/MoviePilot-Plugins](https://github.com/thsrite/MoviePilot-Plugins) 中的「药丸签到」插件（v3.0.1，原作者 [@thsrite](https://github.com/thsrite)），由 **a2695154202** 按 TgtoDrive Python 插件协议改写。

- **插件 id**：`invites-signin`
- **版本**：`1.0.3`
- **作者**：`a2695154202`
- **入口**：`plugin.py`
- **超时**：300 秒
- **依赖**：仅使用 Python 标准库 + 容器已安装的 `requests`；可选 `curl_cffi`（浏览器指纹模式）。**不安装任何依赖。**
- **许可证**：GPL-3.0（继承上游，见文末「来源与许可证」）

---

## 一、功能

| 功能 | 说明 |
| --- | --- |
| 自动签到（`auto`） | 先用 Cookie 向站点换取新的 Flarum session 再签到；整条通道失败后回退「用户名 + 密码」登录签到，与原始插件策略一致。 |
| 仅 Cookie 签到（`cookie`） | 只用填写的 Cookie 通道，不尝试登录。 |
| 仅账号密码签到（`login`） | 只用用户名密码登录后签到。 |
| 查询签到状态（`status`） | 只读取 `canCheckin`、最近签到时间、累计天数、剩余药丸，不执行签到。 |
| 查看签到历史（`history`） | 展示本地保存的历史记录，不发起任何网络请求。 |
| 读取通知机器人列表（`bots`） | 读取 TgtoDrive 已配置的通知机器人，列出**序号 / 名称 / 状态 / 推送目标（掩码）/ 来源**，并为每个可用机器人生成一条「发送测试通知」按钮。 |
| 发送测试通知（`test_notify`） | 用当前选中的机器人发送一条测试消息，用于验证通知链路。 |

每个签到功能都带：

- **运行日志窗口**：结果页内嵌 `code` 组件展示完整运行日志；同一份日志也会输出到 TgtoDrive 的「运行日志」。
- **结果通知**：成功 / 今日已签到 / 失败都会推送一条消息到 TgtoDrive 已配置的**通知机器人**（可用「通知机器人」下拉框指定用哪一个，默认自动选主机器人）。
- **微信通知（可选）**：开启后，签到结果会**同时**通过「企业微信通知」插件（`wecom-notify`）发一条微信通知。做法是走 TgtoDrive OpenAPI 的插件运行接口调用那个插件 —— **企业 ID / Secret 等凭据与收件人都沿用它在自己设置里已保存的配置**，本插件只传要发送的内容，支持**文本**与**带图卡片**两种形式。需要先安装并配置好 `wecom-notify`，并填写「TgtoDrive 地址」与「OpenAPI 令牌」。
- **「运行一次」按钮**：固定在表单**顶部右侧**（与页签标题行齐平），用「执行功能」中选中的功能立即执行一次，并强制开启本次通知；同一位置还有「发送测试通知」。
- **按钮分布**：「刷新机器人列表」在「通知与接口」页签内，其余页签不显示；「运行一次」「发送测试通知」固定在顶部右侧，不随页签切换。

### 签到判定逻辑（与原插件一致）

1. 签到前查询 `GET /api/users/{userId}`，若 `canCheckin=false` 且 `lastCheckinTime` 为今天 → 视为「今日已签到」，不重复签到。
2. 否则 `POST /api/checkin`。
3. HTTP 非 200 时再查一次状态；若状态显示今日已签到，仍按成功处理（原插件同样逻辑，避免因重复签到报错而误判失败）。
4. HTTP 200 时必须确认响应中 `canCheckin=false` 且 `lastCheckinTime` 为今天，才算签到成功。

---

## 二、参数

| 参数 | 类型 | 默认 | 说明 |
| --- | --- | --- | --- |
| `func` | select | `auto` | 执行功能，见上表。 |
| `notify` | boolean | `true` | 是否推送结果通知。 |
| `notify_bot` | select | `auto` | 用哪个通知机器人推送：`auto`（优先主机器人）或 `index:1`–`index:8`（列表第 N 个）。选中值随插件设置保存。 |
| `tgto_base_url` | text | 空 | TgtoDrive 地址，留空则读环境变量 `TGTO_OPENAPI_BASE_URL`；只填了令牌时会按 `http://127.0.0.1:12366` 尝试。 |
| `tgto_token` | password | 空 | OpenAPI 令牌，留空则读环境变量 `TGTO_OPENAPI_TOKEN`。用于读取通知机器人，以及调用「企业微信通知」插件。 |
| `wecom_notify` | boolean | `false` | 是否**同时发送微信通知**（调用 `wecom-notify` 插件）。 |
| `wecom_msgtype` | select | `text` | 微信通知形式：`text` 文本 / `template_card` 带图卡片。 |
| `wecom_touser` | text | 空 | 微信接收成员（UserID，多个用 `\|` 分隔，或 `@all`）；留空则沿用 `wecom-notify` 的收件人设置。 |
| `wecom_card_image` | text | 空 | 微信卡片图片；留空则沿用 `wecom-notify` 的卡片图片设置。 |
| `cookie` | password | 空 | 需包含 `flarum_remember`（`flarum_session` 会自动刷新）。 |
| `username` | text | 空 | 回退登录通道的用户名 / 邮箱。 |
| `user_password` | password | 空 | 回退登录通道的密码。 |
| `site_base` | text | `https://invites.fun` | 站点地址，一般无需修改。 |
| `use_proxy` | boolean | `true` | 先读容器环境变量，再读 TgtoDrive 全局代理。 |
| `use_browser_fingerprint` | boolean | `false` | 改用 `curl_cffi` 模拟 Chrome 指纹（应对 Cloudflare）。 |
| `retry_count` | number | `2` | 1–10，失败重试轮数。 |
| `retry_interval` | number | `10` | 0–300 秒。**原插件单位是分钟，此处改为秒**，以适配插件超时。 |
| `history_days` | number | `30` | 1–3650，本地历史保留天数。 |

参数会随 `/app/db` 持久卷保存，服务重启与插件更新后保留；卸载插件时删除。

---

## 三、通知实现说明（重要）

TgtoDrive 的 OpenAPI **没有**「发送任意内容通知」的接口——`POST /api/proxy_settings/test_tg` 只能发送固定内容的测试消息。

因此本插件采用的做法是：

1. 用 `GET /api/notify-bots`（必要时回退 `GET /api/proxy_settings`）读取项目里**已经配置好的通知机器人**；
2. 按「键名语义 + 取值形态」识别出机器人 Token、推送目标 ID 与代理（规范中该响应被标记为 `generic`，字段名不做保证，故不硬编码字段路径）；
3. 用选中的机器人直接调用 Telegram Bot API `sendMessage` 推送签到结果。

即：**使用的是项目自己配置的通知机器人**，只是绕过「只能发测试文本」的限制。

### 3.1 「通知机器人」下拉框是怎么工作的

TgtoDrive 的插件清单由服务端**静态读取**（AST），打开插件页面时不会执行插件代码，因此下拉框的选项**无法**按接口返回结果动态生成，也不允许在运行结果里放 `field` 组件。

所以本插件把下拉框做成**按序号选择**：

1. 点一次「刷新机器人列表」（等价于 `func=bots`），结果页会给出 `序号 / 名称 / 状态 / 推送目标 / 来源` 的对照表；
2. 在「通知与接口」页的「通知机器人」下拉框里选「列表第 N 个机器人」，该选择会随插件设置一起保存，下次打开自动恢复；
3. 每次发送通知时，日志都会打印**实际使用的机器人名称与序号**（结果表的「通知机器人」一行同样显示），便于核对；
4. 若所选序号不存在，或该条目缺少 Token / 推送目标 ID，插件会**自动回退到主通知机器人**并在日志中说明，不会让通知静默失败。

### 3.2 微信通知是怎么发出去的

签到插件**不直接实现企业微信接口**，而是复用它旁边那个「企业微信通知」插件：

```text
invites-signin                          wecom-notify
     │  POST /api/toolbox/plugins/wecom-notify/run
     │  {"params": {"func": "send", "msgtype": "...", "content"/"card_content": "..."}}
     └──────────────────────────────────────────▶  ├─ 用它已保存的企业 ID / Secret 取 access_token
                                                   └─ 调 message/send 把消息发出去
```

这样设计的原因：

- **凭据只有一份** —— 企业 ID、Secret、代理地址已经配在 `wecom-notify` 里，签到插件不必再存一份密钥；
- **收件人可复用** —— 不填「微信接收成员」时，就发给 `wecom-notify` 里设置好的收件人；
- **样式可复用** —— 卡片图片、来源名称、图片比例都沿用那边的设置。

调用是**非阻塞**的：提交任务后最多轮询 3 次（每次间隔 2 秒）取结果，取不到也不影响签到本身；
结果表的「微信通知」一行会写明是「已发送」还是「已提交（后台执行，未确认结果）」。
完整调用契约见 [`plugins/wecom-notify/CALLING.md`](../wecom-notify/CALLING.md)。

> 建议：只有一个机器人时保持 `auto` 即可。若接口以对象形式返回、条目顺序不稳定，也建议用 `auto`，然后按日志里的机器人名称确认。

### 3.2 连接 TgtoDrive 的两种方式

| 方式 | 做法 | 说明 |
| --- | --- | --- |
| 环境变量（推荐） | 配置 `TGTO_OPENAPI_BASE_URL` 与 `TGTO_OPENAPI_TOKEN` 后重启服务 | 系统不会自动注入，需自行配置 |
| 插件表单 | 在「通知与接口」页填写「TgtoDrive 地址」与「OpenAPI 令牌」 | 令牌为 `password` 类型，界面遮蔽显示；**插件设置以明文 JSON 保存在服务器插件目录，管理员可读取**，更在意安全时请用环境变量并留空此项 |

```text
TGTO_OPENAPI_BASE_URL=http://127.0.0.1:12366
TGTO_OPENAPI_TOKEN=<在「实用工具 → OpenAPI」创建的令牌>
```

两种方式都没配置时，签到照常执行，只跳过通知并在日志中给出提示（不会把签到判为失败）。

> 说明：本插件只**读取**项目配置，不修改任何项目设置；Token 与机器人凭据不会出现在日志、返回值或图片 URL 中，推送目标 ID 与代理地址在展示时会做掩码处理。

---

## 四、持久化与文件

| 路径 | 内容 |
| --- | --- |
| `context["data_dir"]/history.json` | 签到历史（每天一条，保留最近 `history_days` 天）。 |

- `data_dir` 由 TgtoDrive 提供，插件更新后保留，卸载时删除。
- 插件**不写入** `plugin_dir`，也不依赖 `/app/strm`、`/app/upload` 等挂载目录。
- 插件**不保存** Cookie / 密码副本（`flarum_session` 每次运行都从 `flarum_remember` 重新换取，无需落盘）。

### 修改 / 删除行为

- 默认功能**不删除服务器上的任何文件**，唯一的写操作是覆盖 `data_dir/history.json`。
- 「查看签到历史」为纯读取。

---

## 五、定时执行

在「实用工具 → 我的插件 → 定时执行」新增计划，选择本插件：

| 项目 | 建议值 |
| --- | --- |
| cron | `5 8 * * *`（每天 08:05，北京时间 Asia/Shanghai） |
| 运行参数 | `func=auto`，填写 Cookie 或账号密码；`notify=true` |
| timeout | 插件已声明 300 秒 |

错峰建议：避开整点，例如 `17 8 * * *`、`43 7 * * *`。插件本身不含任何定时循环。

---

## 六、安装与使用

### 从插件市场安装

在 TgtoDrive「实用工具 → 我的插件 → 插件市场」添加本仓库为来源（分支 `main`，目录路径 `plugins.json`），刷新后选择本插件安装。后续更新同样在此处操作，插件数据保留。

### 手动导入

**要导入的是打包产物，不是源码目录里的 `plugin.py`。**

| 想导入的文件 | 从哪里拿 |
| --- | --- |
| `invites-signin.py`（单文件，推荐） | 仓库 [Releases](https://github.com/a2695154202/ttd-plugins/releases) 附件，或本仓库 [`dist/invites-signin.py`](../../dist/invites-signin.py) |
| `invites-signin.zip`（插件包） | 仓库 [Releases](https://github.com/a2695154202/ttd-plugins/releases) 附件 |

> ⚠️ **不要把 `plugins/invites-signin/plugin.py` 当作单文件导入**。它是插件包内入口，清单写在同目录的 `plugin.json` 里，单独导入会被 TgtoDrive 拒绝并提示：
> `Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典`。单文件版由 `scripts/package_plugin.py` 在文件开头内联 `PLUGIN_MANIFEST` 后生成，见上表。

步骤：

1. 打开「实用工具 → 我的插件 → 导入插件」。
2. 选择 `invites-signin.py`（单文件）**或** `invites-signin.zip`（压缩包），二者选其一导入即可。
3. 阅读并勾选信任代码的确认项，确认导入。
4. 打开插件卡片：在「账号与凭据」页签填写 Cookie 或账号密码；「通知与接口」页签填 TgtoDrive 地址与令牌（或改用环境变量）、选择通知机器人；**需要微信通知就打开「同时发送微信通知」**；「签到配置」页签按需调整。
5. 想先验证通知链路时，在「通知与接口」页签点「刷新机器人列表」查看序号与名称，再点表单顶部右侧的「发送测试通知」；确认无误后点同处的「运行一次」立即签到并接收通知。
6. 需要每天自动运行时，按第五节配置定时计划。

### 本地构建

在仓库根目录执行（无需第三方依赖）：

```bash
python scripts/package_plugin.py --plugin invites-signin
```

产物输出到 `dist/`，同时打印 SHA-256 与字节数：

- `dist/invites-signin.py` —— 单文件版，顶层内联 `PLUGIN_MANIFEST`，可直接「导入插件」；
- `dist/invites-signin.zip` —— 插件包版，内含 `plugin.json` + `plugin.py` + `README.md`。

打包为确定性输出：相同源码重复打包得到完全相同的字节与 SHA-256，因此本地产物与 GitHub Actions 产物哈希一致。

---

## 七、测试方法

以下场景**均在本地静态检查过语法与清单格式**；真实网络行为需在你的容器内实测确认。

| 场景 | 操作 | 预期 |
| --- | --- | --- |
| 正常签到 | 填写有效 Cookie，`func=auto`，点「运行一次」 | 结果页显示「✅ 签到成功」，日志列出刷新 session、userId、签到响应；主通知机器人收到消息 |
| 今日已签到 | 同一天再次运行 | 结果页显示「✅ 今日已签到（无需重复）」，通知同样发出 |
| 账号密码回退 | 只填用户名密码，`func=login` | 日志出现「账号密码登录成功」，随后完成签到 |
| Cookie 完全失效 | 填写过期 Cookie 且不填账号密码，`func=auto` | 重试 `retry_count` 次后返回 `status=failed`，通知内容为失败原因 |
| 仅查询状态 | `func=status` | 结果页表格给出 `canCheckin`、最近签到时间、累计天数、剩余药丸，无签到请求 |
| 查看历史 | `func=history` | 表格展示历史记录；首次运行显示「暂无记录」 |
| 读取机器人列表 | `func=bots`，已配置地址与令牌 | 表格列出机器人序号 / 名称 / 状态 / 掩码目标 / 来源，并为可用机器人生成测试按钮 |
| 测试通知 | `func=test_notify` 或点「发送测试通知」 | 服务器上出现一条「本条为测试消息」，结果页显示 ✅；该功能会忽略「发送结果通知」开关 |
| 指定机器人 | `notify_bot=index:2` | 日志显示「使用通知机器人「X」（列表第 2 项…）」 |
| **微信通知（文本）** | 开启「同时发送微信通知」，`wecom_msgtype=text`，点「运行一次」 | 签到结束后企业微信收到一条文本通知；结果表「微信通知」一行显示「已发送」 |
| 微信通知（卡片） | `wecom_msgtype=template_card` | 企业微信收到带图卡片，图片与来源沿用 `wecom-notify` 的卡片设置 |
| 微信通知未配置 | 打开开关但不填 TgtoDrive 地址或令牌 | 日志提示跳过微信通知，**Telegram 通知不受影响**；结果表显示「未配置 TgtoDrive 地址或令牌」 |
| 未装企业微信插件 | 打开开关且地址令牌都填了，但没装 `wecom-notify` | 日志提示调用失败（HTTP 404）并附返回内容，签到本身仍正常完成 |
| 序号越界 | `notify_bot=index:8`（项目只有 1 个机器人） | 日志提示不存在该序号并回退到主机器人，通知仍发出 |
| 空输入 | `func=auto`，Cookie 与账号密码都为空 | 抛出 `ValueError`：Cookie 与账号密码均未配置，无法执行签到 |
| 无效输入 | `retry_count=0` 或 `history_days=99999` | 抛出 `ValueError`，提示取值范围 |
| 未配置 OpenAPI | 表单与环境变量都不填，`notify=true` | 签到正常完成，日志提示如何配置，结果页「通知状态」为未发送 |
| 通知链路失败 | Token 或目标 ID 不可用 | 日志记录失败原因，签到结论不受影响 |
| Cloudflare 拦截 | 开启 `use_browser_fingerprint` | 改用 `curl_cffi` 请求，日志中不会出现回退提示 |
| 代理异常 | `use_proxy=true` 但代理不可达 | 请求异常被记录为失败原因，不产生未捕获异常 |

---

## 八、与原 MoviePilot 插件的差异

| 原插件 | 本插件 | 原因 |
| --- | --- | --- |
| `BackgroundScheduler` + `CronTrigger` | 移除，改由 ttd「定时执行」配置 cron | ttd 插件不得注册常驻定时器 |
| `_PluginBase` / `settings` / `logger` / `NotificationType` | 移除，改用 `params` + `context` + `print` + 通知接口 | 不导入项目内部模块 |
| `CloakBrowser` 浏览器仿真 | 改为 `curl_cffi` Chrome 指纹模式 | ttd 容器无浏览器环境，`curl_cffi` 已预装 |
| `settings.PROXY` | 环境变量 → ttd 全局代理 | ttd 无该模块 |
| 插件配置页（Vuetify 表单） | 清单 `inputs` + `ui` 组件 | ttd 由清单自动生成界面 |
| `post_message(...)` | 读取主通知机器人后调用 Telegram Bot API | ttd 无对应发消息接口 |
| 重试间隔（分钟） | 重试间隔（秒） | 适配插件超时限制 |
| 签到时自动回写 Cookie 到配置 | 不再回写 | 每次运行都从 `flarum_remember` 重新换取 session，无需持久化凭据 |

---

## 九、来源与许可证

本插件是 [thsrite/MoviePilot-Plugins](https://github.com/thsrite/MoviePilot-Plugins) 中「药丸签到」插件（v3.0.1，原作者 [@thsrite](https://github.com/thsrite)）的移植衍生作品，由 **a2695154202** 适配为 TgtoDrive 插件。

上游项目以 **GNU General Public License v3.0** 授权。本插件复用了上游的签到判定流程、Cookie 换会话策略、登录回退与重试逻辑，属于 GPL-3.0 定义的衍生作品，因此：

- 本插件同样以 **GPL-3.0** 授权，不得改为 MIT 等宽松许可证；
- 原作者署名保留在本文件与 `plugin.json` 的 `author` 字段中；
- 若你再次分发本插件，需一并提供源码并保留同样的授权与署名。

许可证全文见仓库根目录的 [LICENSE](../../LICENSE)。
