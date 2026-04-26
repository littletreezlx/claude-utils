---
name: godot-qa-stories
description: >
  Use when the user says "验证故事", "跑用户故事", "regression", "run stories",
  "qa stories", or after a batch of Godot code changes needs holistic verification
  beyond unit tests. Verifies user stories against a running Godot game via
  DebugPlayServer. Requires DebugPlayServer embedded and docs/user-stories/qa/ to exist.
version: 0.4.0
---

# Godot QA Stories — 用户故事自主验证

AI 自主闭环：读取 `docs/user-stories/qa/*.qa.md` 中的验证脚本，通过 DebugPlayServer 逐步 curl 验证，确保 Happy Path 全部通过。**纯验证，不修代码。**

## 双文件架构

| 文件 | 角色 | 本 skill 怎么用 |
|------|------|----------------|
| `docs/user-stories/qa/*.qa.md` | 验证脚本（编译产物） | **日常消费** — 直接读取并执行 |
| `docs/user-stories/*.md` | 产品故事（源码） | **仅在失败排障时参考** |

## 核心原则

- **只验证，不修复** — 发现问题记录到报告，不改代码、不补端点、不重启游戏
- **QA 过程中不重启** — 启动一次，跑完所有故事
- **故事按编号顺序** — 前序故事可能创建后序需要的数据
- **只读 qa/ 目录** — 不解析 Story 文件中的内容来执行验证

---

## 执行流程

### Step 0: 发现端口 + 确认 Server

**端口从源码动态读取**（禁止硬编码）：

```bash
# 从 DebugPlayServer.gd 读取 PORT 常量
PORT=$(grep -E '^const PORT' Core/Autoloads/DebugPlayServer.gd | grep -oE '[0-9]+' | head -1)
echo "Godot debug port: $PORT"
```

**检查 Server**：

```bash
curl -s --connect-timeout 3 localhost:$PORT/ping
```

- ✅ 有响应 → 跳到 Step 1
- ❌ 无响应 → 自动启动（见下方"进程管理"）

### Step 1: 加载 QA 文件

**并行** Read 所有 `docs/user-stories/qa/*.qa.md`，按文件名编号排序。

**如果 qa/ 目录不存在**：提示用户先运行 `/generate-stories` 迁移到双文件架构。

### Step 1.5: 端点对账（实际调用验证）

不能只看 `/providers` 列表——端点可能在列表中但实际调用返回 error。**对每个 QA 引用的端点发真实请求**：

```bash
# 1. 获取声明的端点列表
curl -s localhost:$PORT/providers

# 2. 对每个 QA 引用的端点发空调用，检查返回是否非 error
curl -s localhost:$PORT/state/game | grep -q '"ok":true' && echo "OK" || echo "MISSING"
curl -s -X POST localhost:$PORT/play/goto_camp | grep -q '"ok":true' && echo "OK" || echo "MISSING"
```

输出对账结果：

```
端点对账: 12/12 匹配 ✅
```

或（端点缺失标跳过而非失败）：

```
端点对账: 10/12 匹配
  ⏭️ /play/xxx — 端点不存在，跳过相关 Scenario
```

### Step 2: 快照初始状态

并行查询，记录为初始快照：

```bash
curl -s localhost:$PORT/state/game   # gold, population
curl -s localhost:$PORT/state/save   # save data
```

### Step 3: 逐条执行验证

对每个 QA 文件的每个 Scenario：

1. **读 Intent** — 理解这步在验证什么
2. **检查端点是否存在** — 如果 Step 1.5 标记为缺失，直接跳过
3. **执行 curl** — 按 QA 中的 bash 顺序
4. **校验 Assert** — 比对实际返回与断言
5. 判定结果：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 继续 |
| 🐛 失败 | 记录（curl + 实际返回 + 期望值 + Intent），继续 |
| ⏭️ 跳过 | 端点缺失 / 外部依赖 / 需人工操作，记录原因，继续 |

**效率要求**：同一故事内独立的状态查询可以并行 curl。

### Step 4: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx

### 结果总览
| 故事 | 状态 | 通过/总数 |
|------|------|----------|
| 01-main-flow | ✅ | 8/8 |
| 02-xxx | 🐛 | 5/7 |

### 失败详情
#### 02-xxx Scenario 3: {Intent 描述}
- **Intent**: {验证意图}
- **curl**: `curl -s -X POST localhost:$PORT/play/xxx -d '...'`
- **期望**: `success == true`
- **实际**: `{"error":"..."}`
- **初步判断**: {代码 bug / 测试过期 / 环境问题}

### 跳过项
- 02-xxx Scenario 5: 端点 /play/yyy 不存在

### 端点对账不匹配项
- /play/zzz → 端点不存在
```

---

## 进程管理

### 自动启动（仅 Server 未运行时）

1. **杀残留**：`pkill -9 -f "Godot" 2>/dev/null`
2. **检测 Godot 可执行路径**（按优先级）：
   ```bash
   GODOT_BIN=""
   for candidate in \
     "/Applications/Godot.app/Contents/MacOS/Godot" \
     "/Applications/Godot_mono.app/Contents/MacOS/Godot" \
     "$(which godot 2>/dev/null)"; do
     [ -x "$candidate" ] && GODOT_BIN="$candidate" && break
   done
   echo "Godot binary: $GODOT_BIN"
   ```
3. **平台检测 + 启动游戏**（WSL/Linux 必须用 Xvfb，否则无 X11/Wayland 启不了）：

   ```bash
   # DebugPlayServer.gd:17 规定 headless 模式不启动 server,所以必须有 (虚拟) GUI
   if grep -qi microsoft /proc/version 2>/dev/null || \
      ([ "$(uname -s)" = "Linux" ] && [ -z "$DISPLAY" ]); then
     # WSL2 / Linux 无显示器 → Xvfb 路径(2026-04-26 实测可行,见 game-mvp/TODO.md)
     command -v Xvfb >/dev/null || { echo "需先 apt install xvfb"; exit 1; }
     pgrep -x Xvfb >/dev/null || Xvfb :99 -screen 0 1152x648x24 &
     export DISPLAY=:99
   fi
   # macOS / 桌面 Linux 走原生显示
   "$GODOT_BIN" --path "$PWD" &
   ```

   使用 `run_in_background: true` 启动 Godot。Xvfb 也在后台跑（pgrep 防重复启）。
4. **同时并行加载故事**（Step 1），不傻等
5. 等后台启动完成通知后 `curl localhost:$PORT/ping` 确认就绪

### 禁止行为

- ❌ 写 for 循环轮询 curl
- ❌ 反复 `ps aux | grep Godot`
- ❌ QA 过程中重启游戏
- ❌ QA 过程中修改任何代码

---

## Godot 注意事项

1. **启动较慢** — 等 `run_in_background` 完成通知后再 ping
2. **curl JSON 参数** — 单引号包裹：`-d '{"level":1}'`
3. **响应含截图** — `_screenshot` 字段可用 Read 工具查看
4. **战斗状态** — `/state/battle` 仅在 DEPLOY/COMBAT 时有意义
5. **单任务锁** — Server 同一时刻只处理一个请求，429 = 忙，稍后重试
6. **必须在项目根目录执行** — `$PWD` 必须包含 `project.godot` 文件
