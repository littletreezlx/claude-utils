# Claude Code 命令系统

精简高效的斜杠命令库，遵循"**目标导向、自主执行**"设计理念。

## 🚀 快速开始

### 工作流选择

| 模式 | 适用场景 | 命令示例 |
|------|---------|---------|
| **即时执行** | 单一操作 | `/code-review`, `/gitcommit` |
| **串行任务** | 2-5 个线性任务 | `/todo-write` → `/todo-doit` |
| **DAG 任务** ⭐ | ≥3 个复杂任务 | `/todo-huge-task`, `/comprehensive-health-check` |

### 新手入门

1. 从即时执行命令开始：`/code-review`, `/gitcommit`
2. 尝试串行任务：`/todo-write` + `/todo-doit`
3. 掌握 DAG 任务：`/todo-huge-task`

---

## 📋 命令索引

### 🔍 代码质量
| 命令 | 说明 |
|------|------|
| `/code-review` | 代码审查 |

### ♻️ 代码重构
| 命令 | 说明 |
|------|------|
| `/refactor` | 简单重构（单文件） |
| `/refactor-module` | 模块重构（DAG） |
| `/refactor-project` | 项目级重构（DAG） |

### 📋 项目管理
| 命令 | 说明 |
|------|------|
| `/gitcommit` | Git 提交 |
| `/todo-write` | 生成待办清单 |
| `/todo-doit` | 执行待办任务 |
| `/todo-huge-task` | 大任务智能拆分（DAG）⭐ |

### 🔬 项目分析
| 命令 | 说明 |
|------|------|
| `/learn_new_project` | 快速学习新项目 |
| `/catchup` | 赶上项目进度 |
| `/e2e-readiness` | E2E 测试就绪检查 |

### 📚 文档生成
| 命令 | 说明 |
|------|------|
| `/claudemd` | 生成 CLAUDE.md |
| `/techdoc` | 生成技术文档 |
| `/create-page-doc` | 生成页面文档 |
| `/doc-organize` | 文档组织 |
| `/cleanup-docs` | 清理文档 |

### 💡 方案设计
| 命令 | 说明 |
|------|------|
| `/feat-discuss` | 功能方案讨论 |
| `/prd-to-doc` | PRD 转文档 |

### 🧪 测试
| 命令 | 说明 |
|------|------|
| `/test-plan` | 测试规划（DAG） |
| `/test-unit` | 单元测试 |
| `/test-integration` | 集成测试 |
| `/test-e2e` | E2E 测试 |
| `/create-e2e-test` | 创建 E2E 测试 |

### 🏥 健康检查
| 命令 | 说明 |
|------|------|
| `/health-check` | 快速健康检查 |
| `/comprehensive-health-check` | 全面健康检查（DAG）⭐ |

### 🛠️ 工具
| 命令 | 说明 |
|------|------|
| `/screen` | 截图分析 |
| `/init_ui_showcase` | UI 组件展示初始化 |

---

## 🤖 DAG 任务系统

### 什么是 DAG 任务？

DAG（有向无环图）任务编排是**完全自动化、无人值守**的任务执行模式。

### 核心特性

- ✅ **STAGE 阶段控制** - 串行/并行模式
- ✅ **TASK 任务单元** - 细粒度执行
- ✅ **文件冲突检测** - 自动分析，无冲突并行
- ✅ **断点续传** - 中断后自动继续
- ✅ **自动化保证** - batchcc 统一注入自动化指示

### 使用流程

```bash
# 1. 生成任务文件
/todo-huge-task "实现电商用户和订单系统"

# 2. （可选）预览执行计划
python batchcc.py todo-task --dry-run

# 3. 执行（完全自动化）
python batchcc.py todo-task
```

### DAG 命令

| 命令 | 用途 |
|------|------|
| `/todo-huge-task` | 大任务拆分与编排 |
| `/comprehensive-health-check` | 项目全面体检 |
| `/refactor-project` | 项目级重构 |
| `/refactor-module` | 模块重构 |
| `/test-plan` | 测试规划与批量编写 |

> 详细格式参见 @templates/workflow/DAG_TASK_FORMAT.md

---

## 📖 相关文档

| 文档 | 说明 |
|------|------|
| @CLAUDE.md | 命令设计指南 |
| @templates/workflow/DAG_TASK_FORMAT.md | DAG 任务格式规范 |
| @templates/workflow/DAG_EXAMPLE_*.md | DAG 任务示例 |
| @templates/docs/ | 文档模板 |

---

## 💡 最佳实践

- ✅ **Git 优先** - 每个功能完成后立即提交
- ✅ **失败即重置** - 失败 3 次考虑 `git reset --hard HEAD`
- ✅ **E2E 驱动** - 改代码 → 写测试 → 运行 → 验证
- ✅ **场景导航** - 根据任务类型选择合适命令

---

**命令总数**：27 个
**设计原则**：目标导向、自主执行、单一真相源
