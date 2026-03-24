---
name: AI 维护策略共识
description: 与 Gemini 讨论后确定的 AI 独立维护策略 — ROI 评估框架 + 过度工程化警告
type: feedback
---

## 核心原则

评估一切 AI 维护基础设施的标准：**能否以最低 Token 成本换取快速失败 (Fast-Fail)**。

## 高 ROI 措施

1. **CLAUDE.md 必须保持精简** (<150 行索引)，静态参考移到 docs/。每次新会话的固定 Token 成本。
2. **YAML Schema 严格验证** (`extra="forbid"`) — AI 最容易产生结构性幻觉，毫秒级拦截优于跑完 ComfyUI 后发现。
3. **纯逻辑模块必须有测试** (lora_stack, workflow_nodes) — 给 AI 提供 "Prompt 锚点"，出错时报错堆栈是下一轮优化的最佳 Prompt。
4. **Visual Tuning Journal** — 测试无法覆盖的领域专属 Know-How，主观视觉→客观参数的映射。

## 过度工程化警告 (停止做)

- **停止扩展 contract YAML** — Type Hints 比外部契约更 AI 友好，不需要额外文件系统调用。已有的 5 个保留但不再新增。
- **不需要文档腐烂检测脚本** — AI 遇到 FileNotFoundError 后自然全局搜索，试错成本可接受。ai_context.sh 中的抽样检查够用。
- **不需要错误模式知识库** — Claude 自身语料已覆盖大部分。只需记录 ComfyUI 特定怪癖。
- **不需要依赖影响分析工具** — 需要时现写 20 行 AST 遍历脚本，跑完即弃 (Disposable Tool)。

**Why:** 纯个人项目，不需要团队协作边界。测试只能验证逻辑链路，最终质量靠人工视觉评估。

**How to apply:** 新增工程化措施前先问"这能否以最低成本实现快速失败？"如果不能，大概率是过度工程化。
