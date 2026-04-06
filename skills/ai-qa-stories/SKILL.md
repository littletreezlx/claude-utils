---
name: ai-qa-stories
description: >
  This skill should be used when AI should autonomously verify user stories
  against a running Flutter/Android app via Debug State Server. A true AI-autonomous
  loop: reads stories, executes curl sequences, validates assertions, reports
  failures. Use when the user says "验证故事", "跑用户故事",
  "regression", "run stories", "qa stories", or after a batch of code changes
  needs holistic verification beyond unit tests. Requires Debug State Server
  running and docs/user-stories/ to exist.
version: 1.0.0
---

# AI QA Stories — 用户故事自主验证

AI 自主闭环：读取 `docs/user-stories/` 中的用户故事，通过 Debug State Server 逐步 curl 验证，确保 Happy Path 全部通过。**纯验证，不修代码。**

## 核心原则

- **只验证，不修复** — 发现问题记录到报告，不改代码、不补端点、不重启 App
- **QA 过程中不重启** — 启动一次，跑完所有故事
- **故事按编号顺序** — 前序故事可能创建后序需要的数据

---

## 执行流程

### Step 0: 环境准备（必须先执行）

**⚠️ 开始 QA 前，必须先运行 `prep-cyborg-env` Skill 或 `./scripts/prep-env.sh`**，确保环境干净。

这防止"幽灵状态"导致的错误验证结论——Flutter 内存状态与 DB 不一致时，QA 会给出完全错误的通过/失败判断。

详见 `prep-cyborg-env` Skill 文档。

### Step 1: 确认 Server 运行

**端口发现**（按优先级，找到即停）：
1. `grep 'DEBUG_PORT' scripts/start-dev.sh` → 取变量值
2. `grep 'localhost:\d{4,5}' CLAUDE.md` → 从项目 CLAUDE.md 提取
3. `grep '_port.*=.*\d{4,5}' lib/**/debug*.dart` → 从源码读取

```bash
curl -s --connect-timeout 3 localhost:$PORT/providers
```

- ✅ 有响应 → 检查 actions 是否匹配当前项目（避免误连），跳到 Step 2
- ❌ 无响应 → 报告用户：需要先运行 prep-cyborg-env

### Step 2: 加载故事

**并行** Read 所有 `docs/user-stories/*.md`（排除 README/模板），按文件名编号排序。

同时读取 `/providers` 响应，与故事中引用的端点做对账：

```
端点对账: 12/12 匹配 ✅
```

或：

```
端点对账: 10/12 匹配
  ⚠️ /action/xxx — 故事引用但 Server 无此端点
  ⚠️ /data/settings/sync — 路径格式不匹配，实际为 /data/settings-sync
```

### Step 3: 快照初始状态

并行查询关键状态端点，记录为初始快照：

```bash
curl -s localhost:$PORT/state/auth
curl -s localhost:$PORT/data/feeds    # 或项目对应的核心数据
```

### Step 4: 逐条执行故事

对每条故事的每个 Step：

1. 读意图 → 执行 curl → 验证断言
2. 判定结果（三种）：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 继续 |
| 🐛 失败 | 记录（curl 命令 + 实际返回 + 期望值），继续执行后续步骤 |
| ⏭️ 跳过 | 端点缺失 / 外部依赖 / 需要人工操作，记录原因，继续 |

**效率要求**：同一故事内独立的状态查询可以并行 curl。

### Step 5: 输出报告

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
#### 02-daily-use Step 3: [描述]
- curl: `curl -s -X POST localhost:$PORT/action/xxx -d '...'`
- 期望: `success == true`
- 实际: `{"error":"..."}`

### 跳过项
- 03-xxx Step 5: 端点 /action/yyy 不存在
- 04-xxx Step 2: 需要外部 API key

### 端点对账不匹配项
- /data/settings/sync → 实际为 /data/settings-sync
- /action/feeds/createCategory → 端点不存在
```

---

## 进程管理

### 自动启动（仅 Server 未运行时）

1. **杀残留**：
   ```bash
   pkill -9 -f "<app_binary>" 2>/dev/null
   pkill -f "flutter run" 2>/dev/null
   ```
2. **后台启动**（`run_in_background: true`）：

   | 用户输入 | 启动命令 |
   |---------|---------|
   | 无参数 | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `macos` | `./scripts/start-dev.sh --background --device macos` |
   | 指定设备 | `./scripts/start-dev.sh --background --device <设备>` |

3. **同时并行加载故事**（Step 1），不傻等
4. 等后台启动完成通知后 `curl providers` 确认就绪

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
5. **故事按编号顺序** — 前序故事可能创建后序需要的数据
