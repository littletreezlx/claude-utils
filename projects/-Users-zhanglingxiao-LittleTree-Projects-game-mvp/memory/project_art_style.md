---
name: art_style_direction
description: 美术风格方向 — Chibi Q版 + Pony 模型 + Danbooru Tag 体系 + 双模型策略
type: project
---

Phase 2 美术风格与生成管线（2026-03-22，多轮讨论后确定）：

**风格：Chibi Q版 + Kingdom Rush 扁平色块风**
- 角色 2-3 头身（chibi），平涂色块（flat color）+ 粗线条（thick lineart）
- 背景保留厚涂风（impasto），角色和 UI 走扁平风

**双模型策略（AB Test 验证后确定）：**
- **角色/UI** → `prefect_pony`（PonyV6 架构，tag 服从度极高，chibi 命中率 >80%）
- **背景** → `hassaku`（Illustrious 架构，场景/氛围插画强项）
- 切换原因：hassaku 对 chibi/solo 的遵从度低（~20% 命中率），经常生成 character sheet
- prefect_pony 即使有 R18 基因，但通过 `rating_safe` + negative `nsfw, explicit` 双保险完全安全

**Prompt 体系：纯 Danbooru Tag（角色）**
- 角色前缀：`rating_safe, 1boy, solo, chibi, cute, vector art, flat color, cel shading, thick lineart, white background, simple background, full body, standing`
- 角色 negative：`nsfw, explicit, suggestive, score_6, score_5, score_4, realistic, 3d render, multiple views, character sheet, turnaround, grid, comic, multiple boys, 2boys, gradient, complex shading, drop shadow, ground, floor, shadow beneath feet, pixel art`
- 角色 prompt 只写业务描述（如 `goblin warrior, green skin, red war paint, crude sword`），不写画风词
- prefect_pony 的 model_registry 会自动注入 `score_9, score_8_up, score_7_up, masterpiece, best quality`

**关键工程决策（不变）：**
- 角色 Sprite 输出 1024x1024，禁止 post_resize 到小尺寸
- Godot 中通过 Sprite2D.scale 缩放
- MVP 动画：单张静态图 + Godot Tween 假动画
- 风格一致性路线：MVP=prompt统一 → 后期=IP-Adapter

**Why:** Gemini 分析 + 第二 AI 交叉验证 + AB Test 实测证明 pony 在 chibi 场景完胜。
**How to apply:** 角色用 prefect_pony + Danbooru tag，背景用 hassaku + 自然语言。
