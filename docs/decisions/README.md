# 决策记录 (Decision Log)

本目录存放对 `~/.claude/CLAUDE.md`、核心 skill、跨项目工作流的**讨论和修改**的持久化记录。

## 为什么要有这个目录

AI-Only 开发模式下，全局规则是唯一的行为约束源。规则的每次修改都会影响所有未来会话——如果只改规则不留下"为什么这么改"的记录，几个月后 AI（包括人类）再看到规则时会：

1. 不知道规则在防哪种具体的 bug → 容易在边缘情况下自己说服自己绕开
2. 忘了当初评估过并否决的替代方案 → 重复讨论已经做过的决策
3. 规则彼此冲突时无法回溯立法意图 → 无从判断哪条让步

决策记录就是规则的"立法过程"——不是 changelog（那个 git log 已经有了），是**立法意图和替代方案的保存**。

## 什么时候必须写记录

由 `CLAUDE.md` 铁律 8 强制：任何对以下对象的**讨论和修改**都必须同步产出一份记录：

- 全局 `~/.claude/CLAUDE.md`
- 核心 skill（`~/.claude/skills/` 下被其他流程依赖的 skill）
- 跨项目工作流（影响 ≥2 个项目的共享模式、命令、防御策略）

修改和记录必须在**同一次**交付里完成。只改规则不写记录 = 未完成，Founder 有权 rollback。

**豁免**：纯粹的打字错误、格式清理、文档链接修复不需要写记录——这类修改无立法意图可言。

## 文件命名规则

```
YYYY-MM-DD-短标题-kebab-case.md
```

例：
- `2026-04-12-evidence-based-completion.md`
- `2026-04-12-decision-log-requirement.md`

同一天多份记录用 `-01` / `-02` 前缀区分 kebab 段之前：

```
2026-04-12-01-foo.md
2026-04-12-02-bar.md
```

## 记录模板

每份决策记录必须包含以下段落，顺序固定：

```markdown
# {标题}

- **Date**: YYYY-MM-DD
- **Status**: Accepted | Superseded by <file> | Reverted
- **Scope**: ~/.claude/CLAUDE.md § {章节} / skill:{name} / workflow:{name}

## 1. 问题 (What went wrong)

具体触发这次讨论的事实场景。禁止抽象——必须是一个可复现的 bug、一次具体的失败、或一个被观察到的行为漂移。

## 2. 讨论过程 (How we thought about it)

按时间顺序记录关键转折：
- 谁提了什么初步方案
- 哪次咨询（/think、feat-discuss）带来了什么反驳
- 哪个事实纠正改变了诊断
- 最终为什么收敛到这里

## 3. 决策 (What we decided)

最终写入规则文件的具体内容。如果是 CLAUDE.md 修改，粘贴前后 diff 或新增段落原文。

## 4. 放弃的替代方案 (What we rejected and why)

列出至少 1 个认真考虑过但否决的方案，以及否决的具体理由。这条是防止未来 AI 重新提出同样的方案浪费一轮讨论。

## 5. 预期影响 & 监控 (How we will know it works)

- 这条规则会改变什么 AI 行为？
- 如何判断它有效/失效？
- 多久之后回访评估？
```

## 与 memory 系统的区别

- **memory** (`~/.claude/projects/.../memory/`): 跨会话的事实/偏好/用户画像。**短、索引化、面向快速召回**。
- **decisions** (本目录): 规则变更的立法过程。**长、叙事化、面向回溯理解**。

同一个决策可能同时产生一个 memory 条目（如"用户确认偏好方案 X"）和一份 decision 记录（详细过程）。memory 指向 decision 文件作为详细出处即可，不要重复正文。
