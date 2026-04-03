# DAG 任务编排规范

> 所有 DAG 命令的**单一格式规范**。覆盖产出约定、STAGE/TASK 语法、任务描述标准、收尾模式。

---

## 快速开始

```bash
# 1. 生成任务文件（通过 DAG 命令）
/test-plan                          # 或 /refactor-project, /todo-huge-task 等

# 2. 预览执行计划
python batchcc.py task-xxx --dry-run

# 3. 执行（自动断点续传）
python batchcc.py task-xxx

# 4. 重新开始（清空状态）
python batchcc.py task-xxx --restart
```

---

## 产出约定

### 文件结构

| 文件 | 位置 | 说明 |
|------|------|------|
| `task-{名称}` | **项目根目录** | batchcc.py 入口文件，**不带** `.md` 后缀 |
| `.{名称}-tasks/*.md` | 项目根目录 | 任务细节文件（复杂任务时使用） |

**入口文件必须在项目根目录**，不是在子目录中。

### 命名约定

| 命令 | 入口文件 | 细节目录 |
|------|---------|---------|
| `/refactor-project` | `task-refactor-project` | `.refactor-tasks/` |
| `/test-plan` | `task-add-test` | `.test-tasks/` |
| `/comprehensive-health-check` | `task-health-check` | `.health-check-tasks/` |
| `/refactor-module` | `task-refactor-module-[模块名]` | — |
| `/todo-huge-task` | `task-{用户指定名}` | `.{名称}-tasks/` |
| `/doc-update-context` | `task-doc-review` | — |

### 入口文件必备结构

```markdown
# [任务名称]

> **项目宏观目标**：
> [描述项目的最终形态。batchcc 会提取这段话注入给每个子任务]

## STAGE ## name="..." mode="..."
...（业务任务）

## STAGE ## name="review" mode="serial"
...（收尾审视，见"收尾模式"章节）
```

---

## 核心概念

### STAGE（阶段）
粗粒度编排单元，定义执行模式。STAGE **按顺序**执行。

### TASK（任务）
细粒度执行单元，具体的工作项。

### 执行流程
```
Stage 1 [串行] → Stage 2 [并行] → ... → Stage N [收尾]
    ↓               ↓                        ↓
  Task 1          Task 2~4               全局审视
  Task 2          (并行执行)             → /todo-write
  (顺序执行)
```

---

## STAGE 语法

### 格式
```markdown
## STAGE ## name="阶段名称" mode="serial|parallel" max_workers="4"
```

### 参数

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `name` | string | ✅ | 阶段名称 | — |
| `mode` | enum | ✅ | `serial` 或 `parallel` | — |
| `max_workers` | int | ❌ | 最大并发数（仅 parallel） | 2 |

### 执行模式

| 模式 | 用途 | 特点 |
|------|------|------|
| `serial` | 有顺序依赖的任务 | 按顺序执行，前一个失败则停止 |
| `parallel` | 独立无依赖的任务 | 并发执行，自动冲突检测 |

---

## TASK 语法

### 格式

```markdown
## TASK ##
[任务标题]

**目标**：[一句话说明要达成什么]

**核心文件**：
- `src/xxx/target.ts` - [修改] 说明
- `src/xxx/ref.ts` - [参考]

**完成标志**：
- [ ] [可验证的标准]

文件: src/xxx/**/*.ts
排除: src/common/
验证: npm test -- xxx
```

**注意**：`## TASK ##` 两边都要有 `##`，解析器也兼容 `## TASK:` 但不推荐。

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| 目标 | ✅ | 一句话说明要达成什么 |
| 核心文件 | ✅ | 精确路径 + 操作类型（[修改]/[参考]/[新建]） |
| 完成标志 | ✅ | 客观可验证的标准 |
| 项目背景 | 可选 | 复杂任务时提供上下文 |
| 执行步骤 | 可选 | 需要时列出关键步骤 |
| `文件:` | 推荐 | glob 模式，用于并行冲突检测 |
| `排除:` | 可选 | 排除文件，避免误判冲突 |
| `验证:` | 推荐 | 任务完成后执行的验证命令 |

### 对比示例

```markdown
# ❌ 模糊
## TASK ##
优化用户模块
文件: src/modules/user/

# ✅ 清晰
## TASK ##
为用户模块添加统一错误处理

**目标**：所有 API 错误返回统一格式 { code, message, data }

**核心文件**：
- `src/modules/user/user.service.ts` - [修改] 使用标准错误类
- `src/common/errors.ts` - [参考] 查看错误类定义

**完成标志**：
- [ ] `npm test -- user` 全部通过

文件: src/modules/user/**/*.ts
验证: npm test -- user --silent
```

---

## 冲突检测

并行 STAGE 内的 TASK 自动检测 `文件:` 范围：

```markdown
# ✅ 无冲突（可并行）
文件: src/modules/user/**/*.ts    # TASK 1
文件: src/modules/order/**/*.ts   # TASK 2

# ⚠️ 有冲突（自动串行）
文件: src/modules/user/**/*.ts, src/common/types.ts   # TASK 1
文件: src/modules/order/**/*.ts, src/common/types.ts   # TASK 2
```

用 `排除:` 避免共享文件导致的误判。

### 文件范围语法

```markdown
# Glob 模式（推荐）
文件: src/modules/user/**/*.ts

# 精确路径（逗号分隔）
文件: src/config.ts, src/app.ts

# 多行定义
文件: src/modules/user/user.controller.ts
文件: src/modules/user/user.service.ts

# 排除规则
排除: src/common/, tests/
```

---

## 自主执行原则

DAG 任务设计为**无人值守**执行。batchcc.py 自动注入自主执行指示。

### ✅ 应该
1. 自主分析：深入理解任务目标和当前项目状态
2. 自主决策：基于优先级、影响面选择最优方案
3. 直接执行：不询问用户，直接实施
4. 记录理由：在日志中说明决策依据

### ❌ 不应该
1. 询问"需要我帮您...吗？"
2. 列出选项让用户选择
3. 等待用户确认

### 决策失败处理
真正无法决策时（如业务判断），标记任务 `failed`，说明原因和可选方案。

---

## 串行任务的上下文传递

串行 STAGE 内的任务可通过输入输出约定传递上下文：

```markdown
## TASK ##
导出旧系统数据

**输出状态**：
- ✅ 生成 data_export.json
- ➡️ 为下一任务提供：标准格式数据

## TASK ##
转换数据格式

**输入依赖**：
- ⬆️ 前一任务生成的 data_export.json
```

---

## 收尾模式（必须包含）

**每个 DAG 任务的最后一个 STAGE 必须是收尾审视**。

> **为什么**：DAG 任务跨多个 Agent 执行，中间上下文会丢失。收尾阶段是唯一能看到全局结果的机会，必须留痕。

```markdown
## STAGE ## name="review" mode="serial"

## TASK ##
全局审视与收尾

**目标**：纵观所有阶段产出，整体梳理，将剩余工作记录到 TODO.md

**执行步骤**：
1. 回顾所有已完成阶段的实际产出和变更
2. 评估整体完成度：哪些目标已达成？哪些有偏差？
3. 记录关键决策和背景（为什么这样做、遇到了什么问题）
4. 自问：这个任务还剩下什么？还有什么可以进一步优化？
5. 调用 /todo-write 将以下内容写入 TODO.md：
   - 本次任务的背景和执行摘要
   - 已完成的关键变更清单
   - 遗留问题和后续建议
   - 下一步可执行的行动项

**完成标志**：
- [ ] TODO.md 已通过 /todo-write 更新

文件: TODO.md
验证: test -f TODO.md
```

---

## 常见错误

| 错误 | 正确 |
|------|------|
| `## STAGE 1` | `## STAGE ## name="xxx" mode="serial"` |
| `mode="sequential"` | `mode="serial"` |
| `### TASK` 或 `## TASK:` | `## TASK ##` |
| 入口文件放在子目录 | 入口文件放在**项目根目录** |
| 入口文件带 `.md` 后缀 | 不带 `.md` 后缀 |
| 缺少 `文件:` 字段 | 并行任务必须有 `文件:` |
| 缺少收尾 STAGE | 最后必须有 `name="review"` 收尾 |
| 缺少项目宏观目标 | 入口文件开头必须有 |

---

## 常见编排模式

### 模式 1：基础设施 → 并行开发 → 测试 → 收尾

```markdown
## STAGE ## name="init" mode="serial"
## STAGE ## name="dev" mode="parallel" max_workers="4"
## STAGE ## name="test" mode="serial"
## STAGE ## name="review" mode="serial"
```

### 模式 2：独立任务批量执行 → 收尾

```markdown
## STAGE ## name="batch" mode="parallel" max_workers="8"
## STAGE ## name="review" mode="serial"
```

### 模式 3：串行流水线 → 收尾

```markdown
## STAGE ## name="phase-1" mode="serial"
## STAGE ## name="phase-2" mode="serial"
## STAGE ## name="review" mode="serial"
```

---

## 相关文档

| 文档 | 用途 |
|------|------|
| `DAG_TASK_TEMPLATE.md` | 空白模板（可直接复制） |
| `DAG_EXAMPLE_ECOMMERCE.md` | 电商系统示例 |
| `DAG_EXAMPLE_MIGRATION.md` | 数据迁移示例 |
| `REFACTOR_TASK_TEMPLATE.md` | 重构任务模板 |
| `HEALTH_CHECK_TASK_TEMPLATE.md` | 健康检查任务模板 |
| `TEST_PLAN_TEMPLATE.md` | 测试计划模板 |
