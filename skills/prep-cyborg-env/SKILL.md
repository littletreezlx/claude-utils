---
name: prep-cyborg-env
description: >
  AI Cyborg 探索/QA 前的环境准备 Skill。确保 Flutter App + Debug Server 处于干净、一致的状态。
  Use when starting ai-explore, ai-qa-stories, or any workflow that requires programmatic state verification.
version: 0.1.0
---

# Prep Cyborg Env — AI 探索/QA 前置环境准备

## 目的

在执行 `ai-explore`、`ai-qa-stories` 等需要 Debug State Server 的 Skill 之前，**确保 App 处于干净、一致的状态**，避免"幽灵状态"导致的错误结论。

## 核心问题背景

Flutter App 有独立的 Drift SQLite 副本。当通过 `seed-test-data.sh` 直接修改数据库时，运行中的 Flutter App 的 Riverpod 内存状态不会自动同步，导致：
- App UI 显示旧数据
- Debug Server 返回最新数据
- AI 三角验证矛盾

## 职责边界

**本 Skill 负责**：环境干净启动（Kill → Seed → Restart → Verify）

**本 Skill 不负责**：
- Debug Server 代码生成（那是 `init-debug-server` 的职责）
- 用户故事生成（那是 `generate-user-stories` 的职责）
- QA 验证执行（那是 `ai-qa-stories` 的职责）

## 触发条件

1. `ai-explore` 开始前（**必须**）
2. `ai-qa-stories` 开始前（**必须**）
3. 任何需要 Debug State Server 的 Skill 执行前
4. 用户说 "prep", "prepare env", "准备环境"

## 执行流程

### Step 0: 检测当前环境状态

在动手之前，先检查当前状态：

```bash
# 检查 Debug Server 是否可达
curl -s localhost:8788/providers >/dev/null 2>&1 && echo "Debug Server: RUNNING" || echo "Debug Server: DOWN"

# 检查 App 进程
pgrep -fl "flametree_pick\|Runner" | grep -v "Volumes\|PrivateFrameworks\|RuntimeRoot" | head -3

# 检查脏状态（App state vs DB data 是否一致）
curl -s localhost:8788/state/home
curl -s localhost:8788/data/groups
```

**如果状态干净**（App 和 DB 一致）→ 可以跳过，直接开始业务 Skill
**如果状态不一致** → 必须执行 Step 1-3

### Step 1: 强制重置（Kill 所有进程）

```bash
# 杀掉所有 flutter run 进程
pkill -f "flutter run" 2>/dev/null || true
pkill -f "flutter_tools" 2>/dev/null || true

# 删除 PID 文件
rm -f /tmp/flutter_dev.pid

# 等待端口释放
for i in 1 2 3; do
  if ! curl -s "http://localhost:8788/providers" >/dev/null 2>&1; then
    echo "✓ 端口已释放"
    break
  fi
  echo "⏳ 等待端口释放..."
done
```

### Step 2: 播种测试数据（原子操作）

```bash
cd /path/to/project

# 清理旧数据 + 播种新数据
./scripts/seed-test-data.sh clean
./scripts/seed-test-data.sh
```

**注意**：`seed-test-data.sh` 通过 Debug Server API 写入数据，所以 Debug Server 必须在运行。如果 Step 1 已经杀掉进程，Debug Server 也死了。

**正确顺序**：
1. 如果 App 正在运行且状态干净 → `seed-test-data.sh clean` 直接清理
2. 如果 App 状态不一致 → Step 1 杀掉 → Step 2 启动后 seed

### Step 3: 确定性启动（--force-reset）

```bash
./scripts/start-dev.sh --force-reset --background
```

`--force-reset` 保证：
- 先杀掉现有进程
- 再启动全新 App
- PID 文件追踪 Flutter 进程
- 轮询等待 Debug Server ready

### Step 4: 状态健康验证

启动后必须验证三角一致性：

```bash
# 1. Debug Server 可达
curl -s localhost:8788/providers | python3 -c "import sys,json; print('Providers OK' if json.load(sys.stdin)['ok'] else 'FAIL')"

# 2. State 和 Data 一致
STATE=$(curl -s localhost:8788/state/home)
DATA=$(curl -s localhost:8788/data/groups)
echo "State: $STATE"
echo "Data: $DATA"

# 3. 数据非空（seed 成功）
curl -s localhost:8788/data/groups | python3 -c "import sys,json; groups=json.load(sys.stdin)['data']['groups']; print(f'Groups: {len(groups)}')"
```

**通过标准**：三个检查全部 OK → 环境干净，可以开始业务 Skill
**失败**：任一检查失败 → 重复 Step 1-4 或报告用户

## 快速命令

在支持的项目中，可以直接运行：

```bash
# 一键准备干净环境（如果项目有 prep-env.sh）
./scripts/prep-env.sh

# 或手动组合
./scripts/seed-test-data.sh clean && ./scripts/seed-test-data.sh && ./scripts/start-dev.sh --force-reset --background
```

## 输出格式

```
=== Prep Cyborg Env ===
[1/4] 检测当前状态...
       Debug Server: RUNNING
       App 进程: 2 found
       状态: CLEAN（可跳过）
       
✅ 环境已就绪（跳过重置）

--- 或 ---

[1/4] 检测当前状态...
       Debug Server: RUNNING  
       App 进程: 3 found
       状态: DIRTY（需要重置）

[2/4] 杀掉进程... ✓
[3/4] 播种数据... ✓
[4/4] 启动 App... ✓ (PID: 12345)
[5/4] 健康验证... ✓ State=Data ✅

✅ 环境就绪，可以开始探索
```

## 项目级实现

如果项目需要自定义的 prep-env 脚本，在项目 `scripts/` 目录下创建 `prep-env.sh`：

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."

echo "=== 准备 Cyborg 环境 ==="

# 清理
./scripts/seed-test-data.sh clean 2>/dev/null || true

# 播种
./scripts/seed-test-data.sh

# 强制重置启动
./scripts/start-dev.sh --force-reset --background

# 等待并验证
for i in 1 2 3 4 5; do
  if curl -s localhost:8788/providers >/dev/null 2>&1; then
    echo "✅ Debug Server 就绪"
    exit 0
  fi
done
echo "❌ Debug Server 启动失败"
exit 1
```

## 健康检查契约（AI Skill 必须遵守）

业务 Skill（`ai-explore`、`ai-qa-stories` 等）在执行前**必须**：

1. 调用 `prep-cyborg-env` 或等效的 `prep-env.sh`
2. 验证 `curl localhost:8788/state/home` 的 `activeGroupId` 与 `curl localhost:8788/data/groups` 的第一个分组的 `id` 一致
3. 如果验证失败，**停止执行**并报告状态不一致

严禁在状态不一致时继续执行——这会导致错误的探索结论。
