# 默认跳过 Claude Design re-onboard 提示

**Date**: 2026-04-25
**Scope**: 跨项目 skill 修改 — `/ui-bootstrap` + `/ui-adopt`
**Status**: Adopted

---

## 问题

`/ui-bootstrap` 和 `/ui-adopt` 的原设计假设 Founder 走 "**预先 onboard**" 工作流：在改 UI 前先让 Claude Design 项目读一次最新 codebase，并维护 `EXTERNAL_REFS.md` 里的 `onboarded_commit` 字段追踪此基线。skill 据此自动产出：

- `/ui-bootstrap` Phase 6 完成提示和 EXTERNAL_REFS.md 模板里都标红 "建议下次 `/ui-adopt` 前先在 Claude Design 里做一次 re-onboard"
- `/ui-adopt` Phase 5 在每次 Invariant 变更时强制弹出 "⚠️ Claude Design Re-onboard 提示"，要求 Founder 去 Claude Design web 操作并回报，否则 commit 后 AI 还会继续追问

## 真实工作流

Founder 当场澄清：

> 我这里更新之后都会让 Claude Design 去读最新代码的

即每次使用 Claude Design 时**即时**让它拉最新 codebase（在 Claude Design 对话框里直接说"读最新代码"），不预先 onboard。这意味着：

- `onboarded_commit` 字段永远填不上有意义的值（因为没有"上一次 onboard 时刻"这个状态）
- 自动产出的 "建议 re-onboard" 提示是**纯噪音**——Founder 看到只会困惑或忽略
- TODO.md 里被自动塞入的 re-onboard 任务永远是死任务（AI 无法自主执行 + Founder 也不会去做）

本次会话中实际踩坑：`/todo-doit` 把 re-onboard 任务列为"必做/优先级高"挡在 TODO 队列里，AI 在 commit 后还以"下一步"形式向 Founder 推送，Founder 反问"为什么需要 Re-onboard 再 commit"才暴露问题。

## 决策

**默认行为变为"跳过 re-onboard 流程"，保留作为 opt-in 能力**。

### `/ui-bootstrap` 改动

1. EXTERNAL_REFS.md 模板里 `Onboarded from commit` 字段从 `unknown ⚠️ 建议下次 adopt 前 re-onboard` 改为 `n/a` + 注释说明默认工作流不追踪此字段
2. Phase 6 完成提示删除 "建议下次 /ui-adopt 前 re-onboard" 一行
3. 约束段从 "onboarded_commit 固定填 unknown + 标红" 改为 "固定填 n/a，不询问用户"

### `/ui-adopt` 改动

1. description 删除 "触发 re-onboard 提示"
2. Overview 删除 "并提醒用户 re-onboard Claude Design"
3. Phase 5 整段重写为 "**默认跳过**" 路径：
   - 默认不产出任何提示，不更新 onboarded_commit
   - **opt-in 触发条件**（任一满足）：
     - `EXTERNAL_REFS.md` 中 `Onboarded from commit` 是真实 commit sha（不是 `n/a`/`unknown`/空）
     - 用户调用时显式带 `--with-reonboard-prompt` 参数
4. Phase 6 后续步骤把 "Re-onboard Claude Design" 从 #1 必做改为 #2 可选
5. Gotcha 段补充 "默认工作流不存在此问题"

## 为什么不完全删除 re-onboard 概念

考虑过 "选项 A：完全抹掉 re-onboard 概念"，但保留更稳妥：

- Founder 工作流可能演化（如多人协作场景下"预先 onboard + 共享基线" 反而合理）
- 整段删除会让 EXTERNAL_REFS.md 模板变得难以解释 `onboarded_commit` 字段的用意
- 保留 opt-in 能力的成本极低（默认跳过 + 触发条件清晰），可逆性强

## 为什么 EXTERNAL_REFS.md 字段保留

考虑过 "整个删掉 `Onboarded from commit` 字段"，但保留并默认 `n/a` 更清晰：

- 字段存在 + 默认 `n/a` 自带语义说明（"此项目工作流不维护此字段"）
- 未来如某项目要切换为追踪模式，把字段值改成真实 sha 即可，不需要回头改 skill 模板
- 维护负担为零（skill 写一次"填 n/a"，跨项目永久生效）

## 同步动作

- 删除 per-project memory `feedback_claude_design_reonboard.md`（skill 改了之后变冗余）
- flametree_tv 项目的 EXTERNAL_REFS.md 上一轮 commit `238f7b6` 已改为 `n/a` + 同样的注释，与新 skill 默认产出对齐

## 验证

未来跑 `/ui-bootstrap` / `/ui-adopt` 时，应满足：

- `/ui-bootstrap` Phase 6 完成提示**不再**含 "建议 re-onboard"
- 新建 EXTERNAL_REFS.md 的 `Onboarded from commit` 字段值为 `n/a` + 注释说明
- `/ui-adopt` Invariant 变更时**默认不**弹 re-onboard 提示
- 仅当 EXTERNAL_REFS.md 显式填了真实 commit sha 时，`/ui-adopt` Phase 5 才启用提示流程
