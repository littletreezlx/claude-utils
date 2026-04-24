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
1a. **确保 `uploads/` 在 `.gitignore` 中被持久排除**:往项目根 `.gitignore` 追加(若已有则跳过)
   ```
   # Claude Design archive: 用户上传的 reference 截图不入 git(只保留 Claude Design 产出的 HTML/CSS/JSX)
   docs/design/generated/**/uploads/
   ```
   **铁律**:`uploads/` 是 Founder 上传到 Claude Design 当灵感参考的**私人输入**,不是 Claude Design 的**设计输出**。**不论体积大小一律 gitignore**,不走"超 5MB 才排除"那种条件规则。HTML+CSS+JSX 已足够做 pixel-perfect recreate 和 design-system 溯源,uploads 丢了也能从 Claude Design project 的 inputs 历史重新下载。
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

读入 `.claude-design-inbox/` 下的内容（Phase 0.2 已保证 `{Name}.html` 和 `styles.css` 存在）。

#### 2.0 多版本识别(primary 选择 + 旧版淘汰)

Claude Design project 常常同时有多份 HTML(如 `{Name}.html` + `{Name} v2.html`),因为 project 迭代时旧版不会被自动删除。Bootstrap 的 source of truth **始终是最新版**,旧版既不抽设计系统、也不进归档:

1. **识别规则**:
   - 文件名含显式版本号(`v2` / `v3` / `-rev2` / `_2` / ...) → 取版本号最高的那份为 primary
   - 无版本号时 → 按 mtime,取最新的那份
   - 同理 primary 的 JSX 依赖集取带相同版本前缀的那组(如 `v2-primitives.jsx` / `v2-chrome.jsx` / ...)
2. **旧版处置**:
   - **不抽设计系统**:Phase 3 只读 primary HTML + 其 JSX 依赖 + `styles.css`(或等价 tokens 源)
   - **不进归档**:Phase 4.3 的 `docs/design/generated/{ts}-{slug}-bootstrap/project/` 里**排除**所有旧版 HTML 和其专属 JSX
   - **inbox 里的旧版文件**跟其他 inbox 内容一样被 Phase 4.3 的 move 操作清走(原地不保留)
3. **强制提醒**:完成提示里必须列出:"检测到 inbox 里有旧版 `{旧文件名}`,已以 `{最新版}` 为 primary。**请回到 Claude Design project 里删除旧 HTML** —— 给 Claude Design 的 onboarding 和提示词应只指向最新版,避免下次迭代时 AI 混淆两套方案。"
4. **Δ Brief 标记**:Phase 4.4 生成的 `DESIGN_BRIEF.md` 必须包含 `## 清理提示` 段,列出需在 Claude Design 里删除的旧 file name(见 Phase 4.4 模板)。

#### 2.1 标准结构识别

按 Claude Design 标准结构识别 primary 版本:

```text
.claude-design-inbox/           或   .claude-design-inbox/project/
├── {Name}.html               ← primary design file,含 TWEAK_DEFAULTS + ACCENT_MAP
├── styles.css                ← 设计 tokens 真身(全 OKLCH)
├── data.jsx / icons.jsx / art.jsx / chrome.jsx / pages.jsx / pages-extra.jsx / player.jsx
└── uploads/                  ← 视觉参考(macOS/竞品截图等)
```

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
- 提示用户:"旧版本已备份,Phase 4.2.2 会自动审阅独特内容是否已沉淀"

**同理处理已存在的 DESIGN_BRIEF**:

- 若 `docs/design/DESIGN_BRIEF.md` 已存在(往往是 bootstrap 前的旧完整 prompt 风格) → 备份为 `DESIGN_BRIEF.md.pre-bootstrap-{date}.bak`,然后用 4.4 的 Δ Brief 覆盖

#### 4.2.1 `.bak` 自动审阅（AI-Only 必须机械执行，不能留给下次人审）

UI_SHOWCASE 和 DESIGN_BRIEF 的 .bak 备份不能沉默遗留 — 必须验证里面的独特章节是否在新文档里有对应沉淀，否则哲学段落会静默丢失。

**流程**（对每个 `{file}.bak` 逐个跑）：

1. 扫 .bak 顶级章节：`grep -E '^##' {file}.bak` 取所有 `## xxx` 二级标题
2. 对每个章节标题，提取**关键词**（去掉"一、二、1. 2."等序号和通用词"色彩/间距/字体"等）
3. 在以下目标文件里 `grep` 关键词（任一命中即视为已沉淀）：
   - 新 `docs/ui/UI_SHOWCASE.md`
   - `docs/PRODUCT_SOUL.md`
   - `docs/DESIGN_PHILOSOPHY.md`（若项目有此文件）
4. 分类：
   - **高置信度已沉淀**（章节标题**完整短语**在目标文件中直接出现）→ 自动标记"已沉淀"
   - **低置信度命中**（仅关键词命中但完整短语未命中）→ 保守按"未沉淀"处理
   - **未沉淀**（无任何命中）→ 未沉淀
5. 结果分流：
   - **所有章节都高置信度已沉淀** → 自动 `rm {file}.bak`，在完成提示里报告 "{file}.bak 全部 N 个章节已沉淀，已自动删除"
   - **有未沉淀章节或低置信度章节** → 保留 .bak，对每个未沉淀章节入 TODO：
     ```markdown
     - [ ] [UI Bootstrap] 合并 `{file}.bak` §{章节标题} 独特内容到 {推荐目标}
           推荐目标按章节类型推断：
           - Vibe/护栏/哲学段落 → docs/PRODUCT_SOUL.md 或 docs/DESIGN_PHILOSOPHY.md
           - 视觉规范/组件清单 → docs/ui/UI_SHOWCASE.md
           - 其他 → 下代 AI 判断
     ```

**安全原则**：不确定就保留 .bak，宁可入 TODO 让 AI 人工判断，也不静默丢失。序号类/通用类标题（"## 一、"、"## 色彩"）直接走未沉淀路径。

#### 4.2.2 审计 docs/ui/ 下的旧子文档（新 UI_SHOWCASE 的关系）

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
`docs/ui/README.md`(目录索引)**不动**,不是子文档。

这些 TODO 条目用 `[UI Bootstrap]` 标签区分于 Phase 5 的 `[UI Drift]`(前者是文档漂移,后者是代码漂移)。不引用 DRIFT_REPORT —— 那是代码侧的漂移诊断,不包含文档漂移。

#### 4.3 归档当前 export 为首份 bundle

把 `.claude-design-inbox/` 内容**移动**(不是复制)到:

```text
docs/design/generated/{YYYY-MM-DD}-{slug}-bootstrap/
├── README.md      ← 写"这是 bootstrap 首版,从已有 Claude Design 项目同步"
└── project/       ← 原封沿用 export 结构(**uploads/ 已由 Phase 0.1a 的 gitignore 规则自动排除,无需特殊处理**)
```

**移动完成后必须清理 inbox 污染**:

- 删除 `project/.gitignore`(inbox 带的 `* + !README.md` 模板,若不删会反向把 HTML/CSS/JSX 也 ignore 掉,归档完全无法入 git)
- 删除 `project/README.md`(inbox 的"使用说明"模板,与归档无关;归档自己的说明在外层 README.md)
- 处理完验证:`git check-ignore project/styles.css` 应**不匹配**任何规则(即 styles.css 会被 track);`git check-ignore project/uploads/anything.png` 应匹配 `.gitignore:N:docs/design/generated/**/uploads/`(即 uploads 被 ignore)

移动完成后 inbox 本体清空(目录保留,下次复用)。重建空 inbox 时**必须重写 inbox 的 README.md 与 `.gitignore` 模板**(内容参见 `ui-adopt.md` / 本 skill 同步维护的 inbox 模板段,或拷贝自上次 bootstrap 前的版本)。

外层 `README.md` 固化官方三原则(同 `/ui-adopt` Phase 4.4 内容)。

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

## 清理提示(仅当 Phase 2.0 识别到旧版时)
Bootstrap 用 `{最新版 HTML}` 做了 primary,但 Claude Design project 里还遗留以下旧版文件:

- `{旧 HTML 文件名}`
- `{旧 JSX 前缀文件名,如 primitives.jsx / chrome.jsx / ...}`

**请回到 Claude Design 删除这些旧文件**,给 Claude Design 的 onboarding 和提示词只指向最新版。理由:下次改 UI 时 AI 看到两套并存的方案会混淆对齐基线。

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
- **归档必进 git**,**但 `uploads/` 一律 gitignore(不论体积)**,通过 Phase 0.1a 的根 `.gitignore` 规则 `docs/design/generated/**/uploads/` 持久排除。原因:uploads 是 Founder 上传给 Claude Design 的 reference 截图(私人输入),不是 Claude Design 的设计输出
- **归档用 move 不用 copy**,完成后**必须删除 `project/.gitignore` 和 `project/README.md`**(inbox 污染文件,前者会反向 ignore 掉 HTML/CSS/JSX,后者是 inbox 使用说明与归档无关),再清空 inbox 本体(目录保留,重建时重写 inbox 模板的 README + gitignore)
- **onboarded_commit 固定填 unknown + 标红**,不询问用户
- **去重命中时只更新 mtime,不产生新归档**

## 幂等性

命令支持多次调用。Phase 0.3 SHA256 去重保证 inbox 内容未变时不产生新归档(仅更新 EXTERNAL_REFS 的"最后同步时间")。内容有变化时自动归档为新 `{date}-{slug}-iter-{N}/` 目录并重跑 Phase 3-6。

不存在"警告已 bootstrap 过"的弹窗分支——要强制重来,删除 `docs/design/EXTERNAL_REFS.md` 即可。

## Gotchas

- **inbox 自带的 `.gitignore` 和 `README.md` 在 Phase 4.3 的 move 操作后会污染归档**: `.claude-design-inbox/.gitignore` 的规则是 `* + !README.md + !.gitignore` —— 这是 inbox **本地中转站**的规则,让 inbox 里除了 README 之外的所有内容都不入 git。一旦跟着 move 进了 `project/` 目录,它会**反向**把归档里的 HTML/CSS/JSX 全部 ignore 掉,造成归档形似进了 git 实际啥也没跟踪。**Phase 4.3 必须 `rm project/.gitignore project/README.md`**,再用前面定义的根 `.gitignore` 规则(`docs/design/generated/**/uploads/`)处理 uploads。验证命令:`git check-ignore project/styles.css`(应无输出 = 会入 git) + `git check-ignore project/uploads/x.png`(应匹配根 gitignore 的 uploads 规则 = 不入 git)。
- Inbox 里解压结构经常少一层(用户把 ZIP 内容直接平铺,没保留 `project/` 嵌套)→ 自动识别,找到 primary HTML 就往下走
- **多版本同存(`{Name}.html` + `{Name} v2.html` + 等价 JSX 前缀 `v2-*.jsx`)**:primary **只取最新版**(按版本号,次按 mtime);旧版 HTML / 旧版 JSX 既不抽设计系统、也不进归档。完成提示里必须列出旧版文件名并提醒"去 Claude Design 删掉",否则下次 onboard 时 AI 会在两套并存的方案里对齐漂移。见 Phase 2.0
- 漂移诊断最容易犯的错:把代码里的 `Colors.deepOrange` 等**框架内置常量**也报告为"漂移"。这类是框架合理用法,不要误报 —— 只报告自定义 Hex / rgb 调用
- Claude Design 的 `TWEAK_DEFAULTS` 会暴露很多可调维度,但**不要把它们都写进 UI_SHOWCASE §Invariants** —— 那是运行时 tweak,不是体系不变量
- 反向闭环项目(styles.css 声明 "mirror of {file}") → 5.2 对账的 truth 源是本地代码文件,不是 styles.css。不要因为代码值不在 OKLCH 就报为漂移
- 去重命中时 inbox 已清空 —— 不要以为 Phase 0.3 出错了,上一次跑时 bundle 已 move 到 `generated/{ts}-{slug}/project/`,本次只更新 EXTERNAL_REFS "最后同步时间"
