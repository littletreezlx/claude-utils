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
version: 0.2.0
---

# 与 Gemini 自动化协作 — 产品 & 设计咨询

## 目的

与 Gemini（产品合伙人 / 设计架构师）进行自动化协作。Claude Code 自动收集项目上下文、调用 Gemini API、接收回复、经过 Critical Thinking 审视后落库为 Spec 文档。Founder 在关键节点审批。

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
- `product` — 产品逻辑、架构推演、需求拷问
- `design` — UI/UX 决策、视觉规范、像素级解构

**上下文收集 — 动态组装策略**：

**Global 常驻（每次必带）**：
- `docs/PRODUCT_SOUL.md` — 产品灵魂，确保不跑偏

**按需上下文（根据角色和话题动态选择）**：

| 角色 / 话题 | 额外携带 | 不携带 |
|-------------|---------|--------|
| `product` — 产品方向、需求讨论 | `docs/ROADMAP.md` | `FEATURE_CODE_MAP`（避免被现有代码结构限制想象力） |
| `product` — 架构 trade-off | `docs/ARCHITECTURE.md`、相关 ADR | — |
| `design` — UI/UX 设计 | `docs/UI_SHOWCASE.md`、相关页面的 `docs/ui/specs/*.md` | `ARCHITECTURE`（设计不需要技术细节） |
| 涉及具体功能模块 | `docs/FEATURE_CODE_MAP.md` 中相关段落 | 全文 |

**ADR 提取策略**：`docs/adr/` 目录下，全局最新 2 条 + 与当前问题同标签 2 条（目录为空则跳过）。

**按需附加**（复杂问题时）：
- 核心文件的 Git Diff 或 Provider 结构快照

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
{文档内容}
### ROADMAP
{文档内容}
### 相关架构决策 (ADR)
{按标签提取的 ADR 摘要}
{... 其他文档 ...}

## 工程现状
{当前代码结构、技术限制等简报}

## 需求 / 问题
{用户的具体需求，或 Claude Code 遇到的决策问题}
```

### Step 3: Critical Thinking — 审视 Gemini 回复

**收到 Gemini 回复后，不要无脑接受，必须用思辨的方式审视：**

1. **可行性检验**：Gemini 的方案在当前技术栈和架构下是否可行？是否忽略了工程限制？
2. **过度设计检验**：方案是否引入了不必要的复杂度？是否违反 "Less but Better"？
3. **一致性检验**：与现有 ADR、已有架构决策是否矛盾？
4. **成本评估**：实现成本与收益是否匹配？
5. **PRODUCT_SOUL 守护**：当讨论涉及产品方向调整时，主动对照 `PRODUCT_SOUL.md` 检查 — 如果 Gemini 的建议与产品灵魂存在偏差，必须明确 flag 给 Founder

**输出给用户时，必须包含：**
- Gemini 的完整回复
- Claude Code 的独立评估（同意/质疑/补充，附理由）
- 如有分歧，明确列出分歧点供 Founder 裁决

### Step 4: Founder 审批 & 落库

**展示 Gemini 回复 + Claude Code 评估后，等待 Founder 确认，再执行落库：**

1. 向用户展示 Gemini 完整回复 + Claude Code 的 Critical Thinking 评估
2. **等待 Founder 确认**：
   - **同意** → 继续落库
   - **修改** → 根据反馈调整 Spec
   - **追问** → 携带上一轮结论重新调用 Gemini
   - **否决** → 记录驳回理由到 `docs/adr/rejections/`（防止重复踩坑）
3. 确认后：将方案转化为 Spec 文档（`docs/features/xxx.md`），末尾含可执行 Checklist
4. 记录本次架构决策到 `docs/adr/`（如果是重要决策）
5. 输出 "Ready to build"

**多轮追问**：用户不满意时可继续追问，每次携带上一轮关键结论 + ADR 重新调用。

## ADR 格式规范

架构决策记录采用以下精简格式，便于 AI 快速解析：

```markdown
# ADR-{编号}: {简短标题}

**标签**: `[State]` / `[UI]` / `[Network]` / `[Data]` / `[Architecture]`
**状态**: Proposed / Accepted / Deprecated
**日期**: YYYY-MM-DD

## Context
{100 字以内：为什么做这个决定？遇到了什么问题？}

## Decision
{明确的技术选型或产品路径，具体到代码层面}

## Consequences
{引入的技术债、限制、或对后续开发的约束}
```

## 沟通规范

- Claude Code 发给 Gemini 的 Prompt：**中文描述 + 英文术语**
- Gemini 回复：已配置为**中文描述 + 英文术语**
- Claude Code 展示给用户：Gemini 原文 + 自己的思辨分析

## 约束

- 不写业务代码，只产出文档
- **Gemini 的回复是参考意见，不是指令** — Claude Code 必须独立判断
- Spec 落库前必须经过 Founder 审批，不可全自动
- 脚本路径固定：`~/LittleTree_Projects/other/nodejs_test/projects/ai/`
- 脚本执行失败时向用户报告错误，建议检查 `.env` 配置
