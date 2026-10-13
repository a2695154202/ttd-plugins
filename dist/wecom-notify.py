# -*- coding: utf-8 -*-
# 由 scripts/package_plugin.py 依据 plugins/wecom-notify/ 自动生成，请勿直接编辑。
# 单文件插件：顶层唯一的 PLUGIN_MANIFEST 常量字典 + 入口源码。

PLUGIN_MANIFEST = {
  'schema_version': 1,
  'id': 'wecom-notify',
  'name': '企业微信通知',
  'version': '1.0.0',
  'description': '让 TgtoDrive 具备企业微信（WeCom）应用消息推送能力，并且可以被其他插件调用。填写企业 ID / 应用 AgentId / 应用 Secret 后，即可用文本、markdown、文本卡片或带图卡片通知，把任意内容发送给指定成员、部门、标签或全体成员；支持转发代理地址（应对「企业可信IP」限制）、超长消息自动分段、access_token 本地缓存与发送历史。内置「发送测试消息」按钮一键验证通知链路，「查看调用方法」按钮给出被其他插件调用的完整参数说明与示例代码。',
  'author': 'a2695154202',
  'entry': 'plugin.py',
  'timeout': 120,
  'inputs': [
    {
      'name': 'func',
      'label': '执行功能',
      'type': 'select',
      'default': 'test',
      'options': [
        {
          'label': '发送测试消息（内置内容，文本 + 卡片各一条）',
          'value': 'test',
        },
        {
          'label': '检查配置（获取 access_token）',
          'value': 'config',
        },
        {
          'label': '查看发送历史（本地记录）',
          'value': 'history',
        },
        {
          'label': '查看调用方法（供其他插件调用）',
          'value': 'docs',
        },
      ],
      'help': '「发送测试消息」的文本与卡片内容已内置在插件里，无需填写：点击后会依次发出一条文本消息和一条卡片消息（间隔 3 秒），用来验证「配置 + 网络 + 收件人」整条链路。\n\n本插件还向其它插件提供「发送消息（send）」能力，但那需要传入正文参数，因此只在接口层开放，不在本界面出现 —— 用法见「查看调用方法」或仓库里的 CALLING.md。',
    },
    {
      'name': 'msgtype',
      'label': '消息类型',
      'type': 'select',
      'default': 'text',
      'options': [
        {
          'label': '文本 text（微信可收）',
          'value': 'text',
        },
        {
          'label': '图文消息 news（微信可收、带图，推荐）',
          'value': 'news',
        },
        {
          'label': '文本卡片 textcard（微信可收，带标题与跳转按钮）',
          'value': 'textcard',
        },
        {
          'label': 'markdown（仅企业微信可收，微信收不到）',
          'value': 'markdown',
        },
        {
          'label': '卡片通知 template_card（仅企业微信可收，微信收不到）',
          'value': 'template_card',
        },
      ],
      'help': '【微信可收性】这是企业微信的官方限制，与收件人配置无关：\n• 微信可以收到：文本 text、图文消息 news、文本卡片 textcard；\n• 微信收不到：markdown（文档明确「微工作台（原企业号）不支持展示 markdown 消息」）、卡片通知 template_card（官方技术支持明确「微信插件不支持接收模板卡片消息」）。\n所以想「既有卡片效果、微信又能收到」时，请用「图文消息 news」——大图 + 标题 + 描述 + 点击跳转，是微信里最接近卡片的形态。\n\n【长度限制】text / markdown 正文上限 2048 字节（约 680 汉字），超出按「超长消息自动分段」处理；news 标题 ≤128 字节、描述 ≤512 字节；textcard 与 news 需要「卡片标题」；「卡片图片」对 news 同样生效。\n\n【若微信可收的类型仍收不到】请检查管理后台该应用是否勾选了「在微工作台中始终进入主页」——勾选后应用在微信端只能收到文本消息，其他类型会被转换成「到企业微信查看」的提示。',
    },
    {
      'name': 'touser',
      'label': '接收成员（UserID）',
      'type': 'text',
      'default': '@all',
      'placeholder': '@all 或 zhangsan|lisi',
      'help': '多个成员用 | 分隔，最多 1000 个；填 @all 表示发送给该应用的全体可见成员（此时忽略部门与标签）。可在「查询应用可见范围成员」里查到 UserID。',
    },
    {
      'name': 'toparty',
      'label': '接收部门（部门 ID）',
      'type': 'text',
      'default': '',
      'placeholder': '1|2',
      'help': '多个部门用 | 分隔，最多 100 个。touser 为 @all 时本项被忽略。',
    },
    {
      'name': 'totag',
      'label': '接收标签（标签 ID）',
      'type': 'text',
      'default': '',
      'placeholder': '1|2',
      'help': '多个标签用 | 分隔，最多 100 个。touser 为 @all 时本项被忽略。',
    },
    {
      'name': 'safe',
      'label': '保密消息（不可分享、带水印）',
      'type': 'boolean',
      'default': False,
      'help': '对应接口的 safe 参数：0 可对外分享，1 不可分享且内容显示水印。',
    },
    {
      'name': 'title',
      'label': '文本卡片（不填时用内置测试标题）',
      'type': 'text',
      'default': '',
      'placeholder': '文本卡片 / 图文消息 / 卡片通知 的标题',
      'help': '作为 textcard、图文消息 news、卡片通知的标题。textcard 必填（128 字节以内）；news 不填时自动用「渠道名称 + 通知」占位。',
    },
    {
      'name': 'url',
      'label': '卡片跳转链接',
      'type': 'text',
      'default': '',
      'placeholder': 'https://example.com/detail（文本卡片 / 图文消息）',
      'help': 'textcard、图文消息 news、卡片通知 点击后的跳转地址，需带 http/https 协议头。textcard 必填；news 为空时回退为官方站点链接。',
    },
    {
      'name': 'card_type',
      'label': '卡片类型',
      'type': 'select',
      'default': 'text_notice',
      'options': [
        {
          'label': '文本通知型 text_notice（大图 + 键值列表）',
          'value': 'text_notice',
        },
        {
          'label': '图文展示型 news_notice（大图 + 竖排图文）',
          'value': 'news_notice',
        },
      ],
      'help': '仅在「消息类型」选择「卡片通知」时生效。图文展示型需要提供卡片图片，未提供时会自动改用文本通知型。',
    },
    {
      'name': 'card_image',
      'label': '卡片图片（卡片通知 / 图文消息）',
      'type': 'text',
      'default': 'http://192.168.101.100:12366/static/brand_logo.png?v=18de0d2b37259200-5d57',
      'placeholder': 'https://example.com/cover.jpg',
      'help': '卡片主图，「卡片通知」与「图文消息 news」都会使用它。可填 http(s) 链接，也可填容器内已存在的本地图片路径。注意：企业微信服务器访问不到内网地址（如 192.168.x.x / 10.x.x.x / localhost），插件检测到这类地址时会先自行下载，再上传到企业微信换取可用的图片 URL，确保能显示出图。建议尺寸 1068×455、格式 JPG/PNG、不超过 2 MB。',
    },
    {
      'name': 'card_source',
      'label': '卡片来源名称',
      'type': 'text',
      'default': '',
      'placeholder': '站点 1PTBA 消息',
      'help': '显示在卡片左上角的小字，建议不超过 20 字，超出会被截断。',
    },
    {
      'name': 'card_source_icon',
      'label': '来源图标链接',
      'type': 'text',
      'default': '',
      'placeholder': 'https://example.com/icon.png',
      'help': '卡片来源名称左侧的小图标，http(s) 链接，可留空。',
    },
    {
      'name': 'card_sub_title',
      'label': '卡片副标题',
      'type': 'text',
      'default': '',
      'placeholder': '标题下方的一行说明',
      'help': '建议不超过 30 字，超出会被截断。',
    },
    {
      'name': 'card_aspect_ratio',
      'label': '卡片图片比例',
      'type': 'number',
      'default': 2.25,
      'min': 1.3,
      'max': 2.25,
      'step': 0.05,
      'help': '企业微信允许 1.3–2.25，默认 2.25（宽图）。超出范围会自动收敛到边界值。',
    },
    {
      'name': 'channel_name',
      'label': '通知渠道名称',
      'type': 'text',
      'default': '企业微信',
      'placeholder': 'WX',
      'help': '仅用于界面显示与通知标题前缀，可随意填写；与 TgtoDrive 的通知渠道名保持一致的写法即可。',
    },
    {
      'name': 'corp_id',
      'label': '企业 ID（必填）',
      'type': 'text',
      'default': '',
      'placeholder': 'ww 开头的一串字符',
      'help': '企业微信管理后台 →「我的企业 → 企业信息」中的企业 ID（corpid）。',
    },
    {
      'name': 'agent_id',
      'label': '应用 AgentId（必填）',
      'type': 'text',
      'default': '',
      'placeholder': '纯数字，例如 1000001',
      'help': '企业微信管理后台 →「应用管理 → 自建应用 → 应用详情」中的 AgentId，整数。',
    },
    {
      'name': 'corp_secret',
      'label': '应用 Secret（必填）',
      'type': 'password',
      'default': '',
      'help': '自建应用详情页的 Secret。注意：插件设置以明文 JSON 保存于服务器插件目录，管理员可读取；更在意安全时可改用环境变量 TGTO_WECOM_CORP_SECRET，并把此项留空。Secret 不会出现在运行日志或返回值中。',
    },
    {
      'name': 'api_base',
      'label': '代理地址',
      'type': 'text',
      'default': 'https://qyapi.weixin.qq.com',
      'placeholder': 'https://qyapi.weixin.qq.com',
      'help': '接口基础地址。2022 年 6 月 28 日后新建的自建应用必须配置「企业可信IP」才能调用接口（否则报 60020）；若服务器出口 IP 不固定，可在此填写转发代理地址（如 https://wx.example.com），请求会发往「代理地址 + /cgi-bin/...」。不使用代理时保留默认值。',
    },
    {
      'name': 'proxy_mode',
      'label': '网络代理',
      'type': 'select',
      'default': 'off',
      'options': [
        {
          'label': '不使用代理（直连，推荐）',
          'value': 'off',
        },
        {
          'label': '跟随容器环境变量代理（HTTP_PROXY / HTTPS_PROXY）',
          'value': 'env',
        },
      ],
      'help': '默认「不使用代理」。若「代理地址」是只允许特定地区访问的转发服务，本插件跟随容器代理会把请求送去代理而连不通（表现为 SSL 握手被中断：SSLError / UNEXPECTED_EOF_WHILE_READING）。只有当容器必须经代理才能访问企业微信时，才改成「跟随容器环境变量代理」。',
    },
    {
      'name': 'token',
      'label': '回调 Token',
      'type': 'text',
      'default': '',
      'help': '自建应用「接收消息 → API 接收消息」配置中的 Token。用于校验收到的回调请求；本插件是一次性执行、无常驻监听，因此该项仅做配置留档与格式校验，不参与消息收发。',
    },
    {
      'name': 'encoding_aes_key',
      'label': 'EncodingAESKey',
      'type': 'password',
      'default': '',
      'help': '同上，接收消息配置中的 EncodingAESKey（43 位 Base64 字符）。填写后会做长度与字符集校验，格式不对会在日志中提示。',
    },
    {
      'name': 'admin_users',
      'label': '管理员白名单',
      'type': 'textarea',
      'default': '',
      'placeholder': 'CaiShenYeDeXinTouBao|zhangsan',
      'help': '可使用管理菜单及命令的用户 ID 列表，多个用换行、逗号或 | 分隔。当「接收成员 / 部门 / 标签」都为空时，插件会把消息发送给这里的成员作为兜底收件人。',
    },
    {
      'name': 'split_long',
      'label': '超长消息自动分段',
      'type': 'boolean',
      'default': True,
      'help': '开启后，超过 2048 字节的正文会按段落边界切成多条依次发送，并标注序号；关闭则只发送截断后的内容并在日志中提示。',
    },
    {
      'name': 'history_days',
      'label': '历史记录保留天数',
      'type': 'number',
      'default': 30,
      'min': 1,
      'max': 3650,
      'step': 1,
      'help': '发送历史保存在插件数据目录，超出天数的记录会被清理。',
    },
    {
      'name': 'tgto_base_url',
      'label': 'TgtoDrive 地址（可选）',
      'type': 'text',
      'default': '',
      'placeholder': 'http://127.0.0.1:12366',
      'help': '仅当上面的「企业 ID / 应用 Secret」留空时使用：插件会尝试从 TgtoDrive 已保存的项目设置里读取微信渠道配置作为兜底。留空则读取环境变量 TGTO_OPENAPI_BASE_URL。',
    },
    {
      'name': 'tgto_token',
      'label': 'OpenAPI 令牌（可选）',
      'type': 'password',
      'default': '',
      'help': '配合上一项使用，留空则读取环境变量 TGTO_OPENAPI_TOKEN。仅用于读取项目设置，不会出现在日志或返回值中。',
    },
  ],
  'ui': {
    'width': 'wide',
    'layout': 'stack',
    'components': [
      {
        'type': 'heading',
        'text': '企业微信通知',
      },
      {
        'type': 'alert',
        'text': '在企业微信管理后台创建自建应用，把「企业 ID / 应用 AgentId / 应用 Secret」填入「应用配置」页签，然后点右上角「发送测试消息」验证通知链路。若返回 60020（IP 不在可信名单）：把服务器出口 IP 加入应用的「企业可信IP」，或在「应用配置 → 代理地址」填写转发代理地址。',
        'style': {
          'tone': 'warning',
        },
      },
      {
        'type': 'grid',
        'columns': 4,
        'children': [
          {
            'type': 'tabs',
            'style': {
              'span': 3,
            },
            'children': [
              {
                'type': 'card',
                'label': '发送消息',
                'children': [
                  {
                    'type': 'field',
                    'name': 'func',
                  },
                  {
                    'type': 'field',
                    'name': 'msgtype',
                  },
                  {
                    'type': 'field',
                    'name': 'touser',
                  },
                  {
                    'type': 'field',
                    'name': 'toparty',
                  },
                  {
                    'type': 'field',
                    'name': 'totag',
                  },
                  {
                    'type': 'field',
                    'name': 'safe',
                  },
                  {
                    'type': 'field',
                    'name': 'title',
                  },
                  {
                    'type': 'field',
                    'name': 'url',
                  },
                ],
              },
              {
                'type': 'card',
                'label': '卡片通知',
                'children': [
                  {
                    'type': 'field',
                    'name': 'card_type',
                  },
                  {
                    'type': 'field',
                    'name': 'card_image',
                  },
                  {
                    'type': 'field',
                    'name': 'card_source',
                  },
                  {
                    'type': 'field',
                    'name': 'card_source_icon',
                  },
                  {
                    'type': 'field',
                    'name': 'card_sub_title',
                  },
                  {
                    'type': 'field',
                    'name': 'card_aspect_ratio',
                  },
                ],
              },
              {
                'type': 'card',
                'label': '应用配置',
                'children': [
                  {
                    'type': 'field',
                    'name': 'channel_name',
                  },
                  {
                    'type': 'field',
                    'name': 'corp_id',
                  },
                  {
                    'type': 'field',
                    'name': 'agent_id',
                  },
                  {
                    'type': 'field',
                    'name': 'corp_secret',
                  },
                  {
                    'type': 'field',
                    'name': 'api_base',
                  },
                  {
                    'type': 'field',
                    'name': 'proxy_mode',
                  },
                  {
                    'type': 'divider',
                  },
                  {
                    'type': 'button',
                    'label': '检查配置',
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
                ],
              },
              {
                'type': 'card',
                'label': '回调与高级',
                'children': [
                  {
                    'type': 'field',
                    'name': 'token',
                  },
                  {
                    'type': 'field',
                    'name': 'encoding_aes_key',
                  },
                  {
                    'type': 'field',
                    'name': 'admin_users',
                  },
                  {
                    'type': 'divider',
                  },
                  {
                    'type': 'field',
                    'name': 'split_long',
                  },
                  {
                    'type': 'field',
                    'name': 'history_days',
                  },
                  {
                    'type': 'field',
                    'name': 'tgto_base_url',
                  },
                  {
                    'type': 'field',
                    'name': 'tgto_token',
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
                'type': 'button',
                'label': '发送测试消息',
                'action': 'run',
                'params': {
                  'func': 'test',
                },
                'style': {
                  'tone': 'primary',
                  'size': 'large',
                  'variant': 'solid',
                },
              },
              {
                'type': 'button',
                'label': '查看调用方法',
                'action': 'run',
                'params': {
                  'func': 'docs',
                },
                'style': {
                  'tone': 'default',
                  'size': 'large',
                  'variant': 'outline',
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
        'text': '微信能收到的消息类型：文本 text、图文消息 news、文本卡片 textcard；markdown 与卡片通知在微信里收不到（企业微信官方限制）。想「卡片效果 + 微信也能收到」请用「图文消息 news」——大图 + 标题 + 描述 + 点击跳转。',
        'style': {
          'tone': 'muted',
        },
      },
      {
        'type': 'text',
        'text': '「发送测试消息」的内容已内置，无需填写：点击后会依次发出一条文本消息和一条卡片消息（间隔 3 秒），用来验证「配置 + 网络 + 收件人」整条链路。其中卡片那条按「消息类型」里选中的卡片类发送 —— 把类型选成「图文消息 news」就能直接验证微信是否收得到。卡片的图片、来源等参数在「卡片通知」页签（「卡片图片」对图文消息同样生效）；「查看调用方法」给出被其他插件调用的参数表、示例与在线文档链接。',
        'style': {
          'tone': 'muted',
        },
      },
    ],
  },
}


# -*- coding: utf-8 -*-
"""企业微信通知 · TgtoDrive Python 插件

为企业微信（WeCom / 原企业号）自建应用提供「应用消息推送」能力：
按企业微信官方接口 https://developer.work.weixin.qq.com/document 实现
`GET /cgi-bin/gettoken` 与 `POST /cgi-bin/message/send`。

能力
  * 发送消息：文本 / **图文消息 news** / markdown / 文本卡片 / **卡片通知（模板卡片）**
    五种类型，支持发给成员、部门、标签或 @all。
  * **微信可收性**（企业微信官方限制）：微信插件能收到 文本 / 图文消息 / 文本卡片；
    markdown 与模板卡片**收不到**。因此需要微信也收到、又要卡片效果时用「图文消息」——
    大图 + 标题 + 描述 + 点击跳转；把消息类型从「卡片通知」改成「图文消息」时，
    原卡片 JSON 会被**自动转换成图文**，无需重写内容。
  * **卡片通知**：支持带图（图片 URL，或容器内本地图片自动上传换取 URL）、
    来源名称与图标、键值列表（最多 6 条）、点击跳转链接；
    可选文本通知型 text_notice 与图文展示型 news_notice。
  * 发送测试消息（界面顶部独立按钮）：测试文本与测试卡片内容已内置在插件里，
    界面不再提供内容输入框 —— 点击后会依次发出一条文本消息和一条卡片消息
    （间隔 3 秒），用来验证「配置 + 网络 + 收件人」整条链路；卡片那条按「消息类型」
    里选中的卡片类发送（选「图文消息 news」即可直接验证微信是否收得到）。
  * 检查配置：校验必填项格式并真实获取一次 access_token，给出剩余有效期。
  * 查看发送历史：本地记录每次发送的类型、收件人、结果与错误码。
  * **查看调用方法**：输出「被其他插件调用」的参数表与示例，
    并给出仓库内 CALLING.md 的在线链接。

界面取舍
  * 「执行功能」下拉框只有 发送测试消息 / 检查配置 / 查看发送历史 / 查看调用方法；
    **「发送消息（send）」与「查询应用可见范围成员（users）」不在界面上** ——
    send 需要调用方传入正文，只在接口层开放；users 已移除。
  * 顶部两个按钮：发送测试消息、查看调用方法。

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

import json
import re
import socket
import ssl
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:  # 容器内一般已装；不可用时回退 urllib
    import requests
except Exception:  # pragma: no cover - 仅在极简环境触发
    requests = None


# ---------------------------------------------------------------------------
# 常量
# ---------------------------------------------------------------------------

DEFAULT_API_BASE = "https://qyapi.weixin.qq.com"
DEFAULT_TGTO_BASE = "http://127.0.0.1:12366"

USER_AGENT = "TgtoDrive-WecomNotify/1.0 (+https://github.com/a2695154202/ttd-plugins)"

CONNECT_TIMEOUT = 10
READ_TIMEOUT = 30

# 文本与 markdown 正文上限（企业微信文档：不超过 2048 字节）
MESSAGE_BYTE_LIMIT = 2048
# 文本卡片标题上限 128 字节，描述按 512 字节控制
TEXTCARD_TITLE_LIMIT = 128
TEXTCARD_DESC_LIMIT = 512

# access_token 有效期 7200 秒；提前 300 秒视为过期
TOKEN_REFRESH_AHEAD = 300
TOKEN_DEFAULT_TTL = 7200

TOKEN_FILE = "token.json"
HISTORY_FILE = "history.json"
HISTORY_MAX_RECORDS = 500

# 界面上只提供 FUNC_UI 里的功能；``send`` 不出现在「执行功能」下拉框中，
# 仅供其它插件通过 OpenAPI 调用（药丸签到等通知方走的就是这条路径）。
FUNC_LABELS = {
    "send": "发送消息（供其他插件调用）",
    "test": "发送测试消息",
    "config": "检查配置",
    "history": "查看发送历史",
    "docs": "查看调用方法",
}
VALID_FUNCS = tuple(FUNC_LABELS)
FUNC_UI = ("test", "config", "history", "docs")

MSGTYPE_LABELS = {
    "text": "文本",
    "markdown": "markdown",
    "textcard": "文本卡片",
    "news": "图文消息",
    "template_card": "卡片通知（模板卡片）",
}
VALID_MSGTYPES = tuple(MSGTYPE_LABELS)

# 微信插件（原企业号 / 微工作台）能真正收到的消息类型。
# 依据：企业微信文档中「微工作台（原企业号）不支持展示 markdown 消息」
# 「微工作台（原企业号）不支持展示模板卡片消息」，以及官方技术支持明确答复
# 「微信插件不支持接收模板卡片消息」「小程序应用消息也无法在微信插件接收」。
WECHAT_OK = frozenset({"text", "textcard", "news"})
WECHAT_NO = frozenset({"markdown", "template_card"})

# 图文消息（news）的企业微信侧限制
NEWS_MAX_ARTICLES = 8
NEWS_TITLE_LIMIT = 60      # 企业微信按字节限 128，中文按字符取保守值
NEWS_DESC_LIMIT = 160      # 企业微信按字节限 512
NEWS_IMAGE_SPEC = "大图建议 1068×455，小图建议 150×150，JPG / PNG"

CARD_TYPE_LABELS = {
    "text_notice": "文本通知型 text_notice（大图 + 键值列表）",
    "news_notice": "图文展示型 news_notice（大图 + 竖排图文）",
}
VALID_CARD_TYPES = tuple(CARD_TYPE_LABELS)

# 模板卡片各字段的企业微信侧建议上限；超出会被企业微信自行截断，
# 这里主动截断并在日志中说明，避免用户以为内容完整送达。
CARD_TITLE_LIMIT = 26
CARD_TITLE_DESC_LIMIT = 30
CARD_SOURCE_DESC_LIMIT = 20
CARD_SUB_TITLE_LIMIT = 112
CARD_KEYNAME_LIMIT = 5
CARD_VALUE_LIMIT = 30
CARD_ITEMS_MAX = 6
CARD_VERTICAL_MAX = 4
CARD_ASPECT_MIN = 1.3
CARD_ASPECT_MAX = 2.25
CARD_ASPECT_DEFAULT = 2.25
# card_action 在模板卡片中是必填项，缺省时回退到官方站点
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


def _parse_card_items(text, limit=CARD_ITEMS_MAX):
    """把多行「键=值」文本解析成模板卡片的 horizontal_content_list。

    支持 ``键=值``、``键:值``、``键：值``，也支持用 ``|`` 分隔；空行与
    ``#`` 开头的行会被忽略。返回 ``(items, notes)``，notes 为需要写入日志的说明。
    """
    items = []
    notes = []
    for raw_line in str(text or "").replace("\r\n", "\n").split("\n"):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        parts = re.split(r"\s*[=：:]\s*|\s*\|\s*", line, maxsplit=1)
        if len(parts) < 2:
            notes.append("忽略无法解析的行（应为「键=值」）：%s" % line[:40])
            continue
        key = parts[0].strip()
        value = parts[1].strip()
        if not key:
            notes.append("忽略缺少键的行：%s" % line[:40])
            continue
        if len(items) >= limit:
            notes.append("键值条目超过 %d 条，已丢弃「%s」" % (limit, key))
            continue
        short_key, key_cut = _clip(key, CARD_KEYNAME_LIMIT)
        short_value, value_cut = _clip(value, CARD_VALUE_LIMIT)
        if key_cut:
            notes.append("键「%s」超过 %d 字，截断为「%s」"
                         % (key, CARD_KEYNAME_LIMIT, short_key))
        if value_cut:
            notes.append("「%s」的值超过 %d 字，已截断（企业微信侧同样会截断）"
                         % (short_key, CARD_VALUE_LIMIT))
        items.append({"keyname": short_key, "value": short_value})
    return items, notes


def _kv_to_lines(text):
    """把「键=值」多行文本转成「键：值」多行文本，供图文消息的描述使用。

    与 :func:`_parse_card_items` 的区别：不做键 ≤5 字 / 值 ≤30 字的截断
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
            response = requests.get(url, timeout=timeout, stream=True,
                                    headers={"User-Agent": USER_AGENT})
            if response.status_code != 200:
                return None, "HTTP %s" % response.status_code
            data = response.content
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)
    else:
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=timeout[1]) as response:
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
            parts.append(
                "处理方式二选一：① 到企业微信管理后台「应用管理 → 自建应用 → 企业可信IP」"
                "把上述 IP 加入白名单（配置后约 1 分钟生效）；"
                "② 在「应用配置 → 代理地址」填写转发代理地址，由代理的固定 IP 调用接口"
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
                response = requests.get(url, headers=headers,
                                        timeout=(CONNECT_TIMEOUT, READ_TIMEOUT))
                if response.status_code != 200:
                    return None, "HTTP %s" % response.status_code
                return response.json(), None
            except Exception as exc:
                return None, "%s: %s" % (type(exc).__name__, exc)
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=READ_TIMEOUT) as response:
                return json.loads(response.read().decode("utf-8", "replace")), None
        except Exception as exc:
            return None, "%s: %s" % (type(exc).__name__, exc)

    def read(self):
        """返回 ``(config_dict, note)``；config_dict 为空表示没有读到可用配置。"""
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


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

class _NotifyRunner(object):

    def __init__(self, params, context):
        context = context if isinstance(context, dict) else {}
        self.params = params if isinstance(params, dict) else {}
        self.data_dir = context.get("data_dir") or "."
        self.log = _Logger()

        self.func = _s(self.params, "func", "send") or "send"
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
        # 本次执行实际发送过的消息类型（测试消息会发多条，用于生成准确的微信可收性提示）
        self._sent_kinds = []

        self.touser = _s(self.params, "touser")
        self.toparty = _s(self.params, "toparty")
        self.totag = _s(self.params, "totag")
        self.safe = _b(self.params, "safe", False)
        self.title = _s(self.params, "title")
        self.url = _s(self.params, "url")
        self.content = _s(self.params, "content")

        # 模板卡片（卡片通知）相关
        self.card_type = (_s(self.params, "card_type", "text_notice") or "text_notice").lower()
        self.card_image = _s(self.params, "card_image")
        # 「卡片消息内容」；同时兼容早期字段名 card_items
        self.card_content = _s(self.params, "card_content") or _s(self.params, "card_items")
        self.card_items = self.card_content
        self.card_source = _s(self.params, "card_source")
        self.card_source_icon = _s(self.params, "card_source_icon")
        self.card_sub_title = _s(self.params, "card_sub_title")
        self.card_aspect_ratio = _f(self.params, "card_aspect_ratio", CARD_ASPECT_DEFAULT)

        self.split_long = _b(self.params, "split_long", True)
        self.history_days = max(_i(self.params, "history_days", 30), 1)

        self.tgto_base_url = _s(self.params, "tgto_base_url")
        self.tgto_token = _s(self.params, "tgto_token")

        self.config_source = "插件表单"
        self.client = None

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
            "接口地址 %s｜企业ID %s｜AgentId %s｜Secret %s｜网络 %s"
            % (self.client.masked_base(), _mask(self.corp_id), self.agent_id or "（未填写）",
               _filled(self.corp_secret),
               "跟随环境变量代理" if self.use_proxy else "直连（不走代理）")
        )

    def validate_textcard(self):
        if not self.title:
            raise ValueError("消息类型为「文本卡片」时必须填写「卡片标题」")
        if not self.url:
            raise ValueError("消息类型为「文本卡片」时必须填写「卡片跳转链接」")

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
        """
        if self._recipients is not None:
            return self._recipients
        touser = self.touser or "@all"
        if not self.touser and not self.toparty and not self.totag:
            admins = _split_ids(self.admin_users)
            if admins:
                touser = "|".join(admins)
                self.log.info("未填写接收成员/部门/标签，改用「管理员白名单」作为收件人：%s"
                              % "、".join(admins))
            else:
                touser = "@all"
                self.log.info("未填写任何收件人，默认发送给应用全体可见成员（@all）")
        self.log.info("接收人：成员 %s｜部门 %s｜标签 %s"
                      % (touser or "（无）", self.toparty or "（无）", self.totag or "（无）"))
        self._recipients = (touser, self.toparty, self.totag)
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

    def build_template_card(self, content):
        """组装 template_card 结构（文本通知型 / 图文展示型）。"""
        card_type = self.card_type if self.card_type in VALID_CARD_TYPES else "text_notice"
        title, title_cut = _clip(self.title, CARD_TITLE_LIMIT)
        title_desc, desc_cut = _clip(self.card_sub_title, CARD_TITLE_DESC_LIMIT)
        body, body_cut = _clip(str(content or "").replace("\n", " ").strip(),
                               CARD_SUB_TITLE_LIMIT)
        if title_cut:
            self.log.warn("卡片标题超过 %d 字，已截断" % CARD_TITLE_LIMIT)
        if desc_cut:
            self.log.warn("卡片副标题超过 %d 字，已截断" % CARD_TITLE_DESC_LIMIT)
        if body_cut:
            self.log.warn("「消息内容」超过 %d 字，卡片正文已截断" % CARD_SUB_TITLE_LIMIT)
        if not title and not title_desc and not body:
            raise ValueError(
                "卡片通知至少需要填写「卡片标题」或「消息内容」其中之一")

        image_url = self._resolve_card_image()
        ratio = min(max(self.card_aspect_ratio, CARD_ASPECT_MIN), CARD_ASPECT_MAX)
        if self.card_aspect_ratio != ratio:
            self.log.warn("图片比例需在 %.1f–%.1f 之间，已调整为 %.2f"
                          % (CARD_ASPECT_MIN, CARD_ASPECT_MAX, ratio))
        action_url = self.url
        if not action_url:
            action_url = CARD_DEFAULT_ACTION_URL
            self.log.warn("模板卡片的 card_action 为必填项，「卡片跳转链接」为空，"
                          "已回退为 %s" % CARD_DEFAULT_ACTION_URL)

        if card_type == "news_notice" and not image_url:
            self.log.warn("图文展示型需要卡片图片，「卡片图片」为空，已自动改用文本通知型")
            card_type = "text_notice"

        card = {"card_type": card_type}
        if self.card_source:
            source = {"desc": _clip(self.card_source, CARD_SOURCE_DESC_LIMIT)[0]}
            if self.card_source_icon:
                source["icon_url"] = self.card_source_icon
            card["source"] = source

        if card_type == "news_notice":
            main = {"title": title or title_desc or "通知"}
            if title_desc and title:
                main["desc"] = title_desc
            card["main_title"] = main
            card["card_image"] = {"url": image_url, "aspect_ratio": ratio}
            if body:
                card["vertical_content_list"] = [{"title": "内容", "desc": body}]
        else:
            main = {}
            if title:
                main["title"] = title
            if title_desc:
                main["desc"] = title_desc
            if main:
                card["main_title"] = main
            if body and (title or title_desc):
                card["sub_title_text"] = body
            elif body:
                card["sub_title_text"] = body
            if image_url:
                card["card_image"] = {"url": image_url, "aspect_ratio": ratio}
            items, notes = _parse_card_items(self.card_items)
            for note in notes:
                self.log.warn(note)
            if items:
                card["horizontal_content_list"] = items
                self.log.info("卡片键值列表 %d 条：%s"
                              % (len(items), "、".join(i["keyname"] for i in items)))

        card["card_action"] = {"type": 1, "url": action_url}
        return card

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
        elif self.msgtype == "markdown":
            payload["markdown"] = {"content": content}
        elif self.msgtype == "textcard":
            payload["textcard"] = {
                "title": self.title[:TEXTCARD_TITLE_LIMIT],
                "description": content[:TEXTCARD_DESC_LIMIT],
                "url": self.url,
                "btntxt": "查看详情",
            }
        elif self.msgtype == "template_card":
            kind, native = _parse_native_card_json(self.card_content)
            if kind in ("news", "articles"):
                raise ValueError(
                    "「卡片消息内容」里是**图文消息** JSON，但「消息类型」选的是「卡片通知」。"
                    "请把「消息类型」改为「图文消息 news」，或把内容换成模板卡片 JSON"
                    "（含 card_type 的对象）。")
            if kind == "card":
                self.log.info("「卡片消息内容」识别为企业微信原生 template_card JSON，直接使用"
                              "（不再按「键=值」解析）")
                payload["template_card"] = native
            elif kind == "body":
                self.log.info("「卡片消息内容」识别为完整的企业微信请求体 JSON，直接使用")
                merged = dict(native)
                merged.setdefault("msgtype", "template_card")
                for key in ("touser", "toparty", "totag", "agentid"):
                    if key in payload:
                        merged.setdefault(key, payload[key])
                payload = merged
            else:
                payload["template_card"] = self.build_template_card(content)
        elif self.msgtype == "news":
            kind, native = _parse_native_card_json(self.card_content)
            if kind == "news":
                self.log.info("「卡片消息内容」识别为完整的企业微信请求体 JSON（含 news），直接使用")
                merged = dict(native)
                merged.setdefault("msgtype", "news")
                for key in ("touser", "toparty", "totag", "agentid"):
                    if key in payload:
                        merged.setdefault(key, payload[key])
                payload = merged
            elif kind == "articles":
                self.log.info("「卡片消息内容」识别为图文消息 JSON（articles），直接使用")
                payload["news"] = native
            elif kind in ("card", "body"):
                # 用户多半是从「卡片通知」切过来的：原卡片 JSON 不必重写，
                # 自动提取标题 / 描述 / 键值 / 链接 / 图片，降级成图文消息。
                card = native.get("template_card") if kind == "body" else native
                converted = _template_card_to_news(card)
                if converted is None:
                    raise ValueError(
                        "「卡片消息内容」是模板卡片 JSON，但未能从中提取出标题或内容。"
                        "请至少填写 main_title.title、sub_title_text 或 "
                        "horizontal_content_list 中的一项，或改用「键=值」写法。")
                article = converted["articles"][0]
                picurl = article.pop("picurl", "")
                if picurl:
                    resolved = self._resolve_card_image(picurl)
                    if resolved:
                        article["picurl"] = resolved
                self.log.info("「卡片消息内容」是模板卡片 JSON，已自动转换为图文消息 news "
                              "（微信插件不支持模板卡片，转换后微信可以收到）")
                payload["news"] = converted
            else:
                payload["news"] = self.build_news(content)
        else:
            raise ValueError("不支持的「消息类型」：%s" % self.msgtype)

        if self.safe:
            if self.msgtype in ("text", "markdown"):
                payload["safe"] = 1
            else:
                self.log.warn("「%s」类型不支持保密消息（safe），该项已忽略"
                              % MSGTYPE_LABELS.get(self.msgtype, self.msgtype))
        return payload

    def do_send(self, content_override=None, ignore_content=False):
        """发送消息，必要时分段。返回结果字典。"""
        if ignore_content:
            content = content_override or ""
        else:
            content = self.content
            if not content and self.msgtype not in ("template_card", "news"):
                raise ValueError("「消息内容」为空，请填写后再发送")

        self.validate_encoding_key()
        if self.msgtype in ("textcard", "template_card", "news"):
            if self.msgtype == "textcard":
                self.validate_textcard()
            elif self.msgtype == "news":
                self.validate_news()
            return self._dispatch([content], segmented=False)

        chunks = _split_content(content)
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

        界面不再提供内容输入框，测试文本与测试卡片内容都在
        :data:`DEFAULT_TEST_TEXT` / :data:`DEFAULT_TEST_CARD` 里；
        其他插件调用时可传 ``content`` / ``card_content`` 覆盖内置内容。

        先发内置文本消息，间隔 3 秒再发内置卡片消息（共两条通知）。
        """
        text_body = (self.content.strip() or DEFAULT_TEST_TEXT).format(
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            channel=self.channel_name,
            api_base=self.client.masked_base(),
        )
        # 卡片内容写回 self.card_content：模板卡片的键值列表、图文消息的描述
        # 都从这里取，调用方传了 card_content 就用它，没传就用内置的。
        card_content = (self.card_content.strip() or DEFAULT_TEST_CARD).format(
            now=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            channel=self.channel_name,
            api_base=self.client.masked_base(),
        )
        original_card_content = self.card_content
        self.card_content = card_content
        self.card_items = card_content
        self.log.info("使用内置测试内容：文本 %d 字、卡片 %d 行"
                      % (len(text_body), len(card_content.splitlines())))

        # 文本消息取纯文本类；卡片消息取卡片类（textcard / 图文 / 模板卡片）。
        # 都跟随「消息类型」设置 —— 例如把消息类型选成「图文消息 news」，
        # 测试里的卡片就按 news 发送，这样能直接验证「微信是否收得到」。
        text_kind = self.msgtype if self.msgtype in ("text", "markdown") else "text"
        card_kind = (self.msgtype if self.msgtype in ("textcard", "template_card", "news")
                     else "template_card")

        plans = [
            (text_kind, "文本消息", text_body),
            (card_kind, "卡片消息", ""),
        ]

        self.log.info("发送测试消息：共 %d 条（%s）"
                      % (len(plans), "、".join(plan[1] for plan in plans)))
        self.log.info("两条之间间隔 %d 秒发送" % TEST_SEND_GAP_SECONDS)

        self._sent_kinds = [kind for _label, kind, _body in plans]

        original_msgtype = self.msgtype
        outcomes = []
        failures = []
        try:
            for index, (kind, label, body) in enumerate(plans):
                if index:
                    self.log.info("等待 %d 秒后发送下一条…" % TEST_SEND_GAP_SECONDS)
                    time.sleep(TEST_SEND_GAP_SECONDS)

                self.msgtype = kind
                if kind == "template_card":
                    self.title = self.title or "【%s】测试消息" % self.channel_name
                    self.url = self.url or CARD_DEFAULT_ACTION_URL
                    self.card_source = self.card_source or ("%s 测试消息" % self.channel_name)
                elif kind in ("textcard", "news"):
                    # 这两种都要求标题与跳转链接，测试时补默认值以免因缺配置而失败
                    self.title = self.title or "【%s】测试消息" % self.channel_name
                    self.url = self.url or CARD_DEFAULT_ACTION_URL

                self.log.info("→ 发送%s" % label)
                # 模板卡片与图文消息的内容来自 self.card_content（键值列表 /
                # 描述），正文传空以免与键值列表重复；文本卡片的描述需要正文。
                send_body = card_content if kind == "textcard" else body
                outcome = self._dispatch([send_body], segmented=False)
                outcomes.append((label, kind, outcome))
                if outcome.get("status") != "ok":
                    failures.append("%s：%s" % (label, outcome.get("error") or "发送失败"))
        finally:
            self.msgtype = original_msgtype
            self.card_content = original_card_content
            self.card_items = original_card_content

        rows = []
        msgids = []
        for label, kind, outcome in outcomes:
            msgids.extend(outcome.get("msgids") or [])
            rows.append([
                label,
                MSGTYPE_LABELS.get(kind, kind),
                "成功" if outcome.get("status") == "ok" else "失败",
                "、".join(outcome.get("msgids") or []) or (outcome.get("error") or "-")[:60],
            ])
        ok = not failures
        if not ok:
            summary = failures[0]
        else:
            summary = "两条通知都已发送成功（间隔 %d 秒）。" % TEST_SEND_GAP_SECONDS

        components = [
            {"type": "heading", "text": "发送测试消息"},
            {"type": "alert", "text": summary,
             "style": {"tone": "success" if ok else "danger"}},
            {"type": "table", "label": "本次发送（内置内容，共 2 条）",
             "headers": ["内容", "消息类型", "结果", "msgid / 错误"], "rows": rows},
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ]
        return {
            "status": "ok" if ok else "failed",
            "func": self.func,
            "batches_total": len(plans),
            "batches_ok": len([o for _, _, o in outcomes if o.get("status") == "ok"]),
            "msgids": msgids,
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
            ["func", "必填", "send 发送（**界面不提供，仅供调用方使用**）/ test 测试 / config 自检 / history 查历史 / docs 文档"],
            ["msgtype", "必填", "text / news（微信可收）｜textcard（微信可收）｜markdown / template_card（微信收不到）"],
            ["touser", "常用", "UserID，多个用 | 分隔；@all 表示该应用全体可见成员"],
            ["toparty / totag", "可选", "部门 ID / 标签 ID，touser 为 @all 时被忽略"],
            ["title", "卡片", "标题（news / textcard / template_card 使用）"],
            ["content", "常用", "正文。不传时 test 用内置测试文本、send 会报「消息内容为空」；界面没有该输入框"],
            ["card_content", "卡片", "卡片内容：可粘贴企业微信原生 JSON（模板卡片或图文消息，原样发送）；否则每行一条「键=值」。不传时 test 用内置测试卡片内容；界面没有该输入框"],
            ["card_image", "卡片", "主图：http(s) 链接、内网地址或容器内本地路径（都会先换成企业微信可用 URL）；news 同样使用"],
            ["card_source", "卡片", "卡片来源名称，例如「站点 1PTBA 消息」"],
            ["card_source_icon", "卡片", "来源图标 URL"],
            ["card_type", "卡片", "text_notice（默认，大图+键值列表）/ news_notice（图文展示型）"],
            ["url", "卡片", "点击跳转链接；template_card 的 card_action 与 textcard 均为必填，news 为空时回退官方站点"],
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
            "        \"msgtype\": \"template_card\",\n"
            "        \"touser\": \"@all\",\n"
            "        \"title\": \"新入库剧集：示例标题\",\n"
            "        \"card_source\": \"站点 1PTBA 消息\",\n"
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
            {"type": "markdown", "text": (
                "本插件可以通过 TgtoDrive OpenAPI 被**其他插件或脚本**调用，"
                "用于发送企业微信通知（文本、markdown、文本卡片或带图卡片）。\n\n"
                "**完整调用说明（参数表 / 返回值 / 错误处理 / 完整示例）：**\n\n"
                "- [plugins/wecom-notify/CALLING.md](%s)\n\n"
                "调用入口：`POST /api/toolbox/plugins/wecom-notify/run`" % DOCS_URL)},
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

        # 本次实际发送过的类型（测试消息会同时发「文本」+「卡片」，取实际集合更准确）
        sent_kinds = getattr(self, "_sent_kinds", None) or [self.msgtype]
        blocked = [k for k in sent_kinds if k in WECHAT_NO]
        if blocked:
            # 企业微信官方限制：微信插件（原企业号 / 微工作台）不展示 markdown 与模板卡片
            names = "、".join(MSGTYPE_LABELS.get(k, k) for k in blocked)
            reason = ("企业微信官方技术支持明确「**微信插件不支持接收模板卡片消息**」"
                      if "template_card" in blocked
                      else "企业微信文档明确「微工作台（原企业号）不支持展示 markdown 消息」")
            tip = ("要在微信也收到，把「消息类型」改成 **图文消息 news** 即可 ——"
                   "现有的卡片 JSON 会被**自动转换**成图文（标题 / 描述 / 键值 / 链接 / 图片），"
                   "无需重写内容；也可改用 文本卡片 或 文本。"
                   if "template_card" in blocked else
                   "要在微信也收到，请把「消息类型」改为 **图文消息 news**（带图）"
                   "或 文本卡片 / 文本。")
            components.append({
                "type": "alert",
                "text": ("%s —— 本次的「%s」只会在「企业微信」客户端出现，微信里收不到。%s"
                         % (reason, names, tip)),
                "style": {"tone": "warning"},
            })
        elif status == "ok":
            # 自建应用的消息只到「企业微信」客户端；个人微信需要关注「微信插件」才能收到
            components.append({
                "type": "text",
                "text": ("「%s」微信插件可以接收，消息已同时投递给企业微信客户端。"
                         "**若微信里仍收不到**，请按顺序检查三处：\n"
                         "1. 管理后台 → 该应用 →「可见范围」是否包含收件人；\n"
                         "2. 管理后台 → 该应用 → 是否勾选了「**在微工作台中始终进入主页**」——"
                         "勾选后应用在微信端**只能收到文本消息**（其他类型会被转成"
                         "「到企业微信查看」的提示），这一项最容易被忽略；\n"
                         "3. 微信 → 通讯录 → 本企业 → 微信插件 → 右上角 → 设置 →"
                         "「接收应用消息」是否已打开。\n"
                         "（模板卡片与 markdown 在微信里永远收不到，这与配置无关。）"
                         % MSGTYPE_LABELS.get(self.msgtype, self.msgtype)),
                "style": {"tone": "muted"},
            })

        components.extend([
            {"type": "divider"},
            {"type": "heading", "text": "运行日志"},
            {"type": "code", "text": self.log.text()},
        ])
        return {
            "status": status,
            "func": self.func,
            "msgtype": self.msgtype,
            "sent": sent,
            "total": total,
            "msgids": [m for m in msgids if m],
            "error": error,
            "ui": {"width": "wide", "layout": "stack", "components": components},
        }

    # -- 入口 --------------------------------------------------------------

    def execute(self):
        if self.func not in VALID_FUNCS:
            raise ValueError("不支持的执行功能：%s" % self.func)
        if self.msgtype not in VALID_MSGTYPES:
            raise ValueError("不支持的消息类型：%s" % self.msgtype)

        self.log.info("企业微信通知启动，执行功能：%s" % FUNC_LABELS.get(self.func, self.func))
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
