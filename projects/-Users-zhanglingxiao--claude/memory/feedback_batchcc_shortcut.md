---
name: batchcc 快捷命令
description: DAG 任务结尾用 batchcc 快捷命令，不要写 python batchcc.py，不要追问
type: feedback
---

DAG 任务生成完毕后，结尾只写简洁的执行命令：`batchcc task-xxx`，不要写 `python batchcc.py task-xxx`。

**Why:** 用户已将 batchcc.py 封装为 `batchcc` 快捷命令。冗长的 python 调用和追问（"你是想让我检查格式合规性，还是 batchcc.py 不存在？"）是噪音。

**How to apply:** 所有 DAG 型命令（refactor-project、test-plan、comprehensive-health-check、todo-huge-task 等）生成任务后，结尾只给执行命令，不追问、不解释。格式：
```
batchcc task-xxx --dry-run  # 预览
batchcc task-xxx            # 执行
```
