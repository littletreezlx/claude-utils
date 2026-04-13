# think skill 契约式重写（去"防御性提示词叠加"）

- **Date**: 2026-04-13
- **Status**: Accepted
- **Scope**: skill:think (SKILL.md 355 行 → ~230 行)

## 1. 问题 (What went wrong)

产品负责人反馈 `skills/think/SKILL.md` "表述语言描述不是很通俗易懂"。审视下来是 4 类症状：

1. **版本回退注释混在正文里**——3 处 `v0.3 → v0.4 回退：~~字段~~` 块，读者得一边读现行规则一边脑补历史。
2. **术语假定读者自备定义**——Rubber Ducking、Critical-by-default、Anti Means-as-End、Locked Consensus、Attention 稀释。
3. **硬语气密度过高**——"禁止/严禁/必须/违反 skill"出现 20+ 次，反而稀释真正关键的几条。
4. **元评述插话**——「这条规则替代了早期版本中所有带 ⚠️ 的软提示」这类只有读过旧版才看懂的话。

## 2. 讨论过程 (How we thought about it)

Claude Code 先给出 A（温和瘦身）/ B（结构三段式）两方案，/think 调 Gemini 做外部视角复核。

Gemini 的核心诊断是"防御性提示词叠加（Defensive Prompt Layering）"：

- LLM Context Window 里注意力是零和游戏。把每个字段都标"必须/硬约束"等于"没有重点"，模型退化到预训练默认模式。
- 术语 "Rubber Ducking" 在预训练语料里主导含义是"小黄鸭调试法"，与本项目"仪式性咨询/自我麻痹"的用法不完全一致，引发 Semantic Drift——每次读取都要做一次 Contextual Binding，反而不是高密度信息载体。
- 版本回退块在 If-Then 规则链里等同于代码里被注释掉的旧逻辑，抢占 Attention 还可能引发幻觉提取（把删除的规则当补充约束）。
- 情绪化警告（"严禁/必须"）在强 LLM 上的边际效应递减，实际提升遵循度要靠**可机械校验的结构化输出契约**，而非修辞恐吓。

Gemini 明确拒绝 A（"无效的妥协，骨架依然是防御性补丁拼接"），B 方案保留但不够（散文化会削弱结构化锚点），推荐 **C：契约式重写**。

Claude Code 的 Failure_Premise 与 Gemini 诊断同向——术语和硬语气是症状不是病因，根因是"焦虑驱动的规则叠加"。

Founder 选 C-lite（C 的 1~4 条必做，第 5 条"Skill 编辑戒律"暂缓，先看契约化本身效果）。

## 3. 决策 (What we decided)

按 C-lite 执行：

1. **章节按工作流重组**：`用途 / 触发条件 / 与 think-gem-project 的关系 / Step 1-5 / Prompt 模板 / 组装原则 / 约束`。Step 1 是输入契约、Step 3 是输出契约、Step 4 是立场路由、Step 5 是自检。
2. **核心锚点升级为必选输出结构块**：Failure_Premise 和 Digest 从"自然语言要求"改为"Schema 字段"。Digest 定义为 5 字段固定结构，字段缺失或 Failure_Premise 字段非回显 = skill 违反（可机械检测）。
3. **版本回退块全部迁出**：所有 `v0.3 → v0.4 回退` 块从 SKILL.md 删除，历史保留在本 ADR。正文只留一句指针。
4. **硬语气密度降维**：把"严禁/必须"从 20+ 处缩减到 3-4 处真正关键的（Failure_Premise 回显、Escalate 路由、to-discuss.md 写入）。其余改写为可验证阻断条件（例："Digest 输出中 `[我写的 Failure_Premise]` 字段必须与 Prompt 里 Failure_Premise 字段字符串相等"）。
5. **术语白话化**：保留结构化字段名（Failure_Premise、Digest、Crux、Escalate——这些作为 Schema 锚点有价值），但自然段里的黑话翻译——Rubber Ducking → 仪式性咨询，Critical-by-default → 默认批判姿态，Anti Means-as-End → 手段≠目的，Attention 稀释 → 注意力稀释（保留中文化）。

## 4. 为什么不选其他方案

- **A（温和瘦身）**：只做抽脂不换骨架。Gemini 和 Claude 都判断 3 个月后新的 v0.5/v0.6 回退块会原样长回来。
- **B（结构三段式但保留散文）**：改了章节顺序但没改"靠形容词恐吓"的底层模式，Failure_Premise/Digest 这些反仪式性咨询锚点可能在散文化过程中被削弱。
- **C-full（含第 5 条编辑戒律："加约束必须能表达为 I/O Schema 字段变更否则拒绝合并"）**：治本更彻底，但在未验证契约化本身效果前就加元规则，风险是过早固化。先看 C-lite 跑 1~2 个月再评估是否升级到 C-full。
- **Reject（维持现状）**：产品负责人吐槽已明确，且 Gemini 指出"防御性叠加"会持续恶化，不做等于默许膨胀。

## 5. 保留的"v0.3 → v0.4 回退"历史（从 SKILL.md 迁入）

### 已删除的硬信号（自动触发条件）

- ~~方案浮现 ≥2 候选~~ — 实战未验证 Claude 会自发识别"候选方案"这种隐式状态。
- ~~UI 视觉偏差 1 轮定位失败~~ — 实战未验证。

两条累积 3+ 次真实场景后若仍判断有价值，再加回。不在数据到位前预置规则。

### 已删除的 Context 审计字段

- ~~话题性质分类~~
- ~~为何不读其他文档~~

实战里话题经常跨 product + architecture + roadmap 多类，"恰好一个"的约束变成走过场。当前 2 项（CWD + 已读文档）是最小可审计集。

**物理路径启发式方案（按 `lib/features/` vs `lib/core/` 自动选文档）**也被放弃——调研显示各 flutter 项目目录结构不一致，硬编码会水土不服。

### 已删除的 Digest 分支

- ~~Accept-with-caveats~~ — 实战中 Claude 遇到"主干认同 + 细节保留"时更自然用"Escalate + 独立 TODO 组合"表达，四分支的第二项被绕过。简化为三分支（Accept/Refute/Escalate）减少心智负担。

### 已删除的前置审计字段回显

- ~~Context Checklist 回显~~ — Context Checklist 本身已写在 Prompt 的 Context 段开头，可通过输出结构验证。
- ~~Crux 回显~~ — 如果 Failure_Premise 回显了就已经说明 Claude 完成了前置思考，不需要重复证据。

只保留 **Failure_Premise 回显** 作为 Digest 的前置审计锚——它是最难伪造、最能检测仪式性咨询的唯一字段。

### 已删除的"⚠️ 软提示"

早期版本用 `⚠️ 建议 Escalate` 这类软提示表达"影响较大时倾向升级"。在 AI-Only 模式下，带表情符号的软提示等同于注释（被 Claude 忽略）。改为 3.3 Escalate 强制路由（4 条命中条件任一触发即必须 Escalate），无弹性、无解释空间。

## 6. 验证凭证

[验证凭证: N/A - 本次为规则文档重写，无运行时状态。有效性验证需在后续 1~2 个月实战中观察：(1) SKILL.md 行数是否再次膨胀；(2) Digest 的 Failure_Premise 回显字段是否被 Claude 跳过；(3) 产品负责人再次阅读的主观可读性。]
