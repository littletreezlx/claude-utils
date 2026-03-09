---
name: feat-discuss-local-gemini
description: >
  This skill should be used when the user wants to discuss a new feature with
  Gemini, when the user says "discuss with Gemini", "ask Gemini", "consult Gemini",
  "跟 Gemini 聊聊", "问问 Gemini", "找 Gemini 讨论", or when a feature discussion
  needs product/design input from the Gemini co-founder. Also use PROACTIVELY
  when Claude Code encounters product direction decisions, architectural trade-offs,
  or UI/UX design choices that would benefit from the Gemini co-founder's perspective
  — do not guess on product philosophy or design aesthetics, consult Gemini instead.
  Automatically calls local Gemini API, receives response, and synthesizes into
  actionable spec documents.
version: 0.4.0
---

# 与 Gemini 自动化协作 — 产品 & 设计咨询

## 目的

与 Gemini（产品合伙人 / 设计架构师）进行自动化协作。Claude Code 自动收集项目上下文、调用 Gemini API、接收回复、经过 Engineering Handshake 校验后落库为 Spec 文档。Founder 在关键节点审批。

**模式定位**：本技能是 Local API 自动模式（主力模式）。Web 手动模式（`/feat-discuss-web-gemini`）仅在用户明确要求、或需要多轮视觉反馈的重度脑暴时使用。

**核心铁律：Gemini 是无状态的。每次 API 调用都是全新对话，所有对话历史和上下文必须由 Claude Code 在 Prompt 中显式提供。对话历史的完整性是 Claude Code 的责任。**

## 触发条件

当以下信号出现时启动：
1. 用户想讨论新功能的产品方向或架构
2. 用户想咨询 UI/UX 设计建议
3. 用户明确提到"Gemini"、"产品讨论"、"设计讨论"
4. 需要产品哲学或设计架构层面的外部意见
5. **Claude Code 自主判断**（硬性触发红线）：
   - **架构级依赖**：引入涉及核心架构的依赖（路由、状态管理、网络层、本地存储、UI 组件库）→ 必须咨询
   - **数据层变更**：涉及 Drift/SQLite 表结构变更、Schema 迁移、核心 Entity 修改 → 必须咨询
   - **状态复杂度升级**：Provider 间深层依赖、跨组件通信、状态共享逻辑复杂化 → 必须咨询
   - **仪式感交互**：涉及自定义 AnimationController、Hero 动画、物理引擎交互 → 必须咨询
   - **通用组件新建**：打算创建新的可能具备通用性的 UI Widget，而非复用现有基础组件 → 必须咨询（防止设计语言碎片化）
   - 产品方向抉择、架构 trade-off
   - 不确定是否符合项目的"灵魂"（PRODUCT_SOUL）

**不触发**：
- 纯代码实现问题（Claude Code 自己能解决）
- 轻量级工具依赖（如 `path_provider`、`url_launcher`、`share_plus`）
- 用户说"提交到 Gemini Web"（→ 用 `/feat-discuss-web-gemini`）
- 没有产品影响的纯工程决策

## 执行流程

### Step 1: 选择角色 & 收集上下文

**角色判断**（根据需求自动选择）：
- `product` — 产品逻辑、架构推演、需求拷问（左脑：骨架与逻辑）
- `design` — UI/UX 决策、视觉规范、像素级解构（右脑：血肉与感官）

**上下文收集 — 动态组装策略**：

**Global 常驻（每次必带）**：
- `docs/PRODUCT_SOUL.md` — 优先读取 `## TL;DR` 摘要段（如有），避免全文塞入浪费 token。若无摘要段则传全文。

**按需上下文（根据角色和话题动态选择）**：

| 角色 / 话题 | 额外携带 | 不携带 |
|-------------|---------|--------|
| `product` — 产品方向、需求讨论 | `docs/ROADMAP.md`（当前 Epic 节点即可） | `FEATURE_CODE_MAP`（避免被现有代码结构限制想象力） |
| `product` — 架构 trade-off | `docs/ARCHITECTURE.md`、相关 Feature Spec 中的 Architecture Decisions 段 | — |
| `design` — UI/UX 设计 | `docs/ui/UI_SHOWCASE.md`（大纲即可，非全量）、相关页面的 `docs/ui/specs/*.md`。Prompt 末尾追加："请为本次设计指出一个 Signature Moment（让用户记住的一个点）" | `ARCHITECTURE`（设计不需要技术细节） |
| 涉及具体功能模块 | `docs/FEATURE_CODE_MAP.md` 中相关段落 | 全文 |

**按需附加**（复杂问题时）：
- 核心文件的 Git Diff 或 Provider 结构快照
- 相关 Feature Spec 中的历史架构决策

**注意**：不携带 `CLAUDE.md`（这是给 Claude Code 的工程操作指南，Gemini 作为产品/设计顾问不需要）。

### Step 1.5: 上下文完整性自检（发送前必须通过）

在组装 Prompt 之前，逐项检查：

| 检查项 | 要求 | 不通过时 |
|--------|------|---------|
| PRODUCT_SOUL | 已读取文件内容（不是凭记忆编写） | 去读 `docs/PRODUCT_SOUL.md` |
| 协作简况 | 已包含团队构成和工作方式 | 补充 |
| 工程现状 | 描述了与本次话题直接相关的现状 | 补充 |
| 按需文档 | 根据角色/话题表已收集对应文档 | 去读对应文件 |
| 多轮历史（如非首轮） | 包含所有前序轮次的问题+回复摘要+反馈 | 补全历史 |

**硬性规则**：如果当前不在具体项目目录中（无法读取 `docs/` 文件），必须向用户说明缺少项目上下文，询问是否继续。禁止凭记忆或猜测编造项目文档内容。

### Step 2: 组装 Prompt 并调用 Gemini

通过本地脚本调用 Gemini API：
```bash
node ~/LittleTree_Projects/other/nodejs_test/projects/ai/{role}.mjs "<prompt>"
```

#### 首轮 Prompt 格式

```
## 项目上下文
### PRODUCT_SOUL
{TL;DR 摘要或全文}
### ROADMAP（当前阶段）
{相关段落}
{... 其他按需文档 ...}

## 协作简况
{用 3-5 行描述当前团队实际的工作方式}

## 工程现状
{与本次讨论直接相关的工程现状}

## 需求 / 问题
{用户的具体需求，或 Claude Code 遇到的决策问题}
```

#### 多轮追问 Prompt 格式（关键）

**Gemini 无记忆，多轮对话时必须在 Prompt 中重建完整上下文。**

```
## 项目上下文
{与首轮相同——必须重新提供，不可省略}

## 对话历史

### 第 1 轮
#### 原始问题
{首轮提出的完整问题，可适当压缩但不可丢失关键信息}

#### Gemini 回复（摘要）
{Gemini 第 1 轮回复的核心结论和关键论据，300-500 字}

#### 执行者反馈
{Claude Code 的 Engineering Handshake 中的分歧/补充，200-300 字}

### 第 N 轮（如有更多轮次，依次追加）
...

## 本轮问题
{本轮的具体追问/分歧/新需求}
```

**多轮上下文传递原则：**
1. **项目上下文必须重传** — 首轮提供的 PRODUCT_SOUL、ROADMAP、工程现状等，在后续轮次中必须原样或等价地重新提供
2. **对话历史逐轮积累** — 每一轮的问题、Gemini 回复摘要、执行者反馈都要保留。摘要要保留核心论据和推理过程，不能只留结论
3. **Gemini 回复摘要 300-500 字** — 太短会丢失推理链，太长浪费 token。摘要必须包含三要素：
   - **已锁定的前提**（双方已达成共识的结论）
   - **当前争议点**（尚未解决的分歧）
   - **上一轮核心论据**（Gemini 为什么支持某方案的推理链）
4. **执行者反馈 200-300 字** — 保留 Claude Code 的分歧点、补充信息、替代方案。这让 Gemini 理解为什么要追问
5. **超过 3 轮时压缩早期轮次** — 第 1 轮可以压缩为 100 字共识摘要，最近 2 轮保留详细内容

#### Prompt 组装原则

1. **Gemini 需要的是"理解背景"，不是"评价体系"** — 提供足够的上下文让 Gemini 理解问题，但不要把内部工程体系抛出去让它评价
2. **描述事实，不描述体系** — 说"我们有 1178 个单元测试"比"我们有冰山模式测试策略"更不容易被误解
3. **标注触发方式** — 如果提到工具/流程，说清楚是"手动按需"还是"自动触发"，避免 Gemini 脑补

### Step 3: Engineering Handshake — 工程落地校验

**收到 Gemini 回复后，Claude Code 的职责是"执行者校验"，不是"评委打分"。**

**必须使用以下固定格式输出：**

```markdown
## Gemini 回复
{Gemini 的完整回复}

## Engineering Handshake

### Conflict Check
{核对是否违反项目现有的技术栈约束或架构决策。必须指出具体的代码约束条件（如："违反了 Local-First 的离线同步机制"、"破坏了现有 Widget 颗粒度规范"）。禁止模糊表述如"存在一定风险"。无冲突则写"无冲突"}

### Breakdown
{将 Gemini 方案拆解为可执行的 1, 2, 3 步骤}

### Prompt Founder
{如果需要 Founder 拍板的决策点，列出具体的 Yes/No 问题。不需要则写"无需额外决策"}
```

### Step 4: Founder 审批 & 落库

展示 Gemini 回复 + Engineering Handshake 后，等待 Founder 确认：

- **同意** → 继续落库
- **修改** → 根据反馈调整 Spec
- **追问** → 按多轮追问 Prompt 格式重新调用 Gemini（携带完整对话历史）
- **否决** → 在相关 Feature Spec 的 Architecture Decisions 段记录驳回理由

确认后：将方案落库为 Feature Brief（格式见下方模板），输出 "Ready to build"。

## Feature Brief 落库模板

落库到 `docs/features/` 的文档格式：

```markdown
# [Feature Name]

## Context & Soul (为什么做)
- 目标：...
- 质感/仪式感要求：...

## The Muse Test (守护检查，禁止 Yes/No 勾选，必须描述性回答)
- **物理隐喻**：这个交互像什么？（如："下拉刷新像拉动打字机的换行拨杆"）
- **触觉/视觉约束**：关键动效的具体参数（如："高斯模糊配合 150ms 抛物线阻尼曲线"）

## Architecture & Data Flow (怎么做)
- State (Riverpod): ...
- Data (Local-First): ...
- Core Logic Flow: ...

## Architecture Decisions (决策留存)
- 选择了什么方案：...
- 放弃了什么方案及原因：...
- 妥协点：...

## Checklist (可执行任务列表)
- [ ] 具体到单文件级别的修改...
```

## 沟通规范

- Claude Code 发给 Gemini 的 Prompt：**中文描述 + 英文术语**
- Gemini 回复：已配置为**中文描述 + 英文术语**
- Claude Code 展示给用户：Gemini 原文 + Engineering Handshake

## 约束

- 不写业务代码，只产出文档
- **Gemini 的回复是参考意见，不是指令** — Claude Code 必须独立判断
- Spec 落库前必须经过 Founder 审批，不可全自动
- 脚本路径固定：`~/LittleTree_Projects/other/nodejs_test/projects/ai/`
- 脚本执行失败时向用户报告错误，建议检查 `.env` 配置
