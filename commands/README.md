# 🛠️ Claude Code 命令系统

精简高效的斜杠命令库，遵循"**目标导向、自主执行**"的设计理念。

## 🎯 核心价值

### 三种工作流模式

根据任务复杂度选择合适的工作流：

| 模式 | 适用场景 | 特点 | 示例命令 |
|------|---------|------|---------|
| **即时执行型** | 单一操作 | 简单快速，即时反馈 | `/code-review`, `/gitcommit` |
| **串行任务型** | 2-5个串行任务 | 支持断点续传 | `/todo-write` + `/todo-doit` |
| **DAG 任务型** ⭐ | ≥3个复杂任务 | 并行执行 + 自动化编排 | `/todo-huge-task`, `/comprehensive-health-check` |

### 🤖 DAG 自动化保证机制

**系统性保证完全自动化执行**：

```
命令生成任务 → batchcc.py 调度 → 自动注入自动化指示 → Claude 完全自主执行
                                  ↑
                             关键创新点！
```

**核心机制**：
- `batchcc.py` 在调用 Claude 执行每个任务时，自动在任务描述前注入"自动化执行指示"
- 确保每个任务都明确告知 Claude"这是自动化任务，不要询问用户"
- 不依赖任务文件的自动化描述或 Claude 的"记忆"

**好处**：
1. ✅ 系统性保证自动化（不会中途询问用户）
2. ✅ 单一真相源（规范只在 batchcc 中定义）
3. ✅ 防御性设计（每次调用都强制传递）
4. ✅ 降低命令文件复杂度

---

## 📋 命令分类

### 🔍 代码质量
- `/code-review` - 代码审查

### ♻️ 代码重构
- `/refactor` - 简单重构（单个文件）
- `/refactor-module` - 模块重构（DAG 模式）
- `/refactor-project` - 项目级重构（DAG 模式）

### 📋 项目管理
- `/gitcommit` - Git 提交
- `/todo-write` - 生成待办清单
- `/todo-doit` - 执行待办任务
- `/todo-huge-task` - 大任务智能拆分（DAG 模式）⭐

### 🔬 项目分析
- `/learn_new_project` - 快速学习新项目
- `/catchup` - 赶上项目进度
- `/e2e-readiness` - E2E 测试就绪检查

### 📚 文档生成
- `/claudemd` - 生成 CLAUDE.md
- `/techdoc` - 生成技术文档
- `/create-page-doc` - 生成页面文档
- `/doc-organize` - 文档组织

### 🧹 文档清理
- `/cleanup-docs` - 清理文档

### 💡 方案设计
- `/feat-discuss` - 功能方案讨论

### 📄 需求处理
- `/prd-to-doc` - PRD 转文档

### 🧪 测试
- `/test-plan` - 测试规划（DAG 模式）
- `/test-unit` - 单元测试
- `/test-integration` - 集成测试
- `/test-e2e` - E2E 测试
- `/create-e2e-test` - 创建 E2E 测试

### 🏥 健康检查
- `/health-check` - 快速健康检查
- `/comprehensive-health-check` - 全面健康检查（DAG 模式）⭐

---

## 🚀 DAG 任务系统

### 什么是 DAG 任务？

DAG（Directed Acyclic Graph）任务编排是一种**完全自动化、无人值守**的任务执行模式。

### 核心特性

- ✅ **STAGE 粗粒度编排**：串行/并行阶段控制
- ✅ **TASK 细粒度单元**：具体任务定义
- ✅ **文件冲突检测**：自动分析，无冲突并行执行
- ✅ **自动断点续传**：中断后自动继续
- ✅ **状态管理**：完整的执行状态和耗时记录
- ✅ **智能调度**：根据依赖和冲突优化执行
- ✅ **自动化保证**：batchcc 统一注入自动化指示

### 使用流程

```bash
# 1. 运行命令生成任务文件
/todo-huge-task "实现电商用户和订单系统"

# 2. （可选）预览执行计划
python batchcc.py todo-task --dry-run

# 3. 执行任务（完全自动化）
python batchcc.py todo-task

# 4. 中断后继续（自动从断点恢复）
python batchcc.py todo-task
```

### DAG 命令列表

| 命令 | 用途 | 适用场景 |
|------|------|---------|
| `/todo-huge-task` | 大任务拆分与编排 | 多模块开发、大型重构 |
| `/comprehensive-health-check` | 项目全面体检 | 定期检查、接手项目 |
| `/refactor-project` | 项目级重构 | 架构调整、技术栈升级 |
| `/refactor-module` | 模块重构 | 单模块优化 |
| `/test-plan` | 测试规划与批量编写 | 补充测试、测试重构 |

---

## 🔒 自动化保证机制

### 问题：为什么需要自动化保证？

即使命令文件强调"完全自动化"，但如果 Claude 在执行任务时不知道"这是自动化任务"，可能又开始询问用户：

```
❌ 错误行为：
分析发现3个问题，需要我：
1. 修复配置？
2. 更新文档？
3. 重构代码？
请告诉我从哪里开始！
```

### 解决方案：batchcc 统一注入

**实现方式**：
```python
# batchcc.py 在调用 Claude 时自动添加
automation_prefix = """
⚠️ DAG 自动化任务执行模式

你正在执行通过 batchcc.py 编排的自动化任务。

🤖 必须：完全自主执行，不询问用户
❌ 禁止：询问、列选项、等待确认
"""

enhanced_content = automation_prefix + task_description
claude_cmd = ["claude", "-p", enhanced_content, ...]
```

**效果**：
```
✅ 正确行为：
分析发现3个问题：
1. 配置缺失（阻塞性）
2. 文档过时（中等影响）
3. 代码冗余（低优先级）

决策：优先修复配置缺失，因为这会阻塞其他功能。

正在创建配置文件...
✅ 配置文件已创建

接下来更新文档...
✅ 文档已更新
```

### 价值

1. **系统性保证** - 每个任务都强制传递自动化指示
2. **单一真相源** - 规范只在 batchcc 中定义
3. **防御性设计** - 不依赖 Claude 的"记忆"
4. **降低复杂度** - 命令文件不需要重复写自动化规范

---

## 📖 文档系统

### 核心文档

- **CLAUDE.md** - 命令设计指南和使用说明
- **templates/** - 文档和工作流模板
  - `docs/` - README、TECHNICAL 文档模板
  - `workflow/` - DAG 任务格式和示例

### 场景驱动导航

| 我要做什么 | 应该读什么 |
|----------|----------|
| 🆕 添加新功能 | E2E测试规范 + API规范 |
| 🐛 修复 Bug | 项目状态快照 → 相关测试 |
| ♻️ 重构代码 | 测试策略 + ADR 索引 |
| 🔍 理解项目 | 项目状态快照 → 功能映射 |

---

## 💡 核心理念

### 1. 目标导向，而非步骤模板

**❌ 不要**：提供详细的步骤模板
**✅ 应该**：明确目标和约束，让 AI 自主决策

### 2. 完全自动化、无人值守

**DAG 任务系统**：
- 生成任务后直接输出执行命令
- 不等待用户审查
- batchcc 保证每个任务都自动化执行

### 3. 单一真相源

**自动化规范**：只在 batchcc 中定义
**格式规范**：只在 DAG_TASK_FORMAT.md 中定义
**命令文件**：专注描述任务目标和约束

### 4. 务实的质量标准

- 可维护 > 完美
- 能扩展 > 通用
- 够用即可，适度抽象

---

## 🎓 使用建议

### 新手入门

1. 从即时执行型命令开始（`/code-review`, `/gitcommit`）
2. 尝试串行任务型（`/todo-write` + `/todo-doit`）
3. 掌握 DAG 任务型（`/todo-huge-task`, `/comprehensive-health-check`）

### 高级用法

1. **大型重构**：`/comprehensive-health-check` → `/refactor-project`
2. **多模块开发**：`/todo-huge-task` + 并行执行
3. **测试补充**：`/test-plan` + 自动化编写

### 最佳实践

- ✅ Git 优先：每个功能完成后立即提交
- ✅ 失败即重置：失败3次立即 `git reset --hard HEAD`
- ✅ E2E 驱动：改代码 → 写测试 → 运行 → 验证
- ✅ 场景驱动导航：根据任务类型查阅对应文档

---

## 📚 相关文档

- **CLAUDE.md** - 命令设计指南（必读）
- **templates/workflow/DAG_TASK_FORMAT.md** - DAG 任务格式规范
- **templates/workflow/DAG_EXAMPLE_*.md** - DAG 任务示例
- **archived/** - 历史决策和实验记录

---

## 🔄 版本历史

### 最新版本（2025-11-18）

**重大改进**：
- ✅ 添加 batchcc 自动化保证机制
- ✅ 修复命令文件中的"等待用户审查"矛盾
- ✅ 优化命令文件（精简 21-39%）
- ✅ 统一 DAG 任务的自动化规范

**核心价值**：
- 系统性保证 DAG 任务完全自动化执行
- 不会中途询问用户
- 降低命令文件复杂度

---

**维护者**：Claude Code AI
**命令总数**：25 个核心命令
**设计原则**：目标导向、自主执行、单一真相源

---

*基于 YC Vibe Coding Guide 和实践经验持续优化*
