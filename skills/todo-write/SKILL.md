---
name: todo-write
description: >
  This skill should be used to save current session context, progress, and pending
  tasks to TODO.md for later resumption. Use PROACTIVELY when: the conversation is
  getting long and tasks remain, when the user says "save", "保存", "先到这", "下次继续",
  or expresses intent to pause work, when a workflow (like ui-doctor or health-check)
  generates a list of actionable items that should be tracked, or when complex multi-step
  work needs to be persisted across sessions.
version: 3.0.0
---

# 会话保存

保存当前会话的进度、上下文和待办任务到 `TODO.md`，便于 `/todo-doit` 在**新会话**中恢复执行。

> **核心约束**：`todo-doit` 在新会话中运行，**没有当前对话的记忆**，且被要求**完全自主执行、禁止询问用户**。因此 TODO.md 必须包含足够的上下文让一个"失忆的 AI"能独立完成所有剩余任务。

---

## 任务描述格式

每个任务包含：
- **🎯 目标**：要达成什么（可验证）
- **📁 文件**：关键路径 + 操作类型
- **✅ 完成标志**：客观可验证的标准
- **⬅️ 依赖**（可选）：前置任务，有依赖时必须标注

❌ `- [ ] 修复用户模块的 bug`

✅
```
- [ ] 修复 Safari 隐私模式下登录后刷新被踢出
  - 🎯 Safari 隐私模式下登录后刷新保持登录
  - 📁 `src/auth/token.ts:45` - localStorage fallback 到 sessionStorage
  - ✅ Safari 隐私模式下刷新保持登录
```

带依赖示例：
```
- [ ] 集成新的 Token 刷新逻辑到登录流程
  - 🎯 登录后自动使用新 Token 管理器
  - 📁 `src/auth/login.ts` - 替换旧 TokenStore 调用
  - ✅ 登录 → 等待 Token 过期 → 自动刷新 → 不中断会话
  - ⬅️ 依赖: "修复 Safari 隐私模式下登录后刷新被踢出"
```

---

## 输出文件：TODO.md

```markdown
# TODO - [日期]

## 会话目标
> 一句话说明本轮工作在做什么、为什么做

[例：重构 auth 模块，将 Token 存储从 localStorage 迁移到 sessionStorage，解决隐私模式兼容问题]

## 🎯 下一步行动
> 自动执行的下一个任务（从待办列表中选最高优先级）

- [ ] [任务标题]
  - 🎯 / 📁 / ✅

## 当前进度
整体进度: X/Y | 当前阶段: [描述]

## 本次完成
- [x] [任务]

## 待办任务
### 高优先级
- [ ] [任务]（含 🎯/📁/✅/⬅️）
### 普通优先级
- [ ] [任务]

## 关键上下文

### 代码状态
- **当前分支**: [分支名]
- **未提交变更**: [有/无，若有则列出关键文件]
- **已改动文件**: [本次会话修改过的文件清单，含简要说明]

### 技术决策
> 本次会话做了哪些关键选择，新会话的 AI 需要沿用而非重新决策

- [决策内容] — 原因: [为什么这么选]

### 踩坑记录
> 失败方案和原因，防止新会话重蹈覆辙

- ❌ [尝试过的方案] — 失败原因: [具体原因]

### 注意事项
> 执行剩余任务时需要知道的额外信息（环境要求、特殊配置、已知限制等）

- [注意事项]
```

---

## 编写原则

- **为失忆的 AI 写作**：假设读者对当前会话一无所知，但可以读代码和 git log
- **格式标准化**：便于脚本解析
- **下一步唯一**：只写一个（最优先的那个）
- **完成即停止**：所有任务完成时标记 `✅ 所有任务已完成`
- **上下文必填**：会话目标、代码状态、技术决策三个区块不得省略（踩坑记录和注意事项无内容时可写"无"）

---

## 一致性约束（铁律）

**"下一步行动"与"待办任务"必须一致，以待办列表为最终真相：**

- 待办中仍有 `- [ ]` → 禁止标记 `✅ 所有任务已完成`，必须选最高优先级填入下一步
- 待办全部 `- [x]` 或为空 → 才可标记完成
- 写入后自检：扫描 `- [ ]`，若存在则下一步不得为完成状态
- 有 `⬅️ 依赖` 的任务，其前置任务未完成时不得选为下一步
