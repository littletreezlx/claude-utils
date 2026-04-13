---
name: web-gemini 输出精简
description: /web-think 及同类 Web 转发命令只输出可复制的 Prompt，不要单独输出现状分析
type: feedback
originSessionId: 31d317a7-63cc-4fb6-8718-d5a82268f5c0
---
Web 转发类命令（`/web-think`、`/web-gem-project`）的输出应该干净利落，用户拿到就能直接复制给 Gemini。

**Why:** 现状分析已经融入了 Prompt 里，单独输出一遍是冗余信息，增加用户阅读负担。

**How to apply:** Phase 1 研究不输出，Phase 2 的 Prompt 是唯一输出，Prompt 前后不加多余说明。
