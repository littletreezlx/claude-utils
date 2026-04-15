---
name: 锚点修复带来的次级塌陷
description: 修掉主题塌陷（cyberpunk/steampunk）后，LLM 在角色物理特征上出现新的趋同 — 需要"放飞"
type: feedback
originSessionId: 2a345649-f68e-47c7-8f22-acf749083142
---
2026-04-15 B vs C bench 187 样本实测：

**一级塌陷**（已修）：cyberpunk / steampunk / tavern / medieval 默认 — 全 0 across all backends。锚点池有效。

**二级塌陷**（新发现）：
- auburn 头发 67/187 = **36%**
- auburn + chestnut + dark brown 合计 ~60%
- olive + tan 皮肤 42/187 = **22%**
- 几乎零：silver / platinum / pink / red / 深黑
- 想象色（紫/粉/白/银）= 0

**Why**: 锚点把主题（theme/culture）拉开了，但 LLM 在 character 字段（发色/肤色/眼睛/脸型）有高自由度，塌进了"深色暖调 + olive/tan + auburn"的安全带。Founder 反馈："反而一些确实比之前没有出现过的元素减少了……变成一个趋同的感觉。可以再放飞一下。"

**How to apply**:
- 设计/讨论锚点池时，不仅看 theme 多样性，也要统计 character 字段（发色/肤色/眼色）分布
- 可能需要在 prompt 里加 character 多样性护栏（类似 body tier 的显式档位），或者在锚点里埋"奇异发色/科幻种族/玄幻血统"诱因
- 单独扩 role/era 不够；要让 LLM 敢给非人类/非现实角色（ghosts, androids, elves, silver-haired spirits 等）
