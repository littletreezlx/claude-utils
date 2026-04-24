---
name: Claude Design 为中心的设计闭环 — 关键设计决策
description: Claude Design(Anthropic 2026-04-17 发布)是所有 UI 工作流的中心。DESIGN_BRIEF 是 Δ 增量,不是完整描述;归档用 Claude Design export 原生结构;唯一编辑入口铁律
type: reference
originSessionId: f7b5e8aa-fab3-4111-a15a-e7bae2248089
---
2026-04-24 确立,2026-04-24 调整(init-design-brief → ui-design-router skill;feat-done → skill)。未来修改 UI 工作流(ui-vs / ui-adopt / ui-bootstrap / ui-design-router skill / feat-done skill)时不应重新发明这套架构,除非 Claude Design 产品形态大变。

## Claude Design 是什么
- Anthropic 2026-04-17 发布的 prototyping 工具
- Opus 4.7 驱动
- 研究预览,Pro/Max/Team/Enterprise 可用
- URL: claude.ai/design

## 关键产品特性（影响闭环设计）
1. **Onboarding 读 codebase + 设计文件自动建立内部 design system**:后续项目自动沿用 colors/typography/components。这意味着本地文档不必完整描述设计系统
2. **Export bundle 结构**:`{Name}.html` + `styles.css` + `*.jsx`(data/icons/art/chrome/pages/pages-extra/player) + `uploads/`
3. **色值统一 OKLCH** + 4 槽位语义(a=accent / d=deep / s=soft / w=wash)
4. **TWEAK_DEFAULTS + /*EDITMODE-BEGIN/END*/ 注释块**是可调滑块的物理实现
5. **Handoff to Claude Code 是官方路径**:Claude Code 读 export 在目标技术栈 pixel-perfect recreate
6. **官方 handoff README 三原则**:primary design file / pixel-perfect don't copy structure / read source don't screenshot / ambiguous = ask

## 我们的闭环分工
- `/ui-bootstrap` command — 老项目首次接入(建绑定+抽设计系统+归档首版+漂移检测),一次性显式
- `ui-design-router` skill — 用户说"改 X UI" 自动触发。分类小改(直做)/大改(派生 Δ Brief 到 `docs/design/DESIGN_BRIEF.md`)。自动阻止 EXTERNAL_REFS 未绑定的大改
- `/ui-vs` command — 评审 export bundle **源码**(HTML/CSS/JSX),不是截图(因为 "read source not screenshot")
- `/ui-adopt` command — 反哺 SOURCES + 归档 bundle(按 Claude Design 原生结构 `{slug}/project/*`) + 触发 re-onboard 提示
- `feat-done` skill — 功能完成自动触发:Design-First Gate 查 bundle → 文档同步 → 静态分析 → git-workflow

**为什么 init-design-brief 和 feat-done 转 skill**:
- init-design-brief 的触发条件"用户想改 UI"可以从对话自动识别,用户经常会忘记先派生 Brief 就直接让 Claude 改代码 → 用 skill 自动拦住
- feat-done 的触发条件"功能完成"也可以从对话识别,命令形式需要用户记得调用 → skill 更自然
- 决策日期:2026-04-24

## 关键铁律(不得更改)
- **Claude Design 是唯一编辑入口**,本地 `docs/design/generated/{ts}/project/*` 是只读快照,手改 = 下轮 re-export 冲掉
- **UI_SHOWCASE 色板必须 OKLCH + 4 槽位**(和 Claude Design 对齐,不用 Hex)
- **BRIEF 是 Δ 增量**(不重述设计系统),长度不超过一屏
- **归档 README 固化官方三原则**(让 Claude Code 读到归档时遵循)
- **Invariant 变更 → 触发 re-onboard Claude Design**(内部 design system 会漂移)

## Why: 为什么不只是升级 /ui-vs
- 试过只做一个"评审工具",但发现源头(BRIEF)/反哺(/ui-adopt)/接入(/ui-bootstrap)都有独立职责
- 各部分频率不同:bootstrap 一次性 / ui-design-router 每轮(改 UI 即触发) / ui-vs 每轮多次 / ui-adopt 偶尔采纳时 / feat-done 每次完工
- 合并会违反"一类问题一个工具"原则。形式选择(command vs skill)看触发方式:需要用户显式投入(bootstrap/vs/adopt)留 command;可以从对话识别(router/feat-done)转 skill

参考决策记录:2026-04-24 对话(压缩前的多轮讨论),从"完全没想到 Claude Design"到"以它为中心"的方案演化。
