---
name: pick-server/.dev.vars 故意纳入版本控制
description: 用户明确要求把 pick-server/.dev.vars 跟随私有仓库同步，禁止重新加 gitignore
type: feedback
originSessionId: 166ebf6d-669f-44c9-afde-8a6ec523c428
---
`pick-server/.dev.vars` 包含 DEEPSEEK_API_KEY / SILICONFLOW_API_KEY / HMAC_SECRET，**故意**从 .gitignore 移除。

**Why:** 用户跨设备开发，私有仓库 + 同步策略优先于"密钥不入仓"的默认规范（用户决策 2026-04-13）。

**How to apply:**
- 看到 `.dev.vars` 文件时不要建议或自动加回 gitignore
- code-review/security-audit skill 报告"密钥泄露风险"时仅作为风险提示，不要主动修复
- 风险已记录在 pick-server/.gitignore 注释里，删除注释也不要做
- 如果用户某天要把仓库转公开 → 主动提醒先 `git filter-repo` 清掉 .dev.vars 历史
