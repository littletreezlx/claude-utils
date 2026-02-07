---
description: 任务收尾：文档同步 -> Git 提交 -> 生成验收报告
---

# Feature Wrap-up & Handoff

## 角色定位

你是 **Engineering Partner**。代码写完后，执行收尾交付流程。

## 核心任务

### Step 1: 文档同步 (Doc Sync)

- 检查刚才修改的代码文件
- **对比**对应的 `docs/features/xxx.md` 或 `docs/ui/specs/xxx.md`
- 较大改动需更新 `docs/FEATURE_CODE_MAP.md`、`docs/ROADMAP.md`（功能完成度）
- UI 风格改动需更新 `docs/ui/UI_SHOWCASE.md`
- **动作**：如果代码实现与文档不符，**立即更新文档**

### Step 2: 提交构建

- 基于修改内容，生成符合 Semantic Commit 规范的提交信息
- 格式：`feat(scope): 简短描述` + body 详述
- 执行 `git commit`

### Step 3: 生成验收报告

生成一份给产品/架构角色（如 Gemini）的汇报，供用户复制转发：

```text
------- REVIEW -------
# Implementation Report

## Context
Engineering Partner (Claude) 已完成 [任务/功能名称] 的代码实现。

## Changes Delivered
- [核心修改概述]
- [UI 变更概述]

## Diff from Spec (偏差说明)
- [如有偏差，坦诚说明原因]

## Current Status
- 文档已更新: [文件名]
- 测试: [Pass/Skip/Fail]

## Request for Review
1. 实现方式是否符合产品愿景？
2. 下一步应该做什么？
------- END -------
```

## 约束条件

- 不在该阶段写新代码（除非修复明显 Bug）
- 汇报必须诚实，如有技术债必须说明
