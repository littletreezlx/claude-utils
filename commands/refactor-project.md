---
description: 项目级重构（DAG 编排）ultrathink
---

# 项目级重构（DAG 编排）

> 系统性重构项目架构，支持并行执行和断点续传

## 使用方式

```bash
/comprehensive-health-check              # 可选：先诊断
/refactor-project                        # 生成重构任务
python batchcc.py task-refactor-project --dry-run  # 预览
python batchcc.py task-refactor-project  # 执行
```

---

## 自主执行原则

> **强制阅读**：@templates/workflow/DAG_TASK_FORMAT.md
>
> 核心：自主分析 → 自主决策 → 直接执行 → 记录理由（不询问用户）

---

## AI 可维护性优先（核心原则）

> AI 不嫌文件大，嫌文件多且分散。理解 500 行内聚代码 < 跳 5 个 60 行文件组装逻辑。

### 重构判断标准

| 判断维度 | 生成任务 | 不生成任务 |
|---------|----------|-----------|
| 职责是否单一？ | 混乱 → 拆分 | 单一 → 保持 |
| 是否会被复用？ | 会 → 提取组件 | 仅一处用 → 保持内聚 |
| 有循环依赖？ | 有 → 消除 | 无 → 不动 |
| 代码重复？ | 有 → 统一 | 无 → 不动 |
| **文件行数** | **不作为判断依据** | - |

### 判断流程

```
读取文件 → 理解职责 →
├── 职责单一且内聚？→ 保持原状（不管行数）
├── 职责混乱？→ 按职责拆分（不是按行数切）
└── 有可复用的部分？→ 提取到共享位置
```

---

## 执行策略

### 第一步：充分探索项目

**规划质量决定执行效率**：
- 阅读核心文档（README、CLAUDE.md、PROJECT_STATUS.md）
- 浏览项目结构，理解模块划分和依赖关系
- 查找 TODO/FIXME 注释（真实痛点）
- 按优先级识别：职责混乱 > 循环依赖 > 代码重复

### 第二步：生成任务编排文件

```
task-refactor-project                    # 主任务文件
.refactor-tasks/                         # 重构任务细节
├── stage-1-module-refactor.md          # 模块重构（并行）
├── stage-2-integration.md              # 集成验证（串行）
└── stage-3-documentation.md            # 文档更新（并行）
```

### 第三步：各阶段设计

| 阶段 | 内容 | 执行模式 |
|------|------|---------|
| Stage 1 | 各模块独立重构（每个任务自带测试验证）| **并行** max_workers=4 |
| Stage 2 | 全量测试 + 跨模块集成检查 | 串行 |
| Stage 3 | 架构文档、功能映射、ADR | 并行 |

> TASK 格式参照 @templates/workflow/DAG_TASK_FORMAT.md

---

## 重要约束

1. **职责优先于行数** - 职责单一的大文件 > 职责混乱的多个小文件
2. **内聚优先于复用** - 不复用的代码提取反而增加复杂度
3. **测试驱动** - 每阶段测试验证，不过不进下一阶段
4. **不要过度设计** - 解决现有问题，不为"可能的未来"设计

## 严格禁止

1. **以行数为目标** - `行数 ≤ 200` 不是重构目标
2. **机械拆分** - 只在职责混乱时拆分
3. **为复用而复用** - 提取不复用的组件是过度设计

---

## 相关文档

- @templates/workflow/DAG_TASK_FORMAT.md - 格式规范
- `/comprehensive-health-check` - 建议先运行健康检查
- `/refactor-module` - 单模块重构
- `/refactor` - 简单重构（单文件）
