# 2026-04-15-04 batchcc 排除命令级 state（修订 03 判断）

## 遇到的问题

修订 03 之后实战仍出问题：flametree_pick 跑 `/doc-quality-review` Stage 1 时连续产出 7 个 commit，每个都被标"自动提交成功（X 个业务文件）"，但 `git show --stat` 显示真正改的全是：

```
任务 1: 诊断 Batch 1 (root/)
 TODO.md                        |  47 ---
 docs/quality-review-state.json | 641 +++++++++++++++++++----------------------

任务 2: 诊断 Batch 2 (api/ + architecture/ + deployment/)
 docs/quality-review-state.json | 29 +++++++++++++++++++++++++++++
```

`docs/quality-review-state.json` 是 `/doc-quality-review` 命令记录"哪些文档已审查"的**进度文件**，每个 Stage 1 TASK 都会标记本批次的文档为已审查——本质和 batchcc 自己的 `state.json` 一样，只是位置在 `docs/` 而不是 `.task-xxx/`。

## 修订 03 的错误

03 决策记录里我写过：

> 命令级 state（如 `docs/quality-review-state.json`）不在排除范围，仍会跟随业务变更进 commit（这是预期——它是命令的成果物）

**判断错了**。"成果物"和"进度文件"的区分应该按"每次 TASK 是否都改"来定，而不是按"位置"或"是否跨运行保留"：

- 跨运行保留 ≠ 业务成果。命令级 state 跨运行保留是为了下次 `/doc-quality-review` 知道哪些文档已审过 → 跨运行**断点续传**，跟 batchcc 的 state.json 性质一致
- 真正的业务成果是命令对 docs/ 业务文件的修改（Stage 3 处方落地、归档、迁移），而不是 state.json 里的 hash 列表

## 决策

扩展 `_TASK_ARTIFACT_EXCLUDES`，按**命名约定**排除命令级 state：

```python
":(exclude,glob)**/*-state.json",   # 跨目录：xxx-state.json
":(exclude,glob)**/*.state.json",   # 跨目录：xxx.state.json
```

匹配示例：
- ✅ 排除 `docs/quality-review-state.json`（命令进度）
- ✅ 排除 `docs/test-plan-state.json`（未来 /test-plan state）
- ✅ 排除 `task-foo.state.json`（旧格式 batchcc state）
- ❌ 不排除 `app-config.json`（业务配置）
- ❌ 不排除裸 `state.json`（保守：可能是业务文件如 Redux 持久化）

未来 DAG 命令的命令级 state 必须遵守命名约定 `<topic>-state.json` 或 `<topic>.state.json` 才能被自动排除。

## 为什么不选其他方案

- **❌ 排除整个 `docs/quality-review-state.json` 硬编码**：不通用，每个命令都要在 batchcc 加一行
- **❌ 排除裸 `state.json`**：可能误伤业务（Redux 持久化、游戏存档等）
- **❌ 让命令级 state 改放 `.task-xxx/` 内**：`.task-xxx/` 由 `_cleanup()` 删除，命令级 state 需跨运行保留
- **❌ 让命令级 state 改放 `.claude/`**：违反 commands/CLAUDE.md §4「State 避开 `.claude/`」（权限围栏）

## 验证凭证

实测 STDOUT（`/tmp/e2e3` 模拟 baseline 后只动 state 的场景）：

```
=== 场景 A：baseline 后只动 .task-foo/state.json + docs/quality-review-state.json + task-foo.state.json ===
📝 仅任务过程文件变化（无业务改动），跳过自动提交
git log: 无新 commit ✓

=== 场景 B：业务 docs/foo.md + state 同时改 ===
✅ 自动提交成功（1 个业务文件）: 修改业务文档
git show --stat HEAD: docs/foo.md | 1 +  （state 不在 commit 内）
git status: M docs/quality-review-state.json  （state 仍 modified 未提交）✓
```

## 副观察（不在本次修复范围）

flametree_pick Stage 1 Batch 1 commit 还改了 `TODO.md`（删除 47 行）。Stage 1 是诊断阶段，**不应该**修改业务文件，只该产出 `action-plan.batch_X.md` 片段。这是 `commands/doc-quality-review.md` Stage 1 任务约束不够——需要在 Stage 1 TASK 模板里显式声明"诊断阶段禁止修改 docs/ 任何业务文档，TODO.md 由 Stage 4 收尾负责"。下一个决策记录处理。

## 历史 commit 处理建议

flametree_pick 已经形成 7 个"任务 N: 诊断 Batch X" commit，里面只有 state.json + 越界的 TODO.md 改动。用户可选：

- **保留**：作为本次实战教训的 git history，不影响后续工作
- **squash 清理**：`git rebase -i HEAD~9` 把这 7 个 commit + Stage 3 业务 commit 合并成一个 `docs: doc-quality-review 全流程产出`
  - ⚠️ 破坏性操作，仅在没 push 到远程时安全
  - ⚠️ 推荐让 Founder 自己决定，AI 不擅自 rebase
