# Quick Ask 浮窗功能实现计划

> **目标**: 实现类似 Raycast/Spotlight 的极简快速问答体验
> **设计框架**: 建议 A (Top-Input + Snap Resize + Fade In + TTL)
> **代码细节**: 补充建议 B

---

## 核心交互设计

### 窗口状态机
```
Collapsed (60px) ──[发送消息]──→ Expanding ──[动画完成]──→ Expanded (500px)
      ↑                                                        │
      └──────────[ESC + 5分钟超时]─────────────────────────────┘
```

### ESC 分层行为
1. **生成中** → 停止生成
2. **有输入文字** → 清空输入
3. **无输入** → 隐藏窗口

### 短期记忆 TTL
- 窗口隐藏后 5 分钟内重新唤起：保留对话上下文
- 超过 5 分钟：重置为空白输入框状态

### 数据同步策略
- **自动同步**: Quick Ask 的每次对话自动保存到主应用的会话列表中
- 每次发送消息时创建/更新会话（通过 StorageService）
- 会话标题自动生成（首条用户消息前 20 字符）

---

## 文件结构

### 新建文件 (7 个)
```
app/lib/features/quick_ask/
├── view_models/
│   ├── quick_ask_state.dart           # Freezed 状态定义
│   └── quick_ask_view_model.dart      # 状态管理 + 流式处理
├── widgets/
│   ├── quick_ask_content.dart         # 内容容器（状态切换）
│   ├── quick_ask_input.dart           # 简化版输入框
│   ├── quick_ask_message_list.dart    # 简化版消息列表
│   └── quick_ask_message_bubble.dart  # 简化版消息气泡
└── config/
    └── quick_ask_config.dart          # 常量配置
```

### 修改文件 (3 个)
```
app/lib/main.dart                                # 子窗口添加 ProviderScope
app/lib/core/services/overlay_window_service.dart # 传递 token 和默认配置
app/lib/features/quick_ask/pages/quick_ask_page.dart # 完全重写
```

---

## 分阶段实现

### Phase 1: 窗口状态机 + 基础 UI

**目标**: 窗口可正确展开/收起，ESC 分层行为正常

**步骤**:
1. 创建 `quick_ask_config.dart` - 常量配置
   ```dart
   collapsedHeight = 70.0  // 输入框高度
   expandedHeight = 500.0  // 展开后高度
   windowWidth = 600.0
   contextTTL = Duration(minutes: 5)
   ```

2. 创建 `quick_ask_state.dart` - Freezed 状态
   ```dart
   @freezed
   sealed class QuickAskState {
     windowState: collapsed | expanding | expanded
     messages: List<Message>
     inputText: String
     isGenerating: bool
     generatingMessageId: String?
     generatingContent: String
     lastActivityTime: DateTime?
     errorMessage: String?
   }
   ```

3. 创建 `quick_ask_view_model.dart` - 基础版本
   - 窗口状态转换逻辑
   - ESC 行为分层
   - TTL 检测

4. 重写 `quick_ask_page.dart`
   - 添加独立 ProviderScope
   - ESC 键事件监听
   - 调用 WindowController 调整窗口大小

5. 创建 `quick_ask_content.dart`
   - 根据 windowState 切换布局
   - collapsed: 只显示输入框
   - expanded: 输入框 + 消息列表

6. 创建 `quick_ask_input.dart`
   - 基于 ChatInput 简化（移除听写、工具栏）
   - 单行设计，Enter 发送

**验收**: 热键唤起 → 输入 → 窗口展开 → ESC 隐藏

---

### Phase 2: 消息发送 + 流式响应

**目标**: 完整的问答流程，打字机动画正常

**步骤**:
1. 修改 `overlay_window_service.dart`
   - 在 args 中添加 token、defaultModel、apiBaseUrl
   ```dart
   final args = jsonEncode({
     'windowType': 'overlay',
     'token': authToken,           // 新增
     'defaultModel': defaultModel, // 新增
     'apiBaseUrl': apiBaseUrl,     // 新增
     ...
   });
   ```

2. 修改 `main.dart` 子窗口入口
   - 添加 ProviderScope
   - 初始化必要的服务 Provider（包括 StorageService 用于数据同步）
   - StorageService 需要在子窗口中独立初始化（同一个 SQLite 文件）

3. 扩展 `quick_ask_view_model.dart`
   - 初始化 ApiService（使用 windowArgs 中的 token）
   - sendMessage() 方法
   - 流式事件处理（复用 StreamEvent 体系）
   - 打字机效果（提取 ChatUIViewModel 逻辑）

4. 创建 `quick_ask_message_list.dart`
   - 基于 MessageList 简化
   - 自动滚动到底部

5. 创建 `quick_ask_message_bubble.dart`
   - 基于 MessageBubble 简化（移除操作按钮）
   - 保留打字机动画 + Markdown 渲染

**验收**: 发送消息 → AI 流式回复 → 打字机效果 → 停止生成

---

### Phase 3: 动画优化 + 边界处理

**目标**: 丝滑体验，健壮性

**步骤**:
1. 窗口动画优化
   - macOS: `setFrame(rect, animate: true)`
   - 内容区域: 50ms 延迟后 FadeIn

2. TTL 机制完善
   - 窗口显示时检测是否超时
   - 超时则重置状态

3. 错误处理
   - 网络错误: 在输入框下方显示错误提示
   - 服务不可用: 友好提示

4. 主题适配
   - 复用 AppTheme.light
   - 支持深色模式（可选）

**验收**: 动画流畅 → 超时重置正常 → 错误提示友好

---

## 关键代码路径

### 子窗口 Provider 初始化
```dart
// main.dart _runSubWindow()
Future<void> _runSubWindow(List<String> args) async {
  // ... 解析 windowArgs

  runApp(
    ProviderScope(
      overrides: [
        // 子窗口需要的最小服务集
        apiServiceProvider.overrideWith((ref) => ApiService(
          baseUrl: windowArgs['apiBaseUrl'],
          tokenProvider: () => windowArgs['token'],
        )),
      ],
      child: QuickAskPage(windowArgs: windowArgs),
    ),
  );
}
```

### 窗口大小调整
```dart
// quick_ask_view_model.dart
Future<void> _expandWindow() async {
  final controller = await WindowController.fromCurrentEngine();
  final currentFrame = await controller.getFrame();

  final newFrame = Rect.fromLTWH(
    currentFrame.left,
    currentFrame.top,
    currentFrame.width,
    QuickAskConfig.expandedHeight,
  );

  await controller.setFrame(newFrame, animate: true);

  // 50ms 后触发内容淡入
  await Future.delayed(const Duration(milliseconds: 50));
  state = state.copyWith(windowState: QuickAskWindowState.expanded);
}
```

### 流式处理
```dart
// 复用现有的 StreamEvent 体系
void _handleStreamEvent(StreamEvent event) {
  switch (event) {
    case StreamStartEvent(:final aiMessageId):
      state = state.copyWith(isGenerating: true, generatingMessageId: aiMessageId);
    case StreamChunkEvent(:final chunk):
      _addToCharQueue(chunk); // 打字机效果
    case StreamCompleteEvent():
      state = state.copyWith(isGenerating: false);
    case StreamErrorEvent(:final error):
      state = state.copyWith(errorMessage: error);
  }
}
```

---

## 依赖复用清单

| 组件 | 源文件 | 复用程度 |
|------|--------|----------|
| Message 模型 | `core/models/message.dart` | 100% |
| StreamEvent | `chat/view_models/stream_event.dart` | 100% |
| MarkdownMessage | `shared/widgets/markdown_message.dart` | 100% |
| AppColors/AppSpacing | `shared/theme/*` | 100% |
| ChatInput 逻辑 | `chat/widgets/chat_input.dart` | 提取 40% |
| MessageBubble 逻辑 | `chat/widgets/message_bubble.dart` | 提取 60% |
| 打字机逻辑 | `chat/view_models/chat_ui_view_model.dart` | 提取核心 |

---

## 预计工作量

| 阶段 | 内容 | 时间 |
|------|------|------|
| Phase 1 | 窗口状态机 + 基础 UI | 2-3 小时 |
| Phase 2 | 消息发送 + 流式响应 | 3-4 小时 |
| Phase 3 | 动画优化 + 边界处理 | 1-2 小时 |
| **总计** | | **6-9 小时** |

---

## 风险点

1. **子窗口 window_manager 限制**
   - 子窗口不能使用 window_manager 插件
   - 需要通过 WindowController.setFrame() 调整大小
   - 如果 setFrame 不支持动画，需要使用 Flutter 内部动画替代

2. **打字机效果移植**
   - ChatUIViewModel 的打字机逻辑需要提取为可复用模块
   - 或在 QuickAskViewModel 中实现简化版

3. **Token 传递安全性**
   - Token 通过 windowArgs 明文传递
   - 仅限本地进程间通信，风险可接受

4. **SQLite 并发访问（数据同步）**
   - 主窗口和子窗口可能同时访问同一个 SQLite 文件
   - SQLite 支持多读者单写者模式，需要确保 WAL 模式启用
   - 子窗口写入后，主窗口需要刷新才能看到新会话
