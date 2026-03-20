---
name: game-mvp-project-context
description: Barracks Clash MVP - Godot 4.x 2D game project context and architecture decisions
type: project
---

Godot 4.x + GDScript 的 2D 独立 PC 游戏（目标 Steam），核心玩法"重叙事 + 角色养成 + 兵营出兵对冲"。

**Why:** MVP 验证"招募-出兵-战斗-结算"核心循环是否闭环。

**How to apply:**
- 架构：HUD 同屏叠加（CanvasLayer），Area2D 单位，Enum 状态机（MARCH/FIGHT/DEAD）
- 信号：混合模式（跨域走 EventBus autoload，局域直连）
- 目录：按功能模块分组（Core/Autoloads, Features/Units|Battle|UI）
- 已知技术债：String team 应改为 enum Team；无屏幕外单位清理
- 叙事和养成系统排除在 MVP 外，后续加入
- Spec: docs/superpowers/specs/2026-03-19-barracks-clash-mvp-design.md
- Plan: docs/superpowers/plans/2026-03-19-barracks-clash-mvp.md
