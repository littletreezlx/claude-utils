# 2026-04-19-01 generate-stories v3.0：真 DAG + 双模式（Generate/Review）

## 背景

v2.0/v2.1（昨日决策 07/08）落地后，Founder 实操 flametree_pick 跑完 Phase 1/2 对 v2.1 提出两个**根本性纠正**：

### 纠正 1：Gate 2 的"审核"理解错了

Founder 原话：
> "哪怕它覆盖率是 100%，但它很多地方写的不恰当、不合理呀。我希望仍然是每个都具体校验过。"

我之前的理解：Gate 2 一次展示 N 条摘要让 Founder 勾通过。  
Founder 实际要的：**每条 Story + QA 生成后都逐条过目全文**，因为覆盖率达标不等于 AI 写的内容合理。

这是"AI 输出内容质量审核"，不是"候选清单审核"。v2.1 砍了 Gate 1 又把 Gate 2 写成"展示摘要"，两边都不对。

### 纠正 2：我根本没实现 DAG

Founder 原话：
> "你是不是没有理解 DAG 的含义呀？它目前还仍然是在一个会话中执行完成。DAG 是单独一个 DAG 文件，它的目的是让把内容分散在不同的会话中。"

v2.0/v2.1 的"DAG" = 同一个主会话里顺序跑 Phase 1→2→3→4→5。这**完全违反** `~/.claude/commands/CLAUDE.md` 的 **DAG 强制清单 §5**：

> 只说"生成 DAG 任务文件"会让 AI 退化为生成"看起来像 DAG 的扫描+分批说明文档"——用 `## Stage 1: diagnose (parallel)` 这种**人类可读标题**而非 `## STAGE ## name="..." mode="..."` 真语法。后果：batchcc 的 `is_dag_format()` 退化为"简单模式"，整份说明文档被当作 1 个 cc 任务喂给 Claude，污染整个项目。

我正是这个反例——把"DAG"写成了"阶段文档"。根本没拿到 DAG 的核心收益（独立上下文解决偷懒）。

## 诊断

两个错误的共同根因：**没有理解 DAG 是"两步走 + 独立会话"的基础设施模式**，而不是 skill 内部的流水线。

参考 `refactor-project` / `test-plan` / `doc-quality-review` 的标准范式：

```bash
/command-name                    # 第一步：主会话生成 .task-xxx/dag.md
batchcc task-xxx                 # 第二步：独立子会话批量执行
```

每个 TASK 在独立子会话里执行 = 真·独立 context window = 不偷懒、不稀释、不互相带偏。

但用户要"逐条审核"——审核是交互，DAG 是无人值守，这两个是**冲突的**。必须在 DAG 之外安排审核时机。

## 决策

**v2.1 → v3.0：真 DAG + 双模式（Generate / Review）。**

### 架构

```
/generate-stories  ──→  [Mode A: Generate]
                         Phase 1  Context Digest → .task-generate-stories/digest.md
                         Phase 2  Behavior Audit → .task-generate-stories/behavior-audit.md
                         Gate 1   智能检查（v2.1 保留）
                         产出     .task-generate-stories/dag.md（真 DAG 入口）
                         告知用户 两步走：batchcc task-generate-stories

[用户手动]
batchcc task-generate-stories  ──→  独立子会话 × N 并行生成 Story+QA
                                     收尾 TASK 写 REVIEW_QUEUE.md

/generate-stories  ──→  [Mode B: Review]  ← 状态感知自动切换
                         读 REVIEW_QUEUE.md
                         逐条展示 Story+QA 全文（不是摘要）
                         Founder 回复 ✅/✏️/❌
                         ✏️ 或 ❌ → 主会话 dispatch subagent 即时重生
                         全部 ✅ → 清理 .task-generate-stories/ + commit
```

### 模式切换（Q1 A）

主会话检测 `.task-generate-stories/` 状态决定入口模式：

| 状态 | 模式 |
|------|------|
| 目录不存在 | Generate Mode |
| 目录存在 + `dag.md` 存在 + `REVIEW_QUEUE.md` 不存在 | 提示用户跑 batchcc（或 `--restart`）|
| 目录存在 + `REVIEW_QUEUE.md` 存在 | Review Mode |

### 审核粒度（Q2 B）

Founder 选的是**直接审 Story 全文 + QA 全文**，不是摘要。

每轮 Review 展示一条的完整内容，Founder 看完再翻下一条。这对 10 条 Story 确实累，但 Founder 明确说覆盖率不等于质量，**这个累是必要成本**。

### 打回重生（Q3 A）

✏️（具体修改要求）或 ❌（整体重做）时，**主会话内**用 `Task` tool dispatch 一个 subagent 即时重生该条：

- 输入：原 TASK 描述 + digest + behavior-audit 该条行为段 + 相关 features 段 + Founder 修改要求 + 当前版本（作为反面参考）
- 产出：重新生成的 Story+QA，覆盖原文件
- 主会话继续审新版本

**关键区分**（避免违反 CLAUDE.md DAG 强制清单 §1）：

- 🚫 **禁止**：主会话内 dispatch background agent **并发**执行 DAG TASK（会污染 context、撞 529、丢 batchcc 隔离）
- ✅ **允许**：Review Mode 内**单发**单个 subagent **重生一条** Story（这不是 DAG 执行，是后续修订）

v3.0 的 SKILL.md 必须在禁止和允许之间写清楚界限。

## 满足 CLAUDE.md DAG 强制清单

| 条 | 要求 | v3.0 做法 |
|----|------|----------|
| §1 | 显式两步走 + 禁止主会话 dispatch | SKILL.md 开头写明两步走；"约束"章节显式禁止主会话并发执行 DAG TASK |
| §2 | 激进执行约束 | DAG 每个 TASK 的 **完成标志** 必填可验证项；禁止"工作量大"等软借口 |
| §3 | 静默失败拦截器 | DAG 文件检测 Story 数 > 15 时 Fatal 停（候选太多，Phase 2 对账过粗）|
| §4 | State 位置避开 `.claude/` | 用 `.task-generate-stories/` 在**项目根**（不在 ~/.claude/） |
| §5 | 强制真 DAG 语法 + 生成后 grep 自检 | SKILL.md 内嵌完整 `## STAGE ## ... ## TASK ##` 模板；生成后 `grep -c '^## STAGE ##'` ≥ 2、`grep -c '^## TASK ##'` ≥ N+1 |

## 为什么不选其他方案

### ❌ 方案：Subagent 并行（不走真 DAG）

主会话 dispatch N 个 subagent 同时生成 Story，完成后主会话继续 Review。

- 技术上能拿到"独立 context window"效果
- 但违反 CLAUDE.md DAG 强制清单 §1（污染主 context、撞 529 超载、丢 batchcc 断点续传）
- Founder 明确要"真 DAG"，不是近似

### ❌ 方案：Review 作为 DAG 内的一个 TASK

让 batchcc 的收尾 TASK 里"问 Founder 逐条审"。

- DAG 是无人值守，收尾 TASK 独立子会话没有 Founder 交互能力
- batchcc 机制里没有"暂停等 Founder"的通道
- 硬塞进去会违反 DAG 的自主执行原则

### ❌ 方案：独立命令 `/review-stories`

把 Review Mode 拆成独立斜杠命令。

- Founder 要记两个命令
- 失去"状态感知自动切换"的简洁性
- 已被 Q1 B 选项明确 reject

## 风险与反面检验

- **两步走对 Founder 认知负担**：Generate → batchcc → Review 三步。缓解：每步结束明确打印"下一步做 X"。
- **REVIEW_QUEUE.md 是跨会话状态**：Founder 中途 Ctrl+C 后回来仍能从断点继续审（reviewed.log 记进度）。
- **打回重生的 subagent 上下文缺失**：subagent 独立会话无法看 Founder 的具体吐槽语气，只能看结构化的修改要求。缓解：输入 prompt 里明确写 "Founder said: ..."。
- **Review 全文展示长度**：10 条 × (Story + QA) 可能 5000+ 行累计。Founder 是产品负责人，审得起。如不够，未来可加 `/generate-stories --skip-ok-items` 只看标记有问题的。
- **每次 v.X 都在改 skill**：近三天连续改 07 → 08 → 今日 01。这是 AI-Only 协作的正常迭代节奏，每次改动有 decision record 留痕。

## 回滚条件

- batchcc 执行稳定性差（>20% 跑飞）→ 退回 v2.1 的假 DAG，承认基础设施不够成熟
- Founder 在 Review Mode 抱怨"全文太长"→ 加 `--skip-ok-items` 快速过模式
- 打回重生的 subagent 质量明显低于主 batchcc 产出 → Review Mode 的重生改为"加进 redo 队列 + 再跑一次 batchcc --redo-only"

## 联动影响

- ai-qa-stories v2.5 的 `scenario-outdated` 指引继续指向 `/generate-stories` 重跑（现在是真 DAG 流程，更严肃）
- ai-explore v4.0 无影响
- `refactor-project` / `test-plan` / `doc-quality-review` 等既有 DAG skill 继续保持——v3.0 是**向它们对齐**，不是创新

## 触发对话

- 2026-04-18 晚 Founder 在 flametree_pick 试跑 v2.1，Phase 1/2 完成后 Gate 1 UX 反馈 → v2.1 改成智能触发
- 2026-04-19（今日）Founder 更进一步纠正：Gate 2 要逐条看全文 + DAG 根本没实现真分散会话
- 这两次反馈触发 v3.0

## 参考

- DAG 规范：`~/.claude/commands/templates/workflow/DAG_FORMAT.md`
- DAG 强制清单：`~/.claude/commands/CLAUDE.md` §"DAG 命令强制清单"
- 参考 skill：`~/.claude/commands/refactor-project.md` / `~/.claude/commands/doc-quality-review.md`
- 前置决策：`2026-04-18-07-generate-stories-v2-dag-restructure.md` / `2026-04-18-08-generate-stories-v2.1-gate1-smart-trigger.md`
