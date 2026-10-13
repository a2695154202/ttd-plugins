# 贡献指南

感谢你为本插件市场提交内容。本仓库既是普通开源仓库，也是 TgtoDrive 可直接读取的插件市场源，因此对目录结构与元数据有一致性要求。

---

## 报告问题

- **插件功能异常** → 使用 [Bug 反馈](issues/new?template=bug_report.yml) 模板，务必附上 TgtoDrive 中的运行日志与插件返回结果。
- **希望有新插件** → 使用 [插件请求](issues/new?template=plugin_request.yml) 模板。
- **安全问题** → 请勿公开提 Issue。若涉及凭据泄露或任意代码执行，请先私下联系维护者。

提交 Issue 时**不要**粘贴真实 Cookie、密码、OpenAPI Token 或机器人 Token。日志中的代理地址与 Token 请先打码。

---

## 新增插件

### 1. 目录结构

```text
plugins/<插件 id>/
├── plugin.json     # 必需，插件清单
├── plugin.py       # 必需，入口（文件名需与清单 entry 一致）
└── README.md       # 必需，面向用户的使用文档
```

- 目录名必须与 `plugin.json` 的 `id` 完全一致。
- 可以包含辅助 Python 模块与资源子目录，但都需要相对路径、正斜杠，且不得出现 `..`、绝对路径、软硬链接。
- 不要提交 `__pycache__`、虚拟环境、`settings.json` 或任何真实凭据。

### 2. 清单要求

`plugin.json` 为纯 JSON（无注释），关键约束：

| 字段 | 要求 |
| --- | --- |
| `schema_version` | 固定为整数 `1`。 |
| `id` | 匹配 `^[a-z][a-z0-9_-]{1,63}$`，避开 Windows 保留名；更新时**保持不变**。 |
| `version` | 非空字符串，≤ 50 字符，遵循 PEP 440，推荐 `1.0.0`。 |
| `name` | 非空，≤ 100 字符。 |
| `entry` | 包内 `.py` 相对路径，推荐 `plugin.py`，文件必须存在。 |
| `timeout` | 整数 1–86400，默认 60。 |
| `inputs` | 最多 50 项，可省略。 |

细化到每个输入项的约束、`ui` 组件协议、返回值与日志限制，见 [docs/tgto-plugin-kb/04-protocol-checklist.md](docs/tgto-plugin-kb/04-protocol-checklist.md)。

### 3. 入口要求

```python
def run(params, context):
    ...
```

- 必须是**同步**函数，接受两个位置实参；异步库在函数内用 `asyncio.run()` 调用。
- 每次运行都是新进程，全局变量不跨任务保留；不要在模块导入阶段做网络请求或写文件。
- 返回值必须可 JSON 序列化，且不超过 1 MiB。
- 不要把失败包装成成功返回；抛出带明确信息的 `ValueError` / `RuntimeError`。
- 长耗时任务通过插件 `timeout` 放宽，**不要**用 `sleep` 等待下一次执行。

### 4. 文档要求

插件 `README.md` 至少包含：功能说明、参数表、依赖、运行示例、写入的服务器路径、以及任何修改/删除行为。若需要定时执行，给出推荐 cron 与运行参数。

### 5. 许可证

- 若插件为**原创**，请与本仓库保持一致使用 GPL-3.0。
- 若插件**移植或改写自其他项目**，必须确认上游许可证兼容，并在插件 README 与 `plugin.json` 的 `author` 字段中保留原作者署名。
- 上游为 GPL 系时，衍生作品**必须**继续以 GPL 系授权，不能改为 MIT 等宽松许可证。

---

## 提交前自检

```bash
python scripts/package_plugin.py --plugin <插件 id>
python scripts/build_marketplace.py --repo <账号>/<仓库名>
```

脚本会校验清单字段、打包产物并重算哈希。请确认：

- [ ] `python -m json.tool plugins/<id>/plugin.json` 通过。
- [ ] `python -m py_compile plugins/<id>/plugin.py` 通过。
- [ ] `plugin.json` 的 `id` / `version` 与 `CHANGELOG.md` 中的记录一致。
- [ ] README 已更新参数表。
- [ ] 未提交任何凭据、`dist/` 产物或 `settings.json`。

---

## 发布流程

维护者按以下步骤发布：

1. 合并包含版本变更的 PR。
2. 更新 `CHANGELOG.md`。
3. 在 Actions 中手动触发 **Publish plugin**，选择插件 id。
4. 工作流打包、创建固定 tag 的 Release、上传附件，并刷新 `plugins.json` 的 `download_url` / `sha256` / `size`。

`plugins.json` 中的哈希与体积**只能由脚本计算**，禁止手写或推测；重新打包后必须重新计算。
