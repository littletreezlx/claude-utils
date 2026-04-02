---
name: generate-stories
description: >
  This skill should be used to generate user story documents for a project
  from existing documentation (PRODUCT_SOUL, PRODUCT_BEHAVIOR, features/).
  Use when the user says "generate stories", "生成用户故事", "create user
  stories", "写故事", or when a project needs docs/user-stories/ created
  for the first time. Also use when new features have been added and stories
  need updating. Output requires human review before commit.
version: 0.2.0
---

# Generate Stories — 用户故事生成

## 目的

从项目现有文档（SOUL + BEHAVIOR + features/ + ROADMAP）自动生成 `docs/user-stories/` 初稿。生成的故事需要**人工审核后 commit**——故事是测试基准，不能由 AI 自行决定"什么是正确行为"。

## 触发条件

1. 项目首次需要创建 user-stories（目录不存在）
2. 新功能开发完成，需要补充对应的故事
3. 用户明确要求生成或更新故事

## 执行流程

### Step 1: 收集上下文

按优先级读取：
1. `docs/PRODUCT_SOUL.md` — 理解用户画像和核心价值
2. `docs/PRODUCT_BEHAVIOR.md` — 提取用户流程、状态机、**平台差异表**
3. `docs/features/*.md` — 理解各功能的交互细节、**已知限制和未实现项**
4. `docs/ROADMAP.md` — 获取功能完成状态、**Known Issues**
5. 项目 CLAUDE.md — 获取 Debug Server 端口和可用端点

如有 Debug Server 运行，`curl localhost:$PORT/providers` 获取实际可用端点。

### Step 2: 识别核心旅程

从收集的上下文中提取 3-5 条核心用户旅程：

| 类型 | 必须覆盖 | 来源 |
|------|---------|------|
| 首次使用 | ✅ | SOUL（用户画像）+ BEHAVIOR（冷启动流程） |
| 日常核心操作 | ✅ | BEHAVIOR（主流程）+ features/（核心功能） |
| 数据管理 | ✅ | features/（CRUD 相关） |
| 设置/个性化 | 按需 | features/（settings） |
| 分享/协作 | 按需 | features/（share/export） |

### Step 3: 生成故事文件

**严格按下方内联模板格式生成**。每条故事包含产品视角（给 PM/QA 看）和工程验证（给研发/AI 跑）两层信息。

### Step 4: 创建索引

生成 `docs/user-stories/README.md`：

```markdown
# User Stories

## 覆盖的核心路径
1. [首次使用](01-xxx.md) — {一句话描述}
2. [日常操作](02-xxx.md) — {一句话描述}
...

## 执行方式
通过 `/ai-qa-stories` 自动验证所有故事。

## 最后验证
{日期} — 全部通过 / 部分通过（详见各文件）
```

### Step 5: 交付审核

**不自动 commit。** 展示生成的文件列表和摘要，等待用户审核：

```
生成了 N 条用户故事：
1. docs/user-stories/01-first-time-user.md — 首次使用：登录→浏览→播放
2. docs/user-stories/02-daily-listening.md — 日常：搜索→播放→收藏
...

请审核后确认 commit，或提出修改意见。
```

---

## 故事文件模板

每条故事文件**必须**包含以下段落，按顺序排列：

```markdown
# 用户故事 {NN}：{故事名称} — {副标题}

## 故事概述

| 字段 | 值 |
|------|-----|
| **故事名称** | {名称} — {副标题} |
| **用户类型** | {具体到场景的用户描述，如"通勤路上听歌的用户"} |
| **核心诉求** | {一句话：用户想要什么} |
| **验收标准** | {关键路径摘要：A → B → C → D} |

---

## 用户流程

### 步骤 N：{步骤标题}

**前置条件**：{依赖什么状态/前序步骤}

**用户操作**：
1. {用户做什么（UI 层面的描述，如"点击底部 Tab 切换到音乐库"）}
2. ...

**系统行为**：
1. {系统做什么（ViewModel/Service 层面，如"调用 SearchViewModel.search(query)"）}
2. ...
{如有分支行为，用表格呈现：}
| 条件 | 行为 |
|------|------|
| ... | ... |

**意图**：{这一步解决用户什么问题}

**验证**：
\```bash
# {验证意图的简短描述}
curl -s http://localhost:$PORT/... | jq '...'
\```
**断言**：
- {具体到字段级别的预期，如 `playbackState` 为 `playing`}

---

{重复上述步骤结构...}

---

## 验收标准

| 检查点 | 预期结果 |
|--------|---------|
| {用户视角的验收点} | ✅ {可观测的结果} |
| ... | ... |

---

## 平台差异

| 功能 | 移动端 (iOS/Android) | 桌面端 (macOS) |
|------|---------------------|---------------|
| {功能点} | {移动端行为} | {桌面端行为} |
| ... | ... | ... |

> 仅列出与本故事相关的差异。无差异则省略此段。

---

## 已知限制

- {从 ROADMAP/BEHAVIOR/features 中提取的未实现项或已知问题}
- {标注来源，如"（BEHAVIOR 标注待优化）"或"（ROADMAP Known Issues）"}

> 仅列出与本故事直接相关的限制。无限制则省略此段。

---

## 排障指南

| 症状 | 可能原因 |
|------|---------|
| {用户/AI 可能遇到的失败} | {排查方向} |
| ... | ... |
```

### 模板要点说明

1. **三段式步骤结构**（操作→行为→意图）是骨架。确保每步都有用户视角（PM 看）和系统视角（研发看）
2. **curl 验证嵌入在每步内**，紧跟系统行为。不要把所有 curl 堆到文末——步骤内的验证让 `/ai-qa-stories` 可以逐步断言
3. **验收标准表**是独立段落，从用户视角汇总所有检查点（PM/QA 核对用）
4. **平台差异**从 BEHAVIOR 的"平台差异"表和 features 的平台标注中提取
5. **已知限制**从 ROADMAP 的 Known Issues、BEHAVIOR 的路由状态（❌ 标记）、features 的未实现项中提取。这些信息防止 QA 把"设计如此"报成 bug

---

## 约束

- **生成 ≠ 定稿**：AI 生成的故事是初稿，必须人工审核
- **不覆盖已有故事**：如果 `docs/user-stories/` 已有文件，只生成新增/缺失的
- **端口动态获取**：从 CLAUDE.md 读取，curl 中用 `$PORT`
- **不要照抄状态机**：BEHAVIOR 的状态机是系统视角，故事是用户视角。要翻译成用户操作序列
- **已知限制必须标注**：从 ROADMAP/BEHAVIOR 中提取的路由未实现（❌）、功能占位（🚧）等信息，写入对应故事的"已知限制"段

## Gotchas / 踩坑点

1. **不要猜端点名** — 如果 Debug Server 在运行就 curl /providers 获取真实端点；不在运行就从 CLAUDE.md 的命令示例中提取
2. **BEHAVIOR 的状态机 ≠ 用户故事** — 状态机是系统视角，故事是用户视角。要翻译，不要照抄
3. **断言不要太严格** — 留一定弹性（如"列表非空"而非"恰好 5 条"），避免频繁因数据量变化导致"过时"
4. **平台差异不要遗漏** — BEHAVIOR 中有明确的平台差异表，每条故事检查涉及的功能在移动端和桌面端是否有差异
5. **已知限制要标来源** — 每条限制注明出处（BEHAVIOR/ROADMAP/features），方便审核者判断是否仍然有效
