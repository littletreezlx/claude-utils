---
name: skill-creator
description: >
  This skill should be used when the user wants to create a new skill, improve
  an existing skill, or turn a workflow into a reusable skill. Use when the user
  says "create a skill", "make this a skill", "turn this into a skill", "新建技能",
  "做个 skill", "优化 skill", or when a repeated workflow pattern emerges that
  would benefit from being captured as a skill. Also use PROACTIVELY when the user
  describes a multi-step process they want Claude to remember and reuse.
version: 0.1.0
---

# Skill Creator — 技能创建与迭代优化

## 目的

帮助用户创建新 Skill 或改进现有 Skill。通过**意图捕获 → 编写 → 测试 → 迭代**的闭环，确保产出的 Skill 质量可靠、触发精准。

## 触发条件

当以下**任一**条件满足时启动：

1. 用户明确要求创建新 Skill
2. 用户要求将当前工作流/对话提炼为 Skill
3. 用户要求改进现有 Skill 的质量或触发精度
4. 对话中出现重复性工作流模式，适合封装为 Skill

## 执行流程

### Phase 1: 意图捕获

**目标**：明确 Skill 要做什么、何时触发、输出什么。

1. **从上下文提取**：如果对话中已有工作流（用户说"把这个做成 skill"），先从对话历史提取：
   - 使用了哪些工具、步骤顺序、用户做的修正、输入输出格式
2. **补充访谈**（按需向用户确认）：
   - 这个 Skill 让 Claude 做什么？
   - 什么场景应该触发？什么场景不应触发？
   - 期望的输出格式是什么？
   - 有没有边界情况需要处理？
3. **研究现有 Skill**：检查 `skills/` 目录，确认是否有重叠或可复用的部分

### Phase 2: 编写 SKILL.md

基于意图捕获的结果，按照项目 Skill 规范编写。

#### 文件结构

```
skills/<skill-name>/
├── SKILL.md                 # 必需：主文件
├── references/              # 可选：详细参考文档（>300 行时加目录）
└── scripts/                 # 可选：确定性/重复性任务脚本
```

#### SKILL.md 模板

```markdown
---
name: <skill-name>
description: >
  This skill should be used when [触发场景 1], [触发场景 2],
  when the user says "phrase 1", "phrase 2", "中文短语",
  or when [自动触发条件]. [一句话说明功能].
version: 0.1.0
---

# Skill 标题 — 中文副标题

## 目的
[一段话说明用途和角色定位]

## 触发条件
当以下**任一/全部**条件满足时启动：
1. [条件 1]
2. [条件 2]

## 执行流程
### Step 1: ...
### Step 2: ...

## 约束
- [限制项 1]
- [限制项 2]
```

#### 编写原则

| 原则 | 说明 |
|------|------|
| **description 用英文** | Claude 根据 description 做意图匹配，英文触发更精准 |
| **正文用中文 + 英文术语** | 方便阅读维护 |
| **触发短语要"积极"** | Claude 倾向于不触发 Skill，description 要稍微"推一下" |
| **解释 why，少用 MUST** | 说清楚原因比强制命令更有效 |
| **SKILL.md ≤ 100 行** | 超出部分放 `references/`，渐进式加载 |
| **祈使语气** | 指令用祈使句，简洁直接 |

#### description 编写要点

```yaml
# ✅ 好 — 具体触发短语 + 场景 + 功能说明
description: >
  This skill should be used when code changes have passed tests and are ready
  to commit, when a feature is complete, or when the user says "done", "commit".
  Handles conventional commit message generation.

# ❌ 坏 — 太模糊，没有触发短语
description: Provides git commit functionality.
```

### Phase 3: 测试验证

编写完 Skill 后，构造 2-3 个**真实用户会说的**测试 Prompt，验证 Skill 行为。

#### 测试 Prompt 要求

- 像真实用户一样自然表达，包含具体细节（文件路径、上下文、口语化表达）
- 覆盖不同措辞（正式/随意、中/英文混合）
- 包含边界情况

```
# ✅ 好的测试 Prompt
"我刚把用户认证的 JWT 逻辑改完了，测试也跑过了，帮我收尾一下"

# ❌ 坏的测试 Prompt
"请执行 delivery workflow"  # 太明显，不测试真实触发能力
```

#### 验证方法

1. 用测试 Prompt 模拟调用，检查 Skill 是否被正确触发
2. 检查执行结果是否符合预期
3. 确认不该触发的场景没有误触发

### Phase 4: 迭代改进

根据测试反馈，改进 Skill：

1. **泛化而非特化**：修改要适用于广泛场景，不要只针对测试用例过拟合
2. **精简无效指令**：如果某段指令没有实际影响输出，考虑移除
3. **提取公共模式**：多个测试中重复出现的 helper 脚本，提取到 `scripts/`
4. **重复迭代**：修改 → 重测 → 反馈 → 再改，直到用户满意

### Phase 5: 注册与集成

1. 更新 `skills/README.md` 的技能列表表格
2. 如果 Skill 需要被其他 Skill 调用（如 delivery-workflow 调用 git-workflow），在对应 Skill 中添加引用
3. 如果有对应的 Command（`/xxx`），在 README 中标注映射关系

## 约束

- **不制造意外**：Skill 内容不应超出 description 描述的范围
- **遵循项目规范**：与 `skills/README.md` 中定义的结构和风格保持一致
- **安全第一**：Skill 不得包含恶意代码、提权操作或数据泄露逻辑
- **用户确认**：创建完成后展示给用户确认，不自动注册到体系中
