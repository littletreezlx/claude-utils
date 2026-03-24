---
name: lora_stacking_lessons
description: 多 LoRA 堆叠的经验教训 — 权重控制、冲突规避、风格系统交互
type: feedback
---

## LoRA 堆叠经验

**4 个 LoRA 总权重 2.0 在 MiaoMiao 上会互相打架。** V1/V3 风格系统自带 SweatyStyle LoRA，再叠加 shiny_wet_skin 会导致材质溢出（全身变塑料）。

**Why:** 2026-03-21 实验中，DetailedEyes(0.35) + DarkFlash(0.55) + ShinyWetSkin(0.60) + PerfectBreasts(0.50) = 总权重 2.0，超过安全极限 1.4。底模自身的 3D 渲染能力被 LoRA 压制。

**How to apply:**
- 先不挂 LoRA 跑一张看底模裸跑效果，再逐个加
- V1 风格已自带 SweatyStyle @ 0.8，不要再叠出油类 LoRA
- 总权重控制在 1.4 以内
- 风格系统注入的 LoRA 也算在总权重里

## 已安装的可用 LoRA

| 文件名 | 用途 | 建议权重 | 触发词 |
|--------|------|---------|--------|
| DetailedEyes_V3 | 眼部精细化 | 0.3-0.5 | 无 |
| sdxl_darkflash_v6-000060 | 闪光灯黑场 | 0.4-0.6 | `very dark focused flash photo` |
| shiny_wet_skin_v2 | 出油水珠 (IL原生) | 0.4-0.6 | 无 |
| PerfectBreastsPonyV2 | 形变挤压 | 0.4-0.6 | `breasts pushed together` |
