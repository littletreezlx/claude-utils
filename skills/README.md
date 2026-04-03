# Skills 技能库

自动触发的领域知识包，让 Claude Code 更智能化。

---

## 什么是 Skill？

Skill 是 Claude Code 的**自动触发知识包**。与 Command（用户手动 `/xxx` 触发）不同，Skill 通过 description 中的触发短语让 Claude 自主判断何时调用。

### Command vs Skill

| 维度 | Command | Skill |
|------|---------|-------|
| 触发方式 | 用户手动 `/command-name` | Claude 根据意图自动匹配 |
| 结构 | 单个 `.md` 文件 | 目录：`SKILL.md` + 可选的 `references/`、`scripts/` |
| 适用场景 | 明确的操作指令 | 领域知识、自动化工作流 |
| 加载机制 | 调用时全量加载 | 三级渐进加载（metadata → body → references） |

---

## 当前技能列表

| Skill | 自动触发场景 | 对应 Command |
|-------|-------------|--------------|
| `git-workflow` | 代码改完、测试通过、表达"完成"意图 | feat-done Step 3 调用 |
| `test-workflow` | 代码修改后需验证、测试失败时 | `/test-run`（thin wrapper） |
| `consistency-check` | 开始新功能、首次进入项目 | — (自动触发) |
| `code-quality` | 提交前质量关卡、准备 merge | — (自动触发) |
| `think` | 方法论/策略/哲学讨论 | — (自动触发) |
| `feat-discuss-local-gemini` | 讨论新功能、咨询 Gemini 产品/设计意见 | `/feat-discuss-local-gemini` |
| `ui-vision-check` | UI 视觉验证（单页/全局审计）、用户说"视觉检查"/"UI 审计" | — (纯分析，无对应 Command) |
| `ui-vision-advance` | 深度审美评审（五维评审+反 AI 味检测+设计简报）、用户说"审美评审"/"design critique" | `/ui-vision-advance` |
| `ui-doctor` | UI 文档健康探针、Spec 覆盖率和腐烂度检测 | — (自动触发) |
| `ui-spec` | UI 代码变更后 Spec 文档更新 | — (自动触发) |
| `ui-redesign` | 视觉重塑、生成设计方案+Flutter 实现指南 | — (用户主动触发) |
| `screen` | 截屏（Flutter 模拟器/adb/网页），为 UI 工作流提供视觉上下文 | `/screen` (已迁移) |
| `skill-creator` | 创建新 Skill、改进现有 Skill、提炼工作流为 Skill | — (元技能，无对应 Command) |
| `prompt-craft` | 编写/审查/优化项目中的 AI-facing prompt（system prompt、API 调用指令） | — (自动触发) |
| `ai-cli-design` | 编写/优化 CLI 工具或 Python 脚本时，确保对 AI Agent 友好 | — (自动触发) |
| `update-from-stitch` | 从 Stitch 拉取设计稿到本地，对比差异并更新代码 | `/update-from-stitch` |
| `ai-qa-stories` | AI 自主闭环：按 user-stories 文档验证 App（回归测试） | `/ai-qa-stories` |
| `ai-explore` | AI 自主闭环：启发式探索 App 发现未知问题（自动先跑 stories） | `/ai-explore` |
| `generate-stories` | 从现有文档生成 user-stories 初稿（需人工审核） | `/generate-stories` |
| `init-debug-server` | 为 Flutter 项目搭建 Debug State Server 基建 | `/init-debug-server` |

---

## 目录结构

```
skills/
├── README.md                    # 本文件
├── <skill-name>/
│   ├── SKILL.md                 # 必需：主文件
│   ├── references/              # 可选：详细参考文档
│   └── scripts/                 # 可选：辅助脚本
```

---

## 编写指南

### SKILL.md 结构

```markdown
---
name: skill-name
description: >
  This skill should be used when [具体触发场景 1], [具体触发场景 2],
  [具体触发场景 3]. [一句话说明这个 skill 做什么].
version: 0.1.0
---

# Skill 名称

## 目的
[一段话说明这个 skill 的用途]

## 触发条件
[列出自动触发的条件，Claude 会根据这些判断是否调用]

## 执行流程
[具体执行步骤或策略]

## 约束
[限制和禁止项]
```

### 关键规范

#### 1. description 必须用英文 + 具体触发短语

Claude 根据 description 做意图匹配，英文触发更精准。格式：

```yaml
description: >
  This skill should be used when the user asks to "phrase 1", "phrase 2",
  or when [具体场景]. [一句话说明功能].
```

**好例子**：
```yaml
description: >
  This skill should be used when code changes have passed tests and are ready
  to commit, when a feature is complete, or when the user says "done", "commit".
```

**坏例子**：
```yaml
description: Provides git commit functionality.  # 太模糊，没有触发短语
```

#### 2. 正文用中文 + 英文术语

方便阅读和维护，但关键术语保留英文。

#### 3. 触发条件要明确

写清楚什么情况下**应该触发**，什么情况下**不应该触发**。

#### 4. 保持精简

SKILL.md 控制在 100 行以内。详细内容放到 `references/` 目录。

---

## 设计原则

### 1. Command → Skill 迁移策略

当一个 Command 被转化为 Skill 后：
- **可以直接移除对应的 Command 文件**，不需要同时保留两者
- 用户不会主动 `/xxx` 调用的命令，更适合转为 Skill（由 Claude 自动触发）
- 迁移后，Skill 成为该功能的**唯一入口**，避免维护两份逻辑

**判断是否应迁移**：
- ✅ 用户几乎不会主动调用，Claude 自动判断更高效 → 迁移为 Skill，移除 Command
- ✅ 有明确触发条件、可以自动判断的 → 适合 Skill
- ❌ 用户经常主动调用、需要传参数的 → 保持 Command
- ❌ 需要用户决策、破坏性操作的 → 保持 Command
- ⚠️ 两者都有使用场景 → 可并存，但注意保持逻辑一致

### 2. 自动化边界

不是所有 Command 都适合转成 Skill：
- ✅ 有明确触发条件、可以自动判断的 → 适合 Skill
- ❌ 需要用户决策、破坏性操作的 → 保持 Command

### 3. 渐进式披露

Skill 支持三级加载：
1. **Metadata**（name + description）：始终在上下文中
2. **SKILL.md body**：触发时加载
3. **references/**：需要时才加载

利用这个机制，把核心内容放 body，详细文档放 references。

### 4. 复合 Skill 设计模式

当 Skill 需要编排多个子步骤或调用其他 Skill 时，遵循以下原则：

| 原则 | 说明 | 示例 |
|------|------|------|
| **文件路径传递** | Subagent 之间只传文件路径，不传内容。保持上下文窗口干净 | `writer-agent` 接收 `outline.md` 路径而非内容 |
| **混合架构** | 确定性逻辑用脚本（`scripts/`），判断性逻辑用 Agent | 格式化用脚本，润色用 Agent |
| **中间产物持久化** | 每步产出保存为文件，支持断点续传和人工干预 | `source.md → analysis.md → draft.md → final.md` |

> 灵感来源：[Agent + Skills 五步框架](https://x.com/pippingg) —— 用自然语言编排工作流

---

## 质量标杆

参考当前 skills 目录下的示例：
- `git-workflow/SKILL.md` — 简洁的自动触发流程
- `think/SKILL.md` — 轻量级 Gemini 协作
- `consistency-check/SKILL.md` — 明确的触发条件列表

---

## 调试技巧

### Skill 没有自动触发？

1. 检查 description 中的触发短语是否覆盖了你的表达方式
2. 确保触发条件写得足够具体
3. 在对话中明确表达意图（如说"commit"而不是只说"好了"）

### Skill 触发太频繁？

1. 在触发条件中增加**前置条件**（如"测试通过后"）
2. 用更具体的短语替代泛泛的描述
