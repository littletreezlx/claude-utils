# batchcc.py - DAG 任务编排支持

> 简化版 DAG 格式，专注核心价值：串行/并行控制 + 文件冲突检测

## 🎯 核心特性

### ✅ 保留的功能
1. **STAGE 串行/并行控制** - 最核心的价值
2. **文件冲突检测** - 自动识别可并行的任务
3. **执行计划预览** - `--dry-run` 查看执行计划

### ❌ 简化掉的功能
1. **复杂依赖关系** - STAGE 按顺序执行，无需 depends_on
2. **失败策略** - 任何失败都停止，简单直接
3. **断点续传** - 失败了重新跑，AI 执行快
4. **Task ID** - 不需要复杂的任务引用
5. **重试机制** - 失败就失败，重新执行即可

## 📋 简化的 DAG 格式

### 基础格式

```markdown
## STAGE ## name="阶段名" mode="serial"
# 🎯 阶段目标：[阶段的核心目标]
# 📥 输入：[阶段需要的输入]
# 📤 输出：[阶段产生的输出]
# 🔗 为下一阶段提供：[传递给下一阶段的内容]

## TASK ##
[任务标题]

**📖 背景**：
[为什么要做这个任务？解决什么问题？]

**🔨 要做什么**：
1. [具体步骤1]
2. [具体步骤2]
3. [具体步骤3]

**✅ 完成标志**：
- [ ] [如何判断任务完成？]
- [ ] [验证标准]

文件: 文件范围（可选，用于冲突检测）
排除: 排除文件（可选）

## STAGE ## name="阶段名" mode="parallel" max_workers="4"
# 🎯 阶段目标：[并行开发多个模块]

## TASK ##
[任务标题]

**📖 背景**：...
**🔨 要做什么**：...
**✅ 完成标志**：...

文件: src/modules/user/**/*.ts
排除: src/common/

## TASK ##
[任务标题]

**📖 背景**：...
**🔨 要做什么**：...
**✅ 完成标志**：...

文件: src/modules/order/**/*.ts
排除: src/common/
```

### 参数说明

#### STAGE 参数
- `name` (必填): 阶段名称
- `mode` (必填): `serial` 或 `parallel`
- `max_workers` (可选): 最大并发数，默认 4（仅 parallel 模式）

#### TASK 字段
- **任务标题** (第一行): 简短描述任务内容
- **📖 背景** (必填): 为什么要做这个任务，解决什么问题
- **🔨 要做什么** (必填): 具体的执行步骤（带编号）
- **✅ 完成标志** (必填): 如何判断任务完成
- **📥 输入依赖** (串行任务): 依赖前一任务的什么状态
- **📤 输出状态** (串行任务): 完成后的状态，为下一任务提供什么
- `文件:` (可选): 文件范围，用于冲突检测
- `排除:` (可选): 排除的文件，避免误判冲突

## 🚀 使用方式

### 1. 预览执行计划

```bash
python batchcc.py <dag-file> --dry-run
```

### 2. 执行任务（自动断点续传）

```bash
# 正常执行
python batchcc.py <dag-file>

# 行为：
# - 有未完成任务 → 自动从断点继续
# - 没有状态文件 → 从头开始
# - 就这么简单！

# 如果想重新开始
python batchcc.py <dag-file> --restart

# 或者手动删除状态文件
rm <dag-file>.state.json
python batchcc.py <dag-file>
```

### 3. 状态文件

执行过程中会自动生成状态文件：`<dag-file>.state.json`

状态文件记录：
- 每个阶段的完成状态
- 每个任务的完成状态、开始时间、结束时间、耗时
- 失败任务的错误信息

**示例状态文件**：
```json
{
  "task_file": "todo-task",
  "start_time": "2025-11-13T10:30:00",
  "last_update": "2025-11-13T10:45:00",
  "overall_status": "in_progress",
  "stages": [
    {
      "stage_id": 0,
      "name": "初始化",
      "status": "completed",
      "start_time": "2025-11-13T10:30:00",
      "end_time": "2025-11-13T10:35:00",
      "duration": 300.0,
      "tasks": [...]
    },
    {
      "stage_id": 1,
      "name": "业务模块",
      "status": "failed",
      "tasks": [
        {
          "task_id": 1,
          "status": "completed",
          "duration": 180.0
        },
        {
          "task_id": 2,
          "status": "failed",
          "error": "API测试失败"
        },
        {
          "task_id": 3,
          "status": "pending"
        }
      ]
    }
  ]
}
```

### 5. 原有预览方式（已废弃）

**输出示例**：
```
📊 DAG 执行计划
================================================================================
文件: test-dag-simple.md
阶段数: 3
总任务数: 5

Stage 1: 准备 [SERIAL]
────────────────────────────────────────────────────────────────────────────────
模式: 串行执行
任务数: 1

  → Task 1: 创建测试目录

Stage 2: 并行创建文件 [PARALLEL]
────────────────────────────────────────────────────────────────────────────────
模式: 并行执行（最大 3 并发）
任务数: 3
并行批次: 1

    - Task 1: 创建文件 A
    - Task 2: 创建文件 B
    - Task 3: 创建文件 C
```

### 4. 自动格式检测

`batchcc.py` 会自动检测文件格式：
- **包含 `## STAGE ##`** → DAG 模式（支持断点续传）
- **只有 `## TASK ##`** → 简单模式（原有功能）

## 🔍 文件冲突检测

### 检测规则（保守策略）

#### 1. 精确匹配
```markdown
## TASK ##
文件: src/common/types.ts

## TASK ##
文件: src/common/types.ts

→ 冲突！（同一文件）
```

#### 2. 目录重叠（带通配符）
```markdown
## TASK ##
文件: src/modules/**/*.ts

## TASK ##
文件: src/modules/**/*.js

→ 冲突！（相同目录下的通配符）
```

#### 3. 无冲突示例
```markdown
## TASK ##
文件: src/modules/user/**/*.ts
排除: src/common/

## TASK ##
文件: src/modules/order/**/*.ts
排除: src/common/

→ 无冲突！（不同子目录）
```

```markdown
## TASK ##
文件: /tmp/dag_test/file_a.txt

## TASK ##
文件: /tmp/dag_test/file_b.txt

→ 无冲突！（不同具体文件）
```

### 使用排除避免误判

```markdown
## TASK ##
文件: src/modules/user/**/*.ts
排除: src/modules/user/**/*.test.ts
排除: src/common/

## TASK ##
文件: src/modules/user/**/*.test.ts

→ 无冲突！（通过排除分离了文件范围）
```

## 📊 执行流程

```
1. 解析 DAG 文件
   ├─ 提取 STAGE 和 TASK
   └─ 验证格式和参数

2. 顺序执行 STAGE
   ├─ Stage 1 (serial) → 任务顺序执行
   ├─ Stage 2 (parallel)
   │  ├─ 检测文件冲突
   │  ├─ 创建并行批次
   │  └─ 批次内并行，批次间串行
   └─ Stage 3 (serial) → 任务顺序执行

3. 任何失败都停止
   └─ 简单直接，失败重新跑
```

## 💡 设计理念

### 为什么需要状态管理？

1. **大任务常中断** - 执行几十个任务可能要几小时，中间可能失败
2. **节省时间** - 已完成的任务不用重复执行
3. **排查问题** - 可以清楚看到在哪个任务失败，失败原因是什么
4. **灵活控制** - 可以从任意阶段重新开始

### 核心特性

**已实现**：
- ✅ 自动断点续传 - 任务中断后从断点继续
- ✅ 任务完成标记 - 每个任务完成后立即保存状态
- ✅ 失败信息记录 - 记录失败原因，方便排查
- ✅ 执行时间统计 - 记录每个任务和阶段的耗时
- ✅ 灵活控制选项 - 支持重新开始、跳过、清空状态
- ✅ 串行/并行混合 - 根据冲突自动调度
- ✅ 文件冲突检测 - 避免并发修改冲突

**使用场景**：
- 🎯 多模块并行开发（用户、订单、支付模块同时开发）
- 🎯 大规模重构（几十个文件需要重构）
- 🎯 数据迁移（多个数据源并行迁移）
- 🎯 完整系统开发（前后端、测试、部署多阶段）

## 🎓 实际示例

### 电商系统开发

```markdown
## STAGE ## name="初始化" mode="serial"
# 🎯 阶段目标：创建数据库架构
# 📥 输入：空白数据库
# 📤 输出：完整的表结构
# 🔗 为下一阶段提供：可以开始业务开发的数据库环境

## TASK ##
创建数据库表

**📖 背景**：
系统需要用户、订单、支付三个核心表，作为业务模块的基础

**🔨 要做什么**：
1. 创建用户表（users）- 包含 id, name, email, created_at
2. 创建订单表（orders）- 包含 id, user_id, amount, status
3. 创建支付表（payments）- 包含 id, order_id, method, status
4. 运行迁移脚本验证表结构

**✅ 完成标志**：
- [ ] 所有表创建成功
- [ ] 外键关系正确
- [ ] 运行 `npm run migrate:verify` 通过

文件: migrations/

## STAGE ## name="业务模块" mode="parallel" max_workers="4"
# 🎯 阶段目标：并行开发三个业务模块
# 📥 输入：数据库架构
# 📤 输出：完整的业务模块代码

## TASK ##
实现用户模块

**📖 背景**：
用户模块是系统基础，提供注册、登录、个人信息管理功能

**🔨 要做什么**：
1. 创建 User 实体和 Repository
2. 实现注册、登录、更新个人信息 API
3. 编写单元测试（覆盖率 > 80%）

**✅ 完成标志**：
- [ ] 所有 API 端点测试通过
- [ ] 代码覆盖率达标

文件: src/modules/user/**/*.ts
排除: src/common/

## TASK ##
实现订单模块

**📖 背景**：
订单模块处理用户下单、查询订单、修改订单状态的业务逻辑

**🔨 要做什么**：
1. 创建 Order 实体和 Repository
2. 实现创建订单、查询订单、更新状态 API
3. 编写单元测试和集成测试

**✅ 完成标志**：
- [ ] CRUD 功能完整
- [ ] 测试通过

文件: src/modules/order/**/*.ts
排除: src/common/

## TASK ##
实现支付模块

**📖 背景**：
支付模块对接支付网关，处理支付和退款业务

**🔨 要做什么**：
1. 创建 Payment 实体和 Repository
2. 实现支付、退款、查询支付状态 API
3. 集成测试使用模拟支付网关

**✅ 完成标志**：
- [ ] 支付流程完整
- [ ] 退款逻辑正确

文件: src/modules/payment/**/*.ts
排除: src/common/

## STAGE ## name="测试" mode="serial"
# 🎯 阶段目标：验证系统集成

## TASK ##
运行集成测试

**📥 输入依赖**：
- ⬆️ 前一阶段完成的用户、订单、支付模块

**📖 背景**：
验证三个模块集成后的完整业务流程（注册→下单→支付）

**🔨 要做什么**：
1. 启动测试数据库
2. 运行端到端测试：用户注册→创建订单→支付成功
3. 验证数据一致性

**✅ 完成标志**：
- [ ] E2E 测试全部通过
- [ ] 无数据不一致问题

文件: tests/integration/
```

**执行效果**：
- Stage 1: 串行创建数据库（必须先完成）
- Stage 2: 3 个模块并行开发（无冲突，同时进行）
- Stage 3: 串行运行测试（依赖前面所有模块完成）

## 🔧 技术实现

### 文件结构

```
claude-code/
├── batchcc.py              # 主入口（支持 DAG 格式）
├── dag_parser.py           # DAG 文件解析器（~250 行）
├── dag_executor.py         # DAG 执行引擎（~280 行）
└── batch_executor_base.py  # 基础执行器（复用）
```

### 核心类

```python
# dag_parser.py
class DAGParser:
    """解析 STAGE 和 TASK"""
    def parse() -> List[StageNode]

class ConflictDetector:
    """检测文件冲突，创建并行批次"""
    def detect_conflicts(tasks) -> Dict
    def create_batches(tasks, conflicts) -> List[List[Task]]

# dag_executor.py
class DAGExecutor:
    """顺序执行 STAGE，STAGE 内根据 mode 选择串行/并行"""
    def execute() -> bool
    def print_plan()  # --dry-run
```

## 📝 命令文档更新

`/todo-huge-task` 命令的文档（`~/.claude/commands/templates/workflow/`）已更新：

- **DAG_TASK_FORMAT.md** - 完整格式规范（保留复杂版说明）
- **DAG_QUICK_START.md** - 快速开始（更新为简化版）
- **DAG_EXAMPLE_*.md** - 示例文件（简化版格式）

**推荐用法**：
- 使用 `/todo-huge-task` 生成 DAG 文件
- Claude Code 会自动生成简化格式
- 运行 `python batchcc.py todo-task --dry-run` 预览
- 运行 `python batchcc.py todo-task` 执行

## 🐛 故障排查

### 解析失败

**错误**: `缺少必需参数: name`
- **原因**: STAGE 缺少 `name` 或 `mode` 参数
- **修复**: 确保每个 `## STAGE ##` 都有 `name="..."` 和 `mode="..."`

**错误**: `未找到任何 STAGE 定义`
- **原因**: 文件中没有 `## STAGE ##` 标记
- **修复**: 确保文件使用 DAG 格式，或使用简单格式（只有 `## TASK ##`）

### 冲突检测问题

**任务应该并行却串行执行**：
- 检查文件范围是否重叠
- 使用 `--dry-run` 查看冲突信息
- 使用 `排除:` 字段明确分离文件范围

**任务应该串行却并行执行**：
- 将任务放在 `mode="serial"` 的 STAGE 中
- 或者确保文件范围有重叠（会自动检测冲突）

---

**版本**: v1.0 (简化版)
**更新日期**: 2025-11-10
**总代码量**: ~530 行（parser + executor）
