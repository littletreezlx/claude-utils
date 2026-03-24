---
name: game-mvp-project-context
description: Barracks Clash — Godot 4.6 单机军团自走棋，资产型布阵 + 跨局养成，目标 Steam PC
type: project
---

Godot 4.6 + GDScript 的 2D 独立 PC 游戏（目标 Steam），核心定位"养成驱动的单机军团自走棋" (Progression-driven Single-player Legion TD)。

**Why:** 2026-03-22 从"消耗型出兵"(Clash Royale 式) Pivot 为"资产型布阵"(梦塔防/Legion TD 式)。原因：原设计灵魂"棋子不是消耗品"与 MVP 实现矛盾，Pivot 后设计灵魂与机制统一。

**How to apply:**
- 玩法类型：资产型布阵（单位永久资产，波次间满血复活归位）
- 核心循环：部署阶段（网格放兵）→ 战斗阶段（自动对战）→ 波次结算（复活+发金币）
- 职责分离：局内=横向扩展（铺场+站位）；局外=纵向养成（铁匠铺升级）
- 局内无升级，金币仅用于买新兵；升级走营地铁匠铺
- 网格：4×5 (80px)，Click-to-Place 部署，左半屏
- 败北条件：敌方突破基地线 (x=50)
- 波次结算时一次性发放金币（非实时击杀即发）
- 架构：6 个 Autoload 单例，Level.gd 拆为薄壳+LevelStateMachine(RefCounted 纯逻辑)
- 视觉参数集中在 Assets/Data/battle_config.tres（BattleConfig Resource），AI 不改 .tres 数值
- 信号追踪：tools/signal_map.sh 动态生成 EventBus 21 信号→文件映射
- 测试：GUT 9.6.0，headless CLI，97 tests / 216 asserts（5 个测试文件）
- Phase 路线：P1✅ P3✅ P4✅ → P2(视觉包装，进行中)
