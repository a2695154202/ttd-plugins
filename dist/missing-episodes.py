# -*- coding: utf-8 -*-
# 由 scripts/package_plugin.py 依据 plugins/missing-episodes/ 自动生成，请勿直接编辑。
# 单文件插件：顶层唯一的 PLUGIN_MANIFEST 常量字典 + 入口源码。

PLUGIN_MANIFEST = {
  'schema_version': 1,
  'id': 'missing-episodes',
  'name': '剧集缺集检测与补齐（未开发完成）',
  'version': '1.0.1',
  'description': '🚧 未开发完成，仅供测试。比对本地剧集与 TMDB 应有的季集找出缺集，并按你的配置搜索补齐（默认只记录，不写盘）。',
  'author': 'a2695154202',
  'entry': 'plugin.py',
  'timeout': 1800,
  'inputs': [
    {
      'name': 'func',
      'label': '执行功能',
      'type': 'select',
      'default': 'check',
      'options': [
        {
          'label': '仅检测缺失（只读）',
          'value': 'check',
        },
        {
          'label': '检测并补齐',
          'value': 'fill',
        },
        {
          'label': '测试连接',
          'value': 'test',
        },
        {
          'label': '查看生效配置',
          'value': 'config',
        },
        {
          'label': '从头开始（清空扫描进度，不检测）',
          'value': 'reset',
        },
      ],
      'help': '决定本次要做什么。右侧按钮会**覆盖**这里的取值：点「检查缺失」就是 check，点「测试连接」就是 test。\n\n建议顺序：先点「测试连接」确认四个数据源都通 → 再点「检查缺失（只读）」看清缺口 → 最后把「执行功能」切到「检测并补齐」（或直接用第三个按钮）执行补齐。\n\n**从头开始**（`reset`）是另一种用法：**只清空扫描进度**（`scan_cursor.json`），不检测、不补齐、也不发通知 —— 下次运行会从第 1 部重新开始。适合媒体库删改过、换过媒体库，或单纯想重扫一轮的时候。\n\n从其他插件/接口调用本插件时，用这个字段指定动作。',
    },
    {
      'name': 'tgto_base_url',
      'label': 'TgtoDrive 地址',
      'type': 'text',
      'default': 'http://127.0.0.1:12366',
      'placeholder': 'http://127.0.0.1:12366',
      'help': '本插件调用 TgtoDrive 的 OpenAPI（读 TMDB 详情、内置资源检索、转存、离线下载）。同容器通常就是 http://127.0.0.1:12366。\n\n如果你把地址配在容器环境变量 `TGTO_OPENAPI_BASE_URL` 里并希望以它为准，把这里清空即可 —— 本插件把「值等于清单默认值」视为未填写，会改用环境变量。',
    },
    {
      'name': 'tgto_token',
      'label': 'OpenAPI 令牌',
      'type': 'password',
      'default': '',
      'help': '调用 TgtoDrive OpenAPI 的 Bearer 令牌，在「实用工具 → OpenAPI」页面创建。\n\n留空时读容器环境变量 `TGTO_OPENAPI_TOKEN`。令牌不会出现在运行日志、结果页或返回值中。',
    },
    {
      'name': 'emby_url',
      'label': 'Emby 地址',
      'type': 'text',
      'default': '',
      'placeholder': 'http://192.168.1.10:8096（填网页入口带 /emby 也行）',
      'help': '**本插件必须直连 Emby**，因为 TgtoDrive 的 OpenAPI 没有「取某部剧的本地集号清单」的接口（`/api/emby/dashboard` 只给电影/剧集/单集**总量**，`/api/emby/latest` 只给最近入库）。\n\n留空时会尝试复用「TgtoDrive → 影视发现 → Emby 设置」里已配置的地址与 API Key；那里也没有就得在这里填。\n\n填网页入口（形如 `http://host:8096/emby`）也可以，插件会自动去掉 `/emby` 这一层。',
    },
    {
      'name': 'emby_api_key',
      'label': 'Emby API Key',
      'type': 'password',
      'default': '',
      'help': 'Emby 后台「设置 → API 密钥」里创建的密钥，用于读取剧集与集列表（只读）。\n\n留空时同上，尝试复用 TgtoDrive 影视设置里的 Emby 配置。密钥不会出现在日志或结果页中。',
    },
    {
      'name': 'tmdb_source',
      'label': '「应有季集」的数据源',
      'type': 'select',
      'default': 'auto',
      'options': [
        {
          'label': '自动（填了 API Key 就直连 TMDB，否则走 TgtoDrive 代理）',
          'value': 'auto',
        },
        {
          'label': 'TgtoDrive 详情代理',
          'value': 'ttd',
        },
        {
          'label': '直连 TMDB（用下面的 API Key）',
          'value': 'direct',
        },
      ],
      'help': '决定「每一季应该有哪些集」从哪里读。\n\n走 **TgtoDrive 详情代理**时，该季集接口「只有当前详情配置支持完整季集模式时可用」；没开时会返回 HTTP 409 `TMDB_READONLY_MODE_INACTIVE`，缺集检测就没有数据源。\n\n此时**最省事的做法是填上 TMDB API Key 并保持「自动」** —— 插件会直连 api.themoviedb.org，不受那个模式约束。',
    },
    {
      'name': 'tmdb_api_key',
      'label': 'TMDB API Key',
      'type': 'password',
      'default': '',
      'placeholder': 'themoviedb.org → 设置 → API 里申请（用 v3 的 API Key）',
      'help': '本插件**自己直连 TMDB** 时用的密钥。填了它并把数据源保持「自动」，就会绕开 TgtoDrive 详情代理的「完整季集模式」限制。\n\n留空则完全走 TgtoDrive 代理。密钥走查询参数发给 TMDB，插件已做脱敏，不会出现在日志或结果页中。',
    },
    {
      'name': 'tmdb_base_url',
      'label': 'TMDB 接口地址',
      'type': 'text',
      'default': 'https://api.themoviedb.org/3',
      'placeholder': 'https://api.themoviedb.org/3',
      'help': '直连 TMDB 时的接口根地址。容器访问不了官方域名时，可以填一个自建 / 第三方的 TMDB 反代地址（接口结构须与官方一致）。',
    },
    {
      'name': 'tmdb_language',
      'label': 'TMDB 语言',
      'type': 'text',
      'default': 'zh-CN',
      'placeholder': 'zh-CN',
      'help': '影响剧集名称与简介的语言；**不影响集号与播出日期**（缺集比对用的是后两者）。',
    },
    {
      'name': 'tmdb_proxy',
      'label': 'TMDB 代理地址（可选）',
      'type': 'text',
      'default': '',
      'placeholder': 'http://192.168.1.2:7890',
      'help': '本插件直连 TMDB 时使用的代理。填了就**优先用它**，且**只对 TMDB 生效**（不影响 TgtoDrive / Emby / 盘搜的请求）。\n\n留空则按下面的「代理策略」自动挑选。',
    },
    {
      'name': 'tmdb_proxy_mode',
      'label': 'TMDB 代理策略',
      'type': 'select',
      'default': 'auto',
      'options': [
        {
          'label': '自动：TgtoDrive 网络代理 → 容器环境变量 → 直连（逐个尝试）',
          'value': 'auto',
        },
        {
          'label': '只用容器环境变量代理',
          'value': 'env',
        },
        {
          'label': '不使用代理（直连）',
          'value': 'off',
        },
      ],
      'help': '容器出网通常需要代理。\n\n⚠️ 容器里的 `HTTP_PROXY` / `HTTPS_PROXY` 往往是**平台侧内部代理**，拿它出网到公网会被送到错处（实测返回 502）。所以「自动」会**优先用 TgtoDrive 自己配的网络代理**，失败再依次退到环境变量、直连 —— 只在这类「代理 / 网关层」错误时才换下一个，不会重复打扰 TMDB。',
    },
    {
      'name': 'library_ids',
      'label': '媒体库 id（可留空）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 自动扫描全部剧集库；多个用逗号分隔',
      'help': '限定只检测哪些媒体库里的剧集。**留空（推荐）会自动扫描全部剧集库**。\n\n⚠️ **本插件只处理剧集**：电影、音乐、音乐视频、有声书、书籍、家庭视频、合集、照片等类别的媒体库会被**按库类型自动排除**，不参与检测也不参与补齐。被排除的库会**写进运行日志与结果页**，不会静默消失。\n\n如果你手动填了库 id 而其中没有剧集库，插件会明确报错并列出 Emby 里现有的库（避免「静默返回 0 条」看不出原因）。',
    },
    {
      'name': 'max_series',
      'label': '单次检测上限（部）',
      'type': 'number',
      'default': 50,
      'min': 1,
      'max': 2000,
      'help': '每次运行最多检测多少部剧，防止媒体库很大时撞上插件超时（1800 秒）。\n\n**媒体库比它大时不会漏剧**：插件会记录扫描进度，本次从上次的位置往后取，下次接着往后轮转（顺序按剧名排序、稳定不变，所以轮转能覆盖全库）。中途撞上时间预算也会保存进度并带着已完成的结果收工，不会白跑。\n\n要一次扫完就调大；配合「定时执行」分批跑也可以。',
    },
    {
      'name': 'only_aired',
      'label': '只统计已播出的集',
      'type': 'boolean',
      'default': True,
      'help': '开启时，TMDB 上「尚未开播」的集不计入应有集数，因此不会被当成缺集。**强烈建议保持开启** —— 否则未开播的剧会被大量误判为缺失。\n\n没有播出日期的集也按「未开播」处理。',
    },
    {
      'name': 'only_season_exist',
      'label': '只检查「本地已有季」的缺失',
      'type': 'boolean',
      'default': True,
      'help': '开启时，只在「本地已经有这个季的某些集」的情况下才报该季的缺集；**本地一集都没有的季（含整剧未入库）会被跳过**（与参考插件一致）。\n\n关闭后，本地完全没有的季也会被列为「**整季缺失**」，整部剧没入库的会被列为其所有季都缺失 —— 想连整季 / 整剧一起补齐就关掉它。\n\n跳过时不会静默：日志会写明原因，结果页会出现「整剧未入库跳过」卡片与一条说明。',
    },
    {
      'name': 'include_s00',
      'label': '包含特别季（S00）',
      'type': 'boolean',
      'default': False,
      'help': 'S00（特别篇 / 花絮）通常不是正片内容，默认不检测。需要时打开。',
    },
    {
      'name': 'ignore_series',
      'label': '忽略的剧集关键词（可留空）',
      'type': 'text',
      'default': '',
      'placeholder': '多个用逗号分隔，例如：预告, 花絮, 合集',
      'help': '剧名里包含这些关键词的条目会被跳过，不参与检测。多个用逗号分隔。',
    },
    {
      'name': 'fill_action',
      'label': '补齐动作',
      'type': 'select',
      'default': 'record',
      'options': [
        {
          'label': '仅记录并列出链接（最安全）',
          'value': 'record',
        },
        {
          'label': '转存到网盘',
          'value': 'transfer',
        },
        {
          'label': '提交离线下载（磁力 / 电驴 / 种子）',
          'value': 'offline',
        },
      ],
      'help': '找到缺失资源后做什么：\n\n• **仅记录并列出链接**：只把候选链接与提取码写进结果页和日志，你自己决定后续（默认，最安全）；\n• **转存到网盘**：调 TgtoDrive 的转存接口把分享链接存进你的网盘 —— **会真实写网盘、可能消耗会员点数**；遇到磁力 / 电驴 / 种子候选时自动改走 TTD 的离线下载接口提交（目标网盘的离线设置已在 TgtoDrive 里配好），不会跳过；\n• **提交离线下载**：只对磁力 / 电驴 / 种子候选有效，调离线下载接口创建任务。\n\n后两种属于破坏性操作，请先用预览模式确认。',
    },
    {
      'name': 'dry_run',
      'label': '预览模式（不实际写入）',
      'type': 'boolean',
      'default': True,
      'help': '**默认开启**：只打印「将要执行什么」，不会真的转存或创建离线任务。\n\n确认候选是否正确后再关掉它真正执行。推荐先开预览跑一次，核对结果页里的候选链接。',
    },
    {
      'name': 'search_source',
      'label': '搜索源',
      'type': 'select',
      'default': 'both',
      'options': [
        {
          'label': '两者都查',
          'value': 'both',
        },
        {
          'label': '盘搜（PanSou）',
          'value': 'pansou',
        },
        {
          'label': 'TgtoDrive 内置资源检索',
          'value': 'builtin',
        },
      ],
      'help': '去哪里找缺失资源：\n\n• **盘搜（PanSou）**：你自建的网盘搜索服务，响应结构是公开文档化的，候选解析完整；\n• **TgtoDrive 内置资源检索**：调 `/api/media/resources/search`，省一个外部服务，但该接口在规范里没有响应 schema，本插件会把原始响应写进运行日志，便于后续精确对接。',
    },
    {
      'name': 'pansou_url',
      'label': '盘搜地址',
      'type': 'text',
      'default': 'http://127.0.0.1:8888',
      'placeholder': 'http://127.0.0.1:8888',
      'help': '你的盘搜（PanSou）服务地址，默认端口 8888。自建实例常见同容器 http://127.0.0.1:8888 或局域网地址。\n\n搜索源不含盘搜时可以不管；「测试连接」会一并检查 `/api/health`。',
    },
    {
      'name': 'pansou_token',
      'label': '盘搜令牌（启用鉴权时填）',
      'type': 'password',
      'default': '',
      'help': '盘搜默认不启用鉴权（`AUTH_ENABLED=false`）。若你的实例开了鉴权，这里填 JWT Token（登录 `/api/auth/login` 获取），插件会以 `Authorization: Bearer <token>` 调用。\n\n令牌不会出现在日志或结果页中。',
    },
    {
      'name': 'pansou_cloud_types',
      'label': '盘搜网盘类型（可留空）',
      'type': 'text',
      'default': '115,quark,aliyun',
      'placeholder': '留空 = 不限；逗号分隔，如 115,quark,aliyun,magnet',
      'help': '限定盘搜返回哪些网盘类型，留空表示不限。可用值：\n`baidu` `aliyun` `quark` `guangya` `tianyi` `uc` `mobile` `115` `pikpak` `xunlei` `123` `magnet` `ed2k`。\n\n挑选候选时：网盘分享链接走「转存」接口；磁力 / 电驴 / 种子两个动作都能提交（转存动作下会自动改走 TTD 离线下载接口）。',
    },
    {
      'name': 'max_fill_per_run',
      'label': '单次补齐上限（部）',
      'type': 'number',
      'default': 1,
      'min': 0,
      'max': 500,
      'help': '每次运行最多对多少部剧执行补齐，默认 **1** —— 先小步验证，确认无误再调大。填 0 表示不限制。\n\n检测部分不受此限制（由「单次检测上限」控制）。',
    },
    {
      'name': 'resource_sources',
      'label': '资源来源（可留空，读 TgtoDrive 配置）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 由 TgtoDrive 决定；多个用逗号分隔（标识见「测试连接」结果）',
      'help': '限定调 TgtoDrive 内置资源检索（`/api/media/resources/search`）时用哪些**来源**。\n\n**留空即可** —— 由 TgtoDrive 用它自己的配置决定。可用的来源标识由 TgtoDrive 的 `/api/media/providers` 决定（其中包含 RE0），点「测试连接」会把当前可用清单列出来，复制标识填进来即可。\n\n**RE0 不需要在这里配**：RE0 是 TgtoDrive 自己集成的服务，能不能用取决于它的**主账号授权状态**（`/api/re0/status`）—— 本插件只读该状态并在「测试连接」里报告，凭据由 TgtoDrive 自己保管。',
    },
    {
      'name': 'target_dir',
      'label': '目标网盘（可留空）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 直接用 TgtoDrive 已配置的离线下载目标网盘',
      'help': '**仅对「提交离线下载」动作生效**：磁力 / 电驴 / 种子的离线任务落到哪块网盘（即离线接口里的 `provider`）。**留空时会自动使用 TgtoDrive 影视设置里的 `target_provider`** —— 这些你已经在 TgtoDrive 里配过了，不需要在这里重填。\n\n⚠️ **「转存到网盘」用不到这个字段**：转存接口的 `provider` 传的是**分享链接所属网盘**（由插件按候选类型自动识别），转存目标完全由 TgtoDrive 的影视设置决定。\n\n⚠️ 这里填的是**网盘标识**，不是目录路径。TgtoDrive 的转存目录（`media_transfer_targets`）由它自己应用，本插件只在「查看生效配置」里展示、不会把它当网盘标识发出去。\n\n只有想**临时覆盖离线目标**时才需要填写。点「测试连接」可以看到 TgtoDrive 当前的配置。',
    },
    {
      'name': 'notify_channels',
      'label': '运行结果通知（可多选，默认不发送）',
      'type': 'multiselect',
      'default': [],
      'options': [
        {
          'label': 'Telegram（用 ttd 已配置的通知机器人）',
          'value': 'tg',
        },
        {
          'label': '微信（调用「企业微信通知」插件）',
          'value': 'wecom',
        },
      ],
      'help': '每次运行（检测 / 补齐）结束后，把结果整理成三类推给你：① **缺失集的剧集** ② **被成功补全的剧集** ③ **补全失败 / 未补全的剧集**（含「只补全一部分」的，会带 `【部分补全】` 文字标记）。\n\n默认**一个都不勾**，此时不发送任何通知。两个渠道可以同时勾选，**各自独立发送、各自报告结果** —— 一个失败不影响另一个，投递结果也会显示在结果页的「运行通知」表里。\n\n- **Telegram**：读 TgtoDrive 已配置的通知机器人（`GET /api/notify-bots`），用它的 Token 与推送目标直连 `sendMessage`，这里**不需要填任何机器人凭据**。推送时会依次尝试「ttd 网络代理 → 机器人自带代理 → 容器环境变量代理 → 直连」，只在代理层错误时才换下一种。\n- **微信**：调用「企业微信通知」插件发送，企业 ID / Secret / 收件人**全部由那个插件保管**。前提是它已装好、启用，并且你点过它的「发送测试消息」能收到。\n\n想先验证链路：勾好渠道后点右侧「**① 测试连接**」，它会顺便发一条测试通知并给出投递结论。',
    },
    {
      'name': 'notify_bot',
      'label': 'Telegram 机器人序号（0 = 自动）',
      'type': 'number',
      'default': 0,
      'min': 0,
      'max': 20,
      'help': 'TgtoDrive 里可能配了多个 Telegram 通知机器人，这里按**序号**选择用哪一个发通知。\n\n**0（默认）= 自动**：优先用名字带「主」的那个，其次用第一个可用项。\n\n机器人列表是**运行时**才能读到的（来自 `GET /api/notify-bots`），而清单里的下拉选项是静态的 —— 所以这里用序号而不是把机器人名字写死。填了序号但那个位置缺少 Token / 推送目标时会自动回退到主机器人，并在日志里说明。\n\n想知道实际有哪些机器人、哪个是主机器人：点「测试连接」，通知结果里会给出本次使用的机器人名。',
    },
    {
      'name': 'wecom_plugin_id',
      'label': '微信通知插件 id（默认 wecom-notify）',
      'type': 'text',
      'default': 'wecom-notify',
      'placeholder': 'wecom-notify',
      'help': '要把通知交给哪个「企业微信通知」插件发送。默认就是本仓库的 `wecom-notify`，一般不用改。\n\n改成别的值时，目标插件必须同样支持 `envelope` 参数（见它的 CALLING.md），否则发送会失败并在结果页说明原因。',
    },
    {
      'name': 'wecom_touser',
      'label': '微信收件人（留空 = 沿用该插件设置）',
      'type': 'text',
      'default': '',
      'placeholder': '留空 = 用「企业微信通知」里已配好的收件人；也可填 @all 或 zhangsan|lisi',
      'help': '传给「企业微信通知」插件的 `touser`。**留空（默认）＝沿用那个插件里已保存的收件人** —— 推荐留空，因为那个插件自己点测试能收到，用的就是那份配置；一旦在这里填了值就会**覆盖**它，可能发到不在可见范围的人。\n\n（这里正是踩过的坑：平台会把清单默认值填齐，导致「留空」被 `@all` 顶掉。本插件只在**你确实填了非空值**时才传这个字段。）',
    },
  ],
  'ui': {
    'width': 'wide',
    'layout': 'stack',
    'components': [
      {
        'type': 'heading',
        'text': '🚧 剧集缺集检测与补齐 · 未开发完成',
      },
      {
        'type': 'alert',
        'text': '本插件尚未开发完成 —— 功能、参数与结果格式都可能变动，请仅用于测试，不要长期依赖。',
        'style': {
          'tone': 'warning',
        },
      },
      {
        'type': 'markdown',
        'text': '把「本地已有哪些集」与「TMDB 应该有哪些集」求差集找出缺集，再按你配置的搜索源找资源、按选定动作补齐。\n\n**第一次用，按这个顺序来**（右侧三个按钮按 ①②③ 编号）：\n\n1. 点「**① 测试连接**」—— 一次确认 TgtoDrive / Emby / TMDB / 盘搜都通，其中 **TMDB 季集详情（关键）** 那一项最重要，它不通就无法确定「应该有哪些集」；\n2. 点「**② 检查缺失（只读）**」—— 看清缺口，**不写任何数据**；\n3. 确认无误后再点「**③ 检测并补齐**」—— 默认**预览模式**，只打印将要做什么。',
      },
      {
        'type': 'alert',
        'text': '开始前确认两件事：① TgtoDrive 的 OpenAPI 令牌（在「实用工具 → OpenAPI」创建）；② 能直连的 Emby 地址 + API Key —— TgtoDrive 的接口没有「某剧本地集号清单」，所以本地季集只能直连 Emby 读取。Emby 这两项留空时，插件会自动尝试复用「TgtoDrive → 影视发现 → Emby 设置」里已配好的那份，配过就不用再填。',
        'style': {
          'tone': 'primary',
        },
      },
      {
        'type': 'alert',
        'text': '结果有三种，别把第三种当成第二种：「有缺失」＝比出了具体缺集；「无缺失」＝每个季都比对成功且集号齐全；「⚠️ 无法判定」＝某些季的「应有集数」根本没读成（既不算缺失、也不算完整）。遇到「无法判定」先点「测试连接」看 TMDB 季集详情（关键）这一项 —— 不通就到「TMDB 设置」填上 API Key 改用直连即可绕过（TgtoDrive 详情页没开「完整季集模式」时，它的季集接口会返回 409）。',
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
                    'label': '① 连接设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '**这一页是必填项**：TgtoDrive 与 Emby 两处连接。\n\n- **TgtoDrive** —— 用来读 TMDB 详情、做资源检索、转存与离线下载。同容器一般就是 `http://127.0.0.1:12366`。\n- **Emby** —— **必须能直连**，否则读不到「本地已有哪些集」。同容器可以填局域网地址（如 `http://192.168.1.10:8096`），填网页入口带 `/emby` 也行。\n\n填完建议先点右侧「**① 测试连接**」验证一下。',
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
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'emby_url',
                      },
                      {
                        'type': 'field',
                        'name': 'emby_api_key',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '② TMDB 设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '**「每一季应该有哪些集」从这里取。**\n\n默认走 **TgtoDrive 的详情代理**。但该代理的季集接口「**只有当前详情配置支持完整季集模式时可用**」—— 没开时会返回 HTTP 409 `TMDB_READONLY_MODE_INACTIVE`，缺集检测就没有数据源。\n\n**最省事：填上 TMDB API Key，数据源保持「自动」**，插件就会直连 `api.themoviedb.org`，不受上面那个模式约束。API Key 在 [themoviedb.org](https://www.themoviedb.org/settings/api) 注册后到「设置 → API」申请（v3 的 API Key 即可）。\n\n直连是本插件**自己**发的请求、不经过 TgtoDrive，所以容器要能出网；出不了网就填最下面的代理。',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_source',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_api_key',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_base_url',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_language',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_proxy',
                      },
                      {
                        'type': 'field',
                        'name': 'tmdb_proxy_mode',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '③ 检测范围',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '控制检测**哪些剧**、**哪些集算「应该有」**。\n\n默认值已按最佳实践调好，**不建议改动**「只统计已播出的集」—— 关掉它会把尚未开播的集也算成缺集，导致大量误报。\n\n「单次检测上限」默认 50 部。媒体库更大时**不会漏**：插件会记录**扫描进度**，每次接着上次的位置往后轮转，多跑几次即可覆盖全库（顺序按剧名排序，稳定不变）。\n\n**想重新从头扫一遍**：点右侧「**从头开始（清空进度）**」—— 它只清掉进度记录，不检测也不补齐，下次运行就从第 1 部重新开始。',
                      },
                      {
                        'type': 'field',
                        'name': 'library_ids',
                      },
                      {
                        'type': 'field',
                        'name': 'max_series',
                      },
                      {
                        'type': 'field',
                        'name': 'ignore_series',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'only_aired',
                      },
                      {
                        'type': 'field',
                        'name': 'only_season_exist',
                      },
                      {
                        'type': 'field',
                        'name': 'include_s00',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '④ 补齐设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '去哪里找资源、找到后做什么。\n\n**这里的参数大多直接从 TgtoDrive 读，不需要重填**：转存目标网盘 / 点数上限取自 TgtoDrive 的影视设置；**RE0** 是 TgtoDrive 集成的服务，只要在 TgtoDrive 里授权过就能用（本插件只读它的授权状态）；可限定的「资源来源」清单也由 TgtoDrive 提供。\n\n⚠️ 「转存到网盘」与「提交离线下载」会**真实写网盘、可能消耗会员点数**。所以默认是「仅记录并列出链接」+ **预览模式开启** —— 先跑一次核对候选是否正确，再关掉预览真正执行。\n\n插件会先判断「**缺失的集到底在哪个包里**」：从候选标题读出集号（`第01-12集` / `更新至第10集` / `S01E05` / `全集` 等），再与缺失集比对 —— **不含缺失集的直接排除**；只覆盖一部分时，转存 / 离线会**跳过**（会真实写网盘，补一半不划算），「仅记录」则照常列出。每条结论见结果表的「**覆盖**」列。',
                      },
                      {
                        'type': 'field',
                        'name': 'search_source',
                      },
                      {
                        'type': 'field',
                        'name': 'pansou_url',
                      },
                      {
                        'type': 'field',
                        'name': 'pansou_token',
                      },
                      {
                        'type': 'field',
                        'name': 'pansou_cloud_types',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'fill_action',
                      },
                      {
                        'type': 'field',
                        'name': 'dry_run',
                      },
                      {
                        'type': 'field',
                        'name': 'max_fill_per_run',
                      },
                      {
                        'type': 'field',
                        'name': 'resource_sources',
                      },
                      {
                        'type': 'field',
                        'name': 'target_dir',
                      },
                    ],
                  },
                  {
                    'type': 'card',
                    'label': '⑤ 运行通知',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '**每次运行（检测 / 补齐）结束后，把结果整理成三类推给你**：\n\n1. **① 缺失集的剧集** —— 哪些剧缺哪些集；\n2. **② 被成功补全的剧集** —— 本次补好的（「仅记录」或「预览模式」下会如实标注**未真正写入网盘**）；\n3. **③ 补全失败 / 未补全的剧集** —— 含搜不到资源、候选不含缺失集、以及**只补全一部分**的（这种会带 `⚠️【部分补全】` 文字标记），也会列出「本次还没轮到处理」的。\n\n**默认不勾任何渠道**（不发送）。两个渠道可同时勾选，各自独立发送、各自报告结果，失败原因也会写进结果页的「运行通知」表。',
                      },
                      {
                        'type': 'field',
                        'name': 'notify_channels',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'notify_bot',
                      },
                      {
                        'type': 'divider',
                      },
                      {
                        'type': 'field',
                        'name': 'wecom_plugin_id',
                      },
                      {
                        'type': 'field',
                        'name': 'wecom_touser',
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
                'type': 'card',
                'label': '⚡ 快捷操作',
                'children': [
                  {
                    'type': 'field',
                    'name': 'func',
                  },
                  {
                    'type': 'markdown',
                    'text': '下面这些按钮会**覆盖**上面选的「执行功能」，点哪个就跑哪个。「从头开始」只清空扫描进度、**不检测也不补齐**。',
                  },
                  {
                    'type': 'button',
                    'label': '① 测试连接',
                    'action': 'run',
                    'params': {
                      'func': 'test',
                    },
                    'style': {
                      'tone': 'primary',
                      'size': 'large',
                      'variant': 'outline',
                    },
                  },
                  {
                    'type': 'button',
                    'label': '② 检查缺失（只读）',
                    'action': 'run',
                    'params': {
                      'func': 'check',
                    },
                    'style': {
                      'tone': 'primary',
                      'size': 'large',
                      'variant': 'solid',
                    },
                  },
                  {
                    'type': 'button',
                    'label': '③ 检测并补齐',
                    'action': 'run',
                    'params': {
                      'func': 'fill',
                    },
                    'style': {
                      'tone': 'success',
                      'size': 'large',
                      'variant': 'solid',
                    },
                  },
                  {
                    'type': 'button',
                    'label': '查看生效配置',
                    'action': 'run',
                    'params': {
                      'func': 'config',
                    },
                    'style': {
                      'tone': 'default',
                      'size': 'large',
                      'variant': 'outline',
                    },
                  },
                  {
                    'type': 'button',
                    'label': '从头开始（清空进度）',
                    'action': 'run',
                    'params': {
                      'func': 'reset',
                    },
                    'style': {
                      'tone': 'warning',
                      'size': 'large',
                      'variant': 'outline',
                    },
                  },
                  {
                    'type': 'divider',
                  },
                  {
                    'type': 'link',
                    'href': 'https://github.com/a2695154202/ttd-plugins/blob/main/plugins/missing-episodes/README.md',
                    'label': '📖 打开完整说明与常见问题（README）',
                  },
                ],
              },
            ],
          },
        ],
      },
      {
        'type': 'divider',
      },
      {
        'type': 'card',
        'label': '⏰ 定时执行',
        'children': [
          {
            'type': 'markdown',
            'text': '到「**我的插件 → 定时执行**」新建计划，选本插件，运行参数填 `func=check`。\n\n建议先用 `check` 观察一段时间，确认结果可信后再改成 `fill`。媒体库很大时**不用一次扫完** —— 插件会记录扫描进度，每次接着上次的位置往后轮转，多跑几次即可覆盖全库。',
          },
        ],
      },
      {
        'type': 'text',
        'text': '「仅检测缺失」是纯只读操作：不写网盘、不改媒体库、不动 TgtoDrive 的任何设置。补齐动作默认走预览，只有你显式关掉「预览模式」才会真正执行。',
        'style': {
          'tone': 'muted',
        },
      },
    ],
  },
}


# -*- coding: utf-8 -*-
"""剧集缺集检测与补齐 · TgtoDrive 插件

**做什么**：读取「本地媒体库里已有哪些剧集」与「按 TMDB 应该有哪些剧集」，求差集得到缺集；
然后按用户配置的搜索源去找缺失资源，并按选定动作补齐。

三个数据源，缺一不可：

1. **本地已有季集** —— 走 **Emby 直连**。
   ⚠️ 为什么必须直连：TgtoDrive 的 OpenAPI **没有**「取某部剧的本地集号清单」的接口
   （`/api/emby/*` 全是看板/代理/封面类；`/api/emby/dashboard` 只给电影/剧集/单集**总量**，
   `/api/emby/latest` 只给最近入库）。MoviePilot 的同名插件靠 `MediaServerChain.episodes()`，
   在 TTD 里对应不到任何公开接口，因此本插件让用户填 Emby 地址 + API Key 直连读取。
2. **应有季集** —— 两个数据源二选一（默认「自动」）：
   * 走 **TgtoDrive 的 TMDB 代理**（`/api/media/details/...`），不必准备 TMDB 的 API Key；
     但该代理的季集接口「**只有当前详情配置支持完整季集模式时可用**」，未开启时返回
     `HTTP 409 TMDB_READONLY_MODE_INACTIVE`，整条链路就没有数据源；
   * 或 **本插件直连 TMDB**（`api.themoviedb.org`，用户自填 API Key）——
     **不受上面那个模式约束**，并可自选接口地址、语言与代理。
   「自动」= 填了 Key 就直连，否则走代理。见 `_TmdbClient` 与 `_use_direct_tmdb()`。
3. **缺失资源的搜索源** —— 可选 TgtoDrive 内置资源检索（`/api/media/resources/search`），
   或用户自建的**盘搜（PanSou）**实例（默认端口 8888），或两者都查。

**补齐动作**（默认最保守）：
`record` 仅记录并列出链接 → `transfer` 转存到网盘 → `offline` 提交磁力/电驴/种子离线下载。
其中 `transfer` 遇到磁力 / 电驴 / 种子候选时**不跳过**，自动改走 TTD 的离线下载接口
（`/api/media/resources/offline` 的 `link` 字段专收这类链接；目标网盘的离线设置已在
TgtoDrive 侧配好，插件只负责提交）；`offline` 遇到网盘分享链接才跳过（该接口收不了）。
**两个接口的 `provider` 语义相反，别搞混**：offline 的 provider = 任务落地的**目标网盘**；
transfer 的 provider = 分享链接**所属网盘（源）**，转存目标由 TTD 影视设置决定
（曾把目标当源传给 transfer，TTD 一律 409 SHARE_PROVIDER_MISMATCH）。
115 对重复提交同一条磁力 / 种子返回 502「任务已存在」—— 按已提交记账（资源早已在离线队列），
不当失败报。
默认 **dry_run=True**：只打印「将要做什么」，不真正执行；转存/离线会真实写网盘、
消耗网盘额度，务必先跑 dry-run 确认。

实现上遵循本仓库既有约定：模块导入阶段不发网络请求、每次请求都设超时、
凭据一律脱敏、任务结果逐层下沉后再判读（任务查询接口无响应 schema）。

**运行结果通知**：每次检测 / 补齐跑完后，把结果整理成固定三类推给用户勾选的渠道 ——
① 缺失集的剧集、② 被成功补全的剧集、③ 补全失败 / 未补全的（含「只补全一部分」的，
带 `⚠️【部分补全】` 文字标记）。渠道做法沿用仓库约定：Telegram 读 ttd 已配置的通知机器人后
直连 Bot API；微信把内容交给「企业微信通知」插件（凭据由它保管）。两个渠道各自独立发送、
各自报告结果，通知失败**不影响**本次结果页。默认一个渠道都不勾（不发送）。
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from datetime import datetime, date
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PLUGIN_NAME = "剧集缺集检测与补齐（未开发完成）"

DEFAULT_BASE_URL = "http://127.0.0.1:12366"
DEFAULT_PANSOU_URL = "http://127.0.0.1:8888"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60          # TMDB / 盘搜 / 网盘转存都可能偏慢

# 单次检测的**软时间预算**（秒）。清单里声明的 timeout 是 1800，这里留 300 秒余量
# 给收尾（结果序列化、补齐阶段的搜索请求等）。到点就带结果收工并保存进度，
# 避免大媒体库撞上硬超时后**整轮结果全丢**。
DETECT_TIME_BUDGET = 1500

# 整轮（检测 + 补齐）的软预算（秒）。补齐阶段会真正发搜索 / 转存请求，同样可能很久，
# 此前只有检测有预算、补齐没有 —— 缺集一多就会一路跑到硬超时，整轮结果白跑。
# 这里按「从启动算起」计时，给收尾留 150 秒。
TOTAL_TIME_BUDGET = 1650

# 扫描进度文件名（写在 data_dir：更新插件不丢，卸载才删）
CURSOR_FILE = "scan_cursor.json"

# TgtoDrive 在「详情页未启用完整 TMDB 季集模式」时，季集接口
# `/api/media/details/tmdb/tv/{id}/season/{n}` 返回 **HTTP 409 + 该错误码**：
#   {"code":"TMDB_READONLY_MODE_INACTIVE","error":"当前详情页不使用完整 TMDB 季集模式"}
# 命中它说明缺集检测的**前置条件不满足**（拿不到「应该有哪些集」）—— 必须提前拦住整轮扫描，
# 否则会演变成「50 部剧 × 每季一条告警」的刷屏，最后得到一份全是「无法判定」的无用结果。
TMDB_READONLY_ERROR_CODE = "TMDB_READONLY_MODE_INACTIVE"

# TMDB **直连**（不走 TgtoDrive 的详情代理）时的默认地址与语言。
# 为什么要内置直连：TgtoDrive 的 `/api/media/details/tmdb/tv/{id}/season/{n}`
# 「只有当前详情配置支持完整季集模式时可用」，而该模式在部分环境里打不开
# （返回 409 TMDB_READONLY_MODE_INACTIVE）—— 一旦如此，缺集检测就完全没有数据源。
# 直连 TMDB 不受该模式约束。
DEFAULT_TMDB_BASE = "https://api.themoviedb.org/3"
DEFAULT_TMDB_LANGUAGE = "zh-CN"

# 「应有季集」的数据源
# 注意：这里**不放**中文标签表 —— 标签以 plugin.json 的 options 为唯一来源
# （清单里必须写一份给界面用），源码再抄一份只会两边漂移。人话说明由
# `_tmdb_source_note()` 按「本次实际用了哪个」动态拼出。
TMDB_SRC_AUTO = "auto"
TMDB_SRC_TTD = "ttd"
TMDB_SRC_DIRECT = "direct"
VALID_TMDB_SOURCES = (TMDB_SRC_AUTO, TMDB_SRC_TTD, TMDB_SRC_DIRECT)

# TMDB 直连时的代理策略
TMDB_PROXY_AUTO = "auto"
TMDB_PROXY_ENV = "env"
TMDB_PROXY_OFF = "off"
VALID_TMDB_PROXY_MODES = (TMDB_PROXY_AUTO, TMDB_PROXY_ENV, TMDB_PROXY_OFF)
TMDB_PROXY_LABELS = {
    TMDB_PROXY_AUTO: "自动：TgtoDrive 网络代理 → 容器环境变量 → 直连（逐个尝试）",
    TMDB_PROXY_ENV: "只用容器环境变量代理",
    TMDB_PROXY_OFF: "不使用代理（直连）",
}

# 这几个状态码来自**代理 / 网关本身**，说明请求没到 TMDB —— 换下一个代理重试是安全的，
# 不会造成「重复请求把数据搞脏」。TMDB 自身的响应（200/401/404/429…）必须立刻停。
PROXY_LAYER_STATUS = (407, 502, 503, 504, 520, 521, 522, 523, 524)

# 平台 `table` 组件的行数上限（协议清单：≤30 列 200 行）。超出会被拒绝渲染，
# 导致整个结果页看不到 —— 必须自己截断并说明。
MAX_TABLE_ROWS = 200

# -- 运行结果通知 -----------------------------------------------------------
# 每次运行后（check / fill）把结果整理成三类推到用户勾选的渠道：
#   ① 缺失集的剧集  ② 被成功补全的剧集  ③ 补全失败（含「只补全一部分」的，需文字标记）
# 渠道做法沿用本仓库既有约定：
#   * Telegram —— 读 ttd 已配置的通知机器人（`GET /api/notify-bots`）后直连 Bot API
#     `sendMessage`，机器人 Token / 推送目标都从 ttd 读，**不落在本插件里**；
#   * 微信 —— 把内容交给「企业微信通知」插件（默认 `wecom-notify`），
#     企业 ID / Secret / 收件人全部由它保管，本插件不持有这些凭据。
CH_TG = "tg"
CH_WECOM = "wecom"
VALID_CHANNELS = (CH_TG, CH_WECOM)
CHANNEL_LABELS = {CH_TG: "Telegram", CH_WECOM: "微信"}

TELEGRAM_API = "https://api.telegram.org"

# 通知正文上限：企业微信文本消息单条约 2048 字节，Telegram 单条 4096 字符。
# 通知只给「概览 + 前 N 条」，完整清单留在 ttd 结果页 —— 太长的正文既不便阅读，
# 也容易被目标端截断或分段。
NOTIFY_MAX_CHARS = 3200
NOTIFY_MAX_ITEMS = 20
DEFAULT_WECOM_PLUGIN_ID = "wecom-notify"

# 执行功能
FUNC_CHECK = "check"
FUNC_FILL = "fill"
FUNC_TEST = "test"
FUNC_CONFIG = "config"
# 「从头开始」：只清空扫描进度（`scan_cursor.json`），**不运行检测、不补齐**、也不发通知。
# 为什么要有这个入口：进度游标是「上次扫到哪」的唯一状态，媒体库删改过、换过媒体库、
# 或单纯想重新做一轮完整扫描时，用户需要一个**明确且无副作用**的方式把它归零 ——
# 否则只能自己进容器找 data_dir 删文件。它不读 Emby / TgtoDrive，所以配置有问题时也能用。
FUNC_RESET = "reset"
VALID_FUNCS = (FUNC_CHECK, FUNC_FILL, FUNC_TEST, FUNC_CONFIG, FUNC_RESET)
FUNC_LABELS = {
    FUNC_CHECK: "仅检测缺失（只读）",
    FUNC_FILL: "检测并补齐",
    FUNC_TEST: "测试连接",
    FUNC_CONFIG: "查看生效配置",
    FUNC_RESET: "从头开始（清空扫描进度）",
}

# 补齐动作
ACTION_RECORD = "record"
ACTION_TRANSFER = "transfer"
ACTION_OFFLINE = "offline"
VALID_ACTIONS = (ACTION_RECORD, ACTION_TRANSFER, ACTION_OFFLINE)
ACTION_LABELS = {
    ACTION_RECORD: "仅记录并列出链接",
    ACTION_TRANSFER: "转存到网盘",
    ACTION_OFFLINE: "提交离线下载（磁力 / 电驴 / 种子）",
}

# 搜索源
SOURCE_BUILTIN = "builtin"
SOURCE_PANSOU = "pansou"
SOURCE_BOTH = "both"
VALID_SOURCES = (SOURCE_BUILTIN, SOURCE_PANSOU, SOURCE_BOTH)
SOURCE_LABELS = {
    SOURCE_BUILTIN: "TgtoDrive 内置资源检索",
    SOURCE_PANSOU: "盘搜（PanSou）",
    SOURCE_BOTH: "两者都查",
}

# 盘搜的网盘类型 → 中文名（取自 PanSou 官方文档）
PANSOU_CLOUD_LABELS = {
    "baidu": "百度网盘", "aliyun": "阿里云盘", "quark": "夸克", "guangya": "光鸭",
    "tianyi": "天翼", "uc": "UC", "mobile": "移动", "115": "115",
    "pikpak": "PikPak", "xunlei": "迅雷", "123": "123", "magnet": "磁力",
    "ed2k": "电驴", "torrent": "种子", "others": "其他",
}
# 「离线下载」接口专收的链接类型：磁力 / 电驴 / 种子。
# TTD 的离线接口文档原话是「将磁力或其他受支持的离线链接提交到所选网盘的指定目录」——
# 目标网盘（115）的离线设置已在 TTD 侧配好，插件只负责提交。
# 种子除了类型名，还可能以 .torrent 后缀的 http 链接出现（盘搜会归到 others），
# 所以判定要走 _is_offline_link()，不能只看类型名。
OFFLINE_TYPES = ("magnet", "ed2k", "torrent")


def _is_offline_link(url, kind=""):
    """判断一条候选是不是「磁力 / 电驴 / 种子」这类**离线下载链接**。

    三条判定路径，宁多认不少认（认成种子顶多多试一次接口，漏认就直接跳过用户唯一可用的资源）：
    ① 类型名命中 `OFFLINE_TYPES`（含 bt / seed 别名）；
    ② URL 是 `magnet:` / `ed2k:` 协议；
    ③ URL 以 `.torrent` 结尾（盘搜把种子归到 others 时就靠这条兜底）。
    """
    low_kind = str(kind or "").strip().lower()
    if low_kind in OFFLINE_TYPES or low_kind in ("bt", "seed"):
        return True
    low_url = str(url or "").strip().lower()
    if low_url.startswith(("magnet:", "ed2k:")):
        return True
    return low_url.endswith(".torrent")


# 转存接口的 `provider` 要传**分享链接所属网盘**（源），取值就是盘搜的网盘类型。
# ⚠️ 不是转存目标网盘 —— 2026-10-15 实测：把目标（115）当 provider 传，TTD 一律
# 409 SHARE_PROVIDER_MISMATCH「分享链接实际为光鸭链接，…」（它按 URL 认出了链接
# 的真实网盘，与提交的 provider 不符）。转存目标由 TTD 自己的影视设置
# （target_provider）决定，这个接口不需要、也不能传。
# magnet / ed2k / torrent 走离线接口，永远到不了转存；others / 未知类型不传，
# 让 TTD 按 URL 自动识别（它的报错原文证明它本来就认得出）。
TRANSFER_SOURCE_PROVIDERS = tuple(
    key for key in PANSOU_CLOUD_LABELS
    if key not in OFFLINE_TYPES and key != "others")


def _api_error_brief(text, limit=160):
    """把接口的错误响应压成**可读的一行**。

    TTD 的错误体是 ``{"code": "...", "error": "中文说明"}``，直接贴原文会看到
    `\\u4efb\\u52a1...` 这种转义码，用户读不出所以然。这里解析出 code/error
    拼成「code：中文说明」；不是 JSON 就退回原文前 `limit` 字。
    """
    raw = str(text or "").strip()
    if not raw:
        return "（接口未返回内容）"
    try:
        data = json.loads(raw)
    except Exception:
        return raw[:limit]
    if isinstance(data, dict):
        code = str(data.get("code") or "").strip()
        error = str(data.get("error") or data.get("message") or "").strip()
        if code or error:
            return ("%s：%s" % (code, error) if code and error else (code or error))[:limit]
    return raw[:limit]


def _is_duplicate_offline_error(status, data, text):
    """判断离线下载的失败是不是「115 任务已存在」。

    115 对**重复提交同一条磁力 / 电驴 / 种子**返回 502 +
    ``{"code":"115_OFFLINE_FAILED","error":"任务已存在，请勿输入重复的任务"}``。
    这不是失败：资源此前已经提交进 115 的离线队列了（本插件多跑几次就会撞上）。
    报成失败会让用户以为没补上，其实 115 那边早就有了 —— 按「已提交」记账，
    但在说明里写清楚「未重复创建」。
    """
    code, error = "", ""
    if isinstance(data, dict):
        code = str(data.get("code") or "")
        error = str(data.get("error") or "")
    if not code and not error:
        error = str(text or "")[:300]      # data 没解析出来时退回原文
    if "任务已存在" in error or "重复" in error:
        return True
    return code == "115_OFFLINE_FAILED" and ("已存在" in error or "重复" in error)

# 补齐动作的**真实执行结论**（_apply_action 返回，_fill_one 记账，_notify_items 分类）。
# 曾经在这里栽过：entry["status"] 在调 _apply_action **之前**就被无条件写成 done，
# 于是「候选是磁力→跳过」「接口报错→失败」也统统算进「② 被成功补全」——
# 用户收到微信以为补齐了，实际网盘里什么都没有。分类只能按真实结论走。
ACT_DONE = "done"          # 真正执行成功（转存 / 离线已提交；仅记录模式 = 链接已列出）
ACT_SKIPPED = "skipped"    # 候选类型与动作不匹配，什么也没做（如转存动作选中磁力）
ACT_FAILED = "failed"      # 执行了，但接口返回错误
ACT_PREVIEW = "preview"    # dry-run：预告将执行，并未真正执行
ACT_NOOP = "noop"          # 兜底：没有可执行的分支

# 本插件**只处理剧集**。Emby 的媒体库会带 CollectionType，这里显式排除非剧集库：
# 电影、音乐、音乐视频、有声书、书籍、家庭视频、合集、照片、游戏、播放列表。
#
# 为什么不能只靠 `IncludeItemTypes=Series`：
#   ① 用户可能把「媒体库 id」填成电影库 / 音乐库 —— 只靠条目类型查询会静默返回 0 条，
#      看起来像插件坏了；显式排除并写进日志与结果页，才能看出是「按设计不生效」；
#   ② 排除项必须可见，否则用户会以为「配了却没起作用」。
# CollectionType 为空（未标注）时**不做判断**，交给条目类型兜底，避免误杀。
NON_TV_LIBRARY_TYPES = ("movies", "music", "musicvideos", "audiobooks", "books",
                        "homevideos", "boxsets", "photos", "games", "playlists")

SECRET_HINTS = ("secret", "token", "password", "passwd", "pwd", "apikey",
                "api_key", "apikey", "credential", "cookie", "authorization")


# ---------------------------------------------------------------------------
# 预编译正则
# ---------------------------------------------------------------------------
# 这些模式都在**按条循环**的路径上（每部剧 / 每季 / 每集 / 每个参数键各调一次）。
# 写成 `re.sub("字面量", …)` 每次都要走一遍「字符串 → 缓存查找」，量大了就是白开销；
# 提前编译成常量既省这一次查表，也把「同一个模式在多处出现」收敛成一个来源。
_HTTP_URL_RE = re.compile(r"^https?://", re.I)
_URL_CRED_RE = re.compile(r"(?i)\b([a-z][a-z0-9+.\-]*://)[^/@\s]*:[^/@\s]*@")
_KEY_NORM_RE = re.compile(r"[^a-z0-9]")
_IDS_SPLIT_RE = re.compile(r"[,\uFF0C|;；\s]+")
_WS_SPLIT_RE = re.compile(r"\s+")
_DATE_PREFIX_RE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})")
_SEASON_SPECIAL_RE = re.compile(r"特别|特典|specials?", re.I)
_SEASON_EN_RE = re.compile(r"(?:season|s)\s*0*(\d{1,3})", re.I)
_SEASON_CN_RE = re.compile(r"第\s*0*(\d{1,3})\s*季")
# 剧名归一化：依次抹掉集数标注、季标注、方括号 / 圆括号里的补充说明
_TITLE_EPISODE_RE = re.compile(r"(?i)\bS\d{1,2}(E\d{1,3})?\b")
_TITLE_SEASON_EN_RE = re.compile(r"(?i)\b(season|seasons)\s*\d+")
_TITLE_SEASON_CN_RE = re.compile(r"第\s*[0-9一二三四五六七八九十]+\s*[季部]")
_TITLE_BRACKET_RE = re.compile(r"\[[^\]]*\]")
_TITLE_PAREN_RE = re.compile(r"[（(][^）)]*[）)]")


# ---------------------------------------------------------------------------
# 基础工具
# ---------------------------------------------------------------------------

class _Logger(object):
    """同时写入标准输出（TgtoDrive 运行日志）与内存缓冲区（结果页日志窗口）。"""

    MAX_LINES = 2000

    def __init__(self):
        # 用 deque(maxlen=…) 而不是 list：超过上限时 deque 由 C 层直接把最旧的一行挤掉，
        # 是 O(1)；此前用 list + `del lines[:n]`，**每写一行都要搬移整个列表**
        # （2000 行上限下实测慢 100 倍以上）。长任务（几百部剧）日志必然溢出，
        # 这个差别会被放大到上万行。
        self.lines = deque(maxlen=self.MAX_LINES)

    def _emit(self, level, message):
        line = "[%s] [%s] %s" % (datetime.now().strftime("%H:%M:%S"), level, message)
        self.lines.append(line)      # 超出 maxlen 时自动丢弃最旧的一行
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
        return "\n".join(self.lines)[-limit:]


def _as_bool(value, default=False):
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


def _as_list(value):
    """把「多选」类参数归一化成字符串列表。

    平台把多选值以**列表**传来，但定时计划 / 手工调用可能给单个字符串或 ``None``；
    另外值里可能混着空白项。这里统一成「去空白、丢空项」的列表，调用方不必再判类型。
    """
    if isinstance(value, (list, tuple, set)):
        return [str(item).strip() for item in value if str(item).strip()]
    if value in (None, ""):
        return []
    text = str(value).strip()
    return [text] if text else []


def _finite_int(value):
    """把可能是 ``inf`` / ``nan`` 的值安全地转成 ``int``；转不了返回 ``None``。

    为什么需要单独一个函数：``int(float("inf"))`` 抛的是 **OverflowError**，
    而 ``int(float("nan"))`` 抛的是 ValueError —— 只捕获后者会让 ``inf`` /
    ``1e400`` 这类取值**直接穿透出去**。参数表单是 number 类型，但平台/定时计划
    可能把原始字符串原样带进来；schema-less 的响应里更可能出现任意值。
    这里统一兜住，并且**显式判非有限浮点**，不依赖异常类型。
    """
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        try:
            if value != value or value in (float("inf"), float("-inf")):
                return None
            return int(value)
        except (ValueError, OverflowError, TypeError):
            return None
    text = str(value or "").strip()
    if not text:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    if number != number or number in (float("inf"), float("-inf")):
        return None
    try:
        return int(number)
    except (ValueError, OverflowError, TypeError):
        return None


def _as_int(value, default=0):
    number = _finite_int(value)
    return default if number is None else number


def _is_secret_key(key):
    """键名含凭据特征片段即视为敏感（归一化后比较，比枚举更抗新增字段）。"""
    norm = _KEY_NORM_RE.sub("", str(key or "").lower())
    if not norm:
        return False
    return any(hint.replace("_", "") in norm for hint in SECRET_HINTS)


def _mask(value, keep=4):
    """凭据只留末尾几位。

    保留位数不能超过原长的 1/3（且至少 1 位）—— 否则一个 5 位的短凭据会露出 4 位，
    等于把「脱敏」做成了「几乎明文」。短到只剩 1 位可露时就露 1 位，更短则全星号。
    """
    text = str(value or "")
    if not text:
        return "（未填写）"
    keep = max(1, min(keep, len(text) // 3))
    if len(text) <= keep:
        return "*" * len(text)
    return "***%s" % text[-keep:]


def _scrub_url_credentials(text):
    """把 URL 里的 ``user:pass@`` 抹成 ``***@``。

    参数回显会把「TMDB 代理地址 / Emby 地址 / TgtoDrive 地址 / 盘搜地址」原样打出来，
    而这些地址**可能内嵌凭据**（``http://user:pass@host:8080``）。它们不是"密钥字段"，
    走不到 :func:`_is_secret_key` 那条路 —— 不在这里单独处理就会把凭据写进日志。
    """
    return _URL_CRED_RE.sub(r"\1***@", str(text or ""))


def _mask_params(params, max_len=600):
    """把参数渲染成可安全写进日志的一行（敏感键只回显长度，URL 内嵌凭据会被抹掉）。"""
    if not isinstance(params, dict) or not params:
        return "（空）"
    parts = []
    for key, value in params.items():
        if _is_secret_key(key):
            text = "***（已填写，长度 %d）" % len(str(value)) if value else "（空）"
        else:
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            text = _scrub_url_credentials(str(text).replace("\n", "\\n"))
            if len(text) > max_len:
                text = text[:max_len] + "…（共 %d 字）" % len(str(value))
        parts.append("%s=%s" % (key, text))
    return " | ".join(parts)


def scrub_text(text, secrets=()):
    """抹掉文本中可能出现的凭据。

    本插件的凭据都放在请求头里（TTD 的 `Authorization: Bearer`、Emby 的 `X-Emby-Token`、
    盘搜的 `Authorization: Bearer`），一般不随 URL 回显；但 `requests` 的异常消息会带上
    完整 URL，用户也可能把令牌写进地址（如 `http://user:pass@host`）或查询串。
    阈值取 4：原先的 6 会让短凭据**原样留在日志里** —— 脱敏必须覆盖所有真实长度。
    """
    out = str(text or "")
    for secret in secrets:
        secret = str(secret or "")
        if len(secret) >= 4:
            out = out.replace(secret, "***")
    return out


def _safe_json(text):
    try:
        return json.loads(text)
    except Exception:
        return None


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """拒绝跟随重定向。

    `requests` 那条路已经用了 ``allow_redirects=False``；``urllib`` 默认**会跟随**重定向，
    一旦服务端 302 到外部地址，``Authorization`` 头就会被带过去 —— 与「不把凭据转发到
    外部 URL」的约定冲突。这里让重定向直接以 HTTPError 抛出（会被下面按状态码处理）。
    """

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


# urllib 的 opener **构建**实测约 20 毫秒/次（要重建整套 handler）。因此：
#   * 默认 opener 延迟到首次真正发请求时才建 —— 不让模块导入白付这笔钱；
#   * 带代理的 opener 按「代理配置」缓存 —— TMDB 直连对**每个**请求都显式传 proxies，
#     不缓存的话一次大库扫描会白白多花好几秒（实测 300 次请求 ≈ 6 秒）。
# 插件是同步单线程模型，这里不需要加锁。
_URLLIB_OPENERS = {}


def _urllib_opener(proxies=None):
    """返回（并缓存）与给定代理配置对应的 urllib opener。

    ``proxies`` 语义与 :func:`_http_json` 一致：``None`` = 用默认 opener；
    ``{"http": …, "https": …}``（值可为 ``None``）= 显式指定 / 显式绕过。
    """
    if proxies is None:
        key = None
    else:
        # 转成可哈希且与字典顺序无关的键，保证同一份代理配置复用同一个 opener
        key = frozenset((str(k), "" if v is None else str(v)) for k, v in proxies.items())
    opener = _URLLIB_OPENERS.get(key)
    if opener is None:
        if key is None:
            opener = urllib.request.build_opener(_NoRedirect)
        else:
            handler_map = {scheme: value for scheme, value in proxies.items() if value}
            opener = urllib.request.build_opener(
                _NoRedirect, urllib.request.ProxyHandler(handler_map))
        _URLLIB_OPENERS[key] = opener
    return opener


def _with_query(url, params):
    """把 ``params`` 拼进 URL 的查询串（保留 URL 上已有的查询串）。

    三个客户端都要拼查询串，此前同一段 ``url += ("&" if "?" in url else "?") + urlencode(...)``
    各写了一遍 —— 收敛到这里，顺便保证「空 params 不产生一个多余的 ``?``」。
    """
    if not params:
        return url
    return url + ("&" if "?" in url else "?") + urllib.parse.urlencode(params)


def _is_http_url(value):
    """判断是不是 http(s) 地址（``configured`` 属性共用）。"""
    return bool(_HTTP_URL_RE.match(str(value or "").strip()))


def _http_json(method, url, headers=None, body=None, timeout=None, proxies=None):
    """发 JSON 请求，返回 ``(status, text, data)``；网络异常时 status 为 None。

    ``proxies`` 用 ``requests`` 风格的字典（``{"http": …, "https": …}``）。
    传 ``{"http": None, "https": None}`` 表示**显式绕过**容器里的 HTTP_PROXY / HTTPS_PROXY
    —— 那个环境变量常常是平台侧内部代理，跟着它出网会被送到错误的地方（实测 502）。
    传 ``None``（默认）则沿用 requests / urllib 的默认行为。
    """
    headers = dict(headers or {})
    timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
    if requests is not None:
        try:
            response = requests.request(method, url, headers=headers, json=body,
                                        timeout=timeout, allow_redirects=False,
                                        proxies=proxies)
            text = response.text or ""
            return response.status_code, text, _safe_json(text)
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc), None

    data = None
    if body is not None:
        data = json.dumps(body, ensure_ascii=False).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    request = urllib.request.Request(url, data=data, headers=headers, method=method.upper())
    try:
        with _urllib_opener(proxies).open(request, timeout=READ_TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
            return response.status, text, _safe_json(text)
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        return exc.code, text, _safe_json(text)
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc), None


def _first_env_proxy():
    """从环境变量里取第一个非空的代理地址（HTTPS 优先）。取不到返回空串。"""
    for key in ("HTTPS_PROXY", "https_proxy", "HTTP_PROXY", "http_proxy"):
        value = str(os.environ.get(key) or "").strip()
        if value:
            return value
    return ""


def _requests_proxies(proxy):
    """把单个代理地址转成 ``requests`` 的 ``proxies`` 字典。

    注意：``proxy`` 为空串时返回的是 ``{"http": None, "https": None}`` —— 这是
    **显式不走代理**，与 ``None``（沿用环境变量）语义完全不同，两者不能混用。
    """
    if proxy:
        return {"http": proxy, "https": proxy}
    return {"http": None, "https": None}


# ---------------------------------------------------------------------------
# 通知相关的小工具（机器人采集 / 任务结果下沉 / 代理脱敏）
# ---------------------------------------------------------------------------

def _mask_proxy(value):
    """代理地址脱敏：保留协议与主机，把可能存在的账号密码抹成 ``***``。"""
    text = str(value or "")
    if "@" in text:
        scheme, sep, rest = text.partition("://")
        if sep and rest:
            return "%s://***@%s" % (scheme, rest.split("@", 1)[1])
    return text


def _is_primary_name(name):
    """判断某个机器人是不是「主机器人」（ttd 允许给机器人起备注名）。"""
    text = str(name or "").strip().lower()
    return text in ("主", "主机器人", "main", "primary", "默认", "default") or "主" in text


def _collect_bots(payload, source):
    """从 `/api/notify-bots`（或 `/api/proxy_settings`）的响应里启发式找出 Telegram 机器人。

    该接口在规范里标 ``generic``（响应无 schema），历史上出现过几种形态：顶层列表、
    ``data.list`` / ``settings`` 包裹、扁平对象。这里一律兼容，并返回
    ``(可用机器人, 被跳过的条目名)`` —— 跳过的名字要能在日志里说明，
    否则用户会以为「配了机器人却没读到」是插件坏了。
    """
    bots, skipped = [], []

    def consider(node, index):
        if not isinstance(node, dict):
            return
        name = None
        for key in ("name", "remark", "title", "label", "bot_name"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                name = value.strip()
                break
        token = None
        for key in ("token", "bot_token", "botToken", "tg_token", "telegram_token"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                token = value.strip()
                break
        chat_id = None
        for key in ("chat_id", "chatId", "user_id", "admin_user_id", "target",
                    "target_id", "to", "receiver"):
            value = node.get(key)
            if value not in (None, "") and not isinstance(value, (dict, list)):
                chat_id = str(value).strip()
                break
        proxy = None
        for key in ("proxy", "proxy_url", "proxyUrl"):
            value = node.get(key)
            if isinstance(value, str) and value.strip():
                proxy = value.strip()
                break
        kind = str(node.get("type") or node.get("bot_type")
                   or node.get("provider") or "").strip().lower()
        if not name:
            name = "机器人 %d" % index
        if not token or not chat_id:
            skipped.append(name)
            return
        # 类型明确写着非 Telegram（企业微信等）的条目排除掉
        if kind and ("wecom" in kind or "wechat" in kind or "work" in kind
                     or "qy" in kind):
            skipped.append(name)
            return
        if ":" not in token:
            # Telegram bot token 形如 ``123456:ABC-DEF…``，不带冒号的通常不是
            skipped.append(name)
            return
        bots.append({"name": name, "token": token, "chat_id": chat_id,
                     "proxy": proxy, "type": kind, "source": source})

    if isinstance(payload, list):
        for index, node in enumerate(payload, 1):
            consider(node, index)
    elif isinstance(payload, dict):
        candidates = []
        for key in ("list", "bots", "items", "data", "settings", "notify_bots"):
            value = payload.get(key)
            if isinstance(value, list):
                candidates = value
                break
            if isinstance(value, dict):
                for inner_key in ("list", "bots", "items"):
                    if isinstance(value.get(inner_key), list):
                        candidates = value[inner_key]
                        break
                if candidates:
                    break
        if not candidates and any(
                isinstance(payload.get(k), str) and payload.get(k)
                for k in ("token", "bot_token", "botToken")):
            candidates = [payload]
        for index, node in enumerate(candidates, 1):
            consider(node, index)
    return bots, skipped


def descend_result(data, depth=5):
    """把插件任务查询响应一路下沉到**最内层**的结果对象。

    ``GET /api/toolbox/plugins/jobs/{id}`` 没有响应 schema，任务对象可能被包在
    ``result`` / ``job`` / ``data`` / ``task`` 里的任意一层（甚至多层）。只取一层会读到
    「包裹本身」，把 ``delivery_ok`` 这类字段全丢掉 —— 仓库里曾因此把「没送达」显示成
    「已发送」。这里逐层下沉到底，并用层数上限防止自引用。
    """
    node = data if isinstance(data, dict) else {}
    for _ in range(depth):
        child = None
        for key in ("result", "job", "data", "task"):
            value = node.get(key)
            if isinstance(value, dict) and value:
                child = value
                break
        if child is None:
            break
        node = child
    return node



def _url_seg(value):
    """把值安全地放进 URL 的**路径段**。

    TMDB id 来自 Emby 的 ``ProviderIds``、季号来自解析结果 —— 都不能假定它规整：
    里面若有 ``/`` ``?`` ``#`` 就会把请求拼到别的路径上去（甚至会顺带改写查询串）。
    这里按「整段转义」处理，正常的数字串不受影响。
    """
    return urllib.parse.quote(str(value if value is not None else "").strip(), safe="")


def _walk_dicts(node, max_depth=8, limit=3000):
    """深度优先遍历所有 dict（含嵌套），用于容错解析字段名不保证的响应。"""
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


def _split_ids(text):
    return [x.strip() for x in _IDS_SPLIT_RE.split(str(text or "")) if x.strip()]


# 内置兜底表：与 plugin.json 的 inputs 默认值保持一致（改清单时同步）。
# 用途见 _manifest_input_defaults()。
FALLBACK_INPUT_DEFAULTS = {
    "func": FUNC_CHECK,
    "tgto_base_url": DEFAULT_BASE_URL,
    "tgto_token": "",
    "emby_url": "",
    "emby_api_key": "",
    "library_ids": "",
    "pansou_url": DEFAULT_PANSOU_URL,
    "pansou_token": "",
    "max_series": 50,
    "only_aired": True,
    "only_season_exist": True,
    "include_s00": False,
    "ignore_series": "",
    "dry_run": True,
    "fill_action": ACTION_RECORD,
    "search_source": SOURCE_BOTH,
    "pansou_cloud_types": "115,quark,aliyun",
    "max_fill_per_run": 1,
    "resource_sources": "",
    "target_dir": "",
    # 「应有季集」的数据源与凭据（填了 tmdb_api_key 且数据源为 auto/direct 时直连 TMDB）
    "tmdb_source": TMDB_SRC_AUTO,
    "tmdb_api_key": "",
    "tmdb_base_url": DEFAULT_TMDB_BASE,
    "tmdb_language": DEFAULT_TMDB_LANGUAGE,
    "tmdb_proxy": "",
    "tmdb_proxy_mode": TMDB_PROXY_AUTO,
    # 运行结果通知：默认一个都不勾（不改变已有用户的行为）
    "notify_channels": [],
    "notify_bot": 0,
    "wecom_plugin_id": DEFAULT_WECOM_PLUGIN_ID,
    "wecom_touser": "",
}


def _manifest_input_defaults(plugin_dir):
    """返回本插件清单里各 input 的默认值 ``{name: default}``。

    **为什么需要它**：TgtoDrive 的运行接口会按插件清单把**所有** inputs 用默认值填齐
    再交给插件（实测：调用方只传 2 个键，插件却收到 20+ 个键）。于是「值非空」
    不再等于「调用方显式传了」——像本插件的「TgtoDrive 地址」默认值是
    ``http://127.0.0.1:12366``，若不区分，用户在容器环境变量里配的地址就会被它顶掉。

    读取顺序（任一成功即返回）：``plugin_dir`` 附近的 ``plugin.json``
    → 单文件自身源码顶层的 ``PLUGIN_MANIFEST`` → 内置兜底表。
    """
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
    try:
        import ast
        source = Path(__file__).read_text(encoding="utf-8")
        for node in ast.parse(source).body:
            if isinstance(node, ast.Assign) and any(
                    isinstance(t, ast.Name) and t.id == "PLUGIN_MANIFEST"
                    for t in node.targets):
                defaults = _defaults_from_manifest(ast.literal_eval(node.value))
                if defaults:
                    return defaults
                break
    except Exception:
        pass
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


def _norm_title(text):
    """剧名归一化：去掉季/集标注与常见噪声，便于搜索与匹配。"""
    t = str(text or "")
    t = _TITLE_EPISODE_RE.sub(" ", t)
    t = _TITLE_SEASON_EN_RE.sub(" ", t)
    t = _TITLE_SEASON_CN_RE.sub(" ", t)
    t = _TITLE_BRACKET_RE.sub(" ", t)
    t = _TITLE_PAREN_RE.sub(" ", t)
    t = t.replace(".", " ").replace("_", " ")
    t = _WS_SPLIT_RE.sub(" ", t).strip(" -·")
    return t


def _is_relevant(candidate, title):
    """粗筛：候选标题里既不含剧名关键词就丢掉（**只用于盘搜结果**）。

    盘搜是聚合搜索，常返回大量同名 / 蹭名的其它资源，需要按剧名粗筛；
    而 TgtoDrive 内置检索是**按 title 精确查询**的，其结果不该再被标题关键词二次筛掉 ——
    它的 `note` 可能只是「更新至第 10 集」这类不含剧名的文本，此前两路结果统一过滤，
    会把正确的内置候选误杀。判定不出关键词时（剧名全是符号等）不做过滤，避免误杀。
    """
    key_tokens = [tok for tok in _WS_SPLIT_RE.split(str(title or "").lower()) if len(tok) >= 2]
    note = str((candidate or {}).get("note") or "").lower()
    if not note or not key_tokens:
        return True
    return any(tok in note for tok in key_tokens)


# ---------------------------------------------------------------------------
# 「这个资源包到底覆盖了哪些集」
# ---------------------------------------------------------------------------
# 搜索源返回的候选里既有**单集**、也有**部分集**、也有**整季包**。不带判断地挑一个就执行，
# 很容易挑到根本不含缺失集的包（例如缺 E04-E12，却选中了「S01E01」）—— 转存它会白白占用
# 网盘、消耗会员点数，而且结果页还显示「已提交」，用户以为补上了。
#
# 判断依据只有候选的标题 / 描述文本（`note`），所以结论分三态：
#   * 明确是整季 / 全集包 → 视为覆盖**全部**缺失集；
#   * 明确列出了集号     → 取它与缺失集的**交集**（单集也走这条）；
#   * 认不出来           → **绝不能当成「不覆盖」**（保守放行，只标注「覆盖未知」）。
# 只有「明确列出集号、且与缺失集无交集」才判定为「不含缺失集」并排除。

# 先剔除**带数字的画质 / 编码 / 年份噪声**，否则「全1080P」会被当成「第 1080 集」、
# 「2019」会被当成「第 2019 集」。只剔数字型噪声，非数字的（hevc / web-dl）不影响集号识别。
_QUALITY_NOISE_RE = re.compile(
    r"(?i)(?:(?<!\d)(?:2160|1440|1080|720|576|480)\s*p(?![a-z0-9])|"
    r"(?<!\d)[48]\s*k(?![a-z0-9])|"
    r"(?<!\d)\d{1,2}\s*bit(?![a-z0-9])|"
    r"(?<!\d)\d{2,3}\s*fps(?![a-z0-9])|"
    r"(?<!\d)x26[45](?!\d)|(?<!\d)h\.?26[45](?!\d)|(?<!\d)hdr10(?!\d)|"
    r"(?<!\d)(?:19|20)\d{2}(?!\d))")

# 「第01-12集」「01-12集」「第01集-第12集」「更新至第10集」
_EP_RANGE_CN_RES = (
    re.compile(r"第?\s*(\d{1,4})\s*[-~～－—–至到]\s*第?\s*(\d{1,4})\s*[集话話期]"),
    re.compile(r"第?\s*(\d{1,4})\s*[集话話期]\s*[-~～－—–至到]\s*第?\s*(\d{1,4})\s*[集话話期]"),
)
# 「E01-E12」「EP01-12」，以及带季号的「S01E01-E06」
# 前面的否定断言只排除**字母**（不能用 `[a-z0-9]`）—— 否则「S01E01-E06」里 `E01` 前面是数字 `1`，
# 会被挡掉，结果只认出单集 E01，把整段区间丢了。
_EP_RANGE_EN_RE = re.compile(
    r"(?<![a-z])E(?:P)?\s*0*(\d{1,3})\s*[-~～－—–]\s*(?:E(?:P)?\s*)?0*(\d{1,3})(?![0-9])",
    re.I)
# 「更新至第 10 集」→ 1..N
_EP_UPTO_RE = re.compile(r"(?:更新至|更新到|已更新至|已更新)\s*第?\s*(\d{1,4})\s*[集话話期]?")
# 「全12集」
_EP_ALL_CN_RE = re.compile(r"全\s*(\d{1,4})\s*[集话話期]")
# 「第05集」「第5话」
_EP_SINGLE_CN_RE = re.compile(r"第\s*(\d{1,4})\s*[集话話期]")
# 「S01E05」
_EP_SE_RE = re.compile(r"(?<![a-z0-9])S\s*(\d{1,2})\s*E\s*0*(\d{1,3})(?![0-9])", re.I)
# 裸的「E05」「EP5」（欧美命名常见：Show.Name.E05.1080p）—— 前后不能紧邻字母/数字，
# 避免命中 hevc / av1 这类编码名里的字母数字组合。
_EP_BARE_EN_RE = re.compile(r"(?<![a-z0-9])E(?:P)?\s*0*(\d{1,3})(?![0-9a-z])", re.I)
# 明确「整季 / 全集」的标记（没写出集号时）
_FULL_PACK_MARKERS = ("全集", "全季", "整季", "合集", "打包", "完整版", "season pack",
                      "complete season", "complete")

# 一季的集号不会超过这个值；超出的一律不认（宁可判「未知」，也不要认出错集号）
_MAX_EPISODE_NUMBER = 500


def _add_episode_range(target, start, end):
    """把 ``start..end`` 并入集号集合；参数不合法或区间过大时什么都不做。"""
    start, end = _finite_int(start), _finite_int(end)
    if start is None or end is None:
        return
    if not (0 < start <= _MAX_EPISODE_NUMBER and 0 < end <= _MAX_EPISODE_NUMBER):
        return
    if end < start:
        start, end = end, start
    if end - start > _MAX_EPISODE_NUMBER:
        return
    target.update(range(start, end + 1))


def _parse_episode_coverage(text):
    """从候选标题里读出它覆盖的集号。

    返回 ``(kind, numbers)``：

    * ``("all", set())``      —— 明确是**整季 / 全集包**（没有集号限制）；
    * ``("episodes", {…})``   —— 明确只覆盖这些集（单集也在这里）；
    * ``("unknown", set())``  —— **认不出来**。调用方必须把它当作「不知道」而不是「不覆盖」。
    """
    raw = str(text or "")
    if not raw.strip():
        return "unknown", set()
    cleaned = _QUALITY_NOISE_RE.sub(" ", raw)

    numbers = set()
    for pattern in _EP_RANGE_CN_RES:
        for m in pattern.finditer(cleaned):
            _add_episode_range(numbers, m.group(1), m.group(2))
    for m in _EP_RANGE_EN_RE.finditer(cleaned):
        _add_episode_range(numbers, m.group(1), m.group(2))
    for m in _EP_UPTO_RE.finditer(cleaned):
        _add_episode_range(numbers, 1, m.group(1))
    for m in _EP_ALL_CN_RE.finditer(cleaned):
        _add_episode_range(numbers, 1, m.group(1))
    for m in _EP_SINGLE_CN_RE.finditer(cleaned):
        _add_episode_range(numbers, m.group(1), m.group(1))
    for m in _EP_SE_RE.finditer(cleaned):
        _add_episode_range(numbers, m.group(2), m.group(2))
    if not numbers:
        # 裸 E05 放最后：只有在「其它写法都没认出来」时才用它，减少误判面
        for m in _EP_BARE_EN_RE.finditer(cleaned):
            _add_episode_range(numbers, m.group(1), m.group(1))

    if numbers:
        return "episodes", numbers
    low = cleaned.lower()
    if any(marker in low for marker in _FULL_PACK_MARKERS):
        return "all", set()
    return "unknown", set()


def _episode_coverage(note, missing):
    """判断候选覆盖了缺失集里的哪些。

    返回 ``(state, covered, label)``；``state`` 取值与含义：

    * ``all``     —— 自述为整季 / 全集包 → 视为覆盖全部缺失集；
    * ``full``    —— 读出的集号**完全包含**缺失集；
    * ``partial`` —— 只覆盖**一部分**缺失集（单集资源通常落在这里）；
    * ``none``    —— 读出了集号，但与缺失集**没有任何交集** → 应当排除；
    * ``unknown`` —— 读不出来 → **不能**当成不覆盖。
    """
    wanted = {n for n in (missing or []) if isinstance(n, int)}
    kind, numbers = _parse_episode_coverage(note)
    if kind == "unknown":
        return "unknown", set(), "覆盖未知（标题里没有集号）"
    if kind == "all":
        return "all", set(wanted), "整季 / 全集包"
    if not wanted:
        return "unknown", set(), "覆盖未知（本季没有具体缺失集）"
    covered = numbers & wanted
    if not covered:
        return "none", set(), "不含缺失集（包内是 %s）" % (_join_nums(sorted(numbers), limit=4) or "其它集")
    if covered >= wanted:
        return "full", covered, "完整覆盖 %s" % _join_nums(sorted(covered))
    return "partial", covered, "仅覆盖 %s（缺 %s）" % (
        _join_nums(sorted(covered)), _join_nums(sorted(wanted - covered)))


# ---------------------------------------------------------------------------
# 三个客户端
# ---------------------------------------------------------------------------

class _TtdClient(object):
    """TgtoDrive OpenAPI 客户端（读 TMDB 详情 / 内置资源检索 / 转存 / 离线 / 插件调用）。"""

    def __init__(self, base_url, token, logger, timeout=None):
        self.base_url = str(base_url or DEFAULT_BASE_URL).rstrip("/")
        self.token = str(token or "").strip()
        self.log = logger
        self.timeout = timeout
        self._settings_cache = None

    @property
    def configured(self):
        return bool(self.token) and _is_http_url(self.base_url)

    def describe(self):
        return "%s｜令牌 %s" % (self.base_url, _mask(self.token))

    def _headers(self):
        return {"Authorization": "Bearer %s" % self.token} if self.token else {}

    def request(self, method, path, body=None, params=None):
        status, text, data = _http_json(
            method, _with_query(self.base_url + path, params),
            headers=self._headers(), body=body, timeout=self.timeout)
        return status, text, data

    def get_json(self, path, params=None):
        status, text, data = self.request("GET", path, params=params)
        if status is None:
            raise RuntimeError("请求 %s 失败：%s" % (path, scrub_text(text, [self.token])))
        if not 200 <= status < 300:
            raise RuntimeError("请求 %s 返回 HTTP %s：%s"
                               % (path, status, scrub_text((text or "")[:200], [self.token])))
        return data

    def get_soft(self, path, params=None):
        """GET，**不抛异常**：返回 ``(status, data, error)``，供「某一季读不到不影响其它季」的场景使用。

        为什么需要它：`_expected_episodes()` 按季发请求，某一季 404（TMDB 没有这季）或临时
        失败，都不该把**整部剧**打成错误。调用方需要拿到状态码才能区分
        「TMDB 确实没有这一季」（可安全跳过）与「请求失败」（应计为无法判定）。
        """
        status, text, data = self.request("GET", path, params=params)
        if status is None:
            return None, None, scrub_text(text, [self.token])[:160]
        if not 200 <= status < 300:
            return status, None, scrub_text((text or "")[:160], [self.token])
        return status, data, ""

    def post_json(self, path, body):
        status, text, data = self.request("POST", path, body=body)
        return status, text, data

    # -- TgtoDrive 自身的影视资源配置（本插件只读，不改动） ----------------

    def media_settings(self):
        """影视发现基础配置：转存目标网盘、转存目录、点数上限、Emby、RE0 等。

        本轮内缓存：`_ensure_emby()`、`_load_ttd_config()`、`do_test()` 都要读它，
        不缓存就会在每次运行里重复请求同一个接口。
        """
        if self._settings_cache is None:
            self._settings_cache = self.get_json("/api/media/settings")
        return self._settings_cache

    def media_providers(self):
        """可用的榜单、片库、**资源来源**及**网盘转存目标**（无响应 schema，需容错解析）。"""
        return self.get_json("/api/media/providers")

    def media_capabilities(self):
        """当前服务支持的**资源检索 / 转存 / 离线**能力。"""
        return self.get_json("/api/media/capabilities")

    def re0_status(self):
        """RE0 主账号授权与账号状态。

        接口说明原文：「读取 RE0 主账号授权和账号状态，**判断资源检索、解锁及转存等
        RE0 功能是否可用**」—— 也就是说 RE0 是 TgtoDrive 自己集成的服务，
        能不能用它取决于这里的授权状态，本插件不该再让用户填一份 RE0 凭据。
        """
        return self.get_json("/api/re0/status")

    # -- 调用其它插件（本插件用它把通知交给「企业微信通知」） ----------------

    def run_plugin(self, plugin_id, params):
        """提交一次插件运行任务，返回 ``(status, text, data)``。

        注意 body 形态是 ``{"params": {...}}`` —— 与 ttd-daily-digest / wecom-call-demo
        保持一致；**不要**带 ``save_settings``（那会把调用方的临时参数写进对方设置）。
        """
        return self.post_json("/api/toolbox/plugins/%s/run" % _url_seg(plugin_id),
                              {"params": params})

    def plugin_job(self, job_id):
        """查询插件任务结果，返回 ``(status, text, data)``。"""
        return self.request("GET", "/api/toolbox/plugins/jobs/%s" % _url_seg(job_id))

    def plugin_manifest(self, plugin_id):
        """读取某个插件的清单（用于发送前确认它装了、启用、且支持 ``envelope``）。

        列表接口同样没有响应 schema，条目可能直接是 ``plugins`` 数组，也可能被包在
        ``data`` 里；读不到就返回 ``None``，由调用方给出可操作提示。
        """
        status, _text, data = self.request("GET", "/api/toolbox/plugins")
        if status is None or not 200 <= status < 300 or not isinstance(data, dict):
            return None
        items = data.get("plugins")
        if not isinstance(items, list):
            inner = data.get("data")
            items = inner if isinstance(inner, list) else []
        for item in items:
            if isinstance(item, dict) and item.get("id") == plugin_id:
                return item
        return None


class _TmdbClient(object):
    """TMDB 直连客户端（``api.themoviedb.org``），**不经过** TgtoDrive 的详情代理。

    为什么会有这个类
    ----------------
    TgtoDrive 的 ``/api/media/details/tmdb/tv/{id}/season/{n}`` 在规范里写明
    「**只有当前详情配置支持完整季集模式时可用**」；该模式在没有开启的环境里会直接返回
    HTTP 409 ``TMDB_READONLY_MODE_INACTIVE``。缺集检测完全依赖「每一季应该有哪些集」，
    该接口一不可用，整条链路就没了数据源 —— 直连 TMDB 不受这个约束。

    代理
    ----
    API Key 是走**查询参数**的（TMDB v3 规范），因此任何回显都要脱敏；
    容器出网往往需要代理，这里按调用方给的**候选列表**逐个尝试，
    只在「代理 / 网关层错误」（:data:`PROXY_LAYER_STATUS`）时才换下一个 ——
    拿不到 HTTP 响应或拿到网关错误，说明请求没到 TMDB，重试是安全的。
    """

    def __init__(self, api_key, base_url, language, logger, timeout=None,
                 proxy_candidates=None):
        self.api_key = str(api_key or "").strip()
        base = str(base_url or "").strip() or DEFAULT_TMDB_BASE
        self.base_url = base.rstrip("/")
        self.language = str(language or DEFAULT_TMDB_LANGUAGE).strip()
        self.log = logger
        self.timeout = timeout
        # [(代理地址, 说明), …]，最后一项固定是 ("", "直连")。为空时按「直连」处理。
        self.proxy_candidates = list(proxy_candidates or [])
        self.last_proxy_note = ""

    @property
    def configured(self):
        return bool(self.api_key) and _is_http_url(self.base_url)

    def describe(self):
        return "%s｜API Key %s" % (self.base_url, _mask(self.api_key))

    def _params(self, extra=None):
        params = {"api_key": self.api_key}
        if self.language:
            params["language"] = self.language
        if extra:
            params.update(extra)
        return params

    def request(self, path, params=None):
        """GET 一个 TMDB 接口，返回 ``(status, data, error)``；**不抛异常**。

        按 ``proxy_candidates`` 逐个尝试，成功即止。
        """
        url = self.base_url + path
        url = _with_query(url, self._params(params))
        attempts = self.proxy_candidates or [("", "直连")]
        last = ""
        for proxy, label in attempts:
            status, text, data = _http_json("GET", url, timeout=self.timeout,
                                            proxies=_requests_proxies(proxy))
            if status is None:
                # 连不上 = 确定没到 TMDB，换下一个代理是安全的
                last = "%s（经「%s」）" % (scrub_text(text, [self.api_key])[:140], label)
                continue
            if status in PROXY_LAYER_STATUS:
                last = "HTTP %s（经「%s」，来自代理 / 网关）" % (status, label)
                continue
            self.last_proxy_note = label
            return status, data, scrub_text((text or "")[:200], [self.api_key])
        return None, None, last or "所有代理方式都失败"

    def get_json(self, path, params=None):
        """取 JSON；失败抛 RuntimeError（错误信息里 API Key 已脱敏）。"""
        status, data, err = self.request(path, params=params)
        if status is None:
            raise RuntimeError("TMDB 直连请求 %s 失败：%s" % (path, err))
        if not 200 <= status < 300:
            raise RuntimeError("TMDB 直连请求 %s 返回 HTTP %s：%s" % (path, status, err))
        return data

    # -- 业务方法 ---------------------------------------------------------

    def tv_detail(self, tmdb_id):
        """剧集详情：含 ``seasons``（每季的 ``season_number``）与 ``number_of_seasons``。"""
        return self.get_json("/tv/%s" % _url_seg(tmdb_id))

    def tv_season_soft(self, tmdb_id, season):
        """某一季的集数据（含 ``air_date``）。返回 ``(status, data, error)``，**不抛异常**。"""
        return self.request("/tv/%s/season/%s" % (_url_seg(tmdb_id), _url_seg(season)))


class _EmbyClient(object):
    """Emby 直连客户端 —— 本插件唯一能拿到「本地已有哪些集」的途径。"""

    def __init__(self, base_url, api_key, logger, timeout=None):
        base = str(base_url or "").strip().rstrip("/")
        # 用户可能填的是网页入口（形如 http://host:8096/emby），REST 根要去掉这一层。
        # 必须按 **URL 路径**判断，不能用 `base.endswith("/emby")` —— 那样主机名正好叫
        # `emby` 时（如 `http://emby`）会被误当成路径切掉，变成 `http:` 导致全部请求 404。
        if base:
            parsed = urllib.parse.urlsplit(base)
            if parsed.path.rstrip("/").lower() == "/emby":
                base = urllib.parse.urlunsplit(
                    (parsed.scheme, parsed.netloc, parsed.path.rstrip("/")[:-5], "", ""))
                base = base.rstrip("/")
        self.base_url = base
        self.api_key = str(api_key or "").strip()
        self.log = logger
        self.timeout = timeout

    @property
    def configured(self):
        return bool(self.base_url) and bool(self.api_key)

    def describe(self):
        return "%s｜API Key %s" % (self.base_url or "（未填写）", _mask(self.api_key))

    def _headers(self):
        # Emby 既支持 X-Emby-Token 头，也支持 ?api_key= 查询参数；这里用请求头，避免落在日志里
        return {"X-Emby-Token": self.api_key} if self.api_key else {}

    def get_json(self, path, params=None):
        url = _with_query(self.base_url + path, params)
        status, text, data = _http_json("GET", url, headers=self._headers(),
                                        timeout=self.timeout)
        if status is None:
            raise RuntimeError("请求 Emby %s 失败：%s" % (path, scrub_text(text, [self.api_key])))
        if status == 401:
            raise RuntimeError("Emby 拒绝访问（HTTP 401）：API Key 无效或权限不足")
        if not 200 <= status < 300:
            raise RuntimeError("Emby 返回 HTTP %s：%s"
                               % (status, scrub_text((text or "")[:200], [self.api_key])))
        return data

    def test(self):
        info = self.get_json("/System/Info/Public")
        name = ""
        version = ""
        for node in _walk_dicts(info):
            # `/System/Info/Public` 里服务器名就是 `ServerName`（此前这里写成了
            # `ServerName or ServerName`，第二个兜底键永远轮不到，等于没有兜底）
            name = name or str(node.get("ServerName") or "")
            version = version or str(node.get("Version") or "")
        return info, name, version

    def libraries(self):
        """返回 [{id, name, collection_type}]，容错解析。"""
        data = self.get_json("/Library/VirtualFolders")
        nodes = data if isinstance(data, list) else []
        if not nodes:
            # 有的版本会包一层 {"Items": [...]}；按容错原则再找一次
            for node in _walk_dicts(data):
                if isinstance(node.get("Items"), list):
                    nodes = [x for x in node["Items"] if isinstance(x, dict)]
                    break
        out = []
        for node in nodes or []:
            if not isinstance(node, dict):
                continue
            item_id = str(node.get("ItemId") or node.get("Id") or "").strip()
            if not item_id:
                continue
            out.append({
                "id": item_id,
                "name": str(node.get("Name") or "").strip(),
                "type": str(node.get("CollectionType") or "").strip().lower(),
            })
        return out

    def series(self, library_ids=(), limit=0):
        """列出剧集（Series），带上 ProviderIds 以便取 TMDB id。

        **必须按固定规则排序**（这里用 `SortName` 升序）：`_scan_window()` 的「按偏移轮转」
        依赖顺序在多次运行之间保持稳定；若 Emby 每次返回的顺序不同，游标就会指向另一批剧，
        轮转也就失去了意义。
        """
        params = {
            "IncludeItemTypes": "Series",
            "Recursive": "true",
            "Fields": "ProviderIds,ProductionYear,Name",
            "SortBy": "SortName",
            "SortOrder": "Ascending",
        }
        ids = [x for x in library_ids if x]
        if len(ids) == 1:
            params["ParentId"] = ids[0]
        elif ids:
            # 多个库时逐个请求更稳（Emby 的 ParentId 只接受单个）
            merged = []
            for lib in ids:
                merged.extend(self.series((lib,), limit=limit))
            return merged
        data = self.get_json("/Items", params)
        items = []
        for node in _walk_dicts(data):
            if "Items" in node and isinstance(node.get("Items"), list):
                items = [x for x in node["Items"] if isinstance(x, dict)]
                break
        out = []
        for item in items:
            item_id = str(item.get("Id") or "").strip()
            name = str(item.get("Name") or "").strip()
            if not item_id or not name:
                continue
            providers = item.get("ProviderIds") or {}
            tmdb = ""
            if isinstance(providers, dict):
                for key, value in providers.items():
                    if str(key).lower().replace("_", "") == "tmdb" and str(value).strip():
                        tmdb = str(value).strip()
            out.append({
                "id": item_id,
                "name": name,
                "year": _as_int(item.get("ProductionYear"), 0),
                "tmdb": tmdb,
            })
        if limit and len(out) > limit:
            out = out[:limit]
        return out

    def episodes(self, series_id):
        """返回 ``{季号: {集号, …}}``；解析失败返回空字典。"""
        # 用 _url_seg 而不是 urllib.parse.quote：后者的 safe 默认值是 "/"，
        # 一旦 id 里带斜杠就会把请求指到别的路径上去（其它客户端已统一用 _url_seg）。
        data = self.get_json("/Shows/%s/Episodes" % _url_seg(series_id),
                             {"Fields": "ParentIndexNumber,IndexNumber"})
        items = []
        for node in _walk_dicts(data):
            if isinstance(node.get("Items"), list):
                items = [x for x in node["Items"] if isinstance(x, dict)]
                break
        if not items and isinstance(data, list):
            items = [x for x in data if isinstance(x, dict)]
        seasons = {}
        for item in items:
            season = item.get("ParentIndexNumber")
            episode = item.get("IndexNumber")
            if season is None:
                season = item.get("SeasonIndexNumber")
            if episode is None:
                episode = item.get("EpisodeIndexNumber")
            try:
                season = int(season)
                episode = int(episode)
            except (TypeError, ValueError):
                continue
            seasons.setdefault(season, set()).add(episode)
        return seasons


class _PansouClient(object):
    """盘搜（PanSou）客户端。

    接口形态取自官方文档：``POST /api/search``，请求 ``{"kw": …, "res": "merge", …}``，
    响应 ``{"total": n, "results": […], "merged_by_type": {"<网盘类型>": [{"url","password","note","datetime","source"}, …]}}``。
    鉴权可选（``AUTH_ENABLED=true`` 时为 ``Authorization: Bearer <jwt>``）。
    """

    def __init__(self, base_url, token, logger, timeout=None):
        self.base_url = str(base_url or DEFAULT_PANSOU_URL).strip().rstrip("/")
        self.token = str(token or "").strip()
        self.log = logger
        self.timeout = timeout

    @property
    def configured(self):
        return _is_http_url(self.base_url)

    def describe(self):
        return "%s｜令牌 %s" % (self.base_url, _mask(self.token) if self.token else "（未启用鉴权）")

    def _headers(self):
        headers = {"Content-Type": "application/json"}
        if self.token:
            headers["Authorization"] = "Bearer %s" % self.token
        return headers

    def health(self):
        status, text, data = _http_json("GET", self.base_url + "/api/health",
                                        timeout=self.timeout)
        return status, text, data

    def search(self, keyword, cloud_types=(), refresh=False):
        """返回 ``(候选列表, 原始响应, 错误)``；候选为 ``{type,url,password,note,source}``。

        用 ``res="merge"``（PanSou 的默认值）只取按网盘类型归类的 ``merged_by_type`` ——
        相比 ``res="all"`` 少传一份 ``results`` 明细（体积约一半，重复链接本来就靠 URL 去重），
        候选项等价。
        """
        body = {"kw": str(keyword or "").strip(), "res": "merge", "src": "all"}
        if cloud_types:
            body["cloud_types"] = list(cloud_types)
        if refresh:
            body["refresh"] = True
        status, text, data = _http_json("POST", self.base_url + "/api/search",
                                        headers=self._headers(), body=body,
                                        timeout=self.timeout)
        if status is None:
            return [], None, "请求失败：%s" % scrub_text(text, [self.token])
        if not 200 <= status < 300:
            return [], data, "HTTP %s：%s" % (status, scrub_text((text or "")[:200], [self.token]))
        if not isinstance(data, dict):
            return [], data, "响应不是 JSON 对象"
        return _parse_pansou(data), data, ""


# 判定「资源来源」容器的键名线索（小写子串匹配）。
SOURCE_KEY_HINTS = ("source", "resource", "search", "provider", "来源", "检索")
# 明确排除的容器键名（转存目标 / 榜单 / 片库都不是「资源来源」）。
EXCLUDED_KEY_HINTS = ("target", "transfer", "rank", "library", "libraries",
                      "destination", "sink", "save", "dir")


# 「已授权 / 已启用」这类布尔标志的键名（归一化后精确比较）
CAPABILITY_FLAG_KEYS = ("authorized", "enabled", "available", "linked", "bound",
                        "loggedin", "valid", "active")
# 扁平形态下直接当作「能力开关」的布尔键名（子串匹配）
CAPABILITY_FEATURE_HINTS = ("transfer", "offline", "search", "resource", "unlock",
                            "share", "download", "checkin", "subaccount")


def _summarize_capabilities(payload):
    """把 ``/api/media/capabilities`` 的响应折成**可读条目列表**（该接口无 schema，容错）。

    实测响应形态（用户真实环境）：

    ``{"success": true, "data": {"mode": "resources",
       "resource_sources": [{"key": "re0", "label": "RE0"}, …],
       "re0": {"authorized": true}, "guanying": {"authorized": true},
       "seedhub": {"enabled": true}}}``

    此前只挑「键名含 transfer/offline/search/… 的**布尔**字段」，于是这种
    「**子对象里带 authorized/enabled**」的形态被整条忽略，结果页显示
    「未能从响应里识别出能力字段」——其实信息就在里面。现在三路都认：
    ① `mode` 之类的模式串；② 子对象里的 authorized/enabled 标志（带上所在对象的键名）；
    ③ 扁平形态的能力布尔字段。
    """
    out, seen = [], set()

    def add(text):
        if text and text not in seen:
            seen.add(text)
            out.append(text)

    for node in _walk_dicts(payload):
        for key, value in node.items():
            low = str(key).lower().replace("_", "")
            if isinstance(value, str) and low in ("mode", "capabilitymode", "providermode"):
                stripped = value.strip()
                if stripped:
                    add("模式=%s" % stripped)
                continue
            if isinstance(value, bool):
                if any(h in low for h in CAPABILITY_FEATURE_HINTS):
                    add("%s=%s" % (key, "可用" if value else "不可用"))
                continue
            # 子对象里带授权/启用标志：{"re0": {"authorized": true}} → "re0=可用"
            if isinstance(value, dict) and isinstance(key, str) and key:
                for flag in CAPABILITY_FLAG_KEYS:
                    flag_value = value.get(flag)
                    if isinstance(flag_value, bool):
                        add("%s=%s" % (key, "可用" if flag_value else "不可用"))
                        break
    sources = _extract_source_slugs(payload)
    if sources:
        add("可用来源：%s" % "、".join(o["label"] for o in sources[:8]))
    return out[:12]


def _extract_source_slugs(payload):
    """从 ``/api/media/providers`` 的响应里尽力提取「资源来源」标识。

    该接口没有响应 schema（标记 `generic`），所以这里按**容器键名的语义**来判定：
    只看键名含 `source` / `resource` / `search` / `provider` / `来源` / `检索` 的列表，
    并排除含 `target` / `transfer` / `rank` / `library` 的列表 —— 否则「转存目标」、
    「榜单」、「片库」都会混进来源清单（实测踩到过）。

    识别不到时返回空列表：调用方会把**原始响应写进日志**，由用户据此手填。
    宁可漏认，也不把错的值传进 `sources`（那会让检索跑偏或直接失败）。

    返回 ``[{"slug": …, "label": …}, …]``（去重，保持出现顺序）。
    """
    slug_keys = ("slug", "id", "key", "code", "value", "provider")
    label_keys = ("label", "name", "title", "display_name", "displayName", "text")
    out, seen = [], set()

    def take(items):
        for item in items:
            if not isinstance(item, dict):
                continue
            slug = ""
            for key in slug_keys:
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    slug = value.strip()
                    break
            if not slug or slug in seen:
                continue
            label = ""
            for key in label_keys:
                value = item.get(key)
                if isinstance(value, str) and value.strip():
                    label = value.strip()
                    break
            seen.add(slug)
            out.append({"slug": slug, "label": label or slug})

    for node in _walk_dicts(payload):
        for key, value in node.items():
            if not isinstance(value, list):
                continue
            low = str(key).lower()
            if not any(hint in low for hint in SOURCE_KEY_HINTS):
                continue
            if any(hint in low for hint in EXCLUDED_KEY_HINTS):
                continue
            take(value)
    # 顶层直接就是列表的情况（无键名可判）：整包当作来源清单
    if not out and isinstance(payload, list):
        take(payload)
    return out


def _pick_config_value(payload, names):
    """在（无 schema 的）配置响应里按候选键名取第一个非空值。

    允许返回列表 / 字典 —— 例如 `media_transfer_targets` 就是一个列表，
    若只认标量，这类字段会永远取不到值。
    """
    wanted = {str(n).lower().replace("_", "") for n in names}
    for node in _walk_dicts(payload):
        for key, value in node.items():
            if str(key).lower().replace("_", "") not in wanted:
                continue
            if value in (None, "", [], {}):
                continue
            if isinstance(value, (str, int, float, bool, list, tuple, dict)):
                return value
    return None


def _int_or_none(value):
    """同 :func:`_finite_int`，语义是「认不出就返回 None」（供可选数值字段用）。"""
    return _finite_int(value)


def _parse_re0_status(payload):
    """从 ``/api/re0/status`` 的响应里判断 RE0 是否可用。

    返回 ``(True/False/None, 说明)``；``None`` 表示无法判定（该接口标记 `generic`，无 schema）。
    判定策略（双向设防）：先认明确的布尔/状态字段，认不出再按「有没有账号/授权信息」兜底，
    最后才返回「无法判定」—— 不猜测、也不因为字段名不同就断言不可用。
    """
    if not isinstance(payload, dict):
        return None, "响应不是 JSON 对象"
    yes_keys = ("authorized", "is_authorized", "isauthorized", "enabled", "available",
                "linked", "bound", "logged_in", "loggedin")
    for node in _walk_dicts(payload):
        for key, value in node.items():
            norm = str(key).lower().replace("_", "")
            if norm in yes_keys and isinstance(value, bool):
                label = "%s=%s" % (key, value)
                if value:
                    return True, "已授权（%s）" % label
                return False, "未授权（%s）" % label
            if norm in ("status", "state") and isinstance(value, str):
                low = value.strip().lower()
                if low in ("ok", "active", "authorized", "normal", "enabled", "valid",
                           "已授权", "正常"):
                    return True, "状态：%s" % value.strip()
                if low in ("unauthorized", "disabled", "expired", "invalid", "none",
                           "未授权", "已过期", "停用"):
                    return False, "状态：%s" % value.strip()
    # 兜底：出现明确的账号标识就认为有授权信息
    for node in _walk_dicts(payload):
        for key in ("account", "username", "nickname", "user_id", "userId", "uid"):
            value = node.get(key)
            if isinstance(value, (str, int)) and str(value).strip():
                return True, "已存在账号信息（%s）" % scrub_text(str(value)[:20])
    return None, "响应里没有可识别的授权字段（接口无响应 schema）"


def _parse_pansou(payload):
    """把盘搜响应整理成统一的候选列表（按网盘类型分组的结果 + 明细）。"""
    out = []
    seen = set()
    merged = payload.get("merged_by_type") if isinstance(payload, dict) else None
    if isinstance(merged, dict):
        for cloud, items in merged.items():
            for item in items or []:
                if not isinstance(item, dict):
                    continue
                url = str(item.get("url") or "").strip()
                if not url or url in seen:
                    continue
                seen.add(url)
                out.append({
                    "type": str(cloud or item.get("type") or "").strip().lower(),
                    "url": url,
                    "password": str(item.get("password") or "").strip(),
                    "note": str(item.get("note") or "").strip(),
                    "source": str(item.get("source") or "").strip(),
                    "datetime": str(item.get("datetime") or "").strip(),
                })
    results = payload.get("results") if isinstance(payload, dict) else None
    if isinstance(results, list):
        for item in results:
            if not isinstance(item, dict):
                continue
            title = str(item.get("title") or "").strip()
            for link in item.get("links") or []:
                if not isinstance(link, dict):
                    continue
                url = str(link.get("url") or "").strip()
                if not url or url in seen:
                    continue
                seen.add(url)
                out.append({
                    "type": str(link.get("type") or "").strip().lower(),
                    "url": url,
                    "password": str(link.get("password") or "").strip(),
                    "note": str(link.get("work_title") or title).strip(),
                    "source": str(item.get("channel") or "").strip(),
                    "datetime": str(item.get("datetime") or "").strip(),
                })
    return out


# ---------------------------------------------------------------------------
# 执行体
# ---------------------------------------------------------------------------

class _TelegramChannel(object):
    """直接调 Telegram Bot API 发送运行通知（机器人凭据取自 ttd，不落在本插件里）。"""

    key = CH_TG
    label = CHANNEL_LABELS[CH_TG]

    def __init__(self, log, ttd, ttd_proxy="", bot_choice=0):
        self.log = log
        self.ttd = ttd
        self.ttd_proxy_value = str(ttd_proxy or "").strip()
        self.bot_choice = max(_as_int(bot_choice, 0), 0)
        # 选到机器人之后把 Token 记下来，供兜底脱敏用（异常信息里可能带它）
        self._known_tokens = []

    def send(self, text):
        """发一条纯文本通知；返回 ``(ok, 说明)``。

        **任何异常都在这一层收口、不向上抛** —— 通知失败不该让整轮检测 / 补齐
        的结果页取不到；同时异常信息会用已知的 Token 脱敏后再返回。
        """
        try:
            return self._send(text)
        except Exception as exc:
            return False, "发送时异常：%s" % scrub_text(str(exc), self._known_tokens)

    def candidates(self):
        """读 ttd 的通知机器人，返回 ``(可用机器人, 被跳过的条目名)``。"""
        bots, skipped, seen = [], [], set()
        for path in ("/api/notify-bots", "/api/proxy_settings"):
            status, payload, error = self.ttd.get_soft(path)
            if status is None:
                self.log.warn("读取 %s 失败：%s" % (path, error))
                continue
            if status != 200 or payload is None:
                self.log.warn("读取 %s 返回 HTTP %s" % (path, status))
                continue
            found, dropped = _collect_bots(payload, path)
            for bot in found:
                key = (bot["token"], bot["chat_id"])
                if key in seen:
                    continue
                seen.add(key)
                bots.append(bot)
            for name in dropped:
                if name not in skipped:
                    skipped.append(name)
            if bots:
                break
        for index, bot in enumerate(bots, 1):
            bot["index"] = index
        return bots, skipped

    def select(self, bots):
        """按「列表第 N 个」挑选；0 或选不中时回退到主机器人。"""
        usable = [b for b in bots if b["token"] and b["chat_id"]]
        if self.bot_choice > 0:
            target = next((b for b in bots if b["index"] == self.bot_choice), None)
            if target is not None and target["token"] and target["chat_id"]:
                return target
            if target is not None:
                self.log.warn("「列表第 %d 个」机器人（%s）缺少 Token 或推送目标，改用主机器人"
                              % (self.bot_choice, target.get("name") or "-"))
            else:
                self.log.warn("配置里只有 %d 个机器人，不存在「列表第 %d 个」，改用主机器人"
                              % (len(bots), self.bot_choice))
        primary = next((b for b in usable if _is_primary_name(b["name"])), None)
        if primary is not None:
            return primary
        return usable[0] if usable else None

    def _send(self, text):
        """`send()` 的实际实现（外层负责兜异常与脱敏）。"""
        bots, skipped = self.candidates()
        if skipped:
            self.log.info("已排除 %d 个非 Telegram / 缺凭据的条目：%s"
                          % (len(skipped), "、".join(skipped[:6])))
        if not bots:
            # 把「被跳过的条目」也说出来：否则用户明明配了机器人，却只看到
            # 「没读到可用机器人」，完全不知道是缺 Token 还是缺推送目标。
            extra = ("；已跳过 %d 个不可用条目：%s"
                     % (len(skipped), "、".join(skipped[:5])) if skipped else "")
            return False, ("在 ttd 里没读到可用的 Telegram 通知机器人"
                           "（检查「通知机器人」设置是否配了 Token 与推送目标）" + extra)
        bot = self.select(bots)
        if bot is None:
            return False, "读到的机器人条目都缺少 Token 或推送目标"
        self._known_tokens.append(bot["token"])
        self.log.info("通知将使用 Telegram 机器人「%s」（列表第 %s 项）"
                      % (bot["name"], bot["index"]))

        payload = {"chat_id": bot["chat_id"], "text": text,
                   "disable_web_page_preview": True, "disable_notification": False}

        attempts = []
        bot_proxy = (bot.get("proxy") or "").strip()
        env_proxy = _first_env_proxy()

        def push(proxy, label):
            if proxy and all(proxy != item[0] for item in attempts):
                attempts.append((proxy, label))

        # 顺序与 ttd-daily-digest 实测通过的一致：
        #   ttd 自己配的网络代理最可能通 Telegram（容器里的 HTTP_PROXY 常是平台侧
        #   内部代理，出网会 502）→ 机器人自带代理 → 容器环境变量 → 直连兜底。
        if self.ttd_proxy_value:
            push(self.ttd_proxy_value, "ttd 网络代理设置")
        if bot_proxy:
            push(bot_proxy, "机器人自带代理")
        if env_proxy:
            push(env_proxy, "容器环境变量代理")
        attempts.append(("", "直连"))

        self.log.info("通知的 Telegram 连通方式备选 %d 种：%s"
                      % (len(attempts), " → ".join(label for _p, label in attempts)))
        last_error = ""
        for proxy, label in attempts:
            # 逐档留痕（代理地址脱敏）：排查「到底用了哪个代理 / 卡在哪一档」全靠它
            if proxy:
                self.log.info("尝试经「%s」访问 Telegram（%s）" % (_mask_proxy(proxy), label))
            else:
                self.log.info("尝试直连 Telegram（不走代理）")
            try:
                status, body, data = _http_json(
                    "POST", "%s/bot%s/sendMessage" % (TELEGRAM_API, bot["token"]),
                    headers={"Content-Type": "application/json"},
                    body=payload, proxies=_requests_proxies(proxy))
            except Exception as exc:
                # 抛异常 = 连不上，**确定没发出去**，换下一档是安全的
                last_error = "%s（%s）" % (scrub_text(str(exc), [bot["token"]]), label)
                self.log.warn("经「%s」发送失败：%s" % (label, last_error))
                continue
            if status is None:
                last_error = "%s（%s）" % (scrub_text(str(body), [bot["token"]]), label)
                self.log.warn("经「%s」发送失败：%s" % (label, last_error))
                continue
            if status in PROXY_LAYER_STATUS:
                # 这些码来自代理 / 网关本身，说明请求**没到 Telegram** ——
                # 换下一档重试不会造成重复推送。
                last_error = "HTTP %s（%s，来自代理/网关）" % (status, label)
                self.log.warn("经「%s」访问 Telegram 返回 HTTP %s（代理层错误），换下一种方式"
                              % (label, status))
                continue
            # Telegram 自己的响应（200/400/401/403/429…）必须**立刻停** ——
            # 换代理重发会造成重复推送。
            return self._interpret(status, data, bot)
        hint = ""
        if not self.ttd_proxy_value:
            hint = ("；提示：ttd「设置 → 网络代理」里没配代理 —— 若你的网络访问 Telegram "
                    "需要代理，请先在 ttd 里配好")
        return False, ("连接 Telegram 失败，已依次尝试 %d 种方式：%s%s"
                       % (len(attempts), last_error, hint))

    @staticmethod
    def _interpret(status, data, bot):
        """把 Telegram 的响应翻译成 ``(ok, 说明)``。"""
        if status != 200:
            description = ""
            if isinstance(data, dict):
                description = str(data.get("description") or "")[:160]
            hint = ""
            if status == 401:
                hint = "（Token 无效）"
            elif status == 400 and "chat not found" in description.lower():
                hint = "（推送目标 ID 不对，或该用户从未与机器人对话过）"
            elif status == 403:
                hint = "（机器人被屏蔽，或无法主动向该用户发起对话）"
            return False, "Telegram 返回 HTTP %s%s %s" % (status, hint, description)
        if isinstance(data, dict) and data.get("ok") is False:
            return False, "Telegram 拒绝了这条消息：%s" % str(
                data.get("description") or "")[:160]
        message_id = ""
        if isinstance(data, dict):
            result = data.get("result")
            if isinstance(result, dict):
                message_id = str(result.get("message_id") or "")
        return True, "已发送（机器人「%s」%s）" % (
            bot["name"], "message_id=%s" % message_id if message_id else "")


class _WecomChannel(object):
    """把运行通知交给「企业微信通知」插件发送（企业 ID / Secret / 收件人由对方保管）。"""

    key = CH_WECOM
    label = CHANNEL_LABELS[CH_WECOM]

    def __init__(self, log, ttd, plugin_id="", touser=""):
        self.log = log
        self.ttd = ttd
        self.plugin_id = str(plugin_id or "").strip() or DEFAULT_WECOM_PLUGIN_ID
        self.touser = str(touser or "").strip()

    def send(self, text):
        """发一条纯文本通知；返回 ``(ok, 说明)``。异常一律收口并用 ttd 令牌脱敏。"""
        try:
            return self._send(text)
        except Exception as exc:
            return False, "发送时异常：%s" % scrub_text(str(exc), [self.ttd.token])

    def _send(self, text):
        """`send()` 的实际实现（外层负责兜异常与脱敏）。"""
        plugin_id = self.plugin_id

        # 发送前先读目标插件清单，确认它装了、启用、且支持 envelope ——
        # 否则会得到一个难懂的「HTTP 400」
        manifest = None
        try:
            manifest = self.ttd.plugin_manifest(plugin_id)
        except Exception as exc:
            self.log.warn("读取插件清单失败（继续尝试发送）：%s"
                          % scrub_text(str(exc), [self.ttd.token]))
        if manifest is None:
            return False, ("没在 ttd 里找到插件「%s」—— 请确认已安装并启用"
                           "（或把「微信通知插件 id」改成你实际用的那个）" % plugin_id)
        if manifest.get("enabled") is False:
            return False, "插件「%s」已安装但处于停用状态，请先启用" % plugin_id
        inputs = manifest.get("inputs") or []
        declared = {item.get("name") for item in inputs if isinstance(item, dict)}
        if "envelope" not in declared:
            return False, ("插件「%s」不支持 envelope 参数（版本过旧）—— "
                           "请到插件市场把它更新到最新版" % plugin_id)

        envelope = {"version": 1, "msgtype": "text", "content": text,
                    "source": PLUGIN_NAME}
        # 只在**确实填了非空值**时才传 touser：平台的「默认值填齐」行为会把空值顶成 @all，
        # 从而覆盖掉对方插件里已经配好的收件人。
        if self.touser:
            envelope["touser"] = self.touser
            self.log.info("本次将覆盖微信收件人为：%s" % self.touser)
        else:
            self.log.info("未指定微信收件人，沿用「%s」里已保存的设置" % plugin_id)

        params = {"func": "send",
                  "envelope": json.dumps(envelope, ensure_ascii=False)}
        # 平台限制：同一插件同时只能有一个未完成任务，忙碌时返回 HTTP 409。
        # 对方的任务通常很快结束，所以做有限重试（3 次 / 间隔 3 秒）。
        status, body, payload = None, "", None
        for attempt in range(3):
            try:
                status, body, payload = self.ttd.run_plugin(plugin_id, params)
            except Exception as exc:
                return False, "提交任务失败：%s" % scrub_text(str(exc), [self.ttd.token])
            if status != 409:
                break
            detail = ""
            if isinstance(payload, dict):
                detail = str(payload.get("error") or payload.get("message") or "")
            if attempt < 2:
                self.log.warn("目标插件正忙（HTTP 409：%s），3 秒后重试（第 %d/3 次）"
                              % (detail or "队列忙", attempt + 2))
                time.sleep(3)
            else:
                return False, ("目标插件持续处于忙碌状态（HTTP 409：%s）—— "
                               "它的上一个任务还没跑完，稍后再试" % (detail or "队列忙"))

        if status is None:
            return False, "提交任务失败：%s" % scrub_text(str(body), [self.ttd.token])
        if status == 404:
            return False, "目标插件未找到（HTTP 404）—— 未安装或未启用"
        if status in (401, 403):
            return False, "HTTP %s：OpenAPI 令牌无效或权限不足" % status
        if status == 400:
            detail = ""
            if isinstance(payload, dict):
                detail = str(payload.get("message") or payload.get("error") or "")[:160]
            return False, ("HTTP 400：参数被拒（%s）—— 通常是目标插件版本过旧"
                           % (detail or "未知参数"))
        if status == 503:
            return False, "HTTP 503：插件队列已满或对方有未完成任务，稍后重试"
        if status not in (200, 201, 202):
            return False, "提交任务返回 HTTP %s" % status
        if not isinstance(payload, dict):
            return False, "任务响应不是 JSON"

        job_id = payload.get("job_id") or payload.get("id") or payload.get("jobId")
        if not job_id:
            inner = descend_result(payload)
            if inner is not payload:
                job_id = inner.get("job_id") or inner.get("id") or inner.get("jobId")
        if not job_id:
            return False, "任务已受理，但没取到 job_id —— 无法确认是否真的投递"

        self.log.info("微信通知任务已提交，job_id=%s，开始等待结果…" % job_id)
        deadline = time.time() + 60
        last = ""
        seen_state = ""
        while time.time() < deadline:
            try:
                code, text_body, job = self.ttd.plugin_job(job_id)
            except Exception as exc:
                last = "查询任务失败：%s" % scrub_text(str(exc), [self.ttd.token])
                time.sleep(2)
                continue
            if code != 200 or not isinstance(job, dict):
                last = "查询任务返回 HTTP %s" % code
                time.sleep(2)
                continue
            result = descend_result(job)
            state = str(result.get("status") or result.get("state") or "").lower()
            if state:
                seen_state = state
            if state in ("ok", "success", "failed", "error", "timeout"):
                if state not in ("ok", "success"):
                    return False, "目标插件执行失败：%s" % (
                        str(result.get("error") or result.get("message")
                            or "未说明原因")[:200])
                # 必须看投递结论：企业微信对**不在可见范围**的收件人仍返回成功
                if result.get("delivery_ok") is False:
                    detail = result.get("delivery_note") or ""
                    invalid = result.get("invalid_users") or []
                    if invalid:
                        detail = "收件人不在可见范围：%s" % "、".join(
                            str(x) for x in invalid[:5])
                    return False, "已受理但未投递：%s" % (detail or "收件人无效")
                recipient = result.get("recipient") or "未知"
                delivery = str(result.get("delivery_status") or "")
                invalid = result.get("invalid_users") or []
                seg = ""
                total = _as_int(result.get("total"), 0)
                if total:
                    seg = "，成功 %d/%d 段" % (_as_int(result.get("sent"), total), total)
                if delivery == "confirmed" and not invalid:
                    note = "已送达（收件人：%s%s）" % (recipient, seg)
                elif invalid:
                    note = "已发送，但以下收件人不可见、实际未投递：%s（收件人：%s）" % (
                        "、".join(str(x) for x in invalid[:5]), recipient)
                elif delivery == "unknown":
                    # 对方用的是自建转发地址时 user/list 不可用，逐人核对做不了 ——
                    # 但 msgid 已拿到、收件人也没人被判无效，如实说「无法核对」而不是「失败」。
                    note = ("已由「%s」发送（收件人：%s%s）；该接口无法逐人核对投递情况"
                            "（对方用的是自建转发地址），以微信端是否收到为准"
                            % (result.get("channel_name") or "微信", recipient, seg))
                else:
                    note = "已发送（收件人：%s%s）" % (recipient, seg)
                if not any(k in result for k in ("delivery_ok", "delivery_status",
                                                 "recipient", "msgids")):
                    note = "任务已受理（对方未回传投递结论，可能版本过旧）"
                return True, note
            time.sleep(2)
        # 超时时**不能直接判失败**：任务可能仍在跑、消息也可能已经发出去了，
        # 判成失败会把人引去排查一件其实已经成功的事。
        if seen_state in ("running", "pending", "queued", "started", "processing"):
            return False, ("等待结果超时（60 秒）：任务仍在运行（状态 %s）—— "
                           "消息可能已发出，请到微信端确认；若没收到再重试" % seen_state)
        if last:
            return False, "等待结果超时（60 秒）：%s" % last
        return False, ("等待结果超时（60 秒）：任务状态未知 —— "
                       "消息可能已发出，请到微信端确认")


class _Runner(object):

    def __init__(self, params, context):
        context = context if isinstance(context, dict) else {}
        self.p = dict(params or {})
        self.log = _Logger()
        self.data_dir = Path(str(context.get("data_dir") or "."))
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        # 参数回显（敏感项脱敏）—— 与仓库其它插件一致，便于排查「对方没传 / 没接住」
        if self.p:
            self.log.info("收到调用参数（共 %d 个键，敏感项已脱敏）：%s"
                          % (len(self.p), _mask_params(self.p)))
        else:
            self.log.info("本次未收到任何调用参数（将完全使用本插件已保存的设置）")

        base = str(self.p.get("tgto_base_url") or "").strip()
        env_base = str(os.environ.get("TGTO_OPENAPI_BASE_URL") or "").strip()
        # 平台会按清单把默认值填齐，「值等于默认值」要当作**未填**，
        # 否则容器环境变量里的地址永远没有机会生效。
        default_base = str(FALLBACK_INPUT_DEFAULTS["tgto_base_url"])
        try:
            default_base = str(_manifest_input_defaults(context.get("plugin_dir"))
                               .get("tgto_base_url") or default_base)
        except Exception:
            pass
        if base and base == default_base and env_base:
            self.log.info("「TgtoDrive 地址」与清单默认值相同，视为未填写，"
                          "改用容器环境变量 TGTO_OPENAPI_BASE_URL")
            base = ""
        base = base or env_base or DEFAULT_BASE_URL
        token = str(self.p.get("tgto_token") or "").strip() \
            or str(os.environ.get("TGTO_OPENAPI_TOKEN") or "").strip()

        self.func = str(self.p.get("func") or FUNC_CHECK).strip().lower()
        self.action = str(self.p.get("fill_action") or ACTION_RECORD).strip().lower()
        self.source = str(self.p.get("search_source") or SOURCE_BOTH).strip().lower()
        self.dry_run = _as_bool(self.p.get("dry_run"), True)
        self.only_aired = _as_bool(self.p.get("only_aired"), True)
        self.only_season_exist = _as_bool(self.p.get("only_season_exist"), True)
        self.include_s00 = _as_bool(self.p.get("include_s00"), False)
        self.max_series = max(_as_int(self.p.get("max_series"), 50), 1)
        self.max_fill = max(_as_int(self.p.get("max_fill_per_run"), 1), 0)
        self.library_ids = _split_ids(self.p.get("library_ids"))
        self.ignore_words = [w.lower() for w in _split_ids(self.p.get("ignore_series"))]
        self.target_dir = str(self.p.get("target_dir") or "").strip()
        self.cloud_types = [c.lower() for c in _split_ids(self.p.get("pansou_cloud_types"))]
        # 「资源来源」：留空 = 由 TgtoDrive 决定（它自己的 resources/search 会用默认来源）
        self.resource_sources = _split_ids(self.p.get("resource_sources"))

        # 「应有季集」的数据源：走 TgtoDrive 的详情代理，还是本插件直连 TMDB（见 _TmdbClient）
        self.tmdb_source = str(self.p.get("tmdb_source") or TMDB_SRC_AUTO).strip().lower()
        if self.tmdb_source not in VALID_TMDB_SOURCES:
            self.tmdb_source = TMDB_SRC_AUTO
        self.tmdb_proxy_mode = str(self.p.get("tmdb_proxy_mode")
                                   or TMDB_PROXY_AUTO).strip().lower()
        if self.tmdb_proxy_mode not in VALID_TMDB_PROXY_MODES:
            self.tmdb_proxy_mode = TMDB_PROXY_AUTO

        # 运行结果通知：每次 check / fill 跑完后，把结果整理成三类推到所选渠道。
        # 默认**空**（不通知）—— 不改变已有用户的行为，要开就在「⑤ 运行通知」里勾。
        self.notify_channels = [c for c in _as_list(self.p.get("notify_channels"))
                                if c in VALID_CHANNELS]
        # 保留无法识别的取值，好在日志里点名（否则「勾了却没发」会查不出原因）
        self.notify_channels_raw = [c for c in _as_list(self.p.get("notify_channels"))
                                    if c not in VALID_CHANNELS]
        self.notify_bot = max(_as_int(self.p.get("notify_bot"), 0), 0)
        self.wecom_plugin_id = (str(self.p.get("wecom_plugin_id") or "").strip()
                                or DEFAULT_WECOM_PLUGIN_ID)
        self.wecom_touser = str(self.p.get("wecom_touser") or "").strip()

        self.ttd = _TtdClient(base, token, self.log)
        self.emby = _EmbyClient(self.p.get("emby_url"), self.p.get("emby_api_key"), self.log)
        self.pansou = _PansouClient(self.p.get("pansou_url"), self.p.get("pansou_token"),
                                    self.log)
        # 注意：代理候选要读 TgtoDrive 的网络代理（会发请求），因此**延迟到真正用到时**再解析
        # （见 _ensure_tmdb）。放这里会让 config / 未用到 TMDB 的场景也白白发一次请求。
        self.tmdb = _TmdbClient(self.p.get("tmdb_api_key"), self.p.get("tmdb_base_url"),
                                self.p.get("tmdb_language"), self.log)

        # 运行时状态
        self.missing = []          # 检测结果
        self.filled = []           # 补齐记录
        self.emby_source_note = ""
        self.libraries_skipped = []   # 按库类型排除掉的非剧集库 [(名称, 类型)]
        self.libraries_scanned = []   # 实际扫描的剧集库 id
        self.whole_series_skipped = []  # 本地一集都没有、被「只检查已有季」跳过的剧名
        # 「无法判定」的剧 [(剧名, [(季, 原因), …])] —— 某季应有集数读失败、不能算作「无缺失」
        # （否则用户会以为这部剧是完整的，实际根本没查成）
        self.undetermined = []
        # 「季集详情」是否已探活过（整库扫描时只探一次，避免重复请求；见 _require_season_ready）
        self._season_probed = False
        # TMDB 直连的代理候选是否已解析、「TgtoDrive 网络代理」缓存（None = 还没读过）
        self._tmdb_ready = False
        self._ttd_proxy_cache = None
        self.tmdb_note = ""             # 本次实际使用的 TMDB 数据源（人话）
        # TgtoDrive 自身的影视资源配置（只读；见 _load_ttd_config）
        self.ttd_settings = {}
        self.ttd_target_provider = ""
        self.ttd_transfer_targets = ""
        self.ttd_max_points = None
        self.ttd_source_options = []    # 从 /api/media/providers 读到的可用资源来源
        self.ttd_providers_raw = None
        self.re0_available = None       # None=未判定 / True / False
        self.re0_note = ""
        self.ttd_capabilities = None    # /api/media/capabilities 的原始响应
        self.capability_note = ""       # 能力概览（人话）
        self.deadline = 0.0             # 检测的软截止时间戳（见 DETECT_TIME_BUDGET）
        self.started_at = 0.0           # 本轮启动时间戳（检测 + 补齐共用一个总预算）
        self.budget_exhausted = None    # (已检测部数, 整库部数, 起始偏移) 或 None
        self.fill_budget_exhausted = None   # 补齐阶段因时间预算提前收工时记 (已处理, 待处理)
        # 盘搜结果的本轮缓存 {(关键词, 网盘类型): (粗筛后的候选, 错误)}
        # 一部剧缺多个季时关键词（剧名）是相同的 —— 不缓存就会对同一个关键词重复发 N 次请求。
        self._pansou_cache = {}
        # 补齐阶段的账：失败项与「已尝试过」的剧名。
        # 通知要区分「补了但失败」和「这次压根没轮到它」—— 两者都算未补全，
        # 但原因完全不同，混在一起用户会以为插件漏跑了。
        self.fill_errors = []
        self.fill_attempted = set()

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        self.started_at = time.time()
        if self.func not in VALID_FUNCS:
            raise ValueError("不支持的执行功能：%s（可选：%s）"
                             % (self.func, " / ".join(VALID_FUNCS)))
        if self.func == FUNC_FILL and self.action not in VALID_ACTIONS:
            raise ValueError("不支持的补齐动作：%s（可选：%s）"
                             % (self.action, " / ".join(VALID_ACTIONS)))
        if self.source not in VALID_SOURCES:
            raise ValueError("不支持的搜索源：%s（可选：%s）"
                             % (self.source, " / ".join(VALID_SOURCES)))

        self.log.info("%s 启动，执行功能：%s" % (PLUGIN_NAME, FUNC_LABELS.get(self.func)))

        # 「从头开始」要在读配置**之前**分流：它只删一个本地文件，不需要 Emby / TgtoDrive 凭据。
        # 放到后面的话，配置坏掉时就清不了进度了 —— 而那恰恰是最想重置的时候。
        if self.func == FUNC_RESET:
            return self.do_reset()

        self._ensure_emby()
        self._load_ttd_config()

        if self.func == FUNC_TEST:
            return self.do_test()
        if self.func == FUNC_CONFIG:
            return self.do_config()
        result = self.do_check()
        if self.func == FUNC_FILL:
            result = self.do_fill(result)
        # 检测 / 补齐都跑完了才发通知 —— 三类结果（缺失 / 成功 / 失败）此时才是完整的。
        # 通知失败**不会**影响本次结果（见 _notify_after_run）。
        self._notify_after_run(result)
        return result

    # -- 读取 TgtoDrive 自身的配置（搜索来源 / 转存目标 / RE0 授权） ---------

    def _load_ttd_config(self):
        """读取 TgtoDrive 自身的影视资源配置，作为本插件搜索与补齐的默认参数。

        **为什么不再让用户在本插件里重填一遍**：转存目标网盘、转存目录、点数上限、
        可用的资源来源、RE0 的授权状态 —— 这些**本来就已经在 TgtoDrive 里配好了**：

        * `GET /api/media/settings`   → 转存目标网盘 `target_provider`、转存目录
          `media_transfer_targets`、点数上限 `max_points`、Emby 配置（已在别处复用）；
        * `GET /api/media/providers`  → 可用的**资源来源**与网盘转存目标；
        * `GET /api/media/capabilities` → 当前支持的资源检索 / 转存 / 离线能力；
        * `GET /api/re0/status`       → **RE0（TgtoDrive 集成的资源检索/解锁/转存服务）
          是否可用**，取决于主账号授权状态。

        本插件只**读**这些配置，不改动 TgtoDrive 的任何设置；
        表单里对应的字段留空时用 TTD 的配置，填了则以表单为准。
        """
        if not self.ttd.configured:
            return
        # 1) 影视设置
        try:
            self.ttd_settings = self.ttd.media_settings() or {}
            # 只认明确的键名。**不要**把泛化的 "provider" 也列为候选 —— 那个名字在
            # 影视设置里可能属于榜单 / 片库等其它用途，误取会把「转存目标网盘」写成别的值。
            self.ttd_target_provider = str(_pick_config_value(
                self.ttd_settings, ("target_provider", "targetProvider")) or "").strip()
            targets = _pick_config_value(self.ttd_settings,
                                         ("media_transfer_targets", "mediaTransferTargets"))
            if isinstance(targets, (list, tuple)):
                self.ttd_transfer_targets = "、".join(str(x) for x in targets if str(x).strip())
            elif targets:
                self.ttd_transfer_targets = str(targets).strip()
            points = _pick_config_value(self.ttd_settings, ("max_points", "maxPoints"))
            self.ttd_max_points = _int_or_none(points)
            self.log.info("已读取 TgtoDrive 影视设置：转存目标网盘=%s｜转存目录=%s｜点数上限=%s"
                          % (self.ttd_target_provider or "（未配置）",
                             self.ttd_transfer_targets or "（未配置）",
                             self.ttd_max_points if self.ttd_max_points is not None else "（未配置）"))
        except Exception as exc:
            self.log.warn("读取 TgtoDrive 影视设置失败（转存参数将改用表单值）：%s" % str(exc)[:160])

        # 2) 能力清单（资源检索 / 转存 / 离线）—— **先读它**，因为 providers 认不出来源时
        #    它里面的 `resource_sources` 往往就是同一份清单（实测形态一致），可作退路
        try:
            self.ttd_capabilities = self.ttd.media_capabilities()
            summary = _summarize_capabilities(self.ttd_capabilities)
            self.capability_note = "、".join(summary) if summary else \
                "未能从响应里识别出能力字段（该接口无响应 schema）"
            if not summary:
                # 认不出来时给**结构**（键名）而不是前几百字的 JSON：实测响应按字母序排键，
                # 截断常常正好把关键字段名切掉
                self.log.info("capabilities 响应结构：%s"
                              % scrub_text(_describe_shape(self.ttd_capabilities),
                                           [self.ttd.token]))
            self.log.info("TgtoDrive 资源能力：%s" % self.capability_note)
        except Exception as exc:
            self.log.warn("读取 TgtoDrive 资源能力失败：%s" % str(exc)[:160])

        # 3) 可用来源
        try:
            self.ttd_providers_raw = self.ttd.media_providers()
            self.ttd_source_options = _extract_source_slugs(self.ttd_providers_raw)
            if not self.ttd_source_options and self.ttd_capabilities:
                self.ttd_source_options = _extract_source_slugs(self.ttd_capabilities)
                if self.ttd_source_options:
                    self.log.info("已从 /api/media/capabilities 的 resource_sources "
                                  "补齐可用资源来源清单")
            if self.ttd_source_options:
                self.log.info("TgtoDrive 当前可用的资源来源（%d 个）：%s"
                              % (len(self.ttd_source_options),
                                 "、".join("%s(%s)" % (o["label"], o["slug"])
                                           for o in self.ttd_source_options[:8])))
            else:
                self.log.warn("未能识别出「资源来源」清单（providers 与 capabilities 都没有"
                              "可用的 resource_sources）。两个响应已按**键名结构**写入日志，"
                              "可据此在「资源来源」字段里手填标识。")
                self.log.info("providers 响应结构：%s"
                              % scrub_text(_describe_shape(self.ttd_providers_raw),
                                           [self.ttd.token]))
        except Exception as exc:
            self.log.warn("读取 TgtoDrive 可用来源失败：%s" % str(exc)[:160])

        # 4) RE0 授权状态
        try:
            status = self.ttd.re0_status()
            self.re0_available, self.re0_note = _parse_re0_status(status)
            if self.re0_available is True:
                self.log.info("RE0 可用：%s" % self.re0_note)
            elif self.re0_available is False:
                self.log.warn("RE0 当前不可用：%s —— RE0 由 TgtoDrive 自己集成，"
                              "请到「影视发现 → RE0」完成主账号授权后重试" % self.re0_note)
            else:
                self.log.info("RE0 授权状态未能判定：%s" % self.re0_note)
        except Exception as exc:
            self.log.warn("读取 RE0 状态失败：%s" % str(exc)[:160])

    def _effective_provider(self):
        """离线下载时传给 TgtoDrive 的「目标网盘」：表单优先，其次 TTD 已配的 `target_provider`。

        ⚠️ **只用于离线下载接口**（`/api/media/resources/offline` 的 `provider` = 任务落到
        哪块网盘）。**转存接口的 `provider` 不是目标网盘**，而是分享链接所属网盘（源）——
        2026-10-15 实测把目标（115）传给转存接口，TTD 一律 409 SHARE_PROVIDER_MISMATCH。
        转存目标由 TTD 自己的影视设置决定，见 `_apply_action()` 里 TRANSFER_SOURCE_PROVIDERS 的注释。

        ⚠️ 另外**不要把 `media_transfer_targets`（转存目录）也当兜底值**：它是一份路径，
        而接口的 `provider` 要的是网盘标识。此前两条一起兜底，一旦用户只配了
        目录、没配目标网盘，`provider` 就会被填成目录路径，请求参数语义就错了。
        目录只在结果页与日志里展示，不参与请求。
        """
        return self.target_dir or self.ttd_target_provider

    # -- 配置 --------------------------------------------------------------

    def _ensure_emby(self):
        """Emby 连接信息：表单优先，其次尝试复用 TgtoDrive 影视设置里的 Emby 配置。"""
        if self.emby.configured:
            self.emby_source_note = "插件表单"
            return
        if not self.ttd.configured:
            return
        try:
            data = self.ttd.media_settings()
        except Exception as exc:
            self.log.warn("读取 TgtoDrive 影视设置失败（无法复用其中的 Emby 配置）：%s" % exc)
            return
        found = {}
        for node in _walk_dicts(data):
            has_url = any(k in node for k in ("server_url", "ServerUrl", "url"))
            has_key = any(k in node for k in ("api_key", "apiKey", "ApiKey"))
            if has_url and has_key:
                url = node.get("server_url") or node.get("ServerUrl") or node.get("url")
                key = node.get("api_key") or node.get("apiKey") or node.get("ApiKey")
                if isinstance(url, str) and isinstance(key, str) and url.strip() and key.strip():
                    found = {"url": url.strip(), "key": key.strip()}
                    break
        if not found:
            self.log.warn("TgtoDrive 影视设置里没有可复用的 Emby 地址 / API Key，"
                          "请在「① 连接设置」里直接填写")
            return
        self.emby = _EmbyClient(found["url"], found["key"], self.log)
        self.emby_source_note = "TgtoDrive 影视设置（media_emby）"
        self.log.info("已复用 TgtoDrive 影视设置里的 Emby 连接：%s" % self.emby.describe())

    # -- TMDB 数据源（走 TgtoDrive 代理 / 本插件直连） -----------------------

    def _ttd_proxy(self):
        """读 TgtoDrive「网络代理」设置里**实际生效**的代理地址（用于 TMDB 直连出网）。

        为什么优先用它：容器环境变量里的 HTTP_PROXY / HTTPS_PROXY 往往是**平台侧内部代理**，
        拿它出网到公网（TMDB）会被送到错误的地方（实测 502）；真正管用的通常是
        TgtoDrive 自己配的那个代理。读不到就返回空串，由调用方退回环境变量 / 直连。
        """
        if self._ttd_proxy_cache is not None:
            return self._ttd_proxy_cache
        self._ttd_proxy_cache = ""
        if not self.ttd.configured:
            return self._ttd_proxy_cache
        for path in ("/api/proxy_settings", "/api/proxy-settings"):
            try:
                payload = self.ttd.get_json(path)
            except Exception as exc:
                self.log.warn("读取 %s 失败：%s" % (path, exc))
                continue
            if not isinstance(payload, dict):
                continue
            node = payload
            data = payload.get("data")
            if isinstance(data, dict):
                node = data
            for key in ("effective_proxy", "web_proxy", "proxy", "proxy_url"):
                value = node.get(key)
                if isinstance(value, str) and value.strip():
                    self._ttd_proxy_cache = value.strip()
                    return self._ttd_proxy_cache
            for key in ("runtime", "proxies"):
                block = node.get(key)
                if isinstance(block, dict):
                    for sub in ("https", "http"):
                        value = block.get(sub)
                        if isinstance(value, str) and value.strip():
                            self._ttd_proxy_cache = value.strip()
                            return self._ttd_proxy_cache
        return self._ttd_proxy_cache

    def _tmdb_proxy_candidates(self):
        """按「TMDB 代理策略」算出代理候选 ``[(代理, 说明), …]``（去重，最后一项固定是直连）。

        只在「代理 / 网关层错误」时才轮到下一个候选 —— 换个代理重发对 TMDB 是无副作用的
        GET，不会造成重复写入。
        """
        candidates = []

        def push(proxy, label):
            if proxy is None:
                return
            if all(proxy != item[0] for item in candidates):
                candidates.append((proxy, label))

        explicit = str(self.p.get("tmdb_proxy") or "").strip()
        if explicit:
            push(explicit, "「TMDB 代理地址」里填的代理")
        if self.tmdb_proxy_mode == TMDB_PROXY_AUTO:
            ttd_proxy = self._ttd_proxy()
            if ttd_proxy:
                push(ttd_proxy, "TgtoDrive 网络代理设置")
            env_proxy = _first_env_proxy()
            if env_proxy:
                push(env_proxy, "容器环境变量代理")
        elif self.tmdb_proxy_mode == TMDB_PROXY_ENV:
            env_proxy = _first_env_proxy()
            if env_proxy:
                push(env_proxy, "容器环境变量代理")
        push("", "直连")
        return candidates

    def _ensure_tmdb(self):
        """首次用到 TMDB 前解析一次代理候选（要读 TgtoDrive 代理，会发请求，故延迟到用时）。"""
        if self._tmdb_ready:
            return
        self._tmdb_ready = True
        self.tmdb.proxy_candidates = self._tmdb_proxy_candidates()
        self.tmdb_note = self._tmdb_source_note()
        self.log.info("TMDB 数据源：%s" % self.tmdb_note)

    def _use_direct_tmdb(self):
        """本次是否走「本插件直连 TMDB」。"""
        if self.tmdb_source == TMDB_SRC_DIRECT:
            return True
        if self.tmdb_source == TMDB_SRC_TTD:
            return False
        return self.tmdb.configured          # auto：填了 Key 就直连

    def _tmdb_source_note(self):
        """本次实际使用的 TMDB 数据源（人话，写进日志与结果页）。"""
        if self._use_direct_tmdb():
            note = "直连 TMDB（%s，语言 %s）" % (self.tmdb.base_url, self.tmdb.language)
            if self.tmdb.last_proxy_note:
                note += "，经「%s」" % self.tmdb.last_proxy_note
            return note
        if self.tmdb_source == TMDB_SRC_TTD:
            return "TgtoDrive 详情代理（按设置强制使用）"
        return ("TgtoDrive 详情代理（未填 TMDB API Key，自动回退到它）"
                "—— 若报 409 TMDB_READONLY_MODE_INACTIVE，请到「③ TMDB 设置」填入 API Key 改用直连")

    def _tmdb_detail(self, tmdb_id):
        """取 TMDB 剧集详情；失败抛 RuntimeError。"""
        if self._use_direct_tmdb():
            self._ensure_tmdb()
            return self.tmdb.tv_detail(tmdb_id)
        return self.ttd.get_json("/api/media/details/tmdb/tv/%s" % _url_seg(tmdb_id))

    def _tmdb_season_soft(self, tmdb_id, season):
        """取某一季的集数据，**不抛异常**，返回 ``(status, data, error)``。"""
        if self._use_direct_tmdb():
            self._ensure_tmdb()
            return self.tmdb.tv_season_soft(tmdb_id, season)
        return self.ttd.get_soft("/api/media/details/tmdb/tv/%s/season/%s"
                                 % (_url_seg(tmdb_id), _url_seg(season)))

    # -- 测试连接 ----------------------------------------------------------

    def do_test(self):
        rows = []

        # 1) TgtoDrive
        if not self.ttd.configured:
            rows.append(["TgtoDrive", "✘", "未配置地址或 OpenAPI 令牌"])
        else:
            try:
                data = self.ttd.media_settings()
                # 键数要报**真实总数**：此前先切片成前 8 个再取 len，于是 12 个键会显示成 8 个
                all_keys = sorted(data.keys()) if isinstance(data, dict) else []
                shown = all_keys[:8]
                rows.append(["TgtoDrive", "✔",
                             "已连通；/api/media/settings 返回 %d 个顶层键%s"
                             % (len(all_keys),
                                ("：" + "、".join(shown) + ("…" if len(all_keys) > 8 else ""))
                                if shown else "")])
            except Exception as exc:
                rows.append(["TgtoDrive", "✘", str(exc)[:160]])

        # 2) Emby
        if not self.emby.configured:
            rows.append(["Emby", "✘", "未配置地址或 API Key（留空时会尝试复用 TgtoDrive 影视设置）"])
        else:
            try:
                _info, name, version = self.emby.test()
                libs = self.emby.libraries()
                types = sorted({l["type"] for l in libs if l["type"]})
                rows.append(["Emby", "✔", "服务器 %s%s；媒体库 %d 个%s"
                             % (name or "（未命名）", (" v" + version) if version else "",
                                len(libs), ("（类型：" + "、".join(types) + "）") if types else "")])
                # 媒体库筛选：本插件只处理剧集，这里把「将扫描哪些库、排除了哪些」讲清楚
                scanned = None
                try:
                    scanned = self._resolve_libraries()
                    detail = "将扫描 %d 个剧集库；本插件**只处理剧集**，电影 / 音乐等类别不参与" % len(scanned)
                    if self.libraries_skipped:
                        detail += "。已排除：" + "、".join(
                            "%s（%s）" % (n, t or "无类型") for n, t in self.libraries_skipped[:6])
                    rows.append(["媒体库筛选", "✔" if scanned else "⚠", detail])
                except Exception as exc:
                    rows.append(["媒体库筛选", "✘", str(exc)[:170]])
                try:
                    # 用**过滤后**的剧集库取样，否则这里会去查电影/音乐库，和实际检测路径不一致
                    probe_libs = scanned if scanned is not None else self.library_ids
                    series = self.emby.series(probe_libs, limit=3)
                    rows.append(["Emby 剧集读取", "✔" if series else "⚠",
                                 ("示例：" + "、".join(s["name"] for s in series))
                                 if series else "未读到剧集条目（检查媒体库是否含剧集）"])
                except Exception as exc:
                    rows.append(["Emby 剧集读取", "✘", str(exc)[:160]])
            except Exception as exc:
                rows.append(["Emby", "✘", str(exc)[:160]])

        # 3) TMDB —— 「应有季集」的数据源：走 TgtoDrive 详情代理，或本插件直连 TMDB
        if self.ttd.configured or self.tmdb.configured:
            self._ensure_tmdb()          # 解析代理候选（会读一次 TgtoDrive 的网络代理）
            rows.append(["TMDB 数据源", "✔", self._tmdb_source_note()])
            try:
                probe = self._tmdb_probe()
                rows.append(["TMDB 剧集详情", "✔" if probe else "⚠",
                             probe or "接口可用，但没有返回可解析的季列表（可能该剧 ID 无数据）"])
            except Exception as exc:
                rows.append(["TMDB 剧集详情", "✘", str(exc)[:200]])
            # 3b) 季集详情 —— 这一项不通，整个插件的核心功能都做不了，必须显式暴露
            try:
                season_ok, season_msg = self._season_probe()
                rows.append(["TMDB 季集详情（关键）", "✔" if season_ok else "✘", season_msg])
            except Exception as exc:
                rows.append(["TMDB 季集详情（关键）", "✘", str(exc)[:200]])

        # 4) TgtoDrive 自身的影视资源配置（本插件会直接复用，不让你再填一遍）
        if self.ttd.configured:
            if self.re0_available is True:
                rows.append(["RE0（TgtoDrive 集成）", "✔",
                             "%s —— 资源检索 / 解锁 / 转存由 TgtoDrive 自己维护授权，"
                             "本插件只读它的状态" % self.re0_note])
            elif self.re0_available is False:
                rows.append(["RE0（TgtoDrive 集成）", "✘",
                             "%s —— 请到 TgtoDrive 的「影视发现 → RE0」完成主账号授权；"
                             "未授权时走 RE0 的检索 / 转存会不可用" % self.re0_note])
            else:
                rows.append(["RE0（TgtoDrive 集成）", "⚠", self.re0_note])
            if self.ttd_source_options:
                rows.append(["可用资源来源（TgtoDrive）", "✔",
                             "共 %d 个：%s（把想要的标识填进「补齐设置 → 资源来源」）"
                             % (len(self.ttd_source_options),
                                "、".join("%s=%s" % (o["label"], o["slug"])
                                          for o in self.ttd_source_options[:8]))])
            else:
                rows.append(["可用资源来源（TgtoDrive）", "⚠",
                             "未能从 /api/media/providers 识别出来源清单（该接口无响应 schema）。"
                             "原始响应已写入运行日志，可据此手填「资源来源」"])
            rows.append(["转存目标（TgtoDrive）", "✔" if self.ttd_target_provider else "⚠",
                         "网盘=%s｜目录=%s｜点数上限=%s（表单「目标目录」留空时自动用它）"
                         % (self.ttd_target_provider or "（未配置）",
                            self.ttd_transfer_targets or "（未配置）",
                            self.ttd_max_points if self.ttd_max_points is not None else "（未配置）")])
            rows.append(["资源能力（TgtoDrive）", "✔" if self.capability_note else "⚠",
                         self.capability_note or "未读取（/api/media/capabilities 无响应 schema）"])

        # 5) 搜索源
        if self.source in (SOURCE_PANSOU, SOURCE_BOTH):
            status, text, _data = self.pansou.health()
            if status is None:
                rows.append(["盘搜（PanSou）", "✘",
                             "无法访问 %s/api/health：%s"
                             % (self.pansou.base_url, scrub_text(text, [self.pansou.token])[:140])])
            elif 200 <= status < 300:
                rows.append(["盘搜（PanSou）", "✔", "%s/api/health 返回 HTTP %s" % (self.pansou.base_url, status)])
            else:
                rows.append(["盘搜（PanSou）", "✘", "HTTP %s：%s" % (status, (text or "")[:140])])
            try:
                cand, _raw, err = self.pansou.search("测试", cloud_types=self.cloud_types)
                if err:
                    rows.append(["盘搜搜索", "✘", err[:160]])
                else:
                    rows.append(["盘搜搜索", "✔", "「测试」返回 %d 条候选链接" % len(cand)])
            except Exception as exc:
                rows.append(["盘搜搜索", "✘", str(exc)[:160]])

        if self.source in (SOURCE_BUILTIN, SOURCE_BOTH) and self.ttd.configured:
            try:
                status, text, data = self.ttd.post_json("/api/media/resources/search", {
                    "title": "测试", "media_type": "tv",
                })
                ok = status is not None and 200 <= status < 300
                # 非 2xx 是**错误**（✘），不该报成「接口可用但数据为空」（⚠）
                rows.append(["TgtoDrive 内置资源检索", "✔" if ok else "✘",
                             "HTTP %s%s" % (status, "" if ok
                                            else "：" + scrub_text((text or "")[:140], [self.ttd.token]))])
            except Exception as exc:
                rows.append(["TgtoDrive 内置资源检索", "✘", str(exc)[:160]])

        # 6) 运行通知 —— 「测试连接」是用户验证链路的入口，必须一并验证通知渠道：
        #    否则用户勾了渠道却不知道能不能发出去，只能等下一次正式运行才暴露问题。
        if self.notify_channels:
            self.log.info("测试通知渠道：%s"
                          % "、".join(CHANNEL_LABELS.get(c, c) for c in self.notify_channels))
            try:
                results = self._send_notifications(self._test_notify_text())
            except Exception as exc:
                results = [(CHANNEL_LABELS.get(c, c), False, "发送时异常：%s" % exc)
                           for c in self.notify_channels]
            for label, ok, note in results:
                rows.append(["运行通知 · %s" % label, "✔" if ok else "✘", note])
        elif self.notify_channels_raw:
            rows.append(["运行通知", "⚠", "「通知渠道」里有无法识别的取值：%s（可选：Telegram / 微信）"
                         % "、".join(self.notify_channels_raw)])
        else:
            # 没勾渠道**不加行**：这不是配置错误，加个 ⚠ 会把整页结论拉成「有问题」
            # （结果页按「✔ 数 == 总行数」判成功/告警）。只在日志里说一句。
            self.log.info("未勾选「通知渠道」，本次不发送运行结果通知"
                          "（要开启就在「⑤ 运行通知」里勾选并保存）")

        ok_count = sum(1 for r in rows if r[1] == "✔")
        components = [
            {"type": "heading", "text": "🧪 %s · 连接测试" % PLUGIN_NAME},
            {"type": "alert",
             "text": "共 %d 项检查，%d 项通过。带 ✘ 的项请按「说明」列处理；"
                     "「⚠」表示接口可用但数据为空，通常不是配置问题。"
                     % (len(rows), ok_count),
             "style": {"tone": "success" if ok_count == len(rows) else "warning"}},
            {"type": "table", "label": "测试结果", "headers": ["检查项", "结果", "说明"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok",
            "func": self.func,
            "checks": [{"name": r[0], "result": r[1], "detail": r[2]} for r in rows],
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    def _tmdb_probe(self):
        """用一个已知剧集 ID 探活 TMDB 代理，返回可读结论或空串。

        两次探活都失败时，把**最后一次的错误**带回去 —— 此前直接 `except Exception: continue`，
        真实原因（如 HTTP 404 / 403）被吞掉，结果页只显示「没有返回可解析的季列表」，
        排查时看不出是接口不通还是数据为空。
        """
        last_error = ""
        for probe_id in ("1399", "1396"):   # 权力的游戏 / 绝命毒师
            try:
                data = self._tmdb_detail(probe_id)
            except Exception as exc:
                last_error = str(exc)[:140]
                continue
            seasons = _extract_tmdb_seasons(data)
            if seasons:
                return ("可用（%s）；探活剧集返回 %d 个季（%s）"
                        % ("直连 TMDB" if self._use_direct_tmdb() else "经 TgtoDrive 代理",
                           len(seasons),
                           "、".join("S%02d" % s for s in sorted(seasons)[:6])))
            # 能连上但解析不出季 → 说明是**接口返回形态**变了，把结构（键名）带回去
            last_error = "详情接口返回 2xx，但没解析出季列表。响应结构：%s" % \
                         scrub_text(_describe_shape(data), [self.ttd.token, self.tmdb.api_key])
        if last_error:
            raise RuntimeError("TMDB 详情探活失败（两次都未成功）：%s" % last_error)
        return ""

    def _season_probe(self):
        """探活「季集详情」接口，返回 ``(是否可用, 说明)``。

        **为什么必须单独探活**：规范原文写得很清楚 ——
        `/api/media/details/tmdb/tv/{id}/season/{n}`「**只有当前详情配置支持完整季集模式时可用**」。
        这个接口一旦不可用，缺集检测就**无从谈起**（拿不到「应该有哪些集」）。
        不提前探活的话，用户会看到整库每一部剧都报错，却不知道根因在这里。
        """
        last = ""
        for probe_id in ("1399", "1396"):     # 权力的游戏 / 绝命毒师
            status, data, err = self._tmdb_season_soft(probe_id, 1)
            if status is None:
                last = "网络失败：%s" % (err or "未知")
                continue
            if status == 404:
                last = ("HTTP 404 —— 可能是该剧没有第 1 季，也可能是**该接口在当前详情"
                        "配置下不可用**")
                continue
            if not 200 <= status < 300:
                last = "HTTP %s：%s" % (status, err or "")
                continue
            numbers, _air = _extract_tmdb_episodes(data if isinstance(data, dict) else {})
            if numbers:
                return True, ("季集详情可用（%s）；探活剧集 S01 返回 %d 集"
                              % ("直连 TMDB" if self._use_direct_tmdb()
                                 else "经 TgtoDrive 代理", len(numbers)))
            last = ("接口返回 HTTP %s 但没解析出任何集数据。响应结构：%s"
                    % (status, scrub_text(_describe_shape(data),
                                          [self.ttd.token, self.tmdb.api_key])))
        if self._use_direct_tmdb():
            return False, ("TMDB 直连拿不到季集数据（%s）—— 请检查「③ TMDB 设置」里的"
                           "API Key 是否正确、以及容器能否出网（必要时在「TMDB 代理策略 / "
                           "代理地址」里指定代理）。在它恢复之前，本插件确定不了"
                           "「应该有哪些集」。" % last)
        return False, ("季集详情接口不可用（%s）。⚠️ 规范说明该接口**只有当前详情配置支持"
                       "完整季集模式时可用** —— 在它恢复之前，本插件无法确定"
                       "「应该有哪些集」，也就无法检测缺集（会把每一部剧都判为"
                       "「无法判定」而不是「无缺失」）。" % last)

    def _require_season_ready(self):
        """检测前**先探活一次「季集详情」**；确认不可用时立刻失败，不让整库白扫。

        为什么必须拦在这里
        ------------------
        `do_test()` 一直在探活，但 `do_check()` 以前**从不探活** —— 于是当数据源不可用时：
          * 每一部剧的**每一季**都会发一次请求、全部失败；
          * 日志被刷成几十上百条告警（用户实测就是这样）；
          * 最后拿到一份全是「无法判定」的结果，白跑一整轮（还白白消耗了时间预算）。

        因此这里做**一次性**探活（本轮只探一次，结果缓存在 `_season_probed`），按数据源分流：

        * 走 TgtoDrive 代理且命中 ``TMDB_READONLY_ERROR_CODE`` → **全局性**前置条件不满足，
          直接抛错并给出可操作指引（改用直连，或把详情切到完整季集模式）；
        * 直连 TMDB 且探活失败 → 抛错并提示检查 API Key / 出网 / 代理；
        * 其它原因探活失败（例如两部探活剧集恰好没有第 1 季）→ **不阻断**，只告警后继续。
        """
        if self._season_probed:
            return
        self._season_probed = True
        ok, message = self._season_probe()
        if ok:
            self.log.info("季集详情探活：%s" % message)
            return
        if self._use_direct_tmdb():
            raise ValueError(
                "TMDB 直连拿不到季集数据，缺集检测无法进行：\n"
                "  · 数据源：%s\n"
                "  · 探活结果：%s\n"
                "  · 请检查「③ TMDB 设置」里的 **TMDB API Key** 是否正确；\n"
                "  · 若 Key 没问题，多半是容器出不了网：在「TMDB 代理策略」里改成"
                "「只用容器环境变量代理」，或在「TMDB 代理地址」里手填一个可用代理。"
                % (self._tmdb_source_note(), message))
        if TMDB_READONLY_ERROR_CODE in message:
            raise ValueError(
                "TgtoDrive 当前**未启用完整 TMDB 季集模式**，缺集检测无法进行：\n"
                "  · 季集接口 /api/media/details/tmdb/tv/{id}/season/{n} 返回 HTTP 409 "
                "%s；\n"
                "  · 也就是说，本插件拿不到「每一季应该有哪些集」，检测与补齐都做不了；\n"
                "  · **推荐**：到本插件的「③ TMDB 设置」里填上 TMDB API Key，"
                "数据源选「直连 TMDB」后重跑 —— 直连不受该模式约束，最省事；\n"
                "  · 或者：到 TgtoDrive 的影视发现 / 详情页设置里把详情切换为"
                "「完整 TMDB 季集模式」再重跑。"
                % TMDB_READONLY_ERROR_CODE)
        self.log.warn("季集详情探活未通过（%s）—— 仍继续检测，逐部剧的失败会单独列出。"
                      % message)

    # -- 仅检测缺失（只读） -------------------------------------------------

    def _library_note(self):
        """媒体库过滤说明（有排除项时返回文本，否则返回空串）。"""
        if not self.libraries_skipped:
            return ""
        return ("本插件**只处理剧集**，已按媒体库类型排除 %d 个非剧集库：%s —— "
                "电影、音乐等类别不参与检测与补齐。"
                % (len(self.libraries_skipped),
                   "、".join("%s（%s）" % (n, t or "无类型")
                             for n, t in self.libraries_skipped[:8])))

    # -- 扫描窗口与游标 ----------------------------------------------------

    def _cursor_path(self):
        return self.data_dir / CURSOR_FILE

    def _read_cursor_raw(self):
        """读取游标里记录的**原始偏移**（不取模），用于展示「下次从第几部开始」。"""
        try:
            data = json.loads(self._cursor_path().read_text(encoding="utf-8"))
            return int(data.get("offset") or 0)
        except (OSError, ValueError, TypeError):
            return 0

    def _load_cursor(self, total):
        """读取上次扫描到的位置（只用于「整库比单次窗口大」的情况）。"""
        offset = self._read_cursor_raw()
        if total <= 0:
            return 0
        return offset % total

    def _save_cursor(self, offset):
        """保存扫描进度，返回 ``True`` / ``False``（是否真的写进去了）。

        失败只记警告（游标丢了顶多是下次从头扫，不影响正确性）—— 但**返回值必须可信**：
        调用方（如 `do_reset` 的兜底分支）要靠它判断「到底清没清掉」。
        """
        try:
            self._cursor_path().write_text(
                json.dumps({"offset": int(offset),
                            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                           ensure_ascii=False),
                encoding="utf-8")
            return True
        except OSError as exc:
            self.log.warn("保存扫描进度失败（不影响本次结果）：%s" % str(exc)[:120])
            return False

    def do_reset(self):
        """清空扫描进度：只动 `scan_cursor.json`，**不运行检测 / 不补齐、也不发通知**。

        幂等：没有进度文件时也返回成功（只说明「本来就没有记录」），
        免得用户重复点两次看到「失败」。
        删除失败（例如数据目录只读）时退一步把偏移写回 0 —— 效果等价（下次仍从第 1 部开始）。
        """
        path = self._cursor_path()
        existed = path.is_file()
        # 路径被**非文件对象**占用（例如被误建成目录）时：既读不到也删不掉，
        # 必须单独报出来 —— 当成「没有进度」会让用户以为清过了，其实那东西还杵在那儿。
        occupied = path.exists() and not existed
        before = self._read_cursor_raw()

        cleared, error, method = False, "", ""
        if occupied:
            error = "路径存在但不是文件（可能是被误建成目录）"
            self.log.warn("清空扫描进度失败：%s %s" % (CURSOR_FILE, error))
        else:
            try:
                if existed:
                    path.unlink()
                    method = "deleted"
                cleared = True
            except OSError as exc:
                error = str(exc)[:120]
                # 兜底：把偏移写回 0（效果等价）。**必须确认真的写进去了** ——
                # 只看「没抛异常」就报「已清空」会让用户以为进度没了，其实还原封不动。
                if self._save_cursor(0):
                    method = "zeroed"
                    cleared = True
                    self.log.warn("删除进度文件失败（%s），已改为把偏移写回 0" % error)
                else:
                    error = "%s；把偏移写回 0 也失败（见上一条日志）" % error

        if not cleared:
            self.log.warn("清空扫描进度失败：%s" % error)
        elif method == "deleted":
            self.log.info("已清空扫描进度（原记录：下次本应从第 %d 部开始）—— "
                          "下次运行会从第 1 部重新扫" % (before + 1))
        elif method == "zeroed":
            self.log.info("已清空扫描进度（文件删不掉，改为把偏移写回 0）—— "
                          "下次运行会从第 1 部重新扫")
        else:
            self.log.info("扫描进度本来就没有记录（%s 不存在），无需清理" % CURSOR_FILE)

        if occupied:
            alert = ("**清空进度失败**：`%s` 存在但**不是文件**（可能是被误建成目录）—— "
                     "插件既读不到它也删不掉它。请到插件数据目录手动清理后重试。" % CURSOR_FILE)
            tone = "danger"
        elif method == "deleted":
            alert = ("**已清空扫描进度**：`%s` 里的记录已删除，**下一次运行会从第 1 部重新开始**。\n\n"
                     "本次**没有运行检测、没有补齐、也没有发送通知** —— 只清理了一个本地文件。"
                     % CURSOR_FILE)
            tone = "success"
        elif method == "zeroed":
            # 如实说清：文件没删掉，只是把偏移归零（效果等价，但状态文件还在）
            alert = ("**已清空扫描进度**：`%s` 没能直接删除（%s），已改为把偏移**写回 0** —— "
                     "效果相同，**下一次运行会从第 1 部重新开始**。\n\n"
                     "本次**没有运行检测、没有补齐、也没有发送通知**。"
                     "若想彻底删掉文件，请检查插件数据目录的写权限。"
                     % (CURSOR_FILE, error))
            tone = "warning"
        elif cleared:
            alert = ("**没有需要清理的进度**：`%s` 本来就不存在（上一次是全量扫描，或还没跑过）。"
                     "本次同样**没有运行检测与补齐**。" % CURSOR_FILE)
            tone = "default"
        else:
            alert = ("**清空进度失败**：%s —— 插件数据目录可能不可写。"
                     "请检查容器里该目录的权限后重试。" % error)
            tone = "danger"

        rows = [
            ["执行功能", FUNC_LABELS.get(self.func, self.func)],
            ["进度文件", "%s（位于插件数据目录）" % CURSOR_FILE],
            ["清理前记录", "路径被占用，读不到内容" if occupied
             else (("下次本应从第 %d 部开始" % (before + 1)) if existed else "（无记录）")],
            ["本次是否检测 / 补齐", "否 —— 只清空进度"],
            ["本次是否发送通知", "否 —— 「从头开始」不发运行通知"],
            ["下次运行", "从第 1 部重新开始" if cleared else "仍按原进度继续（未清空）"],
        ]
        notes = []
        if cleared:
            notes.append("说明：进度只决定「单次检测上限」不够覆盖整库时的**轮转起点**；"
                         "清空它不会改变检测口径，也不会动媒体库或网盘 —— "
                         "下次运行从剧名排序的第 1 部开始重新算一遍。")
        if cleared and not existed:
            notes.append("另外：整库不超过「单次检测上限」时本来每次都全量扫描，"
                         "进度文件只在媒体库更大时才有意义。")
        return self._result(
            ok=cleared, title="清空扫描进度", tone=tone, alert=alert,
            stats=[("清理前位置", "被占用" if occupied
                    else (("第 %d 部" % (before + 1)) if existed else "无记录")),
                   ("清理结果", "已清空" if (cleared and existed)
                    else ("本来就为空" if cleared else "失败")),
                   ("检测 / 补齐", "未运行")],
            rows=rows, headers=["项目", "值"], notes=notes,
            rows_label="本次做了什么")

    def _scan_window(self, series):
        """决定本次扫描哪一段剧集，返回 ``(窗口列表, 起始偏移, 总数)``。

        媒体库比「单次检测上限」大时，**从上次的位置往后轮转**，让多次运行能覆盖全库；
        库本身不超过上限时永远全扫（偏移恒为 0，行为与不轮转完全一致）。

        为什么需要它：只做「取前 N 部」的话，超出部分永远轮不到 —— 而单次上限又必须存在，
        因为每部剧要发 1 次 Emby + 1 次 TMDB 详情 + 每季 1 次 TMDB 季详情的请求，
        全库一次跑完很可能撞上插件超时（1800 秒），那一轮就整个白跑了。
        """
        total = len(series)
        if total <= self.max_series:
            self._save_cursor(0)
            return list(series), 0, total
        offset = self._load_cursor(total)
        ordered = series[offset:] + series[:offset] if offset else list(series)
        return ordered[:self.max_series], offset, total

    def _missing_rows(self):
        """缺失明细表的行；`do_check` 与 `do_fill` 共用，保证两张表口径一致。"""
        rows = []
        for item in self.missing:
            series_name = item["series"]["name"]
            status = item.get("status") or ""
            # 有读失败的季时，在同一行里点名 —— 否则用户会以为这部剧只缺这些
            undet = ""
            if item.get("undetermined"):
                undet = "另有 %s 无法判定（%s）" % (
                    "、".join(s for s, _ in item["undetermined"]),
                    item["undetermined"][0][1])
            for season, detail in sorted(item["seasons"].items()):
                lacks = detail["episodes"]
                why = detail.get("why") or ""
                if not why and status:
                    why = "该剧状态：%s" % status
                if undet:
                    why = (why + "；" + undet) if why else undet
                rows.append([
                    series_name,
                    "S%02d" % season,
                    ("整季缺失" if detail.get("whole_season") else _join_nums(lacks)),
                    "%d 集" % (len(lacks) or detail.get("total", 0)),
                    why,
                ])
        return rows

    def do_check(self):
        self._require_readiness(need_search=False)
        # 先确认「季集详情」可用 —— 不可用时整轮检测毫无意义，
        # 早失败好过 50 部剧 × 每季一条失败告警（见 _require_season_ready）。
        self._require_season_ready()
        series = self._load_series()
        library_note = self._library_note()
        if not series:
            return self._result(
                ok=True, title="未检测到剧集", tone="warning",
                alert="Emby 里没有读到剧集条目，或所选媒体库里不含剧集。"
                      "可在「② 检测范围」里清空「媒体库 id」以自动扫描全部剧集库。",
                stats=[("检测范围", "全部剧集库" if not self.library_ids
                        else "%d 个媒体库" % len(self.library_ids))],
                rows=[], headers=["项目", "值"],
                notes=[library_note] if library_note else [])

        window, offset, total = self._scan_window(series)
        self.log.info("开始检测 %d 部剧集（单次上限 %d；整库共 %d 部%s）"
                      % (len(window), self.max_series, total,
                         ("，本次从第 %d 部开始轮转" % (offset + 1)) if offset else ""))
        # 软截止：每部剧要发 1 次 Emby + 1 次 TMDB 详情 + 每季 1 次 TMDB 季详情的请求，
        # 大库很容易撞上插件超时（1800 秒）—— 那样整轮结果都会丢掉。
        # 这里预留 300 秒余量，到点就带着已完成的结果收工，并保存进度供下次续扫。
        # 按「本轮启动时间」起算（含配置读取耗时），而不是从现在起算，避免低估已用时间。
        self.deadline = (self.started_at or time.time()) + DETECT_TIME_BUDGET
        missing, skipped, errors = [], [], []
        processed = 0
        for index, item in enumerate(window, 1):
            if time.time() > self.deadline:
                self.budget_exhausted = (processed, total, offset)
                self.log.warn("时间预算（%d 秒）用尽：本次只检测了 %d 部；"
                              "进度已保存，下次运行会从第 %d 部继续"
                              % (DETECT_TIME_BUDGET, processed,
                                 (offset + processed) % total + 1 if total else 1))
                break
            if any(w in item["name"].lower() for w in self.ignore_words):
                skipped.append("%s（命中忽略关键词）" % item["name"])
                processed += 1
                continue
            undet_before = len(self.undetermined)
            try:
                found = self._detect_one(item)
            except Exception as exc:
                errors.append("%s：%s" % (item["name"], str(exc)[:120]))
                self.log.warn("检测「%s」失败：%s" % (item["name"], exc))
                processed += 1
                continue
            if found:
                missing.append(found)
                self.log.info("[%d/%d] %s%s → 缺失 %d 季：%s"
                              % (index, len(window), item["name"],
                                 ("（%s）" % found["status"]) if found.get("status") else "",
                                 len(found["seasons"]), "、".join(
                                     "S%02d 缺 %s" % (s, "整季"
                                                      if d.get("whole_season")
                                                      else (_join_nums(d["episodes"]) or "整季"))
                                     for s, d in sorted(found["seasons"].items()))))
            elif item["name"] in self.whole_series_skipped:
                # 已在 _detect_one 里记过原因，这里不再重复打印「无缺失」，避免自相矛盾
                self.log.info("[%d/%d] %s → 跳过（本地一集都没有，见上一行说明）"
                              % (index, len(window), item["name"]))
            elif len(self.undetermined) > undet_before:
                # 「无法判定」≠「无缺失」：某季的应有集数没读成，不能给用户一个虚假的
                # 「这部剧是完整的」结论（具体原因已在上一行的 WARN 里给出）。
                self.log.info("[%d/%d] %s → 无法判定（见上一行原因，不计入「无缺失」）"
                              % (index, len(window), item["name"]))
            else:
                self.log.info("[%d/%d] %s → 无缺失" % (index, len(window), item["name"]))
            processed += 1
        self.missing = missing
        # 推进游标：整库大于单次窗口时按已处理部数轮转，下次接着往后扫
        if total > self.max_series and total:
            self._save_cursor((offset + processed) % total)

        rows = self._missing_rows()
        total_lacks = sum(len(d["episodes"]) for it in missing for d in it["seasons"].values())

        stats = [
            ("检测剧集", "%d 部" % processed),
            ("有缺失的剧", "%d 部" % len(missing)),
            ("缺失集数合计", "%d 集" % total_lacks),
        ]
        if total > self.max_series:
            stats.append(("整库 / 本次窗口", "%d 部 / 第 %d 部起" % (total, offset + 1)))
        if self.whole_series_skipped:
            # 有才显示：为 0 时留一张「跳过 0 部」的卡片只是噪声
            stats.append(("整剧未入库跳过", "%d 部" % len(self.whole_series_skipped)))
        if self.undetermined:
            stats.append(("无法判定的剧", "%d 部" % len(self.undetermined)))
        alert = ("**仅检测模式**：本次只读，没有修改任何数据。"
                 if not missing else
                 "**仅检测模式**：发现 %d 部剧存在缺集，合计 %d 集。"
                 "如需补齐，把「执行功能」切到「检测并补齐」再运行。" % (len(missing), total_lacks))
        if self.undetermined:
            alert += ("\n\n⚠️ 另有 **%d 部剧无法判定**（某些季的应有集数没读成）——"
                      "本次结果**不完整**，详见下方警告。" % len(self.undetermined))
        note_list = []
        if self.budget_exhausted:
            done, all_total, start = self.budget_exhausted
            note_list.append(
                "⏱ **时间预算（%d 秒）用尽**：本次只检测了 %d 部（整库 %d 部）。"
                "进度已保存，下次运行会从第 %d 部继续轮转 —— 多跑几次即可覆盖全库。"
                "想一次扫完可以调小「单次检测上限」之外的其它设置，或按媒体库分批。"
                % (DETECT_TIME_BUDGET, done, all_total, (start + done) % all_total + 1
                   if all_total else 1))
        elif total > self.max_series:
            note_list.append("ℹ 整库 %d 部大于「单次检测上限」%d 部，本次只扫了从第 %d 部起的 %d 部；"
                             "下次运行会接着往后轮转，避免每次都只看开头那几部。"
                             % (total, self.max_series, offset + 1, len(window)))
        if library_note:
            note_list.append(library_note)
        if self.whole_series_skipped:
            note_list.append("有 %d 部剧在本地**一集都没有**，已按「只检查本地已有季的缺失」跳过：%s —— "
                             "如果你想连整季 / 整剧一起补齐，请在「② 检测范围」里关掉这个开关。"
                             % (len(self.whole_series_skipped),
                                "、".join(self.whole_series_skipped[:8])))
        if skipped:
            note_list.append("以下剧集已按忽略关键词跳过：" + "、".join(skipped[:8]))
        if self.undetermined:
            # 这类**必须显式警告**：它们既不是「有缺失」也不是「完整」，而是「没查成」。
            # 混在「无缺失」里就是假阴性 —— 用户会以为剧集是完整的。
            note_list.append(
                "⚠️ **有 %d 部剧无法判定**（某一季的「应有集数」读取失败，既没算作缺失、"
                "也没算作完整）：%s —— 这类结果**不代表这些剧没有缺失**，"
                "请对照运行日志里的具体原因（常见：TMDB 季详情接口不可用、"
                "或该剧的详情数据不含季集）。"
                % (len(self.undetermined),
                   "、".join("%s（%s）" % (n, (u[0][1] if u else ""))
                             for n, u in self.undetermined[:6])))
        if errors:
            note_list.append("以下剧集检测失败（详见日志）：" + "；".join(errors[:5]))
        return self._result(
            ok=True, title="缺失检测完成", tone="success" if not missing else "warning",
            alert=alert, stats=stats, rows=rows, notes=note_list,
            rows_label="缺失明细（共 %d 行）" % len(rows),
            headers=["剧集", "季", "缺失集", "集数", "说明"])

    def _detect_one(self, item):
        """对一部剧求差集，返回 ``{"series":…, "seasons": {季: {"episodes":[…], …}}}`` 或 None。"""
        if not item.get("tmdb"):
            raise RuntimeError("Emby 条目里没有 TMDB id（ProviderIds.Tmdb 为空），无法确定应有集数")

        local = self.emby.episodes(item["id"])
        if not local and self.only_season_exist:
            # 本地一集都没有的剧：默认设置下跳过（与参考插件的 only_season_exist 语义一致）。
            # 但必须让这件事**可见** —— 否则用户会以为「这些剧被漏掉了」，
            # 而实际上只要关掉「只检查本地已有季的缺失」它们就会被列为整季缺失。
            self.whole_series_skipped.append(item["name"])
            self.log.info("「%s」本地一集都没有 → 按「只检查本地已有季的缺失」跳过"
                          "（若要连整季 / 整剧一起补齐，请关掉该开关）" % item["name"])
            return None
        detail = self._tmdb_detail(item["tmdb"])
        tmdb_seasons = _extract_tmdb_seasons(detail)
        if not tmdb_seasons:
            # 解析不到时**把响应的结构（键名）写进日志**。不要只截前 400 字 ——
            # 实测该响应按字母序排键，`seasons` / `number_of_seasons` 都在 400 字之后被切掉了。
            hint = _describe_shape(detail)
            self.log.warn("TMDB 详情里没有解析出季列表。响应结构：%s" % scrub_text(hint, [self.ttd.token]))
            raise RuntimeError("TMDB 详情里没有解析出季列表（既没有 seasons 数组、也没有 "
                               "number_of_seasons 计数）—— 响应结构已写入运行日志，"
                               "请把这一行反馈给我们以便精确对接")
        status = _extract_tmdb_status(detail)

        # 待检查的季 = TMDB 给出的季 ∪ **本地已有的季**。
        # 为什么要并入本地季：TMDB 的 `number_of_seasons` 与本地分季方式可能不一致
        # （长番常见），只用 TMDB 枚举会漏检本地多出来的那些季；而 TMDB 不存在的季
        # 会走 `absent` 分支被安静跳过，没有副作用。
        candidates = set(tmdb_seasons) | set(int(s) for s in local.keys())

        result = {"series": item, "status": status, "seasons": {}, "undetermined": []}
        checked = 0
        absent = []
        for season in sorted(candidates):
            if season == 0 and not self.include_s00:
                continue
            if self.only_season_exist and season not in local:
                continue          # 该季本地一集都没有 → 按设置跳过
            checked += 1
            expected, why, reason = self._expected_episodes(item["tmdb"], season)
            if expected is None:
                if why == "error":
                    # 这一季**没查成** —— 绝不能当成「无缺失」，否则就是假阴性
                    result["undetermined"].append(("S%02d" % season, reason))
                    self.log.warn("「%s」S%02d 应有集数无法判定：%s"
                                  % (item["name"], season, reason))
                elif why == "absent":
                    absent.append(season)
                    self.log.info("「%s」S%02d TMDB 侧没有该季数据（%s）→ 跳过"
                                  % (item["name"], season, reason))
                continue
            have = set(local.get(season) or ())
            lacks = sorted(set(expected["numbers"]) - have)
            if not lacks and season in local:
                continue
            whole = not local.get(season)
            result["seasons"][season] = {
                "episodes": lacks if not whole else sorted(expected["numbers"]),
                "total": len(expected["numbers"]),
                "whole_season": whole,
                "why": "该季本地一集都没有" if whole else "",
            }
        if result["seasons"]:
            return result
        if result["undetermined"]:
            # 一个可判定的季都没有，但存在**读失败的季**：单独归类，不报「无缺失」
            self.undetermined.append((item["name"], result["undetermined"]))
            return None
        declared_absent = [s for s in absent if s in tmdb_seasons]
        if checked and len(absent) == checked and (local or declared_absent):
            # 这是**自相矛盾**的情形：TMDB 自己声明了这些季（或本地明明有内容），
            # 却对每一季都查不到集数据 —— 几乎不可能是「TMDB 真的没数据」，
            # 而是**「季集详情」接口不可用**（规范原文：该接口「只有当前详情配置支持
            # 完整季集模式时可用」）。
            # 必须归入「无法判定」；若放过就会把整库都报成「无缺失」，是**假阴性**。
            self.undetermined.append((item["name"], [
                ("全部季", "TMDB 季详情对每一季都没有返回集数据（该接口在当前详情配置下不可用）")]))
            self.log.warn("「%s」本地有 %d 个季、TMDB 声明 %d 个季，但季详情对每一季都查不到"
                          "集数据 → 判定为「无法判定」，**不做「无缺失」结论**"
                          % (item["name"], len(local), len(tmdb_seasons)))
            return None
        return None

    def _expected_episodes(self, tmdb_id, season):
        """取 TMDB 该季的「应有集号」；只统计已播出（受 only_aired 控制）。

        返回 ``(numbers, 状态, 原因)``，``numbers`` 为 ``None`` 时按状态区分：

        * ``"ok"``     —— 这一季**本来就没有可期待的集**（尚未播出 / 没有集数据）→ 静默跳过；
        * ``"absent"`` —— TMDB 没有这一季（404 或空）→ 记 info 后跳过，**不算无法判定**；
        * ``"error"``  —— 请求失败（网络 / 5xx / 解析异常）→ **计入「无法判定」**。

        ⚠️ 之前这里直接用会抛异常的 `get_json`：某一季 404 就把**整部剧**打成错误
        （用户实测里 50 部剧全是这样）；而另一端更危险 —— 若把失败当成「没有缺失」，
        用户会以为「这部剧是完整的」，其实是根本没查成。所以状态必须分开，且**逐季隔离**。

        实际请求走 :meth:`_tmdb_season_soft`：按「TMDB 数据源」路由到 TgtoDrive 代理或直连 TMDB。
        """
        status, data, err = self._tmdb_season_soft(tmdb_id, season)
        if status is None:
            return None, "error", "网络失败：%s" % (err or "未知")
        if status == 404:
            return None, "absent", "TMDB 没有这一季（HTTP 404）"
        if not 200 <= status < 300:
            if TMDB_READONLY_ERROR_CODE in (err or ""):
                return None, "error", (
                    "HTTP 409 %s —— TgtoDrive 未启用「完整 TMDB 季集模式」；"
                    "到「③ TMDB 设置」填入 TMDB API Key 并改用「直连 TMDB」即可绕过"
                    % TMDB_READONLY_ERROR_CODE)
            return None, "error", "HTTP %s：%s" % (status, err or "")
        if not isinstance(data, dict):
            return None, "absent", "响应不是 JSON 对象"
        numbers, air_dates = _extract_tmdb_episodes(data)
        if not numbers:
            return None, "absent", "该季没有返回任何集数据"
        if not self.only_aired:
            return {"numbers": sorted(numbers)}, "ok", ""
        today = date.today()
        aired, undated, bad_date = [], [], []
        for number in sorted(numbers):
            air = air_dates.get(number)
            if not air:
                undated.append(number)
                continue
            parsed = _parse_date(air)
            if parsed is None:
                # 有播出日期但**解析不出来**：既不能断定已播、也不能断定未播。
                # 绝不能像以前那样**静默丢掉** —— 那样这一集就永远不会被计入「应有」，
                # 它若真缺了也报不出来，是**假阴性**。
                bad_date.append(number)
                continue
            if parsed <= today:
                aired.append(number)
        if undated:
            self.log.info("S%02d 有 %d 集没有播出日期，按「未开播」处理，不计入应有集数：%s"
                          % (season, len(undated), _join_nums(undated)))
        if bad_date:
            self.log.warn("S%02d 有 %d 集的播出日期**无法解析**，按「未开播」处理、"
                          "不计入应有集数：%s（原始值：%s）—— 若这些集其实已播出，"
                          "请把该剧的季详情结构反馈给我们以便对接"
                          % (season, len(bad_date), _join_nums(bad_date),
                             "、".join(str(air_dates.get(n) or "")[:24] for n in bad_date[:3])))
        if not aired:
            # 整季都还没播出（或全部缺日期）→ 没有可期待的集，跳过；不报「整季缺失」
            self.log.info("S%02d 还没有任何已播出的集，跳过该季（不报缺失）" % season)
            return None, "ok", ""
        return {"numbers": aired}, "ok", ""

    def _resolve_libraries(self):
        """挑出要扫描的**剧集类**媒体库，并记录被排除的库。

        本插件**只处理剧集**：电影、音乐等类别不参与检测与补齐。
        排除依据是 Emby 媒体库的 `CollectionType`；读不到库列表时**降级**为
        「沿用用户填写的库 id（或全部）」并记警告，不会因为读不到库列表就直接失败。
        """
        self.libraries_skipped = []
        self.libraries_scanned = []
        try:
            libs = self.emby.libraries()
        except Exception as exc:
            self.log.warn("读取 Emby 媒体库列表失败（改为按条目类型兜底）：%s" % str(exc)[:160])
            return self.library_ids
        if not libs:
            self.log.warn("Emby 没有返回媒体库列表，改为按条目类型兜底")
            return self.library_ids

        by_id = {lib["id"]: lib for lib in libs}
        kept = []
        if self.library_ids:
            # 用户指定了库 id：逐个判定，非剧集库显式排除并记录
            for wanted in self.library_ids:
                lib = by_id.get(wanted)
                if lib is None:
                    # 不在列表里（可能是隐藏库）：交给条目类型兜底，不擅自丢弃
                    kept.append(wanted)
                    continue
                if lib["type"] in NON_TV_LIBRARY_TYPES:
                    self.libraries_skipped.append((lib["name"] or lib["id"], lib["type"]))
                    continue
                kept.append(wanted)
        else:
            for lib in libs:
                if lib["type"] in NON_TV_LIBRARY_TYPES:
                    self.libraries_skipped.append((lib["name"] or lib["id"], lib["type"]))
                    continue
                kept.append(lib["id"])

        self.libraries_scanned = kept
        if self.libraries_skipped:
            self.log.info("已按媒体库类型排除 %d 个非剧集库（本插件只处理剧集）：%s"
                          % (len(self.libraries_skipped),
                             "、".join("%s[%s]" % (n, t or "无类型")
                                       for n, t in self.libraries_skipped[:8])))
        self.log.info("本次扫描的剧集类媒体库：%s"
                      % ("、".join(kept) if kept else "（无）"))

        if not kept:
            detail = "、".join("%s（%s）" % (n, t or "无类型")
                               for n, t in self.libraries_skipped[:10]) or "（无）"
            raise ValueError(
                "没有找到可扫描的**剧集类**媒体库 —— 本插件只处理剧集，电影 / 音乐等类别不参与。"
                "Emby 里现有的库：%s。"
                "如果你在「媒体库 id」里手动填了库，请确认填的是剧集库（CollectionType 为 tvshows）；"
                "清空该字段则自动扫描全部剧集库。" % detail)
        return kept

    def _load_series(self):
        ids = self._resolve_libraries()
        self.log.info("读取 Emby 剧集列表：%s（%s）"
                      % ("、".join(ids) if ids else "全部媒体库",
                         self.emby_source_note or "插件表单"))
        return self.emby.series(ids)

    def _require_readiness(self, need_search):
        if not self.ttd.configured:
            raise ValueError("未配置 TgtoDrive 地址或 OpenAPI 令牌：请在「① 连接设置」填写，"
                             "或配置容器环境变量 TGTO_OPENAPI_BASE_URL / TGTO_OPENAPI_TOKEN")
        if not self.emby.configured:
            raise ValueError("未配置 Emby 地址或 API Key：本插件需要直连 Emby 才能读取"
                             "「本地已有哪些集」（TgtoDrive 的接口没有提供该数据）。"
                             "请在「① 连接设置」填写，或在 TgtoDrive 影视设置里配好 Emby 后留空。")
        if self.tmdb_source == TMDB_SRC_DIRECT and not self.tmdb.configured:
            raise ValueError("「TMDB 数据源」选了「直连 TMDB」，但没有可用的 TMDB API Key。"
                             "请在「③ TMDB 设置」填写 API Key，或把数据源改回"
                             "「自动（有 Key 直连，无 Key 走 TgtoDrive 代理）」/「TgtoDrive 详情代理」。")
        if need_search and self.source in (SOURCE_PANSOU, SOURCE_BOTH) \
                and not self.pansou.configured:
            raise ValueError("未配置盘搜地址，但搜索源包含盘搜。请在「③ 补齐设置」填写，"
                             "或把搜索源改成「TgtoDrive 内置资源检索」")

    # -- 补齐 --------------------------------------------------------------

    def do_fill(self, check_result):
        if not self.missing:
            self.log.info("没有缺失，跳过补齐")
            return check_result

        # 补齐会真正调用搜索源，这里才校验「需要搜索」的前置条件
        self._require_readiness(need_search=True)

        self.log.info("开始补齐：动作=%s｜dry_run=%s｜搜索源=%s｜单次上限=%d 部/次"
                      % (ACTION_LABELS.get(self.action), self.dry_run,
                         SOURCE_LABELS.get(self.source), self.max_fill))
        if self.action != ACTION_RECORD and self.dry_run:
            self.log.warn("当前是 dry-run：只展示将要执行的操作，不会真正转存 / 离线下载")
        if self.action != ACTION_RECORD and not self.dry_run:
            self.log.warn("**非 dry-run**：补齐动作会真实写网盘 / 创建离线任务")

        handled = 0
        fill_errors = []
        fill_deadline = (self.started_at or time.time()) + TOTAL_TIME_BUDGET
        for item in self.missing:
            if self.max_fill and handled >= self.max_fill:
                self.log.info("已达单次补齐上限 %d 部，剩余 %d 部留到下次运行"
                              % (self.max_fill, len(self.missing) - handled))
                break
            if time.time() > fill_deadline:
                # 与检测阶段同理：补齐每部都要发搜索请求，缺集一多就会撞硬超时。
                # 到点就带着已处理的结果收工，剩余留到下次。
                self.fill_budget_exhausted = (handled, len(self.missing) - handled)
                self.log.warn("总时间预算（%d 秒）用尽：本次只补齐了 %d 部，"
                              "剩余 %d 部留到下次运行"
                              % (TOTAL_TIME_BUDGET, handled, len(self.missing) - handled))
                break
            # 与检测阶段同理：**一部剧出问题不该把整轮补齐拖垮**。此前这里没有逐部隔离，
            # 任一步抛异常（例如某条数据缺字段）都会让整轮失败、已处理的结果一起丢掉。
            name = (item.get("series") or {}).get("name") or "（未知剧名）"
            # 记下「尝试过」：通知里要能区分「补了但失败」与「这次没轮到它」
            self.fill_attempted.add(name)
            try:
                self.filled.append(self._fill_one(item))
            except Exception as exc:
                fill_errors.append("%s：%s" % (name, str(exc)[:100]))
                self.log.warn("补齐「%s」失败（已跳过该项，其余继续）：%s" % (name, exc))
            handled += 1
        # 存到实例上：通知要按「失败原因」分类，不能只留在局部变量里
        self.fill_errors = fill_errors
        if not self.max_fill and handled > 10 and not self.fill_budget_exhausted:
            self.log.info("本次不限制补齐部数，共处理 %d 部；建议先用「单次补齐上限」小步验证"
                          % handled)

        rows = []
        by_status = {}
        for rec in self.filled:
            for entry in rec["actions"]:
                cand = entry.get("candidate") or {}
                # status 现在由 _fill_one 按**真实执行结论**回写（ACT_*）；
                # 这里的兜底只在极端情况下（有候选却没状态）才可能触发。
                status = entry.get("status") or (ACT_DONE if cand else "")
                by_status[status] = by_status.get(status, 0) + 1
                rows.append([
                    rec["series"],
                    entry["season"],
                    ("整季" if entry.get("whole_season") else _join_nums(entry["missing"])) or "-",
                    entry["keyword"],
                    "%d 条" % entry.get("candidate_count", len(entry["candidates"])),
                    # 覆盖列：说明**凭什么**选中这条（或为什么跳过）——
                    # 判断依据是候选标题里的集号，认不出时写「覆盖未知」
                    entry.get("coverage") or "-",
                    cand.get("type") or "-",
                    # 「仅记录」时这一列就是链接本身，截太短会拿不到可用链接（分享链接常有
                    # 200+ 字）。留 400 字足以覆盖常见形态，200 行 × 400 字仍在结果上限内。
                    entry["detail"][:400],
                ])
        stats = [
            ("检测到缺集", "%d 部剧" % len(self.missing)),
            ("本次处理", "%d 部 / %d 季" % (len(self.filled), len(rows))),
            ("补齐动作", ACTION_LABELS.get(self.action, self.action)),
            # 「仅记录」无论开关如何都不会写网盘，别把它标成「预览（dry-run）」——
            # 那会让用户以为「关掉预览就会真写入」，其实还得换动作。
            ("执行方式", "仅记录（不写入）" if self.action == ACTION_RECORD
             else ("预览（dry-run）" if self.dry_run else "实际执行")),
        ]
        if self.action == ACTION_RECORD:
            alert = ("**仅记录模式**：下表列出每个缺失季选中的候选链接与提取码，"
                     "本插件**没有写入网盘、也没有创建离线任务**。"
                     "想真正补齐，请把「补齐设置 → 补齐动作」改成「转存到网盘」或"
                     "「提交离线下载」。")
        elif self.dry_run:
            alert = ("**预览模式（dry-run）**：下表只是将执行的操作与候选链接，"
                     "没有写入网盘、也没有创建离线任务。"
                     "确认无误后把「补齐设置 → 预览模式」关掉再跑一次。")
        else:
            alert = ("已按「%s」处理 %d 部 / %d 季，逐条结果见下表与运行日志。"
                     % (ACTION_LABELS.get(self.action), len(self.filled), len(rows)))
        notes = []
        if self.fill_budget_exhausted:
            done, left = self.fill_budget_exhausted
            notes.append("⏱ **总时间预算（%d 秒）用尽**：本次只补齐了 %d 部，剩余 %d 部留到下次运行"
                         "（缺集很多时属正常，多跑几次即可）。"
                         % (TOTAL_TIME_BUDGET, done, left))
        elif self.max_fill and len(self.filled) < len(self.missing):
            notes.append("本次按「单次补齐上限」（%d 部）处理了 %d 部，还有 %d 部未处理 —— "
                         "再运行一次即可继续（下次会重新检测，再补齐尚未补齐的）。"
                         % (self.max_fill, len(self.filled), len(self.missing) - len(self.filled)))
        if self.undetermined:
            # 别让「补齐完成」被误读成「全都处理好了」：这些剧压根没进入缺失清单
            notes.append("⚠️ 另有 **%d 部剧无法判定**、**没有参与补齐**（某些季的应有集数没读成，"
                         "见检测阶段的警告与运行日志）—— 补齐不覆盖它们。"
                         % len(self.undetermined))
        if by_status.get("no_candidate"):
            notes.append("有 %d 个季**没搜到任何候选**（也可能是候选类型与所选动作不匹配 —— "
                         "例如离线下载只接受磁力 / 电驴 / 种子）。详见下表的「处理结果」列。"
                         % by_status["no_candidate"])
        if by_status.get("no_cover"):
            notes.append("🚫 有 %d 个季**搜到的候选都不含缺失集**（候选标题里写明包的是别的集）—— "
                         "已跳过，没有转存无用资源。换个搜索源、或稍后再试一次。"
                         % by_status["no_cover"])
        if by_status.get(ACT_SKIPPED):
            notes.append("⏭ 有 %d 个季**选中的候选类型与补齐动作不匹配**（动作是「提交离线下载」"
                         "但候选是网盘分享链接 —— 离线接口只收磁力 / 电驴 / 种子）—— 已跳过。"
                         "把「补齐设置 → 补齐动作」改成「转存到网盘」再跑一次即可"
                         "（分享链接走转存接口；磁力 / 电驴 / 种子两个动作都能提交）。"
                         % by_status[ACT_SKIPPED])
        if by_status.get(ACT_FAILED):
            notes.append("✘ 有 %d 个季**执行补齐动作失败**（接口返回错误，未写入网盘）—— "
                         "原因见下表的「处理结果」列与运行日志，可直接重跑。"
                         % by_status[ACT_FAILED])
        if by_status.get("partial_skip"):
            notes.append("⏸ 有 %d 个季**只搜到部分覆盖的候选**（例如缺 E04-E12，却只找到含 E01-E03 的包）—— "
                         "转存 / 离线会真实写网盘、可能消耗会员点数，补一半并不划算，已跳过。"
                         "只想先拿到链接的话，把「补齐动作」临时改成「仅记录」再跑一次即可。"
                         % by_status["partial_skip"])
        if by_status.get("partial_record"):
            notes.append("⚠️ 有 %d 个季选中的候选**只覆盖一部分缺失集**（见「覆盖」列）—— "
                         "列出的链接补不齐，剩余集需要换个资源再跑一次。"
                         % by_status["partial_record"])
        if fill_errors:
            # 补齐失败必须显式列出：否则「补齐处理完成」会被读成「这一部已经补好了」
            notes.append("以下剧集**补齐失败**（已跳过该项、其余照常处理，详见日志）："
                         + "；".join(fill_errors[:5]))
        # 缺失明细表要放进 extra_tables：**先算一次存下来**。此前「行数」和「行内容」
        # 各调用了一次 _missing_rows()，等于把同一张表连算两遍（每行都要拼字符串、
        # 还要重新遍历 self.missing）。
        missing_rows = self._missing_rows()
        return self._result(
            ok=True, title="补齐处理完成", tone="default",
            alert=alert, stats=stats, rows=rows,
            rows_label="补齐明细（共 %d 行，按季展开）" % len(rows),
            headers=["剧集", "季", "缺失集", "搜索关键词", "候选数", "覆盖", "类型", "处理结果"],
            notes=notes,
            extra_tables=[{"type": "table", "label": "缺失明细（共 %d 行）" % len(missing_rows),
                           "headers": ["剧集", "季", "缺失集", "集数", "说明"],
                           "rows": missing_rows or [["（无）", "-", "-", "-", "-"]]}],
            extra_components=self._search_note_components())

    def _fill_one(self, item):
        """对一部剧的**每一个缺失季**分别搜索并执行补齐动作。

        为什么要按季处理：此前整部剧只挑一个候选、只执行一次动作 ——
        一部剧缺 S01/S02/S03 时只会补到其中一个季，用户得反复运行才能补齐。
        现在每个缺失季各自搜索、各自挑候选、各自执行，并分别记账。
        """
        name = item["series"]["name"]
        seasons = sorted(item["seasons"])
        title = _norm_title(name)
        self.log.info("为「%s」搜索缺失内容（%s）"
                      % (name, "、".join("S%02d" % s for s in seasons)))
        record = {"series": name, "seasons": {("S%02d" % s): item["seasons"][s]["episodes"]
                                             for s in seasons},
                  "actions": []}
        for season in seasons:
            detail = item["seasons"][season]
            missing = list(detail.get("episodes") or [])
            # 多季同时缺失时用剧名搜（一次拿到整包更省事）；只缺一季时带上季号，
            # 减少「想补 S02 却抓到 S01 包」的概率。
            keyword = "%s S%02d" % (title, season) if len(seasons) == 1 else title
            # 把已经归一化好的 title 传下去：_search_for 每个季都要用它，
            # 不传就会按季把同一个剧名重复归一化一遍（6 次正则替换）。
            candidates, errors = self._search_for(item, season, keyword, title)
            entry = {
                "season": "S%02d" % season,
                "keyword": keyword,
                "missing": missing,
                "whole_season": bool(detail.get("whole_season")),
                # 只留前 5 条进结果页（免得单页过大），但**数量要单独记**——
                # 此前用 len(只留 5 条的那份列表) 当候选总数，20 条也会显示成「5 条」。
                "candidates": candidates[:5],
                "candidate_count": len(candidates),
                "errors": errors,
                "candidate": None,
                "coverage": "",
                "status": "",
                "detail": "",
            }
            # 按「**缺失集是否真的在这个包里**」排序并筛掉明确不含缺失集的候选
            ordered, excluded = self._rank_candidates(candidates, missing)
            if candidates:
                self.log.info("「%s」%s 覆盖判断：候选 %d 条，其中 %d 条可能含缺失集 %s%s"
                              % (name, entry["season"], len(candidates), len(ordered),
                                 _join_nums(missing) or "（整季）",
                                 ("；排除 %d 条明确不含缺失集的" % len(excluded))
                                 if excluded else ""))
                self._log_candidates(ordered, "可用候选")
                self._log_candidates(excluded, "已排除候选")

            chosen = None
            if not candidates:
                entry["status"] = "no_candidate"
                entry["detail"] = ("没有搜到候选资源"
                                   + ("；" + "；".join(errors) if errors else ""))
                self.log.warn("「%s」%s 未搜到候选资源" % (name, entry["season"]))
            elif not ordered:
                # 搜到了，但没有一条包含缺失集 —— 与其转存一个没用的包，不如如实说明。
                # 这是本插件此前最容易出错的地方：缺 E04-E12 却选中「S01E01」，
                # 转存出去占网盘、耗点数，结果页还显示成「已处理」。
                entry["status"] = "no_cover"
                entry["coverage"] = "均不含缺失集"
                entry["detail"] = ("跳过：搜到 %d 条候选，但标题里都写明了**不含缺失集**（%s），"
                                   "已跳过以免转存无用资源"
                                   % (len(candidates),
                                      "、".join((e["candidate"].get("note") or "-")[:30]
                                                for e in excluded[:2])))
                self.log.warn("「%s」%s 搜到 %d 条候选但不含缺失集（%s）→ 跳过"
                              % (name, entry["season"], len(candidates),
                                 _join_nums(missing) or "整季"))
            else:
                top = ordered[0]
                if top["state"] == "partial" and self.action != ACTION_RECORD:
                    # 只覆盖一部分：转存 / 离线会**真实占用网盘、消耗会员点数**，
                    # 补一半就写进去并不划算 → 跳过并把缺口说清楚（记录模式无副作用，照常列出）
                    entry["status"] = "partial_skip"
                    entry["coverage"] = top["label"]
                    entry["detail"] = ("跳过：最合适的候选只覆盖缺失集的一部分（%s）—— "
                                       "转存 / 离线会真实写网盘，补一半并不划算；"
                                       "可换个搜索源或稍后再跑一次补齐剩余"
                                       % top["label"])
                    self.log.warn("「%s」%s 最优候选只覆盖一部分（%s）→ 写动作已跳过"
                                  % (name, entry["season"], top["label"]))
                else:
                    chosen = top

            if chosen is not None:
                best = chosen["candidate"]
                entry["candidate"] = best
                entry["coverage"] = chosen["label"]
                # 状态必须按 **真实执行结论** 回写。曾经的写法是先无条件写 done
                # 再调 _apply_action，于是「候选是磁力→跳过」「接口报错→失败」
                # 也统统记成成功，通知里赫然列进「② 被成功补全」—— 用户以为补齐了，
                # 网盘里却什么都没有。
                action_status, entry["detail"] = self._apply_action(best)
                if self.action == ACTION_RECORD and chosen["state"] == "partial":
                    # 仅记录 + 只覆盖一部分：链接确实列出了，但补不齐 —— 通知里要带
                    # 【部分补全】标记：不能算成功，也不能混在普通失败里看不出来。
                    entry["status"] = "partial_record"
                else:
                    entry["status"] = action_status
                # 日志里必须留下**完整链接**（尤其是「仅记录」动作 —— 列出链接就是它的目的；
                # 此前注释只看 note/url 的前 80 字，长分享链接会被截掉、无法复制）
                self.log.info("「%s」%s 选定候选（%s）：%s｜%s｜%s"
                              % (name, entry["season"], chosen["label"],
                                 best.get("type") or "未知",
                                 (best.get("note") or "-")[:60], best.get("url") or ""))
            record["actions"].append(entry)
        return record

    def _log_candidates(self, items, tag="候选"):
        """把候选标题打进运行日志。

        覆盖判断唯一依据就是候选标题，判断一旦出错（比如某种没见过的命名方式），
        用户需要能对着**原始标题**看出是哪一步认错了 —— 所以这里明确打出来。
        """
        lines = []
        for item in (items or [])[:5]:
            note = str(item["candidate"].get("note") or "-").replace("\n", " ")[:56]
            lines.append("%s〔%s〕" % (note, item.get("label") or "覆盖未知"))
        if lines:
            self.log.info("%s（前 %d 条）：%s" % (tag, len(lines), " ｜ ".join(lines)))

    def _search_note_components(self):
        return [
            {"type": "text", "text": "**「覆盖」列是怎么来的**：搜索源返回的候选里既有**单集**、"
                                     "也有**部分集**、也有**整季包**。插件会从候选标题里读出它包含的集号"
                                     "（`第01-12集` / `更新至第10集` / `E01-E12` / `S01E05` / `全集` 等），"
                                     "再与缺失集比对，优先级为 **完整覆盖 → 覆盖未知 → 部分覆盖**，"
                                     "**明确不含缺失集的直接排除**（标题里没有集号的算「未知」，不会被误排除）。"
                                     "\n\n对**会真实写网盘**的动作（转存 / 离线），遇到「只有部分覆盖」会**跳过** —— "
                                     "补一半不划算；「仅记录」没有副作用，照常列出并标注缺口。",
             "style": {"tone": "muted"}},
            {"type": "text", "text": "**关于「TgtoDrive 内置资源检索」**：该接口"
                                     "（`/api/media/resources/search`）在规范里没有响应 schema，"
                                     "本插件已把原始响应写入运行日志。若候选为空，"
                                     "请对照日志与「我的插件 → 影视发现」页面确认字段，"
                                     "以便后续版本精确对接。盘搜（PanSou）的响应结构是公开文档化的，"
                                     "候选解析完整。", "style": {"tone": "muted"}},
        ]

    def _search_for(self, item, season, keyword, title=None):
        """针对**一个季**在配置的搜索源里找候选；返回 ``(候选列表, 错误列表)``。

        ``title`` 是调用方已经归一化好的剧名（供粗筛用）；不传则就地归一化。
        """
        candidates, errors = [], []
        detail = item["seasons"].get(season) or {}
        missing = list(detail.get("episodes") or [])
        if title is None:
            title = _norm_title(item["series"]["name"])
        year = item["series"].get("year") or 0

        if self.source in (SOURCE_BUILTIN, SOURCE_BOTH):
            body = {"title": title, "media_type": "tv", "season": season,
                    "tmdb_id": str(item["series"].get("tmdb") or "")}
            if year:
                body["year"] = year
            # 整季缺失时不传 episode（要的是整季）；部分缺失时传第一个缺的集
            if missing and not detail.get("whole_season"):
                body["episode"] = missing[0]
            if self.resource_sources:
                # 来源标识来自 TgtoDrive 的 /api/media/providers，由用户在其列出的范围内选择
                body["sources"] = self.resource_sources
            try:
                status, text, data = self.ttd.post_json("/api/media/resources/search", body)
                self.log.info("内置检索 S%02d%s → HTTP %s，响应：%s"
                              % (season, ("E%02d" % missing[0]) if body.get("episode") else "",
                                 status, scrub_text((text or "")[:400], [self.ttd.token])))
                if status is not None and 200 <= status < 300 and isinstance(data, dict):
                    # 内置检索是按 title 精确查询的，这里不再做标题关键词二次筛（见 _is_relevant）
                    candidates.extend(_extract_builtin_resources(data))
                elif status is not None and not 200 <= status < 300:
                    errors.append("内置检索 HTTP %s" % status)
            except Exception as exc:
                errors.append("内置检索异常：%s" % str(exc)[:100])
                self.log.warn("内置检索失败：%s" % str(exc)[:160])

        if self.source in (SOURCE_PANSOU, SOURCE_BOTH):
            clouds = self.cloud_types or []
            cache_key = (keyword, tuple(clouds))
            if cache_key in self._pansou_cache:
                relevant, err = self._pansou_cache[cache_key]
                self.log.info("盘搜「%s」本轮已查过，复用结果（%d 条候选）"
                              % (keyword, len(relevant)))
            else:
                cand, _raw, err = self.pansou.search(keyword, cloud_types=clouds)
                relevant = []
                if not err:
                    relevant = [c for c in cand if _is_relevant(c, title)]
                    dropped = len(cand) - len(relevant)
                    self.log.info("盘搜「%s」返回 %d 条候选%s；按剧名粗筛后保留 %d 条%s"
                                  % (keyword, len(cand),
                                     ("（限定类型：" + "、".join(clouds) + "）") if clouds else "",
                                     len(relevant),
                                     ("（剔除 %d 条标题不含剧名关键词的）" % dropped) if dropped else ""))
                self._pansou_cache[cache_key] = (relevant, err)
            if err:
                errors.append("盘搜：%s" % err)
            else:
                candidates.extend(list(relevant))

        return candidates, errors

    def _rank_candidates(self, candidates, missing):
        """给候选排序，并挑出「明确不含缺失集」的那些。

        排序键（越小越优先），三级的顺序是有讲究的：

        1. **动作能不能用它** —— 「提交离线下载」只吃磁力 / 电驴 / 种子，网盘分享链接
           对它无效；「转存到网盘」则**两类都吃得下**：分享链接走转存接口，
           磁力 / 电驴 / 种子走 TTD 的离线下载接口（115 的离线设置已在 TTD 侧配好），
           所以对转存动作来说离线链接不再是「实在没别的候选时才轮到」的备胎。
           不在「盘搜网盘类型」白名单里的排最后。
        2. **是否覆盖缺失集** —— 整季包 / 完整覆盖排最前；「覆盖未知」次之（认不出 ≠ 不覆盖，
           不能因为认不出就把它排到后面）；只覆盖一部分再次之；
           **明确不含缺失集的直接排除**。
           此前完全不看这一项，于是缺 E04-E12 时可能选中「S01E01」这类单集资源 ——
           转存它白白占用网盘、消耗点数，结果页还显示成「已处理」。
        3. 资源新旧（越新越可能有效），最后是标题长度（短标题通常更精确）。

        返回 ``(有序列表, 被排除列表)``，列表项为
        ``{"candidate": …, "state": …, "covered": …, "label": …}``。
        """
        def rank(candidate):
            kind = candidate.get("type") or ""
            in_whitelist = (not self.cloud_types) or kind in self.cloud_types
            is_offline = _is_offline_link(candidate.get("url"), kind)
            if self.action == ACTION_OFFLINE:
                if is_offline:
                    return 0
                return 1 if in_whitelist else 2
            if self.action == ACTION_TRANSFER:
                # 分享链接与磁力 / 电驴 / 种子都能进网盘（前者转存接口、后者离线接口），
                # 同权比拼覆盖度；只把白名单外的排后面。
                return 0 if in_whitelist else 1
            # 仅记录：不执行任何写入，链接形态无所谓
            return 0 if (is_offline or in_whitelist) else 1

        coverage_rank = {"all": 0, "full": 0, "unknown": 1, "partial": 2}
        ordered, excluded = [], []
        for candidate in candidates or []:
            state, covered, label = _episode_coverage(candidate.get("note"), missing)
            item = {"candidate": candidate, "state": state,
                    "covered": covered, "label": label}
            if state == "none":
                excluded.append(item)      # 不参与排序，调用方会说明并跳过
            else:
                ordered.append(item)

        def sort_key(item):
            candidate = item["candidate"]
            stamp = _parse_datetime(candidate.get("datetime"))
            return (rank(candidate),
                    coverage_rank.get(item["state"], 3),
                    -len(item["covered"]),          # 同为「部分覆盖」时，覆盖得多的优先
                    -stamp if stamp else 0,
                    -len(candidate.get("note") or ""))
        return sorted(ordered, key=sort_key), excluded

    def _apply_action(self, candidate):
        """按动作处理一条候选；返回 ``(状态, 可读结论)``。

        **动作与候选类型的匹配检查必须放在 dry-run 分支之前**：dry-run 的意义就是
        「准确预告真实运行会做什么」。此前先返回「将提交离线下载…」，于是预览里显示
        会离线下载，真跑时却因候选是网盘链接而「跳过」—— 预览与实际不一致。

        **磁力 / 电驴 / 种子的路由**（2026-10-15 按用户实测反馈调整）：曾因「转存接口的
        share_url 收不了磁力」就在「转存到网盘」动作下直接跳过这类候选 —— 但用户环境里
        TTD 的 115 网盘**离线设置已配好**，TTD 的离线下载接口（`link` 字段）专收
        「磁力或其他受支持的离线链接」，提交即可由 TTD 转存进网盘。所以现在：
        「转存」遇到离线链接改走**离线下载接口**，不再跳过；只有「提交离线下载」
        遇到网盘分享链接时才真的跳过（那个接口确实收不了分享链接）。

        返回值里的状态是**真实执行结论**（ACT_* 常量），调用方必须用它记账：
        「跳过」「失败」都不是成功，不能凭「选中了候选」就默认 done。
        """
        kind = candidate.get("type") or "未知"
        label = PANSOU_CLOUD_LABELS.get(kind, kind)
        url = candidate.get("url") or ""
        pwd = candidate.get("password") or ""
        is_offline = _is_offline_link(url, kind)

        if self.action == ACTION_RECORD:
            return ACT_DONE, "仅记录：%s%s" % (url, ("（提取码 %s）" % pwd) if pwd else "")

        if self.action == ACTION_OFFLINE and not is_offline:
            return (ACT_SKIPPED,
                    "跳过：候选是「%s」，离线下载只支持磁力 / 电驴 / 种子" % label)
        # 「转存」+ 离线链接：不再跳过（见上面的说明），与「离线」动作共用下面的提交分支

        provider = self._effective_provider()
        if self.dry_run:
            # 预告也要按真实路由说：离线链接预告「将提交离线下载」，分享链接预告「将转存」
            if is_offline:
                return (ACT_PREVIEW,
                        "将提交离线下载：%s%s（目标网盘：%s）" % (
                            url, ("（提取码 %s）" % pwd) if pwd else "",
                            provider or "TgtoDrive 默认"))
            return (ACT_PREVIEW,
                    "将%s：%s%s（目标网盘：%s）" % (
                        ACTION_LABELS.get(self.action), url,
                        ("（提取码 %s）" % pwd) if pwd else "",
                        provider or "TgtoDrive 默认"))

        # 磁力 / 电驴 / 种子 → TTD 离线下载接口（`link` 字段；目标网盘的离线设置
        # 已在 TTD 侧配好，插件只负责提交）。转存与离线两个动作都可能走到这里。
        if is_offline:
            # source 用候选自带的来源（盘搜会给 tg:xxx / plugin:xxx，内置检索给 builtin），
            # 不要硬编码 —— 否则把内置检索的结果标成「来自盘搜」是错的。
            body = {"link": url, "source": candidate.get("source") or "plugin",
                    "text": candidate.get("note") or ""}
            if provider:
                body["provider"] = provider
            status, text, data = self.ttd.post_json("/api/media/resources/offline", body)
            ok = status is not None and 200 <= status < 300
            self.log.info("提交离线下载 HTTP %s（目标：%s）：%s"
                          % (status, provider or "TgtoDrive 默认",
                             scrub_text((text or "")[:300], [self.ttd.token])))
            if ok:
                return ACT_DONE, ("已提交离线下载（HTTP %s，目标 %s）"
                                  % (status, provider or "TgtoDrive 默认"))
            if _is_duplicate_offline_error(status, data, text):
                # 115 对重复提交同一条磁力 / 种子返回 502 + 115_OFFLINE_FAILED
                # 「任务已存在」—— 资源此前已提交进离线队列（多跑几次就会撞上），
                # 不是失败。按已提交记账，但说明里写清楚「未重复创建」。
                return ACT_DONE, ("离线任务已存在（115 未重复创建）—— 该链接此前已提交过，"
                                  "资源已在 115 的离线队列中，本次未重复提交")
            return ACT_FAILED, ("离线下载失败：HTTP %s %s"
                                % (status, _api_error_brief(text)))

        if self.action == ACTION_TRANSFER:
            body = {"share_url": url, "source": candidate.get("source") or "plugin"}
            # ⚠️ provider 传**分享链接所属网盘**（源），不是转存目标网盘！
            # 2026-10-15 实测：把目标（115）当 provider 传，TTD 一律 409
            # SHARE_PROVIDER_MISMATCH「分享链接实际为光鸭链接，…」—— 它按 URL
            # 认出了链接的真实网盘，与提交的 provider 不符。转存目标由 TTD 自己的
            # 影视设置（target_provider）决定，这里不传也绝不能传成目标。
            # 认不出网盘类型时**不传 provider**，让 TTD 按 URL 自动识别。
            src_provider = str(kind or "").strip().lower()
            if src_provider in TRANSFER_SOURCE_PROVIDERS:
                body["provider"] = src_provider
            if pwd:
                # ⚠️ 转存接口没有公开的 schema，规范里列出的字段是
                # share_url/provider/source/slug/candidate_item_id/max_points；
                # 分享提取码没有专用字段，这里按规范里的 `slug` 传（尽力而为）。
                body["slug"] = pwd
            # 点数上限直接用 TgtoDrive 影视设置里的值，避免本插件再维护一份
            if self.ttd_max_points is not None:
                body["max_points"] = self.ttd_max_points
                body["enforce_points_limit"] = True
            status, text, data = self.ttd.post_json("/api/media/resources/transfer", body)
            ok = status is not None and 200 <= status < 300
            self.log.info("提交转存 HTTP %s（来源：%s，点数上限：%s）：%s"
                          % (status, src_provider or "TTD 自动识别",
                             self.ttd_max_points if self.ttd_max_points is not None else "未限制",
                             scrub_text((text or "")[:300], [self.ttd.token])))
            if ok:
                return ACT_DONE, ("已提交转存（HTTP %s，来源 %s）"
                                  % (status, src_provider or "TTD 自动识别"))
            return ACT_FAILED, ("转存失败：HTTP %s %s"
                                % (status, _api_error_brief(text)))

        return ACT_NOOP, "未执行"

    # -- 生效配置 ----------------------------------------------------------

    # -- 运行结果通知 --------------------------------------------------------

    @staticmethod
    def _numbered(items, limit=NOTIFY_MAX_ITEMS):
        """渲染成 ``1. xxx`` 形式的行；超长只留前 N 条并说明还剩多少。"""
        if not items:
            return ["（无）"]
        lines = ["%d. %s" % (index, text) for index, text in enumerate(items[:limit], 1)]
        if len(items) > limit:
            lines.append("…另有 %d 部，完整明细见 ttd 插件结果页" % (len(items) - limit))
        return lines

    def _notify_items(self):
        """把本次结果整理成通知要的三类。

        返回 ``(missing_lines, ok_lines, bad_lines, extra_notes)``；
        ``ok_lines`` / ``bad_lines`` 为 ``None`` 表示**本次根本没有执行补齐**（仅检测模式）
        —— 这与「执行了但一部都没成功」是两回事，必须区分开，否则用户会误读成补齐全失败。
        """
        missing_lines = []
        for item in self.missing:
            parts = []
            for season, detail in sorted(item["seasons"].items()):
                if detail.get("whole_season"):
                    parts.append("S%02d 整季缺" % season)
                else:
                    parts.append("S%02d 缺 %s" % (
                        season, _join_nums(detail.get("episodes") or []) or "整季"))
            if item.get("undetermined"):
                parts.append("另有 %s 无法判定" % "、".join(s for s, _w in item["undetermined"]))
            missing_lines.append("%s —— %s" % (item["series"]["name"], "；".join(parts)))

        extra_notes = []
        if self.undetermined:
            extra_notes.append("另有 %d 部剧无法判定（某个季的「应有集数」没读成，"
                               "既没算作缺失、也没算作完整）：%s"
                               % (len(self.undetermined),
                                  "、".join(n for n, _u in self.undetermined[:8])))
        if self.budget_exhausted:
            done, all_total, _start = self.budget_exhausted
            extra_notes.append("检测因时间预算提前收工：本次只检测了 %d 部（整库 %d 部），"
                               "进度已保存，下次运行会继续" % (done, all_total))
        if self.fill_budget_exhausted:
            done, left = self.fill_budget_exhausted
            extra_notes.append("补齐因时间预算提前收工：只处理了 %d 部，剩余 %d 部留到下次"
                               % (done, left))

        if self.func != FUNC_FILL:
            return missing_lines, None, None, extra_notes

        ok_lines, bad_lines, handled = [], [], set()
        for rec in self.filled:
            name = rec.get("series") or "（未知剧名）"
            handled.add(name)
            ok_seasons, bad_parts, partial = [], [], False
            for entry in rec.get("actions") or []:
                season = entry.get("season") or "-"
                status = entry.get("status") or ""
                cover = entry.get("coverage") or ""
                detail = str(entry.get("detail") or "")
                if status in (ACT_DONE, ACT_PREVIEW):
                    # ACT_PREVIEW 是 dry-run 的「将要执行」—— 归入②没问题，
                    # 标题里已注明「预览模式，未真正执行」。
                    ok_seasons.append(season)
                    continue
                if status in ("partial_record", "partial_skip"):
                    # 「补全一部分」必须**文字标记**出来 —— 既不能算成功，
                    # 也不能混在普通失败里看不出来。
                    partial = True
                    bad_parts.append("%s ⚠️【部分补全】只补到一部分（%s），未完全补全"
                                     % (season, cover or "覆盖不全"))
                    continue
                if status == ACT_FAILED:
                    # 接口真的返回了错误（HTTP 5xx/4xx）：是失败，不是成功。
                    bad_parts.append("%s ✘ 补全失败（%s）"
                                     % (season, (detail or "接口未返回成功")[:80]))
                    continue
                reason = {"no_cover": "搜到的资源都不含缺失集",
                          "no_candidate": "没有搜到候选资源",
                          # detail 本身就以「跳过：候选是「磁力」…」开头，直接拿来用，
                          # 不要再套一层「已跳过」—— 否则通知里会出现「跳过：跳过：」。
                          ACT_SKIPPED: detail[:80] or "候选类型与补齐动作不匹配，已跳过",
                          ACT_NOOP: "未执行（未知原因）"}.get(status, status or "未知原因")
                bad_parts.append("%s ✘ 未补全（%s）" % (season, reason))
            if bad_parts:
                tail = ("；已完成：%s" % "、".join(ok_seasons)) if ok_seasons else ""
                bad_lines.append("%s%s —— %s%s"
                                 % ("⚠️ " if partial else "", name, "；".join(bad_parts), tail))
            elif ok_seasons:
                ok_lines.append("%s —— %s" % (name, "、".join(ok_seasons)))

        # 补齐过程中抛异常的（do_fill 已逐部隔离）：属于「失败」，不能算未处理。
        for text in self.fill_errors:
            bad_lines.append("⚠️ %s —— ✘ 补齐过程中出错，该项未完成" % text)
        # 检测出了缺失、但根本没轮到它处理（「单次补齐上限」/ 时间预算）：既不是成功
        # 也不是失败，必须单列说明 —— 不能让它在三类里**凭空消失**。
        pending = [item["series"]["name"] for item in self.missing
                   if item["series"]["name"] not in self.fill_attempted]
        for name in pending:
            bad_lines.append("%s —— ✘ 本次未处理"
                             "（超出「单次补齐上限」或时间预算，下次运行会继续）" % name)
        if pending:
            extra_notes.append("有 %d 部剧本次未执行补齐（受「单次补齐上限」或时间预算限制）"
                               % len(pending))
        return missing_lines, ok_lines, bad_lines, extra_notes

    def _fill_heading(self):
        """② 的措辞要按**本次是否真的写了网盘**来定。

        「仅记录」与「预览模式」都没有真正写入网盘 —— 把它们说成「被成功补全」是假话，
        用户会以为媒体库里已经补好了。
        """
        if self.action == ACTION_RECORD:
            return "② 已找到资源、列出链接的剧集（仅记录，未写入网盘）"
        if self.dry_run:
            return "② 将要执行补齐动作的剧集（预览模式，未真正执行）"
        return "② 被成功补全的剧集"

    def _build_notify_text(self):
        """把三类结果拼成一条**纯文本**通知（微信的文本消息不解析 Markdown）。"""
        missing_lines, ok_lines, bad_lines, extra_notes = self._notify_items()
        total_lacks = sum(len(d.get("episodes") or [])
                          for item in self.missing for d in item["seasons"].values())
        lines = [
            "🎬 %s" % PLUGIN_NAME,
            "运行时间：%s ｜ 功能：%s"
            % (datetime.now().strftime("%Y-%m-%d %H:%M"), FUNC_LABELS.get(self.func, self.func)),
        ]
        if self.func == FUNC_FILL:
            lines.append("检测到 %d 部有缺集（合计 %d 集）｜ 本次已处理 %d 部"
                         % (len(self.missing), total_lacks, len(self.filled)))
        elif self.missing:
            lines.append("检测到 %d 部剧有缺集，合计 %d 集（仅检测，未执行补齐）"
                         % (len(self.missing), total_lacks))
        else:
            lines.append("本次未检测到缺集（仅检测，未执行补齐）")

        lines.extend(["", "① 缺失集的剧集（%d 部）" % len(missing_lines)])
        lines.extend(self._numbered(missing_lines))

        if ok_lines is None:
            lines.extend(["",
                          "② 被成功补全的剧集：本次为「%s」，没有执行补齐"
                          % FUNC_LABELS.get(self.func, self.func),
                          "",
                          "③ 补全失败：同上，本次没有执行补齐"])
        else:
            lines.extend(["", "%s（%d 部）" % (self._fill_heading(), len(ok_lines))])
            lines.extend(self._numbered(ok_lines))
            lines.extend(["", "③ 补全失败 / 未补全的剧集（%d 部）" % len(bad_lines)])
            lines.extend(self._numbered(bad_lines))

        if extra_notes:
            lines.append("")
            lines.extend("· " + note for note in extra_notes)
        lines.extend(["", "— 本消息由 ttd 插件「%s」自动发送" % PLUGIN_NAME])

        text = "\n".join(lines)
        if len(text) > NOTIFY_MAX_CHARS:
            # 宁可截断也不能超长：企业微信文本消息单条约 2048 字节，超了会被分段甚至拒收
            text = text[:NOTIFY_MAX_CHARS].rsplit("\n", 1)[0] + \
                "\n…（内容过长已截断，完整结果请在 ttd 插件结果页查看）"
        return text

    def _test_notify_text(self):
        return "\n".join([
            "🎬 %s" % PLUGIN_NAME,
            "这是一条测试通知：本插件的「运行结果通知」链路可用。",
            "运行时间：%s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "",
            "正式运行时会给出三类结果：",
            "① 缺失集的剧集",
            "② 被成功补全的剧集",
            "③ 补全失败 / 未补全的剧集（含只补全一部分的，会带【部分补全】标记）",
        ])

    def _send_notifications(self, text):
        """把文本发给用户勾选的渠道，返回 ``[(渠道名, 成功, 说明)]``。

        **每个渠道独立发送、独立报告**：一个失败不影响另一个 —— 否则「微信挂了」
        会连带把 Telegram 也吞掉，用户完全不知道消息到底有没有发出去。
        """
        results = []
        for channel in self.notify_channels:
            label = CHANNEL_LABELS.get(channel, channel)
            try:
                if channel == CH_TG:
                    ok, note = _TelegramChannel(self.log, self.ttd, self._ttd_proxy(),
                                                self.notify_bot).send(text)
                else:
                    ok, note = _WecomChannel(self.log, self.ttd, self.wecom_plugin_id,
                                             self.wecom_touser).send(text)
            except Exception as exc:
                # 单个渠道出意外**不能连累另一个**：否则「微信挂了」会把 Telegram 也
                # 标成失败，用户会以为两条都没发出去、白白重跑一轮。
                ok, note = False, "发送时异常：%s" % scrub_text(str(exc), [self.ttd.token])
            if ok:
                self.log.info("运行通知已通过「%s」发出：%s" % (label, note))
            else:
                self.log.warn("运行通知经「%s」发送失败：%s" % (label, note))
            results.append((label, ok, note))
        return results

    def _notify_after_run(self, result):
        """check / fill 跑完后推送三类结果，并把投递情况写进结果页。"""
        if self.notify_channels_raw:
            self.log.warn("「通知渠道」里有无法识别的取值：%s（可选：%s）"
                          % ("、".join(self.notify_channels_raw),
                             " / ".join(CHANNEL_LABELS[c] for c in VALID_CHANNELS)))
        if not self.notify_channels:
            return
        text = self._build_notify_text()
        self.log.info("发送运行结果通知（%d 字 → %s）"
                      % (len(text), "、".join(CHANNEL_LABELS[c] for c in self.notify_channels)))
        try:
            results = self._send_notifications(text)
        except Exception as exc:
            # 通知环节出意外**不能**把整轮结果搞没 —— 检测 / 补齐已经做完了，
            # 结果页必须照常返回（这也是它比通知更重要的原因）。
            self.log.warn("发送运行通知时出现异常（不影响本次结果）：%s" % exc)
            results = [(CHANNEL_LABELS.get(c, c), False, "发送时异常：%s" % exc)
                       for c in self.notify_channels]
        self._inject_notify(result, results)

    def _inject_notify(self, result, results):
        """把「通知投递结果」表插到结果页的「运行日志」之前，并刷新日志窗口。"""
        try:
            components = result.get("ui", {}).get("components")
            if not isinstance(components, list):
                return
            block = [
                {"type": "divider"},
                {"type": "heading", "text": "运行通知"},
                {"type": "table", "label": "通知投递结果", "headers": ["渠道", "结果", "说明"],
                 "rows": [[label, "✔ 已发送" if ok else "✘ 失败", note]
                          for label, ok, note in results]},
            ]
            index = None
            for position, comp in enumerate(components):
                if (isinstance(comp, dict) and comp.get("type") == "heading"
                        and str(comp.get("text") or "").strip() == "运行日志"):
                    index = position
                    break
            if index is None:
                components.extend(block)
            else:
                components[index:index] = block
            # 发送通知也会写日志 —— 结果页的日志窗口要重新取一次，
            # 否则用户看不到「用了哪个机器人 / 失败原因」。
            # 只刷新「运行日志」标题**之后**的那个 code 组件：盲目刷新第一个 code
            # 会把页面里别的代码块一起改掉。
            for position in range((index + 1) if index is not None else 0, len(components)):
                comp = components[position]
                if isinstance(comp, dict) and comp.get("type") == "code" \
                        and isinstance(comp.get("text"), str):
                    comp["text"] = self.log.text()
                    break
            result["notify_total"] = len(results)
            result["notify_failed"] = sum(1 for _label, ok, _note in results if not ok)
        except Exception as exc:
            self.log.warn("把通知结果写入结果页时出错（不影响本次结果）：%s" % exc)

    def do_config(self):
        # TMDB 直连要读 TgtoDrive 的网络代理来解析代理候选，这里先解析一次，
        # 好让下面「数据源 / 代理」两行显示的是**真正会用的**东西。
        if self.ttd.configured or self.tmdb.configured:
            self._ensure_tmdb()
        rows = [
            ["执行功能", FUNC_LABELS.get(self.func, self.func)],
            ["TgtoDrive", self.ttd.describe()],
            ["Emby", "%s（来源：%s）" % (self.emby.describe(), self.emby_source_note or "未确认")],
            ["TMDB 数据源", self._tmdb_source_note()],
            ["TMDB 直连设置", "%s｜语言 %s｜代理策略：%s"
             % (self.tmdb.describe(), self.tmdb.language,
                TMDB_PROXY_LABELS.get(self.tmdb_proxy_mode, self.tmdb_proxy_mode))],
            ["TMDB 手动代理", str(self.p.get("tmdb_proxy") or "").strip()
             or "（未填：按上面的代理策略自动挑）"],
            ["媒体库范围", "、".join(self.library_ids) if self.library_ids else "全部媒体库"],
            ["单次检测上限", "%d 部（%s）" % (self.max_series,
             "整库超过它时按轮转分段扫描" if self.max_series else "不限")],
            ["单次时间预算", "检测 %d 秒 / 整轮 %d 秒（到点保存进度并收工，避免撞上插件超时）"
             % (DETECT_TIME_BUDGET, TOTAL_TIME_BUDGET)],
            ["扫描进度（游标）", "记录在 data_dir/%s；整库大于单次上限时，下次从第 %d 部起轮转"
             % (CURSOR_FILE, self._read_cursor_raw() + 1)],
            ["只统计已播出", "是" if self.only_aired else "否（含未开播，可能误判缺失）"],
            ["只检查已有季", "是" if self.only_season_exist else "否"],
            ["包含特别季 S00", "是" if self.include_s00 else "否"],
            ["忽略关键词", "、".join(self.ignore_words) if self.ignore_words else "（无）"],
            ["搜索源", SOURCE_LABELS.get(self.source, self.source)],
            ["资源来源（TgtoDrive）", "、".join(self.resource_sources) if self.resource_sources
             else "（留空：由 TgtoDrive 决定）"],
            ["TgtoDrive 可用来源", ("、".join("%s=%s" % (o["label"], o["slug"])
                                          for o in self.ttd_source_options[:20])
                                 + ("…（共 %d 个）" % len(self.ttd_source_options)
                                    if len(self.ttd_source_options) > 20 else ""))
             or "（未读到）"],
            ["RE0 状态（TgtoDrive）", {True: "可用：" + self.re0_note,
                                      False: "不可用：" + self.re0_note,
                                      None: "未判定：" + (self.re0_note or "未读取")}[self.re0_available]],
            ["资源能力（TgtoDrive）", self.capability_note or "（未读取）"],
            ["盘搜地址", self.pansou.describe()],
            ["盘搜网盘类型", "、".join(self.cloud_types) if self.cloud_types else "（不限）"],
            ["补齐动作", ACTION_LABELS.get(self.action, self.action)],
            ["预览模式", "开（不会真正写入）" if self.dry_run else "关（会真实执行）"],
            ["单次补齐上限", "%d 部" % self.max_fill if self.max_fill else "不限制"],
            ["离线目标网盘（provider）", ("%s（来自插件表单）" % self.target_dir) if self.target_dir
             else ("%s（来自 TgtoDrive 的 target_provider）" % self.ttd_target_provider
                   if self.ttd_target_provider else "（未配置，由 TgtoDrive 用默认值）")
             + "｜仅用于「提交离线下载」；转存目标由 TgtoDrive 影视设置决定"],
            ["转存目录（仅展示）", self.ttd_transfer_targets or "（TgtoDrive 未配置）"],
        ]
        return self._result(
            ok=True, title="生效配置", tone="default",
            alert="下面是本次运行**实际生效**的配置（凭据已脱敏）。"
                  "填了表单就以表单为准；连接类字段留空时会尝试复用 TgtoDrive 的对应设置。",
            stats=[("执行功能", FUNC_LABELS.get(self.func, self.func)),
                   ("补齐动作", "未涉及" if self.func != FUNC_FILL
                    else ACTION_LABELS.get(self.action, self.action)),
                   ("预览模式", "开" if self.dry_run else "关"),
                   ("搜索源", SOURCE_LABELS.get(self.source, self.source))],
            rows=rows, rows_label="生效配置明细",
            headers=["配置项", "生效值"])

    # -- 结果装配 ----------------------------------------------------------

    def _stat_cards(self, stats):
        children = []
        for label, value in stats:
            children.append({"type": "card", "label": str(label),
                             "children": [{"type": "heading", "text": str(value)}]})
        if not children:
            return None
        return {"type": "grid", "columns": min(max(len(children), 1), 4), "children": children}

    def _result(self, ok, title, alert, tone, stats, rows, notes=None,
                rows_label="明细", headers=None, extra_components=None,
                extra_tables=None):
        components = [
            {"type": "heading", "text": "🎬 %s · %s" % (PLUGIN_NAME, title)},
            {"type": "alert", "text": alert, "style": {"tone": tone}},
        ]
        cards = self._stat_cards(stats)
        if cards:
            components.append(cards)
        for note in (notes or []):
            components.append({"type": "alert", "text": note, "style": {"tone": "warning"}})
        components.append({"type": "divider"})
        # 表头必须由调用方显式给出：此前按「第一行的列数」截取预设表头，
        # 结果 5 列的缺失表第 5 列被错标成「搜索关键词」（实际是跳过原因），
        # 2 列的配置表更会显示出 5 个列名 —— 表头与数据对不上。
        table_headers = headers or ["项目", "值"]
        width = len(table_headers)
        trimmed = []
        components.append({"type": "table", "label": rows_label,
                           "headers": table_headers,
                           "rows": self._cap_rows(rows, width, rows_label, trimmed)})
        for extra in (extra_tables or []):
            if extra.get("type") == "table":
                extra = dict(extra)
                extra["rows"] = self._cap_rows(extra.get("rows") or [],
                                               len(extra.get("headers") or []) or 1,
                                               str(extra.get("label") or "表格"), trimmed)
            components.append(extra)
        if trimmed:
            components.append({
                "type": "text",
                "text": "为遵守平台对表格的限制（**最多 200 行**），以上表格各截取了前 200 行：%s。"
                        "完整清单见下方运行日志，或从返回值的 `missing_total` / `filled_total` 核对数量。"
                        % "；".join(trimmed),
                "style": {"tone": "muted"},
            })
        for extra in (extra_components or []):
            components.append(extra)
        components.append({"type": "divider"})
        components.append({"type": "heading", "text": "运行日志"})
        components.append({"type": "code", "text": self.log.text()})
        return {
            "status": "ok" if ok else "failed",
            "func": self.func,
            "missing_total": len(self.missing),
            "filled_total": len(self.filled),
            "dry_run": self.dry_run,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    @staticmethod
    def _cap_rows(rows, width, label, trimmed):
        """把表格行数压到平台上限内（≤200 行），并记录被截断的表格。

        平台的 `table` 组件限制是 **≤30 列 200 行** —— 媒体库稍大（50 部剧 × 多季）
        缺失明细就会超过 200 行，超出会被拒绝渲染、整页都看不到。

        空表补一行「（无）」占位，让「没有内容」和「没渲染出来」可区分。
        """
        if not rows:
            return [["（无）"] + ["-"] * max(width - 1, 0)]
        if len(rows) <= MAX_TABLE_ROWS:
            return rows
        trimmed.append("%s %d 行 → 显示前 %d 行" % (label, len(rows), MAX_TABLE_ROWS))
        return rows[:MAX_TABLE_ROWS]


# ---------------------------------------------------------------------------
# 响应解析（全部容错：字段名不保证，解析不到就返回空并让调用方记日志）
# ---------------------------------------------------------------------------

def _describe_shape(payload, max_depth=2, max_keys=40, max_parts=10):
    """把（无 schema 的）响应**结构**描述成一行日志：每一层容器的键名。

    为什么不用「截取响应前 N 字」：实测 TTD 的详情响应里键名是**按字母序**排的
    （backdrop_url … number_of_seasons … origin_country … overview … ，
    `seasons` 恰好落在第 400 字之后）—— 截断日志把最关键的字段名切掉了，
    排查时只能看到一堆图片链接和分类。**键名列表体积小、信息量却正好是我们要的。**

    例：``根{data,success} ｜ 根.data{backdrop_url,entity_key,…,number_of_seasons,…}``
    """
    parts = []

    def walk(node, path, depth):
        if len(parts) >= max_parts or depth > max_depth:
            return
        if isinstance(node, dict):
            keys = sorted(str(k) for k in node.keys())
            shown = keys[:max_keys]
            parts.append("%s{%s%s}" % (path or "根", "、".join(shown),
                                       "…共%d个键" % len(keys) if len(keys) > max_keys else ""))
            if depth == max_depth:
                return
            for key in keys[:max_keys]:
                value = node.get(key)
                if isinstance(value, (dict, list)):
                    walk(value, "%s.%s" % (path, key), depth + 1)
                    if len(parts) >= max_parts:
                        return
        elif isinstance(node, list) and node:
            walk(node[0], "%s[0]" % path, depth + 1)

    walk(payload, "", 0)
    return " ｜ ".join(parts)[:1200] or "（空响应）"


# 季号字段的候选键名（TTD 的详情是**自己规范化过的实体**，键名与原始 TMDB 未必一致）
SEASON_NUMBER_KEYS = ("season_number", "seasonNumber", "season_no", "seasonNo",
                      "season", "number", "index")


def _season_number_of(item):
    """从「季」条目里取出季号；取不到时尝试从 `name`（如「第 2 季」/「Season 2」）里折出来。"""
    if isinstance(item, (int, float)):
        return _finite_int(item)
    if not isinstance(item, dict):
        return None
    for key in SEASON_NUMBER_KEYS:
        number = _finite_int(item.get(key))
        if number is not None:
            return number
    name = str(item.get("name") or item.get("title") or "")
    if name:
        if _SEASON_SPECIAL_RE.search(name):
            return 0
        match = _SEASON_EN_RE.search(name) or _SEASON_CN_RE.search(name)
        if match:
            return _finite_int(match.group(1))
    return None


def _extract_tmdb_seasons(payload):
    """从（无 schema 的）剧集详情里取出**季号集合**。

    三条路，按可靠性排序：

    ① 主路径：任何一层里的 `seasons` 列表 —— 逐项按 :data:`SEASON_NUMBER_KEYS` 取季号；
    ② 兜底：`number_of_seasons`（TMDB 语义：**不含特别篇**）→ 合成 ``1..N``。
       ⚠️ 实测 TTD 的详情响应就是这个形态：有 `number_of_seasons` 计数、**没有 `seasons` 数组**，
       只认 `seasons` 会**整库全军覆没**（每一部剧都报「没有解析到季列表」）。
    ③ 全量扫 `season_number`（兜底），但**跳过「单集」形态的节点** —— 详情里的
       `last_episode_to_air` / `next_episode_to_air` 都带 `season_number`，
       不排除会把「下一季（尚未播出）」也当成已存在的季，白发请求甚至产出幽灵季。
    """
    seasons = set()
    for node in _walk_dicts(payload):
        value = node.get("seasons")
        if isinstance(value, list):
            for item in value:
                number = _season_number_of(item)
                if number is not None:
                    seasons.add(number)
    # ② number_of_seasons 兜底
    if not seasons:
        count = _extract_season_count(payload)
        if count:
            seasons.update(range(1, count + 1))
    # ③ 全量扫 season_number（跳过单集节点）
    if not seasons:
        for node in _walk_dicts(payload):
            if node.get("episode_number") is not None or node.get("episodeNumber") is not None:
                continue        # 单集节点，跳过
            number = _season_number_of({"season_number": node.get("season_number"),
                                        "seasonNumber": node.get("seasonNumber")})
            if number is not None and number > 0:
                seasons.add(number)
    return seasons


def _extract_season_count(payload):
    """取「共有多少季」（不含特别篇）。认不出返回 0。"""
    for node in _walk_dicts(payload):
        for key in ("number_of_seasons", "numberOfSeasons", "seasons_count",
                    "seasonsCount", "total_seasons"):
            count = _finite_int(node.get(key))
            if count and count > 0:
                return count
    return 0


def _extract_tmdb_status(payload):
    for node in _walk_dicts(payload):
        value = node.get("status")
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def _extract_tmdb_episodes(payload):
    """从 TMDB 季详情里取 ``({集号, …}, {集号: 播出日期})``。"""
    numbers, air_dates = set(), {}
    for node in _walk_dicts(payload):
        value = node.get("episodes")
        if not isinstance(value, list):
            continue
        for item in value:
            if not isinstance(item, dict):
                continue
            number = item.get("episode_number", item.get("episodeNumber"))
            try:
                number = int(number)
            except (TypeError, ValueError):
                continue
            numbers.add(number)
            air = item.get("air_date", item.get("airDate"))
            if isinstance(air, str) and air.strip() and air.strip().lower() != "null":
                air_dates[number] = air.strip()
    return numbers, air_dates


# 明显是图片 / 封面的 URL 特征：资源链接不应该是这些。
# 无 schema 的响应里 `url` 常常是封面图、`share_url` 才是分享链接 ——
# 取错了会把图片链接当成资源，后面 transfer / offline 就发错了。
IMAGE_URL_HINTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp", ".svg",
                   "image", "poster", "cover", "thumb", "avatar", "logo")


def _looks_like_image_url(url):
    low = str(url or "").lower()
    return any(hint in low for hint in IMAGE_URL_HINTS)


def _extract_builtin_resources(payload):
    """把 TgtoDrive 内置资源检索的响应整理成候选列表（结构未公开，尽力而为）。

    识别策略与两处设防：

    * **键名优先级**：先看 `share_url` / `shareUrl` / `share_link` 这类明确的分享链接键，
      再看 `url` / `link` / `href` / `magnet`；
    * **排除图片链接**：命中 :data:`IMAGE_URL_HINTS` 的（封面 / 海报 / 缩略图）一律跳过，
      并在没有别的链接时放弃该条目 —— 宁可少认，也不把图片当成资源；
    * **来源与网盘类型分开**：`type` 只取网盘类键（type / cloud_type / provider），
      来源（source / site / channel）单独放在 `source` 字段，避免把来源标识当成网盘类型。

    识别不到的条目会被忽略，但调用方已把原始响应写入日志，便于后续精确对接。
    """
    # 分享链接键优先于泛化的 url
    url_keys = ("share_url", "shareUrl", "share_link", "shareLink",
                "url", "link", "href", "magnet")
    type_keys = ("type", "cloud_type", "cloudType", "provider", "netdisk")
    source_keys = ("source", "site", "channel", "from", "provider_name")
    note_keys = ("note", "title", "name", "work_title", "description", "label")

    def first_text(node, keys, want_url=False):
        for key in keys:
            value = node.get(key)
            if not isinstance(value, str) or not value.strip():
                continue
            text = value.strip()
            if want_url and not text.startswith(("http://", "https://", "magnet:", "ed2k:")):
                continue
            if want_url and _looks_like_image_url(text):
                continue
            return text
        return ""

    out, seen = [], set()
    for node in _walk_dicts(payload):
        url = first_text(node, url_keys, want_url=True)
        if not url or url in seen:
            continue     # 没有可用链接，或只有图片链接 —— 跳过（调用方已记录原始响应）
        seen.add(url)
        out.append({
            "type": ("magnet" if url.startswith("magnet:") else
                     ("ed2k" if url.startswith("ed2k:") else
                      (first_text(node, type_keys) or "").lower())),
            "url": url,
            "password": str(node.get("password") or node.get("pwd") or "").strip(),
            "note": first_text(node, note_keys),
            "source": first_text(node, source_keys) or "builtin",
            "datetime": str(node.get("datetime") or node.get("pub_date") or "").strip(),
        })
    return out


# 支持的日期格式 → 该格式对应的字符串长度（显式写出来，不用「len(fmt)+2」这种
# 隐含推导：加一个 `%Y.%m.%d` 之类的格式时，那个魔法数字会悄悄算错长度）。
DATE_FORMATS = (
    ("%Y-%m-%d", 10),
    ("%Y/%m/%d", 10),
    ("%Y-%m-%dT%H:%M:%S", 19),
)


def _parse_date(text):
    """把 ``YYYY-MM-DD`` / ``YYYY/MM/DD`` / ``YYYY-MM-DDTHH:MM:SS`` 解析成 ``date``；认不出返回 None。

    先走「定长直切」快路径：TMDB 的 ``air_date`` 绝大多数就是 ``YYYY-MM-DD``，
    切片 + ``date()`` 构造比 ``strptime`` 快约 **10 倍**（实测 3.3µs → 0.33µs），
    而**一季的每一集都要调用一次** —— 大库扫描时这个差别会放大到几十万次。
    ``strptime`` 与正则仍作为兜底保留，输入输出语义与原实现完全一致。
    """
    text = str(text or "").strip()
    if not text:
        return None
    head = text[:10]
    if len(head) == 10 and head[4] == "-" and head[7] == "-":
        # 形如 2024-01-05 —— 顺带覆盖 2024-01-05T10:00:00 / "2024-01-05 10:00" 这类带时间后缀的
        try:
            return date(int(head[:4]), int(head[5:7]), int(head[8:10]))
        except ValueError:
            pass          # 形似但非法（如 2024-13-45），交给下面按原逻辑继续尝试
    for fmt, length in DATE_FORMATS:
        try:
            return datetime.strptime(text[:length], fmt).date()
        except ValueError:
            continue
    match = _DATE_PREFIX_RE.match(text)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            return None
    return None


def _parse_datetime(text):
    """把候选的时间字段折成可比较的整数（YYYYMMDD）；认不出返回 0。

    用于「选新不选旧」—— 资源越旧越可能失效。
    """
    day = _parse_date(text)
    return day.year * 10000 + day.month * 100 + day.day if day else 0


def _join_nums(numbers, limit=12):
    """把集号列表渲染成 ``E01-E03、E07`` 这样的紧凑写法。"""
    nums = sorted({int(n) for n in numbers if isinstance(n, (int, float)) or str(n).isdigit()})
    if not nums:
        return ""
    parts, start, prev = [], nums[0], nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        parts.append("E%02d" % start if start == prev else "E%02d-E%02d" % (start, prev))
        start = prev = n
    parts.append("E%02d" % start if start == prev else "E%02d-E%02d" % (start, prev))
    text = "、".join(parts[:limit])
    if len(parts) > limit:
        text += "…（共 %d 集）" % len(nums)
    return text


def run(params, context):
    """TgtoDrive 插件入口：同步执行一次检测 / 补齐 / 测试。"""
    return _Runner(params, context).execute()
