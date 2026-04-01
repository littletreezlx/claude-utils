---
name: generate-stories
description: >
  This skill should be used to generate user story documents for a project
  from existing documentation (PRODUCT_SOUL, PRODUCT_BEHAVIOR, features/).
  Use when the user says "generate stories", "生成用户故事", "create user
  stories", "写故事", or when a project needs docs/user-stories/ created
  for the first time. Also use when new features have been added and stories
  need updating. Output requires human review before commit.
version: 0.1.0
---

# Generate Stories — 用户故事生成

## 目的

从项目现有文档（SOUL + BEHAVIOR + features/）自动生成 `docs/user-stories/` 初稿。生成的故事需要**人工审核后 commit**——故事是测试基准，不能由 AI 自行决定"什么是正确行为"。

## 触发条件

1. 项目首次需要创建 user-stories（目录不存在）
2. 新功能开发完成，需要补充对应的故事
3. 用户明确要求生成或更新故事

## 执行流程

### Step 1: 收集上下文

按优先级读取：
1. `docs/PRODUCT_SOUL.md` — 理解用户画像和核心价值
2. `docs/PRODUCT_BEHAVIOR.md` — 提取用户流程和状态机
3. `docs/features/*.md` — 理解各功能的交互细节
4. 项目 CLAUDE.md — 获取 Debug Server 端口和可用端点

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

按 `docs/USER_STORIES_TEMPLATE.md` 格式生成每条故事。

**关键要求**：
- curl 命令用 `$PORT` 变量，不硬编码
- 断言要具体到字段级别
- 前置条件要明确（依赖前序故事 or seed 脚本 or 默认状态）
- 每步都有意图说明（不只是技术操作）

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
1. docs/user-stories/01-first-time-user.md — 首次使用：创建分组→随机选择
2. docs/user-stories/02-daily-selection.md — 日常使用：打开→选分组→摇
...

请审核后确认 commit，或提出修改意见。
```

## 约束

- **生成 ≠ 定稿**：AI 生成的故事是初稿，必须人工审核
- **不覆盖已有故事**：如果 `docs/user-stories/` 已有文件，只生成新增/缺失的
- **遵循模板格式**：严格按 `docs/USER_STORIES_TEMPLATE.md` 格式
- **端口动态获取**：从 CLAUDE.md 读取，curl 中用 `$PORT`

## Gotchas / 踩坑点

1. **不要猜端点名** — 如果 Debug Server 在运行就 curl /providers 获取真实端点；不在运行就从 CLAUDE.md 的命令示例中提取
2. **BEHAVIOR 的状态机 ≠ 用户故事** — 状态机是系统视角，故事是用户视角。要翻译，不要照抄
3. **断言不要太严格** — 留一定弹性（如"列表非空"而非"恰好 5 条"），避免频繁因数据量变化导致"过时"
