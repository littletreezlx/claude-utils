---
name: feedback_visual_workflow_gemini_second_eye
description: 视觉类 skill（ui-vision-advance/ui-vision-check/ui-vs 等）的 /think 调用必须透传截图走 Gemini 默认分支，获取独立第二视角
type: feedback
originSessionId: efa5400d-b03a-4d97-a973-731d4729e9c4
---
视觉审美/设计评审类 skill 调用 `/think` 时，**必须**透传当前评审的截图，不能只传 Claude 写好的文字总结。具体做法：`node think.mjs --image <screenshot> "<prompt>"`，禁用 `--quick`（DeepSeek 分支不支持图片）。

**Why:** 用户强调"主要靠 Claude Code + Gemini 多模态能力"做视觉工作。只传文字总结等于"让 Gemini 审 Claude 的审美判断摘要"——Gemini 无法识别 Claude 漏看或脑补的盲区。直接喂图能打破 Claude 单一模型的审美回音室，让 Gemini 真正作为独立第二视角复核 anti-AI pattern、四柱审视等主观判断。不要预设"两个 AI 会冲突到无法收敛"这类假想风险，Claude 本来就有能力综合两份评审。用户明确反对过度约束 Gemini 的角色（如"只能回答预设 Failure_Premise"），那等于阉割了第二视角的盲区检测价值。

**How to apply:**
- 任何包含截图的 skill 设计，`/think` 调用点必须考虑透传图（`--image` flag）
- 禁用 `--quick` DeepSeek 分支 — 不支持多模态
- 不要强行限定 Gemini 只能回答 Claude 预设的问题
- 全自动闭环 skill（如 `game-ui-advance`）例外：如果加 `/think` 会破坏流畅度且边际价值低，不必强加
- 已废弃的 `ui-redesign` skill 不要再添加（其核心价值被 `ui-vision-advance` 的 Phase 4 设计简报完全覆盖）
