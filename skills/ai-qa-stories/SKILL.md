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
version: 0.5.0
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

**核心原则：启动和加载故事并行，不傻等。整个 QA 会话只启动一次 App。**

```
┌─ 0. 先杀残留进程！────────────────────────────────┐
│ pkill -9 -f "<app_binary>" ; pkill -f "flutter run"│
│ 确认无残留后再启动                                   │
└────────────────────────────────────────────────────┘
          ↓
┌─ 后台启动 App（run_in_background）──────────────┐   ┌─ 前台加载故事 ─────────┐
│ 无参数 → open Simulator + start-dev --background │   │ 并行读取所有 story 文件  │
│ 有参数 → start-dev --background --device <设备>   │   │ 记录 story 列表          │
└─────────────────────────────────────────────────┘   └────────────────────────┘
          ↓ 故事加载完后
    用 tail 检查构建日志，看到 DevTools URL 即就绪
          ↓
    curl providers 确认
          ↓
    ✅ 响应 → 继续 Step 2
    ❌ 仍未响应 → 输出错误，终止
```

> **⚠️ 关键经验：start-dev.sh 的等待循环可能没有 sleep**，60 次 curl 迭代瞬间完成后脚本报"超时"退出，但 flutter run 仍在后台编译。**脚本超时 ≠ 启动失败**。正确做法是等后台任务完成通知到达，然后 `tail -3` 构建日志看是否有 DevTools URL。

**具体步骤**：

1. **先杀残留进程**（防止多实例堆积）：
   ```bash
   # <app_binary> 从 pubspec.yaml name 或 build 产物路径推断
   pkill -9 -f "<app_binary>" 2>/dev/null
   pkill -f "flutter run" 2>/dev/null
   ```

2. **后台启动 App**（`run_in_background: true`）— **必须先判断设备参数**：

   | 用户输入 | 启动命令 |
   |---------|---------|
   | `/ai-qa-stories`（无参数） | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `/ai-qa-stories macos` | `./scripts/start-dev.sh --background --device macos` |
   | `/ai-qa-stories ios` | `open -a Simulator && ./scripts/start-dev.sh --background` |
   | `/ai-qa-stories <其他设备>` | `./scripts/start-dev.sh --background --device <设备>` |

   > **注意**：传了非模拟器设备参数时，**不要** `open -a Simulator`。所有路径统一走 `start-dev.sh`。
   >
   > **⚠️ iOS 首次编译**：Xcode build 可能需要 45s+，可能超过脚本超时。超时不代表失败。

3. **同时（不要等启动完成！）并行加载所有故事文件**（Step 1）

4. 故事加载完后，检查 Server 是否已就绪：
   - 先等后台启动任务的完成通知（**不要自己写 for 循环轮询**）
   - 通知到达后 `tail -3` 构建日志，看是否有 `Dart VM Service` 或 `DevTools` URL
   - 有 → `curl providers` 确认 → 继续
   - 无 → 输出诊断信息（`./scripts/view-dev-log.sh latest`），终止

**禁止行为**：
- ❌ 写 `for i in 1 2 3 ...` 的 curl 轮询循环
- ❌ 反复 `ps aux | grep flutter` 检查进程
- ❌ 反复 `tail /tmp/flutter_run.log` 查看编译进度
- ❌ 在 shell 命令中使用 `sleep`（会被 hook 拦截）
- ❌ 启动完成前就开始 curl 验证
- ❌ **重复调用 start-dev.sh**（每次调用都会启动新 App 实例！整个 QA 会话只启动一次）

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
5. **安全重启 App**（见下方）— **攒齐所有改动，只重启一次**
6. **第二轮验证** — 只重跑 Step 3 中标记为 pending 的故事/步骤

> **守卫**：如果待补端点 > 15 个，说明 Debug Server 覆盖率严重不足，先告知用户再批量补（避免一次性改动过大）。

#### ⚠️ Riverpod autoDispose 陷阱（补端点时必读）

**问题**：Riverpod 3 的 `@riverpod` 注解默认启用 autoDispose。从 Debug Server 调用 ViewModel 方法时，Provider 的 `ref` 在异步操作期间被回收，导致 `Cannot use Ref after disposed` 错误。

**根本原因**：Debug Server 通过 `ProviderContainer.read()` 访问 Provider，不像 Widget 的 `ref.watch()` 能保持 Provider 存活。即使用 `container.listen()` 也无法彻底解决——因为 ViewModel 内部使用 `ref` 访问其他 Provider，而内部 `ref` 会在 async gap 期间失效。

**更隐蔽的坑**：Debug Server 的 `_handleExecuteAction` 在 action 执行后会自动回读 Provider state（`readState(providerName, container)`），这也会触发 autoDispose 错误。**必须用 try-catch 包裹此回读。**

**正确做法：Action handler 绕过 ViewModel，直接用 Repository/Service 层**：

```dart
// ❌ 错误 — ViewModel 的 ref 会在 await 后失效
await c.read(searchViewModelProvider.notifier).searchImmediate(query);

// ❌ 不够 — c.listen 只保活 Provider 本身，内部 ref 仍可能失效
final sub = c.listen(searchViewModelProvider, (_, __) {});
await c.read(searchViewModelProvider.notifier).searchImmediate(query);
sub.close();

// ✅ 正确 — 绕过 ViewModel，用 ServiceLocator 直接访问 Repository
final result = await services.searchRepository.searchAll(query);
```

**哪些 Provider 不受影响**（可以直接 c.read()）：
- `authViewModelProvider` — 通常有 widget 始终 watch 着（全局状态）
- `playerViewModelProvider` — 被 AudioService 流持续同步，保持存活
- `homeViewModelProvider` — 首页通常可见

**哪些 Provider 必须绕过**：
- `searchViewModelProvider` — 只在搜索页活跃
- `playlistViewModelProvider` — 只在播放列表页活跃
- `downloadViewModelProvider` — 只在下载页活跃
- 任何 autoDispose + 页面级的 Provider

### Step 3.9: 恢复初始状态

验证全部完成后，对照 Step 2a 的「初始快照」恢复被改变的状态：

```
初始快照: auth=authenticated, feeds=27, syncInterval=minutes15
当前状态: auth=localMode ← 需恢复！

→ 执行 auth/login 恢复 → sync/fullSync 重建数据
→ 验证 feeds count 与快照一致
```

### 安全重启 App（整个 QA 最多重启 1 次！）

**⚠️ 这是本 skill 最容易犯的错误：反复重启导致多个 App 窗口堆积。**

`run_in_background` 模式下没有交互式热重启，必须 kill → 确认死干净 → 重启。

**铁律**：
- 整个 QA 会话**最多重启 1 次**（补完端点后）
- 如果改了代码需要重启，把所有改动攒到一起，一次性重启
- 每次启动 `start-dev.sh` 都会创建一个新 App 窗口，旧窗口不会自动关闭！

```bash
# 1. 杀 App 进程（-9 强制杀，同时杀 flutter run 和 App binary）
pkill -9 -f "<app_binary_name>" 2>/dev/null
pkill -f "flutter run" 2>/dev/null

# 2. 确认进程已死（单次检查，不轮询）
pgrep -f "<app_binary_name>" || echo "App stopped"

# 3. 重启（同 Step 0 自动启动流程，用 run_in_background）
#    start-dev.sh 的超时可能很快到，但 flutter run 仍在后台编译
#    等 run_in_background 完成通知，然后 tail 日志确认 DevTools URL 出现
```

> `<app_binary_name>` 从 `pubspec.yaml` 的项目名或 build 产物路径推断。
> 例如 lt_music → "FlameTree Music"，flametree_rss_reader → "FlameTree RSS"

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

### 进程管理（最高优先级）
1. **绝不重复启动 App** — 每次 `start-dev.sh` 都打开新窗口，旧窗口不会关闭。整个 QA 会话只启动一次，补端点后只重启一次
2. **杀进程要彻底** — `pkill -f "flutter run"` 不够，必须 `pkill -9 -f "<App名>"` 同时杀。`<App名>` 从 build 产物推断（如 "FlameTree Music"）
3. **start-dev.sh 超时 ≠ 失败** — 脚本的等待循环可能没 sleep，60 次迭代瞬间完成就报"超时"，但 flutter run 仍在后台编译。正确做法：等 `run_in_background` 完成通知，然后 `tail` 日志看 DevTools URL

### Riverpod 陷阱
4. **autoDispose Provider 不能从 Debug Server 直接调用** — ViewModel 的 `ref` 在 async gap 中被回收。补端点时 action handler 必须走 Repository/Service 层，不走 ViewModel
5. **debug_server 的自动状态回读会触雷** — `_handleExecuteAction` 在 action 后自动 `readState(providerName)`，autoDispose 的 provider 会报错。必须用 try-catch 包裹
6. **autoDispose State 可能为空** — 断言优先用 `/data/`（直读 Repository）而非 `/state/`（读 ViewModel 内存状态）

### 数据与 curl
7. **randomSongs 每次返回不同集合** — `data/tracks` 底层调 `getRandomSongs()`，trackId 跨调用不稳定。获取 trackId 后立即使用，或从 `state/home` 的 randomSongs（内存缓存，稳定）获取
8. **JSON 响应含控制字符** — 错误消息含 `\n`，Python `json.loads()` 默认 strict 模式会报错。用 `json.loads(s, strict=False)` 解析
9. **zsh URL 转义** — `curl url?param=value` 在 zsh 中 `?` 被当 glob，必须双引号包裹
10. **播放操作间要留间隔** — 快速连续 play/pause/next 会导致音频爆音（audio pop），影响用户体验

### 流程纪律
11. **不硬编码端口** — 按 Step 0 端口发现协议
12. **端口冲突** — 同机器多项目可能各自有 Debug Server，检查 /providers 的 actions 是否匹配当前项目
13. **故事按编号顺序执行** — 前序故事可能创建后序需要的数据
14. **五种问题，五种处理** — 通过 / 代码 bug / 参数不匹配 / 端点缺失 / 外部依赖
15. **先对账再执行** — Step 1.5 预校验省大量 token
16. **用 /logs 辅助诊断** — `curl -s "localhost:$PORT/logs?count=20"`
17. **破坏性操作先快照** — logout、delete 等操作前记录原值，验证后恢复
18. **禁止手写轮询循环** — 用 `run_in_background` 等完成通知
