## 变更内容

<!-- 简要说明这个 PR 做了什么、为什么需要它 -->

## 关联 Issue

<!-- 例如 Closes #12 -->

## 类型

- [ ] 新增插件
- [ ] 插件功能变更
- [ ] 插件缺陷修复
- [ ] 文档 / 工程化改动

## 自检清单

- [ ] `python .github/scripts/package_plugin.py --all` 通过
- [ ] `plugins.json` 已用 `python .github/scripts/build_marketplace.py --repo <账号>/<仓库名>` 重新生成
- [ ] `plugin.json` 的 `id` 未变更；若有功能改动，`version` 已提升
- [ ] `CHANGELOG.md` 已记录本次变更
- [ ] 插件 `README.md` 的参数表与实际 `inputs` 一致
- [ ] 未提交任何 Cookie、密码、Token、`dist/` 产物或 `settings.json`
- [ ] 若为移植插件，已在 README 与 `author` 字段保留原作者署名，且许可证与上游兼容

## 补充说明

<!-- 截图、日志、注意事项等（请先打码敏感信息） -->
