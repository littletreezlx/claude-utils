---
name: godot-qa-stories
description: >
  This skill should be used when AI should autonomously verify user stories
  against a running Godot game via DebugPlayServer. A true AI-autonomous
  loop: reads QA verification files from docs/user-stories/qa/, executes curl
  sequences, validates assertions, reports failures. Use when the user says
  "验证故事", "跑用户故事", "regression", "run stories", "qa stories", or after
  a batch of code changes needs holistic verification beyond unit tests.
  Requires DebugPlayServer running (port 9999) and docs/user-stories/qa/ to exist.
version: 0.2.0
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

### Step 0: 确认 Server 运行

```bash
curl -s --connect-timeout 3 localhost:9999/ping
```

- ✅ 有响应 → 跳到 Step 1
- ❌ 无响应 → 自动启动（见下方"进程管理"）

### Step 1: 加载 QA 文件

**并行** Read 所有 `docs/user-stories/qa/*.qa.md`，按文件名编号排序。

**如果 qa/ 目录不存在**：提示用户先运行 `/generate-stories` 迁移到双文件架构。

同时读 `Core/Autoloads/DebugPlayServer.gd` 的 `_route` 函数，获取实际可用端点列表（不硬编码）。

对比 QA 文件末尾的端点依赖表与实际端点，输出简要对账：

```
端点对账: 12/12 匹配 ✅
```

或：

```
端点对账: 10/12 匹配
  ⚠️ /play/xxx — 故事引用但 Server 无此端点
```

### Step 2: 快照初始状态

并行查询，记录为初始快照：

```bash
curl -s localhost:9999/state/game   # gold, population
curl -s localhost:9999/state/save   # save data
```

### Step 3: 逐条执行验证

对每个 QA 文件的每个 Scenario：

1. 读 Intent → 执行 curl → 校验 Assert
2. 判定结果（三种）：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 继续 |
| 🐛 失败 | 记录（curl 命令 + 实际返回 + 期望值），继续执行后续步骤 |
| ⏭️ 跳过 | 端点缺失或需要人工操作，记录原因，继续 |

**效率要求**：同一故事内独立的状态查询可以并行 curl。

### Step 4: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: Barracks Clash | 端口: 9999 | 时间: xxx

### 结果总览
| 故事 | 状态 | 通过/总数 |
|------|------|----------|
| 01-main-flow | ✅ | 8/8 |
| 02-xxx | 🐛 | 5/7 |

### 失败详情
#### 02-xxx Step 3: [描述]
- curl: `curl -s -X POST localhost:9999/play/xxx -d '...'`
- 期望: `success == true`
- 实际: `{"error":"..."}`

### 跳过项
- 02-xxx Step 5: 端点 /play/yyy 不存在
```

---

## 进程管理

### 自动启动（仅 Server 未运行时）

1. **杀残留**：`pkill -9 -f "Godot" 2>/dev/null`
2. **后台启动**（`run_in_background: true`）：
   ```bash
   /Applications/Godot.app/Contents/MacOS/Godot --path /Users/zhanglingxiao/LittleTree_Projects/game-mvp &
   ```
3. **同时并行加载故事**（Step 1），不傻等
4. 等后台启动完成通知后 `curl ping` 确认就绪

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
