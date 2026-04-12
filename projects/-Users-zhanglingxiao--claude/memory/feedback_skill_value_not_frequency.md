---
name: feedback_skill_value_not_frequency
description: 不要把"最近没用"作为废弃 skill 的理由，低频高价值 skill 不应被使用频率淘汰
type: feedback
originSessionId: efa5400d-b03a-4d97-a973-731d4729e9c4
---
"最近忘记用"**不等于**"这个 skill 不重要"。低频高价值 skill（紧急场景、边界情况专用工具、跨项目偶发触发的健康探针）不应该因为使用频率低而被合并或废弃。

**Why:** 使用频率只反映"当前工作形态下触发条件是否出现"，不反映 skill 的真实价值。典型例子是 `ui-vision-check` 的 Evolution Dialogue（代码-文档 drift 检测）和全局审计模式——这些是 AI-Only 项目的**低频但不可替代**的场景，最近没触发只是因为暂时没做全局改版或大范围 UI 代码变更，不代表 skill 无用。如果因此合并/废弃，会在触发条件真正出现时丢失响应能力。

对比：废弃 `ui-redesign` 是对的，理由是它**功能完全被 `ui-vision-advance` Phase 4 覆盖**（同问题域重复），不是"用户没用"。同问题域重复 ≠ 低频高价值。

**How to apply:**
- 判断 skill 是否该废弃/合并时，先问**功能上是否有独有价值**（独有的触发场景、独有的产出、独有的问题域），而非"最近是否被使用"
- **同问题域重复** = 可合并（如 ui-redesign vs ui-vision-advance 都是"审美评审 + 设计方向"）
- **不同问题域偶发使用** = 保留（如 ui-vision-check 面向"UI 体系健康"，和 ui-vision-advance 面向"单页深度审美"是不同问题域）
- 如果低频高价值 skill 没被自动触发，问题可能在 description 的触发词写得不够精准，不在 skill 本身——先优化触发词，不要急着删
- 类比：急救包一年用不到一次不该扔，但两把一模一样的剪刀应该留一把
