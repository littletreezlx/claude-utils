# doc-quality-review 范式从"一次性 Map"转为"Trunk-Centric 分批 DAG"

**日期**: 2026-04-15
**影响范围**: `~/.claude/commands/doc-quality-review.md`（全局 skill）

---

## 1. 遇到的问题

在 `flametree_music` 项目（约 50 份 docs/*.md）首次运行旧版 `/doc-quality-review` 时：

- Phase 2 单 TASK 设计要求一次性读入所有待审文档
- AI 实际只处理了 12 份核心文档（PRODUCT_*, ARCHITECTURE, 等），其余 38 份既未审查也未入队
- state 文件只记录 12 份 "reviewed"
- AI 输出"审查完成"成功报告后，在末尾才反问"还有别的没看过的文档吗？"

这是典型的**静默截断**——铁律 5（完成的定义 = 亲眼观测到代码在 Runtime 生效）的违反。Context 不够时 AI 没报错，而是默默处理部分后声称成功。

---

## 2. 讨论过程

用户提出 4 个候选方案后调用 `/think`（Gemini）挑战：

- **A**. 分批 Map + state 接力（按优先级切片）
- **B**. 双层 Map（先骨架再深度）
- **C**. 骨架诊断 + 下沉到 per-doc 独立审查
- **D**. grep 规则化静态匹配

Gemini 核心反驳：
- 否决 B（"归簇判断"本身仍需读内容，节省有限）
- 否决 C（per-doc 自审无法看见跨文档冗余）
- 否决 D（背离 LLM 语义能力，退化回 2010 年静态分析）
- 指出 A 思路对但前提有误——跨文档冗余 90% 发生在**主干 ↔ 叶子**，叶子 ↔ 叶子若有大量冗余说明应合并
- 正解：**Trunk-Centric** — 主干（3-5 份）常驻每个批次的 context，叶子按目录分批，跨批次盲区由主干间接填平
- 另指出 `.claude/quality-review-state.json` 位置会触发权限围栏，自动化模式下每次写都要审批

---

## 3. 最终方案

### 3.1 架构变更

旧: Phase 2 单 TASK 全读 → Phase 3 DAG 执行处方
新: DAG 四阶段：

| STAGE | 模式 | 作用 |
|-------|------|------|
| 1. diagnose | parallel (max 4) | 每批：Trunk 全文 + ≤10 份叶子（按目录聚合）→ action-plan 片段 |
| 2. merge | serial | 合并片段 + 跨批次冲突去重 + 成对处方配对 |
| 3. execute | parallel (max 4) | 每份 doc 一个 TASK 机械执行处方 |
| 4. review | serial | 收尾审视，写入 TODO.md（DAG_FORMAT 规范） |

### 3.2 新增 Fatal Error 拦截（Phase 1.5）

在生成 DAG 之前，以下任一命中 → 直接罢工而非静默降级：
- 单批切片后仍 > 15 份
- Trunk 合计 > 3000 行
- 总批次数 > 20

### 3.3 Value 维度（第四检查维度）

新增"是否仍有价值"维度，支持：
- 归档（≥90 天未更新 + 内容已被覆盖）→ `git mv` 到 `docs/archive/YYYY-MM/`
- 合并（完全被其他文档重述）→ 删 A + 在 B 中补充吸收说明
- 瘦身（单节孤立无被引）→ 删节

阈值 `archive_staleness_days` 在 state 中可配。

### 3.4 State 文件换位

从 `.claude/quality-review-state.json` → `docs/.quality-review-state.json`

原因：`.claude/` 默认是配置权限敏感区，自动化模式下每次写都被拦截。挪到 docs 下既避开权限围栏，又与管理对象就近。

### 3.5 Trunk 默认集

首次运行自动写入 state：
- `docs/PRODUCT_SOUL.md`
- `docs/PRODUCT_BEHAVIOR.md`
- `docs/ARCHITECTURE.md`
- `~/.claude/guides/doc-structure.md`（全局，跨项目）

**明确不加**：
- ROADMAP.md（高频变化会反复触发 standard_hash 失效 → 全量重审）
- FEATURE_CODE_MAP.md（索引而非规则，不含职责定义）

---

## 4. 为什么不选其他方案

| 方案 | 否决理由 |
|------|---------|
| 维持原"一次性 Map" | 违反铁律 5，项目规模增长时必然再次静默截断 |
| 双层 Map（骨架 → 深度） | 骨架阶段判断"哪些文档同簇"本质仍需读内容，省不了多少 context；且随项目扩大"簇边界"会模糊 |
| 骨架诊断 + per-doc 独立审查 | 两份文档各自都不觉得自己越界，但互相冗余这件事在独立视角下永远看不见 |
| grep 关键词库 | 产品术语演化快，关键词表维护成本高且规则会僵化；丢弃 LLM 语义优势 |
| LLM 维护文档关系图/索引 | Gemini 特别强调此路不通——自建 graph 会过期，下一次审查基于过期索引产生顽固幻觉 |
| todo-write + 用户手动接力 | 需要用户一次次触发；每次会话重建 context 成本高；没有并行 |

---

## 5. 可能的失败模式（事前验尸）

1. **主干/叶子边界模糊**：如 `features/random_selection.md` 既描述功能又定义全局抽奖规则，归叶子就会漏检。缓解：state 的 `trunk_docs` 用户可覆盖，边界模糊的文档可提升为 Trunk
2. **Fatal Error 拦截被 --force 绕过**：绕过会退化回静默失败。已在 skill 的"严格禁止"段显式禁止
3. **批次数逼近上限时**：skill 会在 review STAGE 提示"建议发起文档归并"，但没有对应归并 skill——这是未解决的下游缺口，候选未来工作
4. **Value 维度误判**：错误归档仍在活跃的文档。缓解：归档走 `git mv` 保留历史，出错可 `git revert`

---

## 6. 后续 TODO

- [ ] 观察第一次在真实项目运行的效果（回到 flametree_music 50 份文档场景）
- [ ] 如果批次数频繁逼近 20 上限，考虑开发配套的 `/doc-consolidation` skill 做文档归并
- [ ] 评估 Trunk 默认集在不同项目的适用度——特别是非产品类项目（如纯工具库）是否需要不同默认
