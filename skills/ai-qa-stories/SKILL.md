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
version: 0.1.0
---

# AI QA Stories — 用户故事自主验证

## 目的

AI 自主闭环：读取 `docs/user-stories/` 中的用户故事，通过 Debug State Server 逐步执行 curl 验证，确保核心 Happy Path 全部通过。这是真正的 AI 自主测试——不需要人类介入。

## 前置条件

1. 项目有 `docs/user-stories/` 目录且至少有 1 条故事
2. Debug State Server 正在运行（如未运行：`open -a Simulator && ./scripts/start-dev.sh --background`）
3. 端口从项目 CLAUDE.md 读取（不硬编码）

## 执行流程

### Step 1: 加载故事

读取 `docs/user-stories/` 下所有 `.md` 文件，按文件名编号顺序排列。
读项目 CLAUDE.md 获取 Debug Server 端口。

### Step 2: 准备环境

- 检查 Debug Server 是否响应：`curl -s localhost:$PORT/providers`
- 如果故事 01 的前置条件是"空状态"，执行 `./scripts/seed-test-data.sh clean`（如存在）
- 如果需要测试数据，执行 `./scripts/seed-test-data.sh`

### Step 3: 逐条执行

对每条故事的每个 Step：

1. **读意图** — 理解这步要做什么
2. **执行 curl** — 按文档中的命令执行（替换 `$PORT` 为实际端口）
3. **验证断言** — 对比返回值与文档中的期望
4. **判定结果**：
   - 断言通过 → 继续下一步
   - 断言失败 → 分析原因：
     - **代码 bug**：读相关代码，修复 → 重启 App → 从当前故事重新执行
     - **故事过时**（端点 404、字段名变了）：标记为"故事需更新" → 跳过继续

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

## 与 ai-explore 的关系

`ai-qa-stories` 是 `ai-explore` 的前置条件。只有所有故事通过后，才有意义进入启发式探索。`ai-explore` 会自动先调用本 skill。

## Gotchas / 踩坑点

1. **不硬编码端口** — 从 CLAUDE.md 读取
2. **故事按编号顺序执行** — 前序故事可能创建后序需要的数据
3. **autoDispose 的 State 可能为空** — 断言用 `/data/` 而非 `/state/`
4. **修复代码后必须重启 App** — `pkill -f "flutter run"; ./scripts/start-dev.sh --background`
5. **区分"代码 bug"和"故事过时"** — 404 = 故事过时；数据不对 = 可能是 bug
6. **用 /logs 辅助诊断** — `curl localhost:$PORT/logs?count=20` 看操作历史
