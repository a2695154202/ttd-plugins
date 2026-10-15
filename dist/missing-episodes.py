# -*- coding: utf-8 -*-
# 由 scripts/package_plugin.py 依据 plugins/missing-episodes/ 自动生成，请勿直接编辑。
# 单文件插件：顶层唯一的 PLUGIN_MANIFEST 常量字典 + 入口源码。

PLUGIN_MANIFEST = {
  'schema_version': 1,
  'id': 'missing-episodes',
  'name': '剧集缺集检测与补齐',
  'version': '1.0.0',
  'description': '读取媒体库里已有哪些剧集，与 TMDB 上「应该有」的季集求差集，找出缺集；再按你配置的搜索源去找缺失资源并按选定动作补齐。本地季集走 Emby 直连读取（TgtoDrive 的接口没有提供「某剧本地集号清单」，只有电影/剧集/单集的总量统计），应有季集走 TgtoDrive 的 TMDB 代理，因此不需要另外准备 TMDB 的 API Key。搜索源可选 TgtoDrive 内置资源检索、你自建的盘搜（PanSou）或两者都查；补齐动作可选「仅记录并列出链接」「转存到网盘」「提交磁力/电驴离线下载」，默认最保守的「仅记录」，并且默认开启预览模式——只打印将要执行的操作，不会真正写网盘。附带「测试连接」按钮，可一键检查 TgtoDrive、Emby、TMDB 代理与盘搜四项连通性。内置「仅检测缺失」只读模式，适合先看清缺口再决定是否补齐。',
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
      ],
      'help': '决定本次要做什么。右侧按钮会**覆盖**这里的取值：点「检查缺失」就是 check，点「测试连接」就是 test。\n\n建议顺序：先点「测试连接」确认四个数据源都通 → 再点「检查缺失（只读）」看清缺口 → 最后把「执行功能」切到「检测并补齐」（或直接用第三个按钮）执行补齐。\n\n从其他插件/接口调用本插件时，用这个字段指定动作。',
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
      'help': '每次运行最多检测多少部剧，防止媒体库很大时超时（插件超时 1800 秒）。检测按剧名排序，从前往后取。\n\n想全量检测就把它调大；配合定时执行分批跑也可以。',
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
          'label': '提交离线下载（磁力 / 电驴）',
          'value': 'offline',
        },
      ],
      'help': '找到缺失资源后做什么：\n\n• **仅记录并列出链接**：只把候选链接与提取码写进结果页和日志，你自己决定后续（默认，最安全）；\n• **转存到网盘**：调 TgtoDrive 的转存接口把分享链接存进你的网盘 —— **会真实写网盘、可能消耗会员点数**；\n• **提交离线下载**：只对磁力 / 电驴候选有效，调离线下载接口创建任务。\n\n后两种属于破坏性操作，请先用预览模式确认。',
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
      'help': '限定盘搜返回哪些网盘类型，留空表示不限。可用值：\n`baidu` `aliyun` `quark` `guangya` `tianyi` `uc` `mobile` `115` `pikpak` `xunlei` `123` `magnet` `ed2k`。\n\n挑选候选时：磁力 / 电驴适合「提交离线下载」，网盘类型适合「转存」。',
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
      'placeholder': '留空 = 直接用 TgtoDrive 已配置的转存目标网盘',
      'help': '补齐动作要用的**目标网盘标识**（即接口里的 `provider`）。**留空时会自动使用 TgtoDrive 影视设置里的 `target_provider`**，`max_points`（点数上限）也一并复用 —— 这些你已经在 TgtoDrive 里配过了，不需要在这里重填。\n\n⚠️ 这里填的是**网盘标识**（由 TgtoDrive 的转存目标决定），不是目录路径。TgtoDrive 的转存目录（`media_transfer_targets`）由它自己应用，本插件只在「查看生效配置」里展示、不会把它当网盘标识发出去。\n\n只有想**临时覆盖**时才需要填写。点「测试连接」可以看到 TgtoDrive 当前的转存目标与点数上限。',
    },
  ],
  'ui': {
    'width': 'wide',
    'layout': 'stack',
    'components': [
      {
        'type': 'heading',
        'text': '🎬 剧集缺集检测与补齐',
      },
      {
        'type': 'markdown',
        'text': '把「本地已有哪些集」与「TMDB 应该有哪`些集」求差集，找出缺集；按你配置的搜索源找缺失资源，并按选定动作补齐。\n\n**建议第一次这样用**：① 点「测试连接」确认各项都通（尤其 **TMDB 季集详情（关键）** 这一项，它不通就没法确定「应该有哪些集」）→ ② 点「检查缺失（只读）」看清缺口 → ③ 确认无误后再执行补齐（默认**预览模式**，只打印将要做什么）。',
      },
      {
        'type': 'alert',
        'text': '两个前提：① 需要 **TgtoDrive 的 OpenAPI 令牌**（读 TMDB 详情与资源检索）；② 需要 **Emby 直连信息**（地址 + API Key）—— TgtoDrive 的接口没有「某剧本地集号清单」，所以本地季集只能直连 Emby 读取。Emby 两项留空时，插件会尝试复用 TgtoDrive 影视设置里已配置的 Emby。',
        'style': {
          'tone': 'warning',
        },
      },
      {
        'type': 'text',
        'text': '**结果有三种，别把第三种当成第二种**：「有缺失」＝比出了具体缺集；「无缺失」＝每个季都比对成功且集号齐全；**「⚠️ 无法判定」＝某些季的「应有集数」没读成**（既不算缺失、也不算完整）。遇到「无法判定」请先点「测试连接」看 **TMDB 季集详情（关键）** 的结论 —— 规范说明该接口「只有当前详情配置支持完整季集模式时可用」。',
        'style': {
          'tone': 'muted',
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
                    'label': '连接设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '**TgtoDrive** 与 **Emby** 两处连接。Emby 必须能直连（同容器可用局域网地址），否则读不到本地季集。',
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
                    'label': '检测范围',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '控制检测哪些剧、哪些集算「应该有」。默认设置已按参考插件的最佳实践调好，**不建议改动**「只统计已播出的集」。',
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
                    'label': '补齐设置',
                    'children': [
                      {
                        'type': 'markdown',
                        'text': '去哪里找资源、找到后做什么。\n\n**这里的参数大多直接从 TgtoDrive 读，不需要重填**：转存目标网盘 / 点数上限取自 TgtoDrive 的影视设置；**RE0** 是 TgtoDrive 集成的服务，用它只要在 TgtoDrive 里授权过即可（本插件只读它的授权状态）；可限定的「资源来源」清单也由 TgtoDrive 提供。\n\n转存与离线下载会**真实写网盘**，所以默认「仅记录」+ **预览模式开启**。',
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
                'label': '测试连接',
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
                'label': '检查缺失（只读）',
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
                'label': '检测并补齐',
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
            ],
          },
        ],
      },
      {
        'type': 'divider',
      },
      {
        'type': 'text',
        'text': '「仅检测缺失」是纯只读操作：不写网盘、不改媒体库、不动 TgtoDrive 的任何设置。补齐动作默认走预览，只有你显式关掉「预览模式」才会真正执行。',
        'style': {
          'tone': 'muted',
        },
      },
      {
        'type': 'text',
        'text': '定时执行：在「我的插件 → 定时执行」新建计划，选本插件、运行参数填 func=check（或 fill），建议先用 check 观察一段时间，稳定后再切 fill。',
        'style': {
          'tone': 'muted',
        },
      },
    ],
  },
}


# -*- coding: utf-8 -*-
"""剧集缺集检测与补齐 · TgtoDrive 插件

**做什么**：读取「本地媒体库里已有哪些剧集」与「按 TMDB 应该有哪`些剧集」，求差集得到缺集；
然后按用户配置的搜索源去找缺失资源，并按选定动作补齐。

三个数据源，缺一不可：

1. **本地已有季集** —— 走 **Emby 直连**。
   ⚠️ 为什么必须直连：TgtoDrive 的 OpenAPI **没有**「取某部剧的本地集号清单」的接口
   （`/api/emby/*` 全是看板/代理/封面类；`/api/emby/dashboard` 只给电影/剧集/单集**总量**，
   `/api/emby/latest` 只给最近入库）。MoviePilot 的同名插件靠 `MediaServerChain.episodes()`，
   在 TTD 里对应不到任何公开接口，因此本插件让用户填 Emby 地址 + API Key 直连读取。
2. **应有季集** —— 走 TgtoDrive 的 TMDB 代理（`/api/media/details/...`），
   这样用户不必再单独准备 TMDB 的 API Key。
3. **缺失资源的搜索源** —— 可选 TgtoDrive 内置资源检索（`/api/media/resources/search`），
   或用户自建的**盘搜（PanSou）**实例（默认端口 8888），或两者都查。

**补齐动作**（默认最保守）：
`record` 仅记录并列出链接 → `transfer` 转存到网盘 → `offline` 提交磁力/电驴离线下载。
默认 **dry_run=True**：只打印「将要做什么」，不真正执行；转存/离线会真实写网盘、
消耗网盘额度，务必先跑 dry-run 确认。

实现上遵循本仓库既有约定：模块导入阶段不发网络请求、每次请求都设超时、
凭据一律脱敏、任务结果逐层下沉后再判读（任务查询接口无响应 schema）。
"""

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, date
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

PLUGIN_NAME = "剧集缺集检测与补齐"
PLUGIN_ID = "missing-episodes"

DEFAULT_BASE_URL = "http://127.0.0.1:12366"
DEFAULT_PANSOU_URL = "http://127.0.0.1:8888"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 60          # TMDB / 盘搜 / 网盘转存都可能偏慢
JOB_POLL_ATTEMPTS = 8
JOB_POLL_INTERVAL = 3

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

# 平台 `table` 组件的行数上限（协议清单：≤30 列 200 行）。超出会被拒绝渲染，
# 导致整个结果页看不到 —— 必须自己截断并说明。
MAX_TABLE_ROWS = 200

# 执行功能
FUNC_CHECK = "check"
FUNC_FILL = "fill"
FUNC_TEST = "test"
FUNC_CONFIG = "config"
VALID_FUNCS = (FUNC_CHECK, FUNC_FILL, FUNC_TEST, FUNC_CONFIG)
FUNC_LABELS = {
    FUNC_CHECK: "仅检测缺失（只读）",
    FUNC_FILL: "检测并补齐",
    FUNC_TEST: "测试连接",
    FUNC_CONFIG: "查看生效配置",
}

# 补齐动作
ACTION_RECORD = "record"
ACTION_TRANSFER = "transfer"
ACTION_OFFLINE = "offline"
VALID_ACTIONS = (ACTION_RECORD, ACTION_TRANSFER, ACTION_OFFLINE)
ACTION_LABELS = {
    ACTION_RECORD: "仅记录并列出链接",
    ACTION_TRANSFER: "转存到网盘",
    ACTION_OFFLINE: "提交离线下载（磁力 / 电驴）",
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
    "ed2k": "电驴", "others": "其他",
}
# 可直接丢给「离线下载」的链接类型
OFFLINE_TYPES = ("magnet", "ed2k")

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
# 基础工具
# ---------------------------------------------------------------------------

class _Logger(object):
    """同时写入标准输出（TgtoDrive 运行日志）与内存缓冲区（结果页日志窗口）。"""

    MAX_LINES = 2000

    def __init__(self):
        self.lines = []

    def _emit(self, level, message):
        line = "[%s] [%s] %s" % (datetime.now().strftime("%H:%M:%S"), level, message)
        self.lines.append(line)
        # 超过上限时**丢最旧的**，保留最新 —— 否则长任务（几百部剧）会把最后的
        # 汇总与错误信息挤掉，结果页只看到开头的正常行、以为一切顺利。
        if len(self.lines) > self.MAX_LINES:
            del self.lines[:len(self.lines) - self.MAX_LINES]
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


def _as_int(value, default=0):
    try:
        if value in (None, ""):
            return default
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return default


def _is_secret_key(key):
    """键名含凭据特征片段即视为敏感（归一化后比较，比枚举更抗新增字段）。"""
    norm = re.sub(r"[^a-z0-9]", "", str(key or "").lower())
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


def _mask_params(params, max_len=600):
    """把参数渲染成可安全写进日志的一行（敏感键只回显长度）。"""
    if not isinstance(params, dict) or not params:
        return "（空）"
    parts = []
    for key, value in params.items():
        if _is_secret_key(key):
            text = "***（已填写，长度 %d）" % len(str(value)) if value else "（空）"
        else:
            text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
            text = str(text).replace("\n", "\\n")
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


_URLLIB_OPENER = urllib.request.build_opener(_NoRedirect)


def _http_json(method, url, headers=None, body=None, timeout=None):
    """发 JSON 请求，返回 ``(status, text, data)``；网络异常时 status 为 None。"""
    headers = dict(headers or {})
    timeout = timeout or (CONNECT_TIMEOUT, READ_TIMEOUT)
    if requests is not None:
        try:
            response = requests.request(method, url, headers=headers, json=body,
                                        timeout=timeout, allow_redirects=False)
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
        with _URLLIB_OPENER.open(request, timeout=READ_TIMEOUT) as response:
            text = response.read().decode("utf-8", "replace")
            return response.status, text, _safe_json(text)
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        return exc.code, text, _safe_json(text)
    except Exception as exc:
        return None, "%s: %s" % (type(exc).__name__, exc), None


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
    return [x.strip() for x in re.split(r"[,\uFF0C|;；\s]+", str(text or "")) if x.strip()]


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
    t = re.sub(r"(?i)\bS\d{1,2}(E\d{1,3})?\b", " ", t)
    t = re.sub(r"(?i)\b(season|seasons)\s*\d+", " ", t)
    t = re.sub(r"第\s*[0-9一二三四五六七八九十]+\s*[季部]", " ", t)
    t = re.sub(r"\[[^\]]*\]", " ", t)
    t = re.sub(r"[（(][^）)]*[）)]", " ", t)
    t = t.replace(".", " ").replace("_", " ")
    t = re.sub(r"\s+", " ", t).strip(" -·")
    return t


def _is_relevant(candidate, title):
    """粗筛：候选标题里既不含剧名关键词就丢掉（**只用于盘搜结果**）。

    盘搜是聚合搜索，常返回大量同名 / 蹭名的其它资源，需要按剧名粗筛；
    而 TgtoDrive 内置检索是**按 title 精确查询**的，其结果不该再被标题关键词二次筛掉 ——
    它的 `note` 可能只是「更新至第 10 集」这类不含剧名的文本，此前两路结果统一过滤，
    会把正确的内置候选误杀。判定不出关键词时（剧名全是符号等）不做过滤，避免误杀。
    """
    key_tokens = [tok for tok in re.split(r"\s+", str(title or "").lower()) if len(tok) >= 2]
    note = str((candidate or {}).get("note") or "").lower()
    if not note or not key_tokens:
        return True
    return any(tok in note for tok in key_tokens)


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
        return bool(self.token) and bool(re.match(r"^https?://", self.base_url, re.I))

    def describe(self):
        return "%s｜令牌 %s" % (self.base_url, _mask(self.token))

    def _headers(self):
        return {"Authorization": "Bearer %s" % self.token} if self.token else {}

    def request(self, method, path, body=None, params=None):
        url = self.base_url + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
        status, text, data = _http_json(method, url, headers=self._headers(), body=body,
                                        timeout=self.timeout)
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
        url = self.base_url + path
        if params:
            url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
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
        data = self.get_json("/Shows/%s/Episodes"
                             % urllib.parse.quote(str(series_id)),
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
        return bool(re.match(r"^https?://", self.base_url, re.I))

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
    try:
        if value in (None, ""):
            return None
        return int(float(str(value).strip()))
    except (TypeError, ValueError):
        return None


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

        self.ttd = _TtdClient(base, token, self.log)
        self.emby = _EmbyClient(self.p.get("emby_url"), self.p.get("emby_api_key"), self.log)
        self.pansou = _PansouClient(self.p.get("pansou_url"), self.p.get("pansou_token"),
                                    self.log)

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
        self._ensure_emby()
        self._load_ttd_config()

        if self.func == FUNC_TEST:
            return self.do_test()
        if self.func == FUNC_CONFIG:
            return self.do_config()
        result = self.do_check()
        if self.func == FUNC_FILL:
            result = self.do_fill(result)
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
        """补齐时传给 TgtoDrive 的「目标网盘」：表单优先，其次 TgtoDrive 已配的 `target_provider`。

        ⚠️ **不要把 `media_transfer_targets`（转存目录）也当兜底值**：它是一份路径，
        而转存 / 离线接口的 `provider` 要的是网盘标识。此前两条一起兜底，一旦用户只配了
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

    # -- 测试连接 ----------------------------------------------------------

    def do_test(self):
        rows = []

        # 1) TgtoDrive
        if not self.ttd.configured:
            rows.append(["TgtoDrive", "✘", "未配置地址或 OpenAPI 令牌"])
        else:
            try:
                data = self.ttd.media_settings()
                keys = sorted(data.keys())[:8] if isinstance(data, dict) else []
                rows.append(["TgtoDrive", "✔",
                             "已连通；/api/media/settings 返回 %d 个顶层键%s"
                             % (len(keys or []), ("：" + "、".join(keys)) if keys else "")])
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

        # 3) TMDB（经 TgtoDrive）
        if self.ttd.configured:
            try:
                probe = self._tmdb_probe()
                rows.append(["TMDB（经 TgtoDrive）", "✔" if probe else "⚠",
                             probe or "接口可用，但没有返回可解析的季列表（可能该剧 ID 无数据）"])
            except Exception as exc:
                rows.append(["TMDB（经 TgtoDrive）", "✘", str(exc)[:160]])
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
                data = self.ttd.get_json("/api/media/details/tmdb/tv/%s" % probe_id)
            except Exception as exc:
                last_error = str(exc)[:140]
                continue
            seasons = _extract_tmdb_seasons(data)
            if seasons:
                return ("TMDB 代理可用；探活剧集返回 %d 个季（%s）"
                        % (len(seasons), "、".join("S%02d" % s for s in sorted(seasons)[:6])))
            # 能连上但解析不出季 → 说明是**接口返回形态**变了，把结构（键名）带回去
            last_error = "详情接口返回 2xx，但没解析出季列表。响应结构：%s" % \
                         scrub_text(_describe_shape(data), [self.ttd.token])
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
            status, data, err = self.ttd.get_soft(
                "/api/media/details/tmdb/tv/%s/season/1" % probe_id)
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
                return True, ("季集详情可用；探活剧集 S01 返回 %d 集" % len(numbers))
            last = ("接口返回 HTTP %s 但没解析出任何集数据。响应结构：%s"
                    % (status, scrub_text(_describe_shape(data), [self.ttd.token])))
        return False, ("季集详情接口不可用（%s）。⚠️ 规范说明该接口**只有当前详情配置支持"
                       "完整季集模式时可用** —— 在它恢复之前，本插件无法确定"
                       "「应该有哪些集」，也就无法检测缺集（会把每一部剧都判为"
                       "「无法判定」而不是「无缺失」）。" % last)

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
        """保存扫描进度；失败只记警告（游标丢了顶多是下次从头扫，不影响正确性）。"""
        try:
            self._cursor_path().write_text(
                json.dumps({"offset": int(offset),
                            "updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
                           ensure_ascii=False),
                encoding="utf-8")
        except OSError as exc:
            self.log.warn("保存扫描进度失败（不影响本次结果）：%s" % str(exc)[:120])

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
        detail = self.ttd.get_json("/api/media/details/tmdb/tv/%s" % item["tmdb"])
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
        """
        path = "/api/media/details/tmdb/tv/%s/season/%s" % (tmdb_id, season)
        status, data, err = self.ttd.get_soft(path)
        if status is None:
            return None, "error", "网络失败：%s" % (err or "未知")
        if status == 404:
            return None, "absent", "TMDB 没有这一季（HTTP 404）"
        if not 200 <= status < 300:
            return None, "error", "HTTP %s：%s" % (status, err or "")
        if not isinstance(data, dict):
            return None, "absent", "响应不是 JSON 对象"
        numbers, air_dates = _extract_tmdb_episodes(data)
        if not numbers:
            return None, "absent", "该季没有返回任何集数据"
        if not self.only_aired:
            return {"numbers": sorted(numbers)}, "ok", ""
        today = date.today()
        aired, undated = [], []
        for number in sorted(numbers):
            air = air_dates.get(number)
            if not air:
                undated.append(number)
                continue
            parsed = _parse_date(air)
            if parsed and parsed <= today:
                aired.append(number)
        if undated:
            self.log.info("S%02d 有 %d 集没有播出日期，按「未开播」处理，不计入应有集数：%s"
                          % (season, len(undated), _join_nums(undated)))
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
            self.filled.append(self._fill_one(item))
            handled += 1
        if not self.max_fill and handled > 10 and not self.fill_budget_exhausted:
            self.log.info("本次不限制补齐部数，共处理 %d 部；建议先用「单次补齐上限」小步验证"
                          % handled)

        rows = []
        skipped_actions = 0
        for rec in self.filled:
            for entry in rec["actions"]:
                cand = entry.get("candidate") or {}
                if entry["detail"].startswith("跳过") or entry["detail"].startswith("没有搜到"):
                    skipped_actions += 1
                rows.append([
                    rec["series"],
                    entry["season"],
                    ("整季" if entry.get("whole_season") else _join_nums(entry["missing"])) or "-",
                    entry["keyword"],
                    "%d 条" % entry.get("candidate_count", len(entry["candidates"])),
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
        if skipped_actions:
            notes.append("有 %d 个季**没拿到可用的候选**（未搜到资源，或候选类型与所选动作不匹配 —— "
                         "例如离线下载只接受磁力 / 电驴）。详见下表的「处理结果」列。" % skipped_actions)
        return self._result(
            ok=True, title="补齐处理完成", tone="default",
            alert=alert, stats=stats, rows=rows,
            rows_label="补齐明细（共 %d 行，按季展开）" % len(rows),
            headers=["剧集", "季", "缺失集", "搜索关键词", "候选数", "类型", "处理结果"],
            notes=notes,
            extra_tables=[{"type": "table", "label": "缺失明细（共 %d 行）" % len(self._missing_rows()),
                           "headers": ["剧集", "季", "缺失集", "集数", "说明"],
                           "rows": self._missing_rows() or [["（无）", "-", "-", "-", "-"]]}],
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
            # 多季同时缺失时用剧名搜（一次拿到整包更省事）；只缺一季时带上季号，
            # 减少「想补 S02 却抓到 S01 包」的概率。
            keyword = "%s S%02d" % (title, season) if len(seasons) == 1 else title
            candidates, errors = self._search_for(item, season, keyword)
            entry = {
                "season": "S%02d" % season,
                "keyword": keyword,
                "missing": list(detail.get("episodes") or []),
                "whole_season": bool(detail.get("whole_season")),
                # 只留前 5 条进结果页（免得单页过大），但**数量要单独记**——
                # 此前用 len(只留 5 条的那份列表) 当候选总数，20 条也会显示成「5 条」。
                "candidates": candidates[:5],
                "candidate_count": len(candidates),
                "errors": errors,
                "candidate": None,
                "detail": "",
            }
            if not candidates:
                entry["detail"] = "没有搜到候选资源" + ("；" + "；".join(errors) if errors else "")
                self.log.warn("「%s」%s 未搜到候选资源" % (name, entry["season"]))
            else:
                best = self._pick_best(candidates)
                entry["candidate"] = best
                entry["detail"] = self._apply_action(best)
                # 日志里必须留下**完整链接**（尤其是「仅记录」动作 —— 列出链接就是它的目的；
                # 此前注释只看 note/url 的前 80 字，长分享链接会被截掉、无法复制）
                self.log.info("「%s」%s 选定候选：%s｜%s｜%s"
                              % (name, entry["season"], best.get("type") or "未知",
                                 (best.get("note") or "-")[:60], best.get("url") or ""))
            record["actions"].append(entry)
        return record

    def _search_note_components(self):
        return [{"type": "text", "text": "**关于「TgtoDrive 内置资源检索」**：该接口"
                                         "（`/api/media/resources/search`）在规范里没有响应 schema，"
                                         "本插件已把原始响应写入运行日志。若候选为空，"
                                         "请对照日志与「我的插件 → 影视发现」页面确认字段，"
                                         "以便后续版本精确对接。盘搜（PanSou）的响应结构是公开文档化的，"
                                         "候选解析完整。", "style": {"tone": "muted"}}]

    def _search_for(self, item, season, keyword):
        """针对**一个季**在配置的搜索源里找候选；返回 ``(候选列表, 错误列表)``。"""
        candidates, errors = [], []
        detail = item["seasons"].get(season) or {}
        missing = list(detail.get("episodes") or [])
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

    def _pick_best(self, candidates):
        """选一个候选：先看**当前动作能不能用它**，再在同类里「选新不选旧」。

        动作相关性必须考虑 —— 此前不分动作一律把磁力 / 电驴排第一，于是「转存」动作下
        也会优先挑中磁力链接，而磁力并不是网盘分享链接（转存接口的 `share_url` 收不了），
        真跑时会失败或空转。「仅记录」不分动作，网盘白名单内或可直接离线的都算好候选。

        同级再按 `datetime` 降序（资源越旧越可能失效，认不出时间时排最后），
        最后才用标题长度做三级键。
        """
        def rank(kind):
            in_whitelist = (not self.cloud_types) or kind in self.cloud_types
            if self.action == ACTION_OFFLINE:
                if kind in OFFLINE_TYPES:
                    return 0
                return 1 if in_whitelist else 2
            if self.action == ACTION_TRANSFER:
                if kind in OFFLINE_TYPES:
                    return 2        # 磁力 / 电驴不能转存，只在实在没别的候选时才轮到
                return 0 if in_whitelist else 1
            if kind in OFFLINE_TYPES or in_whitelist:
                return 0
            return 1

        def sort_key(c):
            stamp = _parse_datetime(c.get("datetime"))
            return (rank(c.get("type") or ""), -stamp if stamp else 0,
                    -len(c.get("note") or ""))
        return sorted(candidates, key=sort_key)[0]

    def _apply_action(self, candidate):
        """按动作处理一条候选；返回可读结论。

        **动作与候选类型的匹配检查必须放在 dry-run 分支之前**：dry-run 的意义就是
        「准确预告真实运行会做什么」。此前先返回「将提交离线下载…」，于是预览里显示
        会离线下载，真跑时却因候选是网盘链接而「跳过」—— 预览与实际不一致。
        """
        kind = candidate.get("type") or "未知"
        label = PANSOU_CLOUD_LABELS.get(kind, kind)
        url = candidate.get("url") or ""
        pwd = candidate.get("password") or ""

        if self.action == ACTION_RECORD:
            return "仅记录：%s%s" % (url, ("（提取码 %s）" % pwd) if pwd else "")

        if self.action == ACTION_OFFLINE and kind not in OFFLINE_TYPES:
            return "跳过：候选是「%s」，离线下载只支持磁力 / 电驴" % label
        if self.action == ACTION_TRANSFER and kind in OFFLINE_TYPES:
            # 磁力 / 电驴不是网盘分享链接，转存接口的 share_url 收不了
            return "跳过：候选是「%s」，转存只接受网盘分享链接（磁力请改用「提交离线下载」）" % label

        provider = self._effective_provider()
        if self.dry_run:
            return "将%s：%s%s（目标网盘：%s）" % (
                ACTION_LABELS.get(self.action), url,
                ("（提取码 %s）" % pwd) if pwd else "",
                provider or "TgtoDrive 默认")

        if self.action == ACTION_OFFLINE:
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
            return ("已提交离线下载（HTTP %s，目标 %s）"
                    % (status, provider or "TgtoDrive 默认")) if ok else \
                   ("离线下载失败：HTTP %s %s" % (status, scrub_text((text or "")[:120], [self.ttd.token])))

        if self.action == ACTION_TRANSFER:
            body = {"share_url": url, "source": candidate.get("source") or "plugin",
                    "provider": provider or ""}
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
            self.log.info("提交转存 HTTP %s（目标：%s，点数上限：%s）：%s"
                          % (status, provider or "TgtoDrive 默认",
                             self.ttd_max_points if self.ttd_max_points is not None else "未限制",
                             scrub_text((text or "")[:300], [self.ttd.token])))
            return ("已提交转存（HTTP %s，目标 %s）"
                    % (status, provider or "TgtoDrive 默认")) if ok else \
                   ("转存失败：HTTP %s %s" % (status, scrub_text((text or "")[:120], [self.ttd.token])))

        return "未执行"

    # -- 生效配置 ----------------------------------------------------------

    def do_config(self):
        rows = [
            ["执行功能", FUNC_LABELS.get(self.func, self.func)],
            ["TgtoDrive", self.ttd.describe()],
            ["Emby", "%s（来源：%s）" % (self.emby.describe(), self.emby_source_note or "未确认")],
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
            ["目标网盘（provider）", ("%s（来自插件表单）" % self.target_dir) if self.target_dir
             else ("%s（来自 TgtoDrive 的 target_provider）" % self.ttd_target_provider
                   if self.ttd_target_provider else "（未配置，由 TgtoDrive 用默认值）")],
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
        try:
            return int(item)
        except (TypeError, ValueError):
            return None
    if not isinstance(item, dict):
        return None
    for key in SEASON_NUMBER_KEYS:
        value = item.get(key)
        try:
            if value is not None and str(value).strip() != "":
                return int(float(str(value).strip()))
        except (TypeError, ValueError):
            continue
    name = str(item.get("name") or item.get("title") or "")
    if name:
        if re.search(r"特别|特典|specials?", name, re.I):
            return 0
        match = re.search(r"(?:season|s)\s*0*(\d{1,3})", name, re.I) \
            or re.search(r"第\s*0*(\d{1,3})\s*季", name)
        if match:
            try:
                return int(match.group(1))
            except (TypeError, ValueError):
                return None
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
            try:
                value = node.get(key)
                if value is not None and str(value).strip() != "":
                    count = int(float(str(value).strip()))
                    if count > 0:
                        return count
            except (TypeError, ValueError):
                continue
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
    text = str(text or "").strip()
    if not text:
        return None
    for fmt, length in DATE_FORMATS:
        try:
            return datetime.strptime(text[:length], fmt).date()
        except ValueError:
            continue
    match = re.match(r"^(\d{4})-(\d{1,2})-(\d{1,2})", text)
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
