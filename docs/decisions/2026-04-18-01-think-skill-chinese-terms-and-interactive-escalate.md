# 2026-04-18-01 /think skill 术语中文化 + 交互模式绕过 to-discuss.md

**类型**：Skill 契约修改
**影响半径**：全局 `~/.claude/skills/think/SKILL.md` + `~/.claude/guides/doc-structure.md`
**版本**：think 0.3.0 → 0.4.0

## 问题

Founder 在复盘两次 `/think` 实际输出时指出 3 个问题：

### 问题 1：Digest 非自包含

两次 Digest 都大量引用 `R1-R7 / BUG-1~4` 这类外部编号但不重述含义，读者必须翻回 Gemini 原文才能对照。典型反例：

```
[Gemini 核心主张]: BUG-1 证据链不完整，需触发真实 AI 调用才能断言是 App bug 还是
Debug Server 局限；R1/R3/R4 ACCEPT，R5 REJECT (批量已读违背"隐形容器/AI 不越权"哲学)，
R6/R7 REJECT (过度优化)，R2 BLOCKED 等验证。
```

"核心主张"字段被塞成事项清单，失去"一句话整体判断"的摘要功能。

### 问题 2：`Failure_Premise` 语义不清

字面"失败前提"在中英文里都不是标准术语——标准术语是 *premortem*（事前验尸）。即便读过 skill 定义，字段名仍与其含义存在认知距离。

### 问题 3：交互对话中强制落库 `to-discuss.md` 冗余

0.3.0 版本的 Escalate 路由无差别要求"写入项目根 `to-discuss.md`，然后停下等 Founder 拍板"。但 `to-discuss.md` 的设计定位是**异步决策队列**——Claude 自主运行时无法即时请示 Founder 才需落库等下次会话。

而 Founder 触发 `/think` 通常在**交互式对话中**，人就在现场。这种情况下绕道写文件让用户下次翻队列，不如直接在对话里渲染决策模板让用户当场勾选——快得多。

## 讨论过程

Founder 在一次 `/think` 实际输出后提出上述 3 点质疑，Claude Code（本次会话）同意全部 3 点：

- 问题 1 根因是 Digest 缺自包含规则，不是"浓缩过度"
- 问题 2 确认 `Failure_Premise` 即便在英文里也非标准术语
- 问题 3 承认交互/自主会话需要区分处理

## 决定

### 1. 术语中文化

| 原术语 | 新术语 | 出现位置 |
|--------|--------|----------|
| `Failure_Premise` | `事前验尸` | Prompt 首轮模板字段名；Digest `[我的事前验尸]` |
| `Accept / Refute / Escalate` | `采信 / 反驳 / 升级` | Digest `[我的立场]`；3 个立场表格 |
| `Approve / Discuss / Reject` | `采纳 / 再议 / 驳回` | 3.4 升级模板决策选项；`doc-structure.md` to-discuss 模板 |

### 2. Digest 自包含规则（新增）

Digest 必须能脱离 Gemini 原文独立读懂：

- 引用 `R1/BUG-3/Issue-N` 等外部编号时，同字段内用一句话注释（"R5 = 批量已读功能"）
- `[Gemini 核心主张]` 限定一句话整体摘要，**禁止列事项清单**——具体决策分流进 `[下一步行动]`

### 3. 升级路由按会话类型分叉（3.3.2 新增）

| 会话类型 | 判据 | 升级动作 |
|---------|------|---------|
| 交互模式 | 当前有用户 prompt 等待回复 | **直接在对话里展示 3.4 模板**，让用户当场勾选。只有用户明确"先挂起"或无法当场决定时才落库 |
| 自主模式 | `/loop`、cron、batch 自主执行 | 写入项目根 `to-discuss.md`（原流程） |

默认判据：不确定时按交互模式处理。

## 为什么不选其他方案

### 方案 X1：完全移除 to-discuss.md 落库步骤

**否决原因**：自主模式（`/loop`、cron）下 Claude 确实无法请示 Founder，必须有落库通道——否则决策会被吃掉。

### 方案 X2：保留英文术语，只改 Digest 自包含规则

**否决原因**：Founder 明确点出术语造成认知摩擦。且 `Failure_Premise` 在英文里也非标准（应为 *premortem*），改成中文"事前验尸"反而语义更准确。

### 方案 X3：用"按 CLI 入口类型"判断（manual `/think` vs. auto-triggered）

**否决原因**：真正决定"是否落库"的不是触发来源，而是**有没有用户在现场**。手动 `/think` 在 `/loop` 里同样应该落库；auto-triggered `/think` 在对话里同样应该对话展示。按"会话类型"判据更准确。

## 验证凭证

- [验证凭证: N/A - 本次仅修改 skill 规则文档与 guides，无运行时状态可验证。后续 Founder 任意次 /think 调用即产生自然验证。]

## 后续

- 下次 `/think` 调用时，Claude Code 必须：
  - Prompt 中用 `## 事前验尸` 而非 `## Failure_Premise`
  - Digest `[我的立场]` 填中文三选一
  - 升级时默认在对话里展示 3.4 模板，不写 `to-discuss.md`
- 如果连续 3 次 Founder 仍反馈 Digest 不清晰或术语别扭，再开一份决策记录重新考量
