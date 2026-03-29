---
name: game-mvp-project-context
description: Barracks Clash — GDD V3.0 奇幻商队护卫×自走棋防守×常驻兵团养成，Godot 4.6 目标 Steam PC
type: project
---

Godot 4.6 + GDScript 的 2D 独立 PC 游戏（目标 Steam）。

**GDD V3.0 (2026-03-29 与杰确定)：**
核心定位从"养成驱动的单机 Legion TD Demo"升级为完整产品——"奇幻商队护卫×自走棋防守×常驻兵团养成"。

**六大核心系统：**
1. 战斗系统 — 20×40 大网格 Auto-battler，死亡消失/存活保留（滚雪球）
2. 商团长 — 唯一英雄，不可被攻击，光环+大招（唯一手操），3种统帅预设
3. 经济系统 — 局内底薪(逐波递增)+赏金，局外灵魂宝石(唯一货币)
4. 兵团契约 — 稀有度(白蓝紫金)+明牌商店(非盲抽)+碎片升级(Lv1-20)
5. Mechabellum 动态解锁 — 全图鉴招募面板+单线质变科技(全局生效)
6. 大地图跑商 — 杀戮尖塔式节点路线，程序化生成

**关键设计决策：**
- 装甲/伤害克制：3×3矩阵（Unarmored/Heavy/Ethereal × Physical/Pierce/Magic）
- 波次制(非回合制)：部署暂停→自动交战→结算循环
- PVP预留但暂不实现：统一引擎+数值归一化(PVP锁Lv1)

**代码现状（Demo V1，作为 V3.0 重构基础）：**
- Phase 1-5 全部完成，121+ tests 通过
- 当前路线：Phase 7 核心数据结构重构
- 文档体系：docs/ (GAME_DESIGN + ARCHITECTURE + ROADMAP + systems/6份子系统文档)

**Why:** 2026-03-29 与杰讨论后确定 V3.0 方向。从 3 关卡 Demo 走向完整产品。

**How to apply:**
- 设计文档以 docs/GAME_DESIGN.md (V3.0) 为权威来源
- 子系统细节查 docs/systems/ 子目录
- 当前代码架构仍是 Demo V1（4×5网格/全体复活/固定兵种），V3.0 重构从 Phase 7 开始
- Demo V1 原始设计已归档至 docs/archive/demo-v1/
