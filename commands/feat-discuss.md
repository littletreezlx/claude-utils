---
description: 启动新功能：工程现状梳理 -> 架构咨询(Gemini) -> 方案落库(Checklist)
---

# Feature Discussion - 路由入口

默认使用 `/feat-discuss-local-gemini`（自动调用 Gemini API，全流程自动化）。

备选：`/feat-discuss-web-gemini`（生成 Prompt 供用户手动复制到 Gemini Web）。

**执行**：直接调用 `/feat-discuss-local-gemini`，将 `$ARGUMENTS` 原样传递。
