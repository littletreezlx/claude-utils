---
name: ui-design-router
description: >
  This skill should be used when the user expresses intent to change UI, visual
  design, or layout — phrases like "改一下 X 页", "调整 UI", "换个感觉", "补 empty
  态", "加个按钮", "这里不好看", "redesign X", "tweak the styling". Routes the
  change: small (single file bug / copy / existing component usage / pixel-perfect
  recreate of an archived bundle) gets implemented directly; large (≥3 pages /
  touches Invariants / introduces new visual pattern) is gated to the Claude
  Design loop by generating a Δ Brief at docs/design/DESIGN_BRIEF.md. Blocks
  when EXTERNAL_REFS is missing and recommends /ui-bootstrap first.
version: 0.1.0
---

# UI Design Router — 改 UI 前的路由闸门

## 目的

用户说"改 X 页的 Y"时,自动介入并**分类**:小改动直接做,大改动拦下来走 Claude Design 闭环。目标是让 Founder **不用记住 Design-First Gate 规则**,也不会因为忘记走闭环导致设计体系漂移。

## 触发条件

**必须触发**(任一信号出现):
- 用户说"改 X 页"、"调整 UI"、"换个感觉"、"补 X 态"(empty/error/loading)、"重新设计 X"、"加个 X 按钮"、"X 不好看"、"redesign"、"tweak styling"
- 用户贴截图并抱怨视觉/布局
- 用户说"想让 X 看起来像 Y"
- 检测到对话即将涉及跨页面的视觉改动(对方提到"整体"、"所有页面的 Z")

**不触发**:
- 纯逻辑/状态/数据改动,无视觉影响
- 本会话已经触发过一次且已路由完成(本轮结论还有效)
- 用户正在基于一个已归档 bundle 做 pixel-perfect recreate(属于豁免)

## 执行流程

### Step 1: 前置守门

读 `docs/design/EXTERNAL_REFS.md`:
- **不存在 / 未绑定 Claude Design** → 停:
  > "检测到项目未接入 Claude Design 闭环。改 UI 前先跑 `/ui-bootstrap` 建立绑定。"
- **存在** → 继续

读 `docs/ui/UI_SHOWCASE.md`,确认三段式(Vibe / Invariants / Interaction)齐全 → 否则提示先跑 `/ui-bootstrap` 或 `/init-ui-showcase`。

### Step 2: 分类(小改 vs 大改)

对照**豁免白名单**(小改,直接做)- 满足任一即豁免:

- 单文件 bug 修复(不涉及视觉语言)
- 既有组件的**用法**调整(不改定义,如换个已登记色值、调既有组件的 prop)
- 字符串 / 文案修改(不涉及排版)
- **pixel-perfect recreate**:本次就是落地已采纳的设计(用户能指出 `docs/design/generated/{ts}/project/` 路径)
- 响应式微调(单页面内 padding / 边距微调,未触碰档位)

对照**触发阈值**(大改,走闭环)- 满足任一即触发:

- 改动涉及 **≥ 3 个页面**的视觉
- 触及 **Invariants**:OKLCH 色板 / 字阶档位 / 间距档位 / 圆角档位 / 阴影体系
- 引入**新视觉模式**(原体系没有的卡片样式 / 导航形态 / 状态呈现)
- 用户明说"想整体换个感觉"、"重新设计"、"改一下风格"

**模糊地带**直接问用户,不猜。

### Step 3a: 小改路径

告诉用户分类结果和理由,**然后直接实施**:

```text
🟢 分类:小改动(理由:既有 `Button` 组件的 variant 切换,未触 Invariants)
→ 直接实施,不走 Claude Design 闭环
```

实施完后,`feat-done` skill 会在提交前再检查一次"是否需要 bundle"(但豁免路径不要求 bundle)。

### Step 3b: 大改路径 — 生成 Δ Brief

**不要用户跑命令**,直接做:

1. **读入上下文**:
   - `docs/PRODUCT_SOUL.md`
   - `docs/ui/UI_SHOWCASE.md`(Vibe + Invariants + Interaction)
   - `docs/design/EXTERNAL_REFS.md`(Claude Design 绑定)
   - 最近一份 `docs/design/generated/{ts}/README.md`(上轮采纳什么)
2. **提取用户本轮意图**(改什么 / 补什么 / 突破什么)— 不清楚就问一句
3. **写 Δ Brief 到 `docs/design/DESIGN_BRIEF.md`**(覆写,历史在 git log)
4. **同步到终端输出**,方便用户复制到 Claude Design 对话

### Δ Brief 模板(强制)

文件头溯源块 + 结构详见 `references/brief-template.md`。核心原则:

- **只写 delta,不重述设计系统** — Claude Design onboarding 时已读过 codebase,它知道整个系统
- **不超过一屏**(约 60 行)— 超了就是在重述
- **负向约束比正向引导更强** — 优先写"本轮禁止"
- 必含段落:本轮重点 / 本轮要突破(可选) / 本轮硬约束(可选) / 本轮禁止(可选) / References(可选) / 功能流与字段(可选,仅新增)

### Step 4: 告诉用户下一步

```text
🔴 分类:大改动(理由:___)
→ 已生成 Δ Brief 到 `docs/design/DESIGN_BRIEF.md`(内容已输出到对话)
→ 下一步:
  1. 复制 Brief 到 Claude Design 对话(claude.ai/design)
  2. 在 Claude Design 里迭代
  3. 满意后 export bundle
  4. 跑 `/ui-vs` 评审源码
  5. 采纳则 `/ui-adopt` 反哺 + 归档
  6. 本地 pixel-perfect recreate(再次触发本 skill,走豁免路径)
```

## 用户覆盖

分类不对时,用户一句话即可覆盖:

- "不,这是大改动" → 强制走 Brief 生成
- "这次先直接改,我知道是大改" → 放行但**必须警告**:"跳过闭环会让设计体系漂移,`feat-done` 提交时仍会拦查 bundle。确认?"
- "这属于 pixel-perfect recreate,bundle 在 `docs/design/generated/2026-04-20-warm-ceramic/project/`" → 豁免,放行

## 约束

- **禁止自动跑 `/ui-bootstrap`**:接入是破坏性动作,必须用户主动触发
- **禁止把 Brief 写成完整设计描述**:AI 最容易犯的错是把 UI_SHOWCASE 拷过来。只写 delta
- **禁止写到根目录或 `_scratch/`**:Brief 的正确位置是 `docs/design/DESIGN_BRIEF.md`
- **禁止在同一会话内反复触发**:本轮已路由过,后续 UI 讨论沿用结论直到用户明示新一轮
- **模糊不猜**:阈值判断不清时,问用户"这次想改的范围大概是单页面内调整还是跨页面的体系级变化?"
