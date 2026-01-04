# Hero Overlay (英雄卡片) 模式实现计划

## 概述

重构随机选择功能的结果展示方式，从传统弹窗模式改为 **Hero Overlay** 模式，增强仪式感和交互体验。

---

## 需求分析

### 当前痛点
1. 选中结果缺乏仪式感（使用 Dialog 弹窗）
2. 跑马灯动画时未选中卡片透明度太低 (0.6)，看不清
3. 跑动时所有卡片都在呼吸，导致视觉混乱

### 目标效果
1. **卡片样式优化**: 禁用 Opacity，通过 Scale 和阴影区分层级
2. **跑动时禁用呼吸**: 只有最终定格的大卡片在呼吸
3. **Hero Overlay**: 全屏覆盖层 + 中心弹出放大卡片 + 背景模糊
4. **双按钮操作**: "就它了！"（撒花确认）+ "不行，换一个"（排除重选）

---

## 实现方案

### 1. 状态层修改 (random_state.dart)

**新增字段**:
```dart
/// 临时排除的选项 ID 列表（用于"换一个"功能）
@Default(<int>[]) List<int> tempExcludedIds
```

---

### 2. ViewModel 修改 (random_view_model.dart)

**新增方法**:
```dart
/// 排除当前结果并重新选择
Future<void> excludeAndReselect(int excludedOptionId)

/// 清除排除列表
void clearExcludedIds()
```

**修改现有方法**:
- `_playHighlightAnimation()`: 跑动过程中不触发呼吸动画（通过 `isAnimating` 状态控制）

---

### 3. OptionCard 样式优化 (random_list.dart)

**修改 `_calculateOpacity` 方法**:
```dart
// ❌ 删除结果态其他卡片的透明度降低
// ✅ 保持所有卡片 opacity = 1.0
double _calculateOpacity(bool isOtherCard) {
  return widget.isPageVisible ? 1.0 : 0.0;
}
```

**修改 `_BreathingCard` 条件**:
```dart
// ❌ 旧: isBreathing: isFinalSelected && !widget.isAnimating
// ✅ 新: 跑动时完全不呼吸，只有最终定格时呼吸
// 但需要确保只有最终选中的单张卡片呼吸，其他不呼吸
```

---

### 4. 创建 HeroOverlay 组件 (hero_overlay.dart) - 新文件

**位置**: `lib/presentation/features/random_selection/widgets/hero_overlay.dart`

**设计风格**: 简洁干净的英雄卡片，不使用复杂的粒子效果

**核心特性**:
- 全屏黑色半透明背景 (Opacity 0.7)
- `BackdropFilter` 模糊效果 (sigma: 10)
- 中心放大的结果卡片（从 0.0 弹性放大到 1.0）
- 入场动画: `Curves.elasticOut` (500ms)
- 触觉反馈: `HapticFeedback.heavyImpact()` 入场时触发
- 卡片持续呼吸动画 (2秒周期，1.0 ↔ 1.05)
- 双按钮区域

**卡片样式**:
```dart
Container(
  width: 280.aw,
  padding: EdgeInsets.all(ThemeConfig.spacingXl),
  decoration: BoxDecoration(
    color: ThemeConfig.surface,
    borderRadius: BorderRadius.circular(ThemeConfig.radiusXl),
    boxShadow: ThemeConfig.shadowCardElevated,
  ),
  child: Column(
    children: [
      // 选项名称 (大号文字)
      Text(optionName, style: ...),
      SizedBox(height: ThemeConfig.spacingLg),
      // 装饰性分割线
      Divider(),
      SizedBox(height: ThemeConfig.spacingLg),
      // 按钮区域
      _buildButtons(),
    ],
  ),
)
```

**按钮设计**:
| 按钮 | 样式 | 动作 |
|------|------|------|
| "就这个！" | 大尺寸橙色填充按钮 ( Expanded) | 播放撒花特效 → 延迟 300ms → 关闭 Overlay + 隐藏结果 |
| "换一个" | 灰色描边按钮 + 刷新图标 ( Expanded) | 关闭 Overlay + 排除当前选项 + 自动重跑 |

**撒花特效说明**:
- 复用现有的 `ConfettiPainter` 组件（`celebration/confetti_painter.dart`）
- 仅在"就这个！"点击时触发，作为 Overlay 关闭前的过渡效果
- 播放时长约 800ms，然后自动关闭 Overlay

---

### 5. 修改 RandomSelectionPage (random_selection_page.dart)

**架构变更**:
```
旧: Stack + Dialog (showGeneralDialog)
新: Stack + Overlay (内联 HeroOverlay 组件)
```

**实现方式**:
```dart
Stack(
  children: [
    // 底层: 选项网格
    _buildBlurredGrid(state, useCentralSlot),

    // 中层: 中心滚动槽 (n > 15)
    if (useCentralSlot && state.isAnimating)
      CentralSlot(...),

    // 顶层: Hero Overlay (当结果可见时显示)
    if (state.isResultVisible && state.selectedOption != null)
      HeroOverlay(
        optionName: state.selectedOption!.name,
        onConfirm: () => notifier.hideResult(),
        onReselect: () => notifier.excludeAndReselect(state.selectedOption!.id),
      ),

    // 浮层: 底部按钮
    ...
  ],
)
```

---

## 关键文件修改清单

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `random_state.dart` | 修改 | 新增 `tempExcludedIds` 字段 |
| `random_view_model.dart` | 修改 | 新增排除重选逻辑 |
| `random_list.dart` | 修改 | 禁用透明度区分，优化呼吸条件 |
| `hero_overlay.dart` | 新建 | Hero Overlay 组件 |
| `random_selection_page.dart` | 修改 | 用内联 Overlay 替换 Dialog |

---

## 动画物理参数

### 跑马灯（保持现有三阶段）
- **加速**: 200ms → 100ms
- **巡航**: 100ms × 12 帧
- **减速**: 120ms → 500ms (6 帧)

### Hero Overlay 入场
- **缩放曲线**: `Curves.elasticOut`
- **缩放范围**: 0.0 → 1.0
- **时长**: 500ms
- **触觉**: `heavyImpact()` 在动画开始时触发

---

## 注意事项

1. **呼吸动画**: 确保只有最终选中的卡片呼吸，跑动时完全不呼吸
2. **排除逻辑**: 排除的选项需要在下次选择时过滤掉（在 `performRandomSelection` 中处理）
3. **清除机制**: 当用户切换分组或手动点击"开始"按钮时，应清除 `tempExcludedIds`
4. **空选项处理**: 当所有选项都被排除时，显示 Toast 提示并清除排除列表，然后重跑
5. **Dialog 移除**: 删除 `_showResultDialog` 方法和 `RandomResultDialog` 的引用（但保留文件以备后用）
