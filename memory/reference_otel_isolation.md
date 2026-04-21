---
name: OTEL 隔离与 MiniMax guard 配置
description: Founder 的 Claude Code OTEL 上报默认关闭，仅 ~/AndroidStudioProjects/ 激活；MiniMax MCP 会触发 guard 拒绝激活
type: reference
---

Founder 使用的 Claude Code telemetry 隔离策略（默认关、局部开）：

- **默认状态**：全局 shell 环境不 export 任何 `OTEL_*`。任何目录启动 Claude Code 都是 `✅ OTEL 关`（由 `~/.claude/hooks/start-hook.sh` 在 SessionStart 注入模型上下文）
- **唯一激活点**：`~/AndroidStudioProjects/` 下的 `.envrc`，direnv 进目录时 export 公司 Prism 端点 + `device.owner=lingxiao.zhang@shihengtech.com` + `OTEL_LOG_TOOL_DETAILS=1`
- **MiniMax guard**：该 `.envrc` 开头检查 `~/.claude/settings.json` 是否还挂着 MiniMax MCP，命中则 `return 0` 拒绝激活 OTEL（避免 `mcp__MiniMax__*` 工具名泄露给公司 Prism）
- **防御性 unset**：`~/.claude/.envrc` 和 `~/LittleTree_Projects/.envrc` 做兜底 unset，防父 shell 残留污染
- **direnv 静默**：`~/LittleTree_Projects/cs/zsh/otel-isolation.zsh` 设 `DIRENV_LOG_FORMAT=""` 抑制默认 export 列表，每个 `.envrc` 自己 `echo` 一行状态

决策过程与方案对比见 `~/.claude/docs/decisions/2026-04-21-01-otel-minimax-guard.md`。

**碰到相关场景时**：
- Founder 问"OTEL 会不会上报 X" → 先看当前 shell 是否在 `~/AndroidStudioProjects/` 子树下；不在就是关的
- 看到 `.envrc` 里奇怪的 MiniMax grep 逻辑 → 不要删，是故意的 guard
- 想帮 Founder 在 `~/dev/` 等目录补 `.envrc` → 不必要，默认就是关的
