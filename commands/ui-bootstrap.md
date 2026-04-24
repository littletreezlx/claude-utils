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

这个命令**一次性**建立绑定 + 同步首版设计系统 + 诊断漂移 + 把可执行修正项写进 TODO,把项目拉进闭环。

## 前置条件

1. 本地已是 git repo(便于归档进 git)
2. 用户已经在 Claude Design 里有对应项目,并完成过 onboarding(不是从零开始)
3. 用户已从 Claude Design 导出 bundle 并解压到项目的 `.claude-design-inbox/`(Phase 0 会自动建此目录)

**缺失任一 → 停止,说明该先做什么**。

## 核心工作流

### Phase 0: 准备 inbox（仅首次）

目的:把"export 存哪"标准化为项目级固定路径,避免每次问。

1. 检查 `<project-root>/.claude-design-inbox/` 是否存在
   - 不存在 → 创建该目录 + 往项目根 `.gitignore` 追加 `.claude-design-inbox/`(若已有则跳过)
2. 检查 inbox 内容:
   - 为空 → 停止,提示用户:"把 Claude Design 导出的 ZIP 解压到 `.claude-design-inbox/`,然后重新跑 `/ui-bootstrap`"
   - 有内容但找不到 `{Name}.html + styles.css`(可能用户把 ZIP 本身或其他文件放进来) → 提示正确结构再停止
3. **去重检查**(仅当 `docs/design/generated/` 已有历史归档时):
   - 对 inbox 下 `{Name}.html + styles.css + *.jsx`(排除 uploads/)做 SHA256
   - 对最新那份归档 `docs/design/generated/*/project/` 做相同计算
   - 完全相同 → 只更新 `EXTERNAL_REFS.md` 的"最后同步时间"字段后退出,报告"内容无变化,未产生新归档"
   - 有差异 → 继续后续 Phase

### Phase 1: 采集绑定信息（对话式,2 问）

问用户 2 个问题,答完写 EXTERNAL_REFS.md 雏形:

1. **Claude Design project URL**(如 `https://claude.ai/design/p/xxx`)
2. **Organization scope**(`private` / `org-view` / `org-edit`)

**不再询问**以下字段:

- ~~Onboarded commit~~ → 固定填 `unknown`。Claude Design 产品未暴露此字段,每次问都只能填 unknown。EXTERNAL_REFS.md 里自动标红"建议下次 `/ui-adopt` 前先 re-onboard 一次以回填此字段"
- ~~Export 路径~~ → 固定 `.claude-design-inbox/`,Phase 0 已校验
- ~~Slug~~ → 自动生成(格式 `{项目关键词}-v1`,关键词优先取 PRODUCT_SOUL.md 的核心隐喻,其次取 repo 目录名)。在完成提示里告诉用户默认值,如果要换让他说

### Phase 2: 读 Claude Design Export

读入 `.claude-design-inbox/` 下的内容。按 Claude Design 标准结构识别:

```text
.claude-design-inbox/           或   .claude-design-inbox/project/
├── {Name}.html               ← primary design file,含 TWEAK_DEFAULTS + ACCENT_MAP
├── styles.css                ← 设计 tokens 真身(全 OKLCH)
├── data.jsx / icons.jsx / art.jsx / chrome.jsx / pages.jsx / pages-extra.jsx / player.jsx
└── uploads/                  ← 视觉参考(macOS/竞品截图等)
```

**结构检查**:

- 找不到 primary HTML → Phase 0 已拦截,此处不应再出现
- 没有 styles.css → 不是 Claude Design export(可能是其他工具),停止

### Phase 3: 逆向抽取设计系统

从 export 源码里 parse 出 UI_SHOWCASE 三段式内容:

#### 3.1 从 `styles.css` 抽 Invariants

- **色板**: grep 所有 `oklch\(.+?\)` 出现,按语义聚类
  - 如果 HTML 里有 `ACCENT_MAP = { terracotta: {...}, amber: {...}, ... }` 形式,直接读(现成的 4 槽位数据!)
  - 否则从 CSS 变量定义 `--accent`、`--accent-deep`、`--accent-soft`、`--accent-wash` 推
  - **反向闭环检测**:如果 styles.css 第一行注释声明 "mirror of {file}",代码就是 SSOT,在 EXTERNAL_REFS.md 里加 `Project-Specific Override` 段说明
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

- **Project URL**: https://claude.ai/design/p/xxx
- **Organization scope**: private
- **Onboarded from commit**: `unknown` ⚠️ **建议下次 `/ui-adopt` 前先在 Claude Design 里做一次 re-onboard,然后回填此字段**
- **Onboarded from UI_SHOWCASE mtime**: 2026-04-24 (bootstrap 时的 mtime)
- **Re-onboard trigger**: UI_SHOWCASE.md §Invariants 发生变化时,或距 onboard 超过 30 天
- **最后 bootstrap 时间**: 2026-04-24
- **最后一次 bundle**: docs/design/generated/2026-04-24-{slug}-bootstrap/project/
- **最后同步时间**(去重检查命中时更新此字段,不产生新归档): 2026-04-24

## Project-Specific Override(仅当检测到反向闭环)

本项目 styles.css 第 1 行声明 "Token mirror of {file}",即:

- **真相源**: 本地代码 `{file}`
- **Claude Design**: 镜像
- **re-onboard 时必须先读 {file}**,不信任 styles.css 作为 SSOT
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

terracotta:
  light: a=oklch(0.66 0.138 45) d=oklch(0.58 0.145 42)
         s=oklch(0.84 0.065 55) w=oklch(0.95 0.028 60)
  dark:  ... (若 export 里有)
amber: ...

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

#### 4.2.1 审计 docs/ui/ 下的旧子文档（新 UI_SHOWCASE 的关系）

新 UI_SHOWCASE 是"单文件三段式"结构,但很多项目的旧 docs/ui/ 目录下还有 `theme.md` / `components.md` / `responsive.md` / `screens.md` 等从老文档体系遗留的子文档。这些子文档**不能 skill 自动删**(可能藏有独特的 why 解释),但必须**逐个评估与新 UI_SHOWCASE 的关系**,不能沉默遗留。

扫描 `docs/ui/*.md`(排除 `UI_SHOWCASE.md` 和 `specs/` 目录)。按命名识别类型,写入 TODO:

| 典型文件 | 与新 UI_SHOWCASE 关系 | 入 TODO 动作 |
|---------|---------------------|------------|
| `theme.md` / `tokens.md` / `colors.md` | 色板/字阶/间距 100% 被 §Invariants 取代 | `[UI Bootstrap] 审阅 docs/ui/theme.md 有无独特内容(例如 why 解释),确认后删除` |
| `components.md` | 组件清单正交,但易过时 | `[UI Bootstrap] 审计 docs/ui/components.md 是否还准确,过时内容删除或迁到 docs/FEATURE_CODE_MAP.md` |
| `responsive.md` | 断点/布局策略正交 | `[UI Bootstrap] 把 docs/ui/responsive.md 内容迁到 docs/ARCHITECTURE.md §布局,或并入 UI_SHOWCASE §Interaction` |
| `screens.md` / `navigation.md` | 页面导航架构正交 | `[UI Bootstrap] 把 docs/ui/screens.md 内容迁到 docs/PRODUCT_BEHAVIOR.md §导航,或保留并从 UI_SHOWCASE 链过去` |
| 其他未识别 .md | 未知 | `[UI Bootstrap] 审计 docs/ui/{file} 与新 UI_SHOWCASE 的关系,决定保留/迁移/删除` |

`docs/ui/specs/*.md`(per-page spec)**不动**,那是 `/ui-spec` skill 维护的页面级 spec,与 UI_SHOWCASE 正交共存。

这些 TODO 条目都引用 `docs/design/DRIFT_REPORT.md §旧 UI 子文档` 章节(下面 5.3 补一段)作为定位锚。

#### 4.3 归档当前 export 为首份 bundle

把 `.claude-design-inbox/` 内容**移动**(不是复制)到:

```text
docs/design/generated/{YYYY-MM-DD}-{slug}-bootstrap/
├── README.md      ← 写"这是 bootstrap 首版,从已有 Claude Design 项目同步"
└── project/       ← 原封沿用 export 结构(uploads/ > 5MB 时单独排除)
```

移动完成后 inbox 清空(目录保留,下次复用)。

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

### Phase 5: 代码漂移检测 + 自动分类

既然用户说"已经照着 Claude Design 改了代码",代码和 export 可能已分叉。诊断 + **自动把可执行修正项写进 TODO.md**。

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

本地代码与 Claude Design export 的视觉 token 对账。
可执行修正项已自动写入 `TODO.md`;产品判断类留在本文档 §待议段。

## 命中项(可迁移到 OKLCH token)
- `lib/theme/app_colors.dart:12` `Color(0xFFB85C3B)` ≈ accent `terracotta.a`(oklch(0.66 0.138 45))
  → **已入 TODO**(事实 refactor)

## 漂移项

### 违反已登记铁律(已入 TODO)
- `lib/widgets/card_selector.dart:133` 阴影 `0x1A000000` 违反 shadow_tokens 禁止纯黑

### 产品判断(走 /think 后落档)
- `lib/features/ai/colors.dart` 中 AI accent `#E8A838` / `#95D5B2` 游离在 token 外
  `/think` 结论: {略} → {入 TODO / 入 to-discuss}

### 待议(信息不足)
- `lib/legacy/xxx.dart:42` 出现 `Color(0xFF7B1FA2)` purple-ish,来源不明
  可能原因:
  - (A) 代码是真相,需反哺到 Claude Design 新增 purple accent
  - (B) 违规遗留,应移除
  → 下次 session 确认意图后决策

## 缺失项(Claude Design 有,代码没实现)
- accent `amber` (oklch 0.72 0.13 65) 在 styles.css 里定义了,但代码里没引用
  → 未入 TODO(缺失不等于 bug,等自然实现)
```

#### 5.4 自动分类入 TODO.md

按以下规则把漂移项分流。**本步是硬动作,不询问用户**。

| 情况 | 动作 |
|------|------|
| 违反已登记铁律(shadow tokens / color tokens / 阴影禁用纯黑 / 字阶档位外值等) | 直接写 TODO.md 条目,引用 DRIFT_REPORT 章节 |
| 明确 refactor(代码 Hex 与 token 值一致但未引用 token 名) | 直接写 TODO.md 条目 |
| 产品判断(新增 accent 反哺 or 清理 / 设计方向分歧) | 调 `/think` 获取外部视角 → Claude Code 综合判断:能拍板转 TODO,拿不准进 `to-discuss.md` |
| 信息不足(不知道这是什么色 / 可能是遗留) | 留在 DRIFT_REPORT §待议段 |

**TODO 条目格式**(追加到现有 TODO.md 末尾,不覆盖):

```markdown
- [ ] [UI Drift] 修正 `{file}:{line}` {简短描述}
      Ref: docs/design/DRIFT_REPORT.md §{章节}
```

**to-discuss.md 条目格式**(若有):使用全局 `doc-structure.md` 定义的模板,事实前提 + /think 结论 + 决策选项。

**禁用借口**:
- 不允许以"工作量大""涉及多文件"为由把铁律违反留在 DRIFT_REPORT,必须入 TODO
- 不允许自创 P0/P1/P2 分级,所有入 TODO 的条目一视同仁(执行顺序由 `/todo-doit` 决定)

### Phase 6: 完成提示

```markdown
## ✅ UI Bootstrap 完成

### 已建立
- docs/design/EXTERNAL_REFS.md — Claude Design 绑定
- docs/ui/UI_SHOWCASE.md — 三段式(旧版已备份为 .bak)
- docs/design/generated/2026-04-24-{slug}-bootstrap/project/ — 首版 bundle 归档
- docs/design/DESIGN_BRIEF.md — 初始 Δ Brief
- docs/design/DRIFT_REPORT.md — 代码漂移诊断({N} 项漂移,{M} 项缺失)

### 自动产生的下一步
- **TODO.md 新增 {K} 条 UI Drift 条目** — 下次跑 `/todo-doit` 会逐条处理
- **to-discuss.md 新增 {L} 条**(若有) — 等 Founder 裁决
- **.claude-design-inbox/ 已清空** — 下次 export 直接解压到这里再跑命令即可

### 生效 slug
- 本次归档用 `{slug}`(自动取自 {来源:PRODUCT_SOUL 核心隐喻 / repo 名}) — 如要换,现在告诉我

### 注意事项
- `docs/ui/UI_SHOWCASE.md.pre-bootstrap-*.bak` 如果确认无独特内容,可删除
- EXTERNAL_REFS 里 `onboarded_commit = unknown`,建议下次 `/ui-adopt` 前在 Claude Design 里 re-onboard 一次并回填
```

## 约束

- **只读 Claude Design export + 本地代码,不改代码**;但 **TODO.md / to-discuss.md / DRIFT_REPORT.md 必须写**(Phase 5.4 是硬动作)
- **UI_SHOWCASE 覆盖前必备份**:`.pre-bootstrap-{date}.bak`
- **归档必进 git**,体积 > 5MB 的 uploads/ 单独走 git-lfs 或排除
- **归档用 move 不用 copy**,完成后 inbox 必须清空(目录保留)
- **onboarded_commit 固定填 unknown + 标红**,不询问用户
- **去重命中时只更新 mtime,不产生新归档**

## 一次性 vs 可重复跑

- **默认只跑一次**(创建绑定 + 首版同步)
- 第二次跑时检测到 EXTERNAL_REFS.md 已存在 → 提示:"此项目已 bootstrap 过,是否你要的是 **re-onboard**?(重新从 Claude Design 导入 + 更新 onboarded_commit)"
  - 是:清理旧备份,更新 UI_SHOWCASE(再次备份),生成新 drift report
  - 否:停止

## Gotchas

- Inbox 里解压结构经常少一层(用户把 ZIP 内容直接平铺,没保留 `project/` 嵌套)→ 自动识别,找到 primary HTML 就往下走
- 漂移诊断最容易犯的错:把代码里的 `Colors.deepOrange` 等**框架内置常量**也报告为"漂移"。这类是框架合理用法,不要误报 —— 只报告自定义 Hex / rgb 调用
- Claude Design 的 `TWEAK_DEFAULTS` 会暴露很多可调维度,但**不要把它们都写进 UI_SHOWCASE §Invariants** —— 那是运行时 tweak,不是体系不变量
- 反向闭环项目(styles.css 声明 "mirror of {file}") → 5.2 对账的 truth 源是本地代码文件,不是 styles.css。不要因为代码值不在 OKLCH 就报为漂移
