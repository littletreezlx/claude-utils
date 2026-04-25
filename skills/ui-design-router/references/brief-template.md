# Δ Design Brief 模板

写到 `docs/design/DESIGN_BRIEF.md`(覆写,历史在 git log)。

---

## 文件头(必含溯源块)

```markdown
> **派生自** `docs/PRODUCT_SOUL.md` + `docs/ui/UI_SHOWCASE.md` + `docs/design/EXTERNAL_REFS.md`
> **生成者**:`ui-design-router` skill
> **过时请重跑**:任一上游源 mtime 晚于本文件即视为过时
> **消费者**:Claude Design(claude.ai/design)— 已 onboarded,仅需本轮增量

---
```

## 正文结构

```markdown
# Δ Design Brief — {项目名} / {YYYY-MM-DD} / {本轮主题 slug}

## 本轮重点(必填)
{一句话说清本轮要做什么}

例:
- 补齐 search 页的 empty / error / loading 三态。
- 把"暖陶"感进化为"施釉陶"的光泽。
- 重构 library 页的信息密度(现在太拥挤)。

## 本轮要突破(可选)
{本轮允许 Claude Design 在哪些 Vibe 维度做创新,不必守现状}

例:
- accent 可以更深一点,不必局限 terracotta,尝试 rust 或 clay。
- 允许引入细微的纹理层(papery / ceramic 质感)。

## 本轮硬约束(可选,来自 UI_SHOWCASE §Invariants)
{本轮必须严守的不变量,从 Invariants 里抽出与本轮相关的}

例:
- 色板只用**本项目** UI_SHOWCASE §Invariants 中已登记的 accent,不自造。**禁止**直接套用 FlameTree 默认母语 accent 列表(terracotta/amber/peach/rust/sand/clay)——除非该项目 §Vibe 明确继承默认母语
- 间距严格用档位(4/8/12/16/24/32/48/64),不出现 10、20、30。
- 字阶不用 XXL,视觉语气要克制。

## 本轮禁止(可选,最重要的约束手段)
{明确列禁止的视觉模式 — 负向约束比正向引导更强}

例:
- 禁止紫色渐变、荧光色、模糊玻璃质感。
- 禁止 bounce 动效(和"克制"的 Interaction Intent 冲突)。
- 禁止大尺寸 AI 插画(和"Less but Better"冲突)。

## References(灵感源,可选)
{本轮可拖进 Claude Design 的参考 — 图片 / URL / 本地路径}

例:
- `docs/design/references/muji-catalog-2024.pdf` — 手册排版节奏
- https://www.readwise.io/ — highlight 卡片的信息层级处理
- `screenshots/competitor-xyz.png` — 对比反面案例

## 功能流与字段(可选,只列新增/变更,不重述)
{本轮涉及的新字段 / 新页面 / 新交互流,不重述已存在的}

例:
- 新增 search 页 empty 态:图标 + 标题"还没搜过什么" + CTA"看看推荐"
- loading 态:只用 skeleton,不用 spinner
```

## 铁律

- **只写 delta**:Claude Design 已经知道整个设计系统(onboarding 时读过),不重述
- **不超过一屏**(约 60 行):超了就是在重述,不是在增量
- **负向约束优先**:"禁止 X" 比 "请做 Y" 更有力
- **模糊让 Claude Design 问**:模棱两可的点留给 Claude Design 在对话里追问,不要塞进 Brief 硬猜
