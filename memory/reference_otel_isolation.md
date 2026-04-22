---
name: OTEL 隔离与非官方 provider guard 配置
description: Founder 的 Claude Code OTEL 上报默认关闭，仅 ~/AndroidStudioProjects/ 激活；ANTHROPIC_BASE_URL 非空（cc-minimax/cc-kimi 等）会触发 guard 拒绝激活
type: reference
---

Founder 使用的 Claude Code telemetry 隔离策略（默认关、局部开）：

- **默认状态**：全局 shell 环境不 export 任何 `OTEL_*`。任何目录启动 Claude Code 都是 `✅ OTEL 关`（由 `~/.claude/hooks/start-hook.sh` 在 SessionStart 注入模型上下文）
- **唯一激活点**：`~/AndroidStudioProjects/` 下的 `.envrc`，direnv 进目录时 export 公司 Prism 端点 + `device.owner=lingxiao.zhang@shihengtech.com` + `OTEL_LOG_TOOL_DETAILS=1`
- **Provider guard**：该 `.envrc` 开头检查 `ANTHROPIC_BASE_URL` 是否非空，命中则 `return 0` 拒绝激活 OTEL。原因：`cc-minimax` / `cc-kimi` 等 provider switcher（见 `~/.claude/my-scripts/config-manager/cc-provider.zsh`）会 export 此变量，让 Claude Code 走非官方 endpoint；若 OTEL 同时开着，`model` 字段（MiniMax-M2.7 / kimi-k2.5）会进 api_request 事件泄露给公司 Prism。`cc-official` 会 unset `ANTHROPIC_BASE_URL`，自然放行。
- **为什么不查 settings.json 的 MCP 配置**：MCP 是静态配置且永远挂载（tool_decision 指标只有主动调用 `mcp__MiniMax__*` 才会泄露），靠纪律规避而非 guard。主判据是"当前 session 走哪个 LLM endpoint"这个动态信号。
- **防御性 unset**：`~/.claude/.envrc` 和 `~/LittleTree_Projects/.envrc` 做兜底 unset，防父 shell 残留污染
- **direnv 静默**：`~/LittleTree_Projects/cs/zsh/otel-isolation.zsh` 设 `DIRENV_LOG_FORMAT=""` 抑制默认 export 列表，每个 `.envrc` 自己 `echo` 一行状态

决策过程与方案对比见 `~/.claude/docs/decisions/2026-04-21-01-otel-minimax-guard.md`。

**碰到相关场景时**：
- Founder 问"OTEL 会不会上报 X" → 先看当前 shell 是否在 `~/AndroidStudioProjects/` 子树下；不在就是关的
- 看到 `.envrc` 里奇怪的 MiniMax grep 逻辑 → 不要删，是故意的 guard
- 想帮 Founder 在 `~/dev/` 等目录补 `.envrc` → 不必要，默认就是关的
