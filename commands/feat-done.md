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

按 `/git-commit` 规范执行提交。

### Step 3: 生成验收报告

生成一份给产品/架构角色（如 Gemini）的汇报，供用户复制转发。

**核心要素**（按需取舍）：
- 做了什么（变更概述）
- 与 Spec 的偏差（如有）
- 当前状态（文档、测试）
- 请求 Review 的问题

**原则**：诚实汇报，技术债务必须说明

## 约束条件

- 不在该阶段写新代码（除非修复明显 Bug）
