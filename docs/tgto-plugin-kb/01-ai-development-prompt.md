<!--
来源：TgtoDrive「实用工具 → 我的插件 → AI 开发提示词」一键复制内容
捕获时间：2026-10-13 20:01 (GMT+8)
环境来源标注：当前容器实际环境（非本地预览）
说明：以下正文由对话记录逐字保存，未做内容改动；此注释块仅为归档元信息，转发时可整段删除。
-->

请为我开发一个可直接导入 TgtoDrive（tgto123）「实用工具 → 我的插件」的 Python 插件。请严格遵循下面的实际运行环境与插件协议，交付完整可运行的文件，而不是只描述实现思路。最后的「我的插件需求」是本次要实现的功能；若我尚未填写，请先询问具体需求。

## 一、面向用户的容器运行环境

TgtoDrive 面向用户发布为 Linux 容器，正式镜像以 python:3.13-slim 为基础，支持 linux/amd64 与 linux/arm64。请按 Linux 容器开发插件，不要按浏览器所在电脑或开发者的本地系统编写。插件运行器使用容器服务的 sys.executable，为每次任务启动独立 Python 子进程，与服务共用容器内的已安装依赖，不创建虚拟环境。

正式容器内打开此提示词时，下方会实时读取该容器的 Python 完整版本、系统、CPU 架构、已安装依赖版本及常用命令可用性；不使用固定清单替代实际安装情况。若标注为“发布镜像构建参考”，表示来自本地开发预览，只反映构建配置；请在正式容器页面重新复制后再确定具体依赖版本。

环境来源：当前容器实际环境
Python：3.13.16
操作系统：Linux
CPU 架构：x86_64
容器命令检测（基于当前 PATH，不执行命令）：ffmpeg（可用）、ffprobe（可用）、node（可用）、curl（可用）、ping（可用）

当前容器已安装的 Python 分发包与版本（实时读取，不代表导入模块名）：

```text
aiohappyeyeballs==2.6.2
aiohttp==3.14.1
aiosignal==1.4.0
anyio==4.14.1
APScheduler==3.11.2
attrs==26.1.0
babelfish==0.6.1
bcrypt==5.0.0
beautifulsoup4==4.15.0
bencodepy==0.9.5
bilibili-api-python==17.4.2
bitarray==3.8.2
blinker==1.9.0
brotli==1.2.0
cachedict==0.0.7
certifi==2026.6.17
cffi==2.0.0
charset-normalizer==3.4.7
click==8.4.2
cn2an==0.5.24
colorama==0.4.6
cryptography==49.0.0
curl_cffi==0.15.0
dnspython==2.8.0
ed2k==0.0.2.2
emoji==2.15.0
errno2==0.0.5
filelock==3.29.4
Flask==3.1.3
frozenlist==1.8.0
glob_pattern==0.0.2
guessit==3.8.0
h11==0.16.0
h2==4.3.0
hpack==4.2.0
http_response==0.0.9
httpcore==1.0.9
httpcore_request==0.0.7.1
httpx==0.28.1
httpx_request==0.1.9.1
hyperframe==6.1.0
id2dirnode==0.0.2
idna==3.18
iniconfig==2.3.0
integer_tool==0.0.6.1
invoke==3.0.3
iter_collect==0.0.6
iterdir==0.0.10
itsdangerous==2.2.0
jh2==5.0.13
Jinja2==3.1.6
libarchive-c==5.3
lxml==6.1.1
markdown-it-py==4.2.0
MarkupSafe==3.0.3
mdurl==0.1.2
multidict==6.7.1
numpy==2.5.0
opencc-python-reimplemented==0.1.7
opencv-python-headless==4.13.0.92
opencv-python==4.13.0.92
orjson==3.11.9
p115cipher==0.0.5.2
p115client==0.0.9.0.2
p115oss==0.1.0.2
p115pickcode==0.0.5.4
p123client==0.0.9.3.1
packaging==26.3
paramiko==5.0.0
pillow==12.2.0
pip==26.2.1
pluggy==1.6.0
posixpatht==0.0.4
proces==0.1.7
propcache==0.5.2
pyaes==1.6.1
pyasn1==0.6.3
pycparser==3.0
pycryptodome==3.23.0
pycryptodomex==3.23.0
Pygments==2.20.0
PyJWT==2.13.0
pymongo==4.17.0
PyMySQL==1.2.0
PyNaCl==1.6.2
PySocks==1.7.1
pyTelegramBotAPI==4.34.0
pytest==9.1.1
python-argtools==0.0.3
python-asynctools==0.1.3.4
python-concurrenttools==0.1.4
python-cookietools==0.1.5
python-dateutil==2.9.0.post0
python-decotools==0.0.4
python-dictattr==0.0.4
python-dicttools==0.0.5
python-dotenv==1.2.2
python-download==0.0.4.1
python-encode_uri==0.0.3
python-ensure==0.0.2
python-filewrap==0.3.0
python-hashtools==0.0.6
python-http_request==0.1.7.1
python-httpfile==0.0.6
python-iterutils==0.2.10.2
python-property==0.0.3
python-socks==2.8.2
python-startfile==0.0.3
python-temporary==0.0.1
python-texttools==0.0.6
python-undefined==0.0.4
PyYAML==6.0.3
qh3==1.9.2
qrcode-terminal==0.8
qrcode==8.2
rebulk==3.2.0
regex==2026.5.9
requests==2.34.2
rich==15.0.0
rsa==4.9.1
schedule==1.2.2
six==1.17.0
socket_keepalive==0.0.1
soupsieve==2.8.4
sqlitetools==0.0.8.1
Telethon==1.44.0
tqdm==4.68.3
typing_extensions==4.15.0
tzdata==2026.2
tzlocal==5.4.3
urllib3-future==2.21.902
urllib3==2.7.0
urllib3_future_request==0.0.2
wcwidth==0.8.1
Werkzeug==3.1.8
yarl==1.24.2
zstandard==0.25.0
```

- 上面的名称是 Python 分发包名，不一定是 import 名。例如 beautifulsoup4 → bs4、pillow → PIL、opencv-python / opencv-python-headless → cv2、pytelegrambotapi → telebot、python-dotenv → dotenv、pycryptodome → Crypto、opencc-python-reimplemented → opencc、dnspython → dns。不要把带连字符的包名直接写进 import；不确定的 API 请核实该版本文档，不要编造。
- 优先使用标准库与容器中已安装的依赖。系统不会安装插件附带的 requirements.txt，也不要在插件中执行 pip install、创建虚拟环境或修改项目依赖。确需额外库时，先说明并提供使用现有依赖的方案；建议管理员通过基于官方镜像的定制镜像预先安装，避免容器重建后丢失临时安装的依赖。
- 文件路径必须使用容器内的 Linux 路径。宿主机文件必须先挂载，例如宿主机目录挂载到 /media 后，插件使用 /media；不能直接使用 Windows 盘符、NAS 宿主路径或浏览器电脑上的路径。使用 pathlib，不要依赖 PowerShell、Windows 注册表、COM 或桌面 GUI。
- 应用位于 /app，插件通常位于 /app/db/toolbox/plugins。/app/db 应挂载持久卷；插件自己的持久文件仍应通过 context["data_dir"] 定位，不要硬编码版本目录。/app/strm、/app/upload 等目录只有在用户实际挂载且授权时才可用于对应任务，不要假设存在或自动创建宿主机挂载。
- 网络地址取决于容器网络模式：bridge 模式中 localhost / 127.0.0.1 指向容器自身；Linux host 模式与宿主机共享网络，本项目部署示例使用 host 模式。调用宿主机或其他容器服务时，按用户实际网络配置选择可达地址，不要仅凭容器部署就推断 localhost 的目标。
- 插件有当前服务账户的文件、环境变量与网络权限，子进程不是权限沙箱。不要读取或输出与需求无关的账号配置、Cookie、Token、密钥；不要要求用户提供整个 sys.env 配置文件或完整环境变量。需要配置时只请求完成任务所需的信息。
- 正式镜像内的主程序使用受保护的 .pyc / .so，源码不可供插件依赖。内部模块不是稳定的插件 SDK；不要导入 server、tgto123 或启动主服务，不要依赖项目内部函数、数据库表结构和 Flask 请求上下文。外部服务使用明确的 API 与用户提供的配置。
- 官方镜像构建时安装 ffmpeg、Node.js、curl、ping 和 CA 证书，实际命令可用性以上方容器检测为准。使用前仍可通过 shutil.which() 检查，并在必要时查询具体版本；不要假设有编译工具、桌面浏览器、GPU 或额外字体。使用原生扩展或二进制资源时需兼容用户容器的 CPU 架构。

## 二、插件包格式

可以交付一个 `.py` 单文件，或按以下结构交付压缩包。当前运行环境实际可导入的格式：.py、.zip、.pyz、.tar、.tar.gz、.tgz、.tar.bz2、.tbz2、.tbz、.tar.xz、.txz、.7z、.rar。当前不可用的格式：无。Python 代码、JSON 和文档使用 UTF-8 编码，资源文件可为二进制。

系统支持 `.py`、`.zip`、`.pyz`、`.tar`、`.tar.gz` / `.tgz`、`.tar.bz2` / `.tbz2` / `.tbz`、`.tar.xz` / `.txz`、`.7z`、`.rar`。7z/RAR 依赖系统 libarchive 和 libarchive-c，以上方实时可用格式为准；加密、分卷及解码器不支持的压缩方式不可用。`.pyz` 必须是本项目规定结构的 ZIP 插件包，并不是任意 zipapp。

单文件插件：顶层必须且只能有一次 `PLUGIN_MANIFEST = {...}` 字典字面量赋值（允许类型注解），字段与下面的 plugin.json 相同，省略 entry 或写 plugin.py，系统固定保存为 plugin.py。Python 中使用 True/False/None，不能写 JSON 的 true/false/null。系统通过 AST 静态读取清单，不执行脚本；不要用函数、变量、环境读取或表达式生成清单。还必须有唯一同步 `def run(params, context)`，支持传入两个位置实参。无需写前端代码，界面由同一清单自动生成。只有一个脚本时优先交付 `.py`；需要辅助模块或资源时交付压缩包。

压缩包根目录至少包含：

```text
my-plugin.zip
├── plugin.json
├── plugin.py
└── README.md
```

可以包含辅助 Python 模块、子目录与资源；也允许外面再包一层目录，但建议直接以这三个文件为根目录。上传文件最多 10 MiB、500 个文件或目录，解压后总大小最多 50 MiB。路径必须使用相对路径和正斜杠，不得有绝对路径、反斜杠、..、软硬链接、特殊文件、Windows 保留名、重复路径或仅大小写不同的路径。不要打包虚拟环境、__pycache__、安装目录、真实凭据或临时文件。

plugin.json 是普通 JSON，不能包含注释，文件最大 65,536 字节：

- schema_version：整数 1。
- id：匹配 ^[a-z][a-z0-9_-]{1,63}$，并避开 Windows 保留名。更新插件时保持同一 id。
- name：必填非空字符串，最多 100 字符；version：必填非空字符串，最多 50 字符。
- description：可选，最多 4000 字符；author：可选，最多 100 字符。
- entry：包内 .py 文件的相对路径，推荐 plugin.py，文件必须存在。
- timeout：整数秒，1–86400，默认 60，最高 24 小时。例如长任务可写 "timeout": 86400；省略时仍然只有 60 秒，提升上限不会自动延长已有插件。根据实际工作量选择，并为网络请求单独设置更短的超时。
- inputs：可选数组，最多 50 项。应用依据它生成参数表单；可通过 ui 字段指定布局和组件，无需编写 HTML/JavaScript 页面。
- ui：可选声明式界面配置，见下方组件协议。

每个 inputs 项支持：

- name：唯一参数键，匹配 ^[A-Za-z_][A-Za-z0-9_]{0,63}$。
- label：显示名称，非空字符串，最多 100 字符。
- type：支持 text、textarea、password、email、url、tel、search、date、datetime-local、time、color、number、range、boolean、switch、select、radio、multiselect。路径使用 text，复杂配置可使用 textarea 并在 Python 中解析、校验；尚无 file 类型。
- required：布尔值，默认 false。必填文本/单选值不能为空，必填多选至少一项；number/range 的 0 与 boolean/switch 的 false 均有效，不要把 required 布尔参数理解为必须勾选。
- default：可选，必须符合对应类型。number/range 是有限数值且不能是布尔值；boolean/switch 是 JSON true/false；multiselect 是不重复的字符串数组；其他类型为字符串。
- 网页 number 使用 JavaScript 数值；整数只能在 ±9,007,199,254,740,991 范围内精确表示。目录 ID、文件 ID 和其他需要保留每一位的大整数必须使用 text 参数，代码中按需转换为 Python int；返回给网页的此类 ID 也必须转成字符串，避免 JSON 数字显示时丢失精度。
- placeholder：可选字符串，最多 500 字符；help：参数说明，最多 2000 字符。
- number/range 可设置 min/max（有限数值）和 step（正有限数值），服务端校验 min/max；更细的数值、时间或路径业务规则由插件实现。
- select/radio/multiselect 必须有 options，1–100 项，每项是 {"label": "显示名", "value": "字符串值"}；value 必须唯一，最多 500 字符，label 最多 100 字符。select/radio 的 default 必须是某个 option.value；multiselect 的 default 为选项值数组。

不要添加协议没有实现的正则校验、任意 HTML/JS/CSS、自定义路由、cron、schedule 或权限声明字段。整数要求、路径存在性等业务校验由 run 函数实现；单次超过 24 小时的工作应设计为可分批或可续跑任务。定时计划由用户在主程序的“我的插件 → 定时执行”中配置，不能在 plugin.json 或 PLUGIN_MANIFEST 里声明自动运行。

## 保存与恢复设置

表单参数保存到该插件目录的 `settings.json`，随 `/app/db` 持久卷保存；服务重启、插件更新后保留，卸载时删除。网页打开时读取，不会执行插件；输入定义更新后忽略已移除或不符合新类型的旧值。支持单独保存未填完的参数；运行时仍校验所有必填项。定时计划使用计划自身参数，执行时不覆盖表单设置。

读取失败或保存文件损坏时，界面提供「重新读取设置」；读取成功前运行不会自动覆盖旧设置，用户仍可单独保存或恢复默认。等待读取期间已编辑的字段保留，其他字段正常恢复。隐藏页签中的必填项校验失败时，运行按钮自动展开对应页签并定位输入。

`password` 只遮蔽界面显示，保存值仍为服务器上的明文 JSON，管理员可读取。插件自己在 `data_dir` 保存的加密凭据由插件管理；界面保存的是 `inputs` 对应参数。不得在日志或返回结果中输出密码。

## 自定义组件与布局

可选顶层 `ui` 用于布局表单和展示内容，兼容 `schema_version: 1`；没有 `ui` 的插件沿用普通表单。`layout` 为 `stack` 或 `grid`，`columns` 为 1–4，`width` 为 `normal`、`wide` 或 `full`。界面最多 200 个组件、嵌套最多 8 层，手机端网格自动转为单列。输入仍在 `inputs` 声明，通过 `field.name` 放置；未放置的输入自动追加到表单，不能重复引用同一个输入。

```text
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

图片支持 TMDB CDN（image.tmdb.org）等外部服务：将实际完整 HTTPS 图片 URL 填入 image.src，或在运行结果的 ui 中返回。外部图片由浏览器直接加载，无需图片服务开放 CORS，浏览器网络需可达。不要编造真实图片路径，也不要将私有 Token 放进图片 URL；需要服务端凭据的图片由插件下载到 data_dir 后用 data:// 展示。

运行结果可返回 `{"ui": {"layout": "grid", "columns": 2, "components": [...]}, "其他结果": ...}`，或 `{"ui": [...]}`；使用同一组件协议展示图片、表格、卡片等，原始 JSON 仍可展开查看。结果中不放 field；按钮可调用 run/save/reset。生成图片先写入 `Path(context["data_dir"]) / "preview.png"`，再返回 `{"ui": [{"type": "image", "src": "data://preview.png", "alt": "处理结果"}]}`。图片接口需要登录或 Bearer，只读取对应插件内图片文件，拒绝路径逃逸。清单仍限 64 KiB，运行结果仍限 1 MiB。

## 三、Python 执行协议

入口必须提供同步函数 def run(params, context)。异步库可在同步入口里通过 asyncio.run() 调用；不要直接把 run 声明为 async def，也不要返回生成器或协程。

- params 是字典，只包含清单声明的参数。缺失字段会应用 default；没有默认值的可选字段可能不在字典中。可选文本也可能从页面传来空字符串，布尔值始终按布尔值处理，注意区分“缺失”“空字符串”“0”“false”。单个文本最多 65,536 字符，全部参数 JSON 最多 256 KiB。
- context 只有 plugin_dir、data_dir 两个键，都是绝对路径字符串。plugin_dir 为当前版本的代码/资源目录，也是执行时工作目录；插件根目录和入口文件所在目录均加入 sys.path，可导入辅助模块。用 pathlib.Path(context["plugin_dir"]) 读取资源。
- data_dir 是已创建的持久数据目录。把配置、缓存、输出写到 pathlib.Path(context["data_dir"])；子目录需自行创建。更新保留此目录，卸载会删除。不要把需保留的数据写进 plugin_dir；更新会替换代码目录。
- 每次运行是新进程，全局变量不跨任务保留。同一插件只能有一个未完成任务；服务最多同时执行两个插件任务。主程序支持 cron 定时触发插件的同一个 run(params, context)，插件自身不能注册常驻服务、守护线程或后台定时循环；执行结束/超时会清理子进程。不要在模块导入阶段做网络请求、写文件或其他业务操作，应放在 run 内。
- 返回字符串或可 JSON 序列化的字典、列表、数值、布尔值、None；不要返回 Path、bytes、文件句柄、set、NaN、Infinity。序列化结果连同运行器包装最多 1 MiB，结果尽量精简；大结果保存到 data_dir，返回摘要与服务器路径。页面不会把任意服务器路径变成下载链接；图片可用 ui 组件的 data:// 路径展示。返回的 HTML 不会执行。
- print() 是运行日志，标准输出与错误输出各最多保留 64 KiB，超过截断。失败时抛出带可理解信息的 ValueError/RuntimeError 等异常；不要把实际失败包装成成功结果。
- 关闭弹窗不会取消任务；超过 timeout 会终止。当前服务内存里的任务记录会在重启后清空，需保留的结果写入 data_dir。

定时执行约定：

- 用户通过“我的插件”工具栏的“定时执行”新增计划，选择已安装插件，填写插件 inputs 对应的运行参数，设置 cron 表达式，并可预览接下来三次执行时间。可以为同一插件创建多个计划，最多 100 个计划。
- cron 使用 5 段“分 时 日 月 周”，不含秒，固定北京时间 Asia/Shanghai（UTC+8）。支持 *、逗号列表、范围和 / 步长；月和星期可用英文简称，周日可用 0 或 7。日与周都有限定时使用或关系，含通配符时按各字段同时匹配。例如 0 9 * * * 每天 09:00，*/30 * * * * 每 30 分钟，0 9 * * 1-5 工作日 09:00。
- 定时执行复用插件 timeout 和任务队列。上一轮仍在运行或排队、插件停用或队列已满时，本次触发跳过，不累积补跑。停用/删除计划不取消已提交的任务；卸载插件会移除该插件的计划。
- 计划与运行参数保存在 db/toolbox/plugins/.schedules.json，Docker 随 /app/db 持久卷保存。服务启动后自动恢复调度；离线期间的错过时间不补跑，计划保存或重新启用后从下一个匹配分钟开始。插件更新保留计划，但输入定义变更后需用户重新编辑参数；每次触发仍进行参数校验。
- 交付有定时需求的插件时，请提供推荐 cron 表达式、运行参数和 timeout 配置示例，让用户在定时执行界面设置。插件入口完成一次工作即可返回，不要用 sleep 等待下次执行，也不要自动创建或启用用户的定时计划。
- 不使用 input()、交互终端、GUI、Flask session/request；所有输入都通过 params，所有输出通过返回值和日志。文件操作要兼容当前系统；涉及删除/覆盖的插件应先提供预览参数，并验证用户给出的目标路径，不要默认递归扫描或删除整个服务器。

## 四、可以直接导入的完整参考

这是文本按行去重/排序的参考插件，演示参数、日志与持久化。请根据我的需求改写，保留协议结构，不要只原样返回示例。

plugin.json：

```json
{
  "schema_version": 1,
  "id": "text-helper",
  "name": "文本处理示例",
  "version": "1.0.0",
  "description": "按行去重或排序文本，演示参数、运行日志和插件数据保存。",
  "author": "TgtoDrive",
  "entry": "plugin.py",
  "timeout": 30,
  "inputs": [
    {
      "name": "text",
      "label": "待处理文本",
      "type": "textarea",
      "required": true,
      "default": "苹果\n香蕉\n苹果",
      "placeholder": "每行一项"
    },
    {
      "name": "action",
      "label": "处理方式",
      "type": "select",
      "default": "unique",
      "options": [
        {
          "label": "去重（保留顺序）",
          "value": "unique"
        },
        {
          "label": "排序",
          "value": "sort"
        }
      ]
    },
    {
      "name": "strip",
      "label": "清理每行首尾空白",
      "type": "boolean",
      "default": true
    }
  ]
}
```

plugin.py：

```python
"""TgtoDrive Python 插件：只使用 Python 标准库。"""
import json
from pathlib import Path


def run(params, context):
    lines = params["text"].splitlines()
    if params.get("strip", True):
        lines = [line.strip() for line in lines]
    original_count = len(lines)
    if params.get("action", "unique") == "unique":
        lines = list(dict.fromkeys(lines))
    else:
        lines = sorted(lines)

    # 写到 data_dir 的数据会在更新插件后保留；卸载时删除。
    stats_file = Path(context["data_dir"]) / "stats.json"
    try:
        count = int(json.loads(stats_file.read_text(encoding="utf-8"))["runs"])
    except (OSError, ValueError, KeyError, TypeError):
        count = 0
    stats_file.write_text(json.dumps({"runs": count + 1}), encoding="utf-8")
    print(f"已处理 {original_count} 行，输出 {len(lines)} 行")
    return {
        "output": "\n".join(lines),
        "input_lines": original_count,
        "output_lines": len(lines),
        "runs": count + 1,
    }
```

如果交付单 `.py` 文件，将清单和入口合并为下列形式，不需要另附 plugin.json：

```python
# -*- coding: utf-8 -*-
PLUGIN_MANIFEST = {'schema_version': 1,
 'id': 'text-helper',
 'name': '文本处理示例',
 'version': '1.0.0',
 'description': '按行去重或排序文本，演示参数、运行日志和插件数据保存。',
 'author': 'TgtoDrive',
 'timeout': 30,
 'inputs': [{'name': 'text',
             'label': '待处理文本',
             'type': 'textarea',
             'required': True,
             'default': '苹果\n香蕉\n苹果',
             'placeholder': '每行一项'},
            {'name': 'action',
             'label': '处理方式',
             'type': 'select',
             'default': 'unique',
             'options': [{'label': '去重（保留顺序）', 'value': 'unique'},
                         {'label': '排序', 'value': 'sort'}]},
            {'name': 'strip', 'label': '清理每行首尾空白', 'type': 'boolean', 'default': True}]}

"""TgtoDrive Python 插件：只使用 Python 标准库。"""
import json
from pathlib import Path


def run(params, context):
    lines = params["text"].splitlines()
    if params.get("strip", True):
        lines = [line.strip() for line in lines]
    original_count = len(lines)
    if params.get("action", "unique") == "unique":
        lines = list(dict.fromkeys(lines))
    else:
        lines = sorted(lines)

    # 写到 data_dir 的数据会在更新插件后保留；卸载时删除。
    stats_file = Path(context["data_dir"]) / "stats.json"
    try:
        count = int(json.loads(stats_file.read_text(encoding="utf-8"))["runs"])
    except (OSError, ValueError, KeyError, TypeError):
        count = 0
    stats_file.write_text(json.dumps({"runs": count + 1}), encoding="utf-8")
    print(f"已处理 {original_count} 行，输出 {len(lines)} 行")
    return {
        "output": "\n".join(lines),
        "input_lines": original_count,
        "output_lines": len(lines),
        "runs": count + 1,
    }
```

## 五、通过 OpenAPI 调用项目功能

项目提供 OpenAPI 3.0.3 接口文档，在「实用工具 → OpenAPI」弹窗中查看并下载；也可使用 Bearer Token 请求 GET /api/openapi/spec。接口沿用网页的 /api/... 路径，不要编造 /openapi/v1 等前缀。详细参数以该容器导出的规范和接口实际校验为准；标注 inferred 的字段来自静态分析，并不保证包含全部必填条件，generic 表示没有细化模型，documented 表示请求字段已核对。插件运行接口的 params 对象须按目标插件 inputs 填写，不能将示例的空对象用于有必填参数的插件。若需要的字段不明确，请让我提供对应接口定义，不要猜测。网页登录、退出和 OpenAPI 凭据管理仅允许网页登录会话。

当前服务已公开的接口索引（完整参数请下载 OpenAPI 规范）：

```text
POST /api/115-self-share-strm/run — 扫描 115 转存目录并生成自建分享
GET /api/115-share-strm-invalid-cleaner/config — 读取 115 分享 STRM 清理配置
POST /api/115-share-strm-invalid-cleaner/config — 保存 115 分享 STRM 清理配置
GET /api/115-share-strm-invalid-cleaner/fs/list — 浏览 STRM 清理扫描目录
GET /api/115-share-strm-invalid-cleaner/history — 查询 STRM 失效检测历史
GET /api/115-share-strm-invalid-cleaner/history-detail — 查询 STRM 检测历史详情
POST /api/115-share-strm-invalid-cleaner/run — 启动 115 分享 STRM 失效检测
POST /api/115-share-strm-invalid-cleaner/stop — 停止 STRM 失效检测任务
GET /api/115-share-strm-invalid-cleaner/task-status — 查询 STRM 失效检测进度
POST /api/115/qr/login — 完成 115 扫码登录
GET /api/115/qr/status — 查询 115 扫码登录状态
GET /api/115/qr/token — 获取 115 登录二维码凭据
POST /api/123/login/send-code — 发送 123 云盘登录验证码
GET /api/123/login/status — 查询 123 云盘登录状态
POST /api/123/login/verify-code — 完成 123 云盘短信登录
POST /api/189/qr/cancel — 取消天翼云盘扫码登录
POST /api/189/qr/start — 创建天翼云盘登录二维码
POST /api/189/qr/status — 查询天翼云盘扫码登录结果
POST /api/ai-media-parser/cache/clear — 清空 AI 媒体识别缓存
GET /api/ai-media-parser/config — 读取 AI 媒体识别配置
POST /api/ai-media-parser/config — 保存 AI 媒体识别配置
POST /api/ai-media-parser/test-connection — 测试 AI 识别服务连接
GET /api/bot-commands — 读取 Telegram 机器人命令
POST /api/bot-commands — 保存 Telegram 机器人命令
GET /api/directory-selector/list — 浏览网盘子目录
GET /api/directory-selector/resolve — 解析网盘目录名称和路径
POST /api/emby-cover-generator/config — 保存媒体库封面生成设置
POST /api/emby-cover-generator/generate — 启动 Emby 媒体库封面生成
GET /api/emby-cover-generator/libraries — 获取封面生成用媒体库
GET /api/emby-cover-generator/task-status — 查询媒体库封面生成进度
POST /api/emby-metadata-cleaner/clean — 清理 Emby 残余元数据
GET /api/emby-metadata-cleaner/fs/list — 浏览元数据清理目录
POST /api/emby-metadata-cleaner/pick-folder — 打开服务器本地目录选择器
POST /api/emby-metadata-cleaner/preview — 预览 Emby 残余元数据
GET /api/emby/config — 读取 Emby 看板运行配置
GET /api/emby/continue — 查询 Emby 继续观看列表
GET /api/emby/dashboard — 获取 Emby 看板统计
GET /api/emby/dashboard_config — 读取 Emby 看板专用设置
POST /api/emby/dashboard_config/clear — 清除 Emby 看板连接设置
POST /api/emby/dashboard_config/save — 保存 Emby 看板连接设置
POST /api/emby/dashboard_config/test — 测试 Emby 看板连接
GET /api/emby/image/{item_id}/primary — 获取 Emby 主海报图片
GET /api/emby/latest — 查询 Emby 最近入库媒体
GET /api/emby/libraries — 查询 Emby 媒体库统计
GET /api/emby/live — 查询 Emby 正在播放的会话
GET /api/emby/recent — 查询 Emby 最近播放记录
POST /api/emby/refresh_cache — 刷新 Emby 看板缓存
GET /api/emby/top_users_list — 查询 Emby 活跃用户排行
GET /api/emby/trend — 查询 Emby 播放趋势
GET /api/emby/users — 获取 Emby 用户列表
POST /api/emby/webhook/deep_delete — 接收 Emby 媒体深度删除通知
GET /api/emby/webhook/deep_delete_info — 读取 Emby 深度删除回调配置
GET /api/emby_proxy/config — 读取 Emby 反向代理规则
POST /api/emby_proxy/config/clear — 清空 Emby 反向代理规则
POST /api/emby_proxy/config/delete_one — 删除一条 Emby 反向代理规则
POST /api/emby_proxy/config/save — 保存全部 Emby 反向代理规则
POST /api/emby_proxy/config/save_one — 新增或更新 Emby 代理规则
POST /api/emby_proxy/config/test — 测试 Emby 代理目标连接
POST /api/emby_proxy/config/toggle — 切换 Emby 代理规则启停
GET /api/emby_proxy/invites — 查询 Emby 邀请记录
POST /api/emby_proxy/invites/create — 创建 Emby 注册邀请
GET /api/emby_proxy/invites/libraries — 获取邀请可授权的媒体库
POST /api/emby_proxy/invites/renew — 续期 Emby 邀请关联用户
POST /api/emby_proxy/invites/revoke — 撤销 Emby 注册邀请
GET /api/emby_proxy/playback_records — 查询 Emby 代理播放记录
GET /api/env — 读取项目配置项
POST /api/env — 保存项目配置并触发重启
POST /api/guangya/gcid-export — 生成光鸭目录秒传 JSON
POST /api/guangya/login/send-code — 发送光鸭主账号登录验证码
POST /api/guangya/login/verify-code — 完成光鸭主账号短信登录
POST /api/guangya/media-probe-account/login/send-code — 发送光鸭媒体信息小号验证码
POST /api/guangya/media-probe-account/login/verify-code — 登录光鸭媒体信息小号
GET /api/guangya/media-probe-account/status — 查询光鸭媒体信息小号状态
POST /api/guangya/media-probe-account/token/clear — 清除光鸭媒体信息小号凭据
POST /api/guangya/media-probe-account/token/refresh — 刷新光鸭媒体信息小号凭据
POST /api/guangya/media-probe-account/token/validate — 校验光鸭媒体信息小号凭据
POST /api/guangya/token/clear — 清除光鸭主账号凭据
POST /api/guangya/token/refresh — 刷新光鸭主账号凭据
GET /api/guangya/token/status — 查询光鸭云盘登录状态
POST /api/guangya/token/validate — 校验光鸭主账号凭据
GET /api/logs — 读取项目运行日志
GET /api/logs/download — 下载项目日志文件
GET /api/media/actors — 浏览热门演员
GET /api/media/actors/{actor_id}/works — 查询演员作品
GET /api/media/anime/{source} — 浏览动漫内容
GET /api/media/calendar — 查询追剧日历
GET /api/media/capabilities — 查询影视资源功能能力
GET /api/media/details/{source}/{entity_type}/{external_id} — 查询影视或演员详情
GET /api/media/details/tmdb/tv/{external_id}/season/{season_number} — 查询电视剧某季的集数详情
GET /api/media/discover/{source} — 浏览影视片库
POST /api/media/emby/cards — 查询影视条目的 Emby 入库状态
POST /api/media/emby/test — 测试影视发现的 Emby 连接
POST /api/media/emby/tv-progress/preheat — 预热电视剧观看进度元数据
POST /api/media/guanying/captcha — 获取观影登录验证码
POST /api/media/guanying/captcha/verify — 提交观影验证码结果
POST /api/media/guanying/login — 登录观影资源服务
POST /api/media/guanying/relogin — 恢复观影登录状态
DELETE /api/media/guanying/session — 清除观影登录状态
POST /api/media/guanying/test — 测试观影登录是否有效
GET /api/media/providers — 获取影视来源与转存目标
GET /api/media/rankings/{provider} — 查询影视榜单
POST /api/media/resources/copy-link — 获取影视资源分享链接
POST /api/media/resources/offline — 提交影视资源离线下载
POST /api/media/resources/search — 检索影视可用资源
POST /api/media/resources/transfer — 将影视资源转存到网盘
GET /api/media/search — 搜索影视和演员资料
GET /api/media/settings — 读取影视发现基础配置
PUT /api/media/settings — 保存影视发现基础配置
POST /api/music-organize/stop — 停止音乐整理任务
GET /api/notify-bots — 读取 Telegram 通知机器人配置
POST /api/notify-bots — 保存 Telegram 通知机器人配置
GET /api/openapi/spec — 获取当前服务 OpenAPI 规范
GET /api/organize-history — 查询网盘整理历史
POST /api/organize-history/clear — 清空整理历史记录
POST /api/organize-history/delete — 删除整理记录关联的文件
GET /api/organize-history/delete-task-status — 查询整理文件删除任务进度
GET /api/organize-history/detail — 查询一条整理记录详情
POST /api/organize-history/recognize-test — 测试文件名的 TMDB 识别
POST /api/organize-history/reorganize — 重新整理或回退媒体改名
GET /api/organize-history/reorganize-task-status — 查询重新整理或改名回退进度
POST /api/organize-history/run — 立即运行网盘整理
GET /api/pikpak/captcha/callback/{state} — 接收 PikPak 验证码回调
GET /api/pikpak/captcha/status — 查询 PikPak 验证码处理状态
POST /api/pikpak/login — 登录 PikPak 云盘
POST /api/pikpak/token/clear — 清除 PikPak 登录凭据
POST /api/pikpak/token/refresh — 刷新 PikPak 登录凭据
GET /api/pikpak/token/status — 查询 PikPak 登录状态
POST /api/pikpak/token/validate — 校验 PikPak 登录凭据
GET /api/proxy/image/{item_id}/primary — 获取 Emby 海报图片（兼容入口）
GET /api/proxy_settings — 读取全局代理和机器人设置
POST /api/proxy_settings/save — 保存全局代理和机器人设置
POST /api/proxy_settings/test — 测试网络代理连通性
POST /api/proxy_settings/test_tg — 发送 Telegram 机器人测试消息
GET /api/pttransfer/records — 查询 PT 转存记录
DELETE /api/re0/authorization — 清除 RE0 主账号授权
GET /api/re0/authorize — 打开 RE0 主账号授权流程
GET /api/re0/checkin/config — 读取 RE0 自动签到配置
PUT /api/re0/checkin/config — 保存 RE0 自动签到配置
GET /api/re0/status — 查询 RE0 主账号授权状态
POST /api/re0/subaccounts — 新增 RE0 小号配置
GET /api/re0/subaccounts — 查询 RE0 小号列表
DELETE /api/re0/subaccounts/{account_id} — 删除 RE0 小号
PATCH /api/re0/subaccounts/{account_id} — 更新 RE0 小号配置
POST /api/re0/subaccounts/{account_id} — 更新 RE0 小号配置（POST 入口）
DELETE /api/re0/subaccounts/{account_id}/authorization — 清除 RE0 小号授权
GET /api/re0/subaccounts/{account_id}/authorize — 打开 RE0 小号授权流程
POST /api/save_json — 将 JSON 文件清单导入指定网盘目录
POST /api/ssh/connect — 建立 SSH 终端连接
POST /api/ssh/input — 向 SSH 终端发送输入
GET /api/ssh/output — 读取 SSH 终端输出
GET /api/stats/continue — 查询继续观看列表（兼容入口）
GET /api/stats/dashboard — 查询看板统计（兼容入口）
GET /api/stats/latest — 查询最近入库媒体（兼容入口）
GET /api/stats/libraries — 查询媒体库统计（兼容入口）
GET /api/stats/live — 查询正在播放会话（兼容入口）
GET /api/stats/recent — 查询最近播放记录（兼容入口）
GET /api/stats/top_users_list — 查询活跃用户排行（兼容入口）
GET /api/stats/trend — 查询播放趋势（兼容入口）
POST /api/strm-sync/run — 立即同步网盘 STRM
POST /api/tg-transfer/test — 测试 Telegram 最新消息转发
GET /api/tmdb-regex-rules/config — 读取 TMDB 正则识别规则
POST /api/tmdb-regex-rules/config — 保存 TMDB 正则识别规则
GET /api/tmdb-regex-rules/search-tmdb — 为正则规则搜索 TMDB 内容
GET /api/toolbox/123-api-rate-limit/config — 读取 123 云盘 API 限速配置
POST /api/toolbox/123-api-rate-limit/config — 保存 123 云盘 API 限速配置
GET /api/toolbox/custom-release-groups/config — 读取自定义发布组配置
POST /api/toolbox/custom-release-groups/config — 保存自定义发布组规则
GET /api/toolbox/marketplace — 浏览 GitHub 插件市场
POST /api/toolbox/marketplace/install — 安装或更新市场插件
POST /api/toolbox/marketplace/refresh — 刷新 GitHub 插件市场目录
PUT /api/toolbox/marketplace/source — 配置 GitHub 插件市场来源
POST /api/toolbox/marketplace/sources — 添加插件市场来源
DELETE /api/toolbox/marketplace/sources/{source_id} — 移除指定市场来源
PUT /api/toolbox/marketplace/sources/{source_id} — 编辑指定市场来源
GET /api/toolbox/plugins — 查询已安装插件和导入能力
DELETE /api/toolbox/plugins/{plugin_id} — 卸载 Python 插件
PATCH /api/toolbox/plugins/{plugin_id} — 启用或停用 Python 插件
GET /api/toolbox/plugins/{plugin_id}/assets/{filename} — 读取插件包内图片
GET /api/toolbox/plugins/{plugin_id}/files/{filename} — 读取插件生成的图片
POST /api/toolbox/plugins/{plugin_id}/run — 提交 Python 插件运行任务
GET /api/toolbox/plugins/{plugin_id}/settings — 读取插件已保存设置
DELETE /api/toolbox/plugins/{plugin_id}/settings — 清除插件已保存设置
PUT /api/toolbox/plugins/{plugin_id}/settings — 保存插件表单设置
GET /api/toolbox/plugins/ai-development-prompt — 获取插件 AI 开发提示词
GET /api/toolbox/plugins/development-guide — 获取插件开发指南
GET /api/toolbox/plugins/example.py — 下载单文件 Python 插件示例
GET /api/toolbox/plugins/example.zip — 下载 ZIP 插件开发示例
POST /api/toolbox/plugins/import — 导入或更新本地 Python 插件
GET /api/toolbox/plugins/jobs/{job_id} — 查询插件任务结果和日志
GET /api/toolbox/plugins/marketplace-guide — 获取插件市场使用和发布指南
POST /api/toolbox/plugins/schedules — 新增插件定时计划
GET /api/toolbox/plugins/schedules — 查询插件定时计划
DELETE /api/toolbox/plugins/schedules/{schedule_id} — 删除插件定时计划
PATCH /api/toolbox/plugins/schedules/{schedule_id} — 启停插件定时计划
PUT /api/toolbox/plugins/schedules/{schedule_id} — 更新插件定时计划
POST /api/toolbox/plugins/schedules/preview — 预览插件 cron 执行时间
GET /api/toolbox/tg-scheduled-sender/config — 读取 Telegram 定时发送配置
POST /api/toolbox/tg-scheduled-sender/config — 保存 Telegram 定时发送任务
GET /api/toolbox/tmdb/config — 读取 TMDB 连接和识别设置
POST /api/toolbox/tmdb/config — 保存 TMDB 连接和识别设置
GET /api/transfer-history — 查询网盘转存历史
GET /api/users — 获取 Emby 用户（兼容入口）
GET /api/visual-filter/config — 读取可视化筛选规则
POST /api/visual-filter/config — 保存可视化筛选规则
POST /api/visual-filter/config/sync — 同步筛选规则到其他场景
GET /api/visual-filter/tmdb/search — 为筛选规则搜索 TMDB 条目
POST /api/xunlei/login/send-code — 发送迅雷云盘登录验证码
POST /api/xunlei/login/verify-code — 完成迅雷云盘短信登录
POST /api/xunlei/token/clear — 清除迅雷云盘登录凭据
POST /api/xunlei/token/refresh — 刷新迅雷云盘登录凭据
GET /api/xunlei/token/status — 查询迅雷云盘登录状态
POST /api/xunlei/token/validate — 校验迅雷云盘登录凭据
```

下载的规范为每个接口提供中文名称和具体用途。只从当前容器导出的接口索引和规范中选择接口；当前业务界面未开放的影视收藏、自动订阅、Emby 缺集补档及种子文件上传接口已从索引中移除。先按功能说明选择接口，再核对参数和调用示例；同一路径不同 HTTP 方法的行为可能不同。对会修改文件、转存资源、发送消息或保存配置触发重启的接口，开发时应按其用途说明安排调用和结果确认。用途完整不表示请求模型已经细化，仍需注意 inferred / generic 标记。

- 用户在 OpenAPI 页面创建凭据，完整 Token 只显示一次且可撤销，权限等同后台管理员。AI 开发过程只使用 YOUR_OPENAPI_TOKEN 等占位符，不要向我索取真实凭据或把 Token 放入 ZIP、日志、返回值和 URL 查询参数。
- 插件在运行时读取用户配置的 TGTO_OPENAPI_BASE_URL 和 TGTO_OPENAPI_TOKEN 环境变量；这两个变量需用户自行配置，系统不会自动注入令牌。也可以按用户明确要求从 data_dir 内的私有配置文件读取。不要将实际 Token 填入普通可见表单或硬编码。插件与服务共用容器环境，配置后按部署方式重新启动使变量生效。
- BASE_URL 是容器可达的当前服务地址；同一容器通常可使用 http://127.0.0.1:12366，端口仍需按实际配置确认。使用 requests 时每个请求都设置 timeout，通过 Authorization: Bearer <TOKEN> 鉴权，不需要浏览器登录 Cookie。不要导入项目内部模块或直接改数据库来代替公开 API。
- Token 在服务端有独立会话，可完成扫码等多步骤流程；不要把一个 Token 分享给不可信应用。Bearer 不绕过第三方业务授权、破坏性操作确认、webhook token 或 captcha state 校验。插件导入 API 仍要求 trusted=true，Bearer 调用无需 X-Toolbox-Request。POST /api/env 开启音乐整理时仍需 X-Music-Destructive-Confirmed: 1。
- 不把所有响应当作 JSON：有些是文件、图片、HTML 或重定向。默认 allow_redirects=False，检查 HTTP 状态和 Content-Type；不要将 Authorization 自动转发到返回的外部 URL。分页、异步任务轮询、错误提示遵照所选接口约定；避免递归调用自身运行接口。
- 如果收到 HTTP 503 且 code 为 session_persistence_failed，业务操作可能已经完成，只是会话未能保存；应先核对业务结果，不要自动重试修改操作。
- 调用 POST /api/save_json 时，必须在 JSON 顶层传入 target_dir_id（非负整数或数字字符串，推荐字符串；"0" 为明确选择根目录），不再有 API 默认保存目录配置。缺失或无效时会返回 HTTP 400，不会启动任务；目标目录必须属于实际导入的网盘。

运行时调用示例（替换为需求所需接口，不要在模块导入时发请求）：

```python
import os
import requests


def load_toolbox_plugins():
    base_url = os.environ.get("TGTO_OPENAPI_BASE_URL", "").rstrip("/")
    token = os.environ.get("TGTO_OPENAPI_TOKEN", "")
    if not base_url or not token:
        raise ValueError("请配置 TGTO_OPENAPI_BASE_URL 和 TGTO_OPENAPI_TOKEN")
    response = requests.get(
        base_url + "/api/toolbox/plugins",
        headers={"Authorization": "Bearer " + token},
        timeout=(5, 30),
        allow_redirects=False,
    )
    if not 200 <= response.status_code < 300:
        raise RuntimeError(f"项目接口调用失败，HTTP {response.status_code}")
    payload = response.json()
    if payload.get("success") is False:
        raise RuntimeError("项目接口返回失败，请检查参数或服务日志")
    return payload.get("plugins", [])
```

## 六、插件市场与发布

「实用工具 → 我的插件 → 插件市场」使用公开 GitHub 仓库的 plugins.json 获取目录，从固定 tag 的 GitHub Releases 附件下载插件，不需要另外的市场服务器。用户在来源设置填写 `账号/仓库名`、分支（默认 main）和目录路径（默认 plugins.json），可以新增最多 20 个市场来源并按来源过滤。保存后选择插件、查看来源和依赖、确认信任并安装；更新另需确认覆盖。安装完成后从「我的插件」打开使用。没有配置仓库时市场为空，不要编造官方仓库地址。

市场下载遵循全局 Web 代理与系统代理；附件入口不可达时会尝试 GitHub Release API。市场接口允许已认证的跨站请求；多来源安装需提交所选条目的 source_id，不能仅凭重复的插件 ID 推断来源。

若我要求发布市场插件：

- 除完整插件外，说明如何使用项目提供的 plugin-marketplace-template/：新建公开仓库，将模板内容及 .github 放入根目录，在 plugins/<id>/ 放置文件；手动触发 Publish plugin 工作流发布，或按模板 README 本地打包。不要替我虚构发布成功。
- 市场条目包含 id/name/version/description/author/category/homepage/download_url/sha256/size/python_requires/requirements/status/notice。version 推荐 1.0.0，符合 PEP 440；id/version 必须与插件内清单精确一致。
- download_url 必须为 `https://github.com/<owner>/<repo>/releases/download/<固定tag>/<文件名>`，不能是 latest/download 或自动源码包；附件可以是当前支持的单文件或压缩包，必须满足上述插件协议。
- sha256 是最终附件的 SHA-256，size 是附件实际字节数，必须通过构建脚本计算，不能编造；重新打包后重新计算。模板发布脚本会生成这两项和目录条目。
- python_requires 和 requirements 描述真正需要的 Python/分发包版本；市场仅检查当前容器，不安装依赖，不支持 URL 依赖或 extras。不要把开发环境的所有依赖塞进清单。
- 第三方可自己发布 Release，再提交目录条目 PR 供维护者审核。校验时不能运行插件。status=withdrawn 可撤回版本，保留条目并以 notice 说明原因，已安装数据不会远程删除。
- 目录缓存 30 分钟，刷新失败可浏览旧目录；安装前会重新校验远端版本、hash、状态。不要绕过校验或自动重试破坏性操作，也不要在源码、目录、安装包里放真实凭据。

## 七、交付要求

1. 明确插件功能及必要输入；只有缺失信息会影响实现时才询问，不要索取无关敏感信息。
2. 单文件交付提供包含 PLUGIN_MANIFEST 和 run 的完整 `.py`，不另要求 plugin.json；说明文字可以写在文件头部注释或随回复提供。压缩包交付提供最终目录结构，以及 plugin.json、Python 入口、所需辅助文件和 README.md 的完整内容，不省略关键代码。说明须包含参数、依赖、运行示例、服务器路径、输出位置以及任何修改/删除行为。
3. 能生成附件时直接提供单 `.py` 或可导入压缩包；不能生成附件时提供完整文件和打包命令。单文件可直接导入，不必压缩；ZIP 可在包含这些文件的目录运行 `python -m zipfile -c my-plugin.zip plugin.json plugin.py README.md`，有辅助目录时把它们加入命令。不要把打包脚本本身作为插件入口。
4. 检查清单字段、Python 语法、同步 run 签名、默认值、JSON 返回值与大小限制，提供正常、空输入、无效输入和外部服务失败的测试方法；未实际运行的测试必须明确说明。
5. 给出使用步骤：实用工具 → 我的插件 → 导入插件 → 选择支持的文件并确认信任 → 打开 → 填写参数 → 运行。若通过市场安装，先配置来源并刷新，选择插件确认安装。若更新，保持 id 不变并调整 version。

## 我的插件需求

【在这里填写希望实现的功能、输入内容、输出形式，以及会用到的服务器目录或外部服务；不要填写真实密码、Cookie 或 Token。若此处未填写，请先询问我的需求。】
