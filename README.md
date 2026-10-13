# TgtoDrive 第三方插件市场

面向 **TgtoDrive**「实用工具 → 我的插件 → 插件市场」的第三方插件源仓库。

本仓库同时满足两个身份：它是一个标准的 GitHub 开源仓库，也是一个可直接被 TgtoDrive 读取的**插件市场目录**。把本仓库地址填入 TgtoDrive 的「插件市场 → 来源设置」，即可浏览、安装并自动检查更新这里发布的插件，无需另外的市场服务器。

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Plugins](https://img.shields.io/badge/plugins-1-informational)](#插件列表)
[![Protocol](https://img.shields.io/badge/plugin%20protocol-schema__version%201-informational)](#插件列表)

---

## 插件列表

| 插件 | 版本 | 说明 | 文档 |
| --- | --- | --- | --- |
| **药丸论坛签到**<br>`invites-signin` | 1.0.0 | 药丸论坛（invites.fun，Flarum）自动签到。Cookie 优先换取新会话后签到，失败自动回退用户名密码登录；支持仅查询签到状态、查看本地签到历史；结果经 TgtoDrive 已配置的**主通知机器人**推送，结果页内含运行日志窗口与「运行一次」按钮。 | [README](plugins/invites-signin/README.md) |

---

## 在 TgtoDrive 中使用

### 方式一：作为插件市场来源（推荐）

1. 打开「实用工具 → 我的插件 → 插件市场」。
2. 点击「来源设置」，新增来源并填写：
   - **仓库**：本仓库的 `账号/仓库名`
   - **分支**：`main`
   - **目录路径**：`plugins.json`
3. 保存并刷新目录，即可看到上表中的插件。
4. 选择插件 → 查看来源、依赖与版本 → 确认信任后安装。
5. 后续更新同样在此操作，插件数据与设置会保留。

> 市场加载的是仓库根目录的 [`plugins.json`](plugins.json)，附件从固定 tag 的 GitHub Releases 下载（路径形如 `releases/download/<tag>/<文件名>`），不使用 `latest/download`。

### 方式二：手动导入

1. 下载目标版本的可导入产物（二选一）：
   - [**Releases**](../../releases) 页面的附件：`<插件 id>.py`（单文件）或 `<插件 id>.zip`（插件包）；
   - 或仓库内已提交的单文件版：[`dist/<插件 id>.py`](dist)。
2. 在 TgtoDrive 打开「实用工具 → 我的插件 → 导入插件」。
3. 选择文件，阅读并勾选信任确认项后导入。

> ⚠️ **不要直接导入 `plugins/<插件 id>/plugin.py`。** 它是插件包内入口，清单写在同一目录的 `plugin.json` 里；把源码入口当「Python 单文件」导入会被拒绝并提示 `Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典`。可导入的单文件由 `scripts/package_plugin.py` 在文件开头内联 `PLUGIN_MANIFEST` 后生成。
>
> 也可以自行构建：见下方 [本地构建](#本地构建)。

---

## 仓库结构

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/            # Issue 模板
│   └── workflows/
│       └── publish-plugin.yml     # 打包 → 发布 Release → 刷新 plugins.json
├── docs/
│   └── tgto-plugin-kb/            # TgtoDrive 插件开发参考资料存档
├── plugins/
│   └── invites-signin/            # 单个插件的源码目录
│       ├── plugin.json            # 插件清单
│       ├── plugin.py              # 插件入口（同步 run(params, context)）
│       └── README.md              # 插件使用文档
├── scripts/
│   ├── package_plugin.py          # 打包插件并计算 sha256 / size
│   └── build_marketplace.py       # 扫描 plugins/ 生成 plugins.json
├── dist/
│   └── invites-signin.py          # 单文件版产物（可直接导入；zip 不入库，随 Release 分发）
├── plugins.json                   # 插件市场目录 schema_version 1
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

约定：

- 每个插件位于 `plugins/<插件 id>/`，目录名与 `plugin.json` 中的 `id` 一致。
- 插件源码目录只放**源码与文档**；打包产物写入 `dist/`，通过 Release 分发。
  `dist/*.py`（单文件版）入库以便直接下载导入，`dist/*.zip` 不入库。
- 单文件版由 `scripts/package_plugin.py` 在文件开头**内联唯一的 `PLUGIN_MANIFEST` 字典字面量**；
  源码目录里的 `plugin.py` 不带清单，不能当作单文件导入。
- `docs/` 下为 TgtoDrive 官方文档与接口规范的开发参考存档，版权归 TgtoDrive 项目所有。

---

## 本地构建

无需任何第三方依赖，Python 3.9+ 即可：

```bash
# 打包 plugins/ 下全部插件到 dist/，并计算 sha256 与字节数
python scripts/package_plugin.py --all

# 只打包指定插件
python scripts/package_plugin.py --plugin invites-signin

# 依据 dist/ 产物生成/刷新 plugins.json
python scripts/build_marketplace.py --repo <账号>/<仓库名>
```

`build_marketplace.py` 在 GitHub Actions 中会从 `GITHUB_REPOSITORY` 环境变量自动获取仓库名，无需手动传入。

---

## 发布新版本

1. 在 `plugins/<id>/plugin.json` 中提升 `version`（保持 `id` 不变）。
2. 在 `CHANGELOG.md` 中记录本次变更。
3. 提交并推送。
4. 在 Actions 页面手动触发 **Publish plugin** 工作流，选择要发布的插件 id。
5. 工作流会打包、创建固定 tag 的 Release、上传附件，并刷新 `plugins.json` 中的 `download_url` / `sha256` / `size`。

发布约束（由 TgtoDrive 插件市场校验）：

- `plugins.json` 顶层必须是 `{"schema_version": 1, "plugins": [...]}`：
  `schema_version` 为整数 `1`，`plugins` 为数组且**最多 500 项**。
- `sha256` 必须是**最终附件的真实摘要**，`size` 必须是附件的真实字节数，均由脚本计算，不得手写。
- `version` 遵循 PEP 440，推荐 `1.0.0`；`id` 与 `version` 必须与插件内清单精确一致。
- 附件必须是 TgtoDrive 支持的单文件 `.py` 或插件包，且符合插件协议：
  单文件在顶层**有且仅有一次** `PLUGIN_MANIFEST = {...}` 字面量赋值。
- 打包为**确定性输出**：zip 使用 `ZIP_STORED` 且固定时间戳，相同源码在任何 Python 版本下
  都得到相同字节与 SHA-256，本地产物与 CI 产物哈希一致。

---

## 许可证

本项目以 **GNU General Public License v3.0** 发布，全文见 [LICENSE](LICENSE)。这是一项**强制要求**而非偏好，原因见下。

### 关于 `plugins/invites-signin`

该插件移植改写自 [thsrite/MoviePilot-Plugins](https://github.com/thsrite/MoviePilot-Plugins) 中的「药丸签到」插件（原作者 [@thsrite](https://github.com/thsrite)），该上游项目以 **GPL-3.0** 授权；由 **a2695154202** 适配为 TgtoDrive 插件。

本插件复用了上游的签到判定流程、Cookie 换会话策略、登录回退与重试逻辑，属于 GPL-3.0 定义的**衍生作品**。依据 GPL-3.0 的 copyleft 条款，本衍生作品必须以同样的 GPL-3.0 授权，并保留原作者署名——因此本仓库整体采用 GPL-3.0，不能改为 MIT 等宽松许可证。

原作者署名与移植说明同时保留在 [插件目录的 README](plugins/invites-signin/README.md) 与 [`plugin.json`](plugins/invites-signin/plugin.json) 的 `author` 字段中。

### 关于 `docs/`

`docs/tgto-plugin-kb/` 内的 TgtoDrive 插件开发提示词、开发指南与 OpenAPI 规范由 TgtoDrive 项目提供，版权归其所有，此处仅作离线开发参考存档。若需要最新版本，请在 TgtoDrive 容器内重新导出覆盖。

---

## 免责声明

本仓库插件以 TgtoDrive 当前服务账户的权限运行，可访问其网络与文件系统。**请仅导入你已审查或信任来源的代码。** 插件作者不对因使用本仓库内容导致的账号异常、数据丢失或其他损失承担责任。
