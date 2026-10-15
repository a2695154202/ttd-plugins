# TgtoDrive 第三方插件市场

面向 **TgtoDrive**「实用工具 → 我的插件 → 插件市场」的第三方插件源仓库。

本仓库同时满足两个身份：它是一个标准的 GitHub 开源仓库，也是一个可直接被 TgtoDrive 读取的**插件市场目录**。把本仓库地址填入 TgtoDrive 的「插件市场 → 来源设置」，即可浏览、安装并自动检查更新这里发布的插件，无需另外的市场服务器。

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](LICENSE)
[![Plugins](https://img.shields.io/badge/plugins-5-informational)](#插件列表)
[![Protocol](https://img.shields.io/badge/plugin%20protocol-schema__version%201-informational)](#插件列表)

---

## 插件列表

| 插件 | 版本 | 说明 | 文档 |
| --- | --- | --- | --- |
| **药丸论坛签到**<br>`invites-signin` | 1.0.3 | 药丸论坛（invites.fun）自动签到，结果可通知到 TgtoDrive 机器人或企业微信。 | [README](plugins/invites-signin/README.md) |
| **企业微信通知**<br>`wecom-notify` | 1.0.1 | 向企业微信发送应用消息（文本 / 图文），可被其他插件调用。 | [README](plugins/wecom-notify/README.md) |
| **微信通知调用示例**<br>`wecom-call-demo` | 1.0.1 | 演示插件互相调用：调用「企业微信通知」插件发送消息。 | [README](plugins/wecom-call-demo/README.md) |
| **TTD每日推送**<br>`ttd-daily-digest` | 1.0.1 | 把 TgtoDrive 的媒体库数据汇总成一条日报，推送到 Telegram 或企业微信。 | [README](plugins/ttd-daily-digest/README.md) |
| **剧集缺集检测与补齐**<br>`missing-episodes` | 1.0.1 | 比对本地剧集与 TMDB 应有的季集找出缺集，并按你的配置搜索补齐（默认只记录，不写盘）。 | [README](plugins/missing-episodes/README.md) |

上面每行只写一句话，**完整功能、参数与排错请点右侧 README**。

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

> ⚠️ **不要直接导入 `plugins/<插件 id>/plugin.py`。** 它是插件包内入口，清单写在同一目录的 `plugin.json` 里；把源码入口当「Python 单文件」导入会被拒绝并提示 `Python 单文件必须在顶层定义唯一的 PLUGIN_MANIFEST 常量字典`。可导入的单文件由 `.github/scripts/package_plugin.py` 在文件开头内联 `PLUGIN_MANIFEST` 后生成。
>
> 也可以自行构建：见下方 [本地构建](#本地构建)。

---

## 仓库结构

```text
.
├── .github/
│   ├── ISSUE_TEMPLATE/            # Issue 模板
│   ├── scripts/                   # 仓库构建脚本（CI 与本地共用）
│   │   ├── package_plugin.py      # 打包插件并计算 sha256 / size
│   │   └── build_marketplace.py   # 扫描 plugins/ 生成 plugins.json
│   └── workflows/
│       ├── publish-plugin.yml     # 打包 → 发布 Release → 刷新 plugins.json
│       └── validate.yml           # 推送时校验清单、打包与 plugins.json 同步
├── docs/
│   └── tgto-plugin-kb/            # TgtoDrive 插件开发参考资料存档
├── plugins/
│   ├── invites-signin/            # 单个插件的源码目录
│   │   ├── plugin.json            # 插件清单
│   │   ├── plugin.py              # 插件入口（同步 run(params, context)）
│   │   └── README.md              # 插件使用文档
│   ├── wecom-notify/              # 第二个插件，结构与上相同
│   │   └── marketplace.json       # 可选：市场元数据
│   ├── wecom-call-demo/           # 第三个插件（插件互调示例），结构与上相同
│   ├── ttd-daily-digest/          # 第四个插件（每日推送），结构与上相同
│   └── missing-episodes/          # 第五个插件（缺集检测与补齐），结构与上相同
├── publish.bat                    # 双击即发布（Windows；其调用的本地发布脚本不入库）
├── dist/                          # 单文件版产物（可直接导入；zip 不入库，随 Release 分发）
│   ├── invites-signin.py
│   ├── wecom-notify.py
│   ├── wecom-call-demo.py
│   ├── ttd-daily-digest.py
│   └── missing-episodes.py
├── plugins.json                   # 插件市场目录 schema_version 1
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

约定：

- 每个插件位于 `plugins/<插件 id>/`，目录名与 `plugin.json` 中的 `id` 一致。
- 插件源码目录只放**源码与文档**；打包产物写入 `dist/`，通过 Release 分发。
  `dist/*.py`（单文件版）入库以便直接下载导入，`dist/*.zip` 不入库。
- 单文件版由 `.github/scripts/package_plugin.py` 在文件开头**内联唯一的 `PLUGIN_MANIFEST` 字典字面量**；
  源码目录里的 `plugin.py` 不带清单，不能当作单文件导入。
- `docs/` 下为 TgtoDrive 官方文档与接口规范的开发参考存档，版权归 TgtoDrive 项目所有。

---

## 本地构建

无需任何第三方依赖，Python 3.9+ 即可：

```bash
# 打包 plugins/ 下全部插件到 dist/，并计算 sha256 与字节数
python .github/scripts/package_plugin.py --all

# 只打包指定插件
python .github/scripts/package_plugin.py --plugin invites-signin

# 依据 dist/ 产物生成/刷新 plugins.json
python .github/scripts/build_marketplace.py --repo <账号>/<仓库名>
```

`build_marketplace.py` 在 GitHub Actions 中会从 `GITHUB_REPOSITORY` 环境变量自动获取仓库名，无需手动传入。

---

## 发布新版本

1. 在 `plugins/<id>/plugin.json` 中提升 `version`（保持 `id` 不变）。
2. 在 `CHANGELOG.md` 中记录本次变更。
3. **运行仓库根目录的 `publish.bat`** —— 它会跑完整条发布链路，无需再手工去 Actions 点工作流。

### 一键发布脚本

`publish.bat` 依次执行 5 步：打包全部插件 → 刷新 `plugins.json` → 提交 → 推送 →
**触发 `Publish plugin` 工作流并逐字节校验 Release 附件**。

| 命令 | 说明 |
| --- | --- |
| `publish.bat` | 完整链路（推荐） |
| `publish.bat -m "说明"` | 用自定义的提交说明 |
| `publish.bat --no-publish` | 只到推送为止，不触发 Release |
| `publish.bat --publish-only` | 跳过打包与提交，只做发布与校验（补发上次漏掉的 Release） |
| `publish.bat --no-push` | 只打包并提交到本地，不推送 |
| `publish.bat --no-api-fallback` | `git push` 失败时不改用 GitHub API 兜底 |
| `publish.bat --dry-run` | 只打印将要执行的命令，不做任何改动 |

以上链路依赖两个**本机私有脚本**（`scripts/publish_all.py` 与 `scripts/gh_publish.py`）——
它们只存在于维护者本机、**不随仓库分发**（已在 `.gitignore` 中排除），因此你在克隆下来的仓库里看不到它们。

> `git push` 需要访问 `github.com:443`。若该域名不可达（典型报错
> `CONNECT tunnel failed, response 502`）而 `api.github.com` 正常，
> 脚本会自动改用 GitHub Git Data API 构造提交推送 —— 且要求 API 生成的 commit SHA
> 与本地完全一致，否则中止以免产生分叉。

#### 为什么「推送」不等于「发布」

插件市场是拿 `plugins.json` 里声明的 `download_url` 去 GitHub Release 下载附件的。
**推送代码不会创建 Release**，只要少了这一步，市场安装就会失败：

| 情况 | 市场报错 |
| --- | --- |
| tag 对应的 Release 还不存在 | `GitHub 下载失败（HTTP 404）；Release API 回退失败：GitHub 下载失败（HTTP 404）` |
| Release 存在，但附件与目录声明的 `sha256` / `size` 不符（例如改了源码没重新发布） | `GitHub 文件超过允许大小或长度无效` |

`gh_publish.py` 会在发布后**重新下载附件逐字节复核**，与 `plugins.json` 的声明比对，
结果分三态：一致、**确实需要发布**、**网络故障无法判定**。第三态不会触发发布 ——
避免一次网络抖动就无谓地重新发版；三者都有明确的退出码。

> ⚠️ **`publish.bat` 必须保持纯 ASCII 内容**：`cmd.exe` 是按系统 ANSI 代码页解析 `.bat` 文件的，
> 即使写了 `chcp 65001` 也救不了解析阶段；写入 UTF-8 中文会导致整段语法错乱。
> 因此脚本里的中文提示全部由本机私有的 `scripts/publish_all.py` 输出。
>
> 打包是**确定性输出**（zip 用 STORED、固定时间戳、按 POSIX 路径排序），
> 脚本对全部插件打包不会改变已发布插件的哈希，也不会影响其它插件的 Release，
> 更不会让发布工作流产生多余提交；若工作区没有可提交的改动，脚本会跳过提交与推送，
> 但仍会继续做发布与校验。

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
