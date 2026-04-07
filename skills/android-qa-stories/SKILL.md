---
name: android-qa-stories
description: >
  This skill should be used when AI should autonomously verify user stories
  against a running native Android app via embedded Debug Server. A true
  AI-autonomous loop: reads QA verification files from docs/user-stories/qa/,
  executes curl sequences, validates assertions, reports failures. Use when
  the user says "验证故事", "跑用户故事", "regression", "run stories", "qa stories",
  or after a batch of code changes needs holistic verification beyond unit tests.
  Requires Debug Server embedded in the app and docs/user-stories/qa/ to exist.
version: 1.0.0
---

# Android QA Stories — 用户故事自主验证

AI 自主闭环：读取 `docs/user-stories/qa/*.qa.md` 中的验证脚本，通过嵌入式 Debug Server 逐步 curl 验证，确保 Happy Path 全部通过。**纯验证，不修代码。**

## 双文件架构

| 文件 | 角色 | 本 skill 怎么用 |
|------|------|----------------|
| `docs/user-stories/qa/*.qa.md` | 验证脚本（编译产物） | **日常消费** — 直接读取并执行 |
| `docs/user-stories/*.md` | 产品故事（源码） | **仅在失败排障时参考** |

## 核心原则

- **只验证，不修复** — 发现问题记录到报告，不改代码、不补端点、不重启 App
- **QA 过程中不重启** — 启动一次，跑完所有故事
- **故事按编号顺序** — 前序故事可能创建后序需要的数据
- **只读 qa/ 目录** — 不解析 Story 文件中的内容来执行验证

---

## 执行流程

### Step 0: 确认环境

**1. 设备连接**：
```bash
adb devices  # 确认有且仅有一个设备/模拟器在线
```

**2. 获取包名**（从源码读取，按优先级）：
1. `grep 'applicationId' app/build.gradle*` → 取值
2. `grep 'package=' app/src/main/AndroidManifest.xml` → 取值

**3. 端口转发 + 验证**：
```bash
# 端口从 CLAUDE.md 或源码中读取（通常在 DebugServer.kt/java 中硬编码）
adb forward tcp:$PORT tcp:$PORT
curl -s --connect-timeout 3 localhost:$PORT/providers
```

- ✅ 有响应 → 检查 actions 是否匹配当前项目，跳到 Step 1
- ❌ 无响应 → 自动启动（见下方"进程管理"）

### Step 1: 加载 QA 文件

**并行** Read 所有 `docs/user-stories/qa/*.qa.md`，按文件名编号排序。

**如果 qa/ 目录不存在**：提示用户先运行 `/generate-stories` 迁移到双文件架构。

同时读取 `/providers` 响应，与 QA 文件末尾的端点依赖表做对账：

```
端点对账: 12/12 匹配 ✅
```

或：

```
端点对账: 10/12 匹配
  ⚠️ /action/xxx — 故事引用但 Server 无此端点
```

### Step 2: 快照初始状态

并行查询关键状态端点，记录为初始快照：

```bash
curl -s localhost:$PORT/state/auth
curl -s localhost:$PORT/data/items    # 项目核心数据
```

### Step 3: 逐条执行验证

对每个 QA 文件的每个 Scenario：

1. 读 Intent → 执行 curl → 校验 Assert
2. 判定结果（三种）：

| 结果 | 处理 |
|------|------|
| ✅ 通过 | 继续 |
| 🐛 失败 | 记录（curl 命令 + 实际返回 + 期望值），继续执行后续步骤 |
| ⏭️ 跳过 | 端点缺失 / 外部依赖 / 需要人工操作，记录原因，继续 |

**效率要求**：同一故事内独立的状态查询可以并行 curl。

### Step 4: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: xxx | 包名: com.xxx | 端口: xxxx | 时间: xxx
- 设备: [adb devices 输出]

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

### 端点对账不匹配项
- /action/feeds/createCategory → 端点不存在
```

---

## 进程管理

### 自动启动（仅 App 未运行时）

```bash
# 1. 杀残留
adb shell am force-stop $PACKAGE

# 2. 启动 App（后台执行，run_in_background: true）
adb shell am start -n $PACKAGE/.MainActivity

# 3. 端口转发
adb forward tcp:$PORT tcp:$PORT

# 4. 同时并行加载故事（Step 1），不傻等
# 5. 等后台启动通知后 curl providers 确认就绪
```

### 截图（调试用）

```bash
adb exec-out screencap -p > /tmp/android_screen.png
# 然后用 Read 工具查看
```

### 禁止行为

- ❌ 写 for 循环轮询 curl
- ❌ QA 过程中重启 App
- ❌ QA 过程中修改任何代码
- ❌ 在 shell 命令中使用 `sleep`

---

## 注意事项

1. **多设备时指定设备** — `adb -s <serial> shell ...`，避免 "more than one device" 错误
2. **模拟器端口** — 模拟器默认 5554 起，`adb forward` 后用 localhost 访问 Debug Server
3. **Logcat 辅助诊断** — `adb logcat -d -t 20 *:W` 查看最近 20 条警告级别以上日志
4. **故事按编号顺序** — 前序故事可能创建后序需要的数据
