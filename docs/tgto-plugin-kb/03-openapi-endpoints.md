# TgtoDrive OpenAPI 接口索引

> 本文件由 `spec/tgto-openapi.json`（OpenAPI 3.0.3，`TgtoDrive OpenAPI` v1.0.0）自动生成，仅用于快速检索。
> 参数以容器内导出的规范与实际接口校验为准；标注 `inferred` / `generic` 的请求模型来自构建时静态分析，
> **不是完整人工校验的模型**，未声明的 JSON 字段仍可能有效。

- 接口总数：**212**
- 分组数：**36**
- 鉴权：全局 `bearerAuth`（`Authorization: Bearer <TOKEN>`）；`webhookToken` 仅用于 Emby 深度删除回调
- 服务地址：规范内 `servers[0].url = "/"`，即当前服务地址（同容器常见为 `http://127.0.0.1:12366`）

## 标记说明

| `x-documentation-level` | 含义 |
| --- | --- |
| `documented` | 请求字段已人工核对 |
| `inferred` | 字段由静态分析推断，不保证包含全部必填条件 |
| `generic` | 未细化模型 |

路径参数以 `*` 结尾；请求体字段列出的是静态分析提取的字段名，`(必填)` 为规范声明。

---

## 115-self-share-strm

### `POST /api/115-self-share-strm/run`

- 用途：扫描 115 转存目录并生成自建分享
- 文档级别：`generic`

## 115-share-strm-invalid-cleaner

### `GET /api/115-share-strm-invalid-cleaner/config`

- 用途：读取 115 分享 STRM 清理配置
- 文档级别：`generic`

### `POST /api/115-share-strm-invalid-cleaner/config`

- 用途：保存 115 分享 STRM 清理配置
- 文档级别：`inferred`
- 请求体字段：`config`

### `GET /api/115-share-strm-invalid-cleaner/fs/list`

- 用途：浏览 STRM 清理扫描目录
- 文档级别：`inferred`
- 参数：`path`

### `GET /api/115-share-strm-invalid-cleaner/history`

- 用途：查询 STRM 失效检测历史
- 文档级别：`inferred`
- 参数：`page`, `page_size`, `state`, `trigger_source`

### `GET /api/115-share-strm-invalid-cleaner/history-detail`

- 用途：查询 STRM 检测历史详情
- 文档级别：`inferred`
- 参数：`id`

### `POST /api/115-share-strm-invalid-cleaner/run`

- 用途：启动 115 分享 STRM 失效检测
- 文档级别：`inferred`
- 请求体字段：`config`

### `POST /api/115-share-strm-invalid-cleaner/stop`

- 用途：停止 STRM 失效检测任务
- 文档级别：`inferred`
- 请求体字段：`task_id`

### `GET /api/115-share-strm-invalid-cleaner/task-status`

- 用途：查询 STRM 失效检测进度
- 文档级别：`inferred`
- 参数：`id`

## 115

### `POST /api/115/qr/login`

- 用途：完成 115 扫码登录
- 文档级别：`inferred`
- 请求体字段：`app`, `uid`

### `GET /api/115/qr/status`

- 用途：查询 115 扫码登录状态
- 文档级别：`inferred`
- 参数：`sign`, `time`, `uid`

### `GET /api/115/qr/token`

- 用途：获取 115 登录二维码凭据
- 文档级别：`generic`

## 123

### `POST /api/123/login/send-code`

- 用途：发送 123 云盘登录验证码
- 文档级别：`inferred`
- 请求体字段：`captcha`, `phone`, `phone_number`, `traceless`

### `GET /api/123/login/status`

- 用途：查询 123 云盘登录状态
- 文档级别：`generic`

### `POST /api/123/login/verify-code`

- 用途：完成 123 云盘短信登录
- 文档级别：`inferred`
- 请求体字段：`code`, `login_ticket`, `verification_code`

## 189

### `POST /api/189/qr/cancel`

- 用途：取消天翼云盘扫码登录
- 文档级别：`inferred`
- 请求体字段：`login_ticket`

### `POST /api/189/qr/start`

- 用途：创建天翼云盘登录二维码
- 文档级别：`generic`

### `POST /api/189/qr/status`

- 用途：查询天翼云盘扫码登录结果
- 文档级别：`inferred`
- 请求体字段：`login_ticket`

## ai-media-parser

### `POST /api/ai-media-parser/cache/clear`

- 用途：清空 AI 媒体识别缓存
- 文档级别：`generic`

### `GET /api/ai-media-parser/config`

- 用途：读取 AI 媒体识别配置
- 文档级别：`generic`

### `POST /api/ai-media-parser/config`

- 用途：保存 AI 媒体识别配置
- 文档级别：`inferred`
- 请求体字段：`config`

### `POST /api/ai-media-parser/test-connection`

- 用途：测试 AI 识别服务连接
- 文档级别：`inferred`
- 请求体字段：`config`

## bot-commands

### `GET /api/bot-commands`

- 用途：读取 Telegram 机器人命令
- 文档级别：`generic`

### `POST /api/bot-commands`

- 用途：保存 Telegram 机器人命令
- 文档级别：`inferred`
- 请求体字段：`commands`

## directory-selector

### `GET /api/directory-selector/list`

- 用途：浏览网盘子目录
- 文档级别：`inferred`
- 参数：`parent_id`, `provider`

### `GET /api/directory-selector/resolve`

- 用途：解析网盘目录名称和路径
- 文档级别：`inferred`
- 参数：`folder_id`, `provider`

## emby-cover-generator

### `POST /api/emby-cover-generator/config`

- 用途：保存媒体库封面生成设置
- 文档级别：`inferred`
- 请求体字段：`config`

### `POST /api/emby-cover-generator/generate`

- 用途：启动 Emby 媒体库封面生成
- 文档级别：`inferred`
- 请求体字段：`generator_config`, `libraries`

### `GET /api/emby-cover-generator/libraries`

- 用途：获取封面生成用媒体库
- 文档级别：`generic`

### `GET /api/emby-cover-generator/task-status`

- 用途：查询媒体库封面生成进度
- 文档级别：`inferred`
- 参数：`id`

## emby-metadata-cleaner

### `POST /api/emby-metadata-cleaner/clean`

- 用途：清理 Emby 残余元数据
- 文档级别：`inferred`
- 请求体字段：`path`

### `GET /api/emby-metadata-cleaner/fs/list`

- 用途：浏览元数据清理目录
- 文档级别：`inferred`
- 参数：`path`

### `POST /api/emby-metadata-cleaner/pick-folder`

- 用途：打开服务器本地目录选择器
- 文档级别：`generic`

### `POST /api/emby-metadata-cleaner/preview`

- 用途：预览 Emby 残余元数据
- 文档级别：`inferred`
- 请求体字段：`path`

## emby

### `GET /api/emby/config`

- 用途：读取 Emby 看板运行配置
- 文档级别：`generic`

### `GET /api/emby/continue`

- 用途：查询 Emby 继续观看列表
- 文档级别：`inferred`
- 参数：`user_id`

### `GET /api/emby/dashboard`

- 用途：获取 Emby 看板统计
- 文档级别：`inferred`
- 参数：`user_id`

### `GET /api/emby/dashboard_config`

- 用途：读取 Emby 看板专用设置
- 文档级别：`generic`

### `POST /api/emby/dashboard_config/clear`

- 用途：清除 Emby 看板连接设置
- 文档级别：`generic`

### `POST /api/emby/dashboard_config/save`

- 用途：保存 Emby 看板连接设置
- 文档级别：`inferred`
- 请求体字段：`api_key`, `host`, `library_user_name`

### `POST /api/emby/dashboard_config/test`

- 用途：测试 Emby 看板连接
- 文档级别：`inferred`
- 请求体字段：`api_key`, `host`

### `GET /api/emby/image/{item_id}/primary`

- 用途：获取 Emby 主海报图片
- 文档级别：`inferred`
- 参数：`item_id*`, `thumb`

### `GET /api/emby/latest`

- 用途：查询 Emby 最近入库媒体
- 文档级别：`inferred`
- 参数：`limit`

### `GET /api/emby/libraries`

- 用途：查询 Emby 媒体库统计
- 文档级别：`generic`

### `GET /api/emby/live`

- 用途：查询 Emby 正在播放的会话
- 文档级别：`generic`

### `GET /api/emby/recent`

- 用途：查询 Emby 最近播放记录
- 文档级别：`inferred`
- 参数：`user_id`

### `POST /api/emby/refresh_cache`

- 用途：刷新 Emby 看板缓存
- 文档级别：`generic`

### `GET /api/emby/top_users_list`

- 用途：查询 Emby 活跃用户排行
- 文档级别：`generic`

### `GET /api/emby/trend`

- 用途：查询 Emby 播放趋势
- 文档级别：`inferred`
- 参数：`dimension`, `user_id`

### `GET /api/emby/users`

- 用途：获取 Emby 用户列表
- 文档级别：`generic`

### `POST /api/emby/webhook/deep_delete`

- 用途：接收 Emby 媒体深度删除通知
- 文档级别：`inferred`
- 参数：`token`

### `GET /api/emby/webhook/deep_delete_info`

- 用途：读取 Emby 深度删除回调配置
- 文档级别：`generic`

## emby_proxy

### `GET /api/emby_proxy/config`

- 用途：读取 Emby 反向代理规则
- 文档级别：`generic`

### `POST /api/emby_proxy/config/clear`

- 用途：清空 Emby 反向代理规则
- 文档级别：`generic`

### `POST /api/emby_proxy/config/delete_one`

- 用途：删除一条 Emby 反向代理规则
- 文档级别：`inferred`
- 请求体字段：`id`

### `POST /api/emby_proxy/config/save`

- 用途：保存全部 Emby 反向代理规则
- 文档级别：`inferred`
- 请求体字段：`rules`

### `POST /api/emby_proxy/config/save_one`

- 用途：新增或更新 Emby 代理规则
- 文档级别：`inferred`
- 请求体字段：`rule`

### `POST /api/emby_proxy/config/test`

- 用途：测试 Emby 代理目标连接
- 文档级别：`inferred`
- 请求体字段：`api_key`, `host`, `mode`, `proxy_type`, `type`

### `POST /api/emby_proxy/config/toggle`

- 用途：切换 Emby 代理规则启停
- 文档级别：`inferred`
- 请求体字段：`enabled`, `id`

### `GET /api/emby_proxy/invites`

- 用途：查询 Emby 邀请记录
- 文档级别：`inferred`
- 参数：`id`, `limit`

### `POST /api/emby_proxy/invites/create`

- 用途：创建 Emby 注册邀请
- 文档级别：`inferred`
- 请求体字段：`all_libraries`, `count`, `duration_seconds`, `id`, `library_ids`, `note`, `rule_id`

### `GET /api/emby_proxy/invites/libraries`

- 用途：获取邀请可授权的媒体库
- 文档级别：`inferred`
- 参数：`id`

### `POST /api/emby_proxy/invites/renew`

- 用途：续期 Emby 邀请关联用户
- 文档级别：`inferred`
- 请求体字段：`duration_seconds`, `invite_id`, `rule_id`

### `POST /api/emby_proxy/invites/revoke`

- 用途：撤销 Emby 注册邀请
- 文档级别：`inferred`
- 请求体字段：`invite_id`, `rule_id`

### `GET /api/emby_proxy/playback_records`

- 用途：查询 Emby 代理播放记录
- 文档级别：`inferred`
- 参数：`id`, `page`, `page_size`

## env

### `GET /api/env`

- 用途：读取项目配置项
- 文档级别：`generic`

### `POST /api/env`

- 用途：保存项目配置并触发重启
- 文档级别：`inferred`

## guangya

### `POST /api/guangya/gcid-export`

- 用途：生成光鸭目录秒传 JSON
- 文档级别：`inferred`
- 请求体字段：`folderId`, `folderName`, `folder_id`, `folder_name`

### `POST /api/guangya/login/send-code`

- 用途：发送光鸭主账号登录验证码
- 文档级别：`inferred`
- 请求体字段：`phone`, `phone_number`

### `POST /api/guangya/login/verify-code`

- 用途：完成光鸭主账号短信登录
- 文档级别：`inferred`
- 请求体字段：`code`, `verification_code`

### `POST /api/guangya/media-probe-account/login/send-code`

- 用途：发送光鸭媒体信息小号验证码
- 文档级别：`inferred`
- 请求体字段：`phone`, `phone_number`

### `POST /api/guangya/media-probe-account/login/verify-code`

- 用途：登录光鸭媒体信息小号
- 文档级别：`inferred`
- 请求体字段：`code`, `verification_code`

### `GET /api/guangya/media-probe-account/status`

- 用途：查询光鸭媒体信息小号状态
- 文档级别：`generic`

### `POST /api/guangya/media-probe-account/token/clear`

- 用途：清除光鸭媒体信息小号凭据
- 文档级别：`generic`

### `POST /api/guangya/media-probe-account/token/refresh`

- 用途：刷新光鸭媒体信息小号凭据
- 文档级别：`generic`

### `POST /api/guangya/media-probe-account/token/validate`

- 用途：校验光鸭媒体信息小号凭据
- 文档级别：`generic`

### `POST /api/guangya/token/clear`

- 用途：清除光鸭主账号凭据
- 文档级别：`generic`

### `POST /api/guangya/token/refresh`

- 用途：刷新光鸭主账号凭据
- 文档级别：`generic`

### `GET /api/guangya/token/status`

- 用途：查询光鸭云盘登录状态
- 文档级别：`generic`

### `POST /api/guangya/token/validate`

- 用途：校验光鸭主账号凭据
- 文档级别：`generic`

## logs

### `GET /api/logs`

- 用途：读取项目运行日志
- 文档级别：`inferred`
- 参数：`offset`

### `GET /api/logs/download`

- 用途：下载项目日志文件
- 文档级别：`generic`

## media

### `GET /api/media/actors`

- 用途：浏览热门演员
- 文档级别：`inferred`
- 参数：`force`, `page`

### `GET /api/media/actors/{actor_id}/works`

- 用途：查询演员作品
- 文档级别：`inferred`
- 参数：`actor_id*`, `force`

### `GET /api/media/anime/{source}`

- 用途：浏览动漫内容
- 文档级别：`inferred`
- 参数：`source*`, `force`, `genre`, `page`, `prefetch`, `q`, `region`, `sort`, `wait`, `year`

### `GET /api/media/calendar`

- 用途：查询追剧日历
- 文档级别：`inferred`
- 参数：`days`, `force`, `kind`

### `GET /api/media/capabilities`

- 用途：查询影视资源功能能力
- 文档级别：`generic`

### `GET /api/media/details/tmdb/tv/{external_id}/season/{season_number}`

- 用途：查询电视剧某季的集数详情
- 文档级别：`inferred`
- 参数：`external_id*`, `season_number*`, `force`

### `GET /api/media/details/{source}/{entity_type}/{external_id}`

- 用途：查询影视或演员详情
- 文档级别：`inferred`
- 参数：`source*`, `entity_type*`, `external_id*`, `force`

### `GET /api/media/discover/{source}`

- 用途：浏览影视片库
- 文档级别：`inferred`
- 参数：`source*`, `force`, `genre`, `media_type`, `page`, `prefetch`, `region`, `sort`, `wait`, `year`

### `POST /api/media/emby/cards`

- 用途：查询影视条目的 Emby 入库状态
- 文档级别：`inferred`
- 请求体字段：`items`

### `POST /api/media/emby/test`

- 用途：测试影视发现的 Emby 连接
- 文档级别：`inferred`
- 请求体字段：`media_emby`

### `POST /api/media/emby/tv-progress/preheat`

- 用途：预热电视剧观看进度元数据
- 文档级别：`inferred`
- 请求体字段：`priority`, `tmdb_ids`

### `POST /api/media/guanying/captcha`

- 用途：获取观影登录验证码
- 文档级别：`inferred`
- 请求体字段：`attempt_id`

### `POST /api/media/guanying/captcha/verify`

- 用途：提交观影验证码结果
- 文档级别：`inferred`
- 请求体字段：`attempt_id`, `points`

### `POST /api/media/guanying/login`

- 用途：登录观影资源服务
- 文档级别：`inferred`
- 请求体字段：`attempt_id`, `password`, `username`

### `POST /api/media/guanying/relogin`

- 用途：恢复观影登录状态
- 文档级别：`inferred`
- 请求体字段：`attempt_id`

### `DELETE /api/media/guanying/session`

- 用途：清除观影登录状态
- 文档级别：`generic`

### `POST /api/media/guanying/test`

- 用途：测试观影登录是否有效
- 文档级别：`generic`

### `GET /api/media/providers`

- 用途：获取影视来源与转存目标
- 文档级别：`generic`

### `GET /api/media/rankings/{provider}`

- 用途：查询影视榜单
- 文档级别：`inferred`
- 参数：`provider*`, `force`, `media_type`, `page`, `region`

### `POST /api/media/resources/copy-link`

- 用途：获取影视资源分享链接
- 文档级别：`inferred`
- 请求体字段：`provider`, `slug`, `source`

### `POST /api/media/resources/offline`

- 用途：提交影视资源离线下载
- 文档级别：`inferred`
- 请求体字段：`link`, `provider`, `source`, `text`

### `POST /api/media/resources/search`

- 用途：检索影视可用资源
- 文档级别：`inferred`
- 请求体字段：`aliases`, `episode`, `media_type`, `preferences`, `provider`, `season`, `sources`, `title`, `tmdb_id`, `year`

### `POST /api/media/resources/transfer`

- 用途：将影视资源转存到网盘
- 文档级别：`inferred`
- 请求体字段：`candidate_item_id`, `enforce_points_limit`, `max_points`, `provider`, `share_url`, `slug`, `source`

### `GET /api/media/search`

- 用途：搜索影视和演员资料
- 文档级别：`inferred`
- 参数：`media_type`, `page`, `prefetch`, `q`

### `GET /api/media/settings`

- 用途：读取影视发现基础配置
- 文档级别：`inferred`
- 请求体字段：`check_interval_minutes`, `emby_missing_scan_interval_minutes`, `guanying`, `max_points`, `media_emby`, `media_transfer_targets`, `ranking_virtual_libraries`, `target_provider`

### `PUT /api/media/settings`

- 用途：保存影视发现基础配置
- 文档级别：`inferred`
- 请求体字段：`check_interval_minutes`, `emby_missing_scan_interval_minutes`, `guanying`, `max_points`, `media_emby`, `media_transfer_targets`, `ranking_virtual_libraries`, `target_provider`

## music-organize

### `POST /api/music-organize/stop`

- 用途：停止音乐整理任务
- 文档级别：`inferred`
- 请求体字段：`source`

## notify-bots

### `GET /api/notify-bots`

- 用途：读取 Telegram 通知机器人配置
- 文档级别：`generic`

### `POST /api/notify-bots`

- 用途：保存 Telegram 通知机器人配置
- 文档级别：`generic`

## openapi

### `GET /api/openapi/spec`

- 用途：获取当前服务 OpenAPI 规范
- 文档级别：`generic`

## organize-history

### `GET /api/organize-history`

- 用途：查询网盘整理历史
- 文档级别：`inferred`
- 参数：`keyword`, `limit`, `page`, `source`, `status`

### `POST /api/organize-history/clear`

- 用途：清空整理历史记录
- 文档级别：`inferred`
- 请求体字段：`clear_all`, `end_date`, `source`, `start_date`

### `POST /api/organize-history/delete`

- 用途：删除整理记录关联的文件
- 文档级别：`inferred`
- 请求体字段：`record_id`, `record_ids`

### `GET /api/organize-history/delete-task-status`

- 用途：查询整理文件删除任务进度
- 文档级别：`inferred`
- 参数：`id`

### `GET /api/organize-history/detail`

- 用途：查询一条整理记录详情
- 文档级别：`inferred`
- 参数：`record_id`

### `POST /api/organize-history/recognize-test`

- 用途：测试文件名的 TMDB 识别
- 文档级别：`inferred`
- 请求体字段：`name`, `parent_tmdb_id`, `record_id`, `sibling_filenames`, `source`, `source_path`, `source_root_path`

### `POST /api/organize-history/reorganize`

- 用途：重新整理或回退媒体改名
- 文档级别：`inferred`
- 请求体字段：`media_type`, `record_id`, `record_ids`, `selected_title`, `title`, `tmdb_id`

### `GET /api/organize-history/reorganize-task-status`

- 用途：查询重新整理或改名回退进度
- 文档级别：`inferred`
- 参数：`id`

### `POST /api/organize-history/run`

- 用途：立即运行网盘整理
- 文档级别：`inferred`
- 请求体字段：`confirmed`, `source`

## pikpak

### `GET /api/pikpak/captcha/callback/{state}`

- 用途：接收 PikPak 验证码回调
- 文档级别：`inferred`
- 参数：`state*`, `captcha_token`, `expires_in`

### `GET /api/pikpak/captcha/status`

- 用途：查询 PikPak 验证码处理状态
- 文档级别：`generic`

### `POST /api/pikpak/login`

- 用途：登录 PikPak 云盘
- 文档级别：`inferred`
- 请求体字段：`account`, `captcha_token`, `password`, `username`

### `POST /api/pikpak/token/clear`

- 用途：清除 PikPak 登录凭据
- 文档级别：`generic`

### `POST /api/pikpak/token/refresh`

- 用途：刷新 PikPak 登录凭据
- 文档级别：`generic`

### `GET /api/pikpak/token/status`

- 用途：查询 PikPak 登录状态
- 文档级别：`generic`

### `POST /api/pikpak/token/validate`

- 用途：校验 PikPak 登录凭据
- 文档级别：`generic`

## proxy

### `GET /api/proxy/image/{item_id}/primary`

- 用途：获取 Emby 海报图片（兼容入口）
- 文档级别：`inferred`
- 参数：`item_id*`, `thumb`

## proxy_settings

### `GET /api/proxy_settings`

- 用途：读取全局代理和机器人设置
- 文档级别：`generic`

### `POST /api/proxy_settings/save`

- 用途：保存全局代理和机器人设置
- 文档级别：`inferred`
- 请求体字段：`admin_user_id`, `bot_token`, `check_interval`, `proxy`

### `POST /api/proxy_settings/test`

- 用途：测试网络代理连通性
- 文档级别：`inferred`
- 请求体字段：`proxy`

### `POST /api/proxy_settings/test_tg`

- 用途：发送 Telegram 机器人测试消息
- 文档级别：`inferred`
- 请求体字段：`admin_user_id`, `bot_token`, `proxy`

## pttransfer

### `GET /api/pttransfer/records`

- 用途：查询 PT 转存记录
- 文档级别：`inferred`
- 参数：`limit`

## re0

### `DELETE /api/re0/authorization`

- 用途：清除 RE0 主账号授权
- 文档级别：`generic`

### `GET /api/re0/authorize`

- 用途：打开 RE0 主账号授权流程
- 文档级别：`generic`

### `GET /api/re0/checkin/config`

- 用途：读取 RE0 自动签到配置
- 文档级别：`generic`

### `PUT /api/re0/checkin/config`

- 用途：保存 RE0 自动签到配置
- 文档级别：`generic`

### `GET /api/re0/status`

- 用途：查询 RE0 主账号授权状态
- 文档级别：`generic`

### `GET /api/re0/subaccounts`

- 用途：查询 RE0 小号列表
- 文档级别：`inferred`
- 参数：`refresh`

### `POST /api/re0/subaccounts`

- 用途：新增 RE0 小号配置
- 文档级别：`inferred`
- 请求体字段：`label`

### `DELETE /api/re0/subaccounts/{account_id}`

- 用途：删除 RE0 小号
- 文档级别：`generic`
- 参数：`account_id*`

### `PATCH /api/re0/subaccounts/{account_id}`

- 用途：更新 RE0 小号配置
- 文档级别：`inferred`
- 参数：`account_id*`
- 请求体字段：`enabled`, `label`

### `POST /api/re0/subaccounts/{account_id}`

- 用途：更新 RE0 小号配置（POST 入口）
- 文档级别：`inferred`
- 参数：`account_id*`
- 请求体字段：`enabled`, `label`

### `DELETE /api/re0/subaccounts/{account_id}/authorization`

- 用途：清除 RE0 小号授权
- 文档级别：`generic`
- 参数：`account_id*`

### `GET /api/re0/subaccounts/{account_id}/authorize`

- 用途：打开 RE0 小号授权流程
- 文档级别：`generic`
- 参数：`account_id*`

## save_json

### `POST /api/save_json`

- 用途：将 JSON 文件清单导入指定网盘目录
- 文档级别：`inferred`
- 请求体字段：`commonPath`, `files`, `target_dir_id`(必填)

## ssh

### `POST /api/ssh/connect`

- 用途：建立 SSH 终端连接
- 文档级别：`inferred`
- 请求体字段：`host`, `password`, `port`, `sid`, `username`

### `POST /api/ssh/input`

- 用途：向 SSH 终端发送输入
- 文档级别：`inferred`
- 请求体字段：`data`, `sid`

### `GET /api/ssh/output`

- 用途：读取 SSH 终端输出
- 文档级别：`inferred`
- 参数：`sid`

## stats

### `GET /api/stats/continue`

- 用途：查询继续观看列表（兼容入口）
- 文档级别：`inferred`
- 参数：`user_id`

### `GET /api/stats/dashboard`

- 用途：查询看板统计（兼容入口）
- 文档级别：`inferred`
- 参数：`user_id`

### `GET /api/stats/latest`

- 用途：查询最近入库媒体（兼容入口）
- 文档级别：`inferred`
- 参数：`limit`

### `GET /api/stats/libraries`

- 用途：查询媒体库统计（兼容入口）
- 文档级别：`generic`

### `GET /api/stats/live`

- 用途：查询正在播放会话（兼容入口）
- 文档级别：`generic`

### `GET /api/stats/recent`

- 用途：查询最近播放记录（兼容入口）
- 文档级别：`inferred`
- 参数：`user_id`

### `GET /api/stats/top_users_list`

- 用途：查询活跃用户排行（兼容入口）
- 文档级别：`generic`

### `GET /api/stats/trend`

- 用途：查询播放趋势（兼容入口）
- 文档级别：`inferred`
- 参数：`dimension`, `user_id`

## strm-sync

### `POST /api/strm-sync/run`

- 用途：立即同步网盘 STRM
- 文档级别：`inferred`
- 请求体字段：`source`

## tg-transfer

### `POST /api/tg-transfer/test`

- 用途：测试 Telegram 最新消息转发
- 文档级别：`inferred`
- 请求体字段：`command_head`, `source_id`, `spoiler`, `target_id`

## tmdb-regex-rules

### `GET /api/tmdb-regex-rules/config`

- 用途：读取 TMDB 正则识别规则
- 文档级别：`generic`

### `POST /api/tmdb-regex-rules/config`

- 用途：保存 TMDB 正则识别规则
- 文档级别：`inferred`
- 请求体字段：`rules`

### `GET /api/tmdb-regex-rules/search-tmdb`

- 用途：为正则规则搜索 TMDB 内容
- 文档级别：`inferred`
- 参数：`include_adult`, `page`, `query`, `type`

## toolbox

### `GET /api/toolbox/123-api-rate-limit/config`

- 用途：读取 123 云盘 API 限速配置
- 文档级别：`generic`

### `POST /api/toolbox/123-api-rate-limit/config`

- 用途：保存 123 云盘 API 限速配置
- 文档级别：`inferred`
- 请求体字段：`config`

### `GET /api/toolbox/custom-release-groups/config`

- 用途：读取自定义发布组配置
- 文档级别：`generic`

### `POST /api/toolbox/custom-release-groups/config`

- 用途：保存自定义发布组规则
- 文档级别：`inferred`
- 请求体字段：`config`

### `GET /api/toolbox/marketplace`

- 用途：浏览 GitHub 插件市场
- 文档级别：`inferred`

### `POST /api/toolbox/marketplace/install`

- 用途：安装或更新市场插件
- 文档级别：`documented`
- 请求体字段：`id`(必填), `replace`, `sha256`(必填), `source_id`, `trusted`(必填), `version`(必填)

### `POST /api/toolbox/marketplace/refresh`

- 用途：刷新 GitHub 插件市场目录
- 文档级别：`inferred`

### `PUT /api/toolbox/marketplace/source`

- 用途：配置 GitHub 插件市场来源
- 文档级别：`documented`
- 请求体字段：`path`, `ref`, `repository`

### `POST /api/toolbox/marketplace/sources`

- 用途：添加插件市场来源
- 文档级别：`documented`
- 请求体字段：`path`, `ref`, `repository`(必填)

### `DELETE /api/toolbox/marketplace/sources/{source_id}`

- 用途：移除指定插件市场来源
- 文档级别：`inferred`
- 参数：`source_id*`

### `PUT /api/toolbox/marketplace/sources/{source_id}`

- 用途：编辑指定插件市场来源
- 文档级别：`documented`
- 参数：`source_id*`
- 请求体字段：`path`, `ref`, `repository`(必填)

### `GET /api/toolbox/plugins`

- 用途：查询已安装插件和导入能力
- 文档级别：`inferred`

### `GET /api/toolbox/plugins/ai-development-prompt`

- 用途：获取插件 AI 开发提示词
- 文档级别：`generic`

### `GET /api/toolbox/plugins/development-guide`

- 用途：获取插件开发指南
- 文档级别：`generic`

### `GET /api/toolbox/plugins/example.py`

- 用途：下载单文件 Python 插件示例
- 文档级别：`generic`

### `GET /api/toolbox/plugins/example.zip`

- 用途：下载 ZIP 插件开发示例
- 文档级别：`generic`

### `POST /api/toolbox/plugins/import`

- 用途：导入或更新本地 Python 插件
- 文档级别：`documented`

### `GET /api/toolbox/plugins/jobs/{job_id}`

- 用途：查询插件任务结果和日志
- 文档级别：`inferred`
- 参数：`job_id*`

### `GET /api/toolbox/plugins/marketplace-guide`

- 用途：获取插件市场使用和发布指南
- 文档级别：`generic`

### `GET /api/toolbox/plugins/schedules`

- 用途：查询插件定时计划
- 文档级别：`inferred`

### `POST /api/toolbox/plugins/schedules`

- 用途：新增插件定时计划
- 文档级别：`documented`
- 请求体字段：`cron`(必填), `enabled`, `name`, `params`, `plugin_id`(必填)

### `POST /api/toolbox/plugins/schedules/preview`

- 用途：预览插件 cron 执行时间
- 文档级别：`documented`
- 请求体字段：`cron`(必填)

### `DELETE /api/toolbox/plugins/schedules/{schedule_id}`

- 用途：删除插件定时计划
- 文档级别：`inferred`
- 参数：`schedule_id*`

### `PATCH /api/toolbox/plugins/schedules/{schedule_id}`

- 用途：启停插件定时计划
- 文档级别：`documented`
- 参数：`schedule_id*`
- 请求体字段：`enabled`(必填)

### `PUT /api/toolbox/plugins/schedules/{schedule_id}`

- 用途：更新插件定时计划
- 文档级别：`documented`
- 参数：`schedule_id*`
- 请求体字段：`cron`(必填), `enabled`, `name`, `params`, `plugin_id`(必填)

### `DELETE /api/toolbox/plugins/{plugin_id}`

- 用途：卸载 Python 插件
- 文档级别：`inferred`
- 参数：`plugin_id*`

### `PATCH /api/toolbox/plugins/{plugin_id}`

- 用途：启用或停用 Python 插件
- 文档级别：`documented`
- 参数：`plugin_id*`
- 请求体字段：`enabled`(必填)

### `GET /api/toolbox/plugins/{plugin_id}/assets/{filename}`

- 用途：读取插件包内图片
- 文档级别：`inferred`
- 参数：`plugin_id*`, `filename*`

### `GET /api/toolbox/plugins/{plugin_id}/files/{filename}`

- 用途：读取插件生成的图片
- 文档级别：`inferred`
- 参数：`plugin_id*`, `filename*`

### `POST /api/toolbox/plugins/{plugin_id}/run`

- 用途：提交 Python 插件运行任务
- 文档级别：`documented`
- 参数：`plugin_id*`
- 请求体字段：`params`, `save_settings`

### `DELETE /api/toolbox/plugins/{plugin_id}/settings`

- 用途：清除插件已保存设置
- 文档级别：`inferred`
- 参数：`plugin_id*`

### `GET /api/toolbox/plugins/{plugin_id}/settings`

- 用途：读取插件已保存设置
- 文档级别：`inferred`
- 参数：`plugin_id*`

### `PUT /api/toolbox/plugins/{plugin_id}/settings`

- 用途：保存插件表单设置
- 文档级别：`documented`
- 参数：`plugin_id*`
- 请求体字段：`params`(必填)

### `GET /api/toolbox/tg-scheduled-sender/config`

- 用途：读取 Telegram 定时发送配置
- 文档级别：`generic`

### `POST /api/toolbox/tg-scheduled-sender/config`

- 用途：保存 Telegram 定时发送任务
- 文档级别：`inferred`
- 请求体字段：`config`

### `GET /api/toolbox/tmdb/config`

- 用途：读取 TMDB 连接和识别设置
- 文档级别：`generic`

### `POST /api/toolbox/tmdb/config`

- 用途：保存 TMDB 连接和识别设置
- 文档级别：`inferred`
- 请求体字段：`config`

## transfer-history

### `GET /api/transfer-history`

- 用途：查询网盘转存历史
- 文档级别：`inferred`
- 参数：`keyword`, `limit`, `page`, `source`, `status`

## users

### `GET /api/users`

- 用途：获取 Emby 用户（兼容入口）
- 文档级别：`generic`

## visual-filter

### `GET /api/visual-filter/config`

- 用途：读取可视化筛选规则
- 文档级别：`inferred`
- 参数：`scene`

### `POST /api/visual-filter/config`

- 用途：保存可视化筛选规则
- 文档级别：`inferred`
- 请求体字段：`advanced_raw_regex`, `all_mode`, `parse_mode`, `raw_regex`, `rules`, `scene`

### `POST /api/visual-filter/config/sync`

- 用途：同步筛选规则到其他场景
- 文档级别：`inferred`
- 请求体字段：`source_raw_regex`, `source_scene`, `target_scene`

### `GET /api/visual-filter/tmdb/search`

- 用途：为筛选规则搜索 TMDB 条目
- 文档级别：`inferred`
- 参数：`include_adult`, `language`, `page`, `query`, `type`

## xunlei

### `POST /api/xunlei/login/send-code`

- 用途：发送迅雷云盘登录验证码
- 文档级别：`inferred`
- 请求体字段：`phone`, `phone_number`

### `POST /api/xunlei/login/verify-code`

- 用途：完成迅雷云盘短信登录
- 文档级别：`inferred`
- 请求体字段：`code`, `verification_code`

### `POST /api/xunlei/token/clear`

- 用途：清除迅雷云盘登录凭据
- 文档级别：`generic`

### `POST /api/xunlei/token/refresh`

- 用途：刷新迅雷云盘登录凭据
- 文档级别：`generic`

### `GET /api/xunlei/token/status`

- 用途：查询迅雷云盘登录状态
- 文档级别：`generic`

### `POST /api/xunlei/token/validate`

- 用途：校验迅雷云盘登录凭据
- 文档级别：`generic`
