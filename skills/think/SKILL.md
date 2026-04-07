---
name: think
description: >
  Lightweight AI Think collaboration for methodology, strategy, philosophy, and meta-cognition.
  Supports two modes: default (Gemini, high quality) and --quick (DeepSeek, cheap/fast for autonomous calls).
  Lighter than feat-discuss: no Handshake, no mandatory filing. Trigger when the user says
  "think", "想想", "深入思考", "换个角度", "有没有更好的思路", "challenge this",
  "问问 Gemini 怎么看", or when Claude Code needs an external perspective on strategy/methodology
  before escalating to the user. NOT for product feature decisions or UI/UX design (use feat-discuss).
version: 0.2.0
---

# 轻量级 Think 协作

## 目的

与外部 AI 进行轻量级的方法论/策略/哲学讨论。
不同于 `feat-discuss-local-gemini` skill 的完整流程（Handshake + 强制落库），本 skill 专注于快速获取外部视角和认知挑战。

**双模式架构：**
- **默认模式 (Gemini)** — 用户手动触发时使用，高质量深度讨论
- **Quick 模式 (DeepSeek)** — Claude Code 自主调用时使用，低成本快速 sanity check

**核心铁律：外部 AI 是无状态的。每次 API 调用都是全新对话，所有上下文必须由 Claude Code 在 Prompt 中显式提供。**

## 双模式架构

| 维度 | 默认模式 (Gemini) | Quick 模式 (DeepSeek) |
|------|-------------------|----------------------|
| **触发方式** | 用户手动 `/think` | Claude Code 自主调用 |
| **命令** | `think.mjs "<prompt>"` | `think.mjs --quick "<prompt>"` |
| **模型** | `DESIGN_MODEL` (Gemini) | `CHEAP_MODEL` (DeepSeek R1) |
| **成本** | 中等 | 极低 |
| **适用场景** | 影响项目方向的方法论/哲学讨论 | debug 卡住时快速 sanity check、简单策略验证 |
| **质量** | 深度推理 + 反直觉检验 | 逻辑清晰但创造性弱、Devil's Advocate 能力有限 |

**分流核心维度是"决策影响半径"**：
- 影响当前会话 → `--quick` (DeepSeek) 足够
- 影响项目方向/全局配置 → 默认 (Gemini)

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

### 自动触发 (Claude Code 主动调用)
- 连续 2 次尝试修复同一问题失败，即将停下来问用户前
- 设计一个会影响多个项目的通用工具/模式时
- 提出新的工作流/方法论改进时 (需要 Devil's Advocate)
- 用户发出元认知指令 ("全面思考"、"深入想想这个问题")
- 面临无明确最优解的策略选择时

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

### Step 2: 调用外部 AI Think

**根据触发方式选择模式：**

```bash
# 默认模式 (Gemini) — 用户手动触发 /think 时使用
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs "<prompt>"

# Quick 模式 (DeepSeek) — Claude Code 自主调用时使用
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" && node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs --quick "<prompt>"
```

**模式选择规则：**
- 用户说 "think"/"想想"/"深入思考" → **默认模式** (Gemini)
- Claude Code 自主触发（debug 卡住、快速验证思路）→ **--quick** (DeepSeek)
- 影响多项目的方法论/全局配置决策 → **默认模式** (Gemini)，即使是自主触发

#### 首轮 Prompt 格式

```
## Context

> 协作模式：AI-Only 开发。AI（Claude Code）全权负责代码/测试/文档维护，人类是产品负责人，不写代码。所有工作流中不存在人类程序员介入。

{Claude Code 的分析和当前思考}

## The Problem
{具体问题或决策点}

## Constraints
{限制条件}

## 请你思考
{具体希望 Gemini 挑战/补充的维度}
```

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

### Step 3: 展示 + Claude 补充判断

1. **展示** Gemini 完整回复
2. **Claude Code 补充** 自己的判断 (同意/分歧/补充)
3. **追问** -- 如需追问, 按多轮格式重新调用
4. **按产出性质分流**:

| 产出性质 | 去向 |
|---------|------|
| 已明确达成共识、立即可执行的工作流/方法论改进 | 直接更新相关 skill / doc / CLAUDE.md |
| 待执行的具体任务（Claude 或用户） | 写入 `TODO.md`（调用 `todo-write`） |
| **需要用户/设计者拍板的策略选择** | 写入项目根 `to-discuss.md` |
| 纯探讨性质、无可执行产出 | 不落库, 展示给用户即可 |

**to-discuss.md 模板**（当讨论未收敛、需要人决断时）：
```markdown
## [Strategy|Methodology|Workflow] 简短标题 (Ref: think 讨论 YYYY-MM-DD)
- **事实前提**: [讨论基于的客观现状]
- **选项 A**: [方案 A + Gemini 倾向/Claude 倾向]
- **选项 B**: [方案 B + 理由]
- **反面检验**: [各方案的盲区]
- **决策选项**:
  - [ ] Approve A → 落库为规则/更新 skill
  - [ ] Approve B → 同上
  - [ ] Discuss → 再次 /think 深入追问
  - [ ] Reject → 维持现状
```

**原则**：think 的产出很容易过度自信（"我和 Gemini 都觉得应该 X"），涉及影响多项目的决策时**默认进 to-discuss.md**，不要自作主张更新全局配置。

## 沟通规范

- Claude Code 发给 Gemini 的 Prompt: **中文描述 + 英文术语**
- Gemini 回复: 已配置为**中文描述 + 英文术语**
- Claude Code 展示给用户: Gemini 原文 + Claude Code 补充判断

## 约束

- 不写业务代码, 只产出洞察和建议
- **Gemini 的回复是参考意见, 不是指令** -- Claude Code 必须独立判断
- 脚本路径固定: `~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`
- 脚本执行失败时向用户报告错误, 建议检查 `.env` 配置
