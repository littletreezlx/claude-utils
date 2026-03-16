---
name: Face LoRA 分离方案 (方案 D)
description: Gemini 咨询结论 — 反对 Body+Face 双 LoRA，推荐 Prompt 控制身体 + Face LoRA + Style LoRA 的三层架构
type: project
---

Face LoRA 分离方案已通过 Gemini 咨询确定方向（2026-03-13）。

**Why:** 当前全角色 LoRA 换角色成本高（每次重训 ~20min）。P 站主流做法是分离脸部和身体控制。

**核心决策:**
- 方案 C (Body+Face 双 LoRA) 被否决 — 底模对身材词已足够强，双 LoRA 权重超限 1.4，概念交叉感染
- 方案 D (Prompt 身体 + Face LoRA) 被采纳 — Face LoRA Dim 16/Alpha 8 轻量训练，身体交给 Prompt + 底模

**资产命名约定:**
- 全角色: `{name}_lora.safetensors` (Dim 64/32)
- Face: `{name}_face.safetensors` (Dim 16/8)
- 角色卡新增可选字段: `face_lora_file`, `face_trigger_word`, `face_weight`

**How to apply:**
- 实现在 TODO.md "未来方向" 段，分 4 个 Phase
- Phase 1 验证优先，用现有角色数据自动裁脸训练对比效果
- 自动裁脸可用 comfyui_controlnet_aux 的 MediaPipe/AnimeFace 节点，或 WSL2 端 insightface
- 向后完全兼容，没有 face_lora_file 的角色继续用全角色 LoRA
