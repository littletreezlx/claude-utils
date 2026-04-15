# 命令编写指南

本文件指导如何编写和优化 `commands/*.md` 斜杠命令。

> 命令索引和使用说明见 `@README.md`

---

## 设计原则

- **意图优先**：定义"做什么"和"为什么"，AI 自行决定"怎么做"
- **一类问题一个命令**：按用户视角的"一件事"划分，而非按技术操作划分
- **务实简洁**：文件控制在 150 行以内，简单够用 > 完美复杂
- **复用优先**：引用已有命令或 `@templates/`，不重复造轮子

---

## 命令形态

不同复杂度的命令适用不同写法：

### 原子型（单一目标，直接执行）

代表：`git-commit`, `claudemd`, `screen`

```markdown
# [Command Name]
## 目标
[一句话]
## 执行策略
[指导性方针，非具体 CLI 步骤]
## 约束条件
[限制和禁止项]
```

### 流程型（多阶段，可能含用户交互断点）

代表：`feat-discuss`, `feat-done`, `code-review`

```markdown
# [Command Name]
## 角色定位
[一句话定义在这个流程中扮演的角色]
## 核心工作流
### Phase/Step 1: [阶段名]
[该阶段的目标和策略]
### Phase/Step 2: [阶段名]
[该阶段的目标和策略]
## 约束条件
```

**流程型的判断标准**：
- 一个完整工作流中的多个阶段，用户期望一次调用走完
- 阶段之间有自然的交互断点（如等待外部输入）也可以，在命令中说明即可
- 阶段描述应是**目标和策略**，而非具体 CLI 操作

### DAG 型（生成任务文件，无人值守执行）

代表：`refactor-project`, `test-plan`, `todo-huge-task`, `doc-quality-review`

DAG 命令的产出是**任务文件**（非报告），通过 `batchcc` 自动化执行。
编写规范参见 `@templates/workflow/DAG_FORMAT.md`（DAG 统一规范）。

**DAG 命令必须满足下方"DAG 命令强制清单"。**

### 工具型（辅助操作，格式驱动）

代表：`todo-write`, `create-page-doc`

核心是定义**输出格式**，AI 按格式填充内容。输出格式定义可以内嵌在命令中。

---

## 编写规则

### 必须

- Frontmatter 包含 `description`（简短说明，显示在命令列表中）
- 开头明确命令的**核心目标**
- 约束条件中包含**禁止的操作**
- DAG 型命令引用 `@templates/workflow/` 而非内嵌格式说明

### 避免

- **微操指令**：不要写 `git status` → `cat file` → `grep xxx` 这样的 CLI 步骤序列
- **大段内嵌模板**：超过 10 行的模板应外置到 `templates/`（输出格式定义除外）
- **sleep 命令**：严禁使用
- **无用重复**：如果已有命令/skill 覆盖了某个能力，引用它而非重写

### 判断灰区

| 场景 | 建议 |
|------|------|
| 命令需要 Step 1/2/3？ | 流程型允许，但每步写目标而非操作 |
| 需要内嵌代码示例？ | 短示例（< 10 行）OK，长的外置到 templates |
| 一个命令做了 3 件事？ | 如果用户视角是"一件事"就 OK，按技术操作拆才需要分离 |
| 命令之间有重叠？ | 检查是否可以在一方引用另一方，而非各自实现 |

---

## 目录结构

```
commands/
├── CLAUDE.md              # 本文件（编写指南）
├── README.md              # 命令索引（面向用户）
├── *.md                   # 可执行命令
└── templates/
    ├── docs/              # 文档模板
    └── workflow/           # DAG 格式规范和示例
```

---

## Command → Skill 迁移

当一个 Command 被转化为 Skill 后，**对应的 Command 文件可以直接移除**，无需同时保留。

**适合迁移的 Command**：
- 用户几乎不会主动 `/xxx` 调用的（如 `git-commit` → `git-workflow` skill）
- Claude 自动触发比手动调用更自然的（如 `code-review` → `code-quality` skill）

**不适合迁移的 Command**：
- 用户经常主动调用、需要传参数的（如 `/refactor`, `/ui-spec`）
- DAG 型命令（需要明确启动）
- 破坏性/重型操作（需要用户主动决策）

迁移后，Skill 成为该功能的唯一入口，参见 `~/.claude/skills/README.md`。

---

## DAG 命令强制清单

DAG 型命令必须同时满足以下 4 条。源自 `doc-quality-review` 第一次实战的失败教训（决策记录：`docs/decisions/2026-04-15-01-doc-quality-review-trunk-centric.md`）。

### 1. 显式两步走 + 禁止主会话起 background agent

命令开头必须写明：

```bash
/xxx-command          # 第一步：只生成 DAG 任务文件，不执行
batchcc task-xxx      # 第二步：独立会话执行
```

并显式禁止"在当前会话内用 Task tool 起 background agent 并发执行 DAG TASK"。后果：
- 子 agent 产出会通过 system-reminder 回填主会话 → 主 context 仍会爆
- 多 agent 同时冲 API 触发 529 超载
- 丢失 batchcc 的独立会话隔离和断点续传

### 2. 激进执行约束（防保守派默认）

笼统的"机械执行"会被 AI 解读为"只做最安全的"，大量工作被悄悄塞进 TODO。每个执行节点必须显式列出：

- **必做清单**：哪些处方/动作必须自动执行（如归档/删除/迁移/路径修正/字段补全）
- **例外清单**：什么情况才允许转 TODO（如跨文档语义冲突、需源码验证、产品方向决策）
- **禁用借口**：显式禁止"工作量大""涉及多文件""需要小心"等软借口
- **禁止自创分级**：AI 会自创 P0/P1 把 P1 当延迟借口

### 3. 静默失败拦截器（守门员）

读多文件做诊断/汇总的命令必须加可量化的 Fatal Error 拦截（文件数 > N / token 估算超限 / 批次数超阈值），宁可罢工不静默截断。同时显式禁止 `--force` 绕过。

### 4. State 文件位置避开 `.claude/`

持久化的运行时缓存/state 应放在与服务对象就近的位置（如 `docs/`、项目根或 `.git/info/`），避免 `.claude/` 的权限围栏在自动化模式下每次写都触发审批。

### 元原则

**Skill/command 在 AI-Only 项目里是可执行约束，留白处必被保守派默认占据。** "机械执行"不是约束，"列出 8 类必做 + 3 类例外 + 5 条禁用借口"才是。

---

## 质量标杆

| 标杆 | 模式 | 学什么 |
|------|------|--------|
| `refactor.md` / `git-commit.md` / `claudemd.md` | 原子型 | 单一目标的简洁性 |
| `refactor-project.md` | DAG 型 | 多 stage 的并行/串行编排 |
| `doc-quality-review.md` | DAG + 全自动激进执行 | 必做清单 + 例外清单 + 禁用借口的写法（强制清单 §2）|
| `skills/log-audit/SKILL.md` | 用户介入式激进执行 | Action menu 显式选项 + 默认 diagnosis-only + Anti-ritual 自检 + Volume control 60s 拦截 |