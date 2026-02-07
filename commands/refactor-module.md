---
description: 模块重构（DAG）ultrathink
---

# 模块级重构

> 单个模块内的职责优化和数据流重构，DAG 任务编排 + 断点续传

## 使用方式

```bash
/refactor-module "模块名"                                  # 生成任务
python batchcc.py task-refactor-module-[模块名] --dry-run  # 预览
python batchcc.py task-refactor-module-[模块名]            # 执行
```

---

## 自主执行原则

> **强制阅读**：@templates/workflow/DAG_TASK_FORMAT.md
>
> 核心：自主分析 → 自主决策 → 直接执行 → 记录理由（不询问用户）
>
> 决策失败时：标记 `failed`，说明原因和可选方案

---

## 阶段编排

| 阶段 | 内容 | 模式 |
|------|------|------|
| Stage 1 | 分析模块文件、识别问题、制定重构计划 | serial |
| Stage 2 | 拆分职责、消除循环依赖、优化接口 | serial |
| Stage 3 | 运行模块测试、验证接口兼容性 | serial |
| Stage 4 | 更新 docs/ARCHITECTURE.md、docs/FEATURE_CODE_MAP.md | serial |

**生成文件结构**：
```
task-refactor-module-[模块名]               # 主任务文件
.refactor-tasks/module-[模块名]/            # 阶段详情
├── stage-1-analysis.md
├── stage-2-refactor.md
├── stage-3-test.md
└── stage-4-documentation.md
```

> TASK 格式参照 @templates/workflow/DAG_TASK_FORMAT.md

---

## 决策标准

### 自动决策（无需询问）

| 情况 | 决策 |
|------|------|
| 职责混乱 | 按职责拆分（方法数量不作为依据）|
| 循环依赖 | 引入抽象层打破循环 |
| 重复代码 | 提取到工具类（有明确复用场景）|

### 标记失败

- 多种拆分方式同等合理
- 需要业务规则判断
- 涉及跨模块数据迁移

---

## 重要约束

1. **模块边界** - 仅重构单个模块，不调整跨模块关系
2. **测试驱动** - 重构前后都运行测试
3. **不要过度设计** - 解决现有问题，不为未来设计
4. **Git 安全** - 重构前确保工作区干净

## 何时升级

- 需要调整多模块协作 → `/refactor-project`
- 只需单文件优化 → `/refactor`

## 相关文档

- @templates/workflow/DAG_TASK_FORMAT.md - 格式规范
- `/refactor-project` - 项目级重构（多模块）
