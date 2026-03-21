---
name: game-mvp-project-context
description: Barracks Clash MVP - Godot 4.6 2D game, progression-driven auto-battler targeting Steam
type: project
---

Godot 4.6 + GDScript 的 2D 独立 PC 游戏（目标 Steam），核心定位"养成驱动的单机自动对战" (Progression-driven Single-player Auto-battler)。

**Why:** MVP 已验证核心循环（招募-出兵-战斗-结算-养成）闭环。当前处于 MVP→商业化产品 过渡期。

**How to apply:**
- 产品灵魂：养成成就为主轴，叙事为情绪调剂，资源博弈为策略深度
- 设计隐喻："带领老兵穿越绝境"（玩家经营佣兵团，老兵是珍贵资产）
- 差异化：CR 式动态出兵视觉 + 单机低压力 + 跨局养成
- 架构：5 个 Autoload 单例（EventBus/SaveManager/GameManager/AudioManager/SceneManager），Area2D 单位，Enum 状态机，混合信号模式
- 测试：GUT 9.6.0 测试框架（2026-03-21 引入），支持 headless CLI 闭环（写测试→运行→读报错→修复）
- 目录：按功能模块分组（Core/Autoloads, Features/Units|Battle|UI）
- MVP 后路线：Phase1 数据剥离 → Phase2 美术打击感 → Phase3 跨局养成+存档
- 已知架构风险：波次硬编码需 Custom Resource、BaseUnit 需组件化准备、EventBus 需按域整理
- Spec: docs/superpowers/specs/2026-03-19-barracks-clash-mvp-design.md
- Plan: docs/superpowers/plans/2026-03-19-barracks-clash-mvp.md
- 文档规范 Spec: docs/superpowers/specs/2026-03-20-doc-system-and-standards.md
