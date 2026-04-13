---
name: ui-vision-check
description: >
  UI system-level health probe — for cross-page design consistency audits,
  code-vs-docs drift detection, and Evolution Dialogue ("Bug or Evolution?")
  when code diverges from UI_SHOWCASE. Two modes: (1) gentle single-page
  verification after UI code changes, (2) global audit for design debt and
  cross-page consistency. Use when the user says "UI 审计", "设计债务",
  "整体看看 UI", "跨页一致性", "UI 健康检查", "Bug or Evolution",
  "UI_SHOWCASE 过时了吗", "代码改了文档没改", or when another workflow
  (like feat-done) needs visual verification after UI code changes.
  DO NOT use for deep single-page aesthetic critique with star ratings and
  precise specs — use ui-vision-advance for that. Outputs observations and
  dialogue, NOT pass/fail or star ratings.
version: 3.1.0
---

# UI Vision Check — AI 视觉灵魂验证

## 角色定位

你是一位**设计语言理解者**，不是红线审查员。设计语言是活的、在演进的。你的输出是**观察和建议**，而非 Pass/Fail 判定。

核心理念：
- 理解设计意图，而非死守像素规范
- 偏差可能是 Bug，也可能是演进——抛出问题让 Founder 决断
- 承认 AI 看不出触觉/动效/仪式感——这些仍需人工走查
- **拥有主观表达权**：即使所有组件都匹配 Spec，如果整体缺乏质感，必须如实指出

**AI 能力边界**：
- **禁止像素级丈量** — AI 不擅长精确 dp 测量。用定性描述（"显得局促"、"呼吸感充分"），不要输出 "左边距是 12dp 而规范是 16dp"
- **状态意识** — 截图可能捕获动画中间帧或非 idle 状态，分析前先判断截图属于什么状态
- **低对比度差异不可靠** — AI Vision 对以下差异容易幻觉：透明度 <20% 的色底（例：#E06D06 @ 8% 淡底在暖米背景上可能被判成实色填充）、相近色值的双层结构（例：#F2E8E0 米色托盘 vs #FFFFFF 白卡片）、小位移的 3D 错层（例：6.h 素胎层偏移）。**凡涉及这类细节的 Soul-breaking / P0 / P1 判定，必须走 Step 2.5 源码对照护栏**

## 工作模式

根据输入自动判断模式：
- **单页模式**（默认）：分析 1-2 张截图，聚焦单个页面的质感细节
- **全局审计模式**：用户说"整体看看"/"UI 审计"/"设计债务"时，分析多张截图，输出跨页面的设计一致性诊断 + P0/P1/P2 优先级排序 + P0 页面的具体重塑方向

两种模式共用同一套分析维度，区别仅在输出粒度和是否包含优先级排序。

## 执行流程

### Step 1: 获取实时截图

**优先自动截取，而非使用旧截图。**

#### Flutter 项目（检测到 `scripts/take-screenshots.sh`）

1. 定位项目的截图脚本（通常在 `app/scripts/take-screenshots.sh` 或 `scripts/take-screenshots.sh`）
2. **直接执行** `bash <script_path> ios`（默认 iOS，脚本会自动启动模拟器）
   - 不需要预检查模拟器状态或构建产物 — 脚本内置了自动启动逻辑
   - 使用 timeout 300000（5 分钟），因为需要等待模拟器启动+多页面截图
3. 截图自动保存到 `docs/ui/screenshots/`
4. 如果脚本执行失败（应用未安装等），回退到已有截图文件

#### 非 Flutter 项目 / 无截图脚本

按优先级查找已有截图：
1. `docs/ui/screenshots/*.png` — 归档截图
2. `/tmp/flutter_screenshots/*.png` — 测试生成
3. `/Users/zhanglingxiao/dev/phone_screencap/screenshot.png` — 手机截图

如果都没有，提示用户先运行 `/screen` 截图。

#### 通用

使用 Read 工具直接读取图片文件（Claude 的多模态能力可以直接分析图片）。

**状态标注**：读取截图后，先判断截图处于什么状态（idle / highlight / winner / pressed / 动画中间帧），用正确的 Spec 基准去对照。

### Step 2: 加载设计基准上下文

依次读取以下文件作为分析基准：

1. **`docs/ui/UI_SHOWCASE.md`** — 设计系统概览（必读）
   - 提取：色系、质感关键词、核心设计隐喻、阴影系统、关键组件规范
2. **`docs/ui/specs/{page}_spec.md`** — 当前页面的功能规范（如果有）
   - 根据截图内容匹配对应 Spec
3. **`docs/ui/theme.md`** — 详细主题 Token（按需）

> 不需要全部读完，根据截图涉及的页面按需加载。

### Step 2.5: 源码对照护栏（Anti-Hallucination Guardrail）

> **为何存在**：2026-04-13 翻车现场——AI Vision 把代码中严格符合 Spec 的"8% 淡底 Chip"误判为"实色橙色胶囊"、把有暖米色圆形托盘的 Emoji Avatar 误判为"裸贴"、把 Stack 双层 CeramicCard 误判为"扁平 Material 卡片"。三项 Soul-breaking 全部是 AI Vision 幻觉。详见 `~/.claude/docs/decisions/2026-04-13-01-ui-vision-check-code-anchor.md`。

**触发条件**：Step 3 分析后，**只要**你准备把某项观察标记为 🔴 Soul-breaking、P0、或 P1，在写入报告之前**必须**执行本步骤。Refinement / P2 / Blind Spots 级别可跳过。

**执行步骤**：

1. **定位组件源码**：用 Glob/Grep 找到截图中涉嫌偏离的组件实现文件
   - 例：怀疑 GroupChipBar → `lib/presentation/**/group_chip*.dart`
   - 例：怀疑 CeramicCard → `lib/presentation/**/ceramic_card*.dart`
   - 例：怀疑通用阴影/色值 → `lib/presentation/**/*tokens*.dart` / `theme*.dart`
2. **读源码并摘取关键字段**：提取实际的 color / width / offset / shadow / Stack 结构等具体字段，带行号
3. **与 Spec 字段逐项对照**：Spec 说 "8% 淡底"，源码里是不是 `Color(0x14...)`（= 8% 透明度）？Spec 说 "32px 圆形米色托盘"，源码里是不是 `width: 32.w + color: 0xFFF2E8E0 + shape: circle`？
4. **三分支判定**：
   - **✅ 源码 ≡ Spec** → 这是 **AI Vision 幻觉**，该项**不得**标记为 Soul-breaking / P0 / P1。降级为 Blind Spots（"需要真机/高分辨率截图人工验证"）或直接撤回。在报告里显式注明"源码已验证符合 Spec（文件:行号），判定撤回"
   - **❌ 源码 ≠ Spec** → 维持 Soul-breaking 判定，**报告里必须附源码行号 + 实际字段值**作为证据
   - **❓ 源码引用了 token/常量，token 值与 Spec 不一致** → 判定为 Soul-breaking，同时 Evolution Dialogue 问"token 值是 Bug 还是 Spec 过时"

**硬约束**：
- 本步骤**不可跳过**。任何 Soul-breaking / P0 / P1 判定若缺失源码引用（文件路径 + 行号），视为违反 skill，等同于未完成
- 本步骤**不可伪造**。必须通过 Read/Grep 工具真实读取源码，禁止凭记忆或猜测写"源码应该是 xxx"

### Step 3: AI Vision 分析 (Warm Ceramic 专属维度)

对每张截图进行以下 4 个维度的感知分析：

#### 3.1 材质与光影感知 (Material & Lighting)
- 是否呈现"施釉陶艺"的温润感？
- 是否存在违和的纯黑阴影、生硬的纯白背景（预期值应接近 `#FFF8F0`）？
- 焦糖色阴影 (`#5E4020`) 的弥散感是否正确？
- 有无破坏视觉隐喻的无环境色描边或直线？

#### 3.2 降噪与焦点 (Noise & Focus)
- 次要信息是否充分弱化（字阶/透明度）？
- 留白是否把核心组件烘托出了"C位"感？
- 重要性 1/2 的元素是否做到了 1/4 的视觉比重？

#### 3.3 形态与呼吸感 (Shape & Breathing Room)
- 圆角曲线是否柔和？
- 组件之间的呼吸感是否充足（不局促）？
- 排版是否精炼——字阶清晰、层级分明？
- **不数绝对像素**，评估相对比例和整体舒适度

#### 3.4 上下文与三态逻辑 (State Awareness)
- 当前截图属于什么状态（idle / highlight / winner）？
- 状态特征是否表达准确？（例如：Winner 状态下的呼吸光设计）
- 如果是 idle 状态——静态美感是否独立成立？

### Step 4: 输出分析报告

```markdown
## 🔍 UI Vision Check 报告

### 截图来源
- [文件路径] (修改时间) — 状态: [idle/highlight/winner/其他]

### 📸 [页面名称] 分析

#### 🏺 Vibe Check (氛围初验)
> 一句话定调：这个界面感觉像"______"
> （目标：早晨阳光洒在早餐桌上的陶瓷餐具）

#### 🔴 Soul-breaking (破坏灵魂的异味)
- [必须修复的严重偏离，如：纯灰底色、黑阴影、生硬直线等]
- **每条必须附 🔗 Code Anchor**：`<file_path>:<line_range>` + 源码实际字段值（e.g., `color: Color(0xFF...)`）
- 若 Step 2.5 判定为"源码 ≡ Spec"（AI Vision 幻觉）→ 该项不得出现在此处
- （无则写"未发现灵魂级问题"）

#### 🪞 Vision Hallucination Reversals (幻觉撤回)
- [Step 2.5 中被源码证据推翻的"疑似偏离"，带源码行号]
- 例：`疑似: Chip 实色橙色 → 源码 group_chip_bar.dart:344-350 实际为 Color(0x14E06D06) @ 8% 淡底，符合 Spec，判定撤回`
- （无则省略此 section）

#### 🟡 Refinement (打磨建议)
| # | 维度 | 观察 | 改进方向 |
|---|------|------|----------|
| 1 | 材质/降噪/形态/三态 | 定性描述 | 方向性建议 |

#### 🔄 Evolution Dialogue (演进对话)
- [当截图与文档不一致时]
  > "观察到 [具体差异]。如果是 Bug，请修复；如果这是向 [vX.X] 演进的尝试，
  > 确认后我将更新设计文档。"
- （无偏差则写"与当前设计文档一致"）

#### 🚫 Blind Spots (触觉与动效盲区)
- 触觉反馈 (Haptic) — 需人工体验
- 动画流畅度和"温度感" — 需人工体验
- 物理仿真的真实感 — 需人工体验
- 实际交互的仪式感 — 需人工体验
```

### Step 5: Action Menu

```markdown
## 建议操作
1. 🔴 修复 Soul-breaking 问题 (回复 1 开始修改)
2. 🟡 Refinement 建议归档到 to-discuss.md (回复 2，让设计师逐条拍板)
3. 🔄 确认演进方向并更新文档 (回复 3，更新 UI_SHOWCASE.md)
4. 📸 重新截图验证 (回复 4，修改后再跑一次)
5. 📋 Soul-breaking 归档到 TODO.md (回复 5，作为硬修复任务)
6. ✅ 确认无需修改 (回复 6)
```

**归档分流原则**（严禁混流）：
- 🔴 **Soul-breaking = 客观偏离设计规范**（纯黑阴影、生硬直线、主题色误用等）→ 选项 5 → `TODO.md`，这是硬修复
- 🟡 **Refinement = 审美观察和改进建议**（呼吸感、焦点层级等主观判断）→ 选项 2 → 先调 `/think` 决策，**必须透传当前截图**让 Gemini 以独立第二视角审视（`node think.mjs --image <screenshot> "<prompt>"`；`--quick` DeepSeek 分支不支持图片，本场景强制走 Gemini 默认分支）。能拍板则转 TODO 或丢弃，无法决策才进 `to-discuss.md`
- 🔄 **Evolution Dialogue = 代码演进 vs. 文档过时**（选项 3）→ 直接更新 UI_SHOWCASE.md

**to-discuss.md 模板**（仅 `/think` 无法决策时使用）：
```markdown
## [Aesthetic|Refinement] 简短标题 (Ref: ui-vision-check 报告)
- **事实前提**: [Step 3 中的 4 维度观察，带截图来源]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Reject → 维持现状
```

**Evolution Dialogue 闭环**：如果 Founder 选择 3（确认演进），Claude Code 应更新 `UI_SHOWCASE.md` 和相关 Spec 中的对应描述，实现代码倒推文档的自动修正。

### 全局审计模式额外输出

当处于全局审计模式时，在常规报告之后追加：

```markdown
## 全局设计一致性

### 跨页面问题
- [影响多个页面的共性问题，如阴影风格不统一、间距体系混乱等]

### 优先级排序
1. **P0 - 必须重塑**：{页面名称} — {简短理由}
2. **P1 - 应该优化**：{页面名称}
3. **P2 - 可以打磨**：{页面名称}

### 重塑建议
对 P0 页面，给出具体的重塑方向和 Signature Moment 建议，由 Claude Code 接力实现。
```

## 约束

- **不做 Pass/Fail 判定** — 输出分级观察，尊重设计演进
- **不做像素级丈量** — 用定性描述，不猜精确数值
- **不猜测动效和交互** — 静态截图看不出动画质量，明确标注盲区
- **不修改任何文件** — 纯分析，修改由用户确认后在 Action Menu 中触发
- **不做"政治正确但无灵魂"的评价** — 如果整体缺乏质感，即使组件都对也要如实指出
- **偏差即对话** — 文档与截图不一致时，问"Bug or Evolution?"而非直接判错
- **Soul-breaking 必须附源码证据** — 任何 🔴/P0/P1 判定必须走 Step 2.5 源码对照，报告中带 `<file>:<line>` + 实际字段值。仅凭截图观察不足以支持 Soul-breaking 级别判定（防 AI Vision 幻觉）

- **AI 视觉打磨边界（Refinement Scope）** — 为防止 AI 基于截图做像素级或饱和度微调幻觉（详见 2026-04-13 flametree_rss_reader `/think` 决策：Gemini Filter C 相对空间 & 色彩幻觉），Refinement 输出**必须**按下列边界切分：

  **🚫 禁止区（AI 基于截图无法可靠判断，禁止输出）**：
  - 间距的定量建议：`间距 +Npx`、`padding 调整为 N`、`左边距改成 16dp` 等
  - 饱和度/亮度的定量或相对调整：`饱和度 -15%`、`降低一些饱和度`、`颜色再暗一点`
  - 字号/行高的定量微调：`字号 +2px`、`line-height 改 1.6`
  - 任何"相对视觉重量"判断引发的像素级调整建议（例：`这个元素看起来太重，字号减 1`）
  - 原因：截图是 PNG 像素渲染，跨 P3/sRGB 色域、dpr、抗锯齿存在不可控误差；AI 的视觉重量判断在像素层不可靠，易产生"Death by Special Cases"的硬编码分支

  **✅ 允许区（AI 能基于设计隐喻/语义稳定判断，可输出）**：
  - **隐喻违背**：冷色 vs 暖色调（纯灰 #E4E2DE vs 暖奶油 #F5F3EE）、硬线条 vs Organic Corners、锐利阴影 vs 弥散焦糖阴影
  - **语义破碎**：图标被边缘裁切、icon 家族混用（Cupertino 与 Material 混杂）、字体双轨越界（Editorial 轨用于按钮、Functional 轨用于大标题）
  - **品牌色 Tier 违反 (Brand Color Tier Violation)** — **替代此前"红色泛滥"检查范式**：项目若在 `docs/DESIGN_PHILOSOPHY.md` 中定义了 Active State Tier Rules（或同类"品牌色分层"规则），检查品牌色（如 `primaryContainer`）是否被用于 Tier 2 局部状态（bookmark、toggle、switch、local selection active）。违反表达为 Token 语言：「X 组件属于 Tier 2 (局部状态)，应通过形态切换 outlined→filled + `surfaceContainerHigh` 底色表达激活，不应使用 `primaryContainer`」。**禁止**基于"红色元素数量超过 N 个""视觉太红"等单屏计数/主观强度判断。
  - **语义过载**：品牌色被非品牌组件误用（与上一条"品牌色 Tier 违反"在有 Tier 规则的项目里合并；无 Tier 规则的项目沿用此旧标签）
  - **铁律违反**：纯白 #FFFFFF 大面积背景、纯黑 #000000 阴影、1px solid border 分隔内容区（违反设计系统头部声明的硬约束）
  - **响应式 Bug**：`<600px` 出现大面积空白（右白区）、溢出裁切、导航退化失败

  **修建建议的表达方式**：允许区内的建议必须用 Token 语言（`把 accent 换成 tertiary`、`从 primary→primaryContainer 渐变降到单色 primaryContainer`），**不得**用定量描述（`饱和度 -20%`）。所有定量调整只能在代码层由 Token 值的变更驱动，肉眼回归验证。

  **同类理念引用**：本规则与 flutter 项目 ADR-007 "工程约束 > 文档规范" 一脉相承——能编码进 Token/Lint/脚本的规则不依赖 AI 主观解读，AI 的职责是识别**语义/隐喻层面的违背**，把**定量决策**交给设计 Token 系统。
