---
description: 🤖 Gemini 产品方案咨询 (轻量版 - Gems 已有上下文) ultrathink
---

# Gemini 产品方案咨询（轻量版）

## 目标
为**已有项目上下文的 Gemini Gems** 生成精简的咨询 Prompt。

> 如果 Gemini 不了解项目上下文，请使用 `/feat-discuss-gemini-full-context`

## 执行流程

### Step 1: 理解需求
1. 用户想做什么？
2. 分类任务：
   - **TYPE A (逻辑/交互)**: 流程、状态、数据流转
   - **TYPE B (视觉/风格)**: 布局、配色、动效

### Step 2: 生成 Prompt

直接生成，**不做代码扫描**：

```text
------- GEMINI BRIDGE START -------
# Role: [Senior Product Designer / Creative Director]

## Request
[用户原始需求，可适当补充澄清问题]

## Instructions
请基于你对项目的了解，提供专业的解决方案。
用中文回答，技术词汇可用英文。
**不要写代码**，请输出结构化的设计文档，包含：

[TYPE A 逻辑/交互]:
1. User Journey（用户旅程）
2. State Definition（空状态/加载/错误）
3. Logic Rules（业务规则）

[TYPE B 视觉/界面]:
1. Component Anatomy（组件结构）
2. Layout Topology（布局拓扑）
3. Animation Specs（动效规格）

------- GEMINI BRIDGE END -------