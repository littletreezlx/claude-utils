# DAG 任务编排系统 - 文档索引

> `/todo-huge-task` 命令的完整文档体系

## 📚 文档结构

### 核心文档

#### 1. 命令文件
- **位置**: `/Users/zhanglingxiao/.claude/commands/todo-huge-task.md`
- **用途**: `/todo-huge-task` 命令的完整指南
- **内容**:
  - 任务拆分策略
  - 智能判断逻辑
  - 输出格式要求
  - 使用场景判断

#### 2. 格式规范（必读）
- **位置**: `DAG_TASK_FORMAT.md`
- **用途**: 完整的 STAGE 和 TASK 语法规范
- **内容**:
  - STAGE 参数详解（name, mode, max_workers, depends_on）
  - TASK 参数详解（id, depends_on, on_failure, retry）
  - 文件范围标注规则（冲突检测）
  - 失败策略详解（stop/continue/retry）
  - 完整示例和最佳实践

### 快速开始

#### 3. 快速上手指南
- **位置**: `DAG_QUICK_START.md`
- **用途**: 5 分钟快速上手
- **内容**:
  - 三步上手流程
  - 核心概念（2 分钟理解）
  - 三种常见模式
  - 实用技巧
  - 常见问题 FAQ

### 模板和示例

#### 4. 空白模板
- **位置**: `DAG_TASK_TEMPLATE.md`
- **用途**: 快速创建新任务文件的模板

#### 5. 电商系统示例
- **位置**: `DAG_EXAMPLE_ECOMMERCE.md`
- **用途**: 完整的电商系统开发示例
- **包含**:
  - 5 个阶段（数据库 → 业务模块 → 前端 → 集成 → E2E）
  - 15 个任务
  - 串行/并行混合编排
  - 文件范围标注
  - 依赖关系管理

#### 6. 数据迁移示例
- **位置**: `DAG_EXAMPLE_MIGRATION.md`
- **用途**: 数据迁移项目示例
- **包含**:
  - 4 个阶段（备份 → 脚本开发 → 测试迁移 → 生产迁移）
  - 10 个任务
  - 严格的串行控制
  - 依赖链管理

### 测试和验证

#### 7. 简单测试示例
- **位置**: `DAG_TEST_SIMPLE.md`
- **用途**: 最简单的 DAG 任务示例（6 个文件创建任务）

#### 8. 格式验证脚本
- **位置**: `/Users/zhanglingxiao/.claude/commands/verify-dag-format.sh`
- **用途**: 验证 DAG 文件格式是否正确
- **使用**: `./verify-dag-format.sh <task-file>`

---

## 🚀 使用流程

### 方式 1：使用命令生成（推荐）

```bash
# 1. 使用 /todo-huge-task 命令
/todo-huge-task "实现用户和订单管理模块"

# 2. Claude Code 自动生成 todo-task 文件

# 3. 预览执行计划
python batchcc.py todo-task --dry-run

# 4. 执行任务
python batchcc.py todo-task
```

### 方式 2：手动编写

```bash
# 1. 复制模板
cp templates/workflow/DAG_TASK_TEMPLATE.md todo-task

# 2. 参考格式规范编辑
# 查阅: templates/workflow/DAG_TASK_FORMAT.md

# 3. 参考示例
# 电商: templates/workflow/DAG_EXAMPLE_ECOMMERCE.md
# 迁移: templates/workflow/DAG_EXAMPLE_MIGRATION.md

# 4. 验证格式
./verify-dag-format.sh todo-task

# 5. 执行任务
python batchcc.py todo-task
```

---

## 📖 阅读顺序建议

### 新手用户
1. **快速开始** → `DAG_QUICK_START.md`（5 分钟）
2. **看示例** → `DAG_EXAMPLE_ECOMMERCE.md`（理解结构）
3. **用命令** → `/todo-huge-task "你的任务"`
4. **执行** → `python batchcc.py todo-task`

### 进阶用户
1. **格式规范** → `DAG_TASK_FORMAT.md`（详细语法）
2. **命令指南** → `todo-huge-task.md`（拆分策略）
3. **手动编写** → 使用模板创建复杂任务
4. **优化调整** → 根据实际情况调整并行度和依赖

---

## 🎯 核心特性

### 智能编排
- ✅ **STAGE 控制** - 粗粒度串行/并行控制
- ✅ **TASK 灵活** - 细粒度任务定义
- ✅ **依赖管理** - 阶段依赖 + 任务依赖

### 冲突检测
- ✅ **文件范围分析** - 自动检测文件冲突
- ✅ **智能调度** - 无冲突并行，有冲突串行
- ✅ **排除机制** - 避免共享文件误判

### 失败控制
- ✅ **stop** - 立即停止（关键任务）
- ✅ **continue** - 继续执行（独立任务）
- ✅ **retry** - 自动重试（网络任务）

### 可视化
- ✅ **执行计划预览** - `--dry-run` 参数
- ✅ **进度监控** - 实时显示执行状态
- ✅ **结构展示** - 清晰的阶段-任务层级

---

## 🔧 工具链

### 核心工具
- **Claude Code**: `/todo-huge-task` 命令（生成任务文件）
- **batchcc.py**: 任务执行引擎（解析和执行）
- **verify-dag-format.sh**: 格式验证工具

### 配合使用
- **/todo-write**: 简单串行任务（< 3 个任务）
- **/todo-doit**: 自动执行 TODO.md 任务
- **/todo-huge-task**: 复杂并行任务（≥ 3 个任务）

---

## 📝 文档贡献

### 维护日志
- **2025-11-10**: 创建 DAG 任务编排系统完整文档体系
  - 格式规范（DAG_TASK_FORMAT.md）
  - 快速开始（DAG_QUICK_START.md）
  - 命令文档（todo-huge-task.md）
  - 示例文件（电商、迁移）
  - 验证工具（verify-dag-format.sh）

### 文档版本
- **格式规范**: v1.0
- **命令文档**: v1.0
- **示例文件**: v1.0

---

## 🤝 相关链接

- **项目主文档**: `/Users/zhanglingxiao/.claude/commands/CLAUDE.md`
- **全局配置**: `/Users/zhanglingxiao/.claude/CLAUDE.md`
- **批量执行器**: `/Users/zhanglingxiao/LittleTree_Projects/python_test/projects/claude-code/batchcc.py`

---

**最后更新**: 2025-11-10
**文档维护**: Claude Code
