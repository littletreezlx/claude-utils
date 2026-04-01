# Debug State Server — 设计决策参考

## 架构总览

```
Claude Code ──curl──> shelf HTTP Server (localhost:8788, debug only)
                          │
                          ├─ GET  /providers          发现接口
                          ├─ GET  /state/{name}       ViewModel 内存状态
                          ├─ GET  /data/{name}        Repository 直读数据库
                          └─ POST /action/{n}/{m}     执行 ViewModel 方法
                                                        └─ 自动返回最新数据
```

## 两层读取

| 层 | 端点 | 数据来源 | 适用场景 |
|----|------|---------|---------|
| State | `/state/{name}` | Riverpod ViewModel | 验证 UI 状态（页面需打开） |
| Data | `/data/{name}` | Repository → Database | 验证数据持久化（永远可靠） |

autoDispose 的 Provider 在没有 UI 监听时不订阅数据流，State 为空。Data 层绕过这个限制。

## 为什么每个选择

| 决策 | 选择 | 原因 |
|------|------|------|
| HTTP 库 | shelf + shelf_router | Dart 官方维护，路由简洁，成熟 |
| 放 dependencies | 是 | dev_dependencies 无法在 lib/ 导入；kDebugMode + tree shaking = 零生产影响 |
| 反射 | 手动 Registry (Map) | Flutter 禁用 dart:mirrors（AOT） |
| State 序列化 | 手动 toMap | State 类嵌套 Set/Map 等复杂类型，Freezed 加 fromJson 需要自定义 converter，成本高 |
| Container 获取 | ProviderScope.containerOf(context) | 在 postFrameCallback 中调用，此时 ProviderScope 已挂载。不需要改 flutter_common |
| Action 响应 | 自动附带最新数据 | 一次 curl 完成操作+验证，省一个 tool call |
| HTTP vs WebSocket | HTTP | curl 天然支持；无状态模型匹配 LLM ReAct 循环；WebSocket 需维护连接 |

## Registry 编写规则

### StateReader

```dart
// State 有 toJson() → 直接用
'user': (c) => c.read(userProvider).toJson(),

// State 无 toJson()（常见）→ 手动 Map，entity 用 .toJson()
'management': (c) {
  final s = c.read(managementProvider);
  return {
    'groups': s.groups.map((g) => g.toJson()).toList(),
    'selectedId': s.selectedId,
    'isLoading': s.isLoading,
  };
},
```

### DataReader

```dart
// 支持 query params 过滤
'options': (params) async {
  final repo = DI.get<OptionRepository>();
  final groupId = params['groupId'];
  if (groupId != null) {
    // 过滤查询
    return repo.getOptions(int.parse(groupId));
  }
  // 全量查询
  return repo.getAllOptions();
},
```

### ActionHandler

```dart
// 优先用 @visibleForTesting 方法（绕过 UI 流程）
'management/createGroup': (c, p) async {
  final id = await c.read(viewModelProvider.notifier)
      .createGroupForTesting(p['name']);
  return {'createdGroupId': id};
},

// 没有测试方法时用公开 API
'management/selectGroup': (c, p) async {
  await c.read(viewModelProvider.notifier).selectGroup(p['id']);
  return {'selectedGroupId': p['id']};
},
```

### Action 注册优先级

1. **CRUD 操作** — 最常验证（创建/删除/更新核心实体）
2. **核心业务** — 项目灵魂功能（如随机选择）
3. **状态切换** — 选中、排序、筛选
4. **设置变更** — 语言、主题、开关

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

### 等待 Server Ready（AI 使用）

```bash
for i in $(seq 1 30); do
  curl -s -o /dev/null -w "%{http_code}" http://localhost:8788/providers 2>/dev/null \
    && echo "Ready" && break
done
```

## 参考实现

flametree_pick 完整实现：
- `flametree_pick/lib/dev_tools/debug_server.dart` — HTTP 核心（可直接复制）
- `flametree_pick/lib/dev_tools/debug_state_registry.dart` — State + Data 注册
- `flametree_pick/lib/dev_tools/debug_action_registry.dart` — Action 注册
- `flametree_pick/scripts/seed-test-data.sh` — 测试数据播种
- `flametree_pick/docs/superpowers/specs/2026-03-31-debug-state-server-design.md` — 设计文档
