---
description: 把已存在的 Claude Design 项目接入本地闭环体系 — 建绑定、抽设计系统、归档首版、检测代码漂移
---

# UI Bootstrap — Claude Design 闭环首次接入

## 目标

针对「**Claude Design 已有对应项目,但本地 repo 没接入闭环**」的场景:

- Claude Design 里有 project,已做过 onboarding、有产出
- 本地仓库可能已经"照着 Claude Design 改过代码",但没有:
  - `docs/design/EXTERNAL_REFS.md` 绑定
  - `docs/ui/UI_SHOWCASE.md`(或已过时/未按新规范写)
  - `docs/design/generated/` 归档史
  - `docs/design/DESIGN_BRIEF.md`
- 代码和 Claude Design 设计可能已经分叉(代码先改了/设计先改了/两边都改了)

这个命令**一次性**建立绑定 + 同步首版设计系统 + 诊断漂移,把项目拉进闭环。

## 前置条件

1. 本地已是 git repo(便于归档进 git)
2. 用户已经在 Claude Design 里有对应项目,并完成过 onboarding(不是从零开始)
3. 用户已从 Claude Design 导出一份当前 bundle,放在一个指定路径(不一定是归档位置,命令会移动)

**缺失任一 → 停止,说明该先做什么**。

## 核心工作流

### Phase 1: 采集绑定信息（对话式）

问用户 5 个问题,答完写 EXTERNAL_REFS.md 雏形:

1. **Claude Design project URL**(如 `https://claude.ai/design/projects/xxx`)
2. **Organization scope**(`private` / `org-view` / `org-edit`)
3. **当前 Claude Design onboarding 参照的 codebase commit**(用 `git log` 帮用户回忆最近一次在 Claude Design 里做大调整时的代码状态;不确定就填 `unknown` 并标注需要 re-onboard)
4. **Claude Design export 的本地路径**(用户刚从 Claude Design 下载解压到哪里)
5. **本项目的 slug 命名**(用于归档目录,建议项目主题关键词,如 `warm-ceramic-v1`)

### Phase 2: 读 Claude Design Export

读入 Phase 1 采集的 export 路径下的内容。按 Claude Design 标准结构识别:

```text
{export-root}/                或   {export-root}/project/
├── {Name}.html               ← primary design file,含 TWEAK_DEFAULTS + ACCENT_MAP
├── styles.css                ← 设计 tokens 真身(全 OKLCH)
├── data.jsx / icons.jsx / art.jsx / chrome.jsx / pages.jsx / pages-extra.jsx / player.jsx
└── uploads/                  ← 视觉参考(macOS/竞品截图等)
```

**结构检查**:

- 找不到 primary HTML → 提示用户路径是否正确、是否漏了层(Claude Design 标准是 `{bundle}/project/`)
- 没有 styles.css → 不是 Claude Design export(可能是其他工具),停止

### Phase 3: 逆向抽取设计系统

从 export 源码里 parse 出 UI_SHOWCASE 三段式内容:

#### 3.1 从 `styles.css` 抽 Invariants

- **色板**: grep 所有 `oklch\(.+?\)` 出现,按语义聚类
  - 如果 HTML 里有 `ACCENT_MAP = { terracotta: {...}, amber: {...}, ... }` 形式,直接读(现成的 4 槽位数据!)
  - 否则从 CSS 变量定义 `--accent`、`--accent-deep`、`--accent-soft`、`--accent-wash` 推
- **字阶**:扫 `font-size:` 唯一值,按大小排序归档到 XS/S/M/L/XL/XXL
- **间距**:扫 `padding|margin|gap:`,统计 top-K 值作为档位(标准应是 4/8/12/16/24/32/48/64)
- **圆角**:扫 `border-radius:` 唯一值
- **阴影**:扫 `box-shadow:` 唯一值

#### 3.2 从 `{Name}.html` 抽 Interaction Intent

- 读 `transition-timing-function` 倾向(standard / ease-out / cubic-bezier)
- 读 `@keyframes`(判断动效丰富度)
- 读 handler 延迟(setTimeout 等)
- 读 TWEAK_DEFAULTS(可调项暴露了设计意图的维度)

#### 3.3 从 `uploads/` + 文件名/命名 抽 Vibe

- 看 uploads/ 里的参考图(macOS 风格?杂志风?极简?)
- 看 accent 命名(`terracotta` / `clay` / `sand` → 暖陶系)
- 看组件命名(`chrome.jsx` → macOS 式外壳?`art.jsx` → 重视觉?)

### Phase 4: 生成 / 更新源文档

#### 4.1 写 `docs/design/EXTERNAL_REFS.md`

```markdown
# Design 外部工具绑定

## Claude Design

- **Project URL**: https://claude.ai/design/projects/xxx
- **Organization scope**: org-edit
- **Onboarded from commit**: abc123 (2026-04-20)
- **Onboarded from UI_SHOWCASE mtime**: 2026-04-24 (bootstrap 时的 mtime)
- **Re-onboard trigger**: UI_SHOWCASE.md §Invariants 发生变化时,或距 onboard 超过 30 天
- **最后 bootstrap 时间**: 2026-04-24
- **最后一次 bundle**: docs/design/generated/2026-04-24-bootstrap/project/
```

#### 4.2 写 / 重写 `docs/ui/UI_SHOWCASE.md`(三段式)

用 Phase 3 抽取的数据填充三段式骨架:

```markdown
# UI Showcase — {项目名}

> 最后 bootstrap: 2026-04-24(来自 Claude Design export)

## Vibe(软引导)
- 核心隐喻: {抽出来的,如"暖陶 + 纸张感 + 施釉光泽"}
- 材质参照: {如"macOS 原生感 + 无酸纸 + 暖台灯"}
- 情绪目标: {如"静谧书房,私人专注"}

## Invariants(硬约束,Claude Design 禁止自造)

### 色板(OKLCH + 4 槽位)
{从 styles.css 抽出的 ACCENT_MAP,原样 OKLCH 格式}
accent 列表: terracotta / amber / peach / rust / sand / clay
槽位: a (accent) / d (deep) / s (soft) / w (wash)

```
terracotta:
  light: a=oklch(0.66 0.138 45) d=oklch(0.58 0.145 42)
         s=oklch(0.84 0.065 55) w=oklch(0.95 0.028 60)
  dark:  ... (若 export 里有)
amber: ...
```

### 字阶档位
XS / S / M / L / XL / XXL,对应 {抽出的具体 rem 或 px 值}

### 间距档位
4 / 8 / 12 / 16 / 24 / 32 / 48 / 64

### 圆角档位
0 / 4 / 8 / 16 / 999 (pill)

### 阴影体系
{若抽到多层级,枚举;若只有 1-2 种,说明体系薄}

## Interaction Intent

- 响应节奏: {如"<150ms 即时反馈;>500ms 加 skeleton"}
- 反馈语气: {如"克制,淡入淡出优于滑入滑出"}
- 动效曲线: {如"standard easing (cubic-bezier(0.25, 0.1, 0.25, 1));禁止 bounce"}
- TWEAK 暴露维度: theme / accent / density / playerVariant (来自 Claude Design TWEAK_DEFAULTS)
```

**处理已存在的 UI_SHOWCASE**:

- 若已存在**旧版本**(可能是 Hex 色板、缺 Interaction 段等)→ **备份为 `UI_SHOWCASE.md.pre-bootstrap-{date}.bak`**,然后用新版覆盖
- 提示用户:"旧版本已备份,如有独特内容(如原创组件说明)需要保留,请手动合并后删除 `.bak`"

#### 4.3 归档当前 export 为首份 bundle

把用户指定的 export 路径复制到:

```text
docs/design/generated/{YYYY-MM-DD}-{slug}-bootstrap/
├── README.md      ← 写"这是 bootstrap 首版,从已有 Claude Design 项目同步"
└── project/       ← 原封沿用 export 结构(可选择性排除大 uploads/)
```

README.md 固化官方三原则(同 `/ui-adopt` Phase 4.4 内容)。

#### 4.4 生成 `docs/design/DESIGN_BRIEF.md`(初始 Δ Brief)

首版 BRIEF 比较简单:

```markdown
> 派生自 PRODUCT_SOUL + UI_SHOWCASE + EXTERNAL_REFS
> 生成命令: /ui-bootstrap
> 消费者: Claude Design — 已 onboarded

---

# Δ Design Brief — {项目名} / bootstrap 完成

## 本轮重点
Bootstrap 完成。下一轮改 UI 时跟 Claude Code 说明意图,`ui-design-router` skill 会自动识别并派生 Δ Brief(大改)或放行小改。

## References(bootstrap 时识别的灵感源)
{从 uploads/ 里列的内容,如:macOS 原生音乐 app / Muji catalog 等}
```

### Phase 5: 代码漂移检测（重要）

既然用户说"已经照着 Claude Design 改了代码",代码和 export 可能已分叉。**必须诊断**,但**不自动改**。

#### 5.1 扫本地代码里的视觉 tokens

按项目类型(Flutter / React / ...)识别常用的 theme / token 文件:

- Flutter: `lib/theme/`、`lib/core/theme/`、`lib/**/theme*.dart`、`lib/**/colors*.dart`
- React: `src/theme/`、`src/styles/`、tailwind.config.js
- 通用:`*.scss` / `*.css`

grep 色值:
- Hex: `#[0-9a-fA-F]{3,8}`
- RGB: `rgb\(|rgba\(`
- OKLCH: `oklch\(`
- named colors(如 Flutter 的 `Colors.deepOrange`)

#### 5.2 和 `styles.css` 对账

对每个代码里的色值:

- 能在 styles.css 的 OKLCH accent 里**视觉匹配**(色差 ΔE < 5)→ 推荐迁移到 OKLCH token 名
- 完全对不上 → 漂移点,列出代码位置

#### 5.3 输出 `docs/design/DRIFT_REPORT.md`

```markdown
# Bootstrap Drift Report — 2026-04-24

本地代码与 Claude Design export 的视觉 token 对账。**仅诊断,不自动改**。

## 命中项(可迁移到 OKLCH token)
- `lib/theme/app_colors.dart:12` `Color(0xFFB85C3B)` ≈ accent `terracotta.a`(oklch(0.66 0.138 45))
  建议: 用 token 名引用,不用字面 Hex
- ...

## 漂移项(代码里有,Claude Design 没有)
- `lib/theme/app_colors.dart:34` `Color(0xFF7B1FA2)` — 这是什么?purple-ish,不在设计体系
  可能原因:
  - (A) 代码是真相,需要反哺回 Claude Design(告诉它新增 purple accent)
  - (B) 设计是真相,代码里的 purple 是违规,应移除

## 缺失项(Claude Design 有,代码没实现)
- accent `amber` (oklch 0.72 0.13 65) 在 styles.css 里定义了,但代码里没引用 → 待实现

## 建议下一步
1. 逐条检查"漂移项",决定哪边是 truth
2. 若代码方向对 → 下次 UI 改动走完整闭环,反哺到 Claude Design
3. 若设计方向对 → 把不合规色值加入 TODO.md 待清理
```

**不自动删改代码**。每个项目的漂移都是它自己的故事,需要项目 session 看。

### Phase 6: 完成提示

```markdown
## ✅ UI Bootstrap 完成

### 已建立
- docs/design/EXTERNAL_REFS.md — Claude Design 绑定
- docs/ui/UI_SHOWCASE.md — 三段式(旧版已备份为 .bak)
- docs/design/generated/2026-04-24-{slug}-bootstrap/project/ — 首版 bundle 归档
- docs/design/DESIGN_BRIEF.md — 初始 Δ Brief
- docs/design/DRIFT_REPORT.md — 代码漂移诊断({N} 项漂移,{M} 项缺失)

### 必看的后续步骤
1. **读 DRIFT_REPORT.md** — 逐条决策,各项目独立判断
2. **决策完漂移后**:
   - 代码方向对 → 下次 UI 改动时,先在 Claude Design 里更新,再 /ui-adopt 反哺,再本地实现
   - 设计方向对 → 把代码修正项加入 TODO.md
3. **下次 UI 改动走完整闭环**: 跟 Claude Code 说改 X → ui-design-router skill → Claude Design → /ui-vs → /ui-adopt

### 注意事项
- `docs/ui/UI_SHOWCASE.md.pre-bootstrap-*.bak` 如果确认无独特内容,可删除
- Claude Design 当前 onboarding 状态 = EXTERNAL_REFS 里的 onboarded_commit,若已陈旧建议 re-onboard
```

## 约束

- **只读 Claude Design export + 本地代码,只写文档,不改代码**
- **UI_SHOWCASE 覆盖前必备份**:`.pre-bootstrap-{date}.bak`
- **归档必进 git**,体积 > 5MB 的 uploads/ 单独走 git-lfs 或排除
- **onboarded_commit 为 unknown 时必须标红**,强烈建议用户下次跑 `/ui-adopt` 前先 re-onboard 一次
- **DRIFT_REPORT 是诊断,不是 TODO** — 只输出事实,决策权在项目 session

## 一次性 vs 可重复跑

- **默认只跑一次**(创建绑定 + 首版同步)
- 第二次跑时检测到 EXTERNAL_REFS.md 已存在 → 提示:"此项目已 bootstrap 过,是否你要的是 **re-onboard**?(重新从 Claude Design 导入 + 更新 onboarded_commit)"
  - 是:清理旧备份,更新 UI_SHOWCASE(再次备份),生成新 drift report
  - 否:停止

## Gotchas

- 用户 Phase 1 说不出 `onboarded_commit` 很正常(Claude Design 没暴露这个) → 填 `unknown` + 提示"下次在 Claude Design 里做大调整后,来跑一次 /ui-bootstrap --re-onboard 更新这个字段"
- Export 路径经常少一层(用户直接解压到某目录,没保留 `{project-name}/project/` 嵌套)→ 自动识别,找到 primary HTML 就往下走
- 漂移诊断最容易犯的错:把代码里的 `Colors.deepOrange` 等**框架内置常量**也报告为"漂移"。这类是框架合理用法,不要误报 —— 只报告自定义 Hex / rgb 调用
- Claude Design 的 `TWEAK_DEFAULTS` 会暴露很多可调维度,但**不要把它们都写进 UI_SHOWCASE §Invariants** —— 那是运行时 tweak,不是体系不变量
