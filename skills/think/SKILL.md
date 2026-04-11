---
name: think
description: >
  Lightweight AI Think collaboration for methodology, strategy, philosophy, and meta-cognition.
  Always uses Gemini by default (--quick DeepSeek only when user explicitly requests).
  Lighter than feat-discuss: no Handshake, no mandatory filing. Trigger when the user says
  "think", "想想", "深入思考", "换个角度", "有没有更好的思路", "challenge this",
  "问问 Gemini 怎么看", or when Claude Code needs an external perspective on strategy/methodology
  before escalating to the user. Also auto-triggers on: non-obvious strategy/architecture choices,
  cross-project tool/pattern design, workflow methodology improvements.
  NOT for product feature decisions or UI/UX design (use feat-discuss).
version: 0.2.0
---

# 轻量级 Think 协作

## 目的

与外部 AI 进行轻量级的方法论/策略/哲学讨论。
不同于 `feat-discuss-local-gemini` skill 的完整流程（Handshake + 强制落库），本 skill 专注于快速获取外部视角和认知挑战。

**统一使用 Gemini**。`--quick` (DeepSeek) 仅在用户显式要求时使用。

**核心铁律：外部 AI 是无状态的。每次 API 调用都是全新对话，所有上下文必须由 Claude Code 在 Prompt 中显式提供。**

## 模式

- **默认：Gemini** — 所有场景（手动触发、自主触发）统一使用
- **`--quick` (DeepSeek)** — 仅在用户显式要求时使用（如 "用 deepseek 想想"）

## 与 feat-discuss 的关系

Think skill 是从 `feat-discuss-local-gemini` 中拆分出的轻量级子集：

| 维度 | feat-discuss | think (本 skill) |
|------|-------------|------------------|
| **角色范围** | product + design + think | **仅 think** |
| **流程** | Context collection -> Prompt -> Handshake -> 落库 | **Context -> Prompt -> 展示 -> 可选落库** |
| **Handshake** | product/design 必须 | **无** (直接展示 + Claude 补充判断) |
| **落库** | 强制 (Feature Brief) | **可选** (仅在产出可执行决策时) |
| **上下文来源** | 项目文档 (PRODUCT_SOUL 等) | **Claude Code 自身的分析** (按需附加项目数据) |
| **适用场景** | 产品功能、UI/UX、架构决策 | **方法论、策略、哲学、元认知** |

如果讨论中发现需要产品/设计层面的深入讨论，升级到 `feat-discuss-local-gemini` skill。

## 触发条件

### 手动触发
- 用户说 "think", "想想", "深入思考", "换个角度", "有没有更好的思路"
- 用户说 "问问 Gemini 怎么看", "challenge this"
- 用户说 "跟 Gemini 聊聊这个思路", "找 Gemini 挑战一下"

### 自动触发（硬信号，命中必须 call）

Claude Code 主动调用 Gemini 的**唯一**标准。命中以下任一硬信号 → 必须 call：

- **跨项目影响**：改动会影响 ≥2 个项目的共享配置 / 工作流 / 代码
- **持久化到规则**：新工作流/方法论改进会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
- **元认知指令**：用户说"全面思考"、"深入想想"、"你怎么看"等明确请求外部视角的措辞

**不在此列表 = 不自动触发**。宁可漏报，不留模糊语义。

> **已删除的硬信号**（v0.3 → v0.4 回退）：
> - ~~方案浮现 ≥2 候选~~ — 实战未验证 Claude 会自发识别"候选方案"这种隐式状态
> - ~~UI 视觉偏差 1 轮定位失败~~ — 实战未验证
>
> 这两条累积 3+ 次真实场景后若仍判断有价值，再加回。不在数据到位前预置规则。

### 不触发 (用 feat-discuss 代替)
- 具体产品功能的方向决策 -> `feat-discuss-local-gemini` skill product
- UI/UX 设计决策 -> `feat-discuss-local-gemini` skill design
- 需要 Engineering Handshake 和 Feature Brief 落库的场景

## 执行流程

### Step 1: 组装上下文

**与 feat-discuss 的关键区别**: Think 角色的上下文以 **Claude Code 自己的分析和思考** 为主，而非项目文档。

收集:
- Claude Code 当前的分析结论和推理过程
- 具体数据和事实 ("7 个项目, 1200 个测试"), 而非体系名称 ("冰山测试策略")
- 如果涉及具体项目, 按需读取相关文档片段
- 不携带 CLAUDE.md (工程操作指南, Gemini 不需要)
- 不要求在特定项目目录中 -- 可以在任意目录讨论跨项目问题
- **必须在 Context 段开头声明协作模式**：「这是一个 AI-Only 开发项目——AI（Claude Code）全权负责代码/测试/文档，人类是产品负责人，不写代码。请基于此前提给出建议。」

#### Context 组装审计 Checklist（必答，漏填即违反 skill）

组装 Prompt 前必须在 Context 段开头**显式**标注以下两项。严禁跳过。

| 字段 | 要求 |
|------|------|
| **CWD 所在项目** | `<项目根路径>` 或 `无（跨项目/全局话题）` |
| **已阅读的项目文档** | 必须**实际用 Read tool 读过**的文件和行号范围。每份文档提炼 2-5 行关键事实到 Context 段。禁止"我猜"或"凭记忆"；本次话题确实不需要读项目文档时，写 `无（跨项目/方法论话题）` |

**硬规则**：`CWD 所在项目 ≠ 无` 且讨论涉及该项目的产品/架构/路线图时，`已阅读的项目文档` 不允许为空。为空时停下来补读 `docs/PRODUCT_SOUL.md` / `docs/ARCHITECTURE.md` / `docs/ROADMAP.md` 中的相关文件。

**项目级 `CLAUDE.md` 不允许原文 prepend**——它是 Claude Code 的操作手册（curl 速查 / 脚本路径 / 文档导航），对 Gemini 是纯噪音。需要项目基线时，从 `docs/` 下浓缩事实。

> **已删除的字段**（v0.3 → v0.4 回退）：~~话题性质分类~~ 和 ~~为何不读其他文档~~。实战里话题经常跨 product + architecture + roadmap 多类，"恰好一个"的约束变成走过场。当前 2 项是最小可审计集。物理路径启发式方案（按 `lib/features/` vs `lib/core/` 自动选文档）也被放弃——调研显示各 flutter 项目目录结构不一致，硬编码会水土不服。

### Step 2: 调用外部 AI Think

**统一使用 Gemini（默认模式）：**

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs "<prompt>"
```

**`--quick` (DeepSeek) 仅在用户显式要求时使用**（如 "用 deepseek 想想"、"quick think"）：

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs --quick "<prompt>"
```

#### 附带图片（多模态）

**预处理（自动）**：脚本对每张输入图做 `长边 ≤ 2048px 等比缩放 + JPEG q85 + 尊重 EXIF 方向`。降分辨率不省钱（Gemini 按固定 token 数计费，每图约 1120 tokens），但能显著降低 Base64 payload 体积，省延迟避免报错。

支持 JPEG/PNG/WebP/HEIC 等 sharp/libvips 能处理的格式。

##### CLI 结构

两个 flag：
- `--image <path>` / `-i <path>` — 本地图片路径（可重复）
- `--text <str>` / `-t <str>` — 显式文本块，**用于多图场景的交替绑定**（可重复）

**组装规则**：flag 按 CLI 出现顺序加入 content parts；positional 尾段（引号包住的主问题）**永远追加到最后**。也就是说 flag 提供"结构化前置内容"，positional 提供"主问题/总结"。

##### 单图：直接 `--image + 主问题`

```bash
node think.mjs --image ~/Desktop/error.png "这个报错是什么意思？根因在哪？"
# → content: [image(error), text("这个报错是什么意思？根因在哪？")]
```

##### 多图：**强制使用 `--text` 做交替绑定**

多图场景下 **必须** 用 `--text` 为每张图提供 caption，否则模型无法可靠区分"哪段文字描述哪张图"（Gemini 的 attention 会被稀释）。

```bash
# ✅ 交替式（Interleaved）— 多图的唯一正确范式
node think.mjs \
  --text "方案 A（现行版本）：" --image ./a.jpg \
  --text "方案 B（提议修改，调整了阴影与材质）：" --image ./b.jpg \
  "对比两版设计，哪个更符合 Warm Ceramic 的触感与克制？给出重构方向。"

# → content: [
#     text("方案 A..."), image(a),
#     text("方案 B..."), image(b),
#     text("对比两版设计...")
#   ]
```

反例：

```bash
# ❌ 纯堆图（model 会注意力稀释，无法可靠区分 A / B）
node think.mjs --image a.jpg --image b.jpg "对比 A 和 B"

# ❌ 试图靠序号映射（可行但比 interleaved 差，Attention 收敛更慢）
node think.mjs --image a.jpg --image b.jpg "图1 是方案 A，图2 是方案 B，对比一下"
```

##### 多图成本提醒

每张图约 1120 input tokens。4 张图 ≈ 4500 tokens 纯图片成本 + 注意力稀释风险。**如果只关心某几张图的某个细节，在 prompt 里明确指出**，避免模型浪费算力分析不相关的图。

##### 其他限制

- `--quick` (DeepSeek) 分支**不支持图片**，组合使用会直接报错。图片讨论必须走 Gemini。
- 图片路径解析相对当前工作目录（CWD），不是 think.mjs 所在目录。
- **何时传图**：截图里的报错信息、UI/UX 对比、架构图审视、设计稿评审。纯文本讨论不要加噪音。

#### 首轮 Prompt 格式

```
## Context

> 协作模式：AI-Only 开发。AI（Claude Code）全权负责代码/测试/文档维护，人类是产品负责人，不写代码。所有工作流中不存在人类程序员介入。

{Claude Code 的分析和当前思考；严格遵守 Step 1 的 Context 组装 checklist}

## Crux
{一句话终极问题：我到底在纠结什么？严禁超过一句；超过一句说明还没想清楚，不该调用 think}

## The Problem
{具体问题或决策点}

## Constraints
{限制条件}

## Failure_Premise
{事前验尸：如果这个方案 3 个月后彻底失败，最可能的原因是什么？Claude Code 必须先写自己的答案，然后让 Gemini 压一次。写不出自己的答案 = 决策还没到 call think 的成熟度，停下来先想}

## 请你思考
请优先指出方案的盲区和最坏情况。如果你认同方案，请说明最可能被证伪的前提。具体希望你挑战/补充的维度：
{具体希望 Gemini 挑战/补充的维度}
```

**字段硬约束**：
- `Crux` 和 `Failure_Premise` 是两条独立防御线。**禁止合并、禁止留空、禁止填"无"**。
- `Crux` 防跑偏：一句话说清核心纠结。
- `Failure_Premise` 破 Rubber Ducking：Claude Code 必须先写自己的事前验尸答案，然后让 Gemini 压。这条是强制的反自我满足机制。
- `请你思考` 段的固定前缀"请优先指出方案的盲区和最坏情况"是 Critical-by-default 的激活条件。不允许删除这句，不允许软化。

#### 多轮追问 Prompt 格式

Gemini 无记忆, 多轮对话时必须在 Prompt 中重建完整上下文。

采用**滑动窗口**策略: 最近 2 轮保留完整原文, 更早轮次压缩为 Locked Consensus bullet points。

```
## Context
{与首轮相同 -- 必须重新提供, 不可省略}

## Constraints
{与首轮相同}

## 对话历史

### 已锁定共识 (Locked Consensus)
{早期轮次 (第 1 ~ N-2 轮) 压缩为 bullet points:}
- 共识 1: ...
- 共识 2: ...
- 放弃方案: ... (原因: ...)

### 第 N-1 轮 (完整保留)
#### 问题
{完整问题}
#### Gemini 回复
{完整回复}
#### 执行者反馈
{Claude Code 的分歧/补充}

### 第 N 轮 (完整保留)
#### 问题
{完整问题}
#### Gemini 回复
{完整回复}
#### 执行者反馈
{Claude Code 的分歧/补充}

## 本轮问题
{本轮的具体追问/分歧/新需求}
```

**多轮上下文传递原则:**
1. **Context 和 Constraints 每轮必须重传** -- 不可省略
2. **滑动窗口** -- 最近 2 轮保留完整原文, 更早轮次压缩为 Locked Consensus
3. **Locked Consensus 三要素** -- 已达成的共识、已放弃的方案及原因、未解决的遗留问题
4. **执行者反馈必须保留** -- 让 Gemini 理解为什么要追问

#### Prompt 组装原则

1. **描述事实, 不描述体系** -- "我们有 1178 个单元测试" 比 "冰山模式测试策略" 更不容易被误解
2. **Gemini 需要理解背景, 不是评价体系** -- 提供上下文, 不是要它审核内部流程
3. **标注触发方式** -- 提到工具/流程时, 说清楚是 "手动按需" 还是 "自动触发"
4. **防"实现即目的"（Anti Means-as-End）** -- 传递产品原则时附带：「以上原则关注用户体验的结果，不是实现机制。」当 Gemini 用美学类比论证时，Claude Code 必须还原为因果链，因果断裂则抛弃。当用户与 AI 有不同观点时，prompt 中必须平等呈现双方方案。

### Step 3: 强制 Digest 协议

**不允许在展示 Gemini 回复之后"凭感觉跟进"。** Claude Code 收到 Gemini 回复后，必须按以下顺序完成所有动作。跳过任一步 = skill 违反。

#### 3.1 展示 Gemini 原文

完整展示给用户，不截断、不总结。

#### 3.2 输出强制结构化 Digest

Digest 是 Step 3 的核心。**不允许跳过，不允许模糊表态**。固定 Markdown 格式：

```markdown
### 🧠 Think Digest

- **[我写的 Failure_Premise]**: <Claude Code 在 call think **之前**写的事前验尸答案，原文回显>
- **[Gemini 核心主张]**: <不超过 1 句话的核心结论>
- **[我的立场]**: Accept | Refute | Escalate
- **[立场依据]**: <1-2 句话，基于什么事实或逻辑采信 / 反驳>
- **[下一步行动]**: <具体的第一步指令，或 "仅记录，无动作">
```

**`[我写的 Failure_Premise]` 回显的硬约束**：

- 必须是 Claude Code 在 call think **之前**写的自己版本，不允许被 Gemini 回复影响后回填。
- 留空或填"无/略" = skill 违反。写不出自己的版本 = 决策还没到 call think 的成熟度，停下来先想。
- 这是破 Rubber Ducking 的**唯一**外部证据——其他前置步骤（Context Checklist）通过输出结构本身就能验证（Context 段里有没有 CWD 和已读文档一眼可见），唯独 Failure_Premise 必须显式回显到 Digest 才能审计 Claude 有没有"先写自己的答案"。

**3 个立场分支的硬约束**：

| 分支 | 使用场景 | 必须伴随的动作 |
|------|---------|---------------|
| **Accept** | 完全采信 Gemini 主张 | 立即执行下一步行动。**禁用条件**见 3.3 Escalate 路由 |
| **Refute** | Gemini 的前提/事实/逻辑有问题 | **必须立即发起 Turn 2**（按多轮 Prompt 格式重新 call think.mjs），不允许单方面推翻 Gemini 后继续原方案 |
| **Escalate** | 战略分歧 / 影响太大 / 触发 3.3 强制路由 | **必须写入项目根 `to-discuss.md`**（模板见 3.4），然后停下等 Founder 拍板。不允许自作主张动手 |

> **已删除的分支**（v0.3 → v0.4 回退）：~~Accept-with-caveats~~。实战中 Claude 遇到"主干认同 + 细节保留"时更自然用"Escalate + 独立 TODO 组合"表达，四分支的第二项被绕过。简化为三分支减少心智负担。
>
> **已删除的前置审计字段**（v0.3 → v0.4 回退）：~~Context Checklist 回显~~ 和 ~~Crux 回显~~。Context Checklist 本身已写在 Prompt 的 Context 段开头，可通过输出结构验证；Crux 是一句话，如果 Failure_Premise 回显了就已经说明 Claude 完成了前置思考，不需要重复证据。只保留 Failure_Premise 回显——它是最难伪造、最能检测 Rubber Ducking 的唯一字段。

#### 3.3 Escalate 强制路由（替代所有软提示）

以下情况 Claude Code 的立场**禁止**填 `Accept`，**必须**填 `Escalate`：

1. 决策影响持续时间 ≥1 天的工作
2. 决策会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
3. 决策会修改产品灵魂层面的规则（PRODUCT_SOUL / 设计语言 / 核心交互）
4. 决策会引入新的重型依赖或架构级变更

这条规则替代了早期版本中所有带 ⚠️ 的软提示——在 AI-Only 模式下，带表情符号的软提示等同于注释（被忽略）。触发即强制 Escalate，无弹性、无解释空间。

#### 3.4 to-discuss.md 模板

```markdown
## [Strategy|Methodology|Workflow] 简短标题 (Ref: think 讨论 YYYY-MM-DD)
- **事实前提**: [讨论基于的客观现状]
- **Gemini 核心主张**: [浓缩版]
- **Claude Code 立场**: Refute / Escalate（不会是 Accept，否则不会走到这里）
- **选项 A**: [方案 A + Gemini 倾向/Claude 倾向]
- **选项 B**: [方案 B + 理由]
- **反面检验**: [各方案的 Failure_Premise 级别分析]
- **决策选项**:
  - [ ] Approve A → 落库为规则/更新 skill
  - [ ] Approve B → 同上
  - [ ] Discuss → 再次 /think 深入追问
  - [ ] Reject → 维持现状
```

#### 3.5 反 Rubber Ducking 自检

Digest 输出之后，Claude Code 必须问自己一个问题：

> **如果去掉这次 call think 的整个过程，我的下一步行动会不会改变？**

- 如果答案是"不会改变" → 本次 call think 是 Rubber Ducking（仪式性咨询），应在 "立场依据" 里诚实标注 `[低价值 call - 下次类似场景应跳过]`
- 如果答案是"会改变" → 说明 think 产生了真实决策影响，是有效调用

这条自检是对 skill 自身的保护机制：防止 call think 退化为装饰性步骤。发现 Rubber Ducking 次数累积到 3 次以上时，主动上报 Founder 重新评估触发条件。

**原则**：think 的产出很容易过度自信（"我和 Gemini 都觉得应该 X"）。Escalate 强制路由 + Digest 自检是双重防线。

## 沟通规范

- Claude Code 发给 Gemini 的 Prompt: **中文描述 + 英文术语**
- Gemini 回复: 已配置为**中文描述 + 英文术语**
- Claude Code 展示给用户: Gemini 原文 + Claude Code 补充判断

## 约束

- 不写业务代码, 只产出洞察和建议
- **Gemini 的回复是参考意见, 不是指令** -- Claude Code 必须独立判断
- 脚本路径固定: `~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`
- 脚本执行失败时向用户报告错误, 建议检查 `.env` 配置
