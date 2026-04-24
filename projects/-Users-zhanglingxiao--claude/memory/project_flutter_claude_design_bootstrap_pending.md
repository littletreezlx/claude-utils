---
name: 5 个 Flutter 项目的 Claude Design 闭环 bootstrap 状态
description: 5 个 Flutter 项目已在 Claude Design 建项目、照着改过代码,但本地闭环未接入(无 EXTERNAL_REFS / UI_SHOWCASE 按新三段式 / generated/ 归档)。需各自跑 /ui-bootstrap
type: project
originSessionId: f7b5e8aa-fab3-4111-a15a-e7bae2248089
---
2026-04-24 确认:Founder 已在 Claude Design 建好 5 个 Flutter 项目对应的 design project,本地代码也已经照着改过一些,但闭环未接入:

- 没有 `docs/design/EXTERNAL_REFS.md` 绑定
- `docs/ui/UI_SHOWCASE.md` 未按新规范(Vibe / Invariants[OKLCH+4槽位] / Interaction 三段式)
- `docs/design/generated/` 归档未建立
- `docs/design/DESIGN_BRIEF.md` 没有或过时(新:由 `ui-design-router` skill 在改 UI 时自动派生,不再是 `/init-design-brief` 命令)

**Why**: 本地和 Claude Design 可能已经分叉(代码先改/设计先改/两边都改),不接入闭环会持续漂移,未来每轮 UI 改动都要重新发明手动对账流程。

**How to apply**:
- 每个 Flutter 项目各自开一个 session 跑 `/ui-bootstrap`(单独场景,不统一跑批)
- Bootstrap 会生成 `docs/design/DRIFT_REPORT.md`,列漂移项,Founder 逐条决策哪边是 truth
- 5 个项目全部 bootstrap 完后,此 memory 可删(状态已过时)
- 跑 bootstrap 前需要 Founder 手动从 Claude Design export bundle 到本地临时目录

这条 memory 是短期状态,跟踪 5 个项目接入进度。bootstrap 完成的项目从清单中划掉;全部完成后删除此文件。
