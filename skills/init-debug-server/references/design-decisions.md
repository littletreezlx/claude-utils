# Debug State Server — 设计决策参考

## 架构总览

```
Claude Code ──curl──> shelf HTTP Server (localhost:8788, debug only)
                        │
                        ├─ GET  /providers          发现接口
                        ├─ GET  /state/{name}       ViewModel 内存状态
                        ├─ GET  /data/{name}        Repository 直读数据库
                        ├─ POST /action/{n}/{m}     执行业务操作（Headless Bypass）
                        └─ GET  /logs               操作日志环形缓冲区
```

## 核心设计：两层读取

| 层 | 端点 | 数据来源 | 适用场景 |
|----|------|---------|---------|
| State | `/state/{name}` | Riverpod ViewModel | 验证 UI 状态（仅非 autoDispose Provider） |
| Data | `/data/{name}` | Repository → Database | 验证数据持久化（**永远可靠，优先使用**） |

autoDispose 的 Provider 在没有 UI 监听时不订阅数据流，State 为空或读取即崩。Data 层绕过这个限制。

## 核心设计：Headless Bypass

Debug Server 是**无头客户端**，没有 Widget tree，没有 Provider 订阅。它与 App 的交互必须走基础设施层（UseCase / Repository），不走 UI 状态层（ViewModel）。

```
UI Client (正常 App):
  用户点击 → Widget → ref.read(viewModelProvider.notifier).doSomething()
                        ↓ ViewModel 内部
                        ref.read(useCaseProvider).call(params)

Headless Client (Debug Server):
  curl POST → ActionHandler → DI.get<UseCase>().call(params)
                              ↑ 直接走这里，跳过 ViewModel
```

**为什么不能经过 ViewModel？**

Riverpod autoDispose 机制：当没有 Widget watch 一个 Provider 时，Provider 在异步操作的 `await` 间隙被回收，`ref` 变为 disposed。Debug Server 通过 `c.read(notifier)` 调用方法时：
1. `c.read()` 临时激活 Provider
2. 方法内部遇到 `await`，控制权交还事件循环
3. Riverpod 发现没有 listener，autoDispose 触发回收
4. `await` 返回后方法继续执行，使用已 disposed 的 `ref` → **崩溃**

更隐蔽的坑：action 执行后 `_handleExecuteAction` 自动回读 Provider state 做验证，也会唤醒已 disposed 的 Provider 导致同样的错误。

## 为什么每个选择

| 决策 | 选择 | 原因 |
|------|------|------|
| HTTP 库 | shelf + shelf_router | Dart 官方维护，路由简洁，成熟 |
| 放 dependencies | 是 | dev_dependencies 无法在 lib/ 导入；kDebugMode + tree shaking = 零生产影响 |
| 反射 | 手动 Registry (Map) | Flutter 禁用 dart:mirrors（AOT） |
| State 序列化 | 手动 toMap | State 类嵌套 Set/Map 等复杂类型，Freezed 加 fromJson 需要自定义 converter，成本高 |
| Container 获取 | ProviderScope.containerOf(context) | 在 postFrameCallback 中调用，此时 ProviderScope 已挂载 |
| Action 后自动返回数据 | 通过 Data 层回读 | 一次 curl 完成操作+验证；**必须走 Data 层避免 autoDispose 炸裂** |
| HTTP vs WebSocket | HTTP | curl 天然支持；无状态模型匹配 LLM ReAct 循环 |

---

## Registry 编写规则

### StateReader（`/state/{name}`）

只注册**非 autoDispose 的全局 Provider**。页面级 autoDispose Provider 不注册 State，改用 Data 层覆盖。

```dart
// 非 autoDispose 的全局 Provider → 安全
'app': (c) {
  final s = c.read(appViewModelProvider);
  return {
    'currentLanguage': s.currentLanguage,
    'isAnimationEnabled': s.isAnimationEnabled,
    'isLoading': s.isLoading,
  };
},

// ❌ autoDispose 的页面级 Provider → 不要注册为 State
// 'management': (c) => c.read(managementProvider).toMap(), // 会崩
```

如果确实需要暴露某个 autoDispose ViewModel 的当前内存状态（如调试时有 Widget 在 watch），用 try-catch 包裹：

```dart
'management': (c) {
  try {
    final s = c.read(managementViewModelProvider);
    return { /* ... */ };
  } catch (_) {
    return {'error': 'Provider not active (no UI watching)'};
  }
},
```

### DataReader（`/data/{name}`）

通过 DI 获取 Repository，直读数据库。永远可靠，不受 autoDispose 影响。

```dart
// 支持 query params 过滤
'options': (params) async {
  final repo = DI.get<OptionRepository>();
  final groupIdStr = params['groupId'];
  if (groupIdStr != null) {
    final groupId = int.parse(groupIdStr);
    final result = await repo.getOptions(groupId);
    return result.fold(
      onSuccess: (options) => {
        'options': options.map((o) => o.toJson()).toList(),
        'count': options.length,
      },
      onFailure: (error) => {'error': error.toString()},
    );
  }
  // 全量查询 ...
},
```

### ActionHandler（`/action/{name}/{method}`）

**强制规则：ActionHandler 是后端 Controller，只与 UseCase / Repository 交互。**

```dart
// ✅ 正确：通过 DI 获取 UseCase，直接调用
'management/deleteGroup': (c, p) async {
  final useCase = DI.get<DeleteGroupUseCase>();
  final result = await useCase.call(DeleteGroupParams(id: p['id'] as int));
  // result 是 Result<void>，处理成功/失败
  return result.fold(
    onSuccess: (_) => {'action': 'deleteGroup', 'groupId': p['id']},
    onFailure: (e) => {'action': 'deleteGroup', 'error': e.toString()},
  );
},

// ✅ 正确：没有 UseCase 时直接用 Repository
'management/selectGroup': (c, p) async {
  // selectGroup 只是写一个 ID，没有 UseCase
  // 如果用 SharedPreferences 或其他存储，直接调
  final repo = DI.get<GroupRepository>();
  // ... 或者如果这纯粹是 UI 状态（没有持久化），
  // 那它不应该成为 Debug Action
  return {'action': 'selectGroup', 'groupId': p['id']};
},

// ✅ 正确：随机选择（业务核心，有独立 UseCase）
'random/quickSelect': (c, p) async {
  final useCase = DI.get<QuickRandomSelectUseCase>();
  final result = await useCase.call(
    QuickRandomSelectParams(groupId: p['groupId'] as int),
  );
  return result.fold(
    onSuccess: (option) => {
      'action': 'quickSelect',
      'selectedOption': option?.toJson(),
    },
    onFailure: (e) => {'action': 'quickSelect', 'error': e.toString()},
  );
},

// ❌ 绝对禁止：通过 ViewModel 调用（autoDispose 必崩）
// 'management/deleteGroup': (c, p) async {
//   await c.read(managementViewModelProvider.notifier).deleteGroupData(id);
// },
```

**特殊情况：selectGroup 等纯 UI 状态操作**

`selectGroup` 在 ViewModel 中只改内存状态（当前选中的分组 ID），不涉及数据库。这类操作有两种处理方式：

1. **如果有持久化**（如 SharedPreferences 存储 lastSelectedGroupId）→ 通过 DI 直调存储层
2. **如果纯内存状态**→ 可以 `c.read(notifier).selectGroup(id)`（同步操作，无 async gap，不会触发 autoDispose）。但仍需确认该 Provider 当前被 watch 着

判断不了的情况，宁可不注册该 action。

### Action 注册优先级

1. **CRUD 操作** — 最常验证（创建/删除/更新核心实体）
2. **核心业务** — 项目灵魂功能（如随机选择、文章搜索）
3. **设置变更** — 语言、主题、开关（通常是全局非 autoDispose Provider）
4. **状态切换** — 选中、排序、筛选（谨慎，很多是纯 UI 状态）

---

## 集成代码片段

### App 根组件启动

```dart
// initState → postFrameCallback 中
if (kDebugMode) {
  DebugServer.start(ProviderScope.containerOf(context));
}

// dispose 中
if (kDebugMode) {
  DebugServer.stop();
}
```

### _handleExecuteAction 中的自动数据回读

```dart
// action 执行后，自动附带最新数据
final providerName = DebugActionRegistry.providerNameFor(actionKey);
Map<String, dynamic>? autoData;

if (providerName == 'app') {
  // app 是非 autoDispose 全局 Provider，可以安全读 State
  autoData = DebugStateRegistry.readState('app', container);
} else {
  // 其他 action：直读数据库（Headless Bypass）
  autoData = await DebugStateRegistry.readData('groups', const {});
}
```

---

## 参考实现

flametree_pick 完整实现（从这里复制 debug_server.dart 基础框架）：
- `flametree_pick/lib/dev_tools/debug_server.dart` — HTTP 核心
- `flametree_pick/lib/dev_tools/debug_state_registry.dart` — State + Data 注册
- `flametree_pick/lib/dev_tools/debug_action_registry.dart` — Action 注册
- `flametree_pick/scripts/seed-test-data.sh` — 测试数据播种
