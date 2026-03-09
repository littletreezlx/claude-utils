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
| `git-workflow` | 代码改完、测试通过、表达"完成"意图 | `/git-commit` |
| `test-workflow` | 代码修改后需验证、测试失败时 | `/test-run` |
| `delivery-workflow` | 完整功能开发结束，进入收尾 | `/feat-done` |
| `consistency-check` | 开始新功能、首次进入项目 | `/codebase-align` |
| `code-quality` | 提交前质量关卡、准备 merge | `/code-review` |
| `feat-discuss-local-gemini` | 讨论新功能、咨询 Gemini 产品/设计意见 | `/feat-discuss-local-gemini` |
| `ui-vision-check` | UI 视觉验证（单页/全局审计）、用户说"视觉检查"/"UI 审计" | — (纯分析，无对应 Command) |
| `ui-doctor` | UI 文档健康探针、Spec 覆盖率和腐烂度检测 | — (自动触发) |
| `ui-spec` | UI 代码变更后 Spec 文档更新 | — (自动触发) |
| `ui-redesign` | 视觉重塑、生成设计方案+Flutter 实现指南 | — (用户主动触发) |
| `skill-creator` | 创建新 Skill、改进现有 Skill、提炼工作流为 Skill | — (元技能，无对应 Command) |

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

---

## 质量标杆

参考当前 skills 目录下的示例：
- `git-workflow/SKILL.md` — 简洁的自动触发流程
- `delivery-workflow/SKILL.md` — 多阶段流水线
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
