---
name: high-risk-modules
description: 项目中复杂度高、测试覆盖不足的高风险模块，变更时需格外谨慎
type: project
---

以下模块变更风险最高，需要额外谨慎：

1. **ServiceLocator** (0% 测试覆盖) — 全局 DI 容器，改动影响整个 app。两阶段初始化（initialize → initializeLateServices）顺序不能变。
2. **AudioService + 6 个子模块** (41% 覆盖) — 状态传播链最长：AudioService → PlayerViewModel → MiniPlayer/DesktopPlayerBar。子模块间协调场景测试不完整。
3. **离线下载三层链路** — OfflineDownloadCoordinator → OfflineDownloadExecutor → OfflineStorageManager，端到端链路未验证。

**Why:** 这三个区域是项目最复杂的部分，也是测试覆盖最薄弱的地方。过去 Round 2 重构中 PlayerViewModel 与 AudioService 状态不同步的 bug 就出在这个链路上。

**How to apply:** 改动这些模块后，至少跑完相关模块的全部测试，并考虑是否需要补测试。不要依赖"看起来没问题"的直觉。
