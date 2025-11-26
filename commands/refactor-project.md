# 项目级重构（DAG 编排）

> 系统性重构项目架构，支持并行执行和断点续传

## 核心价值
- 🔄 自动断点续传（重构被中断可继续）
- ⚡ 并行重构独立模块（大幅提速）
- 📊 状态可视化（进度和耗时）
- 🛡️ 文件冲突检测（避免并发冲突）

---

## 🚀 使用方式

```bash
# 1. 生成重构任务（建议先运行健康检查）
/comprehensive-health-check  # 可选：先诊断
/refactor-project

# 2. 预览执行计划
python batchcc.py task-refactor-project --dry-run

# 3. 执行（自动断点续传）
git commit -am "Before refactor"
python batchcc.py task-refactor-project
```

---

## 🤖 自主执行原则

**⛔ 强制前置阅读**：执行任何操作前，必须先阅读 @templates/workflow/DAG_TASK_FORMAT.md 的"自主执行原则"章节，否则禁止继续。

**核心**：完全自动化、无人值守执行

✅ **应该做**：自主分析 → 自主决策方案 → 直接执行 → 记录理由
❌ **不应该**：询问用户、列架构选项让用户选

### 重构决策标准

| 自动决策 ✅ | 需标记失败 ❌ |
|------------|-------------|
| 拆分职责混乱的大类 | 多种架构模式同等可行 |
| 消除循环依赖 | 需要业务规则判断 |
| 重构重复代码 | 涉及重大技术栈变更 |
| 优化数据流 | 框架替换决策 |

**决策原则**：
- 够用的简单方案 > 完美的复杂方案
- 解决现存痛点，而非假想需求
- 每阶段测试验证，风险可控

---

## 📋 执行策略

### 第一步：分析项目
- 扫描项目结构和技术栈
- 读取核心文档（README, CLAUDE.md, PROJECT_STATUS.md）
- 诊断问题：模块划分、依赖关系、技术债务

### 第二步：生成任务编排文件

```
项目根目录/
├── task-refactor-project                # 主任务文件
└── .refactor-tasks/                     # 重构任务细节
    ├── stage-1-infrastructure.md        # 基础设施准备
    ├── stage-2-module-refactor.md       # 模块重构（并行）
    ├── stage-3-integration-test.md      # 集成测试
    └── stage-4-documentation.md         # 文档更新
```

**主任务文件格式**：

```markdown
## STAGE ## name="infrastructure" mode="serial"
@.refactor-tasks/stage-1-infrastructure.md

## STAGE ## name="module-refactor" mode="parallel" max_workers="4"
@.refactor-tasks/stage-2-module-refactor.md

## STAGE ## name="integration-test" mode="serial"
@.refactor-tasks/stage-3-integration-test.md

## STAGE ## name="documentation" mode="parallel" max_workers="2"
@.refactor-tasks/stage-4-documentation.md
```

### ⚠️ 子文件 TASK 格式（关键！）

被引用的子文件中，**每个任务必须使用 `## TASK ##` 标记**：

```markdown
# Stage 2: 模块重构

## TASK ##
重构用户模块

**📖 背景**：用户模块职责混乱，需要拆分...
**🔨 要做什么**：1. 拆分服务层 2. 优化数据访问...
**✅ 完成标志**：测试通过，无循环依赖

文件: src/modules/user/**/*.ts
排除: src/common/
验证: npm test -- user

## TASK ##
重构订单模块

...
```

**格式要点**：
- 使用 `## TASK ##`（注意两边都有 `##`）
- 任务标题在标记下一行
- `文件:` 字段必填（用于冲突检测）

### 第三步：各阶段任务设计

| 阶段 | 内容 | 执行模式 |
|------|------|---------|
| **Stage 1** 基础设施 | 测试环境、回滚方案、质量检查 | 串行 |
| **Stage 2** 模块重构 | 各模块独立重构 | **并行** |
| **Stage 3** 集成测试 | 完整测试套件、性能验证 | 串行 |
| **Stage 4** 文档更新 | 架构文档、功能映射、ADR | 并行 |

---

## 💎 严格禁止

1. **内嵌详细示例** ⛔ - 只说明任务类型和关注点
2. **硬编码具体命令** ⛔ - 让 AI 根据项目配置查找
3. **过度详细步骤** ⛔ - 描述目标和验证标准

**示例**：

```markdown
# ❌ 错误（内嵌完整重构示例）
Stage 2 任务示例：
\`\`\`markdown
## TASK: 重构用户模块
...50行详细内容...
\`\`\`

# ✅ 正确（只说明逻辑）
Stage 2 各模块任务应包含：
- 重构目标（解决什么问题）
- 文件范围（支持冲突检测）
- 验证命令（测试通过）
```

---

## 📏 字数约束

- **单个 TASK 描述**：20-40 行
- **每个 stage 文件**：80-150 行

---

## 🎯 重要约束

1. **分析优先** - 充分分析现状，识别核心问题
2. **测试驱动** - 每阶段测试验证，不过不进下一阶段
3. **不要过度设计** - 解决现有问题，不为"可能的未来"设计
4. **Git 里程碑** - 重构前确保工作区干净，方便回滚

---

## 相关文档
- @templates/workflow/DAG_TASK_FORMAT.md - 详细格式规范
- @comprehensive-health-check.md - 建议先运行健康检查
- `/refactor-module` - 单模块重构
- `/refactor` - 简单重构（单文件）
