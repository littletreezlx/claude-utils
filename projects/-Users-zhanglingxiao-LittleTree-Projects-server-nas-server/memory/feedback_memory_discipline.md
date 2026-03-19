---
name: 记忆系统纪律——不存可推导信息
description: 禁止将代码架构、模块结构、文件路径等可从代码/文档推导的信息写入 Memory
type: feedback
---

不要把模块架构、关键文件列表、数据流、状态机等信息写入 Memory。这些信息可以从项目代码和文档中直接读取。

**Why:** 2026-03-19 犯了这个错误——为 Follow/Scheduler/Downloader 三个模块写了详细的架构记忆，本质上是 CLAUDE.md + FEATURE_CODE_MAP + ARCHITECTURE.md 的重复。用户指出系统提示明确禁止这种做法。

**How to apply:** 写入 Memory 前问自己："这条信息能通过读代码或文档得到吗？" 如果能，不存。只存以下类型：
- 用户纠正过的做法（feedback）
- 文档里没写的隐式知识（踩坑、非显而易见的风险）
- 外部系统引用（reference）
- 用户角色和偏好（user）
- 不能从代码/git 推导的项目背景（project，但限于决策动机、时间约束等）
