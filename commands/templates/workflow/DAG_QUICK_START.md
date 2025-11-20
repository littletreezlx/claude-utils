# DAG 任务编排系统 - 快速开始

> 5 分钟快速上手 `/todo-huge-task` + `batchcc.py`

## 🎯 什么时候用？

**适合的场景** ✅
- 多个独立模块的开发（用户、订单、支付、商品）
- 大规模重构（多个模块同时重构）
- 批量任务执行（多个测试、多个迁移脚本）
- 需要并行提升效率的任务

**不适合的场景** ❌
- 任务数少于 3 个 → 用 `/todo-write`
- 严格串行流程 → 用 `/todo-write`
- 高度耦合任务 → 用 `/todo-write`

---

## 🚀 三步上手

### Step 1: 生成任务文件

```bash
/todo-huge-task "实现用户和订单管理模块"
```

Claude Code 会自动：
- 分析任务拆分点
- 识别可并行的部分
- 生成 `todo-task` 文件

### Step 2: 预览执行计划（可选但推荐）

```bash
python batchcc.py todo-task --dry-run
```

输出示例：
```
📊 执行计划概览:
├─ Stage 1: 初始化 [SERIAL]
│  └─ Task 1: 创建数据库表
│
├─ Stage 2: 业务模块 [PARALLEL x4]
│  ├─ Task 2: 用户模块 (files: src/modules/user/)
│  └─ Task 3: 订单模块 (files: src/modules/order/)
│
└─ Stage 3: 测试 [SERIAL]
   └─ Task 4: 集成测试

⏱️ 预计: 20 分钟
⚠️ 注意: Task 4 依赖 Task 2, 3
```

### Step 3: 执行任务

```bash
# 完整执行
python batchcc.py todo-task

# 如果失败，修复后重新执行
python batchcc.py todo-task
```

---

## 📋 核心概念（2 分钟理解）

### STAGE（阶段）
**粗粒度控制**，定义一组任务的执行方式。

```markdown
## STAGE ## name="业务模块" mode="parallel" max_workers="4"
```

- `mode="serial"` → 阶段内任务依次执行
- `mode="parallel"` → 阶段内任务并发执行
- **STAGE 按顺序执行** - 无需 depends_on

### TASK（任务）
**细粒度单元**，具体要做的事。

```markdown
## TASK ##
实现用户管理 API

**📖 背景**：
用户模块是系统的基础，需要提供完整的用户管理功能

**🔨 要做什么**：
1. 创建用户相关的数据模型
2. 实现 CRUD API 接口
3. 编写单元测试和集成测试

**✅ 完成标志**：
- [ ] 所有 API 测试通过
- [ ] 代码覆盖率 > 80%

文件: src/modules/user/**/*.ts
排除: src/common/
```

- **详细的任务描述** - 包含背景、步骤、完成标志
- `文件:` → 冲突检测（同一文件的任务会串行）
- `排除:` → 避免误判冲突
- **任何失败都停止** - 简单直接

---

## 🎨 三种常见模式

### 模式 1：基础设施 → 并行开发 → 集成测试

```markdown
## STAGE ## name="初始化" mode="serial"
# 🎯 阶段目标：创建数据库架构
# 📥 输入：空白数据库
# 📤 输出：完整的表结构
# 🔗 为下一阶段提供：可以开始业务开发的数据库环境

## TASK ##
创建数据库表

**📖 背景**：...
**🔨 要做什么**：...
**✅ 完成标志**：...

## STAGE ## name="开发" mode="parallel" max_workers="4"
# 🎯 阶段目标：并行开发各业务模块
# 📥 输入：数据库架构
# 📤 输出：完整的业务模块代码

## TASK ##
用户模块

**📖 背景**：...
（详细任务描述）

## TASK ##
订单模块

## TASK ##
支付模块

## STAGE ## name="测试" mode="serial"
# 🎯 阶段目标：验证系统集成

## TASK ##
集成测试

**📥 输入依赖**：
- ⬆️ 前一阶段完成的所有业务模块
（详细任务描述）
```

### 模式 2：独立任务批量执行

```markdown
## STAGE ## name="重构模块" mode="parallel" max_workers="8"
## TASK ## 重构模块 A
## TASK ## 重构模块 B
## TASK ## 重构模块 C
## TASK ## 重构模块 D
```

### 模式 3：串行任务的上下文传递

```markdown
## STAGE ## name="数据迁移" mode="serial"
# 🎯 阶段目标：完成数据迁移
# 📥 输入：旧系统数据库
# 📤 输出：新系统数据库

## TASK ##
导出旧系统数据

**📖 背景**：需要从旧系统导出数据以便迁移
**🔨 要做什么**：...
**✅ 完成标志**：生成 data_export.json

**📤 输出状态**：
- ✅ 导出文件：data_export.json (包含所有用户和订单数据)
- ➡️ 为下一任务提供：可以直接导入的标准格式数据

## TASK ##
转换数据格式

**📥 输入依赖**：
- ⬆️ 前一任务生成的 data_export.json

**📖 背景**：旧系统数据格式与新系统不兼容，需要转换
**🔨 要做什么**：...
**✅ 完成标志**：生成 data_transformed.json

**📤 输出状态**：
- ✅ 转换后文件：data_transformed.json
- ➡️ 为下一任务提供：符合新系统格式的数据

## TASK ##
导入新系统

**📥 输入依赖**：
- ⬆️ 前一任务生成的 data_transformed.json
- ⬆️ 数据验证报告确认无误

**📖 背景**：将转换后的数据导入新系统
**🔨 要做什么**：...
**✅ 完成标志**：所有数据导入成功，验证通过
```

---

## 💡 实用技巧

### 1. 文件范围标注（避免冲突）

**有冲突**（会串行）：
```markdown
## TASK ## 任务 A
文件: src/common/types.ts

## TASK ## 任务 B
文件: src/common/types.ts
→ 两个任务修改同一文件，自动串行
```

**无冲突**（可并行）：
```markdown
## TASK ## 任务 A
文件: src/modules/user/**/*.ts
排除: src/common/

## TASK ## 任务 B
文件: src/modules/order/**/*.ts
排除: src/common/
→ 文件范围不重叠，可以并行
```

### 2. 串行任务的上下文传递

**关键原则**：串行任务必须明确说明输入依赖和输出状态

```markdown
## TASK ##
任务 A

**📤 输出状态**：
- ✅ 生成文件 A
- ➡️ 为下一任务提供：配置信息

## TASK ##
任务 B（依赖任务 A）

**📥 输入依赖**：
- ⬆️ 前一任务生成的文件 A
- ⬆️ 前一任务提供的配置信息

**📖 背景**：基于任务 A 的结果继续处理...
```

---

## 🐛 常见问题

### Q: 任务并行但效率没提升？
**A**: 检查是否有文件冲突导致自动串行化。

```bash
# 预览时会显示冲突警告
python batchcc.py todo-task --dry-run
```

### Q: 串行任务如何传递上下文？
**A**: 使用 **📥 输入依赖** 和 **📤 输出状态** 明确说明。

```markdown
## TASK ##
任务 A

**📤 输出状态**：
- ✅ 生成 config.json
- ➡️ 为下一任务提供：配置信息

## TASK ##
任务 B

**📥 输入依赖**：
- ⬆️ 前一任务的 config.json
```

### Q: 中途失败怎么办？
**A**: 修复问题后，重新运行整个任务即可（AI 执行快）。

```bash
# 修复代码后重新运行
python batchcc.py todo-task
```

### Q: 任务描述太简单，AI 不理解怎么办？
**A**: 确保任务包含完整的 **📖 背景**、**🔨 要做什么**、**✅ 完成标志** 三部分。

---

## 📚 延伸阅读

- **详细格式规范**: `DAG_TASK_FORMAT.md` - 完整的 STAGE/TASK 语法（如果需要更多细节）
- **命令文档**: `todo-huge-task.md` - 拆分策略和智能判断
- **实际示例**:
  - `DAG_EXAMPLE_DETAILED.md` - 详细任务描述示例
  - `DAG_EXAMPLE_ECOMMERCE.md` - 电商系统开发
  - `DAG_EXAMPLE_MIGRATION.md` - 数据迁移项目

---

## 🎓 实战练习

尝试用 `/todo-huge-task` 生成一个任务编排：

```bash
/todo-huge-task "重构项目的用户、订单、支付三个模块，每个模块包含 service、controller、model 和测试"
```

看看 Claude Code 如何：
- 识别三个独立模块（可并行）
- 为每个模块生成完整的任务描述（包含背景、步骤、完成标志）
- 标注文件范围避免冲突
- 为串行任务设计上下文传递

---

**开始使用吧！** 🚀

有问题查阅 `DAG_TASK_FORMAT.md` 或查看示例文件。
