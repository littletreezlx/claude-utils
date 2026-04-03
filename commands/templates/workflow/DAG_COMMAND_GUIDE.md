# DAG 命令产出规范

> 所有 DAG 类型命令（`/test-plan`、`/refactor-project`、`/comprehensive-health-check`）统一遵循本规范。

---

## 产出文件

| 文件 | 位置 | 说明 |
|------|------|------|
| `task-{xxx}` | **项目根目录** | **batchcc.py 入口文件**，不带 `.md` 后缀 |
| `.{xxx}-tasks/*.md` | 项目根目录 | 任务细节文件 |

⚠️ **入口文件必须在项目根目录**，不是在 `.test-tasks/` 等子目录中！

---

## 入口文件格式

### ✅ 正确格式

```markdown
# [任务名称]

> **🏠 项目宏观目标**：
> [描述项目的宏观目标]

## STAGE ## name="stage-1" mode="serial"

## TASK ##
T1-1: 任务描述

**🎯 目标**：[要达成什么]

文件: test/unit/xxx_test.dart
验证: ../scripts/test.sh test/unit/xxx_test.dart

## STAGE ## name="stage-2" mode="parallel" max_workers="2"

## TASK ##
T2-1: 任务描述

文件: test/unit/yyy_test.dart
验证: ../scripts/test.sh test/unit/yyy_test.dart
```

### ❌ 常见错误

| 错误 | 正确写法 |
|------|----------|
| `## STAGE 1` 或 `## STAGE: name` | `## STAGE ## name="xxx" mode="serial"` |
| `mode="sequential"` | `mode="serial"` |
| `### TASK` 或 `## TASK:` | `## TASK ##` |
| 所有任务写在一个 `cc '...'` 里 | 每个 TASK 分散开，独立执行 |
| 缺少 `文件:` 字段 | 必须有 `文件:` 字段 |
| 缺少 `验证:` 字段 | 必须有 `验证:` 字段 |

### 格式要点

- `## STAGE ## name="xxx" mode="serial"` — `##` 之间有空格，mode 只认 `serial`/`parallel`
- `## TASK ##` — 必须是 `## TASK ##`
- 每个 TASK 后跟 `文件:` 和 `验证:` 字段
- 入口文件**不带** `.md` 后缀

---

## 执行流程

1. **AI 执行命令**（如 `/test-plan`）
2. **生成入口文件** `task-{xxx}` 到项目根目录
3. **生成细节文件** `.{xxx}-tasks/*.md`
4. **用户执行** `python batchcc.py task-{xxx}` 或 `python batchcc.py task-{xxx} --dry-run`

---

## 统一引用

所有 DAG 命令文件应包含：

```markdown
> **格式规范**：@templates/workflow/DAG_COMMAND_GUIDE.md - 统一产出规范
```

