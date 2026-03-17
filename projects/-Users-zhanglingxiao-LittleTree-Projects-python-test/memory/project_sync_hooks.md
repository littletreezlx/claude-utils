---
name: sync 前置钩子设计意图
description: pushgit 脚本的网关检查和 VPN 检查不能移除，是为了在公司网络下避免被检测到提交使用记录
type: project
---

sync 模块（projects/sync/）的前置钩子（关 Cursor、网关检查、VPN 检查）在 push 和 pull 场景下都需要保留。

**Why:** 用户在公司时，不希望公司网络检测到 Git 同步操作的使用记录。网关检查（192.168.10-20.1）和 VPN 检查是安全防护措施，不是技术冗余。

**How to apply:** 不要建议移除或简化 before_git_sync() 中的任何检查步骤。优化 sync 模块时，前置钩子逻辑是不可动的。
