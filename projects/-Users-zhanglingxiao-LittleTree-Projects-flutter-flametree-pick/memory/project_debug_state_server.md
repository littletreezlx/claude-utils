---
name: Debug State Server
description: flametree_pick has a Debug State Server on localhost:8788 for programmatic app state reading and action execution
type: project
---

flametree_pick 项目已启用 Debug State Server（2026-03-31）。

**Why:** 消除 AI 辅助开发中"写代码 → 人工点击验证 → 报 bug"的半自动循环。通过 curl 直接读写 App 状态，实现秒级验证闭环。

**How to apply:**
- App debug 模式运行时自动启动在 `localhost:8788`
- 优先用 `/data/groups` 和 `/data/options`（直读数据库，不受 autoDispose 影响）
- `/state/xxx` 读 ViewModel 内存状态（需对应页面打开）
- Action 执行后自动返回最新数据库数据
- 代码在 `lib/dev_tools/debug_server.dart`、`debug_state_registry.dart`、`debug_action_registry.dart`
- 设计文档：`docs/superpowers/specs/2026-03-31-debug-state-server-design.md`
