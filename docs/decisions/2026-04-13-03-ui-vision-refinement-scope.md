---
date: 2026-04-13
scope: core-skill
skill: ui-vision-check
related:
  - 2026-04-13-01-ui-vision-check-code-anchor.md
  - flutter/docs/decisions/ADR-007-engineering-constraints-over-docs.md
---

# 决策：ui-vision-check 的 AI 视觉打磨边界（Refinement Scope）

## 遇到的问题

在 flametree_rss_reader 项目 2026-04-13 的 `/ui-vision-check` + `/think` 讨论中，Founder 批准了"选项 A（全盘收敛路线）"的 4 步行动，但 `/think` 引入的独立 Gemini 视角明确警告：9 条 P1/P2 建议中有至少 4 条属于 **Filter C — 相对空间 & 色彩幻觉**，即 AI 基于截图给出的 `饱和度 -N%`、`padding +Npx`、`间距调整` 这类定量建议在 PNG 像素渲染 + P3/sRGB 色域差 + 抗锯齿的组合下**不可靠**，强行执行会导致：

1. **Death by Special Cases**：为单点视觉收益创建 if-else 硬编码分支，污染全局 Theme 一致性
2. **幻觉驱动的代码腐烂**：AI 看截图调 Token → 肉眼无法区分真实优化 vs 像素误差自圆其说
3. **纪律丢失**：每次截图都产出一堆定量建议 → 加剧"这轮的 N px 微调"重复消耗 Founder 精力

`ui-vision-check` skill 已有源码护栏（Step 2.5）阻止 🔴 Soul-breaking 幻觉，但对 🟡 Refinement 级别的"定量打磨"建议**没有拦截**。

## 讨论过程（要点）

**Gemini Filter C 的观察**：
- AI Vision 对像素级相对差异（间距 2px、饱和度 10%）的判断受截图渲染质量影响极大
- 真实的"相对视觉重量"判断依赖人眼的 HVS（Human Visual System）非线性响应，AI 的视觉 token 压缩后丢失了高频细节
- Refinement 不应该是定量微调，而是**隐喻/语义层**的违背识别

**Founder 在 flametree TODO 中的原始措辞**：
> 禁止区: AI 不得基于截图输出"间距 +Npx""饱和度 -N%""padding 调整为 N"等定量建议
>
> 允许区: 隐喻违背（冷灰 vs 暖色、硬线条 vs Organic Corners）、语义破碎（图标裁切、icon 家族混用）、语义过载（强调色在多种职责间复用）
>
> 引用 ADR-007 "工程约束 > 文档规范" 的同类理念

## 决策

在 `~/.claude/skills/ui-vision-check/SKILL.md` 的**约束**段新增硬规则 "**AI 视觉打磨边界（Refinement Scope）**"：

- 🚫 **禁止区**：间距 / 饱和度 / 字号 / 行高 的定量或相对调整，以及任何"视觉重量"驱动的像素级建议
- ✅ **允许区**：隐喻违背、语义破碎、语义过载、铁律违反、响应式 Bug
- **表达强制**：允许区内的建议必须用 **Token 语言**（`把 accent 换成 tertiary`），**不得**用定量描述（`饱和度 -20%`）
- **同类理念**：引用 flutter 项目 ADR-007 "工程约束 > 文档规范"——能编码进 Token/Lint/脚本的规则不依赖 AI 主观解读

## 为什么这么改

### 为什么选"边界 skill 内硬规则"而非"另起新 skill"
- Refinement 是 ui-vision-check 的核心输出之一，纪律应该内聚到 skill 本身；另起新 skill 会产生"AI 忘记加载辅助 skill"的执行漏洞
- skill 的"约束"段已经是 AI 执行时必读的硬规则位置，语义匹配

### 为什么选"禁止区/允许区二分"而非"只列禁止区"
- 只列禁止区 AI 容易在灰色地带（"这是不是像素级？"）自圆其说继续输出
- 禁止区 + 允许区的对称切分 + 表达强制（Token 语言）形成**形式约束**，AI 产出时必须落到明确语言形式，检验更容易

### 为什么引用 ADR-007 而非独立论证
- ADR-007 的核心理念"工程约束 > 文档规范"已经在 flutter 项目证明有效
- 引用而非复制避免规则漂移；未来 ADR-007 演进，Refinement Scope 同步获得理念更新

## 为什么不选其他方案

### ❌ 改 ui-vision-advance（定量审美评审 skill）
- ui-vision-advance 的定位就是"深度单页美学评审 + 精准设计规格"，输出定量建议是其价值所在
- 在那里加禁令会破坏 skill 的能力边界；Refinement 打磨边界属于 ui-vision-check 的日常健康检查职能

### ❌ 让 `/think` 运行时拦截
- `/think` 是后置过滤，只能在 Refinement 已产出后补救；而本规则要求 AI **在生成阶段**就遵守边界
- 依赖后置过滤 = 依赖 AI 记得调 `/think`，在紧凑执行链路上不可靠

### ❌ 只写到 flametree 项目的 TODO/ADR，不动全局 skill
- Refinement 定量幻觉是**所有项目**的 `/ui-vision-check` 共性问题，不是 flametree 特有
- 局部解决留下隐患：下个 Flutter/前端项目 Founder 又要撞一次同样的坑

## 验证方式

下次任一项目运行 `/ui-vision-check`，输出的 🟡 Refinement 表格应满足：
- 所有"改进方向"列只出现 Token 语言（`换 accent → tertiary`、`从渐变降到单色`）
- 不出现 `+Npx`、`-N%`、`饱和度调低`、`间距加大` 等定量表达

如出现违反，说明 AI 没有遵守本决策记录里写入的硬规则 —— 视为 skill 执行失败，报告应回炉。
