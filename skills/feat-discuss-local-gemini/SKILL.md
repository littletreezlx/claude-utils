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
version: 0.3.0
---

# 与 Gemini 自动化协作 — 产品 & 设计咨询

## 目的

与 Gemini（产品合伙人 / 设计架构师）进行自动化协作。Claude Code 自动收集项目上下文、调用 Gemini API、接收回复、经过 Engineering Handshake 校验后落库为 Spec 文档。Founder 在关键节点审批。

**模式定位**：本技能是 Local API 自动模式（主力模式）。Web 手动模式（`/feat-discuss-web-gemini`）仅在用户明确要求、或需要多轮视觉反馈的重度脑暴时使用。

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

> **为什么保持双角色而非合并？** product 关注"该不该做、数据怎么流"，design 关注"怎么好看、动效怎么调"。强行合并会导致 AI 注意力稀释，两头都做不深。经 Gemini 评估确认：看完两套完整 System Prompt 后推翻了合并建议。

**上下文收集 — 动态组装策略**：

**Global 常驻（每次必带）**：
- `docs/PRODUCT_SOUL.md` — 优先读取 `## TL;DR` 摘要段（如有），避免全文塞入浪费 token。若无摘要段则传全文。

> **为什么不硬编码摘要到脚本？** 硬编码意味着 PRODUCT_SOUL 更新时需同步改脚本，违反"单一事实来源"原则。摘要段留在文档中，修改一处即可。

**按需上下文（根据角色和话题动态选择）**：

| 角色 / 话题 | 额外携带 | 不携带 |
|-------------|---------|--------|
| `product` — 产品方向、需求讨论 | `docs/ROADMAP.md`（当前 Epic 节点即可） | `FEATURE_CODE_MAP`（避免被现有代码结构限制想象力） |
| `product` — 架构 trade-off | `docs/ARCHITECTURE.md`、相关 Feature Spec 中的 Architecture Decisions 段 | — |
| `design` — UI/UX 设计 | `docs/ui/UI_SHOWCASE.md`（大纲即可，非全量）、相关页面的 `docs/ui/specs/*.md` | `ARCHITECTURE`（设计不需要技术细节） |
| 涉及具体功能模块 | `docs/FEATURE_CODE_MAP.md` 中相关段落 | 全文 |

**按需附加**（复杂问题时）：
- 核心文件的 Git Diff 或 Provider 结构快照
- 相关 Feature Spec 中的历史架构决策

**注意**：不携带 `CLAUDE.md`（这是给 Claude Code 的工程操作指南，Gemini 作为产品/设计顾问不需要）。

### Step 2: 调用 Gemini

拼接结构化 Prompt，通过本地脚本调用 Gemini API：
```bash
node ~/LittleTree_Projects/other/nodejs_test/projects/ai/{role}.mjs "<prompt>"
```

**Prompt 拼接格式**（中文描述 + 英文术语）：
```
## 项目上下文
### PRODUCT_SOUL
{TL;DR 摘要或全文}
### ROADMAP（当前阶段）
{相关段落}
{... 其他按需文档 ...}

## 协作简况
{用 3-5 行描述当前团队实际的工作方式。目的是让 Gemini 理解"我们怎么工作"，避免脑补。}
{示例：}
{- 这是一人公司 + Claude Code（工程）+ Gemini（产品/设计）的精品团队}
{- 日常开发：Founder 与 Claude Code 结对编程，大部分代码/测试/文档由 Claude Code 自主完成}
{- 工具体系：Claude Code 有一套按需手动调用的 Skill 工具箱（不是自动化流水线）}
{- 当前重点：专注 Flutter 移动端 (iOS/Android)，macOS 已废弃}

## 工程现状
{当前代码结构、技术限制等简报}
{重点：描述与本次讨论话题直接相关的工程现状}
{避免：罗列所有工具/能力清单——Gemini 不需要评价工程工具链}

## 需求 / 问题
{用户的具体需求，或 Claude Code 遇到的决策问题}
```

**上下文组装原则**：
1. **Gemini 需要的是"理解背景"，不是"评价体系"** — 提供足够的上下文让 Gemini 理解问题，但不要把内部工程体系抛出去让它评价
2. **描述事实，不描述体系** — 说"我们有 1178 个单元测试"比"我们有冰山模式测试策略"更不容易被误解
3. **标注触发方式** — 如果提到工具/流程，说清楚是"手动按需"还是"自动触发"，避免 Gemini 脑补

### Step 3: Engineering Handshake — 工程落地校验

**收到 Gemini 回复后，Claude Code 的职责是"执行者校验"，不是"评委打分"。**

> **为什么改名？** 原来的 "Critical Thinking" 步骤深度不确定——有时太浅（走过场），有时太深（花大量 token 质疑合理建议）。固定格式让输出稳定、有价值。

**必须使用以下固定格式输出：**

```markdown
## Gemini 回复
{Gemini 的完整回复}

## Engineering Handshake

### Conflict Check
{仅核对是否违反项目现有的技术栈约束（Flutter/Riverpod/Drift 等），是否与已有 Feature Spec 中的架构决策矛盾。无冲突则写"无冲突"，不要废话}

### Breakdown
{将 Gemini 方案拆解为可执行的 1, 2, 3 步骤}

### Prompt Founder
{如果需要 Founder 拍板的决策点，列出具体的 Yes/No 问题。不需要则写"无需额外决策"}
```

### Step 4: Founder 审批 & 落库

**展示 Gemini 回复 + Engineering Handshake 后，等待 Founder 确认，再执行落库：**

1. 向用户展示 Gemini 完整回复 + Engineering Handshake
2. **等待 Founder 确认**：
   - **同意** → 继续落库
   - **修改** → 根据反馈调整 Spec
   - **追问** → 携带上一轮结论（浓缩为 100 字以内的 `<Previous_Consensus>`）重新调用 Gemini
   - **否决** → 在相关 Feature Spec 的 Architecture Decisions 段记录驳回理由（防止重复踩坑）
3. 确认后：将方案落库为 Feature Brief（格式见下方模板）
4. 输出 "Ready to build"

**多轮追问**：用户不满意时可继续追问。每次必须将上一轮结论浓缩为 `<Previous_Consensus>`（100 字以内）附加到新请求首部，避免全量历史塞入。

## Feature Brief 落库模板

无论结论来自 Local API 还是 Web，最终落库到 `docs/features/` 的文档必须遵循以下格式：

```markdown
# [Feature Name]

## Context & Soul (为什么做)
- 目标：...
- 质感/仪式感要求：...

## The Muse Test (守护检查，按需填写)
- [ ] 是否违反了"少即是多"？(Less but Better)
- [ ] 交互是否具有数字玩具的物理反馈感？(Warmth)

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

> **为什么不用独立 ADR？** 实际项目中 `docs/adr/` 目录始终为空，独立 ADR 机制形同虚设。将架构决策内联到 Feature Spec 的段落中更务实，随功能走、随功能查。

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
