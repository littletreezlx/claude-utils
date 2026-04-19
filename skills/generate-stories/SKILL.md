---
name: generate-stories
description: >
  This skill should be used to generate user story documents for a project
  from existing documentation (PRODUCT_SOUL, PRODUCT_BEHAVIOR, features/).
  Use when the user says "generate stories", "生成用户故事", "create user
  stories", "写故事", or when a project needs docs/user-stories/ rewritten.
  v3.0 is a TRUE DAG: main session produces .task-generate-stories/dag.md,
  user runs batchcc for parallel isolated sub-session story generation, then
  main session re-entry auto-switches to Review Mode for line-by-line Founder
  full-text review. Always full-rewrite (no incremental). Outputs dual files:
  story.md + qa.md.
version: 3.2.0
---

# Generate Stories v3.0 — 真 DAG + 双模式

## 为什么 v3.0 是"真 DAG"

v2.0/v2.1 把 5 个 Phase 塞进同一个会话顺序执行，违反 `~/.claude/commands/CLAUDE.md` 的 **DAG 强制清单 §5**——那只是"看起来像 DAG 的阶段文档"。

**真 DAG** = 主会话产出 `.task-xxx/dag.md` 入口文件，用户手动 `batchcc` 在独立子会话并行执行。每个子会话独立 context window = **真·不偷懒、不稀释、不互相带偏**。

参考范式：`refactor-project` / `test-plan` / `doc-quality-review`。

---

## 两步走（强制）

```bash
/generate-stories                   # 第一步：主会话产 DAG 文件，不执行
batchcc task-generate-stories       # 第二步：独立子会话批量生成
/generate-stories                   # 第三步：再次调用，自动切 Review Mode 逐条审核
```

### 🚫 严禁

**禁止在当前会话内用 Task tool 起 background agent 并发执行 DAG TASK。**

后果（违反 CLAUDE.md DAG 强制清单 §1）：
- 子 agent 产出通过 system-reminder 回填主会话 → 主 context 爆炸
- 多 agent 同时冲 API 触发 529 超载
- 丢失 batchcc 的独立会话隔离和断点续传能力

**允许**（Review Mode 内）：单发一个 subagent 重生**单条**被打回的 Story（不是并发执行 DAG TASK，是后续修订）。

---

## 模式自动切换

主会话检测 `.task-generate-stories/` 状态决定入口模式：

```bash
# 状态探测（skill 执行时先跑）
if [ ! -d .task-generate-stories ]; then
  MODE="generate"
elif [ -f .task-generate-stories/REVIEW_QUEUE.md ]; then
  MODE="review"
elif [ -f .task-generate-stories/dag.md ]; then
  MODE="await_batchcc"     # 提示用户跑 batchcc
else
  MODE="generate"          # 残留目录，按生成处理（会覆盖）
fi
```

| 状态 | 行为 |
|------|------|
| 目录不存在 | Generate Mode |
| 有 `dag.md` 无 `REVIEW_QUEUE.md` | 提示"先跑 `batchcc task-generate-stories` 或 `batchcc task-generate-stories --restart`" |
| 有 `REVIEW_QUEUE.md` | Review Mode |

---

## Mode A: Generate

### Phase 1: Context Digest

**一次性读取项目文档，按压缩准则压缩为「事实摘要」供 DAG 所有子 TASK 复用。**

#### 读取优先级

1. `docs/PRODUCT_SOUL.md`
2. `docs/PRODUCT_BEHAVIOR.md`
3. `docs/features/*.md`
4. `docs/ROADMAP.md`
5. 项目 CLAUDE.md（仅读 Debug Server 端口段）
6. **Debug Server 源码**（用于端点静态提取，见下方）

#### 端点静态提取（v3.2 新增，不启动 Server）

**不要启动 Debug Server**。从源码静态提取即可——`/providers` 的输出只是源码 route 注册表的序列化，grep 等价。

```bash
# 1. 定位 Debug Server 源文件（路径灵活）
DEBUG_SERVER_FILE="lib/dev_tools/debug_server.dart"
[ -f "$DEBUG_SERVER_FILE" ] || \
  DEBUG_SERVER_FILE=$(grep -rlE "class DebugServer|static const int port" lib/ 2>/dev/null | head -1)

# 2. 提取所有端点（典型 Dart route 字符串模式）
if [ -f "$DEBUG_SERVER_FILE" ]; then
  grep -oE "'/(action|state|data|cyborg|providers)[a-zA-Z0-9/_-]*'" "$DEBUG_SERVER_FILE" | \
    tr -d "'" | sort -u
  SOURCE="source"
elif grep -qE '^##.*端点' CLAUDE.md 2>/dev/null; then
  # 降级：从 CLAUDE.md 端点段读
  SOURCE="claude_md"
else
  SOURCE="unknown"  # Gate 1 会触发
fi
```

提取结果按 `action / state / data / cyborg` 分类写入 digest.md"可用端点清单"章节（紧凑格式）：

```markdown
## 可用端点清单（来源：source / claude_md / unknown）

### Actions (N)
- /action/auth/login
- /action/auth/logout
- /action/groups/create

### States (M)
- /state/auth
- /state/groups

### Data (K)
...
```

**信息来源分级**（Gate 1 消费）：

| 来源 | 行为 |
|------|-----|
| `source`（源码 grep 成功）| 继续 Phase 2 |
| `claude_md`（降级）| 打印 warning："端点清单来源 CLAUDE.md，可能过时。建议核对或改从 debug_server.dart 源码" |
| `unknown`（完全不可得）| **Gate 1 直接触发**，不允许继续生成（QA 会大面积 TODO，意义存疑） |

#### 降级策略

| 缺失文档 | 替代 | Story 中标注 |
|---------|------|------------|
| SOUL | README 推断 | ⚠️ 用户画像为推断 |
| BEHAVIOR | 代码结构 + features/ 逆推 | ⚠️ 流程为逆向推断 |
| features/ 为空 | 仅生成骨架 | 提示先补功能文档 |
| 全部缺失 | **终止**，建议先 `/learn-new-project` | — |

#### 压缩准则（严格执行，不是可选）

每条原始内容按下表判断是否进 digest：

| 类别 | ✅ 进 digest | ❌ 不进 digest（下沉到 features/*.md 按需读） |
|------|------------|----------------------------------------------|
| 产品定位 | 一段话核心 | 市场分析 / 长篇 slogan |
| 用户画像 | 1-2 类核心用户 | 次要用户群细分 |
| 状态机 | 核心骨架（主路径 + 关键分叉） | 全状态枚举 / 边缘错误路径 |
| features | 功能清单一行描述 | 每个 feature 完整交互流 |
| 端点 | `/providers` 全量清单（紧凑）| 每个端点返回结构细节 |
| 技术栈 | 核心技术 + 硬限制 | 开发工具链 / 测试框架 |
| 差异化点 | 核心差异化（1-3 条） | 竞品对比 / 营销卖点 |
| Known Issues | 影响 Story 生成的限制 | 历史 issue 流水账 |

**原则**：某类 Story 专属细节（比如 Story 05 的分享详细流程）不进 digest，由该 Story TASK 在执行时按需读 `features/*.md` 相关段落。

#### 末尾自检（必做）

digest 写完后对每个章节/段落自问：

> 这段是 N 个子 TASK 都会用到的吗？还是只有 1-2 个会用？

- 多 TASK 通用 → 保留
- 1-2 TASK 专用 → **删除**，下沉到"该 Story TASK 核心文件列 features/*.md"

#### 梯度行数约束

| 层级 | 行数 | 处理 |
|------|------|------|
| 目标 | ≤ 300 | 推荐，保持压缩锐度 |
| 软上限 | ≤ 500 | 打印 warning 继续（项目偏复杂，二次审视是否还能砍） |
| 硬上限 | ≤ 800 | **Fatal 停**，建议启用 digest 分片或进一步压缩 |

```bash
LINES=$(wc -l < .task-generate-stories/digest.md)
if [ $LINES -gt 800 ]; then
  echo "FATAL: digest $LINES 行超 800 硬上限。启用分片模式或继续压缩。"
  exit 1
elif [ $LINES -gt 500 ]; then
  echo "⚠️ WARNING: digest $LINES 行超 500 软上限。二次审视压缩准则是否严格执行。"
fi
```

**不允许 `--force` 绕过 800 硬上限**（CLAUDE.md §3 静默失败拦截器原则）。

#### Digest 分片（软上限触发时启用）

当项目复杂到主 digest 超 500 行时，按业务域拆分：

```
.task-generate-stories/
├── digest.md              # 通用部分（产品定位/用户/核心状态机/端点清单）
├── digest-<domain-a>.md   # 某类 Story 专用（被 Story N/M 引用）
├── digest-<domain-b>.md   # 另一类（被 Story X 引用）
└── ...                    # 总数 ≤ 5 个
```

- 主 digest ≤ 500 行
- 每个分片 ≤ 300 行
- 分片总数 ≤ 5（超过说明项目应该拆多个 skill 或分阶段交付）

分片后，DAG 入口文件中每个 Story TASK 的"核心文件"显式列出需要的分片（示例见 Phase 3 模板）。

**产出**：`.task-generate-stories/digest.md`（+ 可选分片）

### Phase 2: Behavior Audit + 端点预对账

**从 digest 提取所有可观测行为 → 候选 Story 对账表 + 端点预对账表。**

#### 2a. 行为对账（v3.0 原有）

产出行为清单 / 候选 Story 覆盖映射 / 落选理由 / 覆盖率统计。结构见 v2 模板。

#### 2b. 端点预对账（v3.2 新增）

对每条候选 Story 基于 Story 意图**估算**需要的端点类型，与 Phase 1 提取的端点清单对照：

```markdown
## 端点预对账

| Story | 预计端点 | 实际状态 | 缺失数 |
|-------|---------|---------|-------|
| 01 首次使用 | /action/auth/login, /state/auth, /data/profile | ✅ ✅ ✅ | 0 |
| 02 日常操作 | /action/groups/select, /state/groups | ✅ ✅ | 0 |
| 05 分享 | /action/share/upload | ⏭️ MISSING | 1 |
| 07 清单模式 | /action/stack/start, /state/stack, /data/items | ⏭️ ✅ ✅ | 1 |
| ... | | | |

**汇总**
- 总预计端点数: N
- 缺失数: M  
- 缺失率: M/N = **X%**
```

写入 `behavior-audit.md` 末尾。缺失率是 Gate 1 的真实数据来源。

**预对账规则**：
- AI 根据 Story 意图推断需要的端点类型（增/删/改/读 哪个数据域）
- 估算层面允许偏差——Phase 4 子 TASK 编译 QA 时会精确对账
- 预对账的价值是**Gate 1 前**提前暴露大面积缺失，不是精确计数

### Gate 1（智能触发，v2.1 保留）

Phase 2 结束后 AI 自查：

| 自查项 | 达标条件 | 数据来源 |
|--------|---------|---------|
| 覆盖率 | ≥ 85% | Phase 2 行为对账 |
| 落选归因 | 100% 有明确理由 | Phase 2 行为对账 |
| **端点信息来源** | `source`（源码 grep 成功）或 `claude_md`（降级允许）| Phase 1 端点静态提取 |
| **端点缺失率** | ≤ 30% | Phase 2 端点预对账 |
| 产品优先级分叉 | 无 | Claude Code 综合判断 |

**触发 Gate（任一命中）**：
- 覆盖率 < 85% 且剩余行为无法归因 → 列出无法归因的行为问 Founder
- 端点来源 = `unknown` → 源码 + CLAUDE.md 都读不到端点，QA 大面积 TODO 无意义，问 Founder 是否补 Debug Server 文档
- 端点缺失率 > 30% → 列出缺失端点清单，建议先补 Debug Server 再生成
- 产品优先级分叉 → 只展示该分叉的 A/B 选项

全部达标 → 打印一行：
```
✅ Gate 1 自动通过：覆盖率 X%，端点缺失 Y%，无产品优先级分叉。进入 DAG 生成。
```

<!-- 触发条件细节已在上方「触发 Gate」表格中说明 -->

### Phase 3: 生成 DAG 入口文件

**⚠️ 静默失败拦截器（CLAUDE.md §3）**：

```bash
STORY_COUNT=$(候选 Story 数量)
if [ $STORY_COUNT -gt 15 ]; then
  echo "FATAL: 候选 Story 数 $STORY_COUNT > 15。Phase 2 对账粒度过粗，"
  echo "请重做 Phase 2 合并相似候选，或分阶段交付（先做 v1 核心 10 条）。"
  exit 1
fi
```

**不允许 `--force` 绕过。** >15 条说明行为清单没提炼，DAG 执行会浪费 API 额度。

**产出**：`.task-generate-stories/dag.md`。入口模板（必须完整照抄结构，填充项目特定内容）：

```markdown
# {项目名} user stories 生成

> **项目宏观目标**：
> 基于 `.task-generate-stories/digest.md`（项目事实摘要）+ `behavior-audit.md`
> （覆盖对账表），为 docs/user-stories/ 生成双文件（Story + QA），每条在独立
> 子会话中生成避免上下文稀释 / 注意力漂移 / 风格坍缩。全覆盖模式，覆盖旧文件。

## STAGE ## name="generate" mode="parallel" max_workers="4"

## TASK ##
Story 01: {Story 标题}

**目标**：生成 `docs/user-stories/01-{slug}.md` 和 `docs/user-stories/qa/01-{slug}.qa.md`，覆盖行为 {B-A1, B-A2}。

**核心文件**：
- `.task-generate-stories/digest.md` - [参考] 项目事实摘要（仅此不读其他 docs/）
- `.task-generate-stories/behavior-audit.md` - [参考] 本 Story 覆盖的 B-A1 / B-A2 行为描述
- `docs/features/{feature-name}.md` - [参考] 仅读与本 Story 相关的段落
- `docs/user-stories/01-{slug}.md` - [新建] Story（见模板章节）
- `docs/user-stories/qa/01-{slug}.qa.md` - [新建] QA（见模板章节）

**完成标志**：
- [ ] Story 严格按模板，≤ 8 步，无 ViewModel/Service/curl/API 端点
- [ ] QA 每个 Scenario 都有 curl + Assert（无端点则标 `# TODO: 缺少端点 <name>`）
- [ ] QA 末尾 `端点依赖` 表写入对账状态（对每个引用端点实际 curl 探测）
- [ ] 断言满足严格性标准（见下方）

**执行提示**：
- ✅ 独立上下文原则：只读本 TASK 列出的"核心文件"相关段落，禁止"为保险起见再读 BEHAVIOR 全文"
- ✅ 不读其他 Story 或 QA 文件（防风格坍缩）
- ❌ 禁用软借口（"文件关联很多"/"不小心读多一点"）；digest.md 300 行已够

文件: docs/user-stories/01-{slug}.md, docs/user-stories/qa/01-{slug}.qa.md

## TASK ##
Story 02: {Story 标题}
... (同上结构)

## TASK ##
Story NN: (最后一条)

## STAGE ## name="review" mode="serial"

## TASK ##
产出校验 + 写 REVIEW_QUEUE.md

**目标**：纵观 generate stage 所有产出，校验齐全，生成 `.task-generate-stories/REVIEW_QUEUE.md` 供 Founder Review Mode 消费，并生成 `docs/user-stories/README.md`。

**⚠️ 重要**：你没有前序 TASK 的会话历史。通过以下方式了解已完成工作：
- `git log --oneline -20` 查看本轮 generate stage 新增文件
- `git diff --stat HEAD~N` 查看具体 Story 文件是否都已提交
- 读取 `.task-generate-stories/dag.md` 了解计划 Story 列表
- `ls docs/user-stories/` 和 `ls docs/user-stories/qa/` 扫描产出

**执行步骤**：
1. 扫描 `docs/user-stories/[0-9]*.md` 和 `docs/user-stories/qa/[0-9]*.qa.md`
2. 对账 dag.md 中计划的 Story 和实际生成
3. 对每条产出做快速自检（不展开审内容，只查结构）：
   - Story 步骤数 ≤ 8
   - 无代码类名（grep `ViewModel|Service|Repository|curl`）
   - QA 包含 `端点依赖` 表
4. 写 `.task-generate-stories/REVIEW_QUEUE.md`：
   ```markdown
   # Review Queue for user-stories
   > 由 batchcc 收尾 TASK 产出。主会话 /generate-stories 再次调用时消费此文件进入 Review Mode。

   ## 待审 Stories
   - [ ] 01-{slug}.md + qa/01-{slug}.qa.md | 自检: ✅ 结构合规 | 覆盖: B-A1, B-A2
   - [ ] 02-{slug}.md + qa/02-{slug}.qa.md | 自检: ⚠️ Story 9 步超限 | 覆盖: B-B1
   - [ ] 03-...

   ## Missing（计划但未生成）
   - Story 05: {slug} — TASK 失败，见 state.json
   ```
5. 生成 `docs/user-stories/README.md`（索引 + 架构说明 + 覆盖率摘要）

**完成标志**：
- [ ] REVIEW_QUEUE.md 写入
- [ ] README.md 生成
- [ ] 所有计划 Story 都有产出（或明确列入 Missing）

文件: .task-generate-stories/REVIEW_QUEUE.md, docs/user-stories/README.md
验证: test -f .task-generate-stories/REVIEW_QUEUE.md && test -f docs/user-stories/README.md
```

### 生成后自检（CLAUDE.md §5 强制）

产出 `dag.md` 后**必须**跑以下自检，任一失败立即修正：

```bash
# 1. 真 DAG 语法（不是伪 DAG）
STAGE_COUNT=$(grep -c '^## STAGE ##' .task-generate-stories/dag.md)
TASK_COUNT=$(grep -c '^## TASK ##' .task-generate-stories/dag.md)
[ $STAGE_COUNT -ge 2 ] || { echo "FATAL: STAGE 数 $STAGE_COUNT < 2"; exit 1; }
[ $TASK_COUNT -ge $((N+1)) ] || { echo "FATAL: TASK 数不足，期望 >=$((N+1))"; exit 1; }

# 2. 禁止形式检查（CLAUDE.md §5）
grep -qE '^## Stage [0-9]+:' .task-generate-stories/dag.md && \
  { echo "FATAL: 出现伪 DAG 标题 '## Stage X:'，必须改为 '## STAGE ## name=...'"; exit 1; }
grep -qE '^### Batch [0-9]+:' .task-generate-stories/dag.md && \
  { echo "FATAL: 出现伪 TASK 标题 '### Batch X:'，必须改为 '## TASK ##'"; exit 1; }

# 3. 必备文件
test -f .task-generate-stories/digest.md || { echo "FATAL: digest.md 缺失"; exit 1; }
test -f .task-generate-stories/behavior-audit.md || { echo "FATAL: behavior-audit.md 缺失"; exit 1; }

# 4. 收尾 STAGE
grep -q 'name="review"' .task-generate-stories/dag.md || \
  { echo "FATAL: 缺少 name=\"review\" 收尾 STAGE"; exit 1; }
```

### 告知用户

全部自检通过后打印：

```
✅ Generate Mode 完成。产出：
   .task-generate-stories/digest.md (N 行)
   .task-generate-stories/behavior-audit.md (覆盖率 X%)
   .task-generate-stories/dag.md (N 条 Story TASK + 1 review TASK)

下一步：运行 `batchcc task-generate-stories` 执行并行生成
（独立子会话，避免主 context 污染。不要在本会话内 dispatch subagent 并发执行 DAG）

完成后再次运行 `/generate-stories` 自动进入 Review Mode 逐条审核。
```

**本 skill 到此结束**。不继续执行 DAG，不等 batchcc 完成。

---

## Mode B: Review

### 触发

检测到 `.task-generate-stories/REVIEW_QUEUE.md` 存在 → 自动进入 Review Mode。

### 执行流程

1. **读状态**：
   - `REVIEW_QUEUE.md`（待审清单）
   - `.task-generate-stories/reviewed.log`（已审记录，不存在则建）

2. **逐条审核**（Founder 选择的 Q2 B 模式 = 全文审核）：

   对每条未审 Story 执行以下循环：
   
   a. 读取 `docs/user-stories/NN-{slug}.md` **全文**
   b. 读取 `docs/user-stories/qa/NN-{slug}.qa.md` **全文**
   c. 展示给 Founder：
      ```
      ━━━━━━━━━━ Story NN/Total: {标题} ━━━━━━━━━━
      
      📖 Story 全文:
      {docs/user-stories/NN-{slug}.md 内容}
      
      🧪 QA 全文:
      {docs/user-stories/qa/NN-{slug}.qa.md 内容}
      
      ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
      
      请回复：
        ✅ 通过
        ✏️ [具体修改要求，如"步骤 3 的预期不合理，应该是..."]
        ❌ 重做（整体不行）
      ```
   d. 等待 Founder 回复

3. **Founder 回复处理**：
   
   - `✅ 通过` → 追加 `reviewed.log`（`NN-{slug} OK <timestamp>`），下一条
   - `✏️ {修改要求}` → 主会话 **dispatch subagent** 即时重生该条（见下方）
   - `❌ 重做` → 同 ✏️ 但不带修改要求

4. **全部审完**：
   
   - 全部 ✅ → 清理 `.task-generate-stories/` + 触发 `git-workflow` skill commit
   - 仍有未审（Ctrl+C 中断）→ 提示"继续运行 /generate-stories 恢复 Review Mode"

### 打回重生（Q3 A，主会话 dispatch subagent）

用 `Task` tool 即时 dispatch 一个 subagent（`subagent_type: general-purpose`）：

**subagent prompt 构造**：
```
你是一个独立的 Story+QA 重生子 agent。主 agent 的 Founder 对现有 Story NN 不满意，
需要你基于以下材料重新生成：

## 项目事实摘要
{.task-generate-stories/digest.md 全文}

## 本 Story 覆盖的行为
{从 behavior-audit.md 提取 B-A1, B-A2 对应段落}

## 相关 features 段落
{仅与本 Story 相关的 features/*.md 片段}

## 当前版本（作为反面参考，超越之）
{docs/user-stories/NN-{slug}.md 当前内容}
{docs/user-stories/qa/NN-{slug}.qa.md 当前内容}

## Founder 的具体修改要求
{Founder 原话}

## 任务
1. 按 Story + QA 模板重新生成（见下方模板章节）
2. 覆盖原文件 `docs/user-stories/NN-{slug}.md` 和 `docs/user-stories/qa/NN-{slug}.qa.md`
3. 返回"已重新生成 NN-{slug}，主要变更：..."

严格遵守：
- Story ≤ 8 步
- 无代码类名
- QA 端点对账
- 断言严格性（非空 + 结构 or 精确值）
```

Subagent 完成后（通常 30-60 秒），主会话回到步骤 2.c 重新展示 Story+QA 全文让 Founder 审新版本。

**与 DAG 执行的区别**（避免违反 CLAUDE.md §1）：
- ✅ **允许**：Review Mode 内**单发**一个 subagent 重生**单条** Story（不是并发，不是 DAG）
- 🚫 **禁止**：主会话内 dispatch 多个 subagent 同时跑多条 Story（那是"绕开 batchcc 执行 DAG"）

### 全部通过 → 清理 + commit

```bash
# 清理任务目录（保留 .task-generate-stories 的意义是 batchcc 状态，审核完成即无用）
rm -rf .task-generate-stories/

# 触发 git-workflow commit
# (由 skill 调用 git-workflow skill 生成 commit message 并提交)
```

---

## 断言严格性标准（v2 保留）

弹性不等于松散，每条断言至少满足"量级 + 结构"二选一：

| 弹性级别 | 写法 | 判断 |
|---------|------|------|
| ❌ 太松 | `列表非空` | 1 条也非空，漏抓"只剩 1 条不正常" |
| ✅ 合适 | `列表至少 3 条 且 每条包含 id/title 字段` | 量级 + 结构都约束 |
| ✅ 合适 | `status == "active"` | 枚举值精确 |
| ❌ 太严 | `列表恰好 5 条` | 数据量变化会 false alarm |

**规则**：
1. 枚举值 → 精确（`status == "active"`）
2. 数量 → 量级约束（`>= N`），不要精确值
3. 结构 → 必填字段存在 + 类型对
4. 关系 → 跨字段一致性（`created_at < updated_at`）

---

## Story 文件模板

路径：`docs/user-stories/NN-xxx.md`

```markdown
# 用户故事 {NN}：{故事名称}

> 覆盖行为: B-A1, B-A2 (参见 `.task-generate-stories/behavior-audit.md`)

## 故事概述

| 字段 | 值 |
|------|-----|
| **用户类型** | {具体到场景的用户描述} |
| **核心诉求** | {一句话：用户想要什么} |
| **前置依赖** | {可独立运行 / 依赖 story NN} |
| **验收标准** | {关键路径摘要：A → B → C → D} |

---

## 用户流程

### 步骤 1：{步骤标题}

**操作**：{用户做什么，纯 UI 描述}
**预期**：{用户看到什么结果，可观测}
**意图**：{这一步解决用户什么问题}

---

{重复步骤结构，≤ 8 步}

## 验收标准

| 检查点 | 预期结果 |
|--------|---------|
| {用户视角} | ✅ {可观测的结果} |

## 已知限制

- {产品层面的限制，标注来源}
```

---

## QA 文件模板

路径：`docs/user-stories/qa/NN-xxx.qa.md`

```markdown
# QA：{故事名称}

> 编译自: [../NN-xxx.md](../NN-xxx.md)
> Debug Server Port: $PORT
> 前置依赖: {可独立运行 / 依赖 QA NN}

## Scenario 1: {步骤标题}

**Intent**: {一句话：这步验证什么}

\`\`\`bash
curl -s localhost:$PORT/state/xxx | jq '.field'
\`\`\`

**Assert**:
- `field` 为 `expected_value`
- 列表至少 N 条 且 每条含 id/title 字段

{重复 Scenario 结构...}

## 端点依赖

| 端点 | 用途 | 类型 | 对账状态 |
|------|------|------|---------|
| /state/auth | 验证登录状态 | state | ✅ MATCH |
| /action/remote/sync | 远程同步 | action | ⏭️ MISSING |
```

---

## 约束

- **两步走不可跳**（CLAUDE.md §1）— /generate-stories 只产 DAG，用户手动 batchcc；不得在主会话内 dispatch background agent 并发执行 DAG TASK
- **DAG 真语法**（CLAUDE.md §5）— 入口文件必须有 `## STAGE ## name="..." mode="..."` 和 `## TASK ##`；禁用 `## Stage 1:` `### Batch 1:` 等伪语法
- **生成后 grep 自检**（CLAUDE.md §5）— STAGE ≥ 2、TASK ≥ N+1、无禁止形式；任一失败立即修正
- **候选 Story > 15 时 Fatal 停**（CLAUDE.md §3）— 不允许 `--force` 绕过
- **State 位置**（CLAUDE.md §4）— `.task-generate-stories/` 在**项目根**，不在 `~/.claude/`
- **Review Mode 必须全文**— Q2 B 选项，逐条展示 Story+QA 完整内容；不是摘要
- **Review 中 subagent 单发限制**— 只允许 Review Mode 单发一个 subagent 重生单条；不得并发多个
- **全覆盖模式** — 每次运行覆盖现有 `docs/user-stories/`，git 是回滚机制
- **无增量** — 不支持 `--add` / `--recompile-qa`；想改就重跑
- **职责边界：端点静态提取，不做运行时检测**（v3.2）— 本 skill 从 `debug_server.dart` 源码 grep 端点清单（静态）；**不启动 Debug Server**、**不 curl `/providers`**、**不做 SERVER_BUG 检测**（handler 运行时 bug 是 `ai-qa-stories` 三态对账 MATCH/MISSING/SERVER_BUG 的职责，归因 `server-handler-bug` 计工具错误预算）
- **事实摘要梯度**（v3.1）— 目标 ≤ 300 行 / 软上限 500（warning）/ 硬上限 800（Fatal 停）。超 500 行触发 digest 分片（`digest.md` + `digest-<domain>.md`）。压缩准则和末尾自检不可跳（见 Phase 1）

## Gotchas

1. **Phase 1 事实摘要是 DAG 的命脉** — 所有子 TASK 都只读 digest.md + behavior-audit.md 的自己那段 + 必要的 features 段，不读其他 docs
2. **每个子 TASK 独立会话**（batchcc 跑） — 不要在 TASK 里写"参考其他 Story 保持风格一致"这种需要跨会话记忆的指令
3. **收尾 TASK 无前序会话记忆** — 靠 git log / 文件扫描发现 generate stage 产出
4. **Review Mode 可中断恢复** — reviewed.log 记已审，中途 Ctrl+C 后再跑 /generate-stories 从断点继续
5. **打回重生的 subagent 是独立会话**— 主会话传给它 digest + 该条 audit 段 + Founder 修改要求；完成后主会话重新读生成的文件展示
6. **ai-qa-stories 归因 scenario-outdated 不自动触发本 skill**— Founder 判断是否整体重跑（重跑意味着走完 Generate + batchcc + Review 整个流程）

## 变更历史

- **3.2.0** (2026-04-19)：**端点静态提取 + 职责边界**。根因：v3.1 对"Debug Server 不完善"场景处理不足（Phase 1 只读 CLAUDE.md，Gate 1 的"端点缺失率"无数据来源）。初次提议方案含"启动 Server curl `/providers`"被 Founder 质疑过度设计——源码即真相，grep 等价于 `/providers`。v3.2 改进：(1) Phase 1 新增端点静态提取（`grep -oE "'/(action|state|data|cyborg)/..."` debug_server.dart）；(2) Phase 2 新增端点预对账表，每条候选 Story 估算需要端点与实际清单对比；(3) Gate 1 新增"端点信息来源"和"端点缺失率"两个自查项（unknown 源头直接触发 Gate）；(4) 约束章节明确"职责边界"——静态提取是本 skill，SERVER_BUG 检测是 ai-qa-stories 职责，避免未来再被带偏启动 Server。详见 `~/.claude/docs/decisions/2026-04-19-03-generate-stories-v3.2-static-endpoint.md`。

- **3.1.0** (2026-04-19)：**digest 梯度约束 + 压缩准则**。根因：v3.0 落地同日 Founder 在 flametree_pick 跑 Generate Mode 产出 digest 244 行（简单项目偏长）+ 质疑 300 行硬约束对复杂项目不友好。v3.1 改动：(1) 行数梯度（目标 ≤300 / 软上限 500 warning / 硬上限 800 Fatal），不允许 `--force` 绕过硬上限；(2) Phase 1 引入**压缩准则表**明确"进/不进 digest"判断（features 完整交互流下沉到 features/\*.md 按需读）；(3) 末尾自检"每段是 N TASK 通用还是 1-2 TASK 专用"；(4) 超 500 行启用 **digest 分片**（`digest.md` + `digest-<domain>.md`，每 Story TASK 按需引用分片）。详见 `~/.claude/docs/decisions/2026-04-19-02-generate-stories-v3.1-digest-gradient.md`。

- **3.0.0** (2026-04-19)：**真 DAG + 双模式**。v2.0/v2.1 的"DAG"在同一会话顺序执行，违反 CLAUDE.md DAG 强制清单 §5（退化为"看起来像 DAG 的阶段文档"）。Founder 在 flametree_pick 试跑 v2.1 后两点纠正：(1) Gate 2 不是一次看 N 条摘要而是逐条看全文；(2) DAG 必须是"分散到不同会话"。v3.0 分两模式：**Generate Mode**（主会话产 `.task-generate-stories/dag.md` 真 DAG 入口）+ **Review Mode**（状态感知自动切换，逐条展示 Story+QA 全文审核）；打回重生用主会话 Task tool 单发 subagent 即时完成；严格满足 CLAUDE.md DAG 强制清单 §1-5。详见 `~/.claude/docs/decisions/2026-04-19-01-generate-stories-v3-true-dag-mode.md`。

- **2.1.0** (2026-04-18)：Gate 1 条件触发（达标自动通过）。假 DAG 架构下的局部修复。

- **2.0.0** (2026-04-18)：引入"伪 DAG"（所有 Phase 同会话执行）。v3.0 发现这违反 DAG 规范，已废弃架构。断言严格性标准 / Story+QA 模板 / 全覆盖模式 / 取消 5 条上限等内容保留进 v3.0。

- **1.0.0** 及更早：双文件架构（Story 源码 + QA 编译产物）。核心架构保留。
