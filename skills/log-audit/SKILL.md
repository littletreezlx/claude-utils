---
name: log-audit
description: >
  Use to audit data-plane logging coverage across an entire project — find
  streaming/async/pipeline code that lacks runtime liveness logs (first-data
  marker + periodic counter) per `~/.claude/guides/validation-hygiene.md` §5.
  Use when user says "log audit", "审日志", "查日志覆盖", "看下日志写得怎样",
  "日志补全", "log hygiene", or after a debugging incident exposed thin
  logging. Outputs severity-sorted TODO list, doesn't auto-fix code.
version: 1.0.0
---

# Log Audit — 数据面日志覆盖审计

## 角色定位

你是项目级数据面日志覆盖的诊断工具。只识别"流式/异步/管道"代码是否符合 `guides/validation-hygiene.md` §5 的活性日志标准（lifecycle + first-data marker + 周期 counter），输出可塞进 `TODO.md` 的待办清单。**不修改任何代码**——修复交给 `/todo-doit` 或人工挑选。

类比：`flutter doctor` / `ui-doctor` 的同类工具，专管"运行时可观测性"这一维。

## 适用与不适用

### 适用（属于扫描对象）

具备"持续/周期/流动"特征的代码：

- 媒体管道：屏幕采集（ScreenCapturer）、音视频编解码器（Encoder/Decoder）、推流（Publisher/Renderer）
- 通信通道：WebSocket 连接、SSE handler、long-polling、gRPC streaming
- 消息处理：MQ 消费者、事件总线订阅、Pub/Sub
- 数据流：Stream / Flow / Observable / RxJS pipeline、Kafka consumer
- 后台任务：长跑 Worker、Scheduler、Coroutine 中的 `while(true)` / `while(active)` 循环
- I/O 流转：file watcher、pipe 消费、tail-style reader

### 不适用（跳过，避免范围漂移）

- 一次性请求（HTTP RPC 单次调用）
- UI 渲染回调（一次性事件型）
- 单元测试代码
- 生成的代码（protobuf / .g.dart / .pb.go 等）
- 业务日志（操作审计、错误日志、性能埋点）——这些有自己的规范，本 skill 不审

## 检测维度

对每个候选代码块检查 3 类日志是否存在：

| 类别 | 描述 | 找什么 |
|------|------|--------|
| **(a) Lifecycle** | 启停事件 | `started`/`stopped`/`opened`/`closed`/`connected`/`disconnected` 等 |
| **(b) First-data marker** | 首次数据信号 | `first frame`/`first message`/`first item`/`onReceive` 第一次记录 |
| **(c) Periodic counter** | 周期性活性统计 | 周期任务 + `count`/`rate`/`bytes/s` 之类 |

## 严重性分级

| 等级 | 条件 | 影响 |
|------|------|------|
| 🔴 **Critical** | 缺 (b) **且** 缺 (c) | debug 时完全看不出"是否真在流"，需要 tcpdump/dumpsys 才能判断 |
| 🟡 **Warning** | 有 (a) (b) 但缺 (c) | 知道流开始了，不知道还在不在流 |
| 🟢 **Minor** | 缺 (b) 但有 (c) | 周期统计能判断流速，但首次延迟看不出来 |
| ✅ **Healthy** | (a) (b) (c) 全有 | 符合 §5 标准 |

## 执行流程

### Step 1: 范围确认

- 默认扫描整个项目（CWD）
- 用户给了路径参数（如 `/log-audit app/src/main`）则限定范围
- 跳过 `node_modules` / `build` / `.gradle` / `vendor` / `target` / `dist` / 生成代码目录

### Step 2: 候选识别（双层启发式）

**第一层（粗筛 — 文件名/路径模式）**：用 Glob 找文件名包含以下关键词的文件：
- `Stream`、`Capturer`、`Encoder`、`Decoder`、`Publisher`、`Subscriber`
- `Worker`、`Consumer`、`Producer`、`Handler`、`Listener`
- `Channel`、`Pipe`、`Queue`、`Pipeline`
- `Receiver`、`Sender`、`Socket`、`Transport`

**第二层（精筛 — 代码内部模式）**：用 Grep 在所有源文件中找：
- `Flow<` / `Stream<` / `Observable<` / `Channel<`（Kotlin / Dart / Rx）
- `while *(true|active|running)` + 至少一个 IO/sleep 调用
- `addEventListener` / `.on(` + 持续事件名（`'data'`、`'message'`、`'frame'`）
- `setInterval` / `Timer.periodic` / `flow.collect` / `.subscribe(`

合并两层结果，去重。

### Step 3: 逐候选分析

对每个候选代码块（一个类、一个 fun、一个 init 块）：

1. **Read 关键代码行**（不需读全文件，定位到候选周围 ±30 行）
2. **检查 3 类日志**：对照 `Log.` / `logger.` / `console.` / `print` / `println!` 等常见 logger 调用
3. **判定严重性**
4. **生成修复建议**（具体到该代码块该补哪一类日志，给个示意 snippet）

### Step 4: 汇总输出

输出格式（直接可粘进 TODO.md 由 `/todo-doit` 消费）：

```markdown
## Log Audit 报告 - {date}

**扫描范围**: {项目路径或子模块}
**候选数**: {N}（识别为流式代码）
**整体覆盖**: 🔴 {n_critical} | 🟡 {n_warning} | 🟢 {n_minor} | ✅ {n_healthy}

---

### 🔴 Critical（{N} 项）：完全无运行时活性日志

- [ ] **{file}:{line}** `{class/fun name}` — {一行说明做什么的}
  - **缺**: first-data marker + 周期 counter
  - **影响**: debug 时只能看到 lifecycle，无法判断是否真在流动
  - **修复参考**:
    ```{lang}
    // 加在数据进入处:
    if (firstDataReceived.compareAndSet(false, true)) {
        logger.info("[{tag}] FIRST {data_kind} received: {summary}")
    }
    // 加周期任务（每 5-10s）:
    logger.info("[{tag}] stats: total={N} rate={M/s}")
    ```
  - **完整规范**: `~/.claude/guides/validation-hygiene.md` §5

### 🟡 Warning（{N} 项）：缺周期 counter
{同上格式}

### 🟢 Minor（{N} 项）：缺 first-data marker
{同上格式}

### ✅ Healthy（{N} 项）
- ✅ `{file}` — `{class/fun}` 已有完整 lifecycle + first-data + counter
```

### Step 5: 体量控制

- **默认输出**：每个等级 top-10 完整展示，超过部分写入 `_scratch/log-audit-{date}.md` 供后续查阅
- **超过 30 项时**：强制建议先按"模块"过滤再跑（`/log-audit src/X` 等）
- **0 项**：输出"项目已符合 §5 标准 ✅"

### Step 6: Action Menu

输出末尾给出可执行的 action menu：

```markdown
## 建议操作

1. 📋 **全量塞 TODO**（回复 1）→ 调用 `todo-write` 把所有🔴+🟡 写入 TODO.md，由 `/todo-doit` 逐个消费
2. 🎯 **只塞 Critical**（回复 2）→ 只写🔴到 TODO.md
3. 🔧 **现在就修最严重的**（回复 3）→ 直接对 top-3 🔴 改代码（你来挑）
4. 📊 **细看某项**（回复 4 + 编号）→ 给出该项的更详细修复方案（含完整 snippet 示例）
5. ⏸️ **仅诊断**（回复 5）→ 不动 TODO，仅本次输出留作参考
```

**默认行为**（用户不响应）：保持仅诊断态，不静默写入任何文件。

## 严格约束

1. **不修改任何业务代码** — 纯诊断 + 提议
2. **不生成报告文件**（除非超量自动溢写到 `_scratch/`）— 优先在对话内输出
3. **不 false positive 流式代码**：识别启发式宁可漏报不要错报。看到不确定的（如 RxJS 一次性 `.subscribe`），分类为"不属于本 skill 范围"而非强行算流式
4. **不审业务日志/错误日志/性能日志** — 这些有别的规范，scope 漂移会让 skill 没用
5. **一次扫描超过 60 秒**：立即停下，建议用户用模块过滤参数缩范围

## 与其他 skill 的关系

- **`feat-done`** 在交付前可调用本 skill（场景：本次交付涉及流式代码）
- **`code-quality`** 在 review PR 时可调用本 skill（场景：PR diff 命中流式代码模式）
- **`comprehensive-health-check`** 应将本 skill 作为子节点（"日志覆盖"维度）
- **`/todo-write`** 是本 skill 输出的下游消费者（action menu 选项 1/2 触发）
- **`/todo-doit`** 在用户选 1/2 后逐个执行修复任务

## 触发示例

| 用户说 | 行为 |
|--------|------|
| `/log-audit` | 扫整个 CWD |
| `/log-audit app/src/main/kotlin/.../livekit/` | 扫指定子目录 |
| `审一下日志` / `查日志覆盖` | 扫整个 CWD |
| `LiveKitClient 这个文件日志够吗？` | 当作单文件审，跳过 Step 1 范围确认 |

## 反仪式自检

执行完毕后自问：
> 我这次 audit 给出的 TODO，用户/AI 真会去做吗？还是只是"显得我审过了"？

如果连续 3 次 audit 后输出的 TODO 一项都没被消费（`/todo-doit` 跳过/Reject），说明：
- 严重性分级太宽（漏到 🔴 的不该是 🔴）
- 或修复建议没说服力（用户看完觉得改了不值）
- 或时机不对（用户没空管）

向 Founder 报告，重新校准触发条件或分级阈值。
