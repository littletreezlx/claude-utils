# test-verify / log-audit 加反保守派执行约束

**日期**: 2026-04-15
**影响范围**: `~/.claude/skills/test-verify/SKILL.md`、`~/.claude/skills/log-audit/SKILL.md`（全局 skill）

---

## 1. 遇到的问题

用户反馈 `/test-verify` 和 `log-audit` 实战中"总是偷懒，只写一些"，怀疑是否需要像 `doc-quality-review` 一样重构成 DAG。

诊断后结论：**两者都不符合 DAG 判据**（context 不爆、已有并行机制、变异流程要求源文件独占），"偷懒"的真实成因是**skill 留白被保守派默认占据**，与 `doc-quality-review` 一样走的是同一反模式——"机械执行"的笼统措辞被 AI 解读为"只做最安全的"。

具体症状：

- **test-verify**：Tier 2 抽样 5 个文件、Tier 3 直接跳过被当"下次再说"借口；ESCAPED 发现后没当场修，被记录为"待补"
- **log-audit**：默认 diagnosis-only 被用户感知为"发现问题也不修"；🔴 Critical 和 🟡 Warning 混在一起等用户决策

---

## 2. 讨论过程

候选方案：

- **A. 整体 DAG 化**：类似 doc-quality-review，拆 diagnose/execute stage。否决——context 不爆（单变异只读 ±30 行）、变异必须源文件独占（无法真并行）、log-audit 本质是交互式审查，DAG 的独立会话隔离对它们没价值
- **B. 加激进执行约束**：参照 `doc-quality-review §Stage 3 执行约束`的"必做清单 + 例外清单 + 禁用借口"三段式。采纳

---

## 3. 最终方案

### test-verify

新增 `### 激进执行约束` 小节，含：

- **必做清单**（4 条，禁止转 TODO）：Tier 1 全量变异 / 关键词自动升 Tier 1 / ESCAPED 当场修 / 变异清单执行率 100%
- **例外清单**（2 类）：熔断触发（修复 2 次仍 ESCAPED）/ 测试基础设施异常
- **禁用借口**（5 条）：抽样当跳过借口 / 分批拖延 / 后续统一修 / 覆盖率思维 / 自创 P0/P1
- **完成标志**：每条变异必须有明确终态（CAUGHT / 已修复 / ESCALATION），禁止"待补"

### log-audit

保留 diagnosis-only 默认（尊重"不静默改代码"的原设计意图），但：

- 新增 `--fix` 触发词 + 中文近义词（"审日志并修复"/"审日志顺手修了"），进 aggressive 模式直接应用 🔴
- Triggers 表补入 `--fix` 形态
- 新增 `### 🔴 Critical 的强语义` 小节：**不允许降级**、**不允许隐藏**（🔴 不得因超 top 10 被折叠到 \_scratch），推荐动作必须是"建议立刻 reply 2"而非"酌情处理"

---

## 4. 为什么不选其他方案

### 不选 A（DAG 化）

- `doc-quality-review` 变 DAG 的核心驱动是"50+ 文档一次读爆 context"；test-verify 和 log-audit 都没这个压力（单候选只读 ±30 行）
- test-verify 的 inject/test/checkout 循环要求**同一源文件串行**，DAG 并行反而打架
- log-audit 是交互式 Action Menu 设计，DAG 的独立会话执行会打破"用户选择"这一核心闭环
- DAG 化本身有成本（batchcc 冷启动、任务文件生成）——用在 context 爆炸的场景值，用在已有并行的场景就是过度工程

### 不选"把 log-audit 默认改成 apply 🔴"

- 违反原 skill 的"Do not silently write files or edit code"原则
- 用户明确表达修复意图（`--fix`）才激进是更稳的权衡——默认 diagnosis-only 是正确的，问题是入口缺少快捷通道

---

## 5. 元原则（对 commands/CLAUDE.md 强制清单的补充）

`doc-quality-review` 的经验不是"所有复杂 skill 都该 DAG 化"，而是**"skill/command 在 AI-Only 项目里是可执行约束，留白必被保守派占据"**。当用户报告某个 skill "偷懒"时：

1. **先诊断 context 是否会爆** → 爆就 DAG 化；不爆走 2
2. **再诊断是否"笼统措辞被保守派解读"** → 是就加反保守派约束（必做/例外/禁用借口）
3. **最后诊断默认动作是否需要激进触发词** → 是就加 `--fix` 这类显式开关，而不是改默认

这三步有优先级差——DAG 化成本最高，反保守派约束次之，加触发词最轻。能用轻的解决就不要上重的。
