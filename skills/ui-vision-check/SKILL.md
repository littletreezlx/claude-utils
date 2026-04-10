---
name: ui-vision-check
description: >
  This skill should be used to visually verify UI screenshots against the project's
  design language. Supports both single-page checks and full-project UI audits.
  Use PROACTIVELY after significant UI changes, after a batch of visual modifications,
  or when the user says "check UI", "视觉检查", "UI 看看", "截图分析", "design check",
  "UI 审计", "审视整体 UI", "设计债务". Also use when another workflow (like delivery
  or ui-redesign) needs visual verification. Reads screenshots + design docs, then
  provides observations and suggestions — NOT pass/fail judgments.
version: 3.0.0
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

## 工作模式

根据输入自动判断模式：
- **单页模式**（默认）：分析 1-2 张截图，聚焦单个页面的质感细节
- **全局审计模式**：用户说"整体看看"/"UI 审计"/"设计债务"时，分析多张截图，输出跨页面的设计一致性诊断 + P0/P1/P2 优先级排序 + 直接可用的 `ui-redesign` 触发建议

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
- （无则写"未发现灵魂级问题"）

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
- 🟡 **Refinement = 审美观察和改进建议**（呼吸感、焦点层级等主观判断）→ 选项 2 → 先调 `/think --quick` 决策，能拍板则转 TODO 或丢弃，无法决策才进 `to-discuss.md`
- 🔄 **Evolution Dialogue = 代码演进 vs. 文档过时**（选项 3）→ 直接更新 UI_SHOWCASE.md

**to-discuss.md 模板**（仅 `/think` 无法决策时使用）：
```markdown
## [Aesthetic|Refinement] 简短标题 (Ref: ui-vision-check 报告)
- **事实前提**: [Step 3 中的 4 维度观察，带截图来源]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md（或 /ui-redesign）
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
对 P0 页面，建议触发 `ui-redesign` 进行重塑。
```

## 约束

- **不做 Pass/Fail 判定** — 输出分级观察，尊重设计演进
- **不做像素级丈量** — 用定性描述，不猜精确数值
- **不猜测动效和交互** — 静态截图看不出动画质量，明确标注盲区
- **不修改任何文件** — 纯分析，修改由用户确认后在 Action Menu 中触发
- **不做"政治正确但无灵魂"的评价** — 如果整体缺乏质感，即使组件都对也要如实指出
- **偏差即对话** — 文档与截图不一致时，问"Bug or Evolution?"而非直接判错
