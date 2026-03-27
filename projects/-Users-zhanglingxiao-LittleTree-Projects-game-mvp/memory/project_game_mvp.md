---
name: game-mvp-project-context
description: Barracks Clash — Godot 4.6 单机 Legion TD（梦塔防式布阵+塔防波次防御混合），资产型布阵 + 跨局养成，目标 Steam PC
type: project
---

Godot 4.6 + GDScript 的 2D 独立 PC 游戏（目标 Steam），核心定位"养成驱动的单机 Legion TD"。品类更准确的描述是"塔防+自走棋混合"（波次防御 + 布阵策略），核心参考是梦塔防（封炎模式），而非纯自走棋（TFT/刀塔霸业那种棋盘 PvP）。

**基准玩法参考：梦塔防（封炎模式）/ Legion TD 2**
- 2026-03-25 确定：以梦塔防封炎模式为基础玩法对标，后续在此基础上创新迭代
- 核心特征：部署阶段精心布阵 → 战斗阶段单位自由前进迎敌（Boids 寻路避障）→ 零微操纯观战 → 波次结束满血传送归位
- 单位战斗行为：自由漫游寻敌（非站桩/非束缚），前排坦克吸引火力，后排 DPS 输出，远程兵射程不够也会前移
- 已超越 MVP 阶段，追求最终质感，核心机制不妥协

**Why:** 2026-03-22 从"消耗型出兵"(Clash Royale 式) Pivot 为"资产型布阵"(梦塔防/Legion TD 式)。原因：原设计灵魂"棋子不是消耗品"与 MVP 实现矛盾，Pivot 后设计灵魂与机制统一。

**How to apply:**
- 玩法类型：资产型布阵（单位永久资产，波次间满血复活归位）
- 核心循环：部署阶段（网格放兵）→ 战斗阶段（自动对战，单位 2D 自由寻敌）→ 波次结算（复活+发金币）
- 职责分离：局内=横向扩展（铺场+站位）；局外=纵向养成（铁匠铺升级）
- 局内无升级，金币仅用于买新兵；升级走营地铁匠铺
- 网格：4×5 (80px)，Click-to-Place 部署，左半屏
- 败北条件：敌方突破基地线 (x=50)
- 波次结算时一次性发放金币（非实时击杀即发）
- 架构：6 个 Autoload 单例，Level.gd 拆为薄壳+LevelStateMachine(RefCounted 纯逻辑)
- 视觉参数集中在 Assets/Data/battle_config.tres（BattleConfig Resource），AI 不改 .tres 数值
- 信号追踪：tools/signal_map.sh 动态生成 EventBus 21 信号→文件映射
- 测试：GUT 9.6.0，headless CLI，100 tests / 220 asserts（5 个测试文件）
- Phase 路线：P1✅ P3✅ P4✅ → P2(视觉包装，进行中)
