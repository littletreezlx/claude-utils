# Claude Code 命令系统

精简高效的斜杠命令库，遵循"**目标导向、自主执行**"设计理念。

## 快速选择

```
我要做什么？
│
├─ 快速操作（单次执行）
│  ├─ 截图分析 ──────────── /screen
│  └─ 学习文章经验 ────────── /learn-article
│
├─ 代码库维护
│  ├─ 生成/更新 CLAUDE.md ── /claudemd
│  ├─ 文档审查（vs 代码）── /doc-update-context
│  ├─ 文档质量（vs 标准）── /doc-quality-review
│  └─ 全面体检（DAG）────── /comprehensive-health-check
│
├─ 功能开发
│  ├─ 方案讨论（手动）────── /web-think → 复制到 Gemini Web
│  ├─ PRD 转需求 ─────────── /prd-to-doc
│  ├─ 学习新项目 ─────────── /learn-new-project
│  └─ 功能收尾 ────────────── feat-done skill（自动触发,不再用命令）
│
├─ 代码重构
│  ├─ 单文件 ──────────────── /refactor
│  ├─ 模块级（DAG）────────── /refactor-module
│  └─ 项目级（DAG）────────── /refactor-project
│
├─ 测试工程
│  ├─ 测试审查与补齐（DAG）── /test-plan
│  ├─ 运行与修复 ─────────── /test-run
│  ├─ 基础设施审计 ────────── /test-audit
│  └─ 创建 E2E 测试 ──────── /create-e2e-test
│
├─ 文档生成
│  ├─ 生成 CLAUDE.md ──────── /claudemd
│  ├─ 技术文档 ────────────── /techdoc
│  └─ 文档清理 ────────────── /doc-clean
│
├─ UI 工程（以 Claude Design 为中心的设计闭环）
│  ├─ UI 文档初始化（新项目）── /init-ui-showcase
│  ├─ Claude Design 接入 ──── /ui-bootstrap（老项目一次性用,建绑定+首版同步+漂移检测）
│  ├─ 改 UI 前路由 ──────────── ui-design-router skill（自动触发,分类小改/大改,大改生成 Δ Brief）
│  ├─ 评审 export bundle ──── /ui-vs（读源码,不靠截图;含不变量/覆盖度/审美/交互/Gemini 二眼）
│  ├─ 采纳反哺源文档 ──────── /ui-adopt（下一步主动作,闭合闭环+触发 re-onboard）
│  └─ 逆向生成代码 Spec ──── ui-spec skill
│
├─ 任务管理
│  ├─ 保存待办 ────────────── /todo-write → /todo-doit
│  └─ 大任务拆分（DAG）──── /todo-huge-task
│
└─ 跨工具协作
   ├─ 文档上下文管理 ────────── /doc-update-context
   └─ 全面健康检查（DAG）── /comprehensive-health-check
```

---

## 命令索引

### 代码质量 & 重构
| 命令 | 类型 | 说明 |
|------|------|------|
| `/refactor` | 即时 | 单文件/类级别重构 |
| `/refactor-module` | DAG | 单模块重构 |
| `/refactor-project` | DAG | 项目级重构 |

### 功能开发 & 方案设计
| 命令 | 类型 | 说明 |
|------|------|------|
| `/web-think` | 即时 | 生成 Prompt 供手动转发 Gemini Web（通用话题 + 功能设计） |
| `/web-gem-project` | 即时 | 生成增量 Prompt 给已建 Gem 的 Gemini Web |
| `/prd-to-doc` | 即时 | PRD 转客户端需求文档 |
| `/learn-new-project` | 即时 | 快速学习陌生项目 |

### 测试工程
| 命令 | 类型 | 说明 |
|------|------|------|
| `/test-plan` | DAG | 测试规划与批量编写 |
| `/test-run` | 即时 | 测试运行与修复（thin wrapper → test-workflow skill） |
| `/test-audit` | 即时 | 测试基础设施审计 |
| `/create-e2e-test` | 即时 | 创建 E2E 测试 |

### 文档生成
| 命令 | 类型 | 说明 |
|------|------|------|
| `/claudemd` | 即时 | 生成项目 CLAUDE.md |
| `/techdoc` | 即时 | 技术文档撰写 |
| `/doc-clean` | 串行 | 文档清理归档 |

### 健康检查 & 代码库维护
| 命令 | 类型 | 说明 |
|------|------|------|
| `/comprehensive-health-check` | DAG | 全面体检（工具驱动诊断 + 行动路线） |

### UI 工程（以 Claude Design 为中心的设计闭环）

**首要设计工具是 Claude Design**（Anthropic 2026-04 发布,Opus 4.7 驱动）。它在 onboarding 时读 codebase + 设计文件自动建立内部 design system。本地文档是**增量约束 + 归档快照 + 反哺源**，不是从零描述。

```text
SOURCES (权威源)
 ├─ PRODUCT_SOUL / UI_SHOWCASE(OKLCH Invariants) / EXTERNAL_REFS(Claude Design 绑定)
       │
       │  首次接入: /ui-bootstrap（从 Claude Design export 逆向抽取+漂移检测）
       │  每轮迭代: ui-design-router skill（用户说"改 UI" 自动触发,分类后大改派生 Δ Brief）
       ▼
Δ BRIEF (派生,仅增量) → 复制到 Claude Design 对话框
       ▼
CLAUDE DESIGN（唯一编辑入口）
       │  ├──▶ Share URL → /ui-vs 评审（读源码,不靠截图）
       │  ├──▶ Export bundle → docs/design/generated/{ts}/project/*
       │  └──▶ Handoff to Code → 本地 pixel-perfect recreate
       ▼
DECISION → /ui-adopt 反哺 SOURCES + 归档 + 触发 re-onboard → 回 SOURCES
```

| 命令 | 类型 | 说明 |
|------|------|------|
| `/init-ui-showcase` | 即时 | Flutter UI 文档系统初始化（新项目,建 UI_SHOWCASE.md 骨架） |
| `/ui-bootstrap` | 即时 | **老项目首次接入 Claude Design 闭环** — 建绑定 / 抽设计系统 / 归档首版 / 代码漂移诊断 |
| `ui-design-router` skill | 自动触发 | 用户表达改 UI 意图时自动介入,分类小改/大改,大改派生 Δ Brief 到 `docs/design/DESIGN_BRIEF.md` |
| `/ui-vs` | 即时 | 评审 Claude Design export bundle（读 HTML/CSS/JSX 源码,Phase 0 机械校验 + Phase 0.5 覆盖度 + Phase 1 审美 + Phase 1.5 交互 + Phase 1.9 Gemini 二眼） |
| `/ui-adopt` | 即时 | **设计闭环主动作** — 反哺 SOURCES + 归档 bundle + 触发 Claude Design re-onboard 提示 |

**Design-First Gate**：UI 改动量大时（≥3 页面 / 触及不变量 / 新视觉模式），**先走 Claude Design 再改本地代码**。详见 `~/.claude/guides/doc-structure.md § 设计优先原则`。

**唯一编辑入口铁律**：Claude Design 是设计的唯一编辑入口。本地 `docs/design/generated/{ts}/project/*` 是**只读快照**，严禁手改 export 文件。要改设计回 Claude Design 改。

**老项目(5 个 Flutter 项目)首次接入**：

```bash
# 每个项目独立跑一次
/ui-bootstrap
# 答绑定信息 → 指定 Claude Design export 本地路径
# 自动生成 EXTERNAL_REFS / UI_SHOWCASE / 首版归档 / Δ Brief / DRIFT_REPORT
# 人工读 DRIFT_REPORT.md 逐条决策
```

**接入后典型一轮迭代**：

```text
# 1. 跟 Claude Code 说"想改 X 页 / 换个感觉 / 补 Y 态"
#    → ui-design-router skill 自动介入,分类:
#      - 小改:直接实施,无需走闭环
#      - 大改:自动派生 Δ Brief 到 docs/design/DESIGN_BRIEF.md + 输出到终端

# 2. (大改路径)把 Δ Brief 贴到 Claude Design 对话,在 Claude Design 里迭代
#    Claude Design 里做完,export bundle 到本地临时目录

# 3. 评审 export（读源码,不看截图）
/ui-vs

# 4. 按 /ui-vs 的"下一步"指引:
#    - 继续迭代 → 贴指令回 Claude Design,重来第 2 步
#    - 采纳 → /ui-adopt（闭合闭环+触发 re-onboard 提示）
/ui-adopt

# 5. 本地代码 pixel-perfect recreate(基于归档的 bundle)
#    完成后 feat-done skill 自动触发收尾(Gate 查 bundle + 文档同步 + 提交)
```

### 学习 & 知识管理
| 命令 | 类型 | 说明 |
|------|------|------|
| `/learn-article` | 即时 | 评估文章观点，提炼经验整合到工作流体系 |
| `/note` | 即时 | 知识库速记，自动归档到知识库 |
| `/learn-new-project` | 即时 | 快速学习陌生项目 |

### 项目管理 & 工具
| 命令 | 类型 | 说明 |
|------|------|------|
| `/todo-write` | 串行 | 保存待办清单 |
| `/todo-doit` | 串行 | 执行待办任务 |
| `/todo-huge-task` | DAG | 大任务智能拆分 |
| `/screen` | 即时 | 截图分析辅助 |
| `/doc-update-context` | 串行 | docs/ 全量文档 vs 代码一致性审查 |
| `/doc-quality-review` | DAG | docs/ 文档体系质量审查（Map-Reduce） |

---

## DAG 任务系统

### 什么是 DAG 任务？

DAG（有向无环图）任务编排是**完全自动化、无人值守**的任务执行模式。

### 核心特性

- **STAGE 阶段控制** - 串行/并行模式
- **TASK 任务单元** - 细粒度执行
- **文件冲突检测** - 自动分析，无冲突并行
- **断点续传** - 中断后自动继续
- **自动化保证** - batchcc 统一注入自动化指示

### 使用流程

```bash
# 1. 生成任务文件
/todo-huge-task "实现电商用户和订单系统"

# 2. 执行（完全自动化）
batchcc task-xxx
```

### DAG 命令一览

| 命令 | 用途 |
|------|------|
| `/todo-huge-task` | 大任务拆分与编排 |
| `/comprehensive-health-check` | 项目全面体检 |
| `/refactor-project` | 项目级重构 |
| `/refactor-module` | 单模块重构 |
| `/test-plan` | 测试规划与批量编写 |

> 详细格式参见 @~/.claude/commands/templates/workflow/DAG_FORMAT.md（DAG 统一规范）

---

## 自动化 Skills

除了手动触发的命令，以下 Skill 由 Claude 根据意图自动调用：

| Skill | 自动触发场景 |
|-------|-------------|
| `git-workflow` | 代码改完、测试通过时自动提交 |
| `test-workflow` | 代码修改后自动验证、测试失败自动修复 |
| `consistency-check` | 开始新功能时自动检查代码库自洽性 |
| `code-quality` | 提交前自动代码审查 |
| `think-gem-project` | 遇到产品/架构/UI 决策时自动调用 Gemini API（项目级） |
| `think` | 方法论/策略讨论时调用 Gemini Think |
| `test-verify` | AI 大量生成测试时自动红队验证 |

> Skills 详细说明见 `~/.claude/skills/README.md`

---

## 相关文档

| 文档 | 说明 |
|------|------|
| @CLAUDE.md | 命令设计指南 |
| ~/.claude/skills/README.md | Skill 编写指南 |
| @~/.claude/commands/templates/workflow/DAG_FORMAT.md | DAG 统一规范 |
| @~/.claude/commands/templates/workflow/DAG_EXAMPLE_*.md | DAG 任务示例 |
| @templates/docs/ | 文档模板 |

---

**命令总数**：27 个（`feat-done` 和 `ui-design-router` 已迁移为 skill，由 Claude 自动触发）| **设计原则**：目标导向、自主执行、单一真相源

---

## 矫正坏状态工作流

项目状态不佳？按以下顺序操作：

1. `consistency-check` skill — 快速对齐四要素（代码/测试/文档/CLAUDE.md）
2. `/test-run` — 修复失败的测试（建立安全网）
3. `/claudemd` — 生成或更新项目级 CLAUDE.md
4. `/comprehensive-health-check` — 需要全面诊断时，运行 DAG 体检
5. 按诊断报告的行动路线执行专项命令

核心原则：先建立测试合约 → 再修复代码 → 最后对齐文档
