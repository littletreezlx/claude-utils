---
name: init-debug-server
description: >
  This skill should be used when setting up a Debug State Server for a Flutter
  project, enabling AI autonomous development loop via HTTP endpoints. Use when
  the user says "debug server", "自主开发", "加调试接口", "init debug", or when
  starting a new Flutter project that needs programmatic state verification.
version: 0.1.0
---

# Init Debug State Server — AI 自主开发闭环基建

## 目的

为 Flutter 项目搭建 debug 模式 HTTP Server（shelf, localhost:8788），让 AI 通过 curl 读写 App 状态，摆脱"写代码 → 人工点击验证"的瓶颈。

## 触发条件

1. 用户要求为 Flutter 项目添加 Debug State Server
2. 新 Flutter 项目启动，需要 AI 自主验证能力
3. 用户提到"自主开发"、"调试接口"、"curl 验证"

## 执行流程

### Step 1: 扫描项目架构（只读）

扫描 `lib/` 目录，找出：
- **Provider/ViewModel**：`grep -rn "NotifierProvider\|class.*ViewModel" lib/ --include="*.dart"`
- **State 类**：`grep -rn "@freezed" lib/ --include="*state*.dart"`
- **Repository**：`grep -rn "abstract class.*Repository" lib/ --include="*.dart"`
- **DI 系统**：GetIt / SimplifiedDI / 手动 Provider
- **App 根组件**：找到 `ConsumerStatefulWidget` 的主 App，确认 `postFrameCallback` 位置

输出扫描报告，列出建议注册的 State / Data / Action 端点，**等用户确认**。

### Step 2: 生成代码

参考 flametree_pick 的实现（见 `references/` 目录），生成 3 个文件：

1. **`lib/dev_tools/debug_server.dart`** — HTTP 核心 + 日志缓冲区（几乎不需要定制）
2. **`lib/dev_tools/debug_state_registry.dart`** — 根据 Step 1 结果定制
3. **`lib/dev_tools/debug_action_registry.dart`** — 根据 Step 1 结果定制

**必须包含日志链路**：DebugServer 内置环形日志缓冲区，记录所有请求/响应，通过 `GET /logs` 暴露。见 `references/log-chain.md`。

关键：读 `references/design-decisions.md` 了解每个设计选择的 why。

### Step 3: 集成

- 在 App 根组件 `postFrameCallback` 中启动：`DebugServer.start(ProviderScope.containerOf(context))`
- 在 `dispose` 中停止
- 处理架构守护测试（coupling guard 白名单）
- `xcrun simctl privacy booted grant pasteboard <bundle_id>`（消除剪贴板弹窗）

### Step 4: 打通启动脚本

更新 `scripts/start-dev.sh` 增加 `--background` 模式：
- 后台运行 `flutter run`，日志写入 `/tmp/flutter_run.log`
- 自动轮询等待 Debug Server ready
- `view-dev-log.sh` 可查看构建日志

见 `references/log-chain.md` 的启动脚本模板。

### Step 5: 验证

```bash
./scripts/start-dev.sh --background   # 启动
curl localhost:8788/providers          # 发现接口
curl localhost:8788/logs               # 查看操作日志
```

跑全量测试确认无回归。

### Step 6: 文档

更新 CLAUDE.md（快速命令）和 FEATURE_CODE_MAP（文件索引）。

## Gotchas / 踩坑点

1. **shelf 放 dependencies 不是 dev_dependencies** — `lib/` 下无法导入 dev_dependencies，但 `kDebugMode` + tree shaking 保证零生产影响
2. **autoDispose Provider 的 State 可能为空** — 必须提供 `/data/` 层（Repository 直读数据库）作为可靠数据源
3. **Dart 无运行时反射** — 所有映射手动维护（Map 字面量），无法通过字符串动态调用方法
4. **`@visibleForTesting` 方法是捷径** — ViewModel 已有的测试方法可直接复用，加 `ignore_for_file`
5. **端口冲突** — 检查项目是否有后端服务占用 8787/8788
6. **State 序列化用手动 toMap** — State 类通常无 `toJson()`，嵌套类型复杂，手动写比给 Freezed 加 fromJson 务实
7. **Action 后自动返回数据** — 一次 curl 完成操作+验证，对 LLM ReAct 循环效率至关重要
8. **flutter run 后台不转发 Dart 日志** — `developer.log()` 只在前台 TTY 下可见；`flutter logs` 抓 syslog 也抓不到。解决方案：DebugServer 自己记录操作日志到内存环形缓冲区，通过 `/logs` 暴露
9. **start-dev.sh --background** — AI 自主启动 App 的标准入口，自动等 server ready，日志统一写文件
