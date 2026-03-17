---
name: 文档元数据 hook 日期格式 bug
description: post-commit hook 中 sed 正则 [0-9]* 只匹配纯数字导致日期累加，已修复为 [0-9][0-9-]*
type: feedback
---

禁止在 sed 正则中用 `[0-9]*` 匹配日期字符串（如 `2026-03-12`），必须用 `[0-9][0-9-]*` 以匹配含连字符的完整日期。

**Why:** post-commit-doc-update hook 用 `[0-9]*` 只匹配到年份 `2026`，剩余的 `-03-12` 保留在原文中，每次提交日期就追加一段，累积成 `2026-03-12-03-12-03-12...`。

**How to apply:** 修改文档元数据相关脚本时，确保日期正则能匹配 `YYYY-MM-DD` 全格式。已在 `scripts/git-hooks/post-commit-doc-update` 修复。
