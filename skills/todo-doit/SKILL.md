---
name: todo-doit
description: >
  This skill should be used to resume work from a saved TODO.md, executing the next
  pending task autonomously. Use PROACTIVELY when: the user starts a new session and
  TODO.md exists with pending tasks, when the user says "continue", "继续", "接着做",
  "恢复", or expresses intent to resume previous work, or when another workflow needs
  to execute a queued task list (e.g., after ui-doctor generates action items saved
  via todo-write).
version: 1.0.0
---

# 会话恢复与任务执行

## 核心目标

读取 TODO.md 的"下一步行动"，自主执行任务，完成后更新 TODO.md。所有任务完成后自动删除 TODO.md 文件。

## 禁止行为

- **禁止询问用户** - 必须完全自主决策和执行
- **禁止跳过更新 TODO.md** - 每次执行后必须更新
- **禁止强行继续** - 任务全部完成时明确停止
- **禁止反复失败** - 失败 3 次立即停止并记录

---

## 执行流程

### 1. 读取 TODO.md

- 不存在 → 提示使用 `/todo-write`，停止
- 存在 → 继续

### 2. 解析状态（交叉验证）

**必须同时检查"下一步行动"和"待办任务"两个区域，以待办列表为最终真相：**

| 下一步行动 | 待办任务 | 判定 | 动作 |
|-----------|---------|------|------|
| `✅ 所有任务已完成` | 无 `- [ ]` 项 | 真完成 | 删除 TODO.md，输出完成信息，停止 |
| `✅ 所有任务已完成` | 仍有 `- [ ]` 项 | **状态不一致** | 从待办列表选最高优先级任务作为下一步，继续执行 |
| 有明确任务 | — | 正常 | 解析目标和验收标准，继续执行 |
| 格式不清晰 | — | 异常 | 提示更新格式，停止 |

### 3. 执行任务

- 遵循 CLAUDE.md 的开发规范
- 完全自主执行，根据验收标准判断完成
- 第 1 次失败：分析原因修复
- 第 2 次失败：换思路再试
- 第 3 次失败：停止，在 TODO.md 记录失败信息

### 4. 更新 TODO.md（必须执行）

1. 标记当前任务完成（`[x]` + 时间戳）
2. 从待办任务中选下一个（高优先级优先）
3. 更新"下一步行动"
4. 所有任务完成则：
   - 标记 `✅ 所有任务已完成`
   - 删除 TODO.md 文件

### 5. 完成报告

```
✅ 任务完成: [描述]
📝 变更文件: src/xxx.ts, tests/xxx.test.ts
🎯 下一步: [下一个任务] 或 "所有任务已完成"
```

---

## 核心原则

- **理解优先**: 先充分理解任务目标和验收标准
- **自主执行**: 完全不依赖用户输入
- **及时更新**: 任务完成立即更新 TODO.md
- **明确停止**: 完成时明确标记，不强行继续
- **Git 优先**: 遇到问题立即 git reset，不在错误基础上继续
