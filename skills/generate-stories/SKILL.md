---
name: generate-stories
description: >
  This skill should be used to generate user story documents for a project
  from existing documentation (PRODUCT_SOUL, PRODUCT_BEHAVIOR, features/).
  Use when the user says "generate stories", "生成用户故事", "create user
  stories", "写故事", or when a project needs docs/user-stories/ created
  for the first time. Also use when new features have been added and stories
  need updating. Outputs dual files: story.md (product narrative) + qa.md
  (compiled verification scripts). Story requires product owner confirmation
  before commit.
version: 1.0.0
---

# Generate Stories — 用户故事生成（双文件架构）

## 目的

从项目现有文档（SOUL + BEHAVIOR + features/ + ROADMAP）生成双文件用户故事：

| 文件 | 角色 | 读者 | 内容 |
|------|------|------|------|
| `docs/user-stories/NN-xxx.md` | **源码** | 人（产品验收）+ AI（理解意图） | 产品叙事：操作→预期→意图 |
| `docs/user-stories/qa/NN-xxx.qa.md` | **编译产物** | AI（ai-qa-stories 消费） | 结构化验证：Intent→curl→Assert |

**核心心智模型**：Story 是源码，QA 是编译产物。Story 变了就重新编译 QA。不手动编辑 QA 文件。

生成的 Story 需要**产品负责人确认业务准确性后 commit**——这是产品验收，不是代码审查。

## 触发条件

1. 项目首次需要创建 user-stories（目录不存在）
2. 新功能开发完成，需要补充对应的故事
3. 用户明确要求生成或更新故事

## 执行流程

### Step 1: 收集上下文

按优先级读取：
1. `docs/PRODUCT_SOUL.md` — 理解用户画像和核心价值
2. `docs/PRODUCT_BEHAVIOR.md` — 提取用户流程、状态机
3. `docs/features/*.md` — 理解各功能的交互细节、已知限制
4. `docs/ROADMAP.md` — 获取功能完成状态、Known Issues
5. 项目 CLAUDE.md — 获取 Debug Server 端口和可用端点

如有 Debug Server 运行，`curl localhost:$PORT/providers` 获取实际可用端点。

**降级策略**（标准文档不全时）：

| 缺失文档 | 替代来源 | 故事中标注 |
|---------|---------|-----------|
| SOUL | README + CLAUDE.md 推断用户画像 | ⚠️ 用户画像为推断 |
| BEHAVIOR | 代码结构 + features/ 逆推流程 | ⚠️ 流程为逆向推断 |
| features/ 为空 | 仅生成骨架故事（步骤留空） | 提示用户先补功能文档 |
| 全部缺失 | **终止**，建议先运行 `/learn-new-project` | — |

### Step 2: 识别核心旅程

从收集的上下文中提取核心用户旅程：

| 类型 | 必须覆盖 | 来源 |
|------|---------|------|
| 首次使用 | ✅ | SOUL（用户画像）+ BEHAVIOR（冷启动流程） |
| 日常核心操作 | ✅ | BEHAVIOR（主流程）+ features/（核心功能） |
| 数据管理 | ✅ | features/（CRUD 相关） |
| 设置/个性化 | 按需 | features/（settings） |
| 分享/协作 | 按需 | features/（share/export） |

**数量与裁剪指引**：
- **首次生成建议 3 条**：首次使用 + 1-2 条日常核心操作。后续按需补充
- **上限 5 条**：超过 5 条说明粒度太粗，应拆分
- **每条故事 ≤ 8 步**：超过 8 步的旅程拆为多条
- **增量模式**：已有故事时，走 Step 2.5

### Step 2.5: 增量模式（已有故事时）

如果 `docs/user-stories/` 已有故事文件：

1. **列出现有故事** — 读取所有 `*.md`（排除 README.md），记录已覆盖的旅程
2. **对比 features/** — 识别未覆盖的功能
3. **检查是否需更新** — 新功能可能改变已有流程
4. **只生成增量** — 新故事编号接续已有最大编号
5. **已有故事需更新时** — 标注修改建议但不直接覆盖，交由用户决定

### Step 3: 生成 Story 文件（产品叙事）

**严格按下方 Story 模板生成。** Story 是纯产品视角：用户操作→预期结果→意图。

**禁止在 Story 中出现**：
- ❌ ViewModel/Service/Repository 等代码类名
- ❌ curl 命令或 API 端点
- ❌ 平台差异表（已在 BEHAVIOR 中维护）
- ❌ 排障指南（属于 features/*.md）

### Step 4: 编译 QA 文件（验证脚本）

**这是关键的分步操作：先完成所有 Story，再逐条编译 QA。**

对每条 Story：
1. **读取刚生成的 Story** — 理解每个步骤的操作和预期
2. **读取 Debug Server 端点列表** — 确定可用的验证手段
3. **逐步映射**：Story 的每个步骤 → 对应的 curl + 断言
4. **写入 `docs/user-stories/qa/NN-xxx.qa.md`** — 按 QA 模板格式

**QA 编译规则**：
- 每个 Story 步骤至少映射一个验证（无对应端点时标 `# TODO`）
- Intent 必须是自然语言描述（帮助 AI 判断失败时是代码问题还是测试过期）
- 断言使用弹性表达（"非空"而非"恰好 N 条"）
- 端点依赖表帮助 ai-qa-stories 做上线前对账

### Step 5: 创建索引

生成 `docs/user-stories/README.md`：

```markdown
# User Stories

## 架构说明
- `*.md` — 产品故事（源码），描述用户旅程和验收标准
- `qa/*.qa.md` — 验证脚本（编译产物），供 `/ai-qa-stories` 自动验证
- Story 变更后需重新编译对应的 QA 文件

## 覆盖的核心路径
1. [首次使用](01-xxx.md) — {一句话描述}
2. [日常操作](02-xxx.md) — {一句话描述}
...

## 执行方式
通过 `/ai-qa-stories` 自动验证（只读 qa/ 目录）。

## 最后验证
{日期} — 全部通过 / 部分通过（详见报告）
```

### Step 6: 生成后自检

交付前逐条检查：

- [ ] 每条 Story 无代码类名、无 curl、无 API 端点
- [ ] 每条 Story 的验收标准表完整
- [ ] 每条 QA 至少有 1 个可执行的 curl 验证（无端点时为 `# TODO`）
- [ ] QA 中引用的端点在 `/providers` 中存在（或标注 `# TODO`）
- [ ] QA 的 Intent 描述清晰（AI 能从 Intent 判断失败原因）
- [ ] 断言使用弹性表达
- [ ] Story 和 QA 的步骤编号一一对应

### Step 7: 交付审核

**不自动 commit。** 展示生成的文件列表和摘要，等待用户审核：

```
生成了 N 条用户故事（双文件）：

Stories（产品叙事）：
1. docs/user-stories/01-first-time-user.md — 首次使用
2. docs/user-stories/02-daily-listening.md — 日常听歌

QA（验证脚本，编译自 Story）：
1. docs/user-stories/qa/01-first-time-user.qa.md — 5 个验证步骤
2. docs/user-stories/qa/02-daily-listening.qa.md — 7 个验证步骤

请审核 Story 的业务准确性后确认 commit。
QA 文件为编译产物，无需单独审核。
```

---

## Story 文件模板

路径：`docs/user-stories/NN-xxx.md`

```markdown
# 用户故事 {NN}：{故事名称}

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
1. {用户做什么（纯 UI 描述，如"点击底部 Tab 切换到音乐库"）}
2. ...

**预期**：
{用户看到什么结果（如"展示最近播放的专辑列表，每张显示封面和标题"）}

**意图**：{这一步解决用户什么问题}

---

### 步骤 2：{步骤标题}

**操作**：...
**预期**：...
**意图**：...

---

{重复步骤结构...}

---

## 验收标准

| 检查点 | 预期结果 |
|--------|---------|
| {用户视角的验收点} | ✅ {可观测的结果} |
| ... | ... |

---

## 已知限制

- {产品层面的限制，标注来源（如"ROADMAP Known Issues"）}

> 仅列出与本故事直接相关的限制。无限制则省略此段。
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

```bash
curl -s http://localhost:$PORT/state/xxx | jq '.field'
```

**Assert**:
- `field` 为 `expected_value`
- {其他断言}

---

## Scenario 2: {步骤标题}

**Intent**: {一句话}

```bash
curl -s -X POST http://localhost:$PORT/action/xxx -d '{"key":"value"}'
```

**Assert**:
- 返回 `ok: true`

```bash
# 验证副作用
curl -s http://localhost:$PORT/data/xxx | jq '.items | length'
```

**Assert**:
- 列表非空

---

{重复 Scenario 结构...}

---

## 端点依赖

| 端点 | 用途 | 类型 |
|------|------|------|
| /state/auth | 验证登录状态 | state |
| /data/tracks | 读取音乐列表 | data |
| /action/player/play | 触发播放 | action |

> 端点对账：ai-qa-stories 启动时会比对此表与 /providers 实际端点。
```

---

## 约束

- **Story 是源码，QA 是编译产物** — 修改需求时改 Story，然后重新编译 QA
- **分步生成** — 先完成所有 Story，再逐条编译 QA。不在同一推理过程中同时生成两者
- **不覆盖已有故事** — 如果 `docs/user-stories/` 已有文件，走 Step 2.5 增量模式
- **端口动态获取** — 从 CLAUDE.md 读取，curl 中用 `$PORT`
- **无 Debug Server 时** — QA 中 curl 写为 `# TODO: 补充验证命令（需 Debug Server）`
- **不要照抄状态机** — BEHAVIOR 的状态机是系统视角，Story 是用户视角，要翻译
- **已知限制标来源** — 每条限制注明出处
- **模板权威性** — 本 skill 的内联模板是权威来源。项目中已有 USER_STORIES_TEMPLATE.md 时应同步更新

## Gotchas

1. **Story 不写代码类名** — 旧模板有"系统行为"段（ViewModel/Service），新模板已移除。如果在已有 Story 中看到，编辑时删除
2. **QA 的 Intent 很重要** — 不是装饰。ai-qa-stories 失败时用 Intent 判断"是代码 bug 还是测试过期"
3. **断言弹性** — "列表非空"优于"恰好 5 条"。数据量变化不应导致 QA 失败
4. **qa/ 目录需要手动创建** — 首次生成时确保 `mkdir -p docs/user-stories/qa/`
5. **一条 Story 对应一条 QA** — 文件名保持一致（`01-xxx.md` ↔ `qa/01-xxx.qa.md`）
