## ✅ [DECIDED 2026-04-15] [Workflow] doc-quality-review 扩展到大型项目的范式选择 (Ref: think 讨论 2026-04-15)

> **决策**: Approve B（Trunk-Centric 重构）+ 额外加 Value 维度 + state 换位 `docs/.quality-review-state.json` + DAG 四阶段（diagnose parallel / merge / execute parallel / review）
> **落地**: skill 重写完成 (`commands/doc-quality-review.md` 187 行)
> **决策记录**: `docs/decisions/2026-04-15-01-doc-quality-review-trunk-centric.md`
>
> 以下是讨论时的原始选项，保留作历史参考。

---



- **事实前提**:
  - 现 skill 架构：Phase 2 单 TASK 读全部待审文档做全局诊断，Phase 3 用 DAG 分散执行处方
  - 在 flametree_music 项目（50 份文档）实际运行时，Phase 2 默默只处理了 12 份核心文档，剩余 38 份既未审也未入队，AI 没有报错而是在总结后反问用户"要继续吗"
  - 这是典型的**铁律 5 违反** —— 没有亲眼观测到全量诊断完成就输出了成功报告

- **Gemini 核心主张**:
  1. **"50 份文档"本身是文档微服务化坏味道**，不是工具问题。AI-Only 项目下信息碎片化会让开发时 AI 看不到全局，事后加固审查工具无意义
  2. 跨文档冗余 90% 发生在**主干 ↔ 叶子**之间，叶子 ↔ 叶子几乎不应有冗余——如果有，说明该合并
  3. 正确范式是 **Trunk-Centric Review**：3-5 份主干文档（PRODUCT_SOUL / BEHAVIOR / doc-structure）常驻 context，叶子分批过。跨批次盲区由"主干"间接填平
  4. 立即修复静默失败：超阈值（文件数 > 15 或 token 估算超限）直接 Fatal Error 终止，而非默默截断
  5. 否决方案 B（双层 Map）/ C（下沉执行）/ D（grep 化）；否决 state 演化为关系记忆（LLM 维护 graph 会产生顽固幻觉）

- **Claude Code 立场**: Escalate

- **选项 A — 修 bug 不动范式 (保守)**:
  - 仅加 Phase 1.5 超限拦截器（文件数/token 估算超限 → Fatal Error）
  - 保留"一次性全读"的 Phase 2 诊断假设
  - 副作用：项目超过阈值时 skill 直接罢工，无降级路径——用户必须自己决定"要么瘦身文档要么放弃审查"
  - 改动量：skill 追加 ~20 行，不改核心架构
  - 倾向：Gemini 推荐作为第一步防御

- **选项 B — Trunk-Centric 范式转换 (激进)**:
  - Phase 2 拆成 `Immutable Trunk Context + 分批 Feature 文档`
  - 主干文档常驻 context（每批次重传），叶子文档分批 10-15 份
  - 跨批次冗余通过"同一主干规则被多个叶子违反"的模式被间接发现
  - 副作用：需要在 skill 或项目 CLAUDE.md 里定义"哪些是主干"（增加配置维护），默认可用 PRODUCT_SOUL / BEHAVIOR / ARCHITECTURE / doc-structure 作为合理默认
  - 改动量：skill 重写 Phase 2 流程 ~50 行，state 文件加 `trunk_docs` 字段
  - 倾向：Gemini 推荐作为正解；Claude Code 也倾向此方案，但承认"主干/叶子"分类有边界模糊风险（如 ROADMAP / FEATURE_CODE_MAP 归哪边？）

- **选项 C — 文档瘦身优先 (釜底抽薪)**:
  - 在项目级 CLAUDE.md 或 doc-structure.md 加入文档数量软阈值（如 20 份），超过触发 `/doc-consolidation` 新工作流
  - 强制把叶子 features 合并进主干或按领域聚合，抹除碎片
  - 副作用：需要新增一个跨项目工作流；合并本身是产品决策（哪些 feature 重要到值得独立文档），不能纯靠 AI 决定
  - 改动量：新增 skill / 命令；更新 doc-structure.md 的数量上限规则
  - 倾向：Gemini 建议作为中长期演进；Claude Code 认为这触及产品灵魂层（文档组织哲学）

- **反面检验**:
  - **A 的 Failure_Premise**: 半年后项目一过 15 份文档就报错，用户被迫要么砍文档要么 --force 绕过，久而久之 --force 成为事实默认，拦截器形同虚设
  - **B 的 Failure_Premise**: 主干/叶子的边界在实际项目中比想象更模糊——例如 features/random_selection.md 既描述了功能又定义了全局抽奖规则，归叶子就会漏检，归主干则失去批处理的收益；且随项目演化，"谁是主干"的判断本身需要持续维护
  - **C 的 Failure_Premise**: 文档是给 AI 的上下文——强行合并后单文件会变得过长（主干膨胀到 5000+ 行），AI 读取时仍要分块处理，只是把分片问题从"多文件"转移到"单文件内"，没有真正降维

- **决策选项**:
  - [ ] Approve A → 只加静默失败拦截器，Skill 核心不变
  - [ ] Approve B → 改造成 Trunk-Centric 范式，定义默认主干集
  - [ ] Approve C → 先推文档瘦身工作流，不改 skill
  - [ ] Approve A + B → 分两步走，先拦截静默失败，再做范式转换
  - [ ] Discuss → 再次 /think 深入追问（特别是"主干/叶子"边界定义）
  - [ ] Reject → 维持现状，接受 50+ 文档项目上该 skill 部分失效
