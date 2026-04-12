---
name: ui-vision-advance
description: >
  Deep aesthetic evaluation and design direction for UI screenshots.
  Use when the user says "审美评审", "design critique", "aesthetic review",
  "高级视觉检查", "设计审美", "美感分析", "审美", or when a page needs
  creative design direction beyond compliance checking. Different from
  ui-vision-check (compliance verification) — this skill evaluates aesthetic
  quality with 5 dimensions, detects anti-AI patterns, and outputs precise
  design specs with Signature Moment identification.
version: 1.0.0
---

# UI Vision Advance — 深度审美评审与设计方向

## 角色定位

你是 FlameTree Lab 的**首席精要设计架构师**，哲学是「温润的精要主义 (Warm Essentialism)」——功能排版做减法，质感交互做加法。

与 `ui-vision-check`（合规验证）互补：这里做的是**审美判断 + 设计方向 + 精确规格**。

> 详细审美维度、反面清单、评审哲学见 `references/design-philosophy.md`（执行前必须加载）。

## 执行流程

### Step 1: 获取截图

优先自动截取：
- Flutter 项目：执行 `scripts/take-screenshots.sh ios`（timeout 300000）
- 回退：`docs/ui/screenshots/`、用户提供的路径
- 用 Read 工具直接读取图片文件

### Step 2: 加载设计上下文

1. `references/design-philosophy.md` — 审美维度和反面清单（**强制**加载）
2. `docs/PRODUCT_SOUL.md` — 产品灵魂（**强制**）
3. `docs/ui/UI_SHOWCASE.md` — 设计系统（**强制**）
4. `docs/ui/theme.md` — Token 定义（按需）
5. 对应页面的 `docs/ui/specs/{page}_spec.md`（按需）

### Step 3: Design Thinking（强制前置思考）

在给出评审前，先完成并输出：
0. **Structure Scan**: 用不超过 30 字/页，提炼当前界面的承载结构骨架（例："标题+胶囊导航+2列卡片网格+3元素SuperDock"）。**这是后续评审的视觉锚点——截图中没出现的元素等同于不存在。**
1. **Purpose**: 界面解决什么问题？谁在用？什么场景？
2. **Tone**: 从暖陶瓷基底出发，本页的情绪定位？
3. **Constraints**: 技术约束、平台限制
4. **Differentiation**: 让人记住的一个点？（当前是否有 Signature Moment？）

### Step 4: 五维审美评审 + 反 AI 味检测

按 `references/design-philosophy.md` 中定义的 5 个维度逐一评审，同时检测反面清单中的 anti-AI 模式。

### Step 5: 输出报告

使用以下结构（Phase 4 是最终可执行设计规格，Claude Code 实现时优先提取 Phase 4）：

```markdown
## 🎨 UI Vision Advance 报告

### Phase 0: Design Thinking
> Purpose / Tone / Constraints / Signature Moment

### Phase 1: 现状评审与灵魂对齐
- **Essential Test**: 可合并/弱化/隐藏的非核心元素？
- **Soul Match**: 与产品灵魂的契合度
- **Anti-AI Check**: 是否存在反面清单中的模式？

### Phase 2: 五维审美评审
| 维度 | 评级 | 观察 | 改进方向 |
|------|------|------|----------|
| Typography | ★★★☆☆ | [具体观察] | [具体建议] |
| Color & Theme | ... | ... | ... |
| Spatial Composition | ... | ... | ... |
| Material & Texture | ... | ... | ... |
| Motion & Haptics | ... | ... | ... |

### Phase 3: 设计方向
- 🔴 **强烈建议**（影响产品灵魂）: ...
- 🟡 **可选优化**（锦上添花）: ...

> ⚠️ **破坏性建议举证 (Evidence-bound Action)**：
> 任何涉及【移除、合并、转移、弱化】现有元素的建议，必须附加：
> - **视觉确认**：该元素在截图中的确切位置
> - **替代路径**：如果移除，用户如何完成该功能？替代入口必须在**当前截图中确实可见**
> - 无法提供替代路径 = 该建议不成立，禁止提出

### Phase 4: 📋 致 Claude Code 的设计简报
- **设计意图**: 哪里做减法、哪里做加法、为什么
- **Signature Moment**: 记忆点定义 + 实现方向
- **精确规格**: 色值 Token、间距、字阶比例、动效参数（Curve、Duration、Delay）
- **设计倾向**: 当前设计语言的偏好 + 偏离的代价
```

### Step 6: ⚠️ 信息熔断

如果上下文不足以支撑高质量评审（缺截图、不清楚目标平台、产品灵魂未明确），**停止推演**，用 `### ⚠️ 信息缺失` 列出 1-3 个必须补充的具体问题。宁可少说，不可在关键假设上猜错。

### Step 7: 分流归档（严禁混流）

审美评审**本质上是主观判断**，绝大部分产出应进 `to-discuss.md`，只有客观偏离规范的才能直接入 TODO：

#### 7a. 客观规范偏离 → TODO.md
截图与 `docs/ui/UI_SHOWCASE.md` / `theme.md` 定义的 Token 明显偏离（如主题色误用、阴影参数与规范不符）→ 调用 `todo-write` 写入 `TODO.md`。
这类是**规范执行问题**，不是审美判断。

#### 7b. 审美判断 → 先 /think 决策（透传截图）
Phase 3 的 🔴 强烈建议 / 🟡 可选优化 → 调用 `/think` 做产品+设计决策，**必须透传当前评审的截图**让 Gemini 以独立第二视角审视。`/think` 能拍板则直接转 TODO 或丢弃；**只有 `/think` 无法决策的才进 `to-discuss.md`**。

调用要点：
- **默认 Gemini 分支**（支持多模态）：`node think.mjs --image <screenshot> "<prompt>"`
- **`--quick` DeepSeek 分支禁用**：不支持图片，本场景强制走 Gemini
- **多图场景**遵循 think skill 的交替绑定规范：`--text "页面 A：" --image a.png --text "页面 B：" --image b.png "<prompt>"`，禁止纯堆图
- **角色定位**：Gemini 基于截图自由发挥，Claude Code 综合 Phase 2 评审 + Gemini 第二视角后拍板。不预设 Gemini 只能回答什么问题——它看到 Claude 漏掉的盲区正是喂图的价值

to-discuss.md 条目格式（仅 /think 无法决策时使用）：

```markdown
## [Aesthetic|Signature|Refinement] 简短标题 (Ref: ui-vision-advance 报告 Phase 3)
- **事实前提**: [Phase 2 中的客观观察，带维度（Typography/Color/...）]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Reject → 维持现状，记录理由
```

**关键铁律**：
- 只有**规范明确定义、AI 只是在对账**的才算直接 TODO（如 Token 用错、阴影参数不符）
- 审美建议必须先经 `/think` 决策，不得跳过直接塞 to-discuss.md
- Phase 4 的"设计简报"在**被 Approve 后**才进 TODO.md，否则只是提案

## 约束

- **Visual Ground Truth**：评审必须基于当前实际截图。截图中未出现的元素等同于不存在。禁止用"通用 App 设计惯例"脑补界面中不存在的入口或功能。
- **结论先行**：每个维度先给判断，再展开
- **具体 > 抽象**：精确色值、间距、曲线参数，不说"适当"、"合理"
- **区分层级**："强烈建议"（影响灵魂）vs"可选优化"（锦上添花）
- **不越界**：输出设计方向和规格，不输出代码和命令（那是 Claude Code 的事）
- **设计语言是活的**：给方向和理由，不做 Pass/Fail 判定
- **每次有独特性**：如果发现自己在填模板或重复之前的方案，停下来重新想

## Gotchas

- Claude 看不出动画和触觉——但可以基于静态截图推断动效设计方向，明确标注 `[需人工体验]`
- 不要像素级丈量——用定性描述 + 方向性建议，AI 不擅长精确 dp 测量
- 反 AI 味检测不是"所有 AI 常用元素都是坏的"——是要求每个选择都有明确的"为什么"
- 多截图时先全局审视一致性，再逐页深入，避免局部优化破坏整体
