---
name: session-discipline
description: 会话纪律 - 会话结束时必须保存进度，新会话开始时必须检查 TODO.md
type: feedback
---

会话结束时必须主动保存上下文（todo-write），新会话开始时必须检查 TODO.md。

**Why:** 过去会话经常在中途结束而未保存进度，导致下次会话完全失忆，重复探索同样的代码路径。已在 CLAUDE.md 中添加「会话衔接规则」段落。

**How to apply:** 当用户说"先这样"、"下次再说"、或连续无新需求时，自动触发 todo-write 保存未完成工作。不需要用户提醒。
