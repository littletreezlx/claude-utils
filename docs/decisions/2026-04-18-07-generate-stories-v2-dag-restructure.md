# 2026-04-18-07 generate-stories v2.0：DAG 全覆盖模式

## 背景

Founder 基于实操经验提出诊断：

> "感觉是不是要走 DAG 模式，他好像读太多文件会偷懒？总是一次生成不完整。"

以及决策倾向：

> "我感觉都不用增量，默认就 DAG 吧，因为好多项目前面生成的不好，我觉得可以重新走。"

这是继 ai-explore v4.0 + ai-qa-stories v2.5 之后，Cyborg 质量基础设施链的**第三环重构**——源头 story 生成质量。

## 诊断：为什么 v1.0 一次性生成不完整

Founder 的观察对应三个 LLM 行为机制：

| 现象 | 机制 |
|------|------|
| 读太多文件偷懒 | **上下文稀释**（SOUL+BEHAVIOR+features+ROADMAP 同时进入 → 注意力分散） + **注意力漂移**（AI 抓最显著片段，跳过不起眼但重要的） |
| 一次生成不完整 | **均匀压缩**——同一轮生成 3-5 条 Story，每条被压成差不多长度；编译 QA 时没"再读"Story，用的是简化后的记忆 |
| 跨 Story 不一致 | 同一推理窗口里的风格坍缩，后面条目被前面带偏 |

v1.0 硬伤（上一轮评估已列）：
- ① 没有覆盖完整性度量
- ② "上限 5 条"硬编码
- ③ 同一 AI 写 Story + 编 QA = 自己出题自己答

## 决策

**v1.0 → v2.0，DAG 全覆盖模式。**

### DAG 结构（5 Phase + 2 Founder Gate）

```
Phase 1  Context Digest          一次，压缩项目文档为"事实摘要"
Phase 2  Behavior Audit          从 BEHAVIOR 提取行为清单 + 候选 Story 列表
         ⏸ Founder Gate 1       审核候选 Story，选哪些 / 落选理由
Phase 3  并行 Story 生成          每条独立上下文，只读相关行为 + 事实摘要
Phase 4  并行 QA 编译             每条独立，只读对应 Story + 可用端点
Phase 5  Delivery                汇总 + README + /providers 对账
         ⏸ Founder Gate 2       审核业务准确性
```

### 关键设计决策

1. **无增量模式**：砍掉 `--add NN` / `--recompile-qa NN` 所有增量入口。Founder 明确倾向"重新走"优于"打补丁"。
2. **全覆盖**：每次运行 = 从零重写 `docs/user-stories/` 所有文件。旧文件直接覆盖。
3. **Git 是唯一回滚机制**：Gate 2 不通过就不 commit。通过后的旧故事在 git history。不设 `_archive/` 目录（与"Git 洁癖"原则一致，避免陈旧文件污染仓库）。
4. **Phase 1 压缩一次，后续共享**：避免每个 Phase 3/4 节点都重读 SOUL+BEHAVIOR+features。
5. **Phase 2 的对账表直接解决硬伤 ①**：Founder Gate 1 展示"行为清单 + 候选 Story + 映射关系"，覆盖完整性由 Founder 在此 gate 把关。
6. **取消"上限 5 条"**：数量由 Phase 2 的对账表决定，不由拍脑袋数字决定。
7. **断言严格性标准**：新增章节，明确"弹性不等于松散"（"非空"要搭配"结构断言"）。
8. **Phase 3/4 并行**：默认用主 agent 串行执行但每条独立上下文（Read 重置）；可选用 Agent tool dispatch subagent 真并行（适合 >8 条的场景）。

### 不选的替代方案

- **保留增量模式（双模式）**：复杂度增加但 Founder 明确拒绝
- **Phase 3 + Phase 4 合并为"逐条 Story+QA 打包生成"**：违背 DAG 思路，"自己出题自己答"问题加剧
- **归档旧故事到 `_archive/`**：违反 Git 洁癖原则，Git history 已经足够
- **引入 test-verify 红队验证作为必选 gate**：过度设计，先观察 DAG 化后的质量，再决定是否加

## 下游联动

### ai-qa-stories v2.5 小幅修订

v2.5 的失败详情里 `scenario-outdated` 归因写的是：
> "→ 触发 `/generate-stories` 重编 qa.md"

v2.0 后此指引修订为：
> "→ 建议 Founder 重跑 `/generate-stories`（全覆盖）"

差异：重跑会覆盖**所有**故事，不只失败那条。Founder 是否真的要重跑由他自行判断（可能选择先手动修 qa.md）。

### 与 superpowers:dispatching-parallel-agents 的关系

Phase 3/4 的可选"真并行"模式可以使用 `dispatching-parallel-agents` skill 或直接 Agent tool。skill 文档里不强制，作为优化手段提供。

## 风险与反面检验

- **Gate 1 可能成为瓶颈**：Founder 每次跑都要审候选清单。缓解：Gate 1 结构化展示，Founder 30 秒内判定。
- **全覆盖丢失 Founder 之前的微调**：铁律说 QA 是编译产物不该手动改。如果实际有手动改 Story，Gate 2 不通过就不 commit 能保护。
- **DAG 执行时间长于 v1.0**：可接受——质量优先于速度（AI-Only 项目 Founder 时间预算 <5 min / 审核，不是 <5 min / 生成）。
- **Phase 3/4 并行节点间口径不一致**：通过 Phase 1 的"事实摘要"+ 共享 Style Guide 缓解。仍观察到不一致 → 加 Phase 4.5 一致性校对节点。

## 回滚条件

3 个月内观察到：
- DAG 执行时间 >15 min 且 Founder 抱怨 → 简化 Phase（合并 Phase 3+4）
- Gate 1 落选率 >50% → Phase 2 的候选质量太差，需强化 Context Digest
- `scenario-outdated` 触发 Founder 重跑，但重跑后覆盖率反而下降 → 需要评估增量是否真的不该要

## 参考

- 前两个决策记录：`2026-04-18-05-ai-explore-v4-trust-framework.md` / `2026-04-18-06-ai-qa-stories-v2.5-alignment.md`
- 触发对话：2026-04-18 Founder 追问 generate-stories 写得好不好 → 提出 DAG 诊断
