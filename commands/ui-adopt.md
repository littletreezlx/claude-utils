---
description: 把 Claude Design export 采纳点反哺回 UI_SHOWCASE / PRODUCT_SOUL,归档 bundle,触发 re-onboard 提示,闭合设计闭环
---

# UI Adopt — 采纳决策反哺

## 目标

闭合 Claude Design 设计闭环的**最后一环**:把某一轮 `/ui-vs` 评审通过的设计点反写进源文档(UI_SHOWCASE / PRODUCT_SOUL),把 Claude Design export 归档到 git,并提醒用户 re-onboard Claude Design(内部 design system 需要同步)。

不跑 /ui-adopt = 好设计停在 export 里,下一轮 `ui-design-router` skill 派生的 Δ Brief 没有更新的 Invariants 参考,Claude Design 下轮还按旧 onboarding 做。**设计体系在文档层面静止。**

## 前置条件

1. 会话中已跑过 `/ui-vs` 并产出"值得保留的"清单(或用户在对话里明确列出本轮要采纳什么)
2. 待归档的 Claude Design export bundle 路径已知(通常是用户刚 export 到临时目录,或上次 `/ui-vs` 评审的 bundle)
3. `docs/ui/UI_SHOWCASE.md` 存在 → 否则先跑 `/ui-bootstrap`
4. `docs/PRODUCT_SOUL.md` 存在
5. `docs/design/EXTERNAL_REFS.md` 存在(有 Claude Design 绑定) → 否则先跑 `/ui-bootstrap`

**缺失任一 → 停止,说明缺什么**。

## 核心工作流

### Phase 1: 采纳上下文加载

读入:

- 会话中最近一次 `/ui-vs` 的"值得保留的"清单作为**采纳候选**
- Claude Design export bundle 的源码(styles.css + *.jsx) —— 不是截图
- 当前 `docs/ui/UI_SHOWCASE.md` 全文
- 当前 `docs/PRODUCT_SOUL.md` 全文
- 当前 `docs/design/DESIGN_BRIEF.md`(本轮 Δ Brief,了解本轮意图)
- 当前 `docs/design/EXTERNAL_REFS.md`(Claude Design 绑定信息 + onboarded_commit)

若本会话没跑过 /ui-vs,提示用户:"请先运行 `/ui-vs`,或在对话里直接列出本轮要采纳哪些点"。

### Phase 2: 采纳决策分类

把每个候选采纳点**分类**,因为要写进不同段落:

| 类别 | 说明 | 目标段落 |
|------|------|---------|
| **Invariant 扩展** | 新增 accent(含 OKLCH 4 槽位)/ 新字阶档位 / 新间距档位 / 新阴影层级 | `UI_SHOWCASE.md §Invariants` |
| **Invariant 收紧** | 删除某档位(设计体系瘦身) | `UI_SHOWCASE.md §Invariants`(删除) |
| **Vibe 演进** | 氛围描述更新、新材质语言、产品调性演化 | `UI_SHOWCASE.md §Vibe` |
| **Interaction 更新** | 新反馈语气、新动效倾向、状态转移强度调整 | `UI_SHOWCASE.md §Interaction Intent` |
| **新组件登记** | 出现了体系内没有的卡片/按钮/导航形态且值得沉淀 | `UI_SHOWCASE.md §Components`(或新增) |
| **产品灵魂更新** | 产品定位/用户画像/情感目标发生变化 | `PRODUCT_SOUL.md` — **高风险,需显式确认** |

**色值采纳的提醒**:从 `styles.css` 里直接读 OKLCH 值(L C H 三个数字),原样抄进 UI_SHOWCASE,不要反向翻译成 Hex/自造名称。

### Phase 3: 决策确认(人机交互)

列出分类后的采纳清单,默认"候选",等待用户逐条确认:

```markdown
## 本轮采纳决策清单

### Invariant 扩展 (2 项)
- [ ] 1. 新增 accent `amber`(来自 styles.css):
      oklch(0.72 0.13 65) / 0.62 0.14 62 / 0.86 0.07 70 / 0.96 0.03 75
- [ ] 2. 新增字阶 XXL (28pt,首屏标题用)

### Vibe 演进 (1 项)
- [ ] 3. 把"暖陶"细化为"施釉陶"

### 产品灵魂更新 (0 项)

### 放弃 (1 项)
- [ ] 4. 本轮的"紫色渐变 CTA" — 明确放弃
```

回复方式:
- **全部接受** → Phase 4
- **部分接受**(列号码) → 只留指定项
- **全部放弃** → 跳过源文档更新,只做 Phase 4.3 归档

**产品灵魂更新需额外确认**:有 PRODUCT_SOUL 变更项时,单独问:"确认要改动产品灵魂吗?这是项目的北极星,一般不改"。

### Phase 4: 应用变更

#### 4.1 UI_SHOWCASE.md 更新

用 Edit 工具精准修改对应段落:

- **Invariant 扩展**:追加到档位清单,带一行"何时用"注释
- **Invariant 收紧**:删除档位(提示:下轮跑 `ui-vision-check` 检查代码里哪里用了被删档位)
- **Vibe 演进**:替换 Vibe 段落的隐喻描述(追加而非替换旧版本,保留演进痕迹)
- **Interaction 更新**:追加或替换 Interaction Intent 条目
- **新组件登记**:追加组件描述(形态 + 何时用 + 对应 JSX 文件位置)

#### 4.2 PRODUCT_SOUL.md 更新(仅有产品灵魂变更项时)

- 再次确认后才改
- 改动留下 Git 提交理由(在对话中陈述,便于后续 commit message)

#### 4.3 Bundle 归档

创建归档目录(**格式对齐 Claude Design export 原生结构**):

```text
docs/design/generated/{YYYY-MM-DD}-{slug}/
├── README.md              ← 本命令写,含下方固化指引 + 采纳摘要
└── project/               ← 原封沿用 Claude Design bundle 结构
    ├── {Name}.html        ← primary design file(即 Claude Design export 的入口 HTML)
    ├── styles.css
    ├── *.jsx              ← data / icons / art / chrome / pages / pages-extra / player 等
    └── uploads/           ← 视觉参考(默认不归档,见下)
```

`{slug}` 从本轮核心变化抽取(如 `warm-ceramic-refinement`、`nav-restructure`)。

**uploads/ 处理**:

- **默认不归档**(是输入参考,不是产出,已有源在用户 Claude Design project 里)
- 若必须归档(竞品截图会下架消失)→ 单独走 git-lfs 或写路径占位
- 默认规则:若 uploads/ 总体积 > 5MB,自动排除归档

**Bundle 体积检查**:复制前 `du -sh` 检查,如 `project/` 去掉 uploads/ 后 > 5MB 警告用户(纯 HTML+CSS+JSX 应该几十 KB)。

#### 4.4 归档 README.md(固化官方三原则)

写入 `docs/design/generated/{YYYY-MM-DD}-{slug}/README.md`:

```markdown
# {YYYY-MM-DD} {slug}

## Bundle 来源
- Claude Design project: {从 EXTERNAL_REFS.md 读 URL}
- Export 时间: {YYYY-MM-DD HH:MM}
- 对应 Δ Brief: `docs/design/DESIGN_BRIEF.md` @ git commit {hash}

## 本轮采纳的变化
- Invariant 扩展: ...
- Vibe 演进: ...
- Interaction 更新: ...

## 放弃的方向
- ...

---

## 🔥 CODING AGENTS: READ THIS FIRST

这是 **Claude Design export 的归档快照**。如果你(Claude Code)读到这里,是因为本地代码实现需要参照此设计。遵循以下原则(来自 Claude Design 官方 handoff):

### 1. Primary design file
入口文件是 `project/{Name}.html`。从它开始读,follow 所有 imports(`styles.css` + `*.jsx`)理解整体结构,再动手实现。

### 2. Pixel-perfect recreate,don't copy structure
这是 **prototype**,不是生产代码。目标是在项目技术栈(Flutter / React / 等)里**视觉对等重新实现**。
不要照抄 JSX 组件结构 —— 结构随目标框架惯例,**视觉输出必须对齐**。

### 3. Read source,don't render/screenshot
所有 dimensions / OKLCH 色值 / layout 规则都在 styles.css 里。截图是有损表示。
只读源码,除非用户明确要求渲染。

### 4. Ambiguous = ask
发现不清楚的地方(设计意图、交互预期) → 在对话里问用户,不要自己脑补。
代码写错比等一下澄清成本高得多。

### 5. 这是只读快照
**严禁在本归档里手动改代码**。要改设计,回 Claude Design 改,重新 export,再归档新的目录。违反铁律 = 下轮 Claude Design re-export 把你的修改冲掉。
```

### Phase 5: Re-onboard Claude Design 提示

检查 `docs/design/EXTERNAL_REFS.md` 里的 `onboarded_commit`:

- 若本轮改动包含 **Invariant 变更**(扩展/收紧/色板变化)→ Claude Design 的内部 design system 已过期,**必须提示用户 re-onboard**:

```markdown
⚠️ Claude Design Re-onboard 提示

本轮采纳了 Invariant 变更(新增 accent `amber` / 字阶 XXL),Claude Design 当前 onboarding 时看到的是**旧 UI_SHOWCASE**。

**强烈建议**:
1. 去 Claude Design 项目设置
2. 触发 "Update design system from codebase"(或等效操作)
3. 把 `docs/ui/UI_SHOWCASE.md` 的最新内容提供给它
4. Re-onboard 完成后,我会更新 `EXTERNAL_REFS.md` 的 `onboarded_commit` 字段

不 re-onboard 的后果:下轮 Claude Design 生成会继续用旧不变量,Δ Brief 里的"本轮特别约束"会被当作**临时例外**而非体系变化。

已完成 re-onboard?回复 y,我更新 EXTERNAL_REFS.md。
```

只有 Vibe 或 Interaction 变更(不动 Invariants)可跳过此步,但仍建议重新对话一次让 Claude Design 吸收新隐喻。

### Phase 6: 后续步骤提示

明确告知下一步:

```markdown
## ✅ 采纳完成

### 已更新
- docs/ui/UI_SHOWCASE.md (§Invariants §Vibe)
- docs/design/generated/2026-04-24-warm-ceramic-v2/ (归档)
- docs/design/EXTERNAL_REFS.md (onboarded_commit 更新,如 Phase 5 完成)

### 必做的后续步骤
1. **Re-onboard Claude Design**(若 Phase 5 提示)
2. **下次 UI 改动**走完整闭环:跟 Claude Code 说"改 X" → `ui-design-router` skill 自动派生 Brief → Claude Design 迭代 → `/ui-vs` → `/ui-adopt`

### 本地代码落地
基于 `docs/design/generated/2026-04-24-warm-ceramic-v2/project/` 做 pixel-perfect recreate,
目标技术栈(如 Flutter)的实现结构可以不同,视觉必须对齐。
```

## 约束

- **不改代码**,只改文档 + 归档。代码实现由后续阶段(基于归档的 bundle)负责
- **PRODUCT_SOUL 改动显式确认两次**,否则可能在不经意间漂移产品定位
- **归档必须进 git**,这是设计史的可追溯底座;不得放 `_scratch/`
- **归档目录命名格式固定**:`{YYYY-MM-DD}-{slug}/project/`
- **不自动 commit**:最后让 git-workflow skill 或用户决定怎么提交
- **单轮产物(不含 uploads) > 5MB** → 提示用 git-lfs
- **已有同日归档** → 后缀加 `-v2` / `-v3`
- **OKLCH 原样保留**:从 styles.css 抄过来的色值保留三位小数精度,不要"简化"或"舍入"

## Gotchas

- 最容易犯的错:把"值得保留的"清单**全部默认采纳**。必须让用户逐项勾选,有些"值得保留"只是"可以保留但没必要更新源文档"
- 另一个常见错误:把 Vibe 新隐喻**替换**掉旧的。Vibe 是层累性的,一般是深化或补充(如"暖陶" → "施釉陶"),不是取代
- Invariants 扩展比收紧更常见。收紧档位意味着有代码在用被删档位 → 必须同时提示跑 `ui-vision-check` 检查漂移
- 不 re-onboard Claude Design = 闭环没真正闭上,下轮 Δ Brief 还要写同样的"特别约束"
