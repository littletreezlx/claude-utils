---
name: prompt-craft
description: >
  This skill should be used when the user is writing, reviewing, or debugging
  AI-facing prompts in project code — system prompts, user prompt templates,
  API call prompts, or agent instructions. Use when the user says "write prompt",
  "review prompt", "optimize prompt", "写提示词", "改 prompt", "prompt 不好用",
  or when editing files that contain AI prompt strings (system messages, instruction
  templates). Applies prompt engineering as requirements engineering.
version: 0.1.0
---

# Prompt Craft — AI 提示词工程

## 目的

帮助用户在项目代码中编写高质量的 AI-facing prompt。将"提示词工程"视为"需求工程"：目标清晰、约束明确、验收可测、格式稳定。

## 触发条件

当以下**任一**条件满足时启动：

1. 用户正在编写调用 AI API 的 prompt（system prompt、user prompt 模板）
2. 用户要求审查/优化现有 prompt
3. 用户反馈 prompt 输出不稳定、格式不对、效果不好
4. 编辑的文件中包含 AI prompt 字符串（检测到 `system`/`instruction`/`prompt` 变量）

## 执行流程

### Step 1: 理解 Prompt 用途

先搞清楚三件事：

| 问题 | 为什么重要 |
|------|-----------|
| **谁调用？** | 确定目标模型（Claude/GPT/Gemini），不同模型有不同最佳实践 |
| **做什么？** | 明确任务边界——prompt 要解决的具体问题 |
| **给谁用？** | 终端用户直接看到输出，还是系统内部消费（影响格式要求） |

### Step 2: 结构审查（需求工程五要素）

检查 prompt 是否覆盖以下要素，缺失的标记并补充：

```
┌─────────────────────────────────────────────┐
│  1. 角色定位  — 你是谁，专长是什么            │
│  2. 任务目标  — 要做什么（一句话说清）         │
│  3. 约束条件  — 不做什么、边界在哪             │
│  4. 输出格式  — 结构、长度、语言、JSON schema  │
│  5. 示例/验收 — 好的输出长什么样               │
└─────────────────────────────────────────────┘
```

**不是每个 prompt 都需要五要素齐全**——简单任务只需目标+格式，复杂任务才需要完整覆盖。判断标准：输出不稳定的维度就是缺失的要素。

### Step 3: 反模式检测

| 反模式 | 问题 | 修复 |
|--------|------|------|
| 模糊指令 | "写得好一点" → AI 不知道"好"的标准 | 给具体标准："控制在 200 字内，用数据支撑论点" |
| 矛盾约束 | "简短但详尽" → 互相矛盾 | 明确优先级："优先简短，关键数据不可省略" |
| 万能 prompt | 一个 prompt 做所有事 | 按任务拆分，每个 prompt 单一职责 |
| 依赖心智模型 | 假设 AI 知道项目背景 | 在 prompt 中提供必要上下文 |
| 格式靠运气 | 没有格式约束，期望 AI 猜对 | 用 JSON schema / 示例明确格式 |
| 过度约束 | 规则太多导致 AI 无法完成任务 | 区分硬约束（必须）和软约束（尽量） |

### Step 4: 模型适配

根据目标模型提供针对性建议：

- **Claude**：擅长长上下文、XML 标签结构、system prompt 权重高
- **GPT**：JSON mode 内置支持、function calling 格式
- **Gemini**：多模态原生支持、grounding 能力

如果用户未指定模型，按 Claude 最佳实践编写（XML 标签、清晰分段）。

### Step 5: 输出稳定性加固

- **结构化输出**：需要 JSON 时，提供 schema 或完整示例
- **边界处理**：prompt 中说明"如果输入不符合预期，返回 X"
- **温度建议**：需要确定性输出时建议低温度，创意输出时允许高温度
- **长度控制**：明确 token 预算或字数范围

## 输出

修改后的 prompt 代码 + 简要说明改了什么、为什么改。不生成独立文档。

## 约束

- **改 prompt 不改业务逻辑**：只优化 prompt 文本，不改调用方式（除非用户要求）
- **最小改动**：能改一句不改一段，保留用户原有风格
- **不过度工程化**：简单 prompt 不强加复杂结构
- **标注不确定性**：对"可能更好但没法确定"的改动，标记为建议而非必须
