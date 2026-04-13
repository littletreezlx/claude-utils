# think-gem-project 设计决策

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

## 多轮上下文传递的演进

- **v0.3.0**：100 字 `<Previous_Consensus>`。太短，只能传一句结论，丢失推理链。
- **v0.4.0**：300-500 字固定摘要。方向正确，但固定字数容易磨灭推理细节（尤其是 UI 像素级约束）。
- **v0.5.0**：滑动窗口策略——最近 2 轮保留完整原文，更早轮次压缩为 Locked Consensus bullet points。既控制 token 又保留高保真上下文。

## 为什么废弃 Step 1.5 自检 checklist？

v0.4.0 加入 Step 1.5 是为了防止 Claude Code 凭记忆编造文档内容。v0.5.0 将其核心价值压缩为 Step 1 末尾的 2 条硬约束（必须实际读取文件、不在项目目录时告知用户），因为 Claude Code 的 Read tool 本身就是确定性的——文件存在就返回内容，不存在就报错，不需要 LLM 层面的"自检 checklist"。

## 为什么删除 Prompt 中的"协作简况"？

v0.4.0 的首轮 Prompt 包含"协作简况"（团队构成和工作方式）。经 Gemini 审视后确认：这是元信息噪音，会稀释 Gemini 对核心技术问题的注意力。Gemini 需要的是事实、上下文和边界，不需要知道团队怎么协作。

## 为什么 Prompt 结构与 Web 模式对齐？

v0.5.0 统一采用 `Context & Soul → Current State → The Problem → Constraints → Expected Brief` 结构。Web 模式（已合并进 `/web-think`）先验证了这个结构的有效性——信息密度高、层次清晰、自包含。Local 模式没有理由用不同的结构。

## 为什么 Engineering Handshake 改为条件分流？

v0.4.0 每次都输出完整三段式（Conflict Check / Breakdown / Prompt Founder），对单人 Founder 造成警报疲劳。v0.5.0 改为 Fast Track / Escalation 分流：无冲突时直接出 Breakdown 落库，有冲突时才触发完整 Handshake 等待 Founder 拍板。Founder 的注意力是系统中最稀缺的资源。

## Prompt 组装原则的由来

- "描述事实，不描述体系"：因为 Gemini 看到"冰山模式测试策略"会花大量篇幅评价这个策略本身，而不是回答实际问题
- "标注触发方式"：Gemini 容易把"手动按需工具"脑补为"自动化流水线"，然后基于错误假设给建议
