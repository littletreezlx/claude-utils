# 多文档上下文 & 批量整理功能实现计划

## 功能概述

实现三个核心功能：
1. **多文档上下文**: AI 对话支持同时添加多个文档作为上下文
2. **右键菜单**: 文件树支持右键点击"添加到 AI 上下文"
3. **批量整理**: 选中多个文档后，AI 并行整理并统一预览确认

## 实现步骤

### Phase 1: 多文档上下文基础

#### Task 1.1: 数据模型修改
- 创建 `DocContextItem` 模型（单文档上下文项）
- 修改 `DocContextState` 从单文档改为多文档列表
- 更新 `DocContextNotifier` 方法：
  - `addDocument(path, content, name, type)` - 添加文档
  - `removeDocument(path)` - 移除文档
  - `clearAll()` - 清除所有
  - 更新 `contextPrefix` getter 支持多文档格式

#### Task 1.2: FileTree 多选支持
- 修改 `FileTreeState` 添加 `selectedPaths: Set<String>`
- 修改 `FileTreeNotifier` 添加多选方法：
  - `toggleSelection(path)` - 切换选择
  - `clearSelections()` - 清除选择
- 修改 `FileTreeNodeWidget` 支持 Ctrl/Cmd 多选

### Phase 2: 右键菜单 & 上下文集成

#### Task 2.1: 右键菜单实现
- `FileTreeNodeWidget` 添加 `GestureDetector.onSecondaryTapUp`
- 实现 `showMenu` 显示右键菜单
- 菜单项: "添加到 AI 上下文"
- 多选时批量添加

#### Task 2.2: 上下文指示器更新
- 修改 `_DocContextIndicator` 显示多文档列表
- 显示文档数量和文件名
- 每个文档可单独移除
- "清除所有"按钮

### Phase 3: 批量整理数据层

#### Task 3.1: 批量整理状态模型
- 创建 `SingleDocOrganizeResult` 模型（单文档整理结果）
- 创建 `BatchOrganizeState` 模型
- 创建 `BatchOrganizeStep` 枚举

#### Task 3.2: 批量整理 Provider
- 创建 `BatchOrganizeProvider`
- 实现 `startBatchOrganize(paths, conversationContent)`
- 使用 `Future.wait` 并行处理
- 实现 `confirmSaveAll()` 批量保存

### Phase 4: 批量整理 UI

#### Task 4.1: 批量 Diff 预览弹窗
- 创建 `BatchDiffPreviewDialog`
- 可折叠的文档列表
- 每个文档显示 Diff 统计和预览
- 复选框控制是否保存

#### Task 4.2: 批量整理入口
- 修改 `OrganizeButton` 检测多选状态
- 多选时显示"批量整理 (N 个文档)"

### Phase 5: 测试

#### Task 5.1: 单元测试
- `DocContextProvider` 多文档测试
- `BatchOrganizeProvider` 测试

#### Task 5.2: E2E 测试
- 多选文件测试
- 右键菜单测试
- 批量整理流程测试

## 关键文件变更

### 新增文件
```
app/lib/features/doc_organizer/
├── models/
│   ├── doc_context_item.dart
│   ├── batch_organize_state.dart
│   └── single_doc_organize_result.dart
├── providers/
│   └── batch_organize_provider.dart
└── widgets/
    └── batch_diff_preview/
        ├── batch_diff_preview_dialog.dart
        └── batch_doc_item.dart
```

### 修改文件
```
app/lib/features/doc_organizer/
├── providers/
│   ├── doc_context_provider.dart
│   └── file_tree_provider.dart
├── widgets/
│   ├── file_tree/file_tree_node.dart
│   ├── doc_chat/doc_chat_area.dart
│   └── organize_button.dart
└── pages/doc_organizer_page.dart
```

## 技术决策

1. **并行处理**: 使用 `Future.wait` 同时处理多个文档，提高效率
2. **Token 限制**: 限制最大文档数量（10个），防止超出上下文限制
3. **右键菜单**: 使用 Flutter 原生 `showMenu`，符合桌面操作习惯

## 风险注意

- Token 消耗可能较大，需添加确认提示
- AI API 速率限制，需错误处理和重试
- 多 Provider 状态同步需仔细处理
