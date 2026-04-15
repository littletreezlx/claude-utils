---
name: 签名级特征必须显式标注稀有度
description: heterochromia 等签名特征出现在 prompt 示例里时必须配 "use sparingly" 警告，否则 LLM 会大量复用
type: feedback
originSessionId: b5303160-7c83-4849-b843-32cfe171affe
---
heterochromia (双瞳色) / vertical pupils / 等"签名级"视觉特征极易被 LLM 在示例中当默认模板复用，导致角色集体撞同一特征。

**Why:** 2026-04-15 排查 preview_characters/ 发现 stheno_v2_free_* 系列 30+ 角色里 80% 都有 heterochromia。根因是 `core/prompts/story.py` 里把 heterochromia 同时列在了 eye_color "rare colors welcome (...)" 示例 + distinctive[] 池首位，双重诱导。用户自己的 memory `feedback_example_pollution.md` 已警示过"示例即模板"。

**How to apply:**
- 签名级特征（视觉冲击大、出现一次就抢戏的）放 prompt 示例时必须加 "use at most 1 in ~15 characters / NEVER default to these" 显式频率约束
- 不要把这类特征放列表首位（首位偏置 + AI 抓取概率最高）
- heterochromia 不是颜色而是双色现象，不应出现在 eye_color 字段示例里
- 修改 character/story prompt 池后，跑一批 ≥20 个 preview 看分布，单一特征命中 >20% 即视为污染
