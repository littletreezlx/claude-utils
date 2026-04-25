---
name: Warm Ceramic 全局解耦决策
description: 全局 skill/command 的"暖陶瓷硬绑定"已降级为 FlameTree 默认母语示例,项目通过 UI_SHOWCASE §Anti-default note 强制声明反例
type: project
originSessionId: 3c06a436-8871-48d8-bcd3-ad2cbd2faeb5
---
**事实**:2026-04-25 完成全局 Warm Ceramic 硬绑定解耦。

**Why**:全局 4 个 skill/command 把 Warm Ceramic 当成所有项目的默认裁决器,导致 music/pick/rss_reader 深度照抄(pick 类名直接叫 `WarmCeramicTokens`),非暖调项目会被系统性误判。Founder flametree 品牌确实偏温暖,但"温暖"是合法默认 prior,不是强制标尺。Gemini + GPT 双模型对抗后选了 GPT 方案"反例驱动 + 默认母语" — 决策记录 `~/.claude/docs/decisions/2026-04-25-07-warm-ceramic-unbind.md`(文件名沿用了讨论日期 04-24 的编号 07,实际改动落在 04-25)。

**How to apply**:

1. 任何 skill/command 评审 UI 前必须先读项目 `docs/ui/UI_SHOWCASE.md` §Vibe + §Anti-default note,把它作为基底——**禁止默认套用 Warm Ceramic** 除非项目 §Vibe 显式继承
2. UI_SHOWCASE.md 现在是**四段式强制**:Vibe / Invariants / Interaction / **Anti-default note**(2026-04-25 起)。缺 Anti-default 段会让 ui-design-router 阻塞
3. ui-design-router 派生 Brief 前要回答 3 题:Brief 里有没有 Warm Ceramic 词汇?有没有违反 §Anti-default?硬约束段是不是套了默认 accent 列表?
4. 现有项目 backfill 不紧急:music/pick/rss_reader 是 Warm Ceramic 合理继承者,只需在 UI_SHOWCASE 补一句"为什么继承是项目本质而非偷懒默认";flametree_ai 已有「Amber Terminal」,补 Anti-default 反例;coffee/image-studio/littletree_x 在下次 UI 改动时跑 `/ui-bootstrap` 会自动补
5. **核心铁律**:允许同质,不允许无意识同质。Warm Ceramic 仍是 FlameTree 默认母语,可继承,但继承必须有论证;偏离也必须有论证。两条路都通过反例机制改变 LLM 采样重心
