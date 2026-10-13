# TgtoDrive 插件协议硬约束清单

写插件时逐条对照。全部来自 `01-ai-development-prompt.md` 与 `02-plugin-development-guide.md`。

## 交付形式

- 单个脚本 → 优先 `.py`；需要辅助模块或资源 → 压缩包。
- 单文件：顶层**有且仅有一次** `PLUGIN_MANIFEST = {...}` 字面量赋值，用 Python 的 `True/False/None`。AST 静态读取，**导入时不执行脚本**，因此不能用函数、变量、环境变量或表达式生成清单。
- 单文件固定保存为 `plugin.py`，`entry` 可省略。
- 压缩包：根目录至少含 `plugin.json` + 入口 `.py` + `README.md`；允许外包一层目录。
- 打包命令：`python -m zipfile -c my-plugin.zip plugin.json plugin.py README.md`。**不要把打包脚本当插件入口。**
- 限制：上传 ≤10 MiB、≤500 个条目、解压后 ≤50 MiB。路径用相对路径与正斜杠，禁止绝对路径、反斜杠、`..`、软硬链接、特殊文件、Windows 保留名、重复路径、仅大小写不同的路径。不打包 venv、`__pycache__`、凭据、临时文件。

## 清单字段

| 字段 | 约束 |
| --- | --- |
| `schema_version` | 固定整数 `1` |
| `id` | `^[a-z][a-z0-9_-]{1,63}$`，避开 Windows 保留名，更新时保持不变 |
| `name` | 非空，≤100 字符 |
| `version` | 非空，≤50 字符；市场版本需符合 PEP 440，推荐 `1.0.0` |
| `description` | ≤4000 字符 |
| `author` | ≤100 字符 |
| `entry` | 包内 `.py` 相对路径，推荐 `plugin.py`，文件必须存在 |
| `timeout` | 整数秒 1–86400，**默认仅 60 秒**；长任务须显式写大，如 `86400` |
| `inputs` | ≤50 项 |
| `ui` | 可选；组件 ≤200 个，嵌套 ≤8 层 |

`plugin.json` **不能有注释**，≤65,536 字节。

## 输入字段

- `name`：`^[A-Za-z_][A-Za-z0-9_]{0,63}$`，唯一。`label`：非空，≤100 字符。
- `type`：`text`、`textarea`、`password`、`email`、`url`、`tel`、`search`、`date`、`datetime-local`、`time`、`color`、`number`、`range`、`boolean`、`switch`、`select`、`radio`、`multiselect`。**没有 `file` 类型。**
- `required` 默认 `false`；`number/range` 的 `0` 与 `boolean/switch` 的 `false` 都算有效值。
- 大整数（目录 ID、文件 ID）**必须用 `text`**，并在返回值里转成字符串 —— 网页 `number` 只能精确表示 ±9,007,199,254,740,991。
- `select/radio/multiselect` 必须有 `options`（1–100 项），`value` 唯一且 ≤500 字符；`select/radio` 的 `default` 必须是某个 `option.value`。
- `placeholder` ≤500 字符，`help` ≤2000 字符。
- **不要**添加正则校验、自定义 HTML/JS/CSS、自定义路由、`cron`、`schedule` 或权限声明字段。

## ui 组件

`layout` = `stack` | `grid`；`columns` 1–4；`width` = `normal` | `wide` | `full`。

可用类型：`field`、`group`/`card`/`grid`、`tabs`、`heading`/`text`/`code`/`badge`/`alert`、`markdown`、`divider`、`image`、`link`、`table`（≤30 列 200 行）、`progress`、`button`。

`style`：`tone`(default/primary/success/warning/danger/muted)、`align`、`size`、`variant`(solid/outline/soft)、`span`(1–4)。

要点：

- 输入仍在 `inputs` 里声明，用 `{"type":"field","name":...}` 放置；**未放置的输入会被自动追加到表单**，所以无法"隐藏"某个输入。
- 同一个输入不能重复引用。
- `button.action` 只能是 `run` / `save` / `reset`，不新增服务端路由；`run` 的 `params` 覆盖已声明输入并调用同一入口。**`params` 里的键必须是已声明的输入**，否则会被拒绝。
- `image.src` 支持 HTTP(S)、base64 data URL、`plugin://包内路径`、`data://数据目录路径`。
- 运行结果可返回 `{"ui": {...}, "其他结果": ...}` 或 `{"ui": [...]}`；**结果里不能放 `field`**。

## Python 入口

- 必须是**同步** `def run(params, context)`，支持两个位置实参。异步库用 `asyncio.run()` 在内部调用；不要 `async def`，不要返回生成器/协程。
- `context` 只有 `plugin_dir`、`data_dir` 两个键，均为绝对路径字符串。持久数据写 `data_dir`（更新保留、卸载删除），**不要写 `plugin_dir`**（更新会替换）。
- **不要**在模块导入阶段做网络请求、写文件或其他业务操作 —— 必须放进 `run`。
- 每次运行是新进程，全局变量不跨任务保留。
- 返回值须可 JSON 序列化：字符串、字典、列表、数值、布尔、`None`。**不要**返回 `Path`、`bytes`、文件句柄、`set`、`NaN`、`Infinity`。
- 结果（含运行器包装）**≤1 MiB**；大结果写 `data_dir` 并只返回摘要。
- `print()` 即运行日志，stdout/stderr 各保留 64 KiB，超出截断。
- 失败要抛带可理解信息的 `ValueError`/`RuntimeError`；**不要把实际失败包装成成功结果**。
- 不使用 `input()`、交互终端、GUI、Flask session/request。

## 定时执行

- 由用户在「我的插件 → 定时执行」配置，**插件清单里不能声明 cron**，插件内也不能注册常驻服务、守护线程或后台循环，不要用 `sleep` 等下次执行。
- cron 5 段「分 时 日 月 周」，无秒，固定 `Asia/Shanghai`（UTC+8）。支持 `*`、逗号、范围、`/` 步长；月份与星期可用英文简称，周日 `0` 或 `7`。
- 日与周都有限定时为"或"关系；含通配符（包括 `*/n`）时两字段同时匹配。
- 上一轮仍在运行/排队、插件停用、队列已满 → 本次跳过，不补跑。
- 交付时需给出**推荐 cron + 运行参数 + timeout 示例**。

## 环境与路径

- python:3.13-slim Linux 容器，`sys.executable` 起独立子进程，共用容器依赖。
- **无 pip 安装**、不建 venv、不改项目依赖、不使用 `requirements.txt`。
- 路径必须是容器内 Linux 路径；宿主机目录需先挂载（如挂到 `/media`）。用 `pathlib`，不依赖 PowerShell / 注册表 / COM / 桌面 GUI。
- 应用在 `/app`，插件在 `/app/db/toolbox/plugins`，`/app/db` 为持久卷。
- 不要假设 `/app/strm`、`/app/upload` 存在或可写。
- 命令可用性先 `shutil.which()` 检查。不要假设有编译工具、桌面浏览器、GPU、额外字体。
- 网络：bridge 模式 `127.0.0.1` 指向容器自身；host 模式与宿主机共享网络。按用户实际配置选地址。

## 不要依赖项目内部

- 主程序是受保护的 `.pyc`/`.so`。**不要**导入 `server`、`tgto123`，不要启动主服务，不要依赖内部函数、数据库表结构、Flask 请求上下文。
- 不要直接改数据库代替公开 API。

## OpenAPI 调用

- 环境变量 `TGTO_OPENAPI_BASE_URL` + `TGTO_OPENAPI_TOKEN`（用户自行配置，系统不注入）。同容器常见 `http://127.0.0.1:12366`。
- 用 `Authorization: Bearer <TOKEN>`，走原 `/api/...` 路径，**不要编造 `/openapi/v1` 之类前缀**。
- 每个请求都要设 `timeout`；默认 `allow_redirects=False`，检查状态码与 `Content-Type`（不是所有响应都是 JSON）。
- **不要把 Authorization 转发到返回的外部 URL。**
- 收到 HTTP 503 且 `code=session_persistence_failed`：业务可能已完成，先核对结果，**不要自动重试修改类操作**。
- `POST /api/save_json` 必须在顶层传 `target_dir_id`（推荐数字字符串，`"0"` 表示根目录），否则 400。
- `POST /api/toolbox/plugins/import` 需 `trusted=true`；Bearer 调用无需 `X-Toolbox-Request`。
- 插件运行接口的 `params` 必须按目标插件 `inputs` 填写，未知参数会被拒绝。
- 真实 Token 不入插件包、日志、返回值、URL 查询参数；AI 开发过程只用 `YOUR_OPENAPI_TOKEN` 占位符。

## 凭据与安全

- 不读取/输出与需求无关的账号配置、Cookie、Token、密钥；不要索要整个环境变量文件。
- `password` 类型只遮蔽界面显示，`settings.json` 里仍是明文，管理员可读。
- 日志与返回值中**不得出现密码**。
- 涉及删除/覆盖的插件应先提供预览参数并校验目标路径，**不要默认递归扫描或删除整个服务器**。
