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
version: 0.4.0
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

> **⚠️ 端口冲突**：同一台机器可能有多个项目的 Debug Server 运行在不同端口。收到响应后，检查返回的 actions 列表是否与当前项目匹配（如 RSS 项目应有 articles/feeds 相关 action，不是 groups/options），避免误连其他项目。

#### 自动启动流程（Server 未运行时）

**核心原则：启动和加载故事并行，不傻等。**

```
┌─ 后台启动 App（run_in_background）──────────────┐   ┌─ 前台加载故事 ─────────┐
│ 无参数 → open Simulator + start-dev --background │   │ 并行读取所有 story 文件  │
│ 有参数 → start-dev --background --device <设备>   │   │ 记录 story 列表          │
└─────────────────────────────────────────────────┘   └────────────────────────┘
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
   | `/ai-qa-stories macos` | `./scripts/start-dev.sh --background --device macos` |
   | `/ai-qa-stories ios` | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `/ai-qa-stories <其他设备>` | `./scripts/start-dev.sh --background --device <设备>` |

   > **注意**：传了非模拟器设备参数时，**不要** `open -a Simulator`。所有路径统一走 `start-dev.sh`，享受日志管理和 server ready 等待。
   >
   > **⚠️ iOS 首次编译**：Xcode build 可能需要 45s+，加上 App 启动时间可能超过 `start-dev.sh` 的 60s 超时。超时不代表失败——检查 `/tmp/flutter_run.log` 尾部，如果看到 "Xcode build done" 或 "Syncing files" 说明构建已完成，App 即将就绪。

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

### Step 1: 加载故事 + providers 对账

**一次性并行读取**所有 `docs/user-stories/*.md` 文件（排除 README.md）。
按文件名编号排序。使用多个并行 Read 调用，不要逐个串行读取。

Server 就绪后，读取 `/providers` 响应，记录可用的 states/data/actions 列表。

#### Step 1.5: 故事 curl 预校验（关键！省大量时间）

**在执行任何 curl 之前**，扫描所有故事中的验证 curl 命令，与 `/providers` 返回的实际端点做对账：

1. **路径格式**：故事中 `/data/settings/sync` → 实际可能是 `/data/settings-sync`（连字符 vs 斜杠）
2. **参数名**：故事中 `categoryId` → 实际可能是 `destCategoryId`
3. **路径式 vs 查询式**：故事中 `/data/articles/{id}` → 实际可能需要 `/data/articles?filter=byId&id=xxx`
4. **端点存在性**：故事引用了 `createCategory` action → providers 中没有

**输出对账清单**（在开始验证前先展示给自己看）：

```
对账结果:
✅ /data/feeds — 存在
✅ /action/articles/toggleRead — 存在
⚠️ /data/settings/sync — 路径格式不匹配，实际为 /data/settings-sync
⚠️ /action/feeds/moveFeed — 参数名: 故事用 categoryId，实际期望 destCategoryId
❌ /data/articles/{id} — 不支持路径式查询
❌ /action/feeds/createCategory — 端点不存在
```

**处理**：
- ⚠️ 路径/参数不匹配 → 用实际格式执行验证，测试完后批量修复故事文档
- ❌ 端点不存在 → 记入待补清单（Step 3.5）或标记为功能缺失

> **获取参数名的方法**：如果不确定端点期望什么参数，先用空 body POST，看返回的 error message（通常会提示 "xxx is required"），或直接读 `lib/dev_tools/debug_action_registry.dart` 中对应 handler 的参数解析。

### Step 2: 环境快照 + 准备

#### 2a: 拍摄初始状态快照（重要！）

并行查询关键状态，记录为「初始快照」，验证完成后用于恢复：

```bash
# 并行执行
curl -s localhost:$PORT/state/auth     # → 记录: authenticated / localMode
curl -s localhost:$PORT/data/feeds     # → 记录: feeds count
curl -s localhost:$PORT/data/articles  # → 记录: articles count
curl -s localhost:$PORT/state/sync     # → 记录: sync status
```

> 快照的目的：如果验证过程中执行了破坏性操作（logout、mode 切换、delete），验证结束后可以恢复。

#### 2b: 环境准备

- 如果故事 01 的前置条件是"空状态"，执行 `./scripts/seed-test-data.sh clean`（如存在）
- 如果需要测试数据，执行 `./scripts/seed-test-data.sh`

### Step 3: 第一轮执行（收集问题）

对每条故事的每个 Step：

1. **读意图** — 理解这步要做什么
2. **检查端点** — 先对照 Step 1 记录的 providers 列表，判断所需端点是否存在
3. **执行 curl** — 端点存在则执行（替换 `$PORT` 为实际端口）
4. **验证断言** — 对比返回值与文档中的期望
5. **判定结果**（五种情况，各有处理方式）：

| 类型 | 特征 | 处理 |
|------|------|------|
| ✅ 通过 | 断言匹配 | 继续下一步 |
| 🐛 代码 bug | 端点存在，返回数据不对 | 读代码修复 → 安全重启 → 重跑当前故事 |
| 📝 参数/路径不匹配 | 端点存在但参数名或路径格式与故事文档不一致 | 用实际格式执行验证，记入「故事文档修复清单」 |
| 🔌 端点缺失 | providers 中没有 | 记入「待补端点清单」，标记 pending |
| 🌐 外部依赖 | 需要 API key / 硬件 / 人工 | 跳过，标记原因 |

> **区分外部服务的暂时性 vs 永久性问题**：
> - **超时 / 网络错误** → 暂时性，可稍后重试一次
> - **404 NOT_FOUND / 明确的 "not supported"** → 永久性（如 Miniflux 不支持 rename-tag），记录到 API 文档

#### 破坏性操作保护

以下操作会改变用户真实数据状态，必须**先确认可恢复**再执行：

| 操作 | 风险 | 保护措施 |
|------|------|---------|
| `auth/logout` / `auth/startLocalMode` | 断开 Remote 会话 | 确保有 login credentials 可恢复 |
| `feeds/deleteFeed` / `feeds/deleteCategory` | 删除真实订阅 | **不在用户真实数据上测试** —— 跳过或只验证端点存在 |
| `articles/toggleRead` / `articles/toggleStar` | 改变文章状态 | 执行后立即反向操作恢复 |
| `feeds/moveFeed` | 改变 Feed 分类 | 记录原分类，执行后恢复 |
| `settings/setSyncInterval` | 改变同步配置 | 记录原值，执行后恢复 |

**原则**：测试状态切换类操作时，遵循 `记录原值 → 修改 → 验证 → 恢复` 模式。

**效率要求**：
- 同一故事内多个独立的 data 查询可以并行 curl
- 不要在每个 curl 之间输出冗长的思考过程，保持简洁

### Step 3.5: 自动修复（代码 + 文档）

#### 3.5a: 修复故事文档（参数/路径不匹配）

**触发条件**：Step 3 的「故事文档修复清单」非空。

用 Agent 工具后台批量修复所有故事文档中的路径和参数名错误。给 Agent 提供：
- 完整的实际端点列表（从 /providers 获取）
- 每个端点的参数名（从 debug_action_registry.dart 中读取，或从 error message 推断）
- 需要修复的文件列表和具体错误

#### 3.5b: 自动补全 Debug Server 端点

**触发条件**：Step 3 的「待补端点清单」非空。

**核心原则：端点缺失不是需要人工处理的问题，AI 完全有能力自己补上。**

1. **读 Debug Server 代码** — `lib/dev_tools/debug_server.dart`（或项目的 Debug Server 入口），理解端点注册模式
2. **读相关 ViewModel/Repository** — 找到故事需要但未暴露的方法
3. **区分**：
   - **方法存在但未注册** → 直接在 registry 中注册
   - **方法不存在（功能未实现）** → 标记为"功能缺失"，不要凭空创造
4. **批量注册端点** — 按现有模式一次性补齐
5. **安全重启 App**（见下方）
6. **第二轮验证** — 只重跑 Step 3 中标记为 pending 的故事/步骤

> **守卫**：如果待补端点 > 15 个，说明 Debug Server 覆盖率严重不足，先告知用户再批量补（避免一次性改动过大）。

### Step 3.9: 恢复初始状态

验证全部完成后，对照 Step 2a 的「初始快照」恢复被改变的状态：

```
初始快照: auth=authenticated, feeds=27, syncInterval=minutes15
当前状态: auth=localMode ← 需恢复！

→ 执行 auth/login 恢复 → sync/fullSync 重建数据
→ 验证 feeds count 与快照一致
```

### 安全重启 App

`run_in_background` 模式下没有交互式热重启，必须 kill → 等死 → 重启。**不干净的 kill 会导致新旧进程抢数据库（disk I/O error）**。

```bash
# 1. 先杀 App 进程（不只是 flutter run，要杀实际 App binary）
pkill -f "flutter run" 2>/dev/null; pkill -f "<app_binary_name>" 2>/dev/null

# 2. 确认进程已死（单次检查，不轮询）
pgrep -f "<app_binary_name>" || echo "App stopped"

# 3. 重启（同 Step 0 自动启动流程，用 run_in_background）
```

> `<app_binary_name>` 从 `pubspec.yaml` 的项目名或 build 产物路径推断。

### Step 4: 输出报告

```markdown
## User Stories 验证报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx

### 结果
| 故事 | 状态 | 详情 |
|------|------|------|
| 01-first-time-user | ✅ 通过 | 5/5 步全部通过 |
| 02-daily-selection | ✅ 通过（修复后） | Step 3 groupId 未传递，已修复 |
| 03-data-management | ✅ 通过（补端点后） | 补注册 moveFeed/deleteFeed/rename 端点 |
| 04-ai-summary | ⏭️ 跳过 | 需要 AI API key 配置（外部依赖） |

### AI 自动修复记录
- [代码修复] 02-daily-selection Step 3: groupId 未传递导致选择失败（file:line）
- [文档修复] 17 处故事文档端点路径/参数名修正
- [补端点] 03-data-management: 注册 feeds/moveFeed, feeds/deleteFeed, categories/rename（debug_server.dart:line）
- [兼容性记录] Miniflux 不支持 rename-tag，已记录到 API 文档

### 需要人工处理
- 04-ai-summary: 需配置 AI API key 才能测试完整流程

### 状态恢复
- ✅ auth: authenticated (已恢复)
- ✅ feeds: 27 (未变)
- ✅ syncInterval: minutes15 (已恢复)
```

---

## 与 ai-explore 的关系

`ai-qa-stories` 是 `ai-explore` 的前置条件。只有所有故事通过后，才有意义进入启发式探索。`ai-explore` 会自动先调用本 skill。

## Gotchas / 踩坑点

1. **不硬编码端口** — 按 Step 0 端口发现协议
2. **端口冲突** — 同一台机器多个项目可能各自有 Debug Server，检查 /providers 返回的 actions 是否匹配当前项目
3. **故事按编号顺序执行** — 前序故事可能创建后序需要的数据
4. **autoDispose 的 State 可能为空** — 断言用 `/data/` 而非 `/state/`
5. **修复代码后必须安全重启** — 见"安全重启 App"流程。直接 `pkill -f "flutter run"` 不够，必须同时杀 App binary 并确认死干净
6. **五种问题，五种处理** — 通过 / 代码 bug / 参数不匹配 / 端点缺失 / 外部依赖，各有明确处理路径
7. **用 /logs 辅助诊断** — `curl -s "localhost:$PORT/logs?count=20"` 看操作历史
8. **禁止手写轮询循环** — 不要写 `for i in 1 2 3 ... curl` 轮询。用 `run_in_background` 等完成通知
9. **利用 /providers 预判** — providers 列表可以提前跳过不存在的端点，避免无效 curl
10. **启动和加载并行** — App 启动是后台任务，前台同时加载故事文件，不要串行等待
11. **zsh URL 转义** — `curl url?param=value` 在 zsh 中 `?` 会被当 glob 展开，必须用双引号包裹 URL：`curl -s "localhost:$PORT/logs?count=20"`
12. **iOS 首次编译耗时** — Xcode build 可能需要 45s+，`start-dev.sh` 的 60s 超时可能不够。超时后检查 `/tmp/flutter_run.log` 确认构建状态，构建完成的 App 仍会自行启动
13. **破坏性操作先快照** — logout、mode 切换、delete 等操作前必须记录原值，验证后恢复。deleteFeed/deleteCategory 不在真实数据上执行，只验证端点存在
14. **外部服务区分暂时 vs 永久** — 超时/网络错误可重试；404/NOT_FOUND 是永久限制，记录到文档而非反复重试
15. **先对账再执行** — Step 1.5 的 curl 预校验能提前发现故事文档中的路径/参数名错误，避免执行时逐个排查浪费 token
