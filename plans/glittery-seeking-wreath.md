# UI 风格重构计划 - 温暖柔和拟物感

## 目标
将整个应用的 UI 风格统一修改为参考图片中的"温暖、柔和、拟物感"风格。

## 范围
- ✅ **整个应用统一风格**（首页、管理页、设置页）
- ✅ **更新底部导航栏**（磨砂玻璃胶囊形）

## 设计要点总结

### 核心风格
- **柔和、圆润、干净、轻盈**
- 大圆角、柔和渐变、细腻阴影
- 高级质感的拟物设计

### 色彩方案
| 用途 | 颜色 | 色值（预估） |
|------|------|-------------|
| 主色调深橙 | 渐变顶部 | `#F97316` |
| 主色调浅橙 | 渐变底部 | `#FB923C` |
| 奶油米色 | 右侧内容区 | `#FEF7ED` / `#FFF8F0` |
| 纯白色 | 卡片背景 | `#FFFFFF` |
| 深暖灰 | 浅色背景文字 | `#5C4033` / `#78350F` |
| 白色 | 深色背景文字 | `#FFFFFF` |

### 关键设计元素
1. **全局橙色渐变背景** - 从顶部深橙到底部浅橙
2. **左侧菜单"舌头"形状** - 选中项向右延伸，与右侧奶油色区域无缝连接
3. **超大圆角** - 所有元素使用 24px+ 圆角
4. **磨砂玻璃底部导航** - BackdropFilter + 半透明背景

---

## 实施步骤

### 步骤 1: 更新 ThemeConfig 色彩系统
**文件**: `lib/presentation/constants/theme_config.dart`

**新增/修改颜色**:
```dart
// 温暖风格主色调
static const warmOrangeStart = Color(0xFFF97316);  // 渐变起点（深橙）
static const warmOrangeEnd = Color(0xFFFB923C);    // 渐变终点（浅橙）
static const warmOrangeGradient = [warmOrangeStart, warmOrangeEnd];

// 奶油米色背景
static const creamyBeige = Color(0xFFFEF7ED);      // 右侧内容区背景

// 暖棕色文字（用于浅色背景）
static const warmBrown = Color(0xFF78350F);        // 深暖灰/棕色文字
static const warmBrownLight = Color(0xFF92400E);   // 较浅的暖棕色

// 超大圆角
static const double radiusSuperLg = 32.0;          // 超大圆角
static const double radiusXxl = 40.0;              // 特大圆角（用于舌头形状）
```

**新增阴影效果**:
```dart
// 柔和暖色阴影（用于卡片）
static List<BoxShadow> get shadowWarmSoft => [
  BoxShadow(
    color: warmOrangeStart.withOpacity(0.08),
    blurRadius: 24.0,
    spreadRadius: 0,
    offset: const Offset(0, 8),
  ),
  BoxShadow(
    color: const Color(0xFF000000).withOpacity(0.04),
    blurRadius: 12.0,
    offset: const Offset(0, 4),
  ),
];
```

---

### 步骤 2: 重构 MasterDetailLayout
**文件**: `lib/presentation/features/management/widgets/master_detail_layout.dart`

**修改内容**:
1. 移除中间分隔线
2. 左侧区域使用橙色渐变背景
3. 右侧区域使用奶油米色背景 + 左上角大圆角
4. 添加 ClipRRect 处理右侧区域的圆角

**布局结构**:
```
Row
├── Expanded(flex: 32): 左侧（橙色渐变背景）
│   └── Container(gradient: warmOrangeGradient)
│       └── GroupList
└── Expanded(flex: 68): 右侧（奶油色背景，左上角大圆角）
    └── Container(
          decoration: BoxDecoration(
            color: creamyBeige,
            borderRadius: BorderRadius.only(topLeft: Radius.circular(40))
          )
        )
        └── Column(OptionHeader + OptionList)
```

---

### 步骤 3: 重构 GroupList 左侧菜单
**文件**: `lib/presentation/features/management/widgets/master/group_list.dart`

**核心变化 - "舌头"形状选中态**:

1. **未选中菜单项**:
   - 胶囊形按钮
   - 背景色为较深橙色（半透明或实色）
   - 文字白色

2. **选中菜单项 - "舌头"形状**:
   - 左侧圆角 + 右侧延伸（方角，与右侧区域连接）
   - 背景色：奶油米色
   - 文字颜色：深暖棕色
   - 添加微妙的内阴影

**实现方案**:
```dart
// 选中态容器
Container(
  decoration: BoxDecoration(
    color: ThemeConfig.creamyBeige,
    borderRadius: BorderRadius.only(
      topLeft: Radius.circular(24),
      bottomLeft: Radius.circular(24),
      // 右侧无圆角，与右侧区域连接
    ),
    boxShadow: [
      // 内阴影效果
      BoxShadow(
        color: Colors.black.withOpacity(0.05),
        blurRadius: 4,
        offset: Offset(2, 0),  // 从左侧投射
      ),
    ],
  ),
)
```

**布局调整**:
- 选中项需要 **右侧无 padding**，让其延伸到边界
- 未选中项保持正常 padding

---

### 步骤 4: 重构 ManagementPage 页面布局
**文件**: `lib/presentation/features/management/pages/management_page.dart`

**修改内容**:
1. 整体 Scaffold 背景改为橙色渐变
2. 顶部标题栏（AppBar）背景透明
3. 标题文字改为白色、大号、加粗

```dart
Scaffold(
  body: Container(
    decoration: BoxDecoration(
      gradient: LinearGradient(
        colors: ThemeConfig.warmOrangeGradient,
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
      ),
    ),
    child: SafeArea(
      child: Column(
        children: [
          // 白色标题
          Padding(
            padding: EdgeInsets.all(ThemeConfig.spacingLg),
            child: Text(
              '选项管理',
              style: TextStyle(
                color: Colors.white,
                fontSize: ThemeConfig.fontSizeH1,
                fontWeight: FontWeight.bold,
              ),
            ),
          ),
          // Master-Detail 布局
          Expanded(child: MasterDetailLayout(...)),
        ],
      ),
    ),
  ),
)
```

---

### 步骤 5: 更新 AppHeader 组件
**文件**: `lib/presentation/shared/widgets/common/app_header.dart`

**新增变体**:
```dart
/// 温暖风格头部（白色文字，透明背景）
const AppHeader.warm({
  required this.title,
  this.icon,
}) : textColor = Colors.white,
     backgroundColor = Colors.transparent;
```

---

### 步骤 6: 重构底部导航栏
**文件**: `lib/presentation/app/app_router.dart`

**修改内容**:
1. 容器形状：胶囊形（两端半圆）
2. 材质：磨砂玻璃效果（BackdropFilter）
3. 背景色：带淡淡橙色/米色的半透明
4. 图标/文字颜色：
   - 选中：深棕色
   - 未选中：白色或浅棕色

```dart
ClipRRect(
  borderRadius: BorderRadius.circular(30),  // 半圆形胶囊
  child: BackdropFilter(
    filter: ImageFilter.blur(sigmaX: 20, sigmaY: 20),
    child: Container(
      height: 60,
      decoration: BoxDecoration(
        color: ThemeConfig.creamyBeige.withOpacity(0.85),
        borderRadius: BorderRadius.circular(30),
      ),
      child: Row(children: [...tabs]),
    ),
  ),
)
```

**Tab 项样式**:
```dart
// 选中态
Container(
  decoration: BoxDecoration(
    color: ThemeConfig.creamyBeige,
    borderRadius: BorderRadius.circular(20),
  ),
  child: Column(
    children: [
      Icon(icon, color: ThemeConfig.warmBrown),
      Text(label, style: TextStyle(color: ThemeConfig.warmBrown)),
    ],
  ),
)

// 未选中态
Icon(icon, color: Colors.white.withOpacity(0.8))
```

---

### 步骤 7: 更新右侧内容卡片样式
**文件**: `lib/presentation/features/management/widgets/detail/option_list.dart`

**卡片样式**:
```dart
Container(
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(ThemeConfig.radiusSuperLg),
    boxShadow: ThemeConfig.shadowWarmSoft,
  ),
  child: Text(
    'option1',
    style: TextStyle(color: ThemeConfig.warmBrown),
  ),
)
```

---

### 步骤 8: 更新 OptionHeader
**文件**: `lib/presentation/features/management/widgets/detail/option_header.dart`

- 背景透明
- 标题文字颜色：深暖棕色

---

## 文件修改清单

### 核心主题文件
| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `theme_config.dart` | 新增颜色/阴影 | 核心设计变量 |
| `app_router.dart` | 重构底部栏 | 磨砂玻璃胶囊形 |
| `app_header.dart` | 新增变体 | 温暖风格头部 |

### Management 页面
| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `master_detail_layout.dart` | 重构布局 | 移除分隔线，添加渐变和圆角 |
| `group_list.dart` | 重构样式 | "舌头"形状选中态 |
| `management_page.dart` | 重构页面 | 橙色渐变背景 |
| `option_list.dart` | 更新样式 | 白色卡片+暖色阴影 |
| `option_header.dart` | 更新样式 | 暖棕色文字 |

### 首页 (RandomSelection)
| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `random_selection_page.dart` | 重构页面 | 橙色渐变背景 + 白色标题 |

### 设置页
| 文件 | 修改类型 | 说明 |
|------|---------|------|
| `settings_page.dart` | 重构页面 | 橙色渐变背景 + 白色标题 |
| 设置项组件 | 更新样式 | 奶油色卡片 + 暖棕色文字 |

---

## 实施顺序

### 阶段 1：核心基础设施
1. `theme_config.dart` - 定义所有新颜色和样式变量

### 阶段 2：全局组件
2. `app_router.dart` - 底部导航栏重构（磨砂玻璃胶囊形）
3. `app_header.dart` - 新增温暖风格头部变体

### 阶段 3：Management 页面
4. `management_page.dart` - 添加渐变背景和白色标题
5. `master_detail_layout.dart` - 构建新布局框架（渐变左侧 + 奶油色右侧）
6. `group_list.dart` - 实现"舌头"形状选中态
7. `option_list.dart` + `option_header.dart` - 右侧内容样式

### 阶段 4：其他页面
8. `random_selection_page.dart` - 首页样式更新
9. `settings_page.dart` + 相关组件 - 设置页样式更新

### 阶段 5：验证
10. 运行 `flutter analyze` 确保无错误
11. 运行应用验证视觉效果

---

## 注意事项

1. **保持代码整洁**: 所有新颜色和样式必须在 `ThemeConfig` 中定义
2. **响应式适配**: 使用 `AdaptiveSize` API 确保跨平台一致性
3. **动画过渡**: 保持现有的 `AnimatedContainer` 过渡效果
4. **测试验证**: 修改后运行 `flutter analyze` 和 `flutter test`
