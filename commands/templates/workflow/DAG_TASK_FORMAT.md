# DAG 任务编排格式规范

> `batchcc.py` 执行的任务文件格式，支持串行/并行混合执行

## 🚀 快速开始

```bash
# 1. 生成任务文件
/todo-huge-task "实现用户和订单管理模块"

# 2. 预览执行计划
python batchcc.py todo-task --dry-run

# 3. 执行（自动断点续传）
python batchcc.py todo-task

# 4. 重新开始（清空状态）
python batchcc.py todo-task --restart
```

---

## 📋 核心概念

### STAGE（阶段）
**粗粒度编排单元**，定义执行模式（串行/并行）。STAGE 按顺序执行。

### TASK（任务）
**细粒度执行单元**，具体的工作项。

### 执行流程
```
Stage 1 [串行] → Stage 2 [并行] → Stage 3 [串行]
    ↓               ↓                  ↓
  Task 1          Task 2~4           Task 5~6
  Task 2          (并行执行)         (串行执行)
  (顺序执行)
```

---

## 🤖 自主执行原则

### 核心特性
DAG 任务设计为**完全自动化、无人值守**的执行系统。

`batchcc.py` 会自动为每个任务注入自动化执行指示，确保 Claude：

#### ✅ 应该做的
1. **自主分析**：深入理解任务目标和当前项目状态
2. **自主决策**：基于优先级、影响面、技术可行性选择最优方案
3. **直接执行**：不询问用户，直接实施选定的方案
4. **记录理由**：在日志中清晰说明决策依据

#### ❌ 不应该做的
1. 询问用户"需要我帮您...吗？"
2. 列出多个选项让用户选择
3. 等待用户确认后才继续执行

### 任务编写要求

为了支持 Claude 的自主决策，任务描述应该：

1. **目标明确**：清晰表达要达成的目标
2. **边界清晰**：明确任务的范围和约束条件
3. **上下文充分**：提供足够的背景信息
4. **标准可验证**：明确的完成标志和验证方式

**示例对比**：

```markdown
# ❌ 不清晰（会导致 Claude 询问用户）
## TASK ##
优化错误处理

文件: src/**/*.ts
```

```markdown
# ✅ 清晰（Claude 可以自主决策）
## TASK ##
统一错误处理机制

**📖 背景**：
当前各模块有独立的错误处理器，导致错误格式不一致

**🔨 要做什么**：
1. 创建统一的 ErrorHandler 类
2. 实现标准的错误响应格式
3. 集成到各模块的 API 层

**✅ 完成标志**：
- 所有 API 错误返回统一格式
- 单元测试覆盖主要错误场景

文件: src/common/error-handler.ts
文件: src/modules/*/controller.ts
验证: npm test -- error-handler
```

### 决策失败处理

**只在真正无法决策时才标记任务失败**。

如果遇到需要**业务判断**的情况（如技术选型、架构方案），应该：
1. 标记任务状态为 `failed`
2. 在错误信息中清晰说明无法决策的原因
3. 列出可选方案和各自的优劣分析

---

## 🧠 任务描述规范

> **核心原则**：清晰简洁，AI 容易理解
>
> 任务描述的质量决定执行效率。好的描述 = 目标明确 + 路径清晰 + 可验证。

### 设计原则

| 原则 | 说明 |
|------|------|
| **目标明确** | 一句话说清要达成什么 |
| **路径清晰** | 列出核心文件和操作类型 |
| **可验证** | 完成标准客观可检验 |

### 任务格式

```markdown
## TASK ##
[任务标题]

**🎯 目标**：[要达成什么]

**📁 核心文件**：
- `src/xxx/target.ts` - [修改] 添加 XXX
- `src/xxx/reference.ts` - [参考]

**✅ 完成标志**：
- [ ] [可验证的标准]

文件: src/xxx/**/*.ts
验证: npm test -- xxx --silent
```

### 字段说明

| 字段 | 必填 | 说明 |
|------|------|------|
| 🎯 目标 | ✅ | 一句话说明要达成什么 |
| 📁 核心文件 | ✅ | 精确路径 + 操作类型 |
| ✅ 完成标志 | ✅ | 客观可验证的标准 |
| 🏠 项目背景 | 可选 | 复杂任务时提供上下文 |
| 🔨 执行步骤 | 可选 | 需要时列出关键步骤 |

### 对比示例

```markdown
# ❌ 模糊
## TASK ##
优化用户模块
文件: src/modules/user/

# ✅ 清晰
## TASK ##
为用户模块添加统一错误处理

**🎯 目标**：所有 API 错误返回统一格式 { code, message, data }

**📁 核心文件**：
- `src/modules/user/user.service.ts` - [修改] 使用标准错误类
- `src/common/errors.ts` - [参考] 查看错误类定义

**✅ 完成标志**：
- [ ] `npm test -- user` 全部通过

文件: src/modules/user/**/*.ts
验证: npm test -- user --silent
```

**项目背景**：复杂任务可在 STAGE 头部统一说明，任务内省略。

---

## 🎯 STAGE 语法

### 基础格式
```markdown
## STAGE ## name="阶段名称" mode="serial|parallel" max_workers="4"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 | 默认值 |
|------|------|------|------|--------|
| `name` | string | ✅ | 阶段名称 | - |
| `mode` | enum | ✅ | `serial` 或 `parallel` | - |
| `max_workers` | int | ❌ | 最大并发数（仅 parallel） | 4 |

### 执行模式

#### `mode="serial"` - 串行模式
- **用途**：有严格顺序依赖的任务（数据库 schema、配置初始化）
- **特点**：阶段内任务按顺序执行，前一个失败则停止

#### `mode="parallel"` - 并行模式
- **用途**：独立的功能模块、无依赖的任务
- **特点**：阶段内任务并发执行（受 `max_workers` 限制）
- **冲突检测**：自动分析文件范围，有冲突的任务会自动串行

---

## 🔧 TASK 语法

### 基础格式

**⚠️ 重要：TASK 标记格式**

```markdown
## TASK ##
```

- 标准格式：`## TASK ##`（推荐）
- 两边都要有 `##`
- 解析器也兼容 `## TASK:` 但不推荐使用

### 完整示例
```markdown
## TASK ##
任务描述（多行支持）

**📖 背景**：为什么要做
**🔨 要做什么**：具体步骤
**✅ 完成标志**：如何验证

文件: src/path/to/files/**/*.ts
排除: src/common/types.ts
验证: npm test -- module-name
```

### 任务内容字段

| 字段 | 说明 | 必填 |
|------|------|------|
| 任务描述 | 第一行非空内容 | ✅ |
| `文件:` | 文件范围（glob 模式），用于冲突检测 | 推荐 |
| `排除:` | 排除文件，避免误判冲突 | ❌ |
| `验证:` | 验证命令（任务完成后执行） | ❌ |

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
排除: **/*.test.ts
```

### 冲突检测逻辑

**无冲突（可并行）**：
```markdown
## TASK ##
文件: src/modules/user/**/*.ts
排除: src/common/

## TASK ##
文件: src/modules/order/**/*.ts
排除: src/common/
# → 文件范围不重叠，可以并行
```

**有冲突（自动串行）**：
```markdown
## TASK ##
文件: src/modules/user/**/*.ts
文件: src/common/types.ts

## TASK ##
文件: src/modules/order/**/*.ts
文件: src/common/types.ts
# → types.ts 冲突，自动串行执行
```

---

## 📦 串行任务的上下文传递

串行任务需要明确说明输入依赖和输出状态（这是**提示 Claude** 的约定，非系统功能）：

```markdown
## STAGE ## name="数据迁移" mode="serial"

## TASK ##
导出旧系统数据

**📤 输出状态**：
- ✅ 生成 data_export.json
- ➡️ 为下一任务提供：标准格式数据

## TASK ##
转换数据格式

**📥 输入依赖**：
- ⬆️ 前一任务生成的 data_export.json

**📤 输出状态**：
- ✅ 生成 data_transformed.json
```

---

## 🎨 常见模式

### 模式 1：基础设施 → 并行开发 → 测试

```markdown
## STAGE ## name="初始化" mode="serial"
## TASK ##
创建数据库表

## STAGE ## name="开发" mode="parallel" max_workers="4"
## TASK ##
用户模块
文件: src/modules/user/**/*.ts

## TASK ##
订单模块
文件: src/modules/order/**/*.ts

## STAGE ## name="测试" mode="serial"
## TASK ##
集成测试
```

### 模式 2：独立任务批量执行

```markdown
## STAGE ## name="重构模块" mode="parallel" max_workers="8"
## TASK ## 重构模块 A
## TASK ## 重构模块 B
## TASK ## 重构模块 C
```

---

## ⚠️ 注意事项

### 文件范围标注
- ✅ 尽可能详细标注，帮助冲突检测
- ⚠️ 不标注时，batchcc 无法自动检测冲突
- 💡 使用 `排除:` 避免共享文件导致的误判

### 并行度控制
- ⚠️ `max_workers` 不建议超过 CPU 核心数
- 💡 CPU 密集型任务用小值，IO 密集型可用大值

### 失败策略
- 任何任务失败都会停止整个流程（简单直接）
- 修复后重新运行即可（自动跳过已完成任务）

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| `DAG_TASK_TEMPLATE.md` | 空白模板（可直接复制使用） |
| `DAG_EXAMPLE_ECOMMERCE.md` | 电商系统示例 |
| `DAG_EXAMPLE_MIGRATION.md` | 数据迁移示例 |
| `HEALTH_CHECK_TASK_TEMPLATE.md` | 健康检查任务模板 |
| `REFACTOR_TASK_TEMPLATE.md` | 重构任务模板 |
| `~/.claude/my-scripts/batch/CLAUDE.md` | batchcc.py 执行引擎维护指南 |
