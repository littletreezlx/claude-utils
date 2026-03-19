---
name: maintenance-infrastructure
description: 2026-03-19 建立的项目维护基础设施，包括 ADR、SNIPPETS、变更影响矩阵等
type: project
---

2026-03-19 建立了完整的 AI 自主维护基础设施：

- **`.claude/SNIPPETS.md`**: 代码不变量 + 变更影响矩阵速查 + 代码模式（Do/Don't）
- **`docs/decisions/`**: ADR 架构决策记录（001-ServiceLocator, 002-AudioCoordinator, 003-WarmEssentialism）
- **ARCHITECTURE.md**: 新增「变更影响矩阵」和「模块风险评估」段落
- **test-coverage-report.md**: 新增「模块测试质量标签」（🟢可信赖/🟡需谨慎/🔴无保护）
- **CLAUDE.md 瘦身**: lt-music 级 255→130 行，Flutter 级 306→215 行

**Why:** 解决 AI 每次会话"失忆重启"的问题，让未来的 AI 能快速理解项目上下文、变更风险和架构决策理由。

**How to apply:** 未来做架构决策时主动创建新 ADR；变更高风险模块时先查影响矩阵；新会话先看 SNIPPETS.md 的不变量段。
