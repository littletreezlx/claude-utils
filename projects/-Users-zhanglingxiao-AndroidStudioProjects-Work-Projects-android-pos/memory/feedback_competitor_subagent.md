---
name: 竞品调研默认用 subagent
description: 查看竞品项目代码时默认启动 subagent，避免污染主上下文和浪费 token
type: feedback
---

查看竞品项目代码时，默认启动 subagent（Explore 或 general-purpose）执行，不在主对话中直接读竞品代码。

**Why:** 竞品项目和当前 POS 项目上下文完全不同，直接在主对话中读会：(1) 消耗大量 token (2) 污染主上下文窗口，影响后续 POS 开发任务的质量。

**How to apply:** 用户提到要看竞品实现（客如云/美团/趣买）时，立即用 Agent 工具启动 subagent，把竞品路径和具体问题交给 subagent 处理，主对话只接收总结结果。如果需要补全竞品文档，也在 subagent 中完成。
