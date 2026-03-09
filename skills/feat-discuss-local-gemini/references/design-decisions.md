# feat-discuss-local-gemini 设计决策

本文件记录 Skill 设计中的关键决策和背后的推理，供维护时参考。

## 为什么保持双角色（product / design）而非合并？

product 关注"该不该做、数据怎么流"，design 关注"怎么好看、动效怎么调"。强行合并会导致 AI 注意力稀释，两头都做不深。经 Gemini 评估确认：看完两套完整 System Prompt 后推翻了合并建议。

## 为什么不硬编码 PRODUCT_SOUL 摘要到脚本？

硬编码意味着 PRODUCT_SOUL 更新时需同步改脚本，违反"单一事实来源"原则。摘要段留在文档中，修改一处即可。

## 为什么 Step 3 叫 "Engineering Handshake" 而非 "Critical Thinking"？

原来的 "Critical Thinking" 步骤深度不确定——有时太浅（走过场），有时太深（花大量 token 质疑合理建议）。固定格式让输出稳定、有价值。"Handshake" 强调的是执行者校验，不是评委打分。

## 为什么不用独立 ADR（Architecture Decision Records）？

实际项目中 `docs/adr/` 目录始终为空，独立 ADR 机制形同虚设。将架构决策内联到 Feature Spec 的 `Architecture Decisions` 段更务实，随功能走、随功能查。

## 为什么不携带 CLAUDE.md 给 Gemini？

CLAUDE.md 是给 Claude Code 的工程操作指南（测试策略、Git 规范、代码风格等），Gemini 作为产品/设计顾问不需要这些信息，反而会分散注意力。

## 多轮上下文传递：为什么从 100 字 Previous_Consensus 改为 300-500 字摘要？

v0.3.0 中要求"浓缩为 100 字以内的 `<Previous_Consensus>`"，实际使用中发现 100 字只能传一句结论，丢失了 Gemini 的推理过程和关键论据。第二轮 Gemini 等于在盲猜上一轮自己说了什么。

v0.4.0 改为要求 300-500 字摘要，保留：核心结论 + 关键论据 + 具体建议条目。同时要求项目上下文每轮重传，因为 Gemini 是无状态的。

## 为什么加 Step 1.5 上下文自检？

v0.3.0 的首轮调用中，Claude Code 在不在项目目录时凭记忆编造了 PRODUCT_SOUL 内容，导致 Gemini 基于错误上下文给出建议。自检关卡强制要求：文件内容必须从实际文件读取，不在项目目录中时必须告知用户。

## Prompt 组装原则的由来

- "描述事实，不描述体系"：因为 Gemini 看到"冰山模式测试策略"会花大量篇幅评价这个策略本身，而不是回答实际问题
- "标注触发方式"：Gemini 容易把"手动按需工具"脑补为"自动化流水线"，然后基于错误假设给建议
