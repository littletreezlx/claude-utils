---
name: git-workflow
description: >
  This skill should be used when code changes have passed tests and are ready
  to commit, when a feature or bug fix is complete, when the user says "done",
  "finished", "commit", or expresses completion intent, or when feat-done
  needs to create a commit. If feat-done is orchestrating the delivery flow,
  this skill is called as its Step 3 — do not independently trigger. Handles conventional commit
  message generation and git commit execution based on conversation context.
version: 0.1.0
---

# Git Workflow — 自动提交

## 目的

代码变更完成且测试通过后，自动生成 commit 信息并执行提交。

## 触发条件

当以下条件**全部满足**时启动：

1. 对话中已进行了代码修改
2. 测试已通过（或无需测试的场景）
3. 出现以下信号之一：
   - 用户明确说"完成"、"提交"、"commit"、"done"
   - 一个完整的 feature/bugfix/refactor 单元已结束
   - feat-done 请求提交
   - test-workflow skill 确认修复后测试全部通过

## 执行流程

1. **回顾对话上下文** — 已经知道改了什么、为什么改，不要重新读代码猜测
2. **确认变更范围** — `git status` 验证待提交文件与对话内容一致
3. **生成 commit 信息** — 基于已知意图，而非逆向分析 diff
4. **执行提交** — `git add` 相关文件 + `git commit`

## Commit 格式

`<type>(<scope>): <summary>`

Type 列表：feat, fix, docs, style, refactor, perf, test, chore, ci

### 精炼原则

- 只写一行 summary，不加 body，除非涉及 3 个以上独立变更点
- summary 写**意图**（为什么改），不罗列文件或代码细节
- 控制在 72 字符以内
- 禁止添加 `Co-authored-by` 等署名行

### 示例

```
# ✅ 好
refactor(offlineSync): 用显式方法调用替换可变字段注入

# ❌ 差 — 罗列实现细节
refactor(offlineSync): 用 bindTrigger/triggerSync 替换接口中的 syncTrigger 可变字段
```

## 约束

- 若 `git status` 显示的文件与对话内容不符，**必须询问用户**再提交
- 禁止 push 到远程（push 需用户明确确认）
- 禁止 amend 已有提交（除非用户明确要求）
- 禁止跳过 pre-commit hooks（不使用 --no-verify）
- 优先 `git add <具体文件>` 而非 `git add -A`
