---
name: 禁用 git hooks（pre-commit / post-commit）
description: 用户不需要 git hooks 做文档质量检查或元数据更新，已删除
type: feedback
---

不要安装或恢复 `.git/hooks/pre-commit`（文档质量检查）和 `.git/hooks/post-commit`（文档元数据自动更新）。

**Why:** 用户明确要求不需要这些提交检查，hooks 还导致了文档日期累加 bug。

**How to apply:** 不要运行 `scripts/docs/install-doc-hooks.sh`，不要创建 git hooks。
