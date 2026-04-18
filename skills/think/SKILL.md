---
name: think
description: >
  Lightweight AI Think collaboration for methodology, strategy, philosophy, and meta-cognition.
  Defaults to DUAL mode: Gemini + GPT-5.4 called in parallel, then Claude Code judges which
  answer served the specific question better. `--solo gemini|gpt` for single-model fallback,
  `--quick` DeepSeek only when user explicitly requests. Lighter than feat-discuss: no
  Handshake, no mandatory filing. Trigger when the user says "think", "想想", "深入思考",
  "换个角度", "有没有更好的思路", "challenge this", "问问 Gemini 怎么看", "问问 GPT 怎么看",
  or when Claude Code needs external perspective on strategy/methodology before escalating
  to the user. Also auto-triggers on: non-obvious strategy/architecture choices, cross-project
  tool/pattern design, workflow methodology improvements. NOT for product feature decisions
  or UI/UX design (use feat-discuss).
version: 0.5.2
---

# 轻量级 Think 协作

## 用途

让 Claude Code 主动 call 外部 AI（默认 Gemini）获取对方法论 / 策略 / 哲学 / 元认知问题的独立视角。

与 `think-gem-project` skill 的分工：本 skill 不做产品/UI决策、不走 Handshake、不强制落库——快进快出、只为打破单一视角。

**前提**：外部 AI 是无状态的。每次 API 调用都是全新对话，所有上下文必须在 Prompt 里显式提供。

## 模式

- **默认：Dual**——同时并发调用 **Gemini + GPT-5.4**，两路独立回复后由 Claude Code 做"模型判优 + 综合 Digest"。Gemini 多模态与横向联想占优，GPT-5.4 逻辑链深度占优，两者相互压 bias。
- **`--solo gemini`**——仅用 Gemini（需要多模态且不想花 GPT tokens）
- **`--solo gpt`**——仅用 GPT-5.4（纯文本逻辑推演，跳过多模态链路）
- **`--quick` (DeepSeek)**——只在用户显式要求（"用 deepseek 想想"、"quick think"）时使用；不支持图片、无判优步骤

### 何时降级到 solo

Dual 默认带 ~2x token 成本。以下场景可降级：

- **Turn 2+ 的追问**：首轮 dual 已建立两方立场，后续追问若只需沿某一方深入，用 `--solo` 对应方向即可
- **纯信息查询**：不需要外部视角的简单事实性问题（但此类问题通常根本不该 call think）
- **多模态独占**：`--quick` 不支持图片；带图讨论且不需要 GPT 逻辑比对时可 `--solo gemini`

## 与 think-gem-project 的关系

Think 是从 `think-gem-project` 拆分出的轻量子集：

| 维度 | think-gem-project | think (本 skill) |
|------|-------------------|------------------|
| **角色范围** | product + design + game-product + game-design | 仅方法论/策略/哲学 |
| **流程** | Context → Prompt → Handshake → 落库 | Context → Prompt → 展示 → 可选落库 |
| **Handshake** | product/design 必须 | 无 |
| **落库** | 强制（Feature Brief） | 可选（仅产出可执行决策时） |
| **上下文来源** | 项目文档（PRODUCT_SOUL 等） | Claude Code 自身的分析 |
| **适用场景** | 产品功能、UI/UX、架构决策 | 方法论、策略、哲学、元认知 |

如果讨论中发现需要产品/设计层面的深入讨论，切换到 `think-gem-project`。

## 触发条件

### 手动触发

用户说 "think"、"想想"、"深入思考"、"换个角度"、"有没有更好的思路"、"问问 Gemini 怎么看"、"challenge this"、"跟 Gemini 聊聊这个思路"、"找 Gemini 挑战一下"。

### 自动触发（命中任一硬信号 → 必须 call）

Claude Code 主动 call Gemini 的**唯一**标准。只有这 3 条，宁可漏报不留模糊语义：

- **跨项目影响**：改动会影响 ≥2 个项目的共享配置 / 工作流 / 代码
- **持久化到规则**：新工作流/方法论改进会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
- **元认知指令**：用户说"全面思考"、"深入想想"、"你怎么看"等明确请求外部视角的措辞

### 不触发（改用 think-gem-project）

- 具体产品功能的方向决策 → `think-gem-project` product
- UI/UX 设计决策 → `think-gem-project` design
- 需要 Engineering Handshake 和 Feature Brief 落库的场景

## Step 1：组装上下文（输入契约）

Think 的上下文以 **Claude Code 自己的分析和推理** 为主，而非项目文档（这是和 `feat-discuss` 的关键区别）。

### 输入契约——必选字段

Prompt 的 Context 段开头必须**显式**标注以下 3 项：

| 字段 | 要求 |
|------|------|
| **协作模式声明** | 固定一句：「这是一个 AI-Only 开发项目——AI（Claude Code）全权负责代码/测试/文档，人类是产品负责人，不写代码。请基于此前提给出建议。」 |
| **CWD 所在项目** | `<项目根路径>` 或 `无（跨项目/全局话题）` |
| **已阅读的项目文档** | 实际用 Read tool 读过的文件和行号范围，每份提炼 2-5 行关键事实到 Context 段。本次话题确实不需要读项目文档时，写 `无（跨项目/方法论话题）`；不允许"我猜"或"凭记忆" |

### 校验条件

- `CWD 所在项目 ≠ 无` 且话题涉及该项目的产品/架构/路线图时，`已阅读的项目文档` 不允许为空。为空时停下来补读 `docs/PRODUCT_SOUL.md` / `docs/ARCHITECTURE.md` / `docs/ROADMAP.md` 中相关文件。
- 项目级 `CLAUDE.md` **不得原文 prepend**——它是 Claude Code 的操作手册（curl 速查 / 脚本路径 / 文档导航），对 Gemini 是纯噪音。需要项目基线时从 `docs/` 下浓缩事实。

### 其他组装规则

- 具体数据和事实（"7 个项目, 1200 个测试"）优于体系名称（"冰山测试策略"）——后者在 Gemini 侧没有共享定义，容易被误解。
- 不要求在特定项目目录中运行——可以在任意目录讨论跨项目问题。

## Step 2：调用 think.mjs

**默认（Dual：Gemini + GPT-5.4 并发）：**

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs "<prompt>"
```

输出会以两个分隔块呈现：

```
═══ 🧠 Gemini (google/gemini-3.1-pro-preview) — 9.4s ═══
<Gemini 原文>

═══ 🤖 GPT-5.4 (openai/gpt-5.4) — 2.8s ═══
<GPT 原文>
```

某一路失败时，该块显示 `❌ ERROR` 和错误原因，另一路结果照常返回（`Promise.allSettled` 保证）。

**`--solo gemini` / `--solo gpt`，单模型 fallback：**

```bash
node think.mjs --solo gemini "<prompt>"   # 仅 Gemini
node think.mjs --solo gpt "<prompt>"      # 仅 GPT-5.4
```

**`--quick` (DeepSeek)，仅用户显式要求：**

```bash
node think.mjs --quick "<prompt>"
```

### 附带图片（多模态）

脚本自动对每张输入图做 `长边 ≤ 2048px 等比缩放 + JPEG q85 + 尊重 EXIF 方向`。Gemini 按固定 token 数计费（每图约 1120 tokens），降分辨率不省钱但能显著降低 Base64 payload 体积，省延迟避免报错。支持 JPEG/PNG/WebP/HEIC 等 sharp/libvips 能处理的格式。

**两个 flag**：

- `--image <path>` / `-i <path>`——本地图片路径（可重复）
- `--text <str>` / `-t <str>`——显式文本块，用于多图场景的交替绑定（可重复）

组装规则：flag 按 CLI 出现顺序加入 content parts；positional 尾段（引号包住的主问题）永远追加到最后。即 flag 提供"结构化前置内容"，positional 提供"主问题/总结"。

**单图**：

```bash
node think.mjs --image ~/Desktop/error.png "这个报错是什么意思？根因在哪？"
```

**多图**：必须用 `--text` 为每张图提供 caption，否则模型无法可靠区分"哪段文字描述哪张图"（注意力会被稀释）。

```bash
# ✅ 交替式（Interleaved）— 多图的唯一正确范式
node think.mjs \
  --text "方案 A（现行版本）：" --image ./a.jpg \
  --text "方案 B（提议修改，调整了阴影与材质）：" --image ./b.jpg \
  "对比两版设计，哪个更符合 Warm Ceramic 的触感与克制？给出重构方向。"
```

反例：

```bash
# ❌ 纯堆图（model 注意力稀释，无法可靠区分 A / B）
node think.mjs --image a.jpg --image b.jpg "对比 A 和 B"

# ❌ 靠序号映射（可行但比 interleaved 差，注意力收敛更慢）
node think.mjs --image a.jpg --image b.jpg "图1 是方案 A，图2 是方案 B，对比一下"
```

**成本**：每图约 1120 input tokens，4 图 ≈ 4500 tokens 纯图片成本 + 注意力稀释风险。只关心某几张图的某个细节时，在 prompt 里明确指出，避免模型浪费算力分析不相关的图。

**其他限制**：

- `--quick` (DeepSeek) 分支不支持图片，组合使用会直接报错。图片讨论必须走 Gemini。
- 图片路径解析相对当前工作目录（CWD），不是 think.mjs 所在目录。
- 何时传图：截图里的报错信息、UI/UX 对比、架构图审视、设计稿评审。纯文本讨论不要加噪音。

### 首轮 Prompt 格式

```
## Context

> 协作模式：AI-Only 开发。AI（Claude Code）全权负责代码/测试/文档维护，人类是产品负责人，不写代码。所有工作流中不存在人类程序员介入。

{Claude Code 的分析和当前思考；严格遵守 Step 1 输入契约}

## Crux
{一句话终极问题：我到底在纠结什么？超过一句说明还没想清楚，不该 call think}

## The Problem
{具体问题或决策点}

## Constraints
{限制条件}

## 事前验尸
{如果这个方案 3 个月后彻底失败，最可能的原因是什么？Claude Code 先写自己的答案，然后让 Gemini 压一次。写不出自己答案说明决策还没到 call think 的成熟度，停下来先想}

## 请你思考
请优先指出方案的盲区和最坏情况。如果你认同方案，请说明最可能被证伪的前提。具体希望你挑战/补充的维度：
{具体维度}
```

### 字段作用

- **Crux**：一句话核心纠结，防跑偏。
- **事前验尸（Pre-mortem）**：强制的反自我满足机制——先写自己的事前验尸答案，再让两路模型各自压一次（dual 模式）或单方压（solo 模式）。这是 Digest 前置审计锚（Step 3.2 回显校验）。
- **"请你思考"段的固定前缀**"请优先指出方案的盲区和最坏情况"——激活外部模型的默认批判姿态，dual 和 solo 两种模式下都必须保留，不要删除、不要软化。两路模型吃同一份 Prompt，确保对照有效。

### 多轮追问 Prompt 格式

两路模型都无记忆，多轮对话必须在 Prompt 里重建完整上下文。采用**滑动窗口**：最近 2 轮保留完整原文，更早轮次压缩为已锁定共识 bullet points。Dual 模式下两方**共用同一份 Prompt**（含彼此上轮回复），这样两方都能看到对方观点并相互挑战。

```
## Context
{与首轮相同 -- 每轮重传，不可省略}

## Constraints
{与首轮相同}

## 对话历史

### 已锁定共识 (Locked Consensus)
{早期轮次（第 1 ~ N-2 轮）压缩为 bullet points:}
- 共识 1: ...（如 dual 模式下两方都同意）
- 共识 2: ...（单方主张被另一方采纳）
- 放弃方案: ... (原因: ...)

### 第 N-1 轮 (完整保留)
#### 问题
{完整问题}
#### 🧠 Gemini 回复
{完整回复}
#### 🤖 GPT-5.4 回复
{完整回复 — solo 模式下删除这个分块}
#### Claude Code 判优与反馈
{Claude Code 本轮判优结果 + 分歧/补充}

### 第 N 轮 (完整保留)
#### 问题 / 🧠 Gemini 回复 / 🤖 GPT-5.4 回复 / Claude Code 判优与反馈
{同上}

## 本轮问题
{本轮的具体追问/分歧/新需求}
```

**多轮传递原则：**

1. Context 和 Constraints 每轮必须重传
2. 滑动窗口：最近 2 轮保留完整，更早轮次压缩为已锁定共识
3. 已锁定共识三要素：已达成的共识、已放弃的方案及原因、未解决的遗留问题
4. Claude Code 判优与反馈必须保留——让两方模型理解"Claude 上轮判谁赢、为什么" + "为什么要追问"。Dual 下这段天然起到**让输家看到评语**的效果，逼迫两方在下一轮都提高质量

## Step 3：消化模型回复（输出契约：Digest）

### 3.1 展示双方原文

完整展示两路原文给用户，不截断、不总结。Dual 模式下两块分隔符原样保留（`═══ 🧠 Gemini ... ═══` / `═══ 🤖 GPT-5.4 ... ═══`）。Solo 或 `--quick` 只展示单路。

单路失败（`Promise.allSettled` 标 ❌）不算整体失败：在 Digest 里明确标注"X 路失败，本轮仅基于 Y 方主张"，继续完成判优与决策。若两路同时失败才报错退出。

### 3.2 输出 Digest

Digest 是本 skill 的输出契约，固定 5 字段 Markdown 结构：

**Dual 模式模板（默认）：**

```markdown
### 🧠 Think Digest

- **[我的事前验尸]**: <Claude Code 在 call think **之前**写的事前验尸答案，原文回显>
- **[Gemini 核心主张]**: <Gemini 核心结论，≤100 字，可多句但围绕同一论点；禁止列事项清单或塞入战术细节>
- **[GPT-5.4 核心主张]**: <GPT-5.4 核心结论，≤100 字，可多句但围绕同一论点；禁止列事项清单或塞入战术细节>
- **[模型判优]**: Gemini 胜 | GPT 胜 | 互补并采 | 两败俱伤 —— <≤60 字说明在本题上哪方更有用、判据是什么（推理深度 / 具体性 / 盲区识别 / 多模态…）>
- **[我的立场]**: 采信 | 反驳 | 升级
- **[立场依据]**: <1-2 句话，基于上述判优后，我为什么采信 / 反驳 / 升级>
- **[下一步行动]**: <具体的第一步指令，或 "仅记录，无动作"。引用编号（如 R1/BUG-2）必须紧跟一句话注释该编号指代>
```

**Solo / `--quick` 单路模板：**

与 dual 模板相同，但只保留一个"核心主张"字段，并删除 `[模型判优]` 字段（单路无可判优）。

### 校验条件（不满足 = skill 违反）

- Dual 模式 7 字段齐全，Solo/Quick 模式 5 字段齐全；字段名与上方结构字符串相等。
- `[我的事前验尸]` 的内容 = Step 2 首轮 Prompt 里"事前验尸"字段的原文（允许格式微调，语义和主要措辞必须一致）。这是检测仪式性咨询的唯一锚——Claude 在看完模型回复后回填这个字段 = 作弊。
- `[模型判优]` ∈ `{Gemini 胜, GPT 胜, 互补并采, 两败俱伤}`。禁止"都挺好"、"各有优劣"这类回避式措辞——这是一个强制判断题，逼 Claude Code 把"两者对比"变成显式观察。
- `[我的立场]` ∈ `{采信, 反驳, 升级}`，不允许其他值或复合值。
- **自包含规则**：Digest 必须能脱离模型原文独立读懂。引用 `R1/BUG-3/Issue-N` 等外部编号时，必须在同一字段内用一句话注明该编号指代（例："R5 = 批量已读功能"）。
- **核心主张长度**：Gemini/GPT-5.4 核心主张字段各 ≤100 字。超出 = Claude Code 在这里囤积战术细节——那些应下沉到 `[下一步行动]` 或升级模板的"选项"里。可多句、可折中措辞，但必须围绕**一个中心论点**；出现"另外/并且/同时还建议"等并列承接词 = 多论点信号，拆。
- **事前验尸被证伪时必须降级**（新增）：如果两路模型里任一路明确指出事前验尸包含**事实错误**（算术、数据、命名、时效），`[立场依据]` 必须显式标注"事前验尸 P<x> 被纠正，原排序置信度降级"，不允许沉默带过——否则 Founder 会误用已被证伪的 P 级排序做决策权重。这是事前验尸作为"反自我满足锚"的完整性前提。

### 3.2.5 模型判优（Dual 专属）

Claude Code 担任 judge，基于以下维度对比两路回复（不是全维度都给分，挑本题最相关的 1-2 维）：

| 维度 | 看点 |
|------|------|
| **推理深度** | 是否追问到第一性原理，或停留在表层 |
| **盲区识别** | 是否点出我事前验尸没想到的失败模式 |
| **具体性** | 是否给出可执行判据，还是空洞的大词堆砌 |
| **反直觉检验** | 是否主动寻找反面论据，而非附和 |
| **多模态理解**（带图时）| 是否真的看懂图，还是在对文字提示发挥 |
| **时效性** | 是否引用过时/编造的事实 |

"互补并采"不是偷懒选项——只有两路**指向不同维度**且**同时有价值**时才用（例："Gemini 指出 UX 风险，GPT-5.4 指出架构债"）。两路只是措辞不同、观点相同时，必须挑一方"胜"。

### 3.2.6 多轮追问中的双方上下文

多轮追问时，Prompt 的"对话历史"段必须同时保留两路前轮回复（按 `#### Gemini 第 N-1 轮 / #### GPT-5.4 第 N-1 轮` 分块）。这样两方都能看到对方上轮观点并互相挑战，dual 的价值在多轮中会放大。

### 3 个立场的后续动作

| 立场 | 使用场景 | 必须伴随的动作 |
|------|---------|---------------|
| **采信** | 完全采信 Gemini 主张 | 立即执行下一步行动。3.3 升级 路由条件命中时禁用此分支 |
| **反驳** | Gemini 的前提/事实/逻辑有问题 | 立即发起 Turn 2（按多轮格式重调 think.mjs），不允许单方面推翻 Gemini 后继续原方案 |
| **升级** | 战略分歧 / 影响太大 / 触发 3.3 路由 | 按 3.3.2 路由分叉决定动作——**交互模式对话内直接展示**，**自主模式落库 `to-discuss.md`** |

### 3.3 升级 强制路由

#### 3.3.1 命中条件

命中以下任一条件，`[我的立场]` 禁止填 `采信`，必须填 `升级`：

1. 决策影响持续时间 ≥1 天的工作
2. 决策会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
3. 决策会修改产品灵魂层面的规则（PRODUCT_SOUL / 设计语言 / 核心交互）
4. 决策会引入新的重型依赖或架构级变更

无弹性、无解释空间——由可机械校验的条件命中触发。

#### 3.3.2 会话类型分叉（决定"展示"还是"落库"）

| 会话类型 | 判据 | 升级动作 |
|---------|------|---------|
| **交互模式** | 当前有用户 prompt 等待回复（正常对话会话） | **直接在对话里展示 3.4 模板内容**，让用户当场勾选决策选项。用户明确"先挂起来"或无法当场决定时，才落库 `to-discuss.md` |
| **自主模式** | 无用户 prompt（`/loop`、cron、batch 自主执行） | 直接写入项目根 `to-discuss.md`（模板见 3.4），排入 Last-Resort Queue 等待 Founder 下次会话处理 |

默认判据：如果不确定当前是否交互模式，按交互模式处理（用户在现场的代价远低于让用户事后翻队列）。

#### 3.3.3 Digest 与升级模板的分工（避免双重展开）

**一旦 `[我的立场] = 升级`，Digest 必须收缩为"身份证"模式**，由升级模板承担主体展示。否则 Founder 会读到两次同样的概括——核心主张、判优、立场都被重复一遍。

| 字段 | 升级模式下的处理 |
|------|-----------------|
| `[我的事前验尸]` | 保留原文回显（这是 skill 反仪式性锚，不可省） |
| `[Gemini 核心主张]` | **保留≤100字主张**；具体战术细节下沉到升级模板的"选项"段 |
| `[GPT-5.4 核心主张]` | 同上 |
| `[模型判优]` | 保留判优 + 判据（身份证核心） |
| `[我的立场]` | 填"升级" |
| `[立场依据]` | **保留**，说明触发 3.3.1 哪条 |
| `[下一步行动]` | 收缩为一句话："见下方升级模板，Founder 勾选"，具体选项不在此展开 |

升级模板里**不要再重复** Gemini 核心主张 / GPT 核心主张 / 模型判优字段——Digest 已经有了。升级模板聚焦于 Founder 的决策工作：事实前提 + 选项 A/B/C + 反面检验 + 决策勾选框。

```markdown
## [策略|方法论|工作流] 简短标题 (Ref: think 讨论 YYYY-MM-DD)
- **事实前提**: [讨论基于的客观现状 — 自主模式落库时必填；交互模式下 Founder 已在对话现场，可省略或精简]
- **选项 A**: [方案 A + 两方倾向标注（如 "Gemini 倾向 A / GPT-5.4 倾向 B"）]
- **选项 B**: [方案 B + 理由]
- **选项 C**（可选，≤4 项）: [方案 C + 理由]
- **反面检验**: [各方案的事前验尸级分析]
- **Claude Code 综合推荐**: 采纳 <A|B|C|D> —— [≤100 字：三方（事前验尸 + Gemini + GPT-5.4）整合后我为什么推荐这个；选它你会得到什么、失去什么；为什么不是最接近的替代 Y]
- **决策选项**:
  - [ ] 采纳 A → 落库为规则/更新 skill
  - [ ] 采纳 B → 同上
  - [ ] 采纳 C → 同上
  - [ ] 再议 → 再次 /think 深入追问
  - [ ] 驳回 → 维持现状
```

**选项互斥性约束**：

- 选项总数 ≤4 项（A/B/C/D），禁止超过
- 选项必须**两两互斥**：选 A 不能自动包含 B 的子集；"组合 A+B 部分"不单列为独立选项，若确实需要折中，把折中组合作为新的独立选项 C（要素明确列出）
- 选项粒度**对等**：不允许"全套方案 A / A 的一个子步骤 / A 的重型版"这种嵌套关系——Founder 读时会陷入包含关系判断
- 若四个选项仍不够，用"再议"分流到下一轮 /think，不要继续膨胀选项数

**`[Claude Code 综合推荐]` 字段强制要求**：

- **必须明确指向一个具体选项**（A/B/C/D 之一），不允许"看情况"、"看 Founder 偏好"、"视实测结果"等回避措辞——三方 AI（事前验尸 + Gemini + GPT-5.4）判断都沉淀好了，Claude Code 就是 synthesizer，拒绝推荐 = 工作没做完
- **必须包含反面对比**：不只说"选 X 的理由"，还要说"为什么不是最接近的替代 Y"——这是对 Founder 决策权的尊重，让他看到权衡而不是单向推销
- **不允许"组合推荐"**（"推荐 A 但也做一点 B"）：互斥性约束已保证选项不重叠，推荐就是挑一个
- **长度 ≤100 字**：与核心主张字段对齐；过长 = 没想清楚，停下来压缩

**为什么不重复核心主张字段**：升级模板触发时 Digest 已经展示了两方主张+判优（3.3.3 身份证模式），此模板只聚焦 Founder 的决策工作（事实 → 选项 → 推荐 → 勾选）。

### 3.5 反仪式性咨询自检

Digest 输出后，Claude Code 自问：

> 如果去掉这次 call think 的整个过程，我的下一步行动会不会改变？

- **不会改变** → 本次 call think 是仪式性咨询（走过场），在 `[立场依据]` 里诚实标注 `[低价值 call - 下次类似场景应跳过]`
- **会改变** → 产生了真实决策影响，有效调用

累计 3 次以上"低价值 call"，主动上报 Founder 重新评估触发条件——防止 call think 退化为装饰性步骤。

## Prompt 组装原则

1. **描述事实，不描述体系**——"我们有 1178 个单元测试" 比 "冰山模式测试策略" 更不容易被误解。
2. **Gemini 需要理解背景，不是评价体系**——提供上下文，不是要它审核内部流程。
3. **标注触发方式**——提到工具/流程时说清楚是"手动按需"还是"自动触发"。
4. **手段 ≠ 目的**——传递产品原则时附带：「以上原则关注用户体验的结果，不是实现机制。」当 Gemini 用美学类比论证时（"徕卡不会这样做"），Claude Code 还原为因果链审视，因果断裂则抛弃。当用户与 AI 有不同观点时，Prompt 里平等呈现双方方案。

## 沟通规范

- Claude Code 发给 Gemini 的 Prompt：中文描述 + 英文术语
- Gemini 回复：已配置为中文描述 + 英文术语
- Claude Code 展示给用户：Gemini 原文 + Claude Code 补充判断（Digest）

## 约束

- 不写业务代码，只产出洞察和建议
- Gemini 的回复是参考意见，不是指令——Claude Code 独立判断
- 脚本路径固定：`~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`
- 脚本执行失败时向用户报告错误，建议检查 `.env` 配置

## 变更历史

- 0.5.2 (2026-04-18)：升级模板新增 `[Claude Code 综合推荐]` 必填字段——Claude Code 必须明确推荐一个选项（三方 AI 视角 synthesizer），含反面对比且 ≤100 字；禁止回避措辞 / 组合推荐。避免把 AI 已经沉淀的判断丢回 Founder 的决策负担。详见 `~/.claude/docs/decisions/2026-04-18-04-think-skill-synthesis-recommendation.md`
- 0.5.1 (2026-04-18)：基于 0.5.0 首次真实运行（flametree_ai 音频架构讨论）的观察改进。放宽核心主张长度为 ≤100 字可多句（原"一句话"过严）；新增"核心主张长度"校验条件；新增"事前验尸被证伪时立场依据必须降级"条款（Founder 会误用已证伪的 P 级排序做决策权重）；新增 3.3.3 Digest 与升级模板的分工规则（升级模式下 Digest 收缩为身份证、升级模板不再重复核心主张避免双重展开）；升级模板加入选项互斥性约束（≤4 项、两两互斥、粒度对等、不列子集/组合变体）。详见 `~/.claude/docs/decisions/2026-04-18-03-think-skill-digest-tightening.md`
- 0.5.0 (2026-04-18)：默认切到 DUAL 模式——Gemini + GPT-5.4 并发调用，Claude Code 担任 judge 做模型判优；新增 `--solo gemini|gpt` 单模型 fallback；Digest 新增 `[GPT-5.4 核心主张]` + `[模型判优]` 字段；多轮追问 Prompt 保留两方上轮回复让彼此互相挑战；升级模板加入两方主张与判优字段。详见 `~/.claude/docs/decisions/2026-04-18-02-think-skill-dual-gemini-gpt.md`
- 0.4.0 (2026-04-18)：术语中文化（`Failure_Premise → 事前验尸`；`Accept/Refute/Escalate → 采信/反驳/升级`；`Approve/Discuss/Reject → 采纳/再议/驳回`）；新增 Digest 自包含规则；升级路由按会话类型分叉（交互模式对话展示、自主模式落库）。详见 `~/.claude/docs/decisions/2026-04-18-01-think-skill-chinese-terms-and-interactive-escalate.md`
- 本 skill 的版本回退逻辑（曾经尝试过但被移除的字段/分支/触发条件）保留在 `~/.claude/docs/decisions/2026-04-13-04-think-skill-contract-refactor.md` 第 5 节。再次提议引入已回退字段前先读该文档。
