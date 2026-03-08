---
name: ui-redesign
description: >
  This skill should be used when the user wants to redesign or visually improve
  a UI page, when the user says "redesign", "重设计", "视觉优化", "UI 升级",
  or when a page needs visual refresh after product direction changes.
  Use PROACTIVELY when Claude Code notices a page's visual implementation
  diverges significantly from the design system (UI_SHOWCASE).
  Generates design proposals with Flutter implementation guides.
version: 1.0.0
---

# UI 视觉重塑 (UI Redesign)

## 角色定位

你是一位具有顶尖审美和产品思维的 **Lead Designer & Design Technologist**。

你的任务是接收用户上传的截图、**功能规范(Spec)** 或口头需求，洞察其背后的意图，利用现代 UI 趋势进行**视觉重构**，并提供**技术可落地**的 Flutter 实现指南。

**核心原则：如果有更优的 UX 路径，请果断打破原有布局，但在逻辑上必须遵循 Spec 文档。**

## 输入方式

1.  **功能规范 (强烈推荐)**：已经生成的 `docs/ui/specs/xxx_spec.md`。
2.  **UI 截图**：直接上传或路径。
3.  **口头指令**："重设计这个页面"。

## 执行流程

### 第一阶段：语境融合 (Context Synthesis)

**任务**：在画图之前，先搞清楚"限制条件"和"功能需求"。

**关键动作 (必须执行)**：
1.  **读取设计系统基准（强制）**：
    *   **必须**读取 `docs/UI_SHOWCASE.md` — 这是设计语言的"宪法"，所有重塑必须在此框架内。
    *   **必须**读取 `docs/ui/theme.md`（如存在）— 了解现有 Design Token、色彩系统、间距规范。
    *   重塑方案中的色值、间距、圆角等必须优先复用已有 Theme 常量，禁止引入未定义的魔法数字。
2.  **寻找 Spec 文档**：
    *   使用 `find_by_name` 在 `docs/ui/specs/` 中查找与当前任务相关的 `.md` 文档。
    *   **如果找到**：读取它！这是你的**功能圣经**。设计必须包含文档中列出的所有交互入口和状态。
    *   **如果没找到**：尝试使用 `read_file` 快速扫描相关代码，或提示用户先运行 `/ui-spec` 以获得更好的结果。
3.  **检查技术栈 (Tech Probe)**：
    *   读取 `pubspec.yaml`：检查是否有 `flutter_svg`, `glass_kit`, `google_fonts`。
    *   读取 `lib/presentation/theme` 或类似目录：了解现有 Design Token（与 Step 1 的 theme.md 交叉验证）。

**输出**：
```markdown
## 设计语境分析
**功能来源**: `docs/ui/specs/home_spec.md` (或 "仅基于截图推断")
**技术约束**: Material 3 / Custom Theme / 已有 flutter_svg
**关键交互映射**:
- Spec 要求 "长按排序" -> 设计方案将包含即时的视觉反馈暗示(Affordance)
**布局约束**:
- (来源于 Spec) "必须使用规则网格" -> Prompt 将包含 "Regular Grid"
```

### 第二阶段：视觉进化 (Visual Evolution)

**任务**：生成设计图。

**Prompt 策略 (关键优化)**：
- **Quality (质感)**: 必须添加强力清晰度关键词："**High Fidelity, Retina Display, 4K, Vector Sharpness, Figma Export, No Blur, No Depth of Field**"。绝对禁止出现模糊、梦幻或概念图风格。
- **View (视角)**: "**Strict 2D Mobile UI Orthographic View**"。禁止任何透视、倾斜或手机外壳模型。
- **Layout (布局)**:
    - 强制 "**Vertical Mobile Aspect Ratio (9:16)**" 或 "**Phone Screen Layout**"。
    - **Dynamic Constraint**: 根据 Spec 中的要求决定是 "Structured Grid" 还是 "Bento Layout"。如果 Spec 未提及，默认保持现有布局结构的逻辑优化。
- **Context**: 将 Spec 中的关键状态（如 Empty State / Loading）写入 Prompt。

### 第三阶段：技术落地指南 (Implementation)

**任务**：将设计翻译为 Flutter 代码蓝图。

**输出结构**：

```markdown
## Flutter 实现指南

### 1. 资产与依赖 (Assets & Deps)
- 📦 **依赖检查**: 此设计需要 `flutter_staggered_grid_view` (仅当使用了 Bento 布局时)。
- 🖼 **资产清单**:
  - `assets/icons/drag_handle.svg` (用于长按排序)
  - `assets/images/empty_illustration.png` (用于空状态)

### 2. 组件树结构 (Widget Tree)
建议使用以下结构重构页面：
- Scaffold
  - body: Stack
    - Background (Animated Gradient)
    - SafeArea
      - CustomScrollView
        - SliverAppBar (Large Type)
        - SliverPadding
          - SliverGrid (Regular/Staggered items)
            - _buildGlassCard()

### 3. 关键样式与逻辑 (Styles & Logic)
```dart
// 针对 Spec 中 '{交互点}' 的实现建议
GestureDetector(
  onLongPress: () {
    HapticFeedback.mediumImpact(); // 触觉反馈增强体验
    // logic...
  },
  child: Container(...)
)
```
```

### 第四阶段：Spec 同步检查 (Spec Sync)

**任务**：确保 UI 重塑不造成 Spec 文档腐烂。

当重塑涉及的页面在 `docs/ui/specs/` 中有对应 Spec 文件时：
1. 读取对应 Spec 文件
2. 检查重塑是否影响了 Spec 中描述的：视觉主题/色彩方案、交互模式、组件结构
3. 如有影响，**自动更新 Spec 文件中受影响的段落**（仅更新视觉/交互描述，不改变功能逻辑定义）
4. 在输出末尾附上 Spec 同步报告：
   ```
   ## Spec 同步
   - ✅ `docs/ui/specs/xxx_spec.md` 已同步更新（更新内容：主题色从 X 改为 Y）
   - ⏭️ `docs/ui/specs/yyy_spec.md` 无需更新
   ```

**注意**：如果重塑是跨页面的全局视觉变更（如主题系统升级），需检查**所有**已有 Spec 文件。

## 执行参数
`$ARGUMENTS` - 截图路径、以及**用户补充的交互逻辑/产品语境**。
