---
name: check-environment-first
description: Always identify which machine (Mac/WSL/NAS) you're running on before diagnosing network issues
type: feedback
---

排查问题时，先确认自己运行在哪台机器上，再决定排查方式。

**Why:** 2026-03-16 排查 Agent 502 时，误以为自己在 Mac 上，尝试 SSH 远程查看日志，浪费了多轮对话才发现自己就在 Windows WSL 本地，可以直接执行 `agent-ctl.sh`。

**How to apply:** 遇到跨设备问题（Mac ⇄ Windows ⇄ NAS）时，第一步检查 `hostname` 或当前工作目录，确认所处环境后再选择本地排查还是远程排查。
