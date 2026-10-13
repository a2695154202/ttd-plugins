# TgtoDrive 插件开发知识库

最初交给 AI 的那批资料，已全部固化到这里，不再依赖对话上下文或 `Downloads` 目录。

- **归档时间**：2026-10-13
- **来源**：TgtoDrive（tgto123）「实用工具 → 我的插件」的 AI 开发提示词、开发指南、示例插件与容器导出的 OpenAPI 规范
- **容器环境快照**：Python 3.13.16 / Linux / x86_64，`ffmpeg`、`ffprobe`、`node`、`curl`、`ping` 均可用

---

## 文件清单

| 文件 | 内容 | 大小 | SHA-256（前 16 位） |
| --- | --- | --- | --- |
| `01-ai-development-prompt.md` | 「AI 开发提示词」全文：容器环境、插件协议、执行协议、参考插件、插件市场、交付要求 | 49,047 B | `a1ca67cfc234b3f1` |
| `02-plugin-development-guide.md` | 「实用工具 · Python 插件开发」开发指南全文 | 20,944 B | `392a388859d61899` |
| `03-openapi-endpoints.md` | 由规范生成的接口索引，按 tag 分组，含文档级别与请求字段 | 31,713 B | `3eef39ece867ac64` |
| `04-protocol-checklist.md` | 协议硬约束清单（写代码时对照用） | — | — |
| `spec/tgto-openapi.json` | OpenAPI 3.0.3 规范原文，189 条路径 / 212 个操作 | 414,873 B | `9db32cc7bd7b2990` |
| `example/text-helper/plugin.json` | 官方示例清单 | 929 B | `ed259cfd55347f8e` |
| `example/text-helper/plugin.py` | 官方示例入口 | 1,022 B | `8fa70a4840e608e3` |
| `example/text-helper/README.md` | 与 `02-` 内容相同（同一文档） | 20,944 B | `392a388859d61899` |
| `example/tgto-text-helper.zip` | 官方原始压缩包（**未入库**，见下方说明） | 10,777 B | `26823111ac889f48` |

> `example/tgto-text-helper.zip` 是二进制压缩包，内容已完整解包保留在 `example/text-helper/`（三个文件与包内一致），因此原件不纳入版本控制（已在 `.gitignore` 中忽略）；需要原件时可在 TgtoDrive 插件页调用 `GET /api/toolbox/plugins/example.zip` 重新下载。表中 SHA-256 为原件快照值。

> `02-plugin-development-guide.md` 与 `example/text-helper/README.md` 的 SHA-256 完全一致 —— 第二份长文本就是示例包里的 README，这里保留两份以便单独查阅，内容无差异。
>
> `01-ai-development-prompt.md` 没有对应的原始文件，是对话中唯一一份，已完整落盘。文件顶部的注释块是归档元信息，转发给其他 AI 时可整段删除。

---

## 怎么用

**要开发新插件**：把 `01-ai-development-prompt.md` 全文 + `spec/tgto-openapi.json`（或查阅 `03-openapi-endpoints.md` 选接口）一起交给 AI，再在末尾「我的插件需求」处写明需求。这是最初的标准做法。

**要查接口**：先看 `03-openapi-endpoints.md` 按 tag 找到候选接口，再回 `spec/tgto-openapi.json` 核对具体字段。

**要核对协议**：看 `04-protocol-checklist.md`。

**要对照官方写法**：看 `example/text-helper/`。

## 环境更新提示

容器内可直接重新获取最新版本：

```text
GET /api/toolbox/plugins/ai-development-prompt   获取当前容器的 AI 开发提示词
GET /api/toolbox/plugins/development-guide       获取插件开发指南
GET /api/toolbox/plugins/example.py              下载单文件示例
GET /api/toolbox/plugins/example.zip             下载 ZIP 示例
GET /api/openapi/spec                            获取当前服务的 OpenAPI 规范
```

容器重建或升级后，上述接口返回的环境快照（Python 版本、已装依赖、命令可用性）可能变化，建议用新内容替换 `01-` 与 `02-`。

## 已知的规范短板（影响实现决策）

规范里带 `x-documentation-level` 标记，统计如下：`documented` 12 个、`inferred` 131 个、`generic` 71 个。

这意味着**大部分接口的请求模型是静态分析推断出来的，响应体则完全没有 schema**。两个已踩到的坑：

1. `POST /api/media/resources/search` 等接口的字段只列出名字，没有类型和必填性说明。
2. `GET /api/proxy_settings` / `GET /api/notify-bots` 的**响应字段名未知**，无法据此硬编码读取通知机器人配置，只能做启发式识别。

因此凡涉及这两个接口的实现，都需要在真实容器里实测确认。
