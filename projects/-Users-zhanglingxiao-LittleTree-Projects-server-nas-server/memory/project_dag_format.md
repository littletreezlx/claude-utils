---
name: dag-task-format
description: batchcc.py DAG 任务文件的 STAGE/TASK 声明格式要求
type: project
---

- STAGE 声明必须用 `## STAGE ## name="xxx" mode="serial|parallel" max_workers="N"` 格式
- 不能用 `## Stage 0: xxx` + 单独的 `mode: serial` 行（batchcc.py 无法解析）
- TASK 声明用 `## TASK ##`（两边都要有 `##`）
- 格式规范文件：`~/.claude/commands/templates/workflow/DAG_TASK_FORMAT.md`

**Why:** 曾因格式不对导致 DAG 编排失败。
**How to apply:** 创建 DAG 任务文件时参考格式规范模板。
