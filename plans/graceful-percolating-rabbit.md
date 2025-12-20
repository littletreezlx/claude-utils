# MVVM 架构重构计划

## 目标
将项目状态管理层重构为标准 MVVM 架构（基于 Riverpod 3），统一命名规范和目录结构。

## 用户确认的方案
- ✅ 全部转换为 `@riverpod` 注解方式
- ✅ Core 模块 Provider 也移动到 `core/view_models/`
- ✅ State 类与 ViewModel 放在同一个 `view_models/` 目录
- ✅ **扁平目录结构**：`features/xxx/view_models/`（无 presentation 中间层）
- ✅ **规范写入** `/flutter/CLAUDE.md`（Flutter 通用层）

---

## 重构清单

### Phase 1: Chat 功能模块 (高优先级)

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/chat/providers/chat_provider.dart` | `features/chat/view_models/chat_view_model.dart` | `ChatNotifier` → `ChatViewModel` |
| `features/chat/providers/chat_data_provider.dart` | `features/chat/view_models/chat_data_view_model.dart` | `ChatDataNotifier` → `ChatDataViewModel` |
| `features/chat/providers/chat_ui_provider.dart` | `features/chat/view_models/chat_ui_view_model.dart` | `ChatUINotifier` → `ChatUIViewModel` |
| `features/chat/providers/chat_area_provider.dart` | `features/chat/view_models/chat_area_view_model.dart` | `ChatAreaNotifier` → `ChatAreaViewModel` |
| `features/chat/providers/search_mode_provider.dart` | `features/chat/view_models/search_mode_view_model.dart` | `SearchModeNotifier` → `SearchModeViewModel` |
| `features/chat/providers/dictation_provider.dart` | `features/chat/view_models/dictation_view_model.dart` | `DictationNotifier` → `DictationViewModel` |
| `features/chat/providers/compare_chat_provider.dart` | `features/chat/view_models/compare_chat_view_model.dart` | `CompareChatNotifier` → `CompareChatViewModel` |
| `features/chat/providers/file_attachments_provider.dart` | `features/chat/view_models/file_attachments_view_model.dart` | `FileAttachmentsNotifier` → `FileAttachmentsViewModel` |
| `features/chat/providers/image_generation_provider.dart` | `features/chat/view_models/image_generation_view_model.dart` | `ImageGenerationNotifier` → `ImageGenerationViewModel` |
| `features/chat/providers/current_model_support_provider.dart` | `features/chat/view_models/current_model_support_view_model.dart` | 函数型 Provider 保留 |

**State 文件**:
| 原文件 | 新文件 |
|--------|--------|
| `features/chat/providers/chat_state.dart` | `features/chat/view_models/chat_state.dart` |
| `features/chat/providers/chat_data_state.dart` | `features/chat/view_models/chat_data_state.dart` |
| `features/chat/providers/chat_ui_state.dart` | `features/chat/view_models/chat_ui_state.dart` |

### Phase 2: Sessions 功能模块

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/sessions/providers/sessions_provider.dart` | `features/sessions/view_models/sessions_view_model.dart` | `SessionsNotifier` → `SessionsViewModel` |
| `features/sessions/providers/compare_sessions_provider.dart` | `features/sessions/view_models/compare_sessions_view_model.dart` | `CompareSessionsNotifier` → `CompareSessionsViewModel` |
| `features/sessions/providers/sessions_state.dart` | `features/sessions/view_models/sessions_state.dart` | - |

### Phase 3: Settings 功能模块

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/settings/providers/settings_provider.dart` | `features/settings/view_models/settings_view_model.dart` | `SettingsNotifier` → `SettingsViewModel` |
| `features/settings/providers/theme_provider.dart` | `features/settings/view_models/theme_view_model.dart` | `ThemeNotifier` → `ThemeViewModel` |
| `features/settings/providers/preferences_provider.dart` | `features/settings/view_models/preferences_view_model.dart` | `PreferencesNotifier` → `PreferencesViewModel` |
| `features/settings/providers/models_provider.dart` | `features/settings/view_models/models_view_model.dart` | `ModelsNotifier` → `ModelsViewModel` |
| `features/settings/providers/usage_provider.dart` | `features/settings/view_models/usage_view_model.dart` | `UsageNotifier` → `UsageViewModel`, `SelectedTimeRangeNotifier` → `SelectedTimeRangeViewModel` |
| `features/settings/providers/hot_key_provider.dart` | `features/settings/view_models/hot_key_view_model.dart` | `HotKeyNotifier` → `HotKeyViewModel` |

### Phase 4: Doc Organizer 功能模块

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/doc_organizer/providers/organize_provider.dart` | `features/doc_organizer/view_models/organize_view_model.dart` | `OrganizeNotifier` → `OrganizeViewModel` |
| `features/doc_organizer/providers/doc_chat_area_provider.dart` | `features/doc_organizer/view_models/doc_chat_area_view_model.dart` | `DocChatAreaNotifier` → `DocChatAreaViewModel` |
| `features/doc_organizer/providers/doc_chat_provider.dart` | `features/doc_organizer/view_models/doc_chat_view_model.dart` | `DocChatNotifier` → `DocChatViewModel` |
| `features/doc_organizer/providers/doc_content_provider.dart` | `features/doc_organizer/view_models/doc_content_view_model.dart` | `DocContentNotifier` → `DocContentViewModel` |
| `features/doc_organizer/providers/doc_context_provider.dart` | `features/doc_organizer/view_models/doc_context_view_model.dart` | `DocContextNotifier` → `DocContextViewModel` |
| `features/doc_organizer/providers/doc_library_provider.dart` | `features/doc_organizer/view_models/doc_library_view_model.dart` | `DocLibraryNotifier` → `DocLibraryViewModel` |
| `features/doc_organizer/providers/file_tree_provider.dart` | `features/doc_organizer/view_models/file_tree_view_model.dart` | `FileTreeNotifier` → `FileTreeViewModel` |
| `features/doc_organizer/providers/doc_chat_state.dart` | `features/doc_organizer/view_models/doc_chat_state.dart` | - |
| `features/doc_organizer/providers/doc_chat_storage_helper.dart` | `features/doc_organizer/helpers/doc_chat_storage_helper.dart` | 非 ViewModel，移动到 helpers/ |

### Phase 5: Draw 功能模块

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/draw/providers/draw_provider.dart` | `features/draw/view_models/draw_view_model.dart` | `DrawNotifier` → `DrawViewModel` |
| `features/draw/providers/draw_params_provider.dart` | `features/draw/view_models/draw_params_view_model.dart` | `DrawParamsNotifier` → `DrawParamsViewModel` |
| `features/draw/providers/draw_history_provider.dart` | `features/draw/view_models/draw_history_view_model.dart` | `DrawHistoryNotifier` → `DrawHistoryViewModel` |

### Phase 6: 其他功能模块

**Auth**:
| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/auth/providers/auth_provider.dart` | `features/auth/view_models/auth_view_model.dart` | `AuthNotifier` → `AuthViewModel` |
| `features/auth/providers/auth_state.dart` | `features/auth/view_models/auth_state.dart` | - |

**Role Management**:
| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/role_management/providers/role_form_provider.dart` | `features/role_management/view_models/role_form_view_model.dart` | `RoleFormNotifier` → `RoleFormViewModel` |
| `features/role_management/providers/role_sync_provider.dart` | `features/role_management/view_models/role_sync_view_model.dart` | `RoleSyncNotifier` → `RoleSyncViewModel` |

**Image Gallery**:
| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `features/image_gallery/providers/image_gallery_provider.dart` | `features/image_gallery/view_models/image_gallery_view_model.dart` | `ImageGalleryNotifier` → `ImageGalleryViewModel` |

### Phase 7: Core 模块

| 原文件 | 新文件 | 类名变更 |
|--------|--------|----------|
| `core/providers/unified_role_notifier.dart` | `core/view_models/unified_role_view_model.dart` | `UnifiedRoleNotifier` → `UnifiedRoleViewModel` |
| `core/providers/unified_role_provider.dart` | 合并到上面 | - |
| `core/providers/global_role_state_provider.dart` | `core/view_models/global_role_state_view_model.dart` | `GlobalRoleStateNotifier` → `GlobalRoleStateViewModel` |
| `core/providers/category_ui_state_provider.dart` | `core/view_models/category_ui_state_view_model.dart` | `CategoryExpandedNotifier` → `CategoryExpandedViewModel` |
| `core/providers/role_actions_provider.dart` | `core/view_models/role_actions_view_model.dart` | `RoleActionsNotifier` → `RoleActionsViewModel` |
| `core/providers/category_actions_provider.dart` | `core/view_models/category_actions_view_model.dart` | `CategoryActionsNotifier` → `CategoryActionsViewModel` |
| `core/providers/overlay_providers.dart` | `core/view_models/overlay_view_model.dart` | 函数型 Provider 保留 |
| `core/providers/role_derived_providers.dart` | `core/view_models/role_derived_view_model.dart` | 派生 Provider 保留 |
| `core/providers/service_providers.dart` | `core/providers/service_providers.dart` | **保留原位**（服务注入，非 ViewModel） |
| `core/localization/locale_provider.dart` | `core/localization/locale_provider.dart` | **保留原位**（非 ViewModel） |

---

## 执行步骤

### Step 1: 准备工作
1. 确保 `git status` 干净
2. 运行测试确保起点正常：`flutter test --reporter=silent`
3. 创建目录结构

### Step 2: 逐模块重构（每个模块）
1. **创建新目录**: `presentation/view_models/`
2. **移动并重命名文件**
3. **转换为 @riverpod 注解**（手写 → 代码生成）
4. **更新类名**: `XxxNotifier` → `XxxViewModel`
5. **更新 Provider 变量名**: `xxxProvider` → `xxxViewModelProvider`
6. **修复导入引用**
7. **运行 build_runner**: `flutter packages pub run build_runner build --delete-conflicting-outputs`
8. **运行测试验证**

### Step 3: 更新引用
1. 全局搜索替换所有 `import 'xxx_provider.dart'` → `import 'xxx_view_model.dart'`
2. 全局搜索替换 `xxxProvider` → `xxxViewModelProvider`
3. 全局搜索替换 `XxxNotifier` → `XxxViewModel`
4. 更新 `ref.watch()` 和 `ref.read()` 调用

### Step 4: 清理
1. 删除旧的空 `providers/` 目录
2. 删除旧的 `.g.dart` 文件
3. 运行完整测试套件

### Step 5: 文档更新
1. 更新 `app/CLAUDE.md` 中的目录结构
2. 更新 `FEATURE_CODE_MAP.md`
3. 在项目根目录 `CLAUDE.md` 添加 MVVM 规范

---

## 代码转换模板

### 手写 Notifier → @riverpod ViewModel

**Before (手写方式)**:
```dart
// chat_provider.dart
import 'package:flutter_riverpod/flutter_riverpod.dart';

class ChatNotifier extends Notifier<ChatState> {
  @override
  ChatState build() {
    return ChatState();
  }

  Future<void> sendMessage(String content) async { ... }
}

final chatProvider = NotifierProvider<ChatNotifier, ChatState>(() {
  return ChatNotifier();
});
```

**After (@riverpod 方式)**:
```dart
// chat_view_model.dart
import 'package:riverpod_annotation/riverpod_annotation.dart';

part 'chat_view_model.g.dart';

@riverpod
class ChatViewModel extends _$ChatViewModel {
  @override
  ChatState build() {
    return ChatState();
  }

  Future<void> sendMessage(String content) async { ... }
}

// 生成的 Provider: chatViewModelProvider
```

### AsyncNotifier → @riverpod AsyncViewModel

**Before**:
```dart
final unifiedRoleProvider = AsyncNotifierProvider<UnifiedRoleNotifier, RolesResponse>(
  UnifiedRoleNotifier.new,
);

class UnifiedRoleNotifier extends AsyncNotifier<RolesResponse> {
  @override
  Future<RolesResponse> build() async {
    return _fetchRoles();
  }
}
```

**After**:
```dart
part 'unified_role_view_model.g.dart';

@riverpod
class UnifiedRoleViewModel extends _$UnifiedRoleViewModel {
  @override
  Future<RolesResponse> build() async {
    return _fetchRoles();
  }
}

// 生成的 Provider: unifiedRoleViewModelProvider
```

---

## 新目录结构（扁平化）

```
app/lib/
├── core/
│   ├── view_models/             # ✨ ViewModel（原 providers/ 中的 Notifier）
│   │   ├── unified_role_view_model.dart
│   │   ├── global_role_state_view_model.dart
│   │   └── ...
│   ├── providers/               # 保留：服务注入（非 ViewModel）
│   │   └── service_providers.dart
│   └── ...
│
├── features/
│   ├── chat/
│   │   ├── view_models/         # ✨ ViewModel + State
│   │   │   ├── chat_view_model.dart
│   │   │   ├── chat_state.dart
│   │   │   └── ...
│   │   ├── pages/               # UI 页面
│   │   ├── widgets/             # UI 组件
│   │   └── ...
│   └── ...
```

**设计理念**：
- **扁平结构** — 无 `presentation/` 中间层，避免过度设计
- **务实优先** — 个人项目不需要 Clean Architecture 的完整分层
- **最小改动** — `providers/` → `view_models/`，层级不变

---

## CLAUDE.md 规范内容

将以下内容添加到 `/flutter/CLAUDE.md`（Flutter 通用层）:

```markdown
## 🏗️ 架构模式：MVVM + Riverpod 3

### 核心理念
- **ViewModel = Riverpod Notifier** — 在 Flutter 中，ViewModel 通过 Riverpod 的 Notifier 实现
- **扁平目录结构** — 避免过度分层（无 presentation/domain/data 中间层）
- **务实 > 完美** — 个人项目不需要企业级架构

### 命名规范
| 类型 | 命名规则 | 示例 |
|------|----------|------|
| ViewModel 文件 | `xxx_view_model.dart` | `chat_view_model.dart` |
| ViewModel 类 | `XxxViewModel` | `ChatViewModel` |
| State 类 | `XxxState` | `ChatState` |
| Provider 变量 | `xxxViewModelProvider`（自动生成） | `chatViewModelProvider` |

### 目录结构
```
features/{module}/
├── view_models/       # ViewModel + State（核心）
├── pages/             # UI 页面
├── widgets/           # UI 组件
├── models/            # 领域模型（可选）
└── helpers/           # 工具函数（可选）
```

### Riverpod 3 规范
```dart
// ✅ 正确：使用 @riverpod 注解
@riverpod
class ChatViewModel extends _$ChatViewModel {
  @override
  ChatState build() => const ChatState();
}

// ❌ 错误：手写 NotifierProvider
final chatProvider = NotifierProvider<ChatNotifier, ChatState>(...);
```

**强制要求**：
- 必须使用 `@riverpod` 注解（代码生成）
- 禁止手写 `NotifierProvider`、`StateNotifierProvider`
- ViewModel 继承 `_$XxxViewModel`（生成的基类）

### 什么不是 ViewModel？
以下应保留在 `providers/` 或其他目录：
- **服务注入** — `service_providers.dart`（DI 容器）
- **简单派生状态** — 纯计算的 Provider（无业务逻辑）
- **全局配置** — `locale_provider.dart` 等基础设施
```

---

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 大量文件移动导致 Git 历史混乱 | 中 | 分批提交，每个模块一个 commit |
| Provider 引用遗漏 | 高 | 全局搜索 + 编译检查 |
| 测试失败 | 高 | 每步运行测试，及时回滚 |
| build_runner 生成失败 | 中 | 检查 part 声明和类名一致性 |

---

## 预估工作量

- **Phase 1-3 (Chat/Sessions/Settings)**: 核心模块，约 25 个文件
- **Phase 4-6 (其他 Features)**: 约 15 个文件
- **Phase 7 (Core)**: 约 10 个文件
- **引用更新**: 全局搜索替换
- **测试验证**: 每阶段运行测试

**总计约 50+ 个文件变更**
