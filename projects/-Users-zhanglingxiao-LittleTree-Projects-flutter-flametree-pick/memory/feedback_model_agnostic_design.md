---
name: 不为不同模型设计不同路径
description: AI 工作流应模型无关——输入质量决定输出质量，不要按模型能力分流
type: feedback
---

不要为不同能力的 AI 模型（如 Claude vs MiniMax）设计不同的执行路径或检查清单。

**Why:** 用户明确指出"区分模型来对待不合适"。两个模型 QA 探索表现差异大，根因是缺乏结构化输入（user-stories），不是模型能力差异。给同样好的输入，低能力模型也能按部就班验证。

**How to apply:** 设计 skill/workflow 时，专注于提升输入质量（如 user-stories 的完整度、断言的具体性），而不是为不同模型写不同的引导。一个 skill，一个流程，模型能力差异体现在探索深度上。
