---
name: AI-Only Development Paradigm Awareness
description: 工作流设计必须基于"AI 全权开发"前提，不假设人类程序员存在。2026-04-07 用户发现的系统性盲区
type: feedback
---

所有工作流、skill、文档体系的设计必须基于"AI-Only"前提：AI 全权负责代码/测试/文档，人类是产品负责人。

**Why:** 2026-04-07 讨论 user-stories 架构时，用户指出 Claude Code 和 Gemini 都默认假设"有人类开发者维护两个文件很难"，因此否决了实际更优的双文件方案。根因是工作流体系中没有声明"这是 AI-Only 项目"。

**How to apply:**
- 全局 CLAUDE.md 顶部已添加「项目协作模式（AI-Only Development）」声明
- 决策升级按**影响半径**（非领域）划分：组件内 AI 闭环，跨 App 共享状态/重型依赖才升级
- 测试防线三道：结构性时间差（TDD）→ 运行时验证（Debug Server）→ 红队对抗（/test-verify）
- /think 和 /feat-discuss prompt 模板已添加协作模式声明
- 设计任何新 skill/workflow 时，先问：「这个步骤假设了人类会做什么？在 AI-Only 场景下谁来做？」
