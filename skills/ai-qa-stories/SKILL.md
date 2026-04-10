---
name: ai-qa-stories
description: >
  This skill should be used when AI should autonomously verify user stories
  against a running Flutter/Android app via Debug State Server. A true AI-autonomous
  loop: reads QA verification files from docs/user-stories/qa/, executes curl
  sequences, validates assertions, reports failures. Use when the user says
  "验证故事", "跑用户故事", "regression", "run stories", "qa stories", or after
  a batch of code changes needs holistic verification beyond unit tests. Requires
  Debug State Server running and docs/user-stories/qa/ to exist.
version: 2.2.0
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
- **QA 过程中不重启** — 启动一次，跑完所有故事
- **故事按编号顺序** — 前序故事可能创建后序需要的数据
- **只读 qa/ 目录** — 不解析 Story 文件中的内容来执行验证

---

## 执行流程

### Step 0: 环境准备（必须先执行）

**⚠️ 开始 QA 前，必须先运行 `prep-cyborg-env` Skill 或 `./scripts/prep-env.sh`**，确保环境干净。

这防止"幽灵状态"导致的错误验证结论——Flutter 内存状态与 DB 不一致时，QA 会给出完全错误的通过/失败判断。

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

### Step 3: 端点对账（实际调用验证）

端点对账必须**实际调用**验证，不能只看 `/providers` 列表。

1. **获取实际端点列表**：
   ```bash
   curl -s localhost:$PORT/providers
   ```

2. **验证每个端点**（对每个引用的端点发请求，检查返回不是 error）：
   ```bash
   # 检查 /state/xxx 是否存在且返回非 error
   curl -s localhost:$PORT/state/xxx | grep -q '"ok":true' && echo "OK" || echo "MISSING"

   # 检查 /data/xxx 是否存在且返回非 error
   curl -s localhost:$PORT/data/xxx | grep -q '"ok":true' && echo "OK" || echo "MISSING"
   ```

3. **输出对账结果**：

   全部存在：
   ```
   端点对账: 12/12 匹配 ✅
   ```

   有缺失端点（标记为跳过而非失败）：
   ```
   端点对账: 10/12 匹配
     ⏭️ /state/articles — 端点不存在，跳过相关 Scenario
     ⏭️ /action/feeds/createCategory — 端点不存在，跳过相关 Scenario
   ```

### Step 4: 快照初始状态

并行查询关键状态端点，记录为初始快照：

```bash
curl -s localhost:$PORT/state/auth
curl -s localhost:$PORT/data/feeds    # 或项目对应的核心数据
```

### Step 5: 逐条执行验证

对每个 QA 文件的每个 Scenario：

1. **读 Intent** — 理解这步在验证什么
2. **检查端点是否存在** — 如果引用的端点在对账时被标记为缺失，直接跳过
3. **执行 curl** — 按文件中的 bash 代码块顺序执行
4. **校验 Assert** — 比对实际返回与断言
5. 判定结果（三种）：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 继续 |
| 🐛 失败 | 记录（curl 命令 + 实际返回 + 期望值 + Intent），继续 |
| ⏭️ 跳过 | 端点缺失 / 外部依赖 / 缺少数据，记录原因，继续 |

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
- **初步判断**: {基于 Intent 的快速判断：代码 bug / 测试过期 / 环境问题}

### 跳过项
- 03-xxx Scenario 5: 端点 /action/yyy 不存在，跳过
- 04-xxx Scenario 2: 需要外部 API key，跳过

### 端点对账不匹配项
- /data/settings/sync → 实际为 /data/settings-sync
- /state/articles → 端点不存在
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
   | 指定设备 | `./scripts/start-dev.sh --background --device <设备>` |

3. **同时并行加载 QA 文件**（Step 2），不傻等
4. 等后台启动完成通知后 `curl providers` 确认就绪

### 禁止行为

- ❌ 写 for 循环轮询 curl
- ❌ 反复 `ps aux | grep flutter`
- ❌ QA 过程中重启 App
- ❌ QA 过程中修改任何代码
- ❌ 在 shell 命令中使用 `sleep`
- ❌ 重复调用 start-dev.sh（每次调用都会启动新窗口！）

---

## 重要修复说明

### v2.2.0 修复

1. **删除硬编码端口表**：常见端口表已移除，不再依赖静态配置。端口统一从 `debug_server.dart` 源码读取，确保与实际运行状态一致。

2. **端口冲突主动检测**：Step 1 中增加了 `lsof` 检测逻辑，能在启动前发现端口被其他项目占用的情况，并给出明确警告。

3. **清空所有 Flutter 进程**：进程管理从只杀 `<app_binary>` 改为杀 `pkill -9 -f "flutter"` + `pkill -9 -f "fvm"`，确保 Simulator 上只有一个目标 App 在跑。

4. **端点验证方式改为实际调用**：不能只看 `/providers` 列表，因为端点可能在列表中但实际调用返回 error（如 `/state/articles` 列在 states 中但返回 `Unknown state`）。

5. **不存在的端点标记为跳过而非失败**：端点缺失是环境/配置问题，不算测试失败。

## 注意事项

1. **start-dev.sh 超时 ≠ 失败** — 脚本等待循环可能瞬间完成就报"超时"，flutter run 仍在后台编译。等 `run_in_background` 通知后 `tail` 日志看 DevTools URL
2. **端口冲突** — 同机器多项目可能各自有 Debug Server，检查 /providers 的 actions 是否匹配当前项目
3. **zsh URL 转义** — `curl "url?param=value"` 必须双引号包裹
4. **autoDispose State 可能为空** — 断言优先用 `/data/`（直读 Repository）而非 `/state/`（读 ViewModel 内存状态）
5. **QA 按编号顺序** — 前序 QA 可能创建后序需要的数据
6. **旧格式兼容** — 如果只有 `docs/user-stories/*.md` 而没有 `qa/` 目录，提示用户迁移
