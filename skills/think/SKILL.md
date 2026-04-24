---
name: think
description: >
  Lightweight AI Think collaboration for methodology, strategy, philosophy, and meta-cognition.
  Defaults to SOLO mode: Claude Code picks `--solo gemini` (multimodal/lateral) or `--solo gpt`
  (logic-heavy) based on topic. `--dual` explicitly when the topic truly needs two-model
  contention. `--quick` DeepSeek only when user explicitly requests. Lighter than feat-discuss:
  no Handshake, no mandatory filing. Trigger when the user says "think", "想想", "深入思考",
  "换个角度", "有没有更好的思路", "challenge this", "问问 Gemini 怎么看", "问问 GPT 怎么看",
  or when Claude Code needs external perspective on strategy/methodology before escalating
  to the user. Also auto-triggers on: non-obvious strategy/architecture choices, cross-project
  tool/pattern design, workflow methodology improvements. NOT for product feature decisions
  or UI/UX design (use feat-discuss).
version: 0.6.0
---

# 轻量级 Think 协作

## 用途

让 Claude Code 主动 call 外部 AI 获取对方法论 / 策略 / 哲学 / 元认知问题的独立视角。

与 `think-gem-project` skill 的分工:本 skill 不做产品/UI决策、不走 Handshake、不强制落库——快进快出、只为打破单一视角。

**前提**:外部 AI 是无状态的。每次 API 调用都是全新对话,所有上下文必须在 Prompt 里显式提供。

## 模式与选择逻辑

默认跑 Solo(单模型),由 Claude Code 按话题性质选一方。Dual 作为显式可选路径。

| 模式 | 用法 | 何时选 |
|------|------|--------|
| **`--solo gpt`** | `node think.mjs --solo gpt "<prompt>"` | 偏逻辑推演 / 战略分析 / 算法设计 / 纯文本推理 |
| **`--solo gemini`** | `node think.mjs --solo gemini "<prompt>"` | 需多模态(图片) / 横向联想 / 开放探索 / 无明确倾向时的兜底 |
| **`--dual`** | `node think.mjs --dual "<prompt>"` | **真**有策略分歧 / 影响极广 / 需双方对抗;成本 2x,详细规则见 `skills/think/ADVANCED.md` |
| **`--quick`** | `node think.mjs --quick "<prompt>"` | 用户显式要求("用 deepseek 想想"、"quick think");不支持图片、无判优步骤 |

**选择纪律**:首轮就做分类判断,不要习惯性 `--dual`。Gemini 多模态/横向联想占优,GPT-5.4 逻辑链深度占优。无明确倾向默认 `--solo gemini`(多模态兜底更通用)。

## 与 think-gem-project 的关系

Think 是从 `think-gem-project` 拆分出的轻量子集:

| 维度 | think-gem-project | think (本 skill) |
|------|-------------------|------------------|
| **角色范围** | product + design + game-product + game-design | 仅方法论/策略/哲学 |
| **流程** | Context → Prompt → Handshake → 落库 | Context → Prompt → 展示 → 可选落库 |
| **Handshake** | product/design 必须 | 无 |
| **落库** | 强制(Feature Brief) | 可选(仅产出可执行决策时) |
| **上下文来源** | 项目文档(PRODUCT_SOUL 等) | Claude Code 自身的分析 |
| **适用场景** | 产品功能、UI/UX、架构决策 | 方法论、策略、哲学、元认知 |

如果讨论中发现需要产品/设计层面的深入讨论,切换到 `think-gem-project`。

## 触发条件

### 手动触发

用户说 "think"、"想想"、"深入思考"、"换个角度"、"有没有更好的思路"、"问问 Gemini 怎么看"、"challenge this"、"跟 Gemini 聊聊这个思路"、"找 Gemini 挑战一下"。

### 自动触发(命中任一硬信号 → 必须 call)

Claude Code 主动 call Gemini 的**唯一**标准。只有这 3 条,宁可漏报不留模糊语义:

- **跨项目影响**:**当前改动直接修改** ≥2 个项目可读取的文件(共享 skill / 全局 CLAUDE.md / 跨项目 doc / shared 工具脚本)。仅"思路会被借鉴"、"未来可能影响"不算(那属于触发条件 2 或 3 的覆盖范围)
- **持久化到规则**:新工作流/方法论改进会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
- **元认知指令**:用户说"全面思考"、"深入想想"、"你怎么看"等明确请求外部视角的措辞

### 不触发(改用 think-gem-project)

- 具体产品功能的方向决策 → `think-gem-project` product
- UI/UX 设计决策 → `think-gem-project` design
- 需要 Engineering Handshake 和 Feature Brief 落库的场景

## Step 1:组装上下文(输入契约)

Think 的上下文以 **Claude Code 自己的分析和推理** 为主,而非项目文档(这是和 `feat-discuss` 的关键区别)。

### 输入契约——必选字段

Prompt 的 Context 段开头必须**显式**标注以下 3 项:

| 字段 | 要求 |
|------|------|
| **协作模式声明** | 固定一句:「这是一个 AI-Only 开发项目——AI(Claude Code)全权负责代码/测试/文档,人类是产品负责人,不写代码。请基于此前提给出建议。」 |
| **CWD 所在项目** | `<项目根路径>` 或 `无(跨项目/全局话题)` |
| **已阅读的项目文档** | 实际用 Read tool 读过的文件和行号范围,每份提炼 2-5 行关键事实到 Context 段。本次话题确实不需要读项目文档时,写 `无(跨项目/方法论话题)`;不允许"我猜"或"凭记忆" |

### 校验条件

- `CWD 所在项目 ≠ 无` 且话题涉及该项目的产品/架构/路线图时,`已阅读的项目文档` 不允许为空。为空时停下来补读 `docs/PRODUCT_SOUL.md` / `docs/ARCHITECTURE.md` / `docs/ROADMAP.md` 中相关文件。
- 项目级 `CLAUDE.md` **不得原文 prepend**——它是 Claude Code 的操作手册(curl 速查 / 脚本路径 / 文档导航),对 Gemini 是纯噪音。需要项目基线时从 `docs/` 下浓缩事实。

### 其他组装规则

- 具体数据和事实("7 个项目, 1200 个测试")优于体系名称("冰山测试策略")——后者在外部模型侧没有共享定义,容易被误解。
- 不要求在特定项目目录中运行——可以在任意目录讨论跨项目问题。

## Step 2:调用 think.mjs

**Solo 基础调用(默认)**:

```bash
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs --solo <gemini|gpt> "<prompt>"
```

**`--dual` / 多轮追问 / `--quick`** 的完整调用方式和 Prompt 格式详见 `skills/think/ADVANCED.md`。

### 附带图片(多模态)

脚本自动对每张输入图做 `长边 ≤ 2048px 等比缩放 + JPEG q85 + 尊重 EXIF 方向`。Gemini 按固定 token 数计费(每图约 1120 tokens),降分辨率不省钱但能显著降低 Base64 payload 体积,省延迟避免报错。支持 JPEG/PNG/WebP/HEIC 等 sharp/libvips 能处理的格式。

**两个 flag**:

- `--image <path>` / `-i <path>`——本地图片路径(可重复)
- `--text <str>` / `-t <str>`——显式文本块,用于多图场景的交替绑定(可重复)

组装规则:flag 按 CLI 出现顺序加入 content parts;positional 尾段(引号包住的主问题)永远追加到最后。

**单图**:

```bash
node think.mjs --solo gemini --image ~/Desktop/error.png "这个报错是什么意思?根因在哪?"
```

**多图**:必须用 `--text` 为每张图提供 caption,否则模型无法可靠区分"哪段文字描述哪张图"(注意力会被稀释)。

```bash
# ✅ 交替式(Interleaved)— 多图的唯一正确范式
node think.mjs --solo gemini \
  --text "方案 A(现行版本):" --image ./a.jpg \
  --text "方案 B(提议修改,调整了阴影与材质):" --image ./b.jpg \
  "对比两版设计,哪个更符合 Warm Ceramic 的触感与克制?给出重构方向。"
```

**其他限制**:

- `--quick` (DeepSeek) 分支不支持图片,组合使用会直接报错。图片讨论必须走 Gemini
- 图片路径解析相对当前工作目录(CWD),不是 think.mjs 所在目录
- 何时传图:截图里的报错信息、UI/UX 对比、架构图审视、设计稿评审。纯文本讨论不要加噪音

### 首轮 Prompt 格式

```
## Context

> 协作模式:AI-Only 开发。AI(Claude Code)全权负责代码/测试/文档维护,人类是产品负责人,不写代码。所有工作流中不存在人类程序员介入。

{Claude Code 的分析和当前思考;严格遵守 Step 1 输入契约}

## Crux
{一句话终极问题:我到底在纠结什么?超过一句说明还没想清楚,不该 call think}

## The Problem
{具体问题或决策点}

## Constraints
{限制条件}

## 事前验尸
{如果这个方案 3 个月后彻底失败,最可能的原因是什么?Claude Code 先写自己的答案,然后让外部模型压一次}

## 请你思考
请优先指出方案的盲区和最坏情况。如果你认同方案,请说明最可能被证伪的前提。具体希望你挑战/补充的维度:
{具体维度}
```

### 字段作用

- **Crux**:一句话核心纠结,防跑偏
- **事前验尸(Pre-mortem)**:强制的反自我满足机制——先写自己的事前验尸答案,再让外部模型压一次。这是 Digest 前置审计锚(Step 3.2 回显校验)
- **"请你思考"段的固定前缀**"请优先指出方案的盲区和最坏情况"——激活外部模型的默认批判姿态,不要删除、不要软化

### 事前验尸的质量下限

**要求**:至少点名一个**可证伪的前提假设**——指向具体的数据/机制/前提(如"假设 GPT 首轮延迟 ≤3s"、"假设用户能识别色板的 3% OKLCH 差异"、"假设 flametree 项目没有并发写入"),而不是泛化情绪(如"用户不喜欢"、"技术栈不适合"、"架构有问题")。

**标准**:一个前提假设是"可证伪"的,当且仅当**存在一个明确的观测或实验能让它被推翻**。列不出可证伪假设 = 决策不成熟,停下来先想,不要 call think。

这是"写出答案"之上的第二道质量门——空洞的事前验尸通过仪式齐全但推进无效,可证伪标准逼出具体性。

### 多轮追问

多轮追问的 Prompt 格式(滑动窗口 + 已锁定共识)和 Dual 模式下的两方上下文保留规则,详见 `skills/think/ADVANCED.md`。

## Step 3:消化模型回复(输出契约:Digest)

### 3.1 展示原文

完整展示模型原文给用户,不截断、不总结。

Solo 模式展示单路。Dual 模式两块分隔符原样保留(详见 ADVANCED.md)。

单路失败(`Promise.allSettled` 标 ❌)不算整体失败:在 Digest 里明确标注"X 路失败,本轮仅基于 Y 方主张",继续完成决策。若两路同时失败(Dual)才报错退出。

### 3.2 输出 Digest(Solo 模式模板)

Digest 是本 skill 的输出契约。Solo 固定 5 字段:

```markdown
### 🧠 Think Digest

- **[我的事前验尸]**: <Claude Code 在 call think **之前**写的事前验尸答案,原文回显(含可证伪前提)>
- **[外部模型核心主张]**: <模型核心结论,≤100 字,可多句但围绕同一论点;禁止列事项清单或塞入战术细节>
- **[我的立场]**: 采信 | 反驳 | 升级
- **[立场依据]**: <1-2 句话,基于上述判断,我为什么采信 / 反驳 / 升级>
- **[下一步行动]**: <具体的第一步指令,或 "仅记录,无动作"。引用编号(如 R1/BUG-2)必须紧跟一句话注释该编号指代>
```

**Dual 模式 7 字段模板**(含 `[模型判优]` + 反偏好校验)见 `skills/think/ADVANCED.md`。

### 校验条件(不满足 = skill 违反)

- Solo 模式 5 字段齐全(Dual 7 字段);字段名与上方结构字符串相等
- `[我的事前验尸]` 的内容 = Step 2 首轮 Prompt 里"事前验尸"字段的原文(允许格式微调,语义和主要措辞必须一致)。这是检测仪式性咨询的唯一锚——Claude 在看完模型回复后回填这个字段 = 作弊
- `[我的立场]` ∈ `{采信, 反驳, 升级}`,不允许其他值或复合值
- **自包含规则**:Digest 必须能脱离模型原文独立读懂。引用 `R1/BUG-3/Issue-N` 等外部编号时,必须在同一字段内用一句话注明该编号指代(例:"R5 = 批量已读功能")
- **核心主张长度**:外部模型核心主张字段 ≤100 字。超出 = 在这里囤积战术细节——那些应下沉到 `[下一步行动]` 或升级模板的"选项"里。可多句、可折中措辞,但必须围绕**一个中心论点**;出现"另外/并且/同时还建议"等并列承接词 = 多论点信号,拆
- **事前验尸被证伪时必须降级**:如果外部模型明确指出事前验尸包含**事实错误**(算术、数据、命名、时效),`[立场依据]` 必须显式标注"事前验尸包含被证伪的事实项,原判断置信度降级",不允许沉默带过——否则 Founder 会误用已被证伪的判断做决策权重。这是事前验尸作为"反自我满足锚"的完整性前提

### 3 个立场的后续动作

| 立场 | 使用场景 | 必须伴随的动作 |
|------|---------|---------------|
| **采信** | 完全采信外部模型主张 | 立即执行下一步行动。3.3 升级 路由条件命中时禁用此分支 |
| **反驳** | 外部模型的前提/事实/逻辑有问题 | 立即发起 Turn 2(按多轮格式重调 think.mjs),不允许单方面推翻外部模型后继续原方案 |
| **升级** | 战略分歧 / 影响太大 / 触发 3.3 路由 | 按 3.3.2 路由分叉决定动作——**交互模式对话内直接展示**,**自主模式落库 `to-discuss.md`** |

### 3.3 升级强制路由

#### 3.3.1 命中条件

命中以下任一条件,`[我的立场]` 禁止填 `采信`,必须填 `升级`:

1. 决策影响持续时间 ≥1 天的工作
2. 决策会持久化到 skill / 全局 CLAUDE.md / 跨项目 doc
3. 决策会修改产品灵魂层面的规则(PRODUCT_SOUL / 设计语言 / 核心交互)
4. 决策会引入新的重型依赖或架构级变更

无弹性、无解释空间——由可机械校验的条件命中触发。

#### 3.3.2 会话类型分叉(决定"展示"还是"落库")

| 会话类型 | 判据 | 升级动作 |
|---------|------|---------|
| **交互模式** | 当前有用户 prompt 等待回复(正常对话会话) | **直接在对话里展示 3.3.3 模板内容**,让用户当场勾选决策选项。用户明确"先挂起来"或无法当场决定时,才落库 `to-discuss.md` |
| **自主模式** | 无用户 prompt(`/loop`、cron、batch 自主执行) | 直接写入项目根 `to-discuss.md`(模板见 3.3.3),排入 Last-Resort Queue 等待 Founder 下次会话处理 |

默认判据:不确定时按交互模式处理(用户在现场的代价远低于让用户事后翻队列)。

#### 3.3.3 升级模板骨架

```markdown
## [策略|方法论|工作流] 简短标题 (Ref: think 讨论 YYYY-MM-DD)
- **事实前提**: [讨论基于的客观现状 — 自主模式落库时必填;交互模式下可省略或精简]
- **选项 A**: [方案 A + 理由]
- **选项 B**: [方案 B + 理由]
- **选项 C**(可选,≤4 项总): [方案 C + 理由]
- **反面检验**: [各方案的事前验尸级分析]
- **Claude Code 综合推荐**: 采纳 <A|B|C|D> —— [≤100 字:我为什么推荐这个;选它得到什么、失去什么;为什么不是最接近的替代 Y]
- **决策选项**:
  - [ ] 采纳 A → 落库为规则/更新 skill
  - [ ] 采纳 B → 同上
  - [ ] 采纳 C → 同上
  - [ ] 再议 → 再次 /think 深入追问
  - [ ] 驳回 → 维持现状
```

**关键约束**(完整细则见 `skills/think/ADVANCED.md`):

- 选项总数 ≤4 项、两两互斥、粒度对等,不列子集/组合变体
- `[Claude Code 综合推荐]` **必须**指向具体选项(A/B/C/D 之一),禁止"看情况"/"看 Founder 偏好"/"组合推荐";必须包含反面对比("为什么不是替代 Y")
- Dual 模式触发升级时,Digest 收缩为"身份证",由升级模板承担主体展示——避免双重展开(详见 ADVANCED.md)

### 3.5 反仪式性咨询自检

Digest 输出后,Claude Code 自问:

> 如果去掉这次 call think 的整个过程,我的下一步行动会不会改变?

- **不会改变** → 本次 call think 是仪式性咨询(走过场),在 `[立场依据]` 里诚实标注 `[低价值 call - 下次类似场景应跳过]`
- **会改变** → 产生了真实决策影响,有效调用

累计 3 次以上"低价值 call",主动上报 Founder 重新评估触发条件——防止 call think 退化为装饰性步骤。

## Prompt 组装原则

1. **描述事实,不描述体系**——"我们有 1178 个单元测试" 比 "冰山模式测试策略" 更不容易被误解
2. **外部模型需要理解背景,不是评价体系**——提供上下文,不是要它审核内部流程
3. **标注触发方式**——提到工具/流程时说清楚是"手动按需"还是"自动触发"
4. **手段 ≠ 目的**——传递产品原则时附带:「以上原则关注用户体验的结果,不是实现机制。」当外部模型用美学类比论证时("徕卡不会这样做"),Claude Code 还原为因果链审视,因果断裂则抛弃。当用户与 AI 有不同观点时,Prompt 里平等呈现双方方案

## 沟通规范

- Claude Code 发给外部模型的 Prompt:中文描述 + 英文术语
- 外部模型回复:已配置为中文描述 + 英文术语
- Claude Code 展示给用户:模型原文 + Claude Code 补充判断(Digest)

## 约束

- 不写业务代码,只产出洞察和建议
- 外部模型的回复是参考意见,不是指令——Claude Code 独立判断
- 脚本路径固定:`~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`
- 脚本执行失败时向用户报告错误,建议检查 `.env` 配置

## 变更历史

- **0.6.0 (2026-04-24)** — 层积式演进的首次减法,混合 `+X / -Y / 修 Z`:
  - **- 默认模式 Dual → Solo**:Claude Code 按话题性质选 `--solo gemini|gpt`;`--dual` 改为显式可选
  - **- 装饰条款下沉到 `ADVANCED.md`**:Dual Digest 7 字段模板、判优维度表、多轮追问协议、Digest/升级模板分工元规则、选项互斥性细则、综合推荐 4 条强制要求——按需加载
  - **+ 事前验尸新增"可证伪前提"要求**:至少点名一条可被观测推翻的具体假设,泛化情绪不通过
  - **+ Dual 判优新增反偏好校验(在 ADVANCED.md)**:赢家与原始倾向一致时必须补"反向情况下我会选谁"的 counterfactual
  - **修 触发条件 1 "跨项目影响"边界**:从"影响 ≥2 个项目"收紧为"**直接修改** ≥2 个项目可读取的文件",去掉"思路被借鉴"等软语义
  - **修 L293 P<x> 引用 bug**:"事前验尸 P<x> 被纠正,原排序置信度降级"改为"事前验尸包含被证伪的事实项,原判断置信度降级"——不再依赖未定义的 P 级概念
  - 详见 `~/.claude/docs/decisions/2026-04-24-04-think-skill-simplification.md`
- 0.5.2 (2026-04-18):升级模板新增 `[Claude Code 综合推荐]` 必填字段(现完整细则下沉到 ADVANCED.md)
- 0.5.1 (2026-04-18):首次真实运行观察改进——核心主张 ≤100 字、事前验尸证伪降级、3.3.3 Digest/升级模板分工、选项互斥性约束(现分工规则和互斥性细则下沉到 ADVANCED.md)
- 0.5.0 (2026-04-18):引入 DUAL 模式(Gemini + GPT-5.4 并发 + 判优),Digest 新增 `[GPT-5.4 核心主张]` + `[模型判优]` 字段(现 Dual 路径完整规则下沉到 ADVANCED.md)
- 0.4.0 (2026-04-18):术语中文化、自包含规则、升级路由按会话类型分叉
- 历史回退字段/分支/触发条件保留在 `~/.claude/docs/decisions/2026-04-13-04-think-skill-contract-refactor.md` 第 5 节。再次提议引入已回退字段前先读该文档
