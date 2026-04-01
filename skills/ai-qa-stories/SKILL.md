---
name: ai-qa-stories
description: >
  This skill should be used when AI should autonomously verify user stories
  against a running Flutter app via Debug State Server. A true AI-autonomous
  loop: reads stories, executes curl sequences, validates assertions, reports
  or fixes failures. Use when the user says "验证故事", "跑用户故事",
  "regression", "run stories", "qa stories", or after a batch of code changes
  needs holistic verification beyond unit tests. Requires Debug State Server
  running and docs/user-stories/ to exist.
version: 0.2.0
---

# AI QA Stories — 用户故事自主验证

## 目的

AI 自主闭环：读取 `docs/user-stories/` 中的用户故事，通过 Debug State Server 逐步执行 curl 验证，确保核心 Happy Path 全部通过。这是真正的 AI 自主测试——不需要人类介入。

## 前置条件

1. 项目有 `docs/user-stories/` 目录且至少有 1 条故事
2. 端口通过标准协议发现（见 Step 0）

---

## 执行流程

### Step 0: Pre-flight + 自动启动

**端口发现**（按优先级，找到即停）：
1. `grep 'DEBUG_PORT' scripts/start-dev.sh` → 取变量值
2. `grep 'localhost:\d{4,5}' CLAUDE.md` → 从项目 CLAUDE.md 提取
3. `grep '_port.*=.*\d{4,5}' lib/dev_tools/debug_server.dart` → 从源码读取

**Server 检查**：
```bash
curl -s --connect-timeout 3 localhost:$PORT/providers
```

- ✅ 有响应 → 直接跳到 Step 1
- ❌ 无响应 → 进入**自动启动流程**（见下方）

#### 自动启动流程（Server 未运行时）

**核心原则：启动和加载故事并行，不傻等。**

```
┌─ 后台启动 App（run_in_background）──┐   ┌─ 前台加载故事 ─────────┐
│ 无参数 → open Simulator + start-dev │   │ 并行读取所有 story 文件  │
│ 有参数 → flutter run -d <设备>       │   │ 记录 story 列表          │
└─────────────────────────────────────┘   └────────────────────────┘
          ↓ 故事加载完后
    单次检查 Server：curl providers
          ↓
    ✅ 响应 → 继续 Step 2
    ❌ 未响应 → 用 start-dev.sh 的 run_in_background 等待
              → 完成通知到达后再次 curl
              → 仍未响应 → 输出错误，终止
```

**具体步骤**：

1. **后台启动 App**（`run_in_background: true`）— **必须先判断设备参数**：

   | 用户输入 | 启动命令 |
   |---------|---------|
   | `/ai-qa-stories`（无参数） | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `/ai-qa-stories macos` | `flutter run -d macos 2>&1` |
   | `/ai-qa-stories <其他设备>` | `flutter run -d <设备> 2>&1` |

   > **注意**：传了设备参数时，**不要** `open -a Simulator`，**不要**用 `start-dev.sh`。直接 `flutter run -d <设备>`。

2. **同时（不要等启动完成！）并行加载所有故事文件**（Step 1）

3. 故事加载完后，检查 Server 是否已就绪：
   - 就绪 → 继续
   - 未就绪 → 等待后台启动任务的完成通知（**不要自己写 for 循环轮询**）
   - 启动任务完成后再 curl 一次
   - 仍然不行 → 输出诊断信息（查看日志 `./scripts/view-dev-log.sh latest`），终止

**禁止行为**：
- ❌ 写 `for i in 1 2 3 ...` 的 curl 轮询循环
- ❌ 反复 `ps aux | grep flutter` 检查进程
- ❌ 反复 `tail /tmp/flutter_run.log` 查看编译进度
- ❌ 在 shell 命令中使用 `sleep`（会被 hook 拦截）
- ❌ 启动完成前就开始 curl 验证

### Step 1: 加载故事（并行，与启动同时进行）

**一次性并行读取**所有 `docs/user-stories/*.md` 文件（排除 README.md）。
按文件名编号排序。使用多个并行 Read 调用，不要逐个串行读取。

Server 就绪后，读取 `/providers` 响应，记录可用的 states/data/actions 列表，用于后续判断端点是否存在。

### Step 2: 准备环境

- 如果故事 01 的前置条件是"空状态"，执行 `./scripts/seed-test-data.sh clean`（如存在）
- 如果需要测试数据，执行 `./scripts/seed-test-data.sh`

### Step 3: 逐条执行

对每条故事的每个 Step：

1. **读意图** — 理解这步要做什么
2. **检查端点** — 先对照 Step 1 记录的 providers 列表，如果所需端点不存在，直接标记 ⚠️ 跳过（不要发 curl 去试 404）
3. **执行 curl** — 按文档中的命令执行（替换 `$PORT` 为实际端口）
4. **验证断言** — 对比返回值与文档中的期望
5. **判定结果**：
   - 断言通过 → 继续下一步
   - 断言失败 → 分析原因：
     - **代码 bug**：读相关代码，修复 → **安全重启 App**（见下方） → 从当前故事重新执行
     - **故事过时**（端点 404、字段名变了）：标记为"故事需更新" → 跳过继续

**安全重启 App**（修复 bug 后需要重启时）：

`run_in_background` 模式下没有交互式热重启，必须 kill → 等死 → 重启。**不干净的 kill 会导致新旧进程抢数据库（disk I/O error）**。

```bash
# 1. 先杀 App 进程（不只是 flutter run，要杀实际 App binary）
pkill -f "flutter run" 2>/dev/null; pkill -f "<app_binary_name>" 2>/dev/null

# 2. 确认进程已死（单次检查，不轮询）
pgrep -f "<app_binary_name>" || echo "App stopped"

# 3. 重启（同 Step 0 自动启动流程，用 run_in_background）
```

> `<app_binary_name>` 从 `pubspec.yaml` 的项目名或 build 产物路径推断。

**效率要求**：
- 同一故事内多个独立的 data 查询可以并行 curl
- 不要在每个 curl 之间输出冗长的思考过程，保持简洁

### Step 4: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx

### 结果
| 故事 | 状态 | 详情 |
|------|------|------|
| 01-first-time-user | ✅ 通过 | 5/5 步全部通过 |
| 02-daily-selection | ❌ 失败 | Step 3 断言失败：期望 selectedOption 非空，实际为 null |
| 03-data-management | ⚠️ 过时 | Step 2 端点 /action/xxx 返回 404 |

### 修复记录
- [已修复] 02-daily-selection Step 3: groupId 未传递导致选择失败（file:line）

### 需要人工处理
- 03-data-management: 故事文档需更新（端点路径已变更）
```

---

## 与 ai-explore 的关系

`ai-qa-stories` 是 `ai-explore` 的前置条件。只有所有故事通过后，才有意义进入启发式探索。`ai-explore` 会自动先调用本 skill。

## Gotchas / 踩坑点

1. **不硬编码端口** — 按 Step 0 端口发现协议
2. **故事按编号顺序执行** — 前序故事可能创建后序需要的数据
3. **autoDispose 的 State 可能为空** — 断言用 `/data/` 而非 `/state/`
4. **修复代码后必须安全重启** — 见 Step 3 的"安全重启 App"流程。直接 `pkill -f "flutter run"` 不够，必须同时杀 App binary 并确认死干净
5. **区分"代码 bug"和"故事过时"** — 404 = 故事过时；数据不对 = 可能是 bug
6. **用 /logs 辅助诊断** — `curl localhost:$PORT/logs?count=20` 看操作历史
7. **禁止手写轮询循环** — 不要写 `for i in 1 2 3 ... curl` 轮询。用 `run_in_background` 等完成通知
8. **利用 /providers 预判** — providers 列表可以提前跳过不存在的端点，避免无效 curl
9. **启动和加载并行** — App 启动是后台任务，前台同时加载故事文件，不要串行等待
