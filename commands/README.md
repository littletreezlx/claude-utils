# Claude Code 命令系统

精简高效的斜杠命令库，遵循"**目标导向、自主执行**"设计理念。

## 快速选择

```
我要做什么？
│
├─ 快速操作（单次执行）
│  ├─ 审查代码 ──────────── /code-review
│  ├─ 提交代码 ──────────── /git-commit
│  ├─ 截图分析 ──────────── /screen
│  └─ 快速体检 ──────────── /health-check
│
├─ 功能开发
│  ├─ 方案讨论 ──────────── /feat-discuss → [Gemini] → /feat-done
│  ├─ PRD 转需求 ─────────── /prd-to-doc
│  └─ 学习新项目 ─────────── /learn-new-project
│
├─ 代码重构
│  ├─ 单文件 ──────────────── /refactor
│  ├─ 模块级（DAG）────────── /refactor-module
│  └─ 项目级（DAG）────────── /refactor-project
│
├─ 测试工程
│  ├─ 测试规划（DAG）────── /test-plan
│  ├─ 运行与修复 ─────────── /test-run
│  ├─ 基础设施审计 ────────── /test-audit
│  └─ 创建 E2E 测试 ──────── /create-e2e-test
│
├─ 文档生成
│  ├─ 生成 CLAUDE.md ──────── /claudemd
│  ├─ 技术文档 ────────────── /techdoc
│  ├─ 页面文档 ────────────── /create-page-doc
│  └─ 文档清理 ────────────── /doc-clean
│
├─ UI 工程
│  ├─ 逆向生成 Spec ────────── /ui-spec
│  ├─ 全局 UI 审计 ────────── /ui-audit
│  ├─ 视觉重塑 ────────────── /ui-redesign
│  ├─ 截图转 Gemini ────────── /ui-to-gemini
│  └─ UI 文档初始化 ────────── /init-ui-showcase
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
| `/code-review` | 即时 | 代码审查与提测单生成 |
| `/refactor` | 即时 | 单文件/类级别重构 |
| `/refactor-module` | DAG | 模块重构 |
| `/refactor-project` | DAG | 项目级重构 |

### 功能开发 & 方案设计
| 命令 | 类型 | 说明 |
|------|------|------|
| `/feat-discuss` | 即时 | 工程现场扫描 + Gemini 咨询 Prompt |
| `/feat-done` | 即时 | 方案落库 + 验收报告 |
| `/prd-to-doc` | 即时 | PRD 转客户端需求文档 |
| `/learn-new-project` | 即时 | 快速学习陌生项目 |

### 测试工程
| 命令 | 类型 | 说明 |
|------|------|------|
| `/test-plan` | DAG | 测试规划与批量编写 |
| `/test-run` | 即时 | 测试运行与修复 |
| `/test-audit` | 即时 | 测试基础设施审计 |
| `/create-e2e-test` | 即时 | 创建 E2E 测试 |

### 文档生成
| 命令 | 类型 | 说明 |
|------|------|------|
| `/claudemd` | 即时 | 生成项目 CLAUDE.md |
| `/techdoc` | 即时 | 技术文档撰写 |
| `/create-page-doc` | 即时 | 页面双文档体系生成 |
| `/doc-clean` | 串行 | 文档清理归档 |

### 健康检查
| 命令 | 类型 | 说明 |
|------|------|------|
| `/health-check` | 即时 | 快速健康检查 |
| `/comprehensive-health-check` | DAG | 全面深度诊断 |

### UI 工程
| 命令 | 类型 | 说明 |
|------|------|------|
| `/ui-spec` | 即时 | 逆向生成功能规范文档 |
| `/ui-audit` | 即时 | 全局 UI 设计审计 |
| `/ui-redesign` | 即时 | 视觉重塑 + Flutter 落地 |
| `/ui-to-gemini` | 即时 | UI 截图转 Gemini 素材 |
| `/init-ui-showcase` | 即时 | Flutter UI 文档系统初始化 |

### 项目管理 & 工具
| 命令 | 类型 | 说明 |
|------|------|------|
| `/git-commit` | 即时 | Git 规范提交 |
| `/todo-write` | 串行 | 保存待办清单 |
| `/todo-doit` | 串行 | 执行待办任务 |
| `/todo-huge-task` | DAG | 大任务智能拆分 |
| `/screen` | 即时 | 截图分析辅助 |
| `/doc-update-context` | 串行 | docs/ 全量文档深度审查与修正 |

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

# 2. （可选）预览执行计划
python batchcc.py todo-task --dry-run

# 3. 执行（完全自动化）
python batchcc.py todo-task
```

### DAG 命令一览

| 命令 | 用途 |
|------|------|
| `/todo-huge-task` | 大任务拆分与编排 |
| `/comprehensive-health-check` | 项目全面体检 |
| `/refactor-project` | 项目级重构 |
| `/refactor-module` | 模块重构 |
| `/test-plan` | 测试规划与批量编写 |

> 详细格式参见 @templates/workflow/DAG_TASK_FORMAT.md

---

## 相关文档

| 文档 | 说明 |
|------|------|
| @CLAUDE.md | 命令设计指南 |
| @templates/workflow/DAG_TASK_FORMAT.md | DAG 任务格式规范 |
| @templates/workflow/DAG_EXAMPLE_*.md | DAG 任务示例 |
| @templates/docs/ | 文档模板 |

---

**命令总数**：29 个 | **设计原则**：目标导向、自主执行、单一真相源
