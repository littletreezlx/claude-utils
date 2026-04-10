---
name: /think 同时处理产品和技术决策
description: /think 调用外部 AI 时应同时做技术判断和产品决策，能拍板就直接执行，只有真正难以处理的才留到 to-discuss.md
type: feedback
originSessionId: 26768341-b0b0-49fa-922f-a643c72f3a97
---
`/think` 不仅仅是技术 sanity check，还应包括产品决策。外部 AI（Gemini）完全有能力做产品判断。

**Why:** 用户认为 `/think` 已经给了综合意见，再把产品问题原封不动丢到 `to-discuss.md` 是多余的一步。to-discuss.md 应该只留真正困难的决策给产品负责人。

**How to apply:**
- ai-explore、ai-qa-stories 等工作流的 filing 阶段：`/think` 评估后，能拍板的问题（包括产品方向）直接转 TODO 或 Reject
- 只有 `/think` 也明确表示拿不准、涉及重大产品方向变更的，才写入 `to-discuss.md`
- 提高 `to-discuss.md` 的门槛：从"不是技术对错的问题"提升到"连外部 AI 咨询也无法决定的问题"
