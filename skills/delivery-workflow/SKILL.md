---
name: delivery-workflow
description: >
  This skill should be used when a complete feature, bug fix, or meaningful
  unit of work is finished, when all code changes are done and tests pass,
  when the user says "feature done", "wrap up", "收尾", "交付", or expresses
  completion of a development task. Orchestrates the full delivery pipeline:
  doc sync, git commit, and acceptance report generation.
version: 0.1.0
---

# Delivery Workflow — 功能收尾与交付

## 目的

一个完整的开发单元完成后，自动执行交付流水线。扮演 **Engineering Partner** 角色，处理收尾阶段。

## 触发条件

当以下条件**全部满足**时启动：

1. 一个完整的 feature、bugfix 或有意义的 refactor 已完成
2. 代码变更已完成，测试通过
3. 出现以下信号之一：
   - 用户说"完成"、"收尾"、"交付"、"feature done"、"wrap up"
   - 一个完整的功能开发周期明显结束
   - 用户明确请求交付/收尾

## 执行流水线

### Step 1: 文档同步（Doc Sync）

- 检查本次对话中修改的代码文件
- **FEATURE_CODE_MAP 一致性验证**：项目有该文件时，自动检查本次新增/删除/重命名的文件是否在 Map 中有对应条目，缺失则补充，失效则修正
- 对比项目文档体系中对应的文档（功能文档、UI 规范等）
- 较大改动需更新功能索引（如 `FEATURE_CODE_MAP.md`）和路线图（如 `ROADMAP.md`）
- UI 风格改动需更新设计系统文档（如 `UI_SHOWCASE.md`）
- **动作**：代码实现与文档不符时，**立即更新文档**

### Step 1.5: 项目级交付检查（Project-specific Checks）

检查当前项目的 CLAUDE.md 是否定义了交付前必须执行的工程约束检查（如静态分析、架构边界检查等），如有则执行。任一检查失败则修复后再提交。

### Step 2: Git 提交

确认测试通过后，触发 git-workflow skill 执行提交。

### Step 3: 生成验收报告

生成一份给产品/架构角色（如 Gemini）的汇报，供用户复制转发。

**核心要素**（按需取舍）：
- 做了什么（变更概述）
- 与 Spec 的偏差（如有）
- 当前状态（文档、测试）
- 需确认的技术决策（陈述式，说明背景和选择理由）

**原则**：诚实汇报，技术债务必须说明。

## 约束

- 该阶段不写新代码（除非修复明显 Bug）
- 不新增/删除文件（文档更新除外）
- 不修改依赖文件
