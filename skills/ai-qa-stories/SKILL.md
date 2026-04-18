---
name: ai-qa-stories
description: >
  Use when the user says "验证故事", "跑用户故事", "regression", "run stories",
  "qa stories", or after a batch of Flutter code changes needs holistic verification
  beyond unit tests. Verifies user stories against a running Flutter app via
  Debug State Server. Requires Debug State Server running and docs/user-stories/qa/
  to exist.
version: 2.5.0
---

# AI QA Stories — 用户故事自主验证

AI 自主闭环：读取 `docs/user-stories/qa/*.qa.md` 中的验证脚本，通过 Debug State Server 逐步 curl 验证，确保 Happy Path 全部通过。**纯验证，不修代码。**

## 双文件架构

| 文件 | 角色 | 本 skill 怎么用 |
|------|------|----------------|
| `docs/user-stories/qa/*.qa.md` | 验证脚本（编译产物） | **日常消费** — 直接读取并执行 |
| `docs/user-stories/*.md` | 产品故事（源码） | **仅在失败排障时参考** — 理解业务意图 |

## 核心原则

- **只验证，不修复** — 发现问题记录到报告，不改代码、不补端点、不重启 App
- **QA 过程中不重启 App**（优先用 `/cyborg/reset` 做 State Teardown；不存在则沿用故事编号顺序依赖）
- **故事按编号顺序** — 前序故事可能创建后序需要的数据
- **只读 qa/ 目录** — 不解析 Story 文件中的内容来执行验证
- **失败必附硬证据** — fail 时自动采集 Crime Scene 三件套（before 红框 / after / oracle diff），Founder 30 秒判真假
- **Server Bug 非测试缺陷** — 端点对账三态把 Debug Server 自身不一致单独红标，计入工具错误预算而非 qa 失败

---

## Debug Server 契约

与 `ai-explore` v4.0 共用同一份契约（单一来源，契约升级双边继承）。本 skill 期望的端点清单：

### 必需端点

| 端点 | 契约 |
|------|------|
| `/providers` | 列出所有 state / action 端点，用于 Step 3 对账 |
| `/state/*` `/data/*` | 数据面快照（优先 `/data/` 直读 Repository，见注意事项 4） |
| `/action/*` | 故事脚本执行通道 |

### 可选增强端点（实现则升级能力）

| 端点 | 未实现时的降级 |
|------|--------------|
| `/cyborg/reset` | State Teardown。缺失 → 沿用"故事编号顺序依赖" |
| `/cyborg/dom`（带 `generation` 字段） | stale-node 探测。缺失 → 无视觉证据层，失败详情仅 Oracle |
| `/cyborg/tap?nodeId=X&generation=Y`（quiet-frame + 2s 硬超时） | 防动画中间态误判。缺失 → curl 执行后多补一次 State 重读 |

**详见** `~/.claude/skills/ai-explore/SKILL.md` § Debug Server 契约。契约变更在 ai-explore v4 决策记录中同步维护。

---

## 执行流程

### Step 0: 环境准备（必须先执行）

**⚠️ 开始 QA 前，必须先运行 `prep-cyborg-env` Skill 或 `./scripts/prep-env.sh`**，确保环境干净。

这防止"幽灵状态"导致的错误验证结论——Flutter 内存状态与 DB 不一致时，QA 会给出完全错误的通过/失败判断。

### Step 0.5: 测试数据来源策略（关键）

空库 App（0 feeds / 0 articles / unauthenticated）会让 80% 的 scenario 因前置缺失而 SKIP/FAIL，QA 失去意义。必须先确定测试数据从哪来，按以下三档决策：

| 档位 | 判定条件 | 处理 |
|------|---------|------|
| **A. Seed 模式** | 项目有 `scripts/seed-test-data.sh` 或 `prep-env.sh` | 走 Step 0 标准路径，seed 脚本注入确定性数据 |
| **B. Remote Prep 模式** | 无 seed 脚本，但项目 CLAUDE.md 提供测试账号（server + user + password）且支持 remote 同步 | **允许** QA 在 Step 4 之前主动 `auth/login` + `sync/fullSync` 获取测试数据。这属于"**准备**"不是"**修复**"，不违反"只验证不修改代码"原则 |
| **C. 空库验证模式** | 以上皆无 | 照跑，但在报告开头明确标注「空库验证 — 预计大量 SKIP 属预期」，并建议 Founder 补 seed 脚本 |

**准备操作的边界**（B 档允许做的事）：
- ✅ 调用 `/action/auth/login`、`/action/sync/fullSync`、已知初始化性质的 action
- ✅ 调用项目 CLAUDE.md 中明确列为"测试配置"的端点
- ❌ 不改代码、不补端点、不重启 App、不清空已有用户数据
- ❌ 不调用破坏性 action（delete、logout 等）作为准备步骤

执行准备操作后，在报告「环境」小节记录：
```
测试数据来源: Remote Prep (login + fullSync) — feeds=N, articles=M
```

### Step 1: 发现 Server 端口

**端口来源只有一个**：从项目源码读取 `lib/dev_tools/debug_server.dart` 中的 `static const int port = NNNN;`。

禁止使用硬编码端口表。每个项目的 Debug Server 端口由各项目自行管理，Skill 只读源码。

```bash
# 从项目 debug_server.dart 读取端口
PORT=$(grep 'static const int port' lib/dev_tools/debug_server.dart | grep -oE '[0-9]+$' | tail -1)
echo "Project port: $PORT"

# 检查该端口是否已被其他 Flutter App 占用（避免误连）
OTHER_APP=$(lsof -ti :$PORT 2>/dev/null | xargs ps -p 2>/dev/null | grep -v PID | tr -d '\n')
if [ -n "$OTHER_APP" ]; then
  echo "WARN: Port $PORT occupied by: $OTHER_APP"
fi
```

**验证 Server 是否可达**：
```bash
RESPONSE=$(curl -s --connect-timeout 3 localhost:$PORT/providers 2>&1)
if echo "$RESPONSE" | grep -q '"ok":true'; then
  # 检查 actions 是否匹配当前项目（避免误连）
  if echo "$RESPONSE" | grep -qE '"actions":\['; then
    echo "Server reachable, checking project match..."
    # 提取 actions 数组中的第一个 action 路径作为项目标识
    SAMPLE_ACTION=$(echo "$RESPONSE" | grep -oE '"[a-z]+/[a-z]+"' | head -1 | tr -d '"')
    echo "Sample action: $SAMPLE_ACTION (用于验证项目匹配)"
    # 如果有其他 Flutter App 占着端口，这里会 report
  fi
else
  echo "Server not reachable on port $PORT"
fi
```

- ✅ 有响应且项目匹配 → 跳到 Step 2
- ⚠️ 有响应但项目不匹配（端口被其他项目占用）→ 跳过 Step 0，直接报告端口冲突，等待用户确认后重新启动
- ❌ 无响应 → 跳过 Step 0，启动 App

### Step 2: 加载 QA 文件

**并行** Read 所有 `docs/user-stories/qa/*.qa.md`，按文件名编号排序。

**如果 qa/ 目录不存在或为空**：
- 检查 `docs/user-stories/*.md` 是否存在旧格式故事
- 如有旧格式 → 提示用户：「检测到旧格式故事文件，需要先运行 `/generate-stories` 迁移到双文件架构」
- 如无故事 → 提示用户：「没有用户故事，需要先运行 `/generate-stories` 生成」

### Step 3: 端点对账（三态判定）

端点对账必须**实际调用**验证，不能只看 `/providers` 列表。对账结果分三态，区分"缺失"和"Server 自身不一致 Bug"：

1. **获取 providers 声明**：
   ```bash
   curl -s localhost:$PORT/providers
   ```

2. **对每个引用的端点实际调用**，按返回决定状态：

   | 状态 | 判定条件 | 报告处理 |
   |------|---------|---------|
   | ✅ **匹配** | providers 列表包含 + 实际调用返回 `"ok":true` | 相关 scenario 正常跑 |
   | ⏭️ **缺失** | providers 列表不包含 | 相关 scenario 标 SKIP |
   | 🔥 **Server Bug** | providers 列表**声明存在**，但实际调用返回 `"ok":false` 或 `Unknown state/action` | 相关 scenario 标 FAIL，**报告顶部单独红标**：Server 自身不一致 |

   ```bash
   # 示例判定
   RESP=$(curl -s localhost:$PORT/state/xxx)
   IN_PROVIDERS=$(echo "$PROVIDERS" | grep -q '"xxx"' && echo yes || echo no)
   OK=$(echo "$RESP" | grep -q '"ok":true' && echo yes || echo no)

   if [ "$IN_PROVIDERS" = "yes" ] && [ "$OK" = "yes" ]; then echo "MATCH"
   elif [ "$IN_PROVIDERS" = "no" ]; then echo "MISSING"
   else echo "SERVER_BUG"; fi
   ```

3. **输出对账结果**：

   ```
   端点对账: 10/12 匹配 | 1 缺失 | 1 Server Bug
     ⏭️ /action/auth/startLocalMode — 端点不存在（providers 未声明）
     🔥 /state/ai-processing — providers 声明但 handler 返回 Unknown（Server Bug，非测试缺陷）
   ```

### Step 4: 快照初始状态

并行查询关键状态端点，记录为初始快照：

```bash
curl -s localhost:$PORT/state/auth
curl -s localhost:$PORT/data/feeds    # 或项目对应的核心数据
```

### Step 5: 逐条执行验证

**故事间 State Teardown**（强推荐）：开始每个新故事前，如 `/cyborg/reset` 端点可用，调用一次清路由栈 + state 缓存。不可用时沿用"故事编号顺序依赖"。

```bash
# 新故事开始前
curl -s -o /dev/null -w '%{http_code}' localhost:$PORT/cyborg/reset
# 404 → 端点不存在，沿用顺序依赖；200 → 已清状态，当前故事可无脏状态开始
```

对每个 QA 文件的每个 Scenario：

1. **读 Intent** — 理解这步在验证什么
2. **检查端点是否存在** — 如果引用的端点在对账时被标记为缺失，直接跳过
3. **（可选）操作前快照** — 若 Cyborg Probe 可用且本 scenario 涉及 UI 变化，截一张 before.png（失败时才保留）
4. **执行 curl** — 按文件中的 bash 代码块顺序执行
5. **校验 Assert** — 比对实际返回与断言
6. 判定结果（三种）：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 丢弃 before.png，继续 |
| 🐛 失败 | **触发 Crime Scene 采集**：保留 before.png、截 after.png、快照 oracle.json；记录详情（见 Step 6） |
| ⏭️ 跳过 | 端点缺失 / 外部依赖 / 缺少数据，记录原因，继续 |

**Crime Scene 三件套采集**（仅 fail 时触发，pass 路径零开销）：

```bash
SNAP_DIR="screenshots/qa/$(date +%Y-%m-%d)"
mkdir -p "$SNAP_DIR"
PREFIX="$SNAP_DIR/${STORY_ID}_scenario_${SCENARIO_ID}"

# before.png 在 step 3 已截，fail 时移到最终位置
mv /tmp/qa_before_$$.png "${PREFIX}_before.png" 2>/dev/null

# after.png + oracle 快照
./scripts/screenshot-simulator.sh "${PREFIX}_after.png" 2>/dev/null  # 无 Simulator 时静默跳过
curl -s localhost:$PORT/state/route > "${PREFIX}_oracle.json"
# 追加当前 scenario 涉及的核心数据快照
curl -s localhost:$PORT/data/... >> "${PREFIX}_oracle.json"
```

无 Cyborg Probe / 无 Simulator 时，Crime Scene 降级为仅 oracle.json（纯文本），在报告中标注"无视觉证据"。

**效率要求**：同一 QA 文件内独立的状态查询可以并行 curl。

**失败时回溯**（可选）：如果某个 Scenario 失败且 Intent 不足以判断原因，读取对应的 Story 文件（`../NN-xxx.md`）获取业务上下文，辅助诊断。

### Step 6: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx

### 结果总览
| 故事 | 状态 | 通过/总数 |
|------|------|----------|
| 01-first-time-user | ✅ | 5/5 |
| 02-daily-use | 🐛 | 3/5 |

### 失败详情
#### 02-daily-use Scenario 3: {Intent 描述}
- **Intent**: {验证意图}
- **curl**: `curl -s -X POST localhost:$PORT/action/xxx -d '...'`
- **期望**: `success == true`
- **实际**: `{"error":"..."}`
- **Crime Scene**:
  - `screenshots/qa/2026-04-18/02-daily-use_scenario_3_before.png` (可缺失)
  - `screenshots/qa/2026-04-18/02-daily-use_scenario_3_after.png` (可缺失)
  - `screenshots/qa/2026-04-18/02-daily-use_scenario_3_oracle.json` (必备)
- **归因**: {四选一}
  - `server-handler-bug` — Debug Server 端 handler 问题（如 action 返回 success 但 state 不同步、providers 声明但 handler 未注册）→ 计入工具错误预算
  - `code-business-bug` — 业务代码实际 bug
  - `prereq-missing` — 测试前置数据/配置缺失（非代码问题）
  - `scenario-outdated` — 故事脚本过时（端点改名、断言字段改动）→ 建议 Founder 重跑 `/generate-stories`（v2.0 全覆盖模式，无单条重编）
- **Blocked by**（可选）: {如果此 FAIL 是其他 FAIL 的连带效应，填前置 scenario ID，便于报告聚合根因}

### 跳过项
- 03-xxx Scenario 5: 端点 /action/yyy 不存在，跳过
- 04-xxx Scenario 2: 需要外部 API key，跳过

### 端点对账不匹配项
- /data/settings/sync → 实际为 /data/settings-sync
- /state/articles → 端点不存在
```

### Step 6.5: 工具错误预算追踪

本次 run 的 `server-handler-bug` 归因条数要累入月度工具错误预算。目的：把 **Debug Server 自身的 bug** 与 **业务 bug** 分账，防止 Founder 在失败堆中找不到真问题、防止 skill 误报率失控。

**更新 `_scratch/ai-qa-stories/tool-errors/$(date +%Y-%m).md`**：

```markdown
# Purpose: 本月 ai-qa-stories 工具误报追踪
# Created: 2026-04-18

## 2026-04-18 第 N 次 run
- 总 scenario: 42, fail: 5
- server-handler-bug: 2
- scenario-outdated: 1
- code-business-bug: 2
- 累计本月: scenario 180, server-handler-bug 11 = **6.1%** ✅

## 阈值
默认 30%（与 ai-explore 对齐）。超阈值 → 报告顶部显著标注：
"⚠️ 本月 server-handler-bug 占比 X% 超阈值，建议优先修 Debug Server handler 而非继续跑 qa。"
```

---

## 进程管理

### 自动启动（仅 Server 未运行时）

1. **清空 Simulator**（杀所有 Flutter 进程，确保只有一个 App 在跑）：
   ```bash
   # 杀所有 Flutter 相关进程
   pkill -9 -f "flutter" 2>/dev/null
   pkill -9 -f "fvm" 2>/dev/null

   # 确认端口已释放
   sleep 1
   lsof -ti :$PORT 2>/dev/null && echo "WARN: Port still occupied after cleanup" || echo "Port clean"
   ```
   > **为什么杀所有**：同机器多项目可能各自占用相同端口（尤其是都写死 8790 的情况）。QA 一次只测一个 App，杀光后启动目标项目是最干净的状态。

2. **后台启动**（`run_in_background: true`）：

   | 用户输入 | 启动命令 |
   |---------|---------|
   | 无参数 | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `macos` | `./scripts/start-dev.sh --background --device macos` |
   | `ios` | `./scripts/start-dev.sh --background --device ios` |
   | `android` | 见下方「Android 专属」小节 |

3. **同时并行加载 QA 文件**（Step 2），不傻等
4. 等后台启动完成通知后 `curl providers` 确认就绪

### Android 专属（经验积累）

Android 路径有几个宿主机不透明的坑，必须单独处理：

1. **start-dev.sh `--device android` 可能失败** — 部分项目脚本把 `android` 字面量直接传给 `flutter run -d android`，在多设备或设备名不匹配时会报 "No supported devices found"。**回退策略**：

   ```bash
   DEV_ID=$(flutter devices 2>/dev/null | awk '/android-arm/{print $3; exit}')  # 取设备 ID
   [ -n "$DEV_ID" ] && nohup flutter run -d "$DEV_ID" > /tmp/flutter_run.log 2>&1 &
   ```

2. **必须配置 adb forward**（App 内 Debug Server 监听设备 localhost，宿主机 curl 进不去）：

   ```bash
   adb forward tcp:$PORT tcp:$PORT
   adb forward --list  # 验证
   ```

   大多数 Flutter 项目的 `scripts/start-dev.sh` 会自动调用 `setup_android_port_forward`，但若绕过脚本手动 `flutter run`，必须手工执行。

3. **首次安装可能被设备端拦截** — `adb: failed to install ... INSTALL_FAILED_USER_RESTRICTED: Install canceled by user`。需要在设备上开启「USB 安装」或在系统弹窗确认。遇到此错误 → 停止、提示 Founder、等待确认后重试。

4. **冷启动耗时** — 首次 Gradle 构建 + APK 安装约 **2-3 分钟**。用 `ScheduleWakeup(delaySeconds=180)` 等待，别用 sleep/轮询。

### 禁止行为

- ❌ 写 for 循环轮询 curl
- ❌ 反复 `ps aux | grep flutter`
- ❌ QA 过程中重启 App
- ❌ QA 过程中修改任何代码
- ❌ 在 shell 命令中使用 `sleep`
- ❌ 重复调用 start-dev.sh（每次调用都会启动新窗口！）

---

## 注意事项

1. **start-dev.sh 超时 ≠ 失败** — 脚本等待循环可能瞬间完成就报"超时"，flutter run 仍在后台编译。等 `run_in_background` 通知后 `tail` 日志看 DevTools URL
2. **端口冲突** — 同机器多项目可能各自有 Debug Server，检查 /providers 的 actions 是否匹配当前项目
3. **zsh URL 转义** — `curl "url?param=value"` 必须双引号包裹
4. **autoDispose State 可能为空** — 断言优先用 `/data/`（直读 Repository）而非 `/state/`（读 ViewModel 内存状态）
5. **QA 按编号顺序** — 前序 QA 可能创建后序需要的数据
6. **旧格式兼容** — 如果只有 `docs/user-stories/*.md` 而没有 `qa/` 目录，提示用户迁移

---

## 变更历史

- **2.5.0** (2026-04-18)：与 `ai-explore` v4.0 共享基础设施对齐（DRY）。5 项改动：新增「Debug Server 契约」章节（Generation ID / quiet-frame / `/cyborg/reset` 契约单一来源指向 ai-explore v4）、新增「工具错误预算」追踪（月度累计 `server-handler-bug` 占比，阈值 30%）、Step 5 失败时采集 Crime Scene 三件套（before 红框 / after / oracle.json）、Step 5 加故事间 State Teardown（`/cyborg/reset` 可选）、screenshots 路径对齐 user memory（`screenshots/qa/YYYY-MM-DD/`）。**不做 v3 大重写**——qa 本质 pass/fail 与 ai-explore 的 A/B/C/D 可信度梯度不同，persona×strategy / Behavioral Fuzzing / Ignorance Hash 不适用。详见 `~/.claude/docs/decisions/2026-04-18-06-ai-qa-stories-v2.5-alignment.md`。

- **2.4.0** 及更早：双文件架构（qa/ 编译产物 + stories/ 源码）、端点对账三态判定（MATCH / MISSING / SERVER_BUG）、测试数据三档策略（Seed / Remote Prep / 空库）、归因四选一、Android 专属启动路径。已被 v2.5 完整保留并扩展。
