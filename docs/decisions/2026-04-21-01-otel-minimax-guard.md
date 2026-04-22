# 2026-04-21-01 OTEL 隔离：增加 MiniMax-MCP guard，精简 direnv 输出，删除 claude-me alias

- **Date**: 2026-04-21
- **Status**: Accepted
- **Scope**: 跨项目工作流 — `~/LittleTree_Projects/cs/zsh/otel-isolation.zsh` + `~/AndroidStudioProjects/.envrc`

## 1. 问题 (What went wrong)

2026-04-17 上线的 OTEL 隔离方案（见 `otel-isolation.zsh` 头部注释）有两个未覆盖的漏洞被 Founder 追问出来：

**漏洞 1：MiniMax MCP 会绕过现有防御泄露模型身份**

Founder 自费的 MiniMax 模型配置在**全局** `~/.claude/settings.json` 的 `mcpServers.MiniMax` 字段里，任何目录启动 Claude Code 都会加载。进入工作目录 `~/AndroidStudioProjects/` 时 direnv 激活 OTEL 上报，此时若调用 MiniMax：

- `claude_code.tool_decision` 指标里 `tool_name` 字段值是 `mcp__MiniMax__web_search` / `mcp__MiniMax__understand_image` 等——**直接泄露"在用 MiniMax"这个事实**
- 公司 `OTEL_LOG_TOOL_DETAILS=1` 已开启，工具入参（搜索词、图片路径）也会进日志
- `device.owner=lingxiao.zhang@shihengtech.com` 与上述工具名绑定上报到公司 Prism 端点

用户的原意：MiniMax 是"轻量任务用的个人工具"（排查日志等），不希望公司知道使用事实。

**漏洞 2：direnv 默认输出太吵**

Founder 现场粘贴的 `cdpos` shell 输出：

```
direnv: loading ~/AndroidStudioProjects/.envrc
direnv: export +CLAUDE_CODE_ENABLE_TELEMETRY +NO_PROXY +OTEL_EXPORTER_OTLP_ENDPOINT +OTEL_EXPORTER_OTLP_PROTOCOL +OTEL_LOGS_EXPORTER +OTEL_LOGS_EXPORT_INTERVAL +OTEL_LOG_TOOL_DETAILS +OTEL_METRICS_EXPORTER +OTEL_METRIC_EXPORT_INTERVAL +OTEL_RESOURCE_ATTRIBUTES ~no_proxy/...
```

10+ 行 export 列表，实用信息量低（只需要知道"OTEL 开/关"即可）。

**顺便发现：`claude-me` alias 基本不用**

`otel-isolation.zsh` 里的 `claude-me='CLAUDE_CODE_ENABLE_TELEMETRY=0 ... claude'` alias 设计为"手动覆盖入口"，但 direnv + 默认关闭的策略已经足够稳，Founder 明确说"claude-me 基本不用了"。

## 2. 讨论过程 (How we thought about it)

**第一轮：澄清 OTEL 当前泄露面**

我最初误读了 `otel-isolation.zsh` 注释里的 "已部署的 .envrc：~/.claude/ 和 ~/LittleTree_Projects/"，推断为"那两个目录是强制关的，其他地方默认开"。Founder 立即纠正："我的策略是所有地方都关，只有在 `~/AndroidStudioProjects/` 才打开"。

纠正后重新梳理：
- 默认 shell 环境不含任何 `OTEL_*` → 默认关
- `~/AndroidStudioProjects/.envrc`：唯一激活点
- `~/.claude/.envrc` + `~/LittleTree_Projects/.envrc`：防御性双保险（unset 父 shell 可能残留的变量）

这个澄清很关键——否则给 `~/dev/temp` 补 `.envrc` 是完全多余的动作。

**第二轮：定位 MiniMax 的真实泄露路径**

区分两种 MiniMax 接入方式：
1. **Base URL 重定向**（如 `ANTHROPIC_BASE_URL=minimax_endpoint`）——此时 `api_request.model` 字段会泄露 MiniMax 模型名
2. **MCP server 挂载**（Founder 的方式）——MiniMax 的 HTTP 请求发生在 MCP 子进程里，**不经过 Claude Code 的 API 层**，所以 `api_request` 事件看不到 MiniMax

关键识别：漏洞在 `tool_decision` 指标的 `tool_name` 字段，不在 API 层。这决定了 guard 应该检测的是 **MCP 配置**，不是 API env var。

**第三轮：guard 触发条件的设计**

讨论三个备选触发源：
- `~/.claude/settings.json` 里 grep `"MiniMax"` → 最可靠，因为 MCP 加载就靠这份配置
- shell 里 `MINIMAX_API_KEY` / `MINIMAX_API_HOST` → 次要信号，防止以后改成环境变量驱动
- 定期扫描运行中的 MCP 子进程 → 过度设计，entry-time 检查足够

选择前两个 OR 关系触发（任一命中就拒绝激活 OTEL），在 MiniMax 生态未来变化时留余量。

**第四轮：失败模式下 direnv 的行为**

验证 `return 0` 在 direnv 源 .envrc 语境下的效果：
- direnv 源文件时 `return` 正常退出
- 由于 guard 位于 export 之前，退出时"无变量变化" → direnv 不打 `export +X +Y` diff
- 这同时解决了"消息太吵"的问题——failed-arm 天然静默

**第五轮：现场验证**

Founder 改完后 `cdpos` 观察到：
```
direnv: loading ~/AndroidStudioProjects/.envrc
⛔ MiniMax 挂载中 → OTEL 未激活（...）
```

第一行 `direnv: loading ...` 还在 → 原因是当前 shell 没重载 `DIRENV_LOG_FORMAT=""`。新终端会只剩第二行。这是预期行为，不是 bug。

## 3. 决策 (What we decided)

### 3.1 `~/LittleTree_Projects/cs/zsh/otel-isolation.zsh`

- **删除** `claude-me` alias（Founder 不再用）
- **新增** `export DIRENV_LOG_FORMAT=""`（抑制 direnv 默认 export 列表，让每个 .envrc 自己 echo 一行状态）
- **保留** `direnv hook zsh` 加载逻辑

文件从 22 行压到 17 行。

### 3.2 `~/AndroidStudioProjects/.envrc`

在文件**最前面**（任何 `export OTEL_*` 之前）加入 guard：

```bash
if { [[ -f "$HOME/.claude/settings.json" ]] && grep -q '"MiniMax"' "$HOME/.claude/settings.json" 2>/dev/null; } || \
   [[ -n "${MINIMAX_API_KEY:-}" || -n "${MINIMAX_API_HOST:-}" ]]; then
  unset MINIMAX_API_KEY MINIMAX_API_HOST
  echo "⛔ MiniMax 挂载中 → OTEL 未激活（先从 settings.json 移除 MiniMax 再 direnv reload）"
  return 0
fi
```

文件末尾加 `echo "🔴 OTEL ON · device.owner=..."`，让 armed 状态可见。

### 3.3 `~/.claude/.envrc` 和 `~/LittleTree_Projects/.envrc`

**不变**。这两份是防御性 unset，执行完静默退出；符合"no news is good news"的信号语义。

### 3.4 验证路径

Founder 新开终端 → `cdpos` → 应看到单行 `⛔ MiniMax 挂载中 → OTEL 未激活...`。若将来清空 settings.json 的 MiniMax 条目后 `direnv reload`，应看到 `🔴 OTEL ON · device.owner=...`。

## 4. 放弃的替代方案 (What we rejected and why)

**方案 A：把 MiniMax MCP 从全局 `settings.json` 迁到项目级 `.mcp.json`**
- 优点：从源头消除问题——工作目录下 MCP 根本不加载，guard 也可省略
- 缺点：Founder 想在**除工作目录外**的所有地方都能用 MiniMax，需要在多个非工作目录都部署 `.mcp.json`，维护面扩大；而且得决定"非工作目录"到底是哪些根（`~`？`~/dev/`？`~/LittleTree_Projects/`？）
- **否决理由**：这次没有做，但留在 TODO 里。Founder 最后一条消息明确说"好了就这样吧"，表示当前 guard 方案够用。未来若发现 guard 太容易被忘记 reload 就升级到 A 方案。

**方案 B：guard 不 return 0，而是改 `CLAUDE_CODE_ENABLE_TELEMETRY=0` 强制关**
- 优点：即使未来有新 OTEL 上报路径绕过总开关，也有 `OTEL_EXPORTER_OTLP_ENDPOINT` 未设置兜底
- 缺点：`.envrc` 剩余部分会继续 export device.id / endpoint / `OTEL_LOG_TOOL_DETAILS=1`，即使 `ENABLE_TELEMETRY=0` 也会在 direnv 输出里显示一长串 diff——破坏"消息精炼"目标
- **否决理由**：`return 0` 直接不 export 任何东西，效果等价（默认就是关的），且完全静默。更干净。

**方案 C：让 guard 扫描运行中的 MCP 子进程而非静态配置**
- 优点：能捕捉 Claude Code 启动后动态改 MCP 的情况
- 缺点：Claude Code 不支持运行时改 MCP；entry-time 静态检查已经覆盖所有启动路径
- **否决理由**：过度设计。

**方案 D：全局静默 direnv（`DIRENV_LOG_FORMAT=""`）vs 单独 `.envrc` 定制**
- 方案 D1：保留 direnv 默认输出，只在 `.envrc` 里精简
- 方案 D2：全局抑制 + 每个 `.envrc` 自己 echo
- **选择 D2**：用户的实际痛点是"export +X +Y 大列表"的重复性噪声，这个列表是 direnv 全局行为，单 `.envrc` 层面无法关闭。只能全局静默。

## 5. 预期影响 & 监控 (How we will know it works)

**AI 行为改变**：
- 未来会话读到 `~/AndroidStudioProjects/.envrc` 的 guard 代码时，能正确理解"这是防 MCP tool_name 泄露"，不会误判为冗余代码删掉
- 读到 `otel-isolation.zsh` 没有 `claude-me` alias 时，不会奇怪地重建它

**有效性信号**：
- Founder 的 OTEL 上报数据里 `tool_name` 字段不再出现 `mcp__MiniMax__*` → guard 生效
- Founder 不再被 direnv 长条 export 列表打扰 → 精简生效
- Founder 如果某天想在工作目录激活 OTEL，会被 guard 拦住，从而主动决定"要么移除 MiniMax，要么放弃这次 OTEL"——这是我们想要的决策点

**失效信号**：
- 如果 Founder 某天抱怨"我明明移除了 MiniMax 但 OTEL 还不激活" → `direnv reload` 未执行，或文件匹配字符串 `"MiniMax"` 有变体没覆盖
- 如果公司 Prism 指标里出现 `mcp__MiniMax__*` → guard 失守，可能是 settings.json 的 key 名变了（如大小写）或 MINIMAX 配置改成了别的方式注入

**回访评估**：
- 两周后（~2026-05-05）检查 Founder 是否有"忘了 reload" / "guard 被绕过"的反馈
- 若 Founder 开始频繁切换 MiniMax 开关位置，升级到方案 A（迁 `.mcp.json`）

## 修订 2026-04-21-01a：guard 判据从 "MCP 配置" 改为 "ANTHROPIC_BASE_URL"

**触发事实**：Founder 在 `cc-official` 状态下 `cdpos` 进工作目录，仍被 guard 拦住不激活 OTEL。原因：原 guard 检查 `~/.claude/settings.json` 里是否含 `"MiniMax"`，而 MCP 配置是静态的、永远命中，与 LLM provider 切换无关。

**重新识别两个泄露源**：
| 源 | 信号 | 何时泄露 |
|----|------|---------|
| LLM = 非官方 provider | `ANTHROPIC_BASE_URL` 非空 | 每次 api_request 事件的 `model` 字段（MiniMax-M2.7 / kimi-k2.5）自动泄露 |
| MCP tool = MiniMax | settings.json 静态挂载 | 仅在用户**主动调用** `mcp__MiniMax__*` 时 `tool_decision` 指标泄露 |

原 guard 混淆了两者。应该硬屏蔽源 1（自动、无法规避），源 2 靠用户纪律。

**Founder 的明确判断**（原话）：「我觉得主要判断依据是环境变量」，并指出 `ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"` 就是关键字段。

**新 guard**（覆盖原 3.2 小节）：

```bash
if [[ -n "${ANTHROPIC_BASE_URL:-}" ]]; then
  echo "⛔ 非官方 LLM: $ANTHROPIC_BASE_URL → OTEL 未激活（先 cc-official 再 direnv reload）"
  return 0
fi
```

- 覆盖所有非官方 provider（MiniMax、Kimi、未来任何 switcher）
- `cc-official` 会 `unset ANTHROPIC_BASE_URL`，自然放行
- 不再 check settings.json 的 MCP 配置（MCP 软泄露由用户纪律处理）

**放弃方案**：加软警告 `⚠️ MiniMax MCP 可用`。原因：每次进工作目录都打印反而变噪声，且 MCP 可用 ≠ 必然调用。用户纪律足够。

**更新后预期行为矩阵**：

| 当前状态 | `cdpos` 显示 |
|---------|--------------|
| `cc-official`（`ANTHROPIC_BASE_URL` 未设） | `🔴 OTEL ON · device.owner=...` |
| `cc-minimax` / `cc-kimi`（`ANTHROPIC_BASE_URL` 已设） | `⛔ 非官方 LLM: <url> → OTEL 未激活...` |

**影响范围**：仅改 `~/AndroidStudioProjects/.envrc` guard 段（第 10-20 行），其他部分不变。

## 附：相关代码位置

- `~/LittleTree_Projects/cs/zsh/otel-isolation.zsh` — direnv hook 加载 + log format 抑制
- `~/AndroidStudioProjects/.envrc` — 工作目录 OTEL 激活点 + MiniMax guard
- `~/.claude/.envrc` — 防御性 unset（本次未改）
- `~/LittleTree_Projects/.envrc` — 防御性 unset（本次未改）
- `~/.claude/hooks/ip-guard.sh` — SessionStart 时显示 IP + OTEL 状态（guard 命中时会显示 `✅ OTEL 关`）
- `~/.claude/settings.json` — MiniMax MCP 全局配置源（guard 检测对象）
