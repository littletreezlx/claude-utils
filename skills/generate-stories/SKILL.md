---
name: generate-stories
description: >
  This skill should be used to generate user story documents for a project
  from existing documentation (PRODUCT_SOUL, PRODUCT_BEHAVIOR, features/).
  Use when the user says "generate stories", "生成用户故事", "create user
  stories", "写故事", or when a project needs docs/user-stories/ rewritten.
  v2.0 runs as a 5-Phase DAG with 2 Founder Gates; always full-rewrite (no
  incremental mode). Outputs dual files: story.md + qa.md. Story requires
  product owner confirmation before commit.
version: 2.0.0
---

# Generate Stories — DAG 全覆盖模式

## 目的

从项目现有文档（SOUL + BEHAVIOR + features/ + ROADMAP）生成双文件用户故事。**v2.0 改为 DAG 流水线**，每次运行从零重写，用 Git 做版本控制。

| 文件 | 角色 | 读者 | 内容 |
|------|------|------|------|
| `docs/user-stories/NN-xxx.md` | **源码** | 人（产品验收）+ AI（理解意图） | 产品叙事：操作→预期→意图 |
| `docs/user-stories/qa/NN-xxx.qa.md` | **编译产物** | AI（ai-qa-stories 消费） | 结构化验证：Intent→curl→Assert |

**核心心智模型**：Story 是源码，QA 是编译产物。Story 变了就重新编译 QA。不手动编辑 QA 文件。

## 为什么 v2.0 是 DAG

v1.0 一次性生成 3-5 条 Story + 编译 QA，实操暴露三个 LLM 行为陷阱：

| 现象 | 机制 |
|------|------|
| 读太多文件偷懒 | 上下文稀释 + 注意力漂移——AI 抓最显著片段，跳过不起眼但重要的 |
| 一次生成不完整 | 均匀压缩——每条 Story 被压成差不多长度；编译 QA 时没"再读"Story，用的是简化记忆 |
| 跨 Story 风格不一致 | 同一推理窗口里的风格坍缩，后面条目被前面带偏 |

DAG 化解决方案：
- **Phase 1 一次压缩，后续共享** → 消除重读开销
- **Phase 2 对账表** → 把覆盖完整性变成可视决策，不靠 AI 拍脑袋
- **Phase 3/4 每节点独立上下文** → 焦点集中，不偷懒，不被相邻条目带偏

## 运行模式

**只有一种模式：全覆盖 DAG。** 每次运行：

1. 从零生成所有 Story + QA
2. 覆盖 `docs/user-stories/` 现有文件（git 是唯一回滚机制）
3. 经 2 个 Founder Gate 后才 commit

**不支持**：`--add` 增量、`--recompile-qa NN` 单条重编。ai-qa-stories 归因 `scenario-outdated` 时，建议 Founder 手动判断是否要重跑本 skill（整集重做）。

## 触发条件

1. 项目首次需要创建 user-stories（目录不存在）
2. Founder 判断现有故事集质量不够好，决定重做
3. 重大功能迭代后，故事集需要整体重写
4. 用户明确要求生成或重新生成

---

## DAG 执行流程

```
Phase 1  Context Digest       （一次，压缩所有文档为「事实摘要」）
            ↓
Phase 2  Behavior Audit       （提取行为清单 + 候选 Story）
            ↓
         ⏸ Founder Gate 1    （审核覆盖完整性）
            ↓
Phase 3  并行 Story 生成       （每条独立上下文）
            ↓
Phase 4  并行 QA 编译          （每条独立，对账 /providers）
            ↓
Phase 5  Delivery             （README + 对账结果汇总）
            ↓
         ⏸ Founder Gate 2    （审核业务准确性，通过后才 commit）
```

### Phase 1：Context Digest

**一次性读取项目文档，压缩为「事实摘要」供后续 Phase 复用。**

按优先级读取：
1. `docs/PRODUCT_SOUL.md` — 用户画像和核心价值
2. `docs/PRODUCT_BEHAVIOR.md` — 用户流程、状态机
3. `docs/features/*.md` — 交互细节、已知限制
4. `docs/ROADMAP.md` — 完成状态、Known Issues
5. 项目 CLAUDE.md — Debug Server 端口和可用端点

**降级策略**：

| 缺失文档 | 替代来源 | 故事中标注 |
|---------|---------|-----------|
| SOUL | README + CLAUDE.md 推断用户画像 | ⚠️ 用户画像为推断 |
| BEHAVIOR | 代码结构 + features/ 逆推流程 | ⚠️ 流程为逆向推断 |
| features/ 为空 | 仅生成骨架故事（步骤留空） | 提示用户先补功能文档 |
| 全部缺失 | **终止**，建议先运行 `/learn-new-project` | — |

**产出**：写入 `_scratch/generate-stories/digest-YYYY-MM-DD.md`，包含：
- 项目一句话描述
- 用户画像（按场景分类）
- 核心功能列表（feature-level）
- 关键状态机（从 BEHAVIOR 提取）
- 可用端点清单（`/providers` 快照）
- 已知限制 + Known Issues

**长度硬约束**：≤ 300 行。超过 = Context Digest 没压缩到位，重做。

### Phase 2：Behavior Audit

**基于 Phase 1 的事实摘要，建立「行为清单 → 候选 Story」的对账表。**

这是解决覆盖完整性硬伤的核心步骤。产出的对账表是 Founder Gate 1 的决策材料。

**步骤**：

1. 从 Phase 1 的"关键状态机"和"核心功能列表"提取所有**可观测行为**（用户能感知的操作/状态转移/数据变化）
2. 按行为性质归类：首次使用 / 日常核心操作 / 数据管理 / 设置 / 分享协作 / 边界 & 异常 / 数据同步
3. 对每类提出候选 Story，并标注：
   - 该 Story 预计覆盖哪些行为
   - 剩余未覆盖行为（落选）+ 落选理由

**产出**：写入 `_scratch/generate-stories/behavior-audit-YYYY-MM-DD.md`：

```markdown
## 行为清单

### 首次使用
- [ ] B-001 用户首次启动 App，看到引导
- [ ] B-002 用户首次添加第一条数据
- [ ] B-003 ...

### 日常核心操作
- [ ] B-011 ...
- [ ] B-012 ...

（...按所有类别列全）

## 候选 Story 清单

### Story 01: 首次使用者完成首次添加
- 预计覆盖: B-001, B-002
- 未覆盖但同类的: B-003（落选理由：边缘路径，ROADMAP 未规划）

### Story 02: 日常主流程
- 预计覆盖: B-011, B-012, B-015
- 未覆盖但同类的: B-013（落选：依赖远程同步，放到 Story 05）, B-014（落选：企业用户专属）

（...每条候选 Story 都要有覆盖映射 + 落选说明）

## 覆盖率

- 总行为数: 23
- 候选覆盖: 18
- 落选: 5（理由均已说明）
- 覆盖率: 78%
```

### ⏸ Founder Gate 1

**展示 behavior-audit 文档给 Founder，当场决策**：

- ✅ 通过 → 进入 Phase 3
- ✏️ 调整 → Founder 勾选要保留/删除/新增的候选 Story，修改后重新计算覆盖率
- ❌ 驳回 → 重做 Phase 1 或 Phase 2（Context Digest 不准 / 行为清单遗漏）

Gate 1 的意义：**把"要生成什么"的决策权从 AI 移交给 Founder**，避免 AI 自作主张导致覆盖偏斜。

### Phase 3：并行 Story 生成

**对 Gate 1 通过的每条候选 Story，独立生成 Story 文件。**

**独立上下文规则**（这是 DAG 的核心收益）：
- 每条 Story 开始生成前，明确只读：Phase 1 事实摘要 + 该 Story 对应的行为描述 + 相关 features/*.md 的**具体段落**
- **不读**：其他 Story 文件、整本 features/、整本 BEHAVIOR（事实摘要已提炼好）
- **不读**：之前已生成的 Story 内容（防止风格坍缩）

**并行化选项**：
- **默认（串行独立上下文）**：主 agent 逐条生成，每条开始前显式"重置注意力"（重新 Read 该条依赖的段落）
- **可选（真并行 subagent）**：故事 >8 条时，用 `Agent` tool dispatch subagent 并行执行（参考 `superpowers:dispatching-parallel-agents`）。每个 subagent 接收 (事实摘要 + 单条行为 + Story 模板)，返回单条 Story 内容

**每条 Story 的生成约束**：
- 严格按下方 Story 模板
- **禁止**出现：ViewModel/Service 等代码类名、curl 命令、API 端点、平台差异表、排障指南
- 长度：≤ 8 步，超过则该 Story 应在 Phase 2 拆分（Gate 1 未捕获说明对账不细，回 Phase 2）

### Phase 4：并行 QA 编译

**对每条 Story，独立编译 QA 文件。**

**独立上下文规则**：
- 每条 QA 开始编译前，明确只读：该 Story 完整内容 + 项目 `/providers` 端点列表
- **不读**：其他 Story 或其他 QA（防止 QA 互相抄）
- **不读**：Phase 1 事实摘要（Story 已足够，减少噪音）

**编译规则**：
- Story 每步骤至少映射一个 curl + Assert（无对应端点 → 标 `# TODO: 缺少端点 <name>`）
- **Intent 必须是自然语言**（AI 失败时用 Intent 判断是代码 bug 还是测试过期）
- **端点依赖表**（末尾）——ai-qa-stories 用它做三态对账

**端点对账**（Phase 4 内部完成，不等到 ai-qa-stories）：

```bash
# 对每个引用的端点实际调用
for ENDPOINT in $(提取 QA 中所有 /action/... /state/... /data/...); do
  STATUS=$(curl -s -o /dev/null -w '%{http_code}' "localhost:$PORT$ENDPOINT")
  # 记录 MATCH / MISSING / SERVER_BUG
done
```

**对账产出**写入 qa 文件末尾"端点对账状态"小节。MISSING 的端点在 QA 中标 `# TODO`。

### Phase 5：Delivery

**汇总产出 + Founder Gate 2 材料**。

1. 生成 `docs/user-stories/README.md`（索引 + 架构说明 + 覆盖率）
2. 打印交付摘要（见下方模板）
3. 触发 Founder Gate 2

### ⏸ Founder Gate 2

**展示交付摘要 + 抽查 1-2 条 Story 给 Founder**：

```
生成了 N 条用户故事（DAG 全覆盖模式）：

覆盖率（vs Phase 2 行为清单）: 18/23 = 78%
端点对账（vs /providers）: 10/12 MATCH, 1 MISSING, 1 SERVER_BUG

Stories（产品叙事）：
1. docs/user-stories/01-first-time-user.md — 首次使用 → 覆盖 B-001, B-002
2. docs/user-stories/02-daily-use.md — 日常核心 → 覆盖 B-011, B-012, B-015
...

QA（验证脚本）：
1. docs/user-stories/qa/01-first-time-user.qa.md — 5 scenarios, 5 MATCH
2. docs/user-stories/qa/02-daily-use.qa.md — 7 scenarios, 6 MATCH / 1 TODO
...

已知问题：
- Story 04 依赖 /action/remote/sync，该端点目前为 SERVER_BUG
- Story 05 标 TODO: 缺少 /data/articles 端点

请审核业务准确性后确认 commit。
QA 文件为编译产物，无需单独审核。
```

- ✅ 通过 → commit
- ✏️ 局部修改 → Founder 指出哪条需要重改，重跑该 Story 对应的 Phase 3 + Phase 4
- ❌ 整体不过 → 回 Phase 2（行为清单不对）或 Phase 3（生成质量不达标）

---

## 断言严格性标准（替代 v1.0 的"断言弹性"原则）

v1.0 说"弹性——列表非空而非恰好 5 条"。但过度弹性 = 断言形同虚设。

v2.0 标准：**弹性不等于松散，每条断言至少满足"量级 + 结构"二选一**。

| 弹性级别 | 写法 | 判断 |
|---------|------|------|
| ❌ 太松 | `列表非空` | 1 条也非空，漏抓"只剩 1 条不正常" |
| ✅ 合适 | `列表至少 3 条 且 每条包含 id/title 字段` | 量级 + 结构都约束 |
| ✅ 合适 | `status == "active"` | 精确值（状态枚举类断言必须精确） |
| ❌ 太严 | `列表恰好 5 条` | 数据量变化会 false alarm |

**断言写作规则**：
1. **枚举值** → 精确（`status == "active"`）
2. **数量** → 量级约束（`>= N` 或 `N ± 20%`），不要精确值
3. **结构** → 必填字段存在 + 类型对（`has field id && id is int`）
4. **关系** → 跨字段一致性（`created_at < updated_at`）

---

## Story 文件模板

路径：`docs/user-stories/NN-xxx.md`

```markdown
# 用户故事 {NN}：{故事名称}

> 覆盖行为: B-001, B-002 (参见 `_scratch/generate-stories/behavior-audit-YYYY-MM-DD.md`)

## 故事概述

| 字段 | 值 |
|------|-----|
| **用户类型** | {具体到场景的用户描述，如"通勤路上听歌的用户"} |
| **核心诉求** | {一句话：用户想要什么} |
| **前置依赖** | {可独立运行 / 依赖 story NN（原因）} |
| **验收标准** | {关键路径摘要：A → B → C → D} |

---

## 用户流程

### 步骤 1：{步骤标题}

**操作**：
1. {用户做什么（纯 UI 描述）}

**预期**：
{用户看到什么结果（可观测的 UI 描述）}

**意图**：{这一步解决用户什么问题}

---

{重复步骤结构，≤ 8 步}

---

## 验收标准

| 检查点 | 预期结果 |
|--------|---------|
| {用户视角的验收点} | ✅ {可观测的结果} |

---

## 已知限制

- {产品层面的限制，标注来源}

> 无限制则省略此段。
```

---

## QA 文件模板

路径：`docs/user-stories/qa/NN-xxx.qa.md`

```markdown
# QA：{故事名称}

> 编译自: [../NN-xxx.md](../NN-xxx.md)
> Debug Server Port: $PORT
> 前置依赖: {可独立运行 / 依赖 QA NN}

---

## Scenario 1: {步骤标题}

**Intent**: {一句话：这步验证什么}

\`\`\`bash
curl -s localhost:$PORT/state/xxx | jq '.field'
\`\`\`

**Assert**:
- `field` 为 `expected_value`
- 列表至少 N 条 且 每条含 id/title 字段

---

{重复 Scenario 结构...}

---

## 端点依赖

| 端点 | 用途 | 类型 | 对账状态 |
|------|------|------|---------|
| /state/auth | 验证登录状态 | state | ✅ MATCH |
| /data/tracks | 读取列表 | data | ✅ MATCH |
| /action/player/play | 触发播放 | action | 🔥 SERVER_BUG (providers 声明但 handler 未注册) |
| /action/remote/sync | 远程同步 | action | ⏭️ MISSING |

> Phase 4 编译时已完成对账；ai-qa-stories 运行时会重新对账，状态可能变化。
```

---

## 约束

- **DAG 流水线不可跳 Phase** — 每个 Phase 都要执行，Phase 1 产物是后续输入
- **全覆盖模式** — 每次运行覆盖 `docs/user-stories/` 所有文件，git 是唯一回滚
- **不读未声明依赖** — Phase 3 节点只读自己需要的段落（事实摘要 + 单条行为 + 相关 features 段），禁止"为保险起见再读一下 BEHAVIOR"
- **Gate 1 / Gate 2 不可跳** — 两个 Founder 审核是全覆盖模式的安全保障
- **事实摘要 ≤ 300 行** — 超过 = Phase 1 压缩失败，回做
- **每条 Story ≤ 8 步** — 超过 = Phase 2 对账太粗，回 Phase 2 拆分
- **端点对账在 Phase 4 完成** — 不等 ai-qa-stories 才发现端点缺失
- **模板权威性** — 本 skill 的内联模板是权威。项目 USER_STORIES_TEMPLATE.md 有则同步更新

## Gotchas

1. **Phase 1 事实摘要是 DAG 的命脉** — 太粗后续都是垃圾，太细失去 DAG 意义。300 行是目标长度
2. **Phase 3 的"独立上下文"靠显式 Read 重置** — 主 agent 串行执行时，每条 Story 开始前显式 Read 需要的段落，别假设上下文干净
3. **真并行 subagent 慎用** — Subagent 之间风格可能更不一致，只在 >8 条故事时考虑
4. **Gate 1 是最重要的 Gate** — Founder 在这里审"我们要测什么"；Gate 2 只审"写得准不准"
5. **断言弹性不等于松散** — "列表非空"不够，至少加"结构或量级"约束
6. **QA 的 Intent 很重要** — 不是装饰。ai-qa-stories 失败时用 Intent 判断是代码 bug 还是测试过期
7. **一条 Story 对应一条 QA** — 文件名严格对应（`01-xxx.md` ↔ `qa/01-xxx.qa.md`）
8. **ai-qa-stories 归因 scenario-outdated 不自动触发本 skill** — Founder 判断是否整体重跑

## 变更历史

- **2.0.0** (2026-04-18)：DAG 全覆盖模式。根因：Founder 实操观察到 v1.0 一次性读太多文件 → 上下文稀释 + 注意力漂移 + 均匀压缩导致生成不完整。改为 5 Phase DAG + 2 Founder Gate：Phase 1 Context Digest 一次压缩、Phase 2 Behavior Audit 对账表（解决覆盖完整性硬伤）、Phase 3/4 并行独立上下文（解决偷懒）、Phase 5 Delivery 对账 /providers。取消 v1.0 "上限 5 条"硬编码（数量由对账表决定）、取消增量模式（--add / --recompile-qa）、新增断言严格性标准（弹性不等于松散）。详见 `~/.claude/docs/decisions/2026-04-18-07-generate-stories-v2-dag-restructure.md`。

- **1.0.0** 及更早：双文件架构（Story 源码 + QA 编译产物）、降级策略、Story/QA 模板、Intent 字段、端点依赖表。核心架构保留进 v2.0。
