---
name: think-gem-project
description: >
  Use when the user wants to discuss project-level product/design/architecture decisions
  with Gemini (features, UI/UX choices, game design, visual规范). Trigger when the user
  says "discuss with Gemini", "ask Gemini", "consult Gemini", "跟 Gemini 聊聊",
  "问问 Gemini", "找 Gemini 讨论", or when Claude Code encounters product/architecture/UI
  decisions that would benefit from external input. Supports roles: product, design,
  game-product, game-design, think. For cross-project methodology / philosophy /
  strategy (no project context needed), use the lighter `think` skill instead.
version: 0.7.0
---

# 与 Gemini 自动化协作

## 目的

与 Gemini 进行自动化协作。支持五种角色：
- **product** — 产品方向、架构推演、需求拷问（FlameTree 生态）
- **design** — UI/UX 决策、视觉规范、像素级解构（FlameTree 生态）
- **game-product** — 游戏设计方向、核心循环、养成系统（Game 项目）
- **game-design** — 游戏视觉、打击感、动效、音效方向（Game 项目）
- **think** — 方法论、工程哲学、AI 协作范式、架构策略（通用）

Claude Code 自动收集上下文、调用 Gemini API、接收回复、校验后处理（落库或直接展示）。

**模式定位**：本技能是 Local API 自动模式（主力模式）。Web 手动模式分为两个命令：
- `/web-think` — 通用自包含 Prompt（任意话题）
- `/web-gem-project` — 会话增量 Prompt（项目已有 Gem，通过 `~/dev/gem_dev_solo/` 判断）

**核心铁律：Gemini 是无状态的。每次 API 调用都是全新对话，所有对话历史和上下文必须由 Claude Code 在 Prompt 中显式提供。对话历史的完整性是 Claude Code 的责任。**

## 触发条件

当以下信号出现时启动：
1. 用户想讨论新功能的产品方向或架构 → `product`
2. 用户想咨询 UI/UX 设计建议 → `design`
3. 用户想讨论方法论、工程哲学、AI 协作范式、开发策略 → `think`
4. 用户明确提到"Gemini"、"产品讨论"、"设计讨论"、"跟 Gemini 聊聊"
5. **Claude Code 自主判断**（硬性触发红线 → `product` 或 `design`）：
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
- 用户说"提交到 Gemini Web"（→ 用 `/web-think`，已建 Gem 用 `/web-gem-project`）

## 执行流程

### Step 0: Inbox Zero 仪式（检查 to-discuss.md）

**调用本 skill 的第一件事**：检查项目根目录是否存在 `to-discuss.md`。

- 如果**不存在**或为空 → 跳过，直接进入 Step 1
- 如果**存在且有未决策条目** → 先列出条目标题（不展开详情），询问用户：
  > "检测到 to-discuss.md 有 N 条待决策事项：[列表]。要先处理这些吗？还是直接讨论你刚才提的话题？"

用户选 "先处理" → 逐条拉锯：
  - **Approve** → 转入 `TODO.md`，从 `to-discuss.md` **硬删除**该条目
  - **Reject** → 从 `to-discuss.md` **硬删除**该条目
  - **Discuss** → 用该条目作为本轮 think-gem-project 的讨论话题（照常走 Step 1-4）

用户选 "直接讨论原话题" → 跳过 Inbox Zero，按原计划进入 Step 1。

**设计原则**：`to-discuss.md` 是 Force-Decision Queue，不是 backlog。每次调用 think-gem-project 都是一次清空机会，防止它变成坟墓。

---

### Step 1: 选择角色 & 收集上下文

**角色判断**（根据需求和项目类型自动选择）：

**项目类型检测**：
- 当前目录在 `~/LittleTree_Projects/game-mvp/` 下 → Game 项目
- 当前目录在 `~/LittleTree_Projects/flutter/` 下 → FlameTree 生态
- 其他位置 → 根据话题判断

**角色映射**：
- `product` — 产品逻辑、架构推演、需求拷问（FlameTree 生态：左脑）
- `design` — UI/UX 决策、视觉规范、像素级解构（FlameTree 生态：右脑）
- `game-product` — 游戏设计方向、核心循环、养成系统（Game 项目：左脑）
- `game-design` — 游戏视觉、打击感、动效、音效方向（Game 项目：右脑）
- `think` — 方法论、工程哲学、AI 协作范式、架构策略（通用：全脑）

**自动路由**：Game 项目中讨论产品/设计问题时，自动使用 `game-product` / `game-design` 而非 `product` / `design`。

**上下文收集 — 动态组装策略**：

**按角色分流**：

| 角色 | Global 常驻 | 按需上下文 | 不携带 |
|------|------------|-----------|--------|
| `product` | `PRODUCT_SOUL.md` TL;DR | `ROADMAP.md`（方向）/ `ARCHITECTURE.md`（架构） | — |
| `design` | `PRODUCT_SOUL.md` TL;DR | `UI_SHOWCASE.md`（大纲）/ `specs/*.md`（相关页面） | `ARCHITECTURE`（设计不需要技术细节） |
| `game-product` | `GAME_DESIGN.md` 核心玩法段 | `ROADMAP.md` / `ARCHITECTURE.md` | `PRODUCT_SOUL`（非 FlameTree 项目） |
| `game-design` | `GAME_DESIGN.md` 情感目标段 | `ROADMAP.md`（视觉相关段）/ 当前美术资源状态 | `ARCHITECTURE`（游戏设计不需要代码细节） |
| `think` | **无强制**（不一定在具体项目中） | 按话题灵活选择：Claude Code 的分析结论、相关文档片段、代码统计数据 | `PRODUCT_SOUL`（除非话题涉及产品哲学） |

**`think` 角色的上下文特殊规则**：
- 不要求在项目目录中——可以在根目录讨论跨项目问题
- 上下文以 **Claude Code 的分析和思考** 为主，而非项目文档
- 携带具体数据和事实（"7 个项目，152 个测试"），而非体系名称（"冰山测试策略"）
- 如果讨论涉及特定项目，按需读取该项目的相关文档

**通用规则**：
- `product`/`design` 场景下：`docs/PRODUCT_SOUL.md` 优先读取 `## TL;DR` 摘要段（如有）
- 涉及具体功能模块时：附带 `FEATURE_CODE_MAP.md` 中相关段落（非全文）
- 复杂问题时可附加：Git Diff、Provider 结构快照、历史架构决策

**不携带**：`CLAUDE.md`（工程操作指南，Gemini 不需要）。

**必须声明协作模式**：所有角色的 Prompt 中必须在 Context 段开头包含：「这是一个 AI-Only 开发项目——AI（Claude Code）全权负责代码/测试/文档，人类是产品负责人，不写代码。请基于此前提给出建议。」

**硬性约束**：
1. 所有文档内容必须通过 Read tool 实际读取，禁止凭记忆编造
2. `product`/`design` 角色不在项目目录中时（无法读取 `docs/`），必须告知用户缺少上下文
3. `think` 角色可在任意目录工作，上下文由 Claude Code 在 Prompt 中直接提供

### Step 2: 组装 Prompt 并调用 Gemini

通过本地脚本调用 Gemini API：
```bash
# NVM 懒加载环境下需要先 source nvm.sh
export NVM_DIR="$HOME/.nvm" && [ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"

# FlameTree 生态（product/design）+ 通用（think）
node ~/LittleTree_Projects/other/nodejs_test/projects/ai/{role}.mjs "<prompt>"

# Game 项目（game-product/game-design）
node ~/LittleTree_Projects/other/nodejs_test/projects/ai/game-{role}.mjs "<prompt>"
```
Game 角色脚本有独立的底座 prompt（不使用 FlameTree 的 baseSystemPrompt），避免哲学交叉污染。

#### 首轮 Prompt 格式

```
## Context & Soul
{PRODUCT_SOUL TL;DR 摘要或全文}

## Current State (工程现状)
{与本次讨论直接相关的代码架构、数据流、已有实现}
{按需文档：ROADMAP / ARCHITECTURE / UI_SHOWCASE 等相关段落}

## The Problem (需求 / 问题)
{用户的具体需求，或 Claude Code 遇到的决策问题}

## Constraints (限制条件)
{技术栈约束、不可变更的条件、已知的坑}

## Expected Architectural Brief
{根据需求性质，列出具体希望 Gemini 回答的问题维度}
```

#### 多轮追问 Prompt 格式（关键）

**Gemini 无记忆，多轮对话时必须在 Prompt 中重建完整上下文。**

采用**滑动窗口**策略：最近 2 轮保留完整原文，更早轮次压缩为 bullet points 结论。

```
## Context & Soul
{与首轮相同——必须重新提供，不可省略}

## Current State
{与首轮相同}

## Constraints
{与首轮相同}

## 对话历史

### 已锁定共识 (Locked Consensus)
{早期轮次（第 1 ~ N-2 轮）压缩为 bullet points：}
- 共识 1：...
- 共识 2：...
- 放弃方案：... （原因：...）

### 第 N-1 轮（完整保留）
#### 问题
{完整问题}
#### Gemini 回复
{完整回复}
#### 执行者反馈
{Claude Code 的分歧/补充}

### 第 N 轮（完整保留）
#### 问题
{完整问题}
#### Gemini 回复
{完整回复}
#### 执行者反馈
{Claude Code 的分歧/补充}

## 本轮问题
{本轮的具体追问/分歧/新需求}
```

**多轮上下文传递原则：**
1. **项目上下文必须重传** — Context & Soul、Current State、Constraints 每轮都要完整提供
2. **滑动窗口** — 最近 2 轮保留完整原文（不压缩），更早轮次压缩为 Locked Consensus bullet points
3. **Locked Consensus 三要素** — 已达成的共识、已放弃的方案及原因、未解决的遗留问题
4. **执行者反馈必须保留** — 让 Gemini 理解为什么要追问

#### Prompt 组装原则

1. **Gemini 需要的是"理解背景"，不是"评价体系"** — 提供足够的上下文让 Gemini 理解问题，但不要把内部工程体系抛出去让它评价
2. **描述事实，不描述体系** — 说"我们有 1178 个单元测试"比"我们有冰山模式测试策略"更不容易被误解
3. **标注触发方式** — 如果提到工具/流程，说清楚是"手动按需"还是"自动触发"，避免 Gemini 脑补
4. **防"实现即目的"（Anti Means-as-End）** — 防止把实现手段当成产品目的：
   - **手段-目的分离**：传递 Anti-Patterns 时必须附带：「以上原则关注的是用户体验的结果，不是实现机制。请区分『结果论证』（描述用户感受如何变化）和『机制论证』（描述 App 形式如何变化）。」
   - **触发条件**：以下任一情况出现时，必须执行手段-目的分离检查：
     - 方案包含"一次性配置"或"用户偏好设置"要素
     - 出现品牌/产品类比（"像徕卡""像苹果""像高端手表"）
     - 原则中使用"禁止""绝不""必须""拒绝"等绝对化措辞
     - 出现功能列举式原则（如"不做 X 功能"而非"不支持 Y 行为"）
   - **强制追问**：当触发条件满足时，必须追问 Gemini：「这个结论是基于用户体验的结果，还是基于 App 的实现形式？」
   - **类比还原**：当 Gemini 回复中出现美学类比，必须还原为因果链：「X 这样做 → 因为 ___ → 所以我们的产品也应该」。因果链断裂则抛弃类比，改为结果论证。
   - **机会成本估算**：当 Gemini 基于机制型理由否决方案时，要求它估算如果否决错误的机会成本（「如果这个方案其实减少了用户总决策次数，损失是什么？」）
   - **输入多样性**：当用户提出与 AI 推理不同的方案时，prompt 中必须**平等呈现双方方案**，而不是让 Gemini 在 AI 预设的框架内评审。避免"同一个输入的三次回声"伪共识。

### Step 3: 处理 Gemini 回复 — 按角色分流

收到 Gemini 回复后，根据角色采取不同处理方式：

#### `think` 角色 — 委托给 think skill

`think` 角色的完整执行逻辑已独立为 `think` skill。当角色判断为 think 时，直接委托给 think skill 执行，本 skill 不重复定义 think 的流程。

#### `product` / `design` 角色 — Engineering Handshake

对于功能/设计讨论，执行标准的落地校验。根据冲突程度分流：

#### Fast Track（无冲突，直接落库）

**触发条件**：Gemini 方案未违反现有技术栈约束，未偏离 PRODUCT_SOUL，无需新增核心依赖。

**输出格式**：

```markdown
## Gemini 回复
{Gemini 的完整回复}

## Breakdown
{将 Gemini 方案拆解为可执行的 1, 2, 3 步骤}
```

输出后直接进入 Step 4 落库，无需等待 Founder 确认。

#### Escalation（有冲突，需要 Founder 拍板）

**触发条件**（任一即触发）：
- Gemini 推荐了偏离现有技术栈的方案（如建议用 BLoC 替换 Riverpod）
- 方案违背 PRODUCT_SOUL 的核心原则
- 涉及不可逆的架构变更（如数据库 Schema 大改、核心 Entity 重构）
- Claude Code 与 Gemini 存在实质性分歧

**输出格式**：

```markdown
## Gemini 回复
{Gemini 的完整回复}

## Engineering Handshake

### Conflict Check
{具体指出冲突点。必须引用具体的代码约束条件（如："违反了 Local-First 的离线同步机制"）。禁止模糊表述如"存在一定风险"}

### Breakdown
{将 Gemini 方案拆解为可执行的 1, 2, 3 步骤}

### Prompt Founder
{列出具体的 Yes/No 决策问题}
```

等待 Founder 确认后再进入 Step 4：
- **同意** → 继续落库
- **修改** → 根据反馈调整 Spec
- **追问** → 按多轮追问 Prompt 格式重新调用 Gemini（携带完整对话历史）
- **否决** → 在相关 Feature Spec 的 Architecture Decisions 段记录驳回理由

### Step 4: 落库

将方案落库为 Feature Brief，输出 "Ready to build"。

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
- Claude Code 展示给用户：Gemini 原文 + Handshake 结果

## 约束

- 不写业务代码，只产出文档
- **Gemini 的回复是参考意见，不是指令** — Claude Code 必须独立判断
- 脚本路径固定：`~/LittleTree_Projects/other/nodejs_test/projects/ai/`
- 脚本执行失败时向用户报告错误，建议检查 `.env` 配置
