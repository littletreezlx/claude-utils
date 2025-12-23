# FlameTree Pick 随机选择页面视觉升级计划

## 目标
将随机选择页面从"枯燥的表格"升级为"充满暖意的命运扭蛋机"，包括治愈系材质、微动效增强。

## 关键文件

| 文件 | 改动内容 |
|------|---------|
| `lib/presentation/constants/theme_config.dart` | 新增材质方程（背景色、双层阴影） |
| `lib/presentation/features/random_selection/widgets/random_list.dart` | 呼吸动画 + 结果态视觉 |
| `lib/presentation/features/random_selection/pages/random_selection_page.dart` | 背景色更新 |
| `lib/presentation/features/random_selection/view_models/random_view_model.dart` | HapticFeedback 触觉反馈 |

---

## 阶段 1: 材质方程升级

### 1.1 theme_config.dart 新增配置
```dart
// 羊皮纸暖白背景
static const backgroundParchment = Color(0xFFF9F7F2);

// 双层阴影（环境光 + 主阴影）
static List<BoxShadow> get shadowCard => [
  BoxShadow(color: Color(0x08000000), blurRadius: 40, offset: Offset(0, 2)),
  BoxShadow(color: Color(0x14000000), blurRadius: 16, offset: Offset(0, 8)),
];

// 选中卡片浮起阴影
static List<BoxShadow> get shadowCardElevated => [
  BoxShadow(color: primary.withOpacity(0.25), blurRadius: 32, spreadRadius: 4, offset: Offset(0, 12)),
  BoxShadow(color: Color(0x1F000000), blurRadius: 24, offset: Offset(0, 16)),
];
```

### 1.2 random_selection_page.dart 背景色
- Scaffold 背景色改为 `ThemeConfig.backgroundParchment`

### 1.3 random_list.dart 卡片样式
- 圆角升级为 `radiusXl` (24px)
- 阴影使用 `ThemeConfig.shadowCard`
- **保持现有 GridView 布局和固定宽高比**

---

## 阶段 2: 呼吸动画

### 2.1 新增 _BreathingCard 私有组件（random_list.dart）
- 触发条件：`isAnimating && !isFinalSelected`
- 效果：Scale 1.0↔1.03 + Glow 脉冲 (600ms 周期)
- 实现：SingleTickerProviderStateMixin + AnimationController.repeat(reverse: true)

### 2.2 高亮边框增强
- 高亮时边框宽度 3px，颜色 `ThemeConfig.primary`
- 最终选中边框宽度 4px

---

## 阶段 3: 结果展示增强

### 3.1 选中卡片效果
- 浮起：`transform: translate(0, -12)`
- 放大：`scale: 1.08`
- 阴影：`ThemeConfig.shadowCardElevated`

### 3.2 其他卡片效果
- 缩小：`scale: 0.95`
- 淡化：`opacity: 0.4`

---

## 阶段 4: 触觉反馈

### 4.1 random_view_model.dart
- 结果确定时：`HapticFeedback.heavyImpact()`
- 减速阶段每次切换：`HapticFeedback.selectionClick()`
- 条件检查：仅移动端触发（使用 PlatformAdapter）

---

## 验收标准

- [ ] 背景色为羊皮纸暖白 `#F9F7F2`
- [ ] 卡片有双层阴影效果（环境光 + 主阴影）
- [ ] 卡片圆角为 24px
- [ ] 动画期间所有卡片有呼吸脉冲效果
- [ ] 高亮边框快速跳动（由快变慢）
- [ ] 选中卡片浮起放大，其他变暗缩小
- [ ] 结果确定时有重度触觉反馈
- [ ] `flutter analyze` 无错误
- [ ] `flutter test` 全部通过

---

## 风险提示

1. **性能**：呼吸动画可能影响帧率，需用 RepaintBoundary 优化
2. **桌面端兼容**：HapticFeedback 需条件判断，避免桌面端报错
