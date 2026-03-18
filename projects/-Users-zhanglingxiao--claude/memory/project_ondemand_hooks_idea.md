---
name: 按需安全钩子 Skill 想法
description: /careful 和 /freeze 按需钩子模式，未来可实现为安全护栏 Skill
type: project
---

来源：Anthropic《Lessons from Building Claude Code: How We Use Skills》(2026-03)

Skills 可包含**按需钩子（On Demand Hooks）**——调用时激活，会话期间持续生效。

两个值得实现的模式：
- `/careful` — PreToolUse 钩子拦截危险命令（rm -rf、DROP TABLE、force-push、kubectl delete），操作生产环境时启用
- `/freeze` — 阻止对特定目录之外的 Edit/Write 操作，调试时防止误改不相关代码

**Why:** 这些钩子平时不需要（开着会干扰正常开发），但在特定场景下极其有用。
**How to apply:** 当需要创建安全相关 Skill 时，考虑按需钩子模式而非全局钩子。
