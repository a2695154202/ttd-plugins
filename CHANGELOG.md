# Changelog

本仓库所有插件的显著变更记录于此。

格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

---

## invites-signin · 药丸论坛签到

### [1.0.0] - 2026-10-13

首次发布。由 MoviePilot V2 插件「药丸签到」v3.0.1 移植至 TgtoDrive 插件协议（移植适配：a2695154202）。

**新增**

- 自动签到：Cookie 优先换取新的 Flarum 会话后签到，整条通道失败后回退「用户名 + 密码」登录签到。
- 独立功能项：仅用 Cookie 签到、仅用账号密码登录签到、仅查询签到状态、查看本地签到历史。
- 结果通知：签到成功 / 今日已签到 / 失败均通过 TgtoDrive 已配置的通知机器人推送。
- **通知机器人选择**：新增「通知机器人」下拉框，可从 TgtoDrive 已配置的机器人中指定用哪一个推送（`auto` 或列表第 1–8 个），选择随插件设置保存。
- **通知诊断功能**：新增「读取通知机器人列表」（`func=bots`，给出序号 / 名称 / 状态 / 掩码目标 / 来源对照表，并为每个可用机器人生成测试按钮）与「发送测试通知」（`func=test_notify`）。
- **连接方式可选**：除环境变量 `TGTO_OPENAPI_BASE_URL` / `TGTO_OPENAPI_TOKEN` 外，也可在插件「通知与接口」页直接填写地址与令牌。
- **通知目标识别增强**：支持列表、嵌套 `data.list`、扁平单机器人对象、`settings` 包裹等多种返回形态；所选序号缺失或条目缺少凭据时自动回退主机器人并在日志中说明。
- 运行日志窗口：结果页内嵌完整运行日志，同时输出到 TgtoDrive 运行日志。
- 「运行一次」按钮：以「执行功能」中选中的功能立即执行一次，并强制发送本次通知。
- 本地签到历史：保存于插件 `data_dir/history.json`，按 `history_days` 自动清理。

**协议适配**

- 移除原插件的 `BackgroundScheduler` + `CronTrigger`，改由 TgtoDrive「定时执行」配置 cron（推荐 `5 8 * * *`）。
- 移除对 MoviePilot 内部模块（`_PluginBase` / `settings` / `logger` / `NotificationType`）的依赖。
- 浏览器仿真由 `CloakBrowser` 改为容器已预装的 `curl_cffi` Chrome 指纹模式。
- 重试间隔单位由**分钟**改为**秒**，以适配插件超时限制。
- 不再把刷新后的 Cookie 回写配置；`flarum_session` 每次运行都从 `flarum_remember` 重新换取，凭据不落盘。

**已知限制**

- 通知依赖 TgtoDrive OpenAPI 的 `GET /api/notify-bots`（回退 `GET /api/proxy_settings`）读取已配置的机器人；该响应在规范中标记为 `generic`，字段名不做保证，插件采用启发式识别，读取不到时会在日志中给出明确提示。
- TgtoDrive 的插件清单为静态读取，下拉框选项无法按接口结果动态生成，因此「通知机器人」按列表序号选择，需要先点「刷新机器人列表」查看序号对照。详见插件 README。
