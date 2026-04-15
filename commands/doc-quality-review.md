---
description: 项目文档质量审查（DAG：Trunk-Centric 分批诊断 + 机械执行）ultrathink
---

# 项目文档质量审查

## 使用方式（强制两步走）

```bash
/doc-quality-review              # 第一步：只扫描 + 生成 DAG 任务文件，不执行
batchcc task-doc-quality-review  # 第二步：独立会话执行 DAG，断点续传
```

> **⚠️ 严禁在当前会话内起 background agent 并发执行 DAG 任务。**
>
> 错误做法：`/doc-quality-review` 返回任务文件后，主会话用 Task/subagent 并发拉起 Stage 1 诊断。后果：
> - 子 agent 产出会通过 system-reminder 回填主会话 → 主 context 仍会爆（违背 skill 本身的设计前提）
> - 同时冲 API 触发 529 超载
> - 丢失 `batchcc` 的独立会话隔离和断点续传能力
>
> 唯一合法执行路径：用户（或自动化）在命令行显式运行 `batchcc task-doc-quality-review`。

## 目标

审查 `docs/` 下所有文档是否履行了它在文档体系中的职责。

**与 `/doc-update-context` 的区别**：

| 命令 | 参照物 | 回答的问题 |
|------|--------|----------|
| `/doc-update-context` | 文档 vs 代码 | 写的内容和代码一致吗？ |
| `/doc-quality-review`（本命令） | 文档 vs 文档标准 | 文档体系整体健康吗？ |

**本命令基本不读代码**。参照物是 `~/.claude/guides/doc-structure.md` 定义的文档职责和边界。

> **格式规范**：@~/.claude/commands/templates/workflow/DAG_FORMAT.md - DAG 统一规范（**必须遵循**）
> **前置建议**：先跑 `/doc-update-context` 保证"说的是真的"，再跑本命令保证"说得好"。

---

## 架构原则：Trunk-Centric 分批诊断

**核心信念**：跨文档冗余 90% 发生在**主干 ↔ 叶子**之间（叶子 ↔ 叶子若有大量冗余，说明该合并）。因此 Trunk 常驻每批次的 context，叶子按目录分批——跨批次盲区由 Trunk 间接填平。

**拒绝的替代方案**（见 `~/.claude/to-discuss.md` 历史讨论）：
- ❌ 一次性全读（50+ 文档会触发静默截断，违反铁律 5）
- ❌ 骨架聚类（"归簇判断"本质仍需读内容，节省有限）
- ❌ 下沉到 per-doc 独立审查（丧失跨文档视角）

---

## 审查维度（四条硬指标）

| 维度 | 操作定义 | 处方动作 |
|------|---------|---------|
| **唯一性 (Uniqueness)** | 任何一条信息是否只在一个文档中定义？ | 保留权威处、其他处改为引用 |
| **可预测性 (Predictability)** | 按 `doc-structure.md` 职责，AI 闭眼能否猜到某类信息在哪？ | 越界内容迁移到正确文档 |
| **信噪比 (Signal-to-Noise)** | 文档中是否有不属于本文档职责的长篇内容？ | 删除或迁移 |
| **价值 (Value)** | 文档是否仍被引用 / 仍有读者 / 未被新版本取代？ | 归档到 `docs/archive/YYYY-MM/` |

**Value 维度的信号**（满足任一触发归档处方）：
- ≥ 90 天未更新 **且** 内容已被其他文档覆盖 → `[归档] git mv`
- 引用的代码路径失效占比 > 50% → `[归档]`
- 整份文档被其他文档完全引用/重述 → `[合并] 删 A，在 B 中补充吸收说明`
- 单节孤立无被引 → `[瘦身] 删除该节`

阈值可在 state 文件 `archive_staleness_days` 字段覆盖（默认 90）。

**不再检查**：章节是否漂亮、段落是否流畅——这些是人类读者关心的。

---

## 状态文件：`docs/quality-review-state.json`

> **位置说明**：不放在 `.claude/` 下（避免权限围栏，自动化模式下每次写都要审批）。`docs/.` 前缀隐藏且与所审对象就近。

```json
{
  "standard_hash": "<doc-structure.md 的 sha256>",
  "trunk_docs": [
    "docs/PRODUCT_SOUL.md",
    "docs/PRODUCT_BEHAVIOR.md",
    "docs/ARCHITECTURE.md"
  ],
  "archive_staleness_days": 90,
  "batch_size_limit": 10,
  "docs": {
    "docs/features/random.md": {
      "doc_hash": "<sha256>",
      "reviewed_at": "2026-04-15",
      "reviewed_commit": "abc123"
    }
  }
}
```

**重审触发**（任一即需重审）：`doc_hash` 变 / `standard_hash` 变 / 文档未在 state 中。

**Trunk 默认集**（首次运行自动写入）：`PRODUCT_SOUL` + `PRODUCT_BEHAVIOR` + `ARCHITECTURE` + `doc-structure.md`（全局）。不加 ROADMAP（高频变化会触发全量重审）和 FEATURE_CODE_MAP（索引非规则）。用户可手动改 state 覆盖。

**豁免**：`--force` 全量重审。state 丢失只触发一次全量。

---

## 执行策略

### 第一步：扫描 + 分批（命令自身执行，非 DAG 节点）

1. 扫描 `docs/` 所有 `.md`，计算 hash
2. **硬排除编译产物 / 非人工维护文档**（不参与本命令审查；它们由各自的编译器 / 运行时工具验证）：
   - `docs/user-stories/qa/**/*.qa.md` — 由 `/generate-stories` 编译，由 `/ai-qa-stories` 运行时验证
   - `docs/archive/**` — 已归档，不再审查
   - 任何 `*-state.json` / `*.state.json` — 命令运行时 state，非文档
3. 读 state，按重审规则筛出待审文档集
4. **按目录聚合 + 切片**：同目录下文档归一批，单批 ≤ `batch_size_limit`（默认 10）。超过 10 的目录切片命名 `<dir>-a` / `<dir>-b`
5. Trunk 文档**不参与**分批——它们作为每个诊断批次的常驻输入

### 第二步：Fatal Error 拦截（Phase 1.5）

扫描完成后，以下任一命中 → 直接终止，打印切批建议：

- 单批切片后仍 > `batch_size_limit` × 1.5（即 15 份）— 切批逻辑失效
- Trunk 文档合计行数 > 3000（Trunk 本身已超重，需先瘦身）
- 总待审**批次数** > 50（注意：**批次 ≠ 文件**；同目录 ≤10 文档 = 1 批，切片后才算多批。50 批对应约 500 文档，DAG 并行足以承载，超过则说明项目文档已失控，应先归并）

> **这是对铁律 5 的守门员**：宁可罢工也不静默处理不完的诊断。

### 第三步：生成 DAG 任务文件

**产出位置：`.task-doc-quality-review/` 目录**（聚合：入口 `dag.md` + 阶段细节 + `state.json`，清理时整个目录一刀切）。

#### 重跑前清理

如果 `.task-doc-quality-review/` 目录已存在（上一轮残留），**先 `rm -rf .task-doc-quality-review/` 再重新生成**——避免新旧文件混合让 batchcc 解析到错误入口。

#### Stage 编排

| STAGE | 内容 | 模式 |
|-------|------|------|
| Stage 1 `diagnose` | 每批一个 TASK：输入 Trunk 全文 + 该批叶子 → 产出 `action-plan.{batch_id}.md` 片段 | **parallel** max_workers=4 |
| Stage 2 `merge` | 合并所有片段为 `review-action-plan.md` + 跨批次冲突检测（同一 Trunk 规则被多个叶子违反→去重 / 成对处方配对） | serial |
| Stage 3 `execute` | 每份有处方的文档一个 TASK，**激进执行处方**（见下方"Stage 3 执行约束"）| **parallel** max_workers=4 |
| Stage 4 `review` | **收尾审视**，见下文 | serial |

#### ⚠️ 入口文件硬约束（防退化为"扫描说明文档"）

历史教训：本命令实战时 AI 反复生成"人类可读的扫描+分批说明文档"（用 `## Stage 1: diagnose (parallel)` 这种描述性标题），batchcc 识别为"简单模式"把整份文档当 1 个任务喂出去，污染整个 `docs/`。

**`dag.md` 必须严格遵循 `@~/.claude/commands/templates/workflow/DAG_FORMAT.md` 的 STAGE/TASK 语法**，即至少含：

```markdown
# 文档质量审查

> **项目宏观目标**：[1-3 句话，让 batchcc 注入到每个子任务]

## STAGE ## name="diagnose" mode="parallel" max_workers="4"

## TASK ##
诊断 Batch 1: <dir>/

**目标**：对该批次叶子文档执行 4 维诊断（唯一性/可预测性/信噪比/价值），产出 `action-plan.batch_1.md`

**核心文件**：
- `docs/PRODUCT_SOUL.md` - [Trunk 参考]
- `docs/PRODUCT_BEHAVIOR.md` - [Trunk 参考]
- `docs/ARCHITECTURE.md` - [Trunk 参考]
- `docs/<dir>/*.md` - [叶子诊断对象]
- `.task-doc-quality-review/action-plan.batch_1.md` - [新建] 产出处方片段

**完成标志**：
- [ ] 已产出 `action-plan.batch_1.md`，包含每份叶子的处方清单（含 [归档]/[迁移]/[瘦身] 等动作标签）

文件: docs/<dir>/**/*.md, .task-doc-quality-review/action-plan.batch_1.md
排除: docs/PRODUCT_SOUL.md, docs/PRODUCT_BEHAVIOR.md, docs/ARCHITECTURE.md

## TASK ##
诊断 Batch 2: ...
（以下省略，每个批次一个 ## TASK ##）

## STAGE ## name="merge" mode="serial"

## TASK ##
合并所有诊断片段
... 略 ...

## STAGE ## name="execute" mode="parallel" max_workers="4"
（每份有处方的文档一个 TASK，按目录分批；遵守"Stage 3 执行约束"）

## STAGE ## name="review" mode="serial"
（按下方"Stage 4 收尾"模板）
```

**禁止形式**（batchcc 无法解析为 DAG，会退化为简单模式）：

- ❌ `## Stage 1: diagnose (parallel max_workers=4)` ——这是说明性标题，缺 `## STAGE ##` 分隔符
- ❌ `### Batch 1: user-stories/` 替代 `## TASK ##`
- ❌ 把扫描结果表格、Trunk 列表、批次清单作为 `dag.md` 主体（这些可以放文件头作为元数据，但 STAGE/TASK 必须是主结构）
- ❌ 把每个 stage 拆成 `task.stage1.batch_1.md` 等独立文件后在 dag.md 里只放 `@` 引用——可以拆但 dag.md 仍必须含 `## STAGE ##` / `## TASK ##` 顶层结构

#### 生成后自检（强制）

写完 `dag.md` 后**必须**执行以下自检，任一失败必须修正：

```bash
cd .task-doc-quality-review
test "$(grep -c '^## STAGE ##' dag.md)" -ge 4 || echo "❌ STAGE 数 < 4"
test "$(grep -c '^## TASK ##' dag.md)" -ge 4 || echo "❌ TASK 数 < 4"
grep -q '^## STAGE ## name="diagnose" mode="parallel"' dag.md || echo "❌ 缺 diagnose stage"
grep -q '^## STAGE ## name="review" mode="serial"' dag.md || echo "❌ 缺 review 收尾"
```

自检全过才能宣告 `/doc-quality-review` 完成。否则 batchcc 会退化为简单模式把整份文档当 1 个 cc 任务喂出去，**污染 docs/**。

### Stage 3 执行约束（反保守派，防止处方丢进 TODO）

> **核心原则**：处方是 Stage 2 已经产出的决策。Stage 3 的 TASK 是执行者，不是二次决策者。**默认全部执行**，TODO 是例外而非默认。

**必须在 Stage 3 机械执行、禁止转 TODO 的处方类型**：

| 处方类型 | 动作 | 为什么能自动执行 |
|---------|------|---------------|
| `[归档]` | `git mv` 到 `docs/archive/YYYY-MM/` | 可逆（`git revert`），保留历史 |
| `[删除]` | 直接删文档或删节 | 已在处方中指明，Stage 2 已验证"完全被覆盖" |
| `[迁移]` | 跨文档剪切 + 粘贴（成对处方） | 成对约束已在 Stage 2 配对，语义完整 |
| `[LastReviewed 更新]` | frontmatter 改日期 | 纯元数据 |
| `[路径修正]` | 字符串替换失效路径 | 客观正确 |
| `[权威冲突消除]` | 按 Stage 2 指定的"保留权威处 / 其他改引用" | 决策已做 |
| `[瘦身]` | 删除指明的章节 | 已在处方中指明 |
| `[frontmatter 补全]` | 按 doc-structure.md 补缺失字段 | 客观正确 |

**只有以下 3 类处方可以写入 TODO**（`review-action-plan.md` 里必须显式标注 `[需决策]`，否则视为必执行）：

1. **跨文档语义冲突**：例如 A 和 B 对同一概念定义不一致，且 Stage 2 无法判定哪方为权威（需要代码或产品负责人介入）
2. **代码路径需验证**：处方涉及"删除某段是否会误伤"，需要跑 `/doc-update-context` 或查源码才能确认
3. **产品方向决策**：涉及"整个目录该不该存在"等产品级问题

**严格禁止的"转 TODO"借口**：

- ❌ "工作量大" — 并行 4 个 TASK，工作量不是转单
- ❌ "涉及多文件" — 成对处方本就是多文件
- ❌ "需要小心" — 有 git 兜底，不叫小心叫拖延
- ❌ 自创 P0/P1 分级后 P1 延迟执行 — skill 无 P0/P1 概念，分级是借口

**Stage 3 TASK 的完成标志**：处方清单中每一条要么状态为 `✅ 已执行`，要么 `⏸ [需决策]` 并写入 TODO 原因。`⏸ 暂缓` / `⏸ 大工作量` 等模糊状态禁止出现。

### Stage 4 收尾（按 DAG_FORMAT 规范）

> **⚠️** 收尾 TASK 没有前序会话历史，靠 git diff/log + 文件系统自行发现产出。

**执行步骤**：
1. `git log --oneline -20` + `git diff --stat HEAD~N` 了解本轮全貌
2. 读 `review-action-plan.md` 对比计划 vs 实际执行
3. 读 state 确认 `reviewed_commit` 已更新
4. 自问：
   - 哪些处方未执行或标注"需用户决策"？
   - 发现的系统性问题（如 `doc-structure.md` 职责定义有缺陷）？
   - 归档到 `docs/archive/` 的文档是否都成对有吸收说明？
   - 是否触及 Fatal Error 边界警戒（批次数接近上限 → 建议发起文档归并）？
5. **直接写入项目根 `TODO.md`**，包含：
   - 本轮执行摘要（已审批次数、处方执行数、归档数）
   - 未执行/标注"需用户决策"的处方清单（每条含目标文档路径 + 决策点描述）
   - 系统性问题建议（如建议修订 `doc-structure.md` 或发起文档归并）
   - 下一步行动项（自包含：目标、核心文件、完成标志）

---

## 诊断 TASK 的输出契约

每个 Stage 1 的 TASK 产出 `action-plan.{batch_id}.md` 片段：

```markdown
# Batch: <batch_id> (<dir>)

## docs/features/random.md
- [越界] 第 X-Y 行「全局状态管理规则」属于 PRODUCT_BEHAVIOR.md 职责，迁移到 BEHAVIOR.md §状态机 章节；本文档对应位置改为引用
- [归档] 本文档最后更新 2024-08-12，内容已被 features/random_v2.md 完全覆盖，`git mv docs/features/random.md docs/archive/2026-04/`，在 random_v2.md 开头补充"吸收自 random.md"引用

## docs/features/share.md
- （无修改，职责清晰）

## 本批次跨文档观察
- share.md 与 random.md 都提到"结果页面布局"——候选冗余，Stage 2 合并时与其他批次交叉检查
```

Stage 2 合并时消除重复处方、配对"删 + 补"成对约束。

---

## 关键约束

1. **Stage 1 并行各批次只看 Trunk + 本批叶子**——不读全部文档，杜绝 context 爆炸
   - 扫描阶段已硬排除 `user-stories/qa/`、`docs/archive/`、`*-state.json`（编译产物 / 归档 / 运行时 state）
2. **Stage 3 TASK 只执行处方**——发现新问题一律进 TODO，不在本 TASK 中延伸处理
3. **归档走 `git mv` 不 rm**——保留 git 历史，符合"破坏性方案但可逆"
4. **成对处方**——删 A 必须在 B 中有对应"已吸收 X 章节"的补充处方
5. **本命令不读源码**——疑似代码不一致只记 TODO，由 `/doc-update-context` 处理
6. **state 是单一事实源**——不再用 HTML 注释、git log、frontmatter 等

---

## 严格禁止

1. **禁止在 `/doc-quality-review` 当前会话内起 background agent 执行 DAG TASK**——必须用 `batchcc` 独立会话。在主会话起 agent 会让子 agent 产出回填主 context、违背 skill 设计前提
2. **Fatal Error 拦截中不许 --force 绕过**（这是守门员，绕过会退化回静默失败）
3. **诊断批次不允许跨目录混编**（破坏"同目录语义相关度高"的假设）
4. **Stage 3 不允许自创 P0/P1 分级当延迟借口**（skill 无分级概念，处方就是处方）
5. **Stage 3 必须激进执行**：归档/删除/迁移/路径修正等可逆处方默认全做，禁止以"工作量"为由转 TODO（详见"Stage 3 执行约束"）
6. **不生成"一切 OK"走过场报告**，也不凑数制造伪问题
7. **不把自主判断的产品方向决策直接 execute**（如"这整个 features 目录该删了"——这种**才是**进 TODO 的合法场景）

---

## 相关文档

- @~/.claude/commands/templates/workflow/DAG_FORMAT.md - **DAG 统一规范**
- `~/.claude/guides/doc-structure.md` - 文档体系职责定义（Trunk 默认成员）
- `/doc-update-context` - 文档 vs 代码一致性（互补命令）
- 历史决策：`~/.claude/to-discuss.md` → Trunk-Centric 重构的讨论
