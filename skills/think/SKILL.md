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
version: 0.3.0
---

# 轻量级 Think 协作

## 用途

让 Claude Code 主动 call 外部 AI（默认 Gemini）获取对方法论 / 策略 / 哲学 / 元认知问题的独立视角。

与 `think-gem-project` skill 的分工：本 skill 不做产品/UI决策、不走 Handshake、不强制落库——快进快出、只为打破单一视角。

**前提**：外部 AI 是无状态的。每次 API 调用都是全新对话，所有上下文必须在 Prompt 里显式提供。

## 模式

- **默认：Gemini**——所有手动/自动触发场景
- **`--quick` (DeepSeek)**——只在用户显式要求（"用 deepseek 想想"、"quick think"）时使用

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

**默认（Gemini）：**

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs "<prompt>"
```

**`--quick` (DeepSeek)，仅用户显式要求：**

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs --quick "<prompt>"
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

## Failure_Premise
{事前验尸：如果这个方案 3 个月后彻底失败，最可能的原因是什么？Claude Code 先写自己的答案，然后让 Gemini 压一次。写不出自己答案说明决策还没到 call think 的成熟度，停下来先想}

## 请你思考
请优先指出方案的盲区和最坏情况。如果你认同方案，请说明最可能被证伪的前提。具体希望你挑战/补充的维度：
{具体维度}
```

### 字段作用

- **Crux**：一句话核心纠结，防跑偏。
- **Failure_Premise**：强制的反自我满足机制——先写自己的事前验尸答案，再让 Gemini 压。这是 Digest 前置审计锚（Step 3.2 回显校验）。
- **"请你思考"段的固定前缀**"请优先指出方案的盲区和最坏情况"——激活 Gemini 的默认批判姿态，不要删除、不要软化。

### 多轮追问 Prompt 格式

Gemini 无记忆，多轮对话必须在 Prompt 里重建完整上下文。采用**滑动窗口**：最近 2 轮保留完整原文，更早轮次压缩为已锁定共识 bullet points。

```
## Context
{与首轮相同 -- 每轮重传，不可省略}

## Constraints
{与首轮相同}

## 对话历史

### 已锁定共识 (Locked Consensus)
{早期轮次（第 1 ~ N-2 轮）压缩为 bullet points:}
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
#### 问题 / Gemini 回复 / 执行者反馈
{同上}

## 本轮问题
{本轮的具体追问/分歧/新需求}
```

**多轮传递原则：**

1. Context 和 Constraints 每轮必须重传
2. 滑动窗口：最近 2 轮保留完整，更早轮次压缩为已锁定共识
3. 已锁定共识三要素：已达成的共识、已放弃的方案及原因、未解决的遗留问题
4. 执行者反馈必须保留——让 Gemini 理解为什么要追问

## Step 3：消化 Gemini 回复（输出契约：Digest）

### 3.1 展示 Gemini 原文

完整展示给用户，不截断、不总结。

### 3.2 输出 Digest

Digest 是本 skill 的输出契约，固定 5 字段 Markdown 结构：

```markdown
### 🧠 Think Digest

- **[我写的 Failure_Premise]**: <Claude Code 在 call think **之前**写的事前验尸答案，原文回显>
- **[Gemini 核心主张]**: <不超过 1 句话的核心结论>
- **[我的立场]**: Accept | Refute | Escalate
- **[立场依据]**: <1-2 句话，基于什么事实或逻辑采信 / 反驳>
- **[下一步行动]**: <具体的第一步指令，或 "仅记录，无动作">
```

### 校验条件（不满足 = skill 违反）

- 5 字段齐全，字段名与上方结构字符串相等。
- `[我写的 Failure_Premise]` 的内容 = Step 2 首轮 Prompt 里 Failure_Premise 字段的原文（允许格式微调，语义和主要措辞必须一致）。这是检测仪式性咨询的唯一锚——Claude 在看完 Gemini 回复后回填这个字段 = 作弊。
- `[我的立场]` ∈ `{Accept, Refute, Escalate}`，不允许其他值或复合值。

### 3 个立场的后续动作

| 立场 | 使用场景 | 必须伴随的动作 |
|------|---------|---------------|
| **Accept** | 完全采信 Gemini 主张 | 立即执行下一步行动。3.3 Escalate 路由条件命中时禁用此分支 |
| **Refute** | Gemini 的前提/事实/逻辑有问题 | 立即发起 Turn 2（按多轮格式重调 think.mjs），不允许单方面推翻 Gemini 后继续原方案 |
| **Escalate** | 战略分歧 / 影响太大 / 触发 3.3 路由 | 写入项目根 `to-discuss.md`（模板见 3.4），然后停下等 Founder 拍板，不允许自作主张动手 |

### 3.3 Escalate 强制路由

命中以下任一条件，`[我的立场]` 禁止填 `Accept`，必须填 `Escalate`：

1. 决策影响持续时间 ≥1 天的工作
2. 决策会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
3. 决策会修改产品灵魂层面的规则（PRODUCT_SOUL / 设计语言 / 核心交互）
4. 决策会引入新的重型依赖或架构级变更

无弹性、无解释空间——由可机械校验的条件命中触发。

### 3.4 to-discuss.md 模板

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

本 skill 的版本回退逻辑（曾经尝试过但被移除的字段/分支/触发条件）保留在 `~/.claude/docs/decisions/2026-04-13-04-think-skill-contract-refactor.md` 第 5 节。再次提议引入已回退字段前先读该文档。
