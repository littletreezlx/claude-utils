---
description: Git规范提交

---

# Git规范提交

## 核心目标
基于当前对话上下文，生成 commit 信息并执行提交。

## 使用场景
用户在多轮对话中已完成代码修改，调用此命令让 Claude 总结变更并提交。

## 执行方式
1. **回顾对话上下文** - 你已经知道做了什么改动，无需重新分析
2. **确认变更范围** - `git status` 确认待提交文件与上下文一致
3. **生成 commit 信息** - 基于你已知的改动意图，而非逆向分析代码
4. **执行提交** - `git add` + `git commit`

## 提交格式
`<type>(<scope>): <description>`

类型：feat, fix, docs, style, refactor, perf, test, chore, ci

## 注意事项
- 优先使用对话中已知的改动意图，不要重新读代码猜测
- 如果 `git status` 显示的文件与对话内容不符，询问用户
- 排除敏感文件（.env, credentials 等）