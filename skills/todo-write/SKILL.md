---
name: todo-write
description: >
  This skill should be used to save current session context, progress, and pending
  tasks to TODO.md for later resumption. Use PROACTIVELY when: the conversation is
  getting long and tasks remain, when the user says "save", "保存", "先到这", "下次继续",
  or expresses intent to pause work, when a workflow (like ui-doctor or health-check)
  generates a list of actionable items that should be tracked, or when complex multi-step
  work needs to be persisted across sessions.
version: 2.0.0
---

# 会话保存

保存当前会话的进度和待办任务到 `TODO.md`，便于 `/todo-doit` 恢复执行。

---

## 任务描述格式

每个任务包含：
- **🎯 目标**：要达成什么（可验证）
- **📁 文件**：关键路径 + 操作类型
- **✅ 完成标志**：客观可验证的标准

❌ `- [ ] 修复用户模块的 bug`

✅
```
- [ ] 修复 Safari 隐私模式下登录后刷新被踢出
  - 🎯 Safari 隐私模式下登录后刷新保持登录
  - 📁 `src/auth/token.ts:45` - localStorage fallback 到 sessionStorage
  - ✅ Safari 隐私模式下刷新保持登录
```

---

## 输出文件：TODO.md

```markdown
# TODO - [日期]

## 🎯 下一步行动
> 自动执行的下一个任务

- [ ] [任务标题]
  - 🎯 / 📁 / ✅

## 当前进度
整体进度: X/Y | 当前阶段: [描述]

## 本次完成
- [x] [任务]

## 待办任务
### 高优先级
- [ ] [任务]（含 🎯/📁/✅）
### 普通优先级
- [ ] [任务]

## 关键上下文
- 技术决策 / 已尝试但失败的方案
```

---

## 编写原则

- **格式标准化**：便于脚本解析
- **下一步唯一**：只写一个（最优先的那个）
- **完成即停止**：所有任务完成时标记 `✅ 所有任务已完成`

---

## 一致性约束（铁律）

**"下一步行动"与"待办任务"必须一致，以待办列表为最终真相：**

- 待办中仍有 `- [ ]` → 禁止标记 `✅ 所有任务已完成`，必须选最高优先级填入下一步
- 待办全部 `- [x]` 或为空 → 才可标记完成
- 写入后自检：扫描 `- [ ]`，若存在则下一步不得为完成状态
