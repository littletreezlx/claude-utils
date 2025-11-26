# DAG 任务编排系统

> `batchcc.py` 执行的任务编排文档

## 📚 文档索引

| 文档 | 用途 |
|------|------|
| **DAG_TASK_FORMAT.md** | 完整语法规范 + 快速开始 |
| **DAG_TASK_TEMPLATE.md** | 空白模板 |
| **DAG_EXAMPLE_ECOMMERCE.md** | 电商系统示例 |
| **DAG_EXAMPLE_MIGRATION.md** | 数据迁移示例 |
| **HEALTH_CHECK_TASK_TEMPLATE.md** | 健康检查模板 |
| **REFACTOR_TASK_TEMPLATE.md** | 重构任务模板 |

---

## 🚀 快速使用

```bash
# 1. 生成任务文件
/todo-huge-task "实现用户和订单管理模块"

# 2. 预览执行计划
python batchcc.py todo-task --dry-run

# 3. 执行（自动断点续传）
python batchcc.py todo-task
```

---

## 🎯 核心特性

- ✅ **STAGE 阶段控制** - 串行/并行模式
- ✅ **TASK 任务单元** - 细粒度执行
- ✅ **文件冲突检测** - 自动分析，无冲突并行
- ✅ **断点续传** - 中断后自动继续
- ✅ **自动化注入** - batchcc 自动注入执行指示

---

## 📖 阅读顺序

1. `DAG_TASK_FORMAT.md` → 语法规范和快速开始
2. `DAG_EXAMPLE_*.md` → 理解实际应用
3. 使用 `/todo-huge-task` 生成任务

---

## 🔧 相关工具

| 工具 | 用途 |
|------|------|
| `/todo-huge-task` | 生成 DAG 任务文件 |
| `batchcc.py` | 解析和执行任务 |
| `/todo-write` + `/todo-doit` | 简单串行任务（< 3 个） |

---

**相关文档**：
- 命令索引：`@../README.md`
- batchcc 维护指南：`~/.claude/my-scripts/batch/CLAUDE.md`
