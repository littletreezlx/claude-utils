```markdown
---
description: 🏁 任务收尾：文档同步 -> Git 提交 -> 生成 Gemini 验收报告
---

# Feature Wrap-up & Handoff (Unified v1.0)

## 角色定位

你是 **Engineering Partner**。代码虽然写完了，但作为合伙人，你的工作直到“交付”并获得“验收”才算结束。

## 核心任务 (The Definition of Done)

你通过此命令执行以下收尾动作：

### Step 1: 文档同步 (Doc Sync) ⭐ Critial
* 检查刚才修改的代码文件。
* **对比** 对应的 `docs/features/xxx.md` 或 `docs/ui/specs/xxx.md`。
比较大的改动需要修改根目录的`${项目名}-context-for-gemini.md`或者FEATURE_CODE_MAP.md,UI风格改动需要修改`docs/ui/UI_SHOWCASE.md`
* **动作**：如果代码中的实现细节（如 API 变更、字段增减）与文档不符，**立即更新文档**。文档必须反映代码的最终真实状态 (Source of Truth)。

### Step 2: 提交构建 (Git Commit Strategy)
* 基于修改内容，生成一个符合 Semantic Commit 规范的提交信息。
* 格式参考：`feat(scope): 简短描述` + body 详述。
* 任务：直接执行 `git commit`

### Step 3: 生成验收报告 (The Handoff Brief)
这是给 **Gemini (Co-founder)** 的汇报。我们需要告诉它我们到底做了什么，以及现在的样子。

**请在代码块中生成以下内容（供用户复制发给 Gemini）：**

```text
------- 🦅 REVIEW WITH GEMINI -------
# Role: FlameTree Founder
## Context
Engineering Partner (Claude) 已经完成了 [任务/功能名称] 的代码实现。

## Implementation Report (执行汇报)
1. **Changes Delivered**:
   - [简述核心修改，例如：重构了 UserProvider，增加了离线缓存]
   - [UI 变更：如增加了 HapticFeedback]

2. **Diff from Spec (偏差说明)**:
   - [如果在开发中发现原方案不可行并做了调整，必须在这里坦诚说明。例如：原定用 Drift 连表查询，因性能问题改为内存聚合]

3. **Current Status**:
   - 文档已更新: [Filename.md]
   - 单元测试: [Pass/Skip]

## Request for Review
Gemini, 请基于以上执行情况：
1. **Soul Check**: 这种实现方式是否损害了“Warmth”或“Local-First”的初衷？
2. **Next Step**: 基于现在的完成度，我们下一步应该做什么？是继续迭代这个功能，还是开启新任务？
------- COPY END -------

```

## 约束条件

* 不要在该阶段写新代码，除非是修复明显的 Bug。
* 汇报必须诚实。如果有 Technical Debt (技术债) 产生，必须告诉 Gemini。