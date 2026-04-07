---
name: init-debug-server
description: >
  This skill should be used when setting up a Debug State Server for a Flutter
  project, enabling AI autonomous development loop via HTTP endpoints. Use when
  the user says "debug server", "自主开发", "加调试接口", "init debug", or when
  starting a new Flutter project that needs programmatic state verification.
version: 0.2.0
---

# Init Debug State Server — AI 自主开发闭环基建

## 目的

为 Flutter 项目搭建 debug 模式 HTTP Server（shelf, localhost:8788），让 AI 通过 curl 读写 App 状态，摆脱"写代码 → 人工点击验证"的瓶颈。

## 架构铁律：Headless Bypass Policy

> Debug Server 是**无头客户端 (Headless Client)**，不是 UI 客户端。
> 它没有 Widget tree，不持有任何 Provider 的订阅，不维护 UI 生命周期。
> 因此它**不能**像 UI 那样通过 ViewModel 驱动业务。

```
[Debug API Action] ──(X FORBIDDEN)──> ViewModel / StateNotifier
[Debug API Action] ──(V REQUIRED)──>  UseCase / Repository (via DI) ──> DB

[验证操作结果]    ──(X FORBIDDEN)──> GET /state/{name}  (读 ViewModel 内存)
[验证操作结果]    ──(V REQUIRED)──>  GET /data/{name}   (直读 DB/Repository)
```

**为什么？** Riverpod autoDispose Provider 在没有 Widget watch 时，ref 在 async gap 后被回收。Debug Server 通过 `c.read(notifier)` 调用任何包含 `await` 的方法**必然崩溃**。更隐蔽的是：action 执行后自动回读 Provider state 做验证，也会触发同样的错误。

**唯一例外：** 非 autoDispose 的全局 Provider（如 AppViewModel），且有 Widget 始终 watch 着，可以安全 `c.read()`。但为了一致性，新项目**默认全部走 DI**。

---

## 触发条件

1. 用户要求为 Flutter 项目添加 Debug State Server
2. 新 Flutter 项目启动，需要 AI 自主验证能力
3. 用户提到"自主开发"、"调试接口"、"curl 验证"

---

## 执行流程

### Step 1: 扫描项目架构（只读）

扫描 `lib/` 目录，找出：
- **Provider/ViewModel**：`grep -rn "NotifierProvider\|class.*ViewModel" lib/ --include="*.dart"`
- **State 类**：`grep -rn "@freezed" lib/ --include="*state*.dart"`
- **Repository**：`grep -rn "abstract class.*Repository" lib/ --include="*.dart"`
- **UseCase**：`grep -rn "class.*UseCase" lib/ --include="*.dart"`
- **DI 系统**：GetIt / SimplifiedDI / 手动 Provider — 确认 UseCase/Repository 的获取方式
- **App 根组件**：找到 `ConsumerStatefulWidget` 的主 App，确认 `postFrameCallback` 位置

输出扫描报告，列出建议注册的 State / Data / Action 端点，**等用户确认**。

### Step 2: 生成代码

参考 `references/design-decisions.md` 的设计原则，生成 3 个文件：

1. **`lib/dev_tools/debug_server.dart`** — HTTP 核心 + 日志缓冲区（几乎不需要定制）
2. **`lib/dev_tools/debug_state_registry.dart`** — State + Data 读取（根据 Step 1 定制）
3. **`lib/dev_tools/debug_action_registry.dart`** — Action 执行（根据 Step 1 定制）

**必须包含日志链路**：DebugServer 内置环形日志缓冲区（200 条），记录所有请求/响应，通过 `GET /logs` 暴露。见 `references/log-chain.md`。

#### Action Handler 生成规则（Headless Bypass 落地）

```
CRITICAL: ActionHandlers must act as backend controllers.
          Interact ONLY with UseCases/Repositories via DI.
          NEVER c.read(xxxViewModelProvider.notifier).
```

**判断流程**：

1. 该操作有对应 UseCase 且已注册到 DI？→ `DI.get<XxxUseCase>().call(params)`
2. 没有 UseCase 但有 Repository？→ `DI.get<XxxRepository>().method()`
3. 都没有（说明业务逻辑锁在 ViewModel 里）？→ **不注册该 action**，标记为"需重构后再暴露"

**Action 结果自检纪律**：

action 执行后的自动数据回读**必须走 `/data/` 端点（直读 DB）**，严禁回读 `/state/`（ViewModel 内存状态）。这条规则在 `debug_server.dart` 的 `_handleExecuteAction` 中体现：

```dart
// action 执行后，自动附带最新数据
// ✅ 正确：直读数据库
autoData = await DebugStateRegistry.readData('groups', const {});

// ❌ 禁止：读 ViewModel 状态（autoDispose 会炸）
// autoData = DebugStateRegistry.readState('management', container);
```

唯一例外：非 autoDispose 的全局 Provider（如 `app`），可以 `readState('app', container)`。

### Step 3: 集成

- 在 App 根组件 `postFrameCallback` 中启动：`DebugServer.start(ProviderScope.containerOf(context))`
- 在 `dispose` 中停止
- 处理架构守护测试（coupling guard 白名单）

### Step 4: 打通启动脚本 + 测试数据

**启动脚本** — 更新 `scripts/start-dev.sh` 增加 `--background` 模式：
- 后台运行 `flutter run`，日志写入文件
- 轮询等待 Debug Server ready（**每次迭代必须 sleep 1s**，否则 60 次瞬间完成报超时）
- `view-dev-log.sh` 可查看构建日志
- 见 `references/log-chain.md` 的模板

**测试数据播种脚本** — 创建 `scripts/seed-test-data.sh`：
```bash
#!/bin/bash
# seed-test-data.sh — 播种/清理测试数据
PORT=8788

if [ "${1:-}" = "clean" ]; then
  echo "🧹 Cleaning test data..."
  # 读取所有非默认分组并删除
  # 具体逻辑根据项目实体调整
else
  echo "🌱 Seeding test data..."
  # 通过 Debug Server action 创建测试实体
  curl -s -X POST "localhost:$PORT/action/xxx/create" -d '{"name":"Test Item"}' > /dev/null
fi
```

### Step 5: 验证

```bash
./scripts/start-dev.sh --background   # 启动
curl localhost:8788/providers          # 发现接口
curl localhost:8788/data/groups        # 读数据
curl -X POST localhost:8788/action/xxx/create -d '{"name":"test"}'  # 执行操作
curl localhost:8788/logs               # 查看操作日志
```

跑全量测试确认无回归。

### Step 6: 文档

更新 CLAUDE.md（快速命令区 + Debug Server curl 示例）和 FEATURE_CODE_MAP（文件索引）。

---

## Clean Session Startup（AI 协作必须遵守）

### 问题背景

Flutter App 有独立的 Drift SQLite 副本。通过外部脚本（`seed-test-data.sh`）修改 DB 时，运行中的 App 的 Riverpod 内存状态**不会**自动同步。这会导致：

- App UI 显示旧数据（Riverpod 缓存）
- Debug Server 返回最新数据（直读 DB）
- AI 三角验证矛盾 → 错误结论

### 职责边界

| 组件 | 职责 |
|------|------|
| `init-debug-server` | 搭建 Debug Server 代码骨架 |
| `start-dev.sh --force-reset` | 提供干净进程沙箱 |
| `seed-test-data.sh` | 通过 Debug Server API 播种数据 |
| **`prep-cyborg-env` Skill** | **统一环境准备**：Kill → Seed → Restart → Verify |
| `ai-explore` / `ai-qa-stories` | **假设环境干净**，不处理状态修复 |

### 正确的启动顺序

```
1. prep-cyborg-env（或 ./scripts/prep-env.sh）
   ├── Kill 所有 Flutter 进程
   ├── Seed 数据（通过 Debug Server API）
   └── start-dev.sh --force-reset（全新启动 + Wait ready）
   
2. 健康验证
   ├── curl /state/home 的 activeGroupId
   ├── curl /data/groups 的第一个分组 id
   └── 两者必须一致
   
3. 开始 AI 业务 Skill（ai-explore / ai-qa-stories）
```

### 启动脚本更新记录

- `start-dev.sh --force-reset`：新增强制重置参数，保证干净沙箱
- `scripts/prep-env.sh`：一键环境准备脚本（Kill → Seed → Reset → Verify）

---

## Gotchas / 踩坑点

### 架构级（生成代码时必须遵守）

1. **Headless Bypass 是不可妥协的** — Action Handler 永远不走 ViewModel。即使"这个 Provider 好像没用 autoDispose"，也不要碰。一致性比优化重要
2. **shelf 放 dependencies 不是 dev_dependencies** — `lib/` 下无法导入 dev_dependencies，但 `kDebugMode` + tree shaking 保证零生产影响
3. **Dart 无运行时反射** — 所有映射手动维护（Map 字面量），无法通过字符串动态调用方法
4. **Action 后自动返回数据** — 一次 curl 完成操作+验证，对 LLM ReAct 循环效率至关重要。但回读**只走 Data 层**
5. **端口冲突** — 检查项目是否有后端服务占用 8787/8788，同机器多项目各自有 Debug Server 时注意端口分配

### 操作级（遇到问题时排查）

6. **start-dev.sh 轮询必须有 sleep** — 没有 sleep 的 for 循环 60 次瞬间完成就报"超时"，但 flutter run 仍在后台编译。脚本超时 ≠ 启动失败
7. **flutter run 后台不转发 Dart 日志** — `developer.log()` 只在前台 TTY 下可见，所以 DebugServer 自带日志缓冲区通过 `/logs` 暴露
8. **State 序列化用手动 toMap** — State 类通常无 `toJson()`，嵌套复杂类型多，手动写比给 Freezed 加 fromJson 务实
9. **`@visibleForTesting` 方法** — 如果 ViewModel 已有 `xxxForTesting()` 方法，可在 UseCase 不存在时作为**临时方案**复用，但优先级低于 DI 直调。文件头加 `// ignore_for_file: invalid_use_of_visible_for_testing_member`

---

## 参考实现

flametree_pick 完整实现：
- `flametree_pick/lib/dev_tools/debug_server.dart` — HTTP 核心（可直接复制）
- `flametree_pick/lib/dev_tools/debug_state_registry.dart` — State + Data 注册
- `flametree_pick/lib/dev_tools/debug_action_registry.dart` — Action 注册
- `flametree_pick/scripts/seed-test-data.sh` — 测试数据播种
- `flametree_pick/scripts/start-dev.sh` — 支持 `--force-reset` 强制重置
- `flametree_pick/scripts/prep-env.sh` — 一键环境准备（Kill → Seed → Reset → Verify）
