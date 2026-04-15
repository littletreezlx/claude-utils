# 2026-04-15-03 batchcc 跳过仅任务过程文件的 commit

## 遇到的问题

`/doc-quality-review` 在 ai-image-studio 跑的过程中，git log 出现一连串"任务 N: 诊断 Batch X"的 commit，**实质内容为空**——既没有改任何业务文档/代码，也没有改命令级 state，只是 batchcc 自己写了 `.task-doc-quality-review/state.json` 和阶段产物（`action-plan.batch_X.md`）。

用户反馈："这个不应该单独 commit，没有意义……每个 stage 或者 task 实际做了改动才 commit。"

## 根因

`batchcc.py:_auto_commit_if_needed()` 用 `git add .` 扫所有变更，包括：

- `.task-xxx/state.json` —— batchcc 进度状态（每 TASK 完成都写）
- `.task-xxx/action-plan.*.md` —— Stage 1 诊断中间产物
- `.task-xxx/review-action-plan.md` —— Stage 2 合并中间产物

这些是 batchcc 运行时的**编排过程文件**，本质和编译产物 / 缓存类似——最终由 `DAGExecutor._cleanup()` 删整个 `.task-xxx/` 目录。把它们 commit 进 git history 既没回溯价值，又污染审计：

- "任务 5" commit 看似有进度推进，diff 只有 state.json 多了一行 `"completed_at": ...`
- 业务回溯时（如 `git blame docs/foo.md`）被无关的"任务 N" commit 干扰

## 决策

修改 `_auto_commit_if_needed()`：

1. **`git add` 显式排除任务过程产物**：`:!.task-*` / `:!.task-*/**` / `:!task-*` / `:!task-*.state.json`
2. **暂存区为空时跳过 commit**：用 `git diff --cached --name-only` 检查实际 staged 文件，仅任务文件变化 → 打印"仅任务过程文件变化，跳过自动提交"，不产生空内容 commit
3. **失败模式不抛 CalledProcessError**：旧代码用 `check=True`，失败时异常 swallow stderr；新代码用 returncode 检查 + stderr 摘要打印

排除规则提取为类常量 `_TASK_ARTIFACT_EXCLUDES`，方便后续维护。

## 为什么不选其他方案

- **❌ 改 batchcc 不写 state.json**：state.json 是断点续传的核心，不能不写
- **❌ 在 .gitignore 加 `.task-*/`**：会让命令级 state（如 `docs/quality-review-state.json`）也被忽略；且要求每个项目都改 .gitignore，迁移成本高
- **❌ commit 任务文件，但用合并 commit / squash**：增加 batchcc 复杂度，且 git log 仍有中间状态污染
- **❌ 完全关闭 auto_commit**：会丢失"业务改完即提交"的便利，回退到手动 commit

## 验证凭证

`my-scripts/batch/batchcc.py` `_auto_commit_if_needed` 重写后实测：

```
=== 场景 1：只动任务文件 ===
.task-foo/dag.md + .task-foo/state.json 改动
→ STDOUT: 📝 仅任务过程文件变化（无业务改动），跳过自动提交
→ git log 无新 commit ✓

=== 场景 2：业务文件 + 任务文件同时改 ===
biz.md（业务）+ .task-foo/state.json（任务）
→ STDOUT: ✅ 自动提交成功（1 个业务文件）: 修改业务文档
→ git show --stat: biz.md | 1 + （仅业务文件进 commit）
→ git status --porcelain: ?? .task-foo/  （任务目录仍未追踪）✓
```

## 影响范围

- `_auto_commit_if_needed()` 是 batchcc 串行/并行两条路径**唯一**的 commit 入口（`execute_command_serial` 串行调用、`execute_dag_batch_parallel` 并行批次内主线程串行调用），改一处即可
- 旧任务（已经 commit 进 git 的 `.task-xxx/` 内容）不受影响——已 tracked 的文件本次 commit 不会被排除掉，但下次 batchcc 跑时新的 state 写入不会再形成独立 commit
- 命令级 state（如 `docs/quality-review-state.json`）**不在排除范围**，仍会跟随业务变更进 commit（这是预期——它是命令的成果物）
