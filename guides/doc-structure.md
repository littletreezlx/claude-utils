# 项目文档标准结构

本文件定义项目 docs/ 目录的标准文件体系。全局 CLAUDE.md 通过 `@` 引用本文件，避免每次会话都加载完整表格。

> **受众**：文档体系的首要读者是 AI（跨会话上下文传递），次要读者是产品负责人（做产品决策时偶尔阅读）。格式优先满足 AI 高效消费和人类偶尔阅读。
>
> **协作模式**：AI-Only 开发。所有文档由 AI 生成和维护，人类是产品负责人。工作流中不存在「人工审核代码」「人工走查」等环节。

## 根目录入口文件

- `README.md` — 人类入口
- `CLAUDE.md` — AI 入口
- `TODO.md` — 已决策行动队列（`/todo-doit` 消费）
- `to-discuss.md` — `/think` 也无法决策的事项队列（产品负责人最终裁决）

## 三文件协作架构（行动/决策/材料 分离）

| 文件 | 内容性质 | 谁来消费 |
|------|---------|---------|
| `TODO.md` | 已决策、可执行任务 | AI（`/todo-doit` 自动执行）|
| `to-discuss.md` | `/think` 也无法决策的事项 | 产品负责人最终裁决 |
| `_scratch/*.md` | 原始材料、探索报告、调试日志 | AI 查阅上下文用 |

**铁律**：
- 事实型 bug → `TODO.md`；观点/产品/设计判断 → **先借助 `/think` 获取外部视角，Claude Code 自己综合判断做最终决策**，能拍板则转 TODO 或丢弃，自己也拿不准才进 `to-discuss.md`；原始材料 → `_scratch/`
- **严禁把 AI 的观点伪装成已决策任务塞进 TODO.md**（会污染 `/todo-doit` 的执行流）
- **严禁跳过 `/think` 直接把观点丢进 `to-discuss.md`**（`/think` 引入独立视角后，Claude Code 能处理绝大部分产品+技术决策）
- TODO.md 与 to-discuss.md **物理独立，不设指针**（否则互相污染、变成视觉盲点）
- `to-discuss.md` 不是 backlog 而是 **Last-Resort Queue**：只放 `/think` 明确表示无法决策的事项。每条要么转 TODO，要么被驳回，不得无限积压
- **交互模式下绕过 to-discuss.md**：`/think` 在主动对话中触发时，升级决策直接在对话里展示模板让用户当场勾选（见 `skills/think/SKILL.md` § 3.3.2）。只有自主模式（`/loop`、cron、batch）或用户当场无法定夺时才落库到 `to-discuss.md`

### to-discuss.md 条目模板

> **前置条件**：写入 to-discuss.md 前必须已调用 `/think`，且 `/think` 明确表示无法决策。

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/xxx.md § 章节)
- **事实前提**: [基于什么客观现象，禁止加主观修饰]
- **/think 结论**: [/think 给出了什么判断，为什么它认为自己无法拍板]
- **决策选项**:
  - [ ] 采纳 → 转 TODO.md
  - [ ] 驳回 → 直接删
```

**禁止给 AI 观点加置信度字段** —— AI 在胡说时极度自信，置信度是噪音。

## docs/ 标准文件

| 文件 | 回答的问题 | 更新频率 | 内容 |
|------|----------|---------|------|
| `docs/PRODUCT_SOUL.md` | **为谁**做、**为什么**存在 | 极少变 | 产品愿景、用户画像、设计隐喻、情感目标 |
| `docs/PRODUCT_BEHAVIOR.md` | 系统**怎么运转** | 中频 | 状态机、导航规则、交互模式、全局状态策略 |
| `docs/user-stories/*.md` | 用户**会做什么** | 中频 | 用户视角操作序列 + 可执行验证步骤（`/ai-qa-stories` 消费） |
| `docs/user-stories/qa/*.qa.md` | 怎么**自动验证** | 中频 | 结构化验证脚本（编译自 story，AI 专属） |
| `docs/features/*.md` | 功能**怎么设计** | 中频 | 功能架构、API 契约、交互细节、实现决策 |
| `docs/ARCHITECTURE.md` | 系统**怎么搭建** | 中频 | 技术架构、数据流、关键技术决策、目录结构 |
| `docs/ROADMAP.md` | 项目**去向哪** | 高频 | 当前阶段状态、Known Issues、Next Steps |
| `docs/FEATURE_CODE_MAP.md` | 代码**在哪里** | 中频 | 功能→代码路径索引（GPS 导航） |
| `docs/design/DESIGN_BRIEF.md` | 设计工具**本轮的增量指令** | 低频（派生） | 给 Claude Design 的 **Δ Brief**（Code→Design 的委托函，只写本轮要做/不做什么），派生自 PRODUCT_SOUL + UI_SHOWCASE + EXTERNAL_REFS，由 `ui-design-router` skill 在检测到大改动意图时自动派生 |
| `docs/design/HANDOFF.md` | 设计工具**本轮的回函** | 每轮覆写 | Claude Design 写给 Claude Code 的**建议函 + 它侧已做的镜像修正说明**（Design→Code 方向，省去 diff 反推成本）。与 DESIGN_BRIEF.md 对称。**不具合规约束力** —— 由 `/ui-vs` / `/ui-adopt` / `ui-design-router` 等 Skill 消费判断，Claude Code 保留否决权 |
| `docs/design/EXTERNAL_REFS.md` | **Claude Design 怎么绑定** | 低频 | Claude Design project URL / org scope / 上次 onboarding 的 codebase commit / re-onboard 触发条件。若项目未接入 Claude Design，跑 `/ui-bootstrap` 建立 |
| `docs/design/generated/{YYYY-MM-DD-slug}/project/` | 某轮 **Claude Design export 归档** | 每轮一次（或首次 bootstrap） | 原封沿用 Claude Design export 结构（`{Name}.html` + `styles.css` + `*.jsx` + `uploads/`），进 git 便于迭代溯源。**体积控制**：uploads/ 单独控制在 5MB 内或 git-lfs |

### 派生文档约定

`docs/design/DESIGN_BRIEF.md` 是**派生增量指令**，不是完整设计描述：

- **定位**：给 Claude Design 看的"小纸条"。Claude Design 在 onboarding 时已经读过 codebase + 设计文件建立了内部 design system，BRIEF 不重述设计系统，只描述**本轮特别的 delta**（要做什么、不要做什么、参考哪些灵感）
- 源：`PRODUCT_SOUL.md` + `docs/ui/UI_SHOWCASE.md` + `docs/design/EXTERNAL_REFS.md`
- 生成：`ui-design-router` skill 在检测到大改动意图时自动派生
- 文件头必须带 `> 派生自 PRODUCT_SOUL + UI_SHOWCASE + EXTERNAL_REFS，由 ui-design-router skill 派生,过时会自动重跑`
- **清理规则**：`/doc-clean`、`inbox` skill 等**不得**将该文件当作临时产物清理
- **过时判定**：任一上游源文件 mtime 晚于本文件 → 标记过时、重跑

### 镜像传话层（BRIEF ⇄ HANDOFF，双向传话，非权威）

`DESIGN_BRIEF.md` 和 `HANDOFF.md` 是**一对镜像传话文件**，每轮迭代时承载 Claude Code 与 Claude Design 之间的双向沟通，**但都不是 truth**。

```text
    DESIGN_BRIEF.md  ─────▶  CLAUDE DESIGN  ─────▶  HANDOFF.md
     (委托函,我写)            (外部,对方)             (回函,它写)
          ▲                                                │
          │                                                ▼
          └────────── Skill 层(ui-vs/ui-adopt/router) ────┘
                                  │
                                  ▼
          truth = PRODUCT_SOUL + UI_SHOWCASE + EXTERNAL_REFS
```

| 文件 | 方向 | 作用 |
|---|---|---|
| `docs/design/DESIGN_BRIEF.md` | Code → Design | 我方本轮的**委托函**：要做什么、不做什么、参考哪些灵感（增量） |
| `docs/design/HANDOFF.md` | Design → Code | 对方本轮的**回函**：建议代码侧改哪些地方、它已在自己侧做了哪些镜像修正 |

**核心定位**：

- 两者都是**传话载体**，不是合规物件。权威仍在 SOURCES（PRODUCT_SOUL / UI_SHOWCASE / EXTERNAL_REFS）
- **合规约束在 Skill 层**（`/ui-vs` / `/ui-adopt` / `ui-design-router` / `feat-done`），**不在文件结构本身**
- Claude Code 读 HANDOFF 后**仍走自己的判断流程**：`/ui-vs` 的 Phase 0 Invariants 机械校验、Phase 1 四柱审视、Phase 1.9 Gemini 第二视角 —— HANDOFF 的建议**不绕过**这些质量门
- 真正落地由 Skill 决定：小改且 Invariants 不破 → `ui-design-router` 直接执行；触及 Invariants / ≥3 页面 / 新视觉模式 → 仍走 `/ui-vs` + `/ui-adopt` + 归档 bundle 的完整闭环

**HANDOFF.md 的价值**：省掉 Claude Code 做 diff 反推"这轮 Claude Design 改了什么、想让我改什么"的体力活。对方说清楚，我方看清楚。仅此而已，不承担更多。

**HANDOFF.md 规范约定**：

- 位置：`docs/design/HANDOFF.md`（与 DESIGN_BRIEF 同层对称）
- 写入方式：Claude Design 每轮输出**完整文件原文**供 Claude Code 整文件覆写，不发增量片段（拼接易错位）
- `Repo ref: @ <commit-sha>`：**阅读上下文标记**（非校验字段）。标明该回函基于哪个代码快照写成 —— Claude Code 据此判断 `Files to touch` 是否可能已飘走
- `Files to touch` 字段是**建议性指向**，非命令式。Claude Code 执行前校验文件是否仍存在、是否在 ref 之后被动过，保留否决权
- 反馈回流格式：Claude Code 对 HANDOFF 条目的异议用 `[FEEDBACK for TASK-XXX]` 结构化块，用户粘贴给 Claude Design
- 清理规则：同 DESIGN_BRIEF，不得被 `/doc-clean`、`inbox` skill 当临时产物清理

**Status 状态机（谁来标，铁律）**：

| Status | 维护者 | 含义 |
|---|---|---|
| `ready-for-code` | Claude Design | 我这边建议这样改,Code 可执行 |
| `needs-design-revision` | Claude Design | Code 提了异议,我要先改设计再回来 |
| `in-progress` | Claude Code | 正在执行该条目 |
| `done` | **仅 Claude Code**（`/ui-adopt` / `feat-done` 在 push 后追加带 commit sha 的行）| 代码侧已真正落地 |

**Claude Design 永远不标 `done`** —— "我这边建议做完了"不等于"代码侧已落地",两者的 truth source 不同。

**可选 Appendix 段（Claude Design 侧的自我修正日志）**：

HANDOFF.md 末尾可能出现 `## Appendix` 段，记录 Claude Design 在**它自己侧**（如内部 styles.css 镜像）做了哪些修正。这类条目：

- **不进入 TASK 流、不占 TASK 编号**
- **Claude Code 无需响应** —— 仓库代码本就是 truth,drift 只存在于 Claude Design 的镜像侧
- 仅作审计痕迹,让 Code 知情但不触发动作
- **Code 侧识别规则**:以 `## Appendix`(含 `## Appendix A/B/...`) 开头的整段一律跳过,不按 TASK 处理 —— 即使 Claude Design 忘记在段标题标"不占 TASK 编号",识别仍按段标题前缀走

### Code 侧执行约定（2026-04-24 实战提炼）

当 HANDOFF Pending 段有 TASK 时,Code 按本约定处理,避免每个会话重新判断:

**F1. `Files to touch (suggestion)` 不准时的处理**

- Code 用语义查找(文件名相似 / 内容相关)自行纠正路径
- 在执行日志注明 `actual path: X`(让 Claude Design 下轮拿到更新的基线)
- **只有找不到任何合理对应文件**才发 `[FEEDBACK for TASK-XXX]`,不要把"拼写偏差"当"语义冲突"(实战踩过 `article_card.dart` vs `article_item.dart`)

**F2. 降级方案决策门槛**

- TASK **未明示授权降级** → 发 FEEDBACK 问,不自己拍
- **明示授权降级**(如"若字体无 smcp feature 则 fallback") → 按授权范围执行,不越界
- 授权范围**模糊**(如"如果有需要调整") → FEEDBACK 明确边界后再执行

**F3. 多 TASK commit 粒度**

- 同 HANDOFF 多 TASK **功能连续**(同一页面 / 同一交互流) → 一个 commit
- **功能分散**(不同模块) → 按 TASK 分 commit
- `feat-done` 尊重 Code 判断,不强制粒度,commit message 里写清"本 commit 含 TASK-001/002"即可

### UI 设计闭环体系（以 Claude Design 为中心）

**首要消费者：Claude Design**（Anthropic 2026-04 发布的 prototyping 工具，由 Opus 4.7 驱动）。Claude Design onboarding 时读 codebase + 设计文件自动建立内部 design system，后续项目复用。因此 **本地文档的定位从"完整描述"变为"增量约束 + 归档快照 + 反哺更新源"**。

```text
SOURCES (权威源，唯一 truth)
 ├─ docs/PRODUCT_SOUL.md           — 产品情绪底色（极少变）
 ├─ docs/ui/UI_SHOWCASE.md         — 视觉体系（Vibe + Invariants[OKLCH] + Interaction）
 └─ docs/design/EXTERNAL_REFS.md   — Claude Design 绑定（URL + org + onboarded commit）
       │
       │  首次接入: /ui-bootstrap（从 Claude Design export 逆向抽取 + 建立绑定 + 漂移检测）
       │  每轮迭代: ui-design-router skill（自动触发:用户说"改 X" → 分类小改/大改,大改派生 Δ Brief）
       ▼
镜像传话层 (每轮对话,非权威)
 ├─ docs/design/DESIGN_BRIEF.md   — Code → Design 委托函（派生自 SOURCES，本轮增量）
 └─ docs/design/HANDOFF.md        — Design → Code 回函（Claude Design 每轮整文件覆写）
       │  用户粘贴 / 整文件覆写 双向传递
       ▼
CLAUDE DESIGN（唯一编辑入口 — 外部)
       │  读 BRIEF + 仓库源码 → 写 HANDOFF + 生成 prototype
       │  用户在 Claude Design 里迭代（对话/inline 评论/滑块）
       │
       ├──▶ Share URL          → /ui-vs 评审（读 URL 或本地 export 源码 + HANDOFF 作为上下文）
       ├──▶ Export bundle      → docs/design/generated/{ts}/project/*（归档进 git）
       └──▶ Handoff to Code    → Claude Code 读 export 重新实现（pixel-perfect, 目标技术栈）
       ▼
DECISION (Skill 层,不盲从 HANDOFF 建议)
       │  /ui-adopt （反哺 SOURCES + 触发 re-onboard 提示 + 在 HANDOFF 标 Done 带 commit sha）
       ▼
回到 SOURCES，进入下一轮
```

**唯一编辑入口铁律**：Claude Design 是设计的**唯一编辑入口**。本地 `docs/design/generated/{ts}/project/*` 是**只读快照**，**严禁在 export 文件里手动改代码**。要改设计,回 Claude Design 改,重新 export,再归档新的 `{ts}/`。违反后果：下次 Claude Design re-export 会覆盖你的手改，整轮工作白做。

### 设计优先原则（Design-First Gate）

**UI 改动量大时，严禁直接写本地代码 —— 必须先走 Claude Design 闭环**。

**触发阈值**（任一满足即为"改动量大"）：

- 本次改动涉及 **≥ 3 个页面** 的视觉
- 触及 **设计不变量**（OKLCH 色板 / 字阶档位 / 间距档位 / 圆角档位 / 阴影）
- 新增**新的视觉模式**（原体系没有的卡片样式 / 导航形态 / 状态呈现）
- 用户明说"想整体换个感觉"、"重新设计"、"改一下风格"

**触发后的强制流程**：

1. 在 **Claude Design** 里对当前设计做迭代（对话/评论/滑块）
2. Export bundle 到本地
3. `/ui-vs` 评审 export 源码（读 HTML/CSS/JSX，不是截图）
4. 满意则 `/ui-adopt` 反哺 SOURCES + 归档 export + 触发 re-onboard 提示
5. **然后才**进入本地代码实现（pixel-perfect recreate in Flutter/React/etc）

**可以绕过的例外**（只允许这些情况直接改代码）：

- 单文件 bug 修复（不涉及视觉语言）
- 已在 UI_SHOWCASE 里登记的既有组件的**用法**调整（不改定义）
- 字符串 / 文案修改（不涉及排版）
- 响应已采纳设计的落地实现（本次就是步骤 5，基于 `docs/design/generated/{ts}/project/` 做 pixel-perfect recreate）

**`feat-done` 的 Step 0 自检**要问两个问题：
- 本次改动是否触发 Design-First Gate？
- 若触发，本次实现**基于哪个 bundle**（`docs/design/generated/{ts}/project/` 路径必须明确）？

触发但没有对应 bundle → 停流程，回去走闭环。

### UI_SHOWCASE.md 强制段落

`docs/ui/UI_SHOWCASE.md` 必须包含四个段落（缺失任一则 `ui-design-router` skill 拒绝派生 Brief，`/ui-bootstrap` 会生成初版）：

#### 1. Vibe（软引导，可扩展）

情绪隐喻、材质类比、氛围描述。FlameTree 默认母语示例（仅供参考）："静谧书房"、"暖陶"、"施釉陶"。**项目可继承默认母语，也可声明完全不同的基底**（如"冷峻终端"、"报纸 editorial"、"磨砂工具感"）—— 关键在于段内措辞要具体到 LLM 能识别（避免"现代简约"这种空泛词）。Claude Design 在 Vibe 层允许创造性演进。

#### 2. Invariants（硬约束，不可自造）

设计不变量。**色板采用 OKLCH + 4 槽位**（和 Claude Design 内部模型对齐），其他维度用档位枚举：

- **色板（OKLCH + 4 槽位）**：每个命名 accent 定义 4 个槽位
  - `a` = accent（主色）
  - `d` = deep（深强调）
  - `s` = soft（柔和背景）
  - `w` = wash（最浅，几乎白）
  - 格式：`terracotta: { hue: 45, light: { a: 'oklch(0.66 0.138 45)', d: '...', s: '...', w: '...' } }`
  - **禁止 Hex / RGB / HSL**，禁止 AI 工具自造新 accent 或新槽位
- **字阶档位**：XS / S / M / L / XL / XXL 六档，禁止自造新档
- **间距档位**：4 / 8 / 12 / 16 / 24 / 32 / 48 / 64
- **圆角档位**：0 / 4 / 8 / 16 / 999（pill）
- **阴影体系**：必须枚举全部层级

**为何 OKLCH**：Claude Design export 的 `styles.css` 里色值全部用 OKLCH（感知均匀色彩空间），我们的 SOURCE 用同一心智模型才不会在每轮 bootstrap / adopt 时翻译。

#### 3. Interaction Intent（交互意图）

关键交互节奏（响应延迟预期）、反馈语气（脆 vs 绵）、动效曲线倾向（standard easing / no bounce）、状态转移的视觉强度（克制 vs 戏剧）。

#### 4. Anti-default note（反照抄锚,强制）

**一句话声明：本项目最不该像 FlameTree 默认母语（Warm Ceramic / 暖陶 / 施釉陶）的地方。**

为什么强制：LLM 在生成 UI 时最爱抄默认（Material Design / 大厂常态 / 项目集已有的成功样本）。给它一个明确反例，比给它十个正向字段更能改变它的采样重心——**反例驱动 > schema 驱动**。

**两类合法写法**：

**A. 项目调性明显不同于默认母语** —— 直接列反例：

> 例 1（冷峻工具型）："本项目不该有手作温润感、不该出现陶土/釉面隐喻、不该用焦糖色阴影。应该 sharp / tool-like / 冷光精准。"
>
> 例 2（编辑感）："本项目不该被框架化（规整网格、统一卡片）、不该过度装饰。应该像报纸 editorial：留白即层级，typography 撑骨架。"

**B. 项目就是默认母语的合理继承者** —— 必须写"为什么这次继承是项目本质而不是偷懒默认"：

> 例（音乐播放）："本项目继承 Warm Ceramic，因为音乐应用要营造私人聆听场域，温润材质与情绪克制契合。但应**特别避免**滑向"咖啡馆装饰风"——这是 Warm Ceramic 最常见的失败方向。"

**禁止的写法**：

- ❌ 空白（"暂无"/"待定"）—— 触发 ui-design-router 阻塞
- ❌ "本项目采用 Warm Ceramic" 类纯声明（无反例 = 等于没写）
- ❌ "现代简约" / "克制优雅" 类空泛词（LLM 无法识别为约束）

**ui-design-router / ui-vs / ui-vision-check 在执行前必须读本段**，把段内列的反例升级为本轮硬性扣分项。

## 文档边界（易混淆的三者）

- **BEHAVIOR** = 系统规则（"状态 A 在条件 X 下转移到 B"）
- **user-stories** = 用户叙事（"小明不知道吃什么→打开 App→摇→火锅"），qa/ 子目录存放编译的验证脚本
- **features/** = 工程设计（"随机选择用 Fisher-Yates 算法"）

> User Stories 格式模板：`docs/USER_STORIES_TEMPLATE.md`

## 模块质量标签

在 ROADMAP.md 或架构文档中给各模块标注状态：

- 🟢 稳定（可大刀阔斧）
- 🟡 缺测试（需小心）
- 🔴 债务高（谨慎操作）

## 文档保鲜原则

- FEATURE_CODE_MAP.md 中引用的代码路径必须实际存在，失效路径视为文档腐烂
- 代码文件新增/删除/重命名后，检查文档索引是否需要同步
- user-stories/qa/ 中的 curl 命令返回 404 或断言失败 → 故事过时，需从 story 重新编译 qa
