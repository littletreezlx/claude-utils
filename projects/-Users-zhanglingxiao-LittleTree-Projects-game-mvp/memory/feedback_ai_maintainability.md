---
name: ai-maintainability-conventions
description: AI 维护 Godot 项目的关键约定：BattleConfig 参数隔离、Humble Object 模式、signal_map 工具、类型标注
type: feedback
originSessionId: 48924f91-54e8-4c55-9aac-d5d871071c8c
---
## 视觉参数隔离约定
所有视觉/手感参数（动画时长、击退距离、闪白强度、屏幕震动衰减等）集中在 `Assets/Data/battle_config.tres`，代码通过 `const CFG = preload("res://Assets/Data/battle_config.tres")` 读取。**AI 可改 .tres 数值**，但必须通过 Debug Play Server 实战验证手感（`/play/goto_battle` → 跑战斗 → 截图 + 关键数值快照作为凭证）。
**Why:** 集中化最初由 2026-03-24 与 Gemini 讨论后确定（避免 AI 改逻辑时意外改掉魔法数字，物理隔离到 .tres 消除风险）。原约定 "AI 不改 .tres" 在 2026-04-26 修订为 "AI 可改但必须截图闭环验证"——AI-Only 协作模式下 Founder 不动手，原规则导致数值调优流程停滞。详见 `~/.claude/docs/decisions/2026-04-26-01-ai-full-autonomy-godot-scenes.md`。
**How to apply:** 新增视觉/手感参数时，加到 `Core/Data/BattleConfig.gd` Resource 脚本 + 更新 `battle_config.tres`，代码里用 `CFG.xxx` 读取。改数值后必须 Debug Play Server 验证手感再交付。

## Humble Object 模式（Godot 场景测试策略）
复杂 Node 类（如 Level.gd）应拆为：纯逻辑类（RefCounted，100% 可测）+ 薄壳 Node（不测试）。Level.gd 已拆出 `LevelStateMachine.gd`。
**Why:** GUT 难以 mock .tscn 节点树，直接测 Node 类等于"给屎山穿防弹衣"。纯逻辑类不依赖场景树，可以完全 headless 测试。
**How to apply:** 当一个 Node 脚本超过 200 行且包含状态机/复杂决策逻辑时，考虑拆出 RefCounted 纯逻辑类。

## 信号追踪用 signal_map.sh
改 EventBus 信号前先跑 `bash tools/signal_map.sh`，查看该信号的所有 emit 和 connect 位置。不在 EventBus.gd 里写手动注释（会腐化）。
**Why:** 21 个信号的 .connect() 分散在 14 个文件中，手动注释两周后必定过时。脚本每次现跑保证 100% 准确。
**How to apply:** 改信号签名或新增/删除信号时，先跑脚本确认 blast radius。

## 类型标注和 assert 哨兵
所有 .gd 文件应有完整类型标注（函数返回值、参数、for 循环变量）。关键路径（状态机转换、金币操作）加 assert() 前置条件检查。
**Why:** GDScript 弱类型对 AI 是灾难，类型标注让引擎静态分析成为"第一名预警员"。assert 在 headless 测试时快速暴露时序/状态错误。
**How to apply:** 新写代码时必须带类型标注。在状态转换入口加 assert 检查前置状态。
