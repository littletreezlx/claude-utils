---
name: commit 自动 / push 需确认 — 别再问
description: CLAUDE.md 明写 commit 自动 push 需确认，不要在完成任务后问"现在 commit 吗"
type: feedback
originSessionId: 64a2f534-9a91-48bb-801e-9552a65720f4
---
完成一个完整功能或 bug 修复后，直接运行测试并 `git commit`，**不要**询问用户是否 commit。只有 `git push` 才需要用户确认。

**Why:** 用户已在 `~/.claude/CLAUDE.md` 的「Git 策略」和「速查表」里明确写过：
- "自主提交：完成一个完整功能后，直接运行测试并 commit，无需询问用户"
- "不允许直接推送到远程仓库（push 仍需用户确认）"

在已经确认过修复方案并跑通测试后，再问"我现在 commit 吗"会让用户觉得我没读懂规则。用户原话："push 肯定不能自动啊，commit 当然是自动啊，这你都读不懂吗？"

**How to apply:**
- 测试通过 → 直接 `git add <specific files>` + `git commit`
- 只有涉及 `git push`、`git push --force`、`git reset --hard`、删分支等破坏性/对外可见操作时才询问
- 确认修复方案那一步已经是用户的"授权"，不需要为 commit 再要一次
- 写 commit message 时按项目风格（中文描述 + 解释 why，不是 what）
