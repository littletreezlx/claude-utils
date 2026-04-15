# 2026-04-15-02 DAG 入口语法强制 + 生成后自检

## 遇到的问题

`/doc-quality-review` 在 ai-image-studio 项目实战时第二次失败：

```
batchcc.py - 简单模式
✅ 找到 1 个命令:
  1. cc '# doc-quality-review DAG — ai-image-studio ## 扫描结果 ...'
```

batchcc 把 600 行的扫描+分批说明文档当作 1 个 cc 任务喂给 Claude Code，会污染整个 `docs/`。flametree_pick 之前生成的 `task-doc-quality-review` 也是同样的退化。

## 根因

`commands/doc-quality-review.md` 第三步只用表格描述了 STAGE 列表（`| Stage 1 | diagnose | parallel |`），没给出完整的 `## STAGE ## name="..." mode="..."` 模板示例，AI 就按"人类可读说明"的方式生成入口文件——用 `## Stage 1: diagnose (parallel max_workers=4)` 这种描述性标题，缺 batchcc 解析所需的 `## STAGE ##` / `## TASK ##` 分隔符。

`is_dag_format()` 因为找不到 `## STAGE` + `## TASK` 标记，退回简单模式，整份文档作为 1 个 TASK。

这正是 `commands/CLAUDE.md` 强制清单的元原则警告："Skill/command 在 AI-Only 项目里是可执行约束，留白处必被保守派默认占据"——只说"生成 DAG"，AI 就会生成"看起来像 DAG 的说明文档"。

## 决策

### 1. `commands/doc-quality-review.md` 第三步加三段硬约束

- **重跑前清理**：`rm -rf .task-doc-quality-review/` 避免新旧文件混合
- **入口文件硬约束**：内嵌完整 `## STAGE ## name="diagnose" mode="parallel" max_workers="4"` + `## TASK ##` 模板示例（含 4 个 STAGE、各自至少 1 个 TASK）
- **禁止形式清单**：显式列出 `## Stage 1: ...`、`### Batch 1: ...` 替代 `## TASK ##` 等错误写法
- **生成后自检**：强制 `grep -c '^## STAGE ##' dag.md` ≥ 4 + `grep -q '^## STAGE ## name="diagnose" mode="parallel"'` 等校验，自检失败必须修正

### 2. `commands/CLAUDE.md` 强制清单加第 5 条

把"强制 DAG 入口语法 + 生成后自检"提升为**所有 DAG 命令**的通用约束（不只 `doc-quality-review`）。今后新增 DAG 命令必须满足：

- 内嵌完整可执行入口模板（不只是表格描述）
- 显式列出禁止形式
- 强制 grep 自检 STAGE/TASK 标记数
- 重跑前清理旧产物

## 为什么不选其他方案

- **❌ 改 batchcc，让简单模式拒绝单文件超过 N 行**：会破坏简单 TASK 格式的合法用法，且根因不在 batchcc
- **❌ 让 `is_dag_format()` 更宽松，识别 `## Stage 1`**：会让"扫描说明文档"被假性识别为 DAG，仍然不能正确执行
- **❌ 把模板外置到 `templates/workflow/DOC_QUALITY_REVIEW_TEMPLATE.md`**：增加文件查找成本，且 AI 会跳过引用直接自由发挥；内嵌在命令里"贴脸看"才能强制
- **❌ 只改 doc-quality-review**：其他 DAG 命令（`refactor-project` / `test-plan` / `todo-huge-task` / `comprehensive-health-check`）有相同退化风险，必须升到强制清单层面

## 验证凭证

- `commands/doc-quality-review.md` 第三步 diff：增加"重跑前清理"段、"入口文件硬约束"段（含完整 STAGE/TASK 模板）、"禁止形式"清单、"生成后自检"段
- `commands/CLAUDE.md` 强制清单第 5 条 diff：新增"强制 DAG 入口语法 + 生成后自检"
- 实战触发上下文：ai-image-studio 项目 `batchcc task-doc-quality-review` 输出 `batchcc.py - 简单模式 / 找到 1 个命令`（用户粘贴的 stdout，2026-04-15 10:26）

## 后续

- ai-image-studio 的 `.task-doc-quality-review/` 目录需删除重跑（`rm -rf` 后再 `/doc-quality-review`）
- flametree_pick 的 `.task-doc-quality-review/dag.md`（本会话手工写的）合规，不受影响
