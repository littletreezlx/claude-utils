---
name: 不要建议移除 sync 前置钩子
description: 用户纠正了我对 pushgit 前置钩子（关 Cursor、网关检查、VPN 检查）的误判，这些是必要的安全措施
type: feedback
---

不要建议移除或简化 sync 模块的前置钩子（关 Cursor、网关检查、VPN 检查），即使是 push 场景。

**Why:** 这些钩子不是为了防文件冲突，而是为了在公司网络环境下避免被检测到同步操作。我之前误判了其设计意图。

**How to apply:** 审查 sync 模块时，将前置钩子视为安全需求而非技术需求，不纳入"过度设计"的优化范围。
