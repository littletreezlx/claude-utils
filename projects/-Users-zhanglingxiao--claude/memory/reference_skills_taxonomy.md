---
name: Skills 9 类分类体系
description: Anthropic 内部 Skills 分类体系，规划新 Skill 时用作自检清单
type: reference
---

来源：Anthropic 工程师 Thariq Shihipar《Lessons from Building Claude Code: How We Use Skills》(2026-03)

规划 Skill 体系时，检查以下 9 个类别是否有缺口：

1. **库与 API 参考** — 内部库/SDK 的踩坑点和代码片段（如 billing-lib、design-system）
2. **产品验证** — 搭配 Playwright/tmux 等工具验证代码正确性（如 signup-flow-driver）
3. **数据获取与分析** — 连接数据源和监控体系（如 funnel-query、grafana）
4. **业务流程与团队自动化** — 重复性工作流一键化（如 standup-post、weekly-recap）
5. **代码脚手架与模板** — 生成项目特有的样板代码（如 new-migration、create-app）
6. **代码质量与审查** — 执行代码标准（如 adversarial-review、code-style）
7. **CI/CD 与部署** — 拉取/推送/部署自动化（如 babysit-pr、deploy-service）
8. **运维手册** — 现象→排查→报告的结构化流程（如 oncall-runner、log-correlator）
9. **基础设施运维** — 日常维护与带安全护栏的破坏性操作（如 orphan-cleanup、cost-investigation）

好的 Skill 清晰地落在某一个类别里；让人困惑的 Skill 往往横跨了好几个。
