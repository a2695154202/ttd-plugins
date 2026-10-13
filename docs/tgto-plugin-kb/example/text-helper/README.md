# 实用工具 · Python 插件开发

在「实用工具 → 我的插件」下载 ZIP 或单文件开发示例，即可获得能直接导入的文本处理插件。修改后通过「导入插件」安装，不需要修改主程序或重启服务。也可以打开「插件市场」，从已配置的 GitHub 仓库下载并安装插件，详见下方市场说明。

也可以点击「AI 开发提示词」，一键复制后发给自己的 AI，并补充要开发的插件需求。提示词面向 Linux 容器；在正式容器内实时读取 Python 版本、操作系统、架构、已安装依赖及版本、常用命令可用性，并附上插件协议、参考代码和打包要求。本地开发预览只显示标注清楚的镜像构建参考，不会把本机环境当成容器环境。

需要调用项目功能时，可在「实用工具 → OpenAPI」创建访问令牌、下载接口规范，并将规范与提示词一起交给 AI。插件使用 Bearer Token 调用原 `/api/...` 路径；真实令牌只在运行时配置，不能写进插件 ZIP 或提示词。详见 [OpenAPI 使用说明](openapi.md)。

目录 ID、文件 ID 等精确标识符请使用 `text` 参数，并以字符串返回给网页。网页 `number` 输入不能精确表示超过 ±9,007,199,254,740,991 的整数，运行前会拒绝此类输入。

## 使用流程

1. 下载开发示例，或按下方协议自行创建插件。
2. 选择插件文件，阅读并勾选信任代码的确认项，然后导入。
3. 插件会显示为工具卡片。打开时自动读取上次保存的设置；填写参数，可单独点击「保存设置」，运行也会自动保存。点击「恢复默认设置」清除保存值。查看返回结果与标准输出、错误日志。
4. 导入相同 `id` 的包时，需要确认更新。更新保留插件数据和启停状态；失败的导入不会覆盖已有版本。
5. 停用插件后不能发起新任务。卸载会删除插件代码及其数据，需确认后执行。运行中不能更新、停用或卸载该插件。
6. 需要自动运行时，点击工具栏「定时执行」，新增计划，选择插件并填写 cron 表达式和运行参数。可以预览接下来三次执行时间，再保存、编辑或启停计划。

Python 插件以当前服务账户运行，可访问服务器文件、环境变量与网络。独立进程只用于隔离异常和限制执行时间，不是权限沙箱。请仅导入自己编写或已审查、可信来源的代码；导入不会自动执行插件。

## 支持格式与包结构

支持 `.py` 单文件，以及 `.zip`、`.pyz`、`.tar`、`.tar.gz` / `.tgz`、`.tar.bz2` / `.tbz2` / `.tbz`、`.tar.xz` / `.txz`、`.7z`、`.rar`。7z/RAR 需要 libarchive-c 和系统 libarchive，官方容器已配置这些依赖；页面按当前环境的实际能力显示可用格式。加密、分卷和解码器不支持的压缩方式会被拒绝。

所有压缩包使用相同结构。`.pyz` 在这里作为 ZIP 插件包读取，并不执行任意 zipapp；它仍需包含 `plugin.json` 和清单指定的 Python 文件。

```text
text-helper.zip
├── plugin.json
├── plugin.py
└── README.md       # 可选，也可以包含其他 Python 模块和资源
```

允许压缩包外包一层目录，但该目录内必须直接包含 `plugin.json`。清单与 Python 文件使用 UTF-8 编码。不支持绝对路径、`..`、反斜杠路径、软硬链接、特殊文件或重复路径。上传文件最大 10 MiB，解压总大小最多 50 MiB，最多 500 个条目。不要打包虚拟环境、缓存、账号密钥或 `__pycache__`。

## 单个 Python 文件

单文件无需额外的 `plugin.json`。把同样的清单写成文件顶层的 `PLUGIN_MANIFEST` 字典，应用会静态读取它并自动生成插件卡片及参数表单；导入时不会执行 Python 代码。字典必须为直接赋值的字面量，不能调用函数、读环境变量或拼接生成。Python 布尔值写 `True` / `False`，不是 JSON 的 `true` / `false`。入口固定为 `plugin.py`，省略清单的 `entry` 即可。

```python
PLUGIN_MANIFEST = {
    "schema_version": 1,
    "id": "hello-plugin",
    "name": "问候插件",
    "version": "1.0.0",
    "inputs": [{"name": "name", "label": "姓名", "type": "text", "default": "世界"}],
}

def run(params, context):
    return "你好，" + params["name"]
```

保存为 UTF-8 的 `hello.py` 后即可导入。必须提供同步的 `run(params, context)`；任意普通脚本、异步入口或依靠导入执行的脚本不能直接作为插件。单文件无需编写前端代码，多文件或额外资源使用压缩包。

## 插件市场

打开「我的插件 → 插件市场 → 来源设置」，填写可信的公开 GitHub 仓库 `账号/仓库名`，分支默认 `main`，目录路径默认 `plugins.json`。保存后加载目录，按名称或分类查找，查看来源、依赖和版本，确认信任后安装。更新需再次确认覆盖，保留插件数据。安装不会自动运行，也不会自动安装 Python 依赖。

项目没有预设尚不存在的官方仓库。维护者可使用项目中的 `plugin-marketplace-template/` 建立市场仓库，发布后让用户填入地址；或在容器配置 `TGTO_PLUGIN_MARKET_REPOSITORY=账号/仓库名` 作为默认来源。页面保存的来源优先于环境默认值。断网时可浏览上次成功的缓存，但新安装必须重新确认远端目录，无法连接时请使用可信的本地导入。

详细的用户操作和维护者发布流程见 [插件市场使用说明](toolbox-marketplace.md)，也可从市场页面打开「使用说明」。

## plugin.json

```json
{
  "schema_version": 1,
  "id": "text-helper",
  "name": "文本处理",
  "version": "1.0.0",
  "description": "逐行处理文本",
  "author": "你的名字",
  "entry": "plugin.py",
  "timeout": 60,
  "inputs": [
    {"name": "text", "label": "文本", "type": "textarea", "required": true},
    {"name": "limit", "label": "最多行数", "type": "number", "default": 100},
    {"name": "strip", "label": "清理空白", "type": "boolean", "default": true},
    {
      "name": "action", "label": "操作", "type": "select", "default": "unique",
      "options": [{"label": "去重", "value": "unique"}, {"label": "排序", "value": "sort"}]
    }
  ]
}
```

| 字段 | 说明 |
| --- | --- |
| `schema_version` | 固定为整数 `1`。 |
| `id` | 插件唯一标识，必须以小写英文字母开头，仅使用小写字母、数字、`-`、`_`，长度 2–64。更新必须保持相同 ID。 |
| `name` / `version` | 必填字符串，工具卡片上的名称和版本。本地导入允许手动更新到任意版本；市场版本需遵循 PEP 440，推荐 `1.0.0`，用于比较更新。 |
| `description` / `author` | 可选字符串。 |
| `entry` | 相对插件根目录的 `.py` 文件路径，通常为 `plugin.py`。 |
| `timeout` | 最长执行秒数，整数 1–86400，最高 24 小时，默认 60。超时会终止进程。长任务可设置 `"timeout": 86400`；已有插件未改配置时仍沿用原超时。 |
| `inputs` | 可省略或为空，最多 50 个输入字段。 |

输入字段的 `name` 是传入 Python 的参数键，使用英文字母、数字、下划线，建议字母开头，并保持唯一；`label` 为显示名称。支持 `text`、`textarea`、`password`、`email`、`url`、`tel`、`search`、`date`、`datetime-local`、`time`、`color`、`number`、`range`、`boolean`、`switch`、`select`、`radio`、`multiselect`；可以设置 `required`、`default`、`placeholder`、`help`。选择项用 `{ "label": "显示名", "value": "字符串值" }`，1–100 项，`value` 唯一。`multiselect` 的值为字符串数组；`boolean` 和 `switch` 为布尔值；`number` 和 `range` 为有限数值，支持 `min`、`max`、正数 `step`；其他类型为字符串。

必填文本/下拉值不能为空，必填多选至少一项；数字 `0` 和布尔值 `false` 是合法输入。可选字段可以省略；在 Python 内用 `params.get()` 设置业务默认值。文本最长 65,536 个字符。服务端校验参数类型、未知参数、选项取值和数值范围；其他业务规则由插件验证。

## 保存与恢复设置

表单参数保存到该插件目录的 `settings.json`，随 `/app/db` 持久卷保存；服务重启、插件更新后保留，卸载时删除。网页打开时读取，不会执行插件；输入定义更新后忽略已移除或不符合新类型的旧值。支持单独保存未填完的参数；运行时仍校验所有必填项。定时计划使用计划自身参数，执行时不覆盖表单设置。

读取失败或保存文件损坏时，界面提供「重新读取设置」；读取成功前运行不会自动覆盖旧设置，用户仍可单独保存或恢复默认。等待读取期间已编辑的字段保留，其他字段正常恢复。隐藏页签中的必填项校验失败时，运行按钮自动展开对应页签并定位输入。

`password` 只遮蔽界面显示，保存值仍为服务器上的明文 JSON，管理员可读取。插件自己在 `data_dir` 保存的加密凭据由插件管理；界面保存的是 `inputs` 对应参数。不得在日志或返回结果中输出密码。

## 自定义组件与布局

可选顶层 `ui` 用于布局表单和展示内容，兼容 `schema_version: 1`；没有 `ui` 的插件沿用普通表单。`layout` 为 `stack` 或 `grid`，`columns` 为 1–4，`width` 为 `normal`、`wide` 或 `full`。界面最多 200 个组件、嵌套最多 8 层，手机端网格自动转为单列。输入仍在 `inputs` 声明，通过 `field.name` 放置；未放置的输入自动追加到表单，不能重复引用同一个输入。

```json
"ui": {
  "width": "wide", "layout": "stack",
  "components": [
    {"type": "heading", "text": "任务配置"},
    {"type": "grid", "columns": 2, "children": [
      {"type": "field", "name": "text"},
      {"type": "field", "name": "action"}
    ]},
    {"type": "alert", "text": "先预览，再开始处理。", "style": {"tone": "warning"}},
    {"type": "button", "label": "去重文本", "action": "run", "params": {"action": "unique"}, "style": {"tone": "primary"}},
    {"type": "image", "src": "plugin://assets/example.png", "alt": "示例图片"}
  ]
}
```

上面是清单的字段片段；图片需放入插件包的 `assets/example.png`。组件如下：

| type | 主要字段与行为 |
| --- | --- |
| `field` | `name` 引用 inputs 中的输入。 |
| `group` / `card` / `grid` | `label`、`children`，grid 可设 `columns`。 |
| `tabs` | `children` 中每个 group/card 为一个页签，使用其 `label` 与 `children`。 |
| `heading` / `text` / `code` / `badge` / `alert` | `text`；code 保留换行。 |
| `markdown` | `text`，支持标题、列表、加粗、行内代码和链接，HTML 作为文本。 |
| `divider` | 分隔线。 |
| `image` | `src`、`alt`、`caption`。支持 HTTP(S)、PNG/JPEG/GIF/WebP/AVIF 的 base64 data URL、`plugin://包内路径`、`data://数据目录路径`。 |
| `link` | `href`、`label`，HTTP(S) 链接在新标签打开。 |
| `table` | `label`、`headers`、`rows`，最多 30 列、200 行；清单单元格用字符串。 |
| `progress` | `label`、`value`、`max`，0 ≤ value ≤ max。 |
| `button` | `label`，`action` 为 `run`、`save`、`reset`。run 的 `params` 覆盖已声明输入并调用同一入口，不新增服务端路由。 |

组件可设 `style`：`tone` 为 default/primary/success/warning/danger/muted，`align` 为 left/center/right，`size` 为 small/normal/large，`variant` 为 solid/outline/soft，`span` 为 1–4（限定在所在网格列数内）。使用主程序的主题色，不执行任意 HTML、JS 或 CSS。

`image.src` 也可直接使用 TMDB CDN（image.tmdb.org）等外部图片的完整 HTTPS URL。外部图片由浏览器直接加载，不要求图片服务开放 CORS；浏览器所在网络需能访问该地址。页面采用延迟加载，且不向图片服务发送页面 Referrer；外部链接推荐 HTTPS，以兼容 HTTPS 部署。

运行结果可返回 `{"ui": {"layout": "grid", "columns": 2, "components": [...]}, "其他结果": ...}`，或 `{"ui": [...]}`；使用同一组件协议展示图片、表格、卡片等，原始 JSON 仍可展开查看。结果中不放 field；按钮可调用 run/save/reset。生成图片先写入 `Path(context["data_dir"]) / "preview.png"`，再返回 `{"ui": [{"type": "image", "src": "data://preview.png", "alt": "处理结果"}]}`。图片接口需要登录或 Bearer，只读取对应插件内图片文件，拒绝路径逃逸。清单仍限 64 KiB，运行结果仍限 1 MiB。

## Python 入口

```python
from pathlib import Path

def run(params, context):
    text = params["text"]
    limit = params.get("limit", 100)
    if not isinstance(limit, int) or not 1 <= limit <= 10000:
        raise ValueError("最多行数必须是 1–10000 的整数")

    lines = text.splitlines()[:limit]
    if params.get("strip", True):
        lines = [line.strip() for line in lines]
    if params.get("action", "unique") == "unique":
        lines = list(dict.fromkeys(lines))
    else:
        lines = sorted(lines)

    # 数据目录可写，更新时保留。插件代码目录用于读取随包资源。
    output = "\n".join(lines)
    (Path(context["data_dir"]) / "last-result.txt").write_text(output, encoding="utf-8")
    print(f"处理完成，共 {len(lines)} 行")
    return {"text": output, "count": len(lines)}
```

- `run(params, context)` 是同步函数，每次运行都会启动新的 Python 进程，模块全局变量不会跨任务保留。
- `params` 为校验后的字典；`context["plugin_dir"]` 是当前版本代码的绝对目录，`context["data_dir"]` 是该插件持久数据的绝对目录。
- 返回值为字符串或可 JSON 序列化的对象，包括列表、字典、数字、布尔值和 `None`。不要返回文件对象、字节、`Path`、集合或无限数值。结果大小最多 1 MiB。
- `print()` 与标准错误流会显示为日志，两种日志各保留最多 64 KiB，超出会截断。抛出异常时任务失败，显示错误信息。
- 可以导入插件包中的模块，以及服务 Python 环境已经安装的依赖。系统不会执行 `pip install` 或安装 `requirements.txt`；建议优先使用标准库，额外依赖由管理员放入运行环境。
- 文件路径对应服务器或容器内部路径。需要访问宿主机文件时，应由管理员先挂载目录；浏览器电脑上的路径不等于服务器路径。
- 所有已登录 Web 管理用户共享插件目录和数据。插件没有独立的用户权限系统。

## 执行与持久化

插件安装在项目的 `db/toolbox/plugins/` 下。Docker 使用现有 `/app/db` 持久卷；保留该卷即可在重建容器后保留插件、启停状态和数据。不要直接修改安装目录里的版本和状态文件，通过界面更新插件。

卸载会先将插件移出列表，再清理代码与数据。若存储清理失败，页面会明确提示残留文件尚未清理，服务下次启动时自动重试；此时插件已不能再运行。

同一插件只能有一个未完成任务；默认最多两个任务同时执行，队列数量有上限，满额时界面会提示稍后重试。任务记录仅保存在当前服务进程内，重启后不保留；需要长期保存的结果应写入 `data_dir`。关闭弹窗不取消任务，再次打开同一插件可在当前页面继续查看；超时仍会终止任务。

插件可自行创建文件或启动外部程序，开发者应负责清理临时文件、设置网络请求超时、避免创建脱离父进程的后台服务。插件运行没有 CPU、内存或文件权限沙箱，不应作为多租户不可信代码执行平台。

## cron 定时执行

点击「我的插件」工具栏的「定时执行」，新增计划，选择已安装插件、填写名称（可选）、cron 表达式及插件运行参数。保存后从下一个匹配的分钟开始执行；支持预览时间、编辑、启用/停用、删除和查看最近任务结果。同一插件可以创建多个计划，总共最多 100 个。

使用 5 段 cron：`分 时 日 月 周`，不含秒，固定按北京时间 `Asia/Shanghai`（UTC+8）执行。支持 `*`、逗号列表、范围及 `/` 步长，月份和星期也可用英文简称；周日可以写 `0` 或 `7`。日与周都有限定时使用“或”关系；其中有通配符（包括 `*/n`）时按两个字段同时匹配。

| cron 示例 | 执行时间（北京时间） |
| --- | --- |
| `0 9 * * *` | 每天 09:00。 |
| `*/30 * * * *` | 每小时的第 0、30 分钟。 |
| `0 9 * * 1-5` | 周一至周五 09:00。 |
| `0 2 1 * *` | 每月 1 日 02:00。 |

定时执行由主服务发起，复用插件 `run(params, context)`、超时和任务队列，不需要在插件内编写定时循环，也不能在插件清单中添加 `cron` 字段来注册计划。上一轮仍在运行或排队、插件停用或队列已满时，跳过本次触发，不累积执行。停用/删除计划不会取消已经提交的任务；卸载插件同时删除该插件的计划。

计划及运行参数保存在 `db/toolbox/plugins/.schedules.json`，随 `/app/db` 持久卷保存。服务重启后自动恢复调度，离线期间错过的触发不补跑；同一分钟已触发的计划也不会因重启重复提交。插件更新保留计划；输入定义改变后可能需要重新编辑参数，每次触发都会按当前插件定义校验。最近任务结果仅在当前服务内存中可查询，重启后需保留的输出仍应由插件写入 `data_dir`。

## HTTP 接口

所有接口要求已登录 Web 会话或有效 OpenAPI Bearer Token。使用网页登录会话修改插件时，需携带请求头 `X-Toolbox-Request: 1`，不允许跨站调用；Bearer 调用无需该请求头。两种方式导入插件都必须提交 `trusted=true`。

浏览器同源请求通过反向代理改写 Host 或外部端口时，可根据浏览器的 `Sec-Fetch-Site: same-origin` 识别；不以代理后的内部地址误拦截。插件 API 响应设为不缓存，保存参数等私有内容不会作为可缓存响应返回。

| 方法与路径 | 用途 |
| --- | --- |
| `GET /api/toolbox/plugins` | 插件列表与限制参数。 |
| `POST /api/toolbox/plugins/import` | multipart 字段 `file`（支持格式的插件文件）、`trusted=true`；更新另传 `replace=true`。 |
| `PATCH /api/toolbox/plugins/<id>` | JSON `{ "enabled": true }`。 |
| `DELETE /api/toolbox/plugins/<id>` | 卸载代码和持久数据。 |
| `POST /api/toolbox/plugins/<id>/run` | JSON `{ "params": { ... } }`，返回任务及 HTTP 202。 |
| `GET /api/toolbox/plugins/<id>/settings` | 返回 `settings.params`、`saved_at`、`readable` 和输入更新提示；文件损坏时 readable 为 false。 |
| `PUT /api/toolbox/plugins/<id>/settings` | JSON `{ "params": { ... } }`，持久保存设置。 |
| `DELETE /api/toolbox/plugins/<id>/settings` | 清除保存值，恢复默认。 |
| `GET /api/toolbox/plugins/<id>/assets/<path>` | 当前插件包内图片。 |
| `GET /api/toolbox/plugins/<id>/files/<path>` | 插件 data_dir 中生成的图片。 |
| `GET /api/toolbox/plugins/jobs/<job_id>` | 查询任务，状态为 `queued`、`running`、`success`、`error` 或 `timeout`。 |
| `GET /api/toolbox/plugins/schedules` | 读取定时计划、下次执行时间和最近任务状态，时区固定为 `Asia/Shanghai`。 |
| `POST /api/toolbox/plugins/schedules` | 新增计划，JSON `{ "plugin_id": "text-helper", "name": "每天处理", "cron": "0 9 * * *", "enabled": true, "params": { "text": "示例" } }`，返回 HTTP 201。 |
| `POST /api/toolbox/plugins/schedules/preview` | JSON `{ "cron": "0 9 * * *" }`，预览接下来三次执行的 Unix 秒时间戳。 |
| `PUT /api/toolbox/plugins/schedules/<schedule_id>` | 更新计划，字段与新增相同。 |
| `PATCH /api/toolbox/plugins/schedules/<schedule_id>` | JSON `{ "enabled": false }`，启用或停用计划。 |
| `DELETE /api/toolbox/plugins/schedules/<schedule_id>` | 删除计划，不取消已提交任务。 |
| `GET /api/toolbox/plugins/example.zip` | 下载可直接导入的示例。 |
| `GET /api/toolbox/plugins/example.py` | 下载包含内嵌清单的单文件示例。 |
| `GET /api/toolbox/plugins/marketplace-guide` | 查看市场使用与发布说明。 |
| `GET /api/toolbox/plugins/development-guide` | 查看本说明。 |
| `GET /api/toolbox/plugins/ai-development-prompt` | 获取包含当前容器实际环境的 AI 开发提示词；本地预览显示镜像构建参考。 |

运行接口可传 `save_settings: true` 保存当前参数，网页默认传 true，其他 API 调用默认 false。跨站市场操作单独允许，详见市场说明。
