# 2026-04-24-01: `/init-design-brief` 和 `/feat-done` 迁移为 skill

## 遇到什么问题

**痛点 1(用户触发):** Founder 经常直接对 Claude Code 说"改一下 X 页的 Y",忘记先跑 `/init-design-brief` 派生 Brief 去 Claude Design 里迭代。结果:
- 小改动和大改动一视同仁,Founder 搞不清什么时候该走闭环什么时候不用
- 直接在代码里改视觉 → 设计体系漂移,下次 Claude Design re-onboard 时会发现代码跟内部 design system 对不上
- 现有的 Design-First Gate 只在 `/feat-done` 里查(提交时),**时机太晚** — 代码已经写完才发现该走闭环

**痛点 2(命令冗余):** `/feat-done` 命令形式使得 Founder 每次功能完成都要记得调用它。但 CLAUDE.md 已经明确它是"自动触发":速查表写"功能完成 | 自动调用 `/feat-done`",自动触发规则表也列出。**命令和自动触发是矛盾的** — 要么手动,要么自动,不能既要又要。

## 讨论过程

会话内递进展开:

1. Founder 先问"init-design-brief 这个是要改动新的 UI 逻辑的时候用吗?" — Claude 解释触发时机
2. Founder 说"那我感觉是不是写成 skill 啊?" — 第一次提出转 skill
3. Claude 给了两边理由,倾向保留为 command(因为 Brief 是"派生交付物"需要用户显式控制)
4. Founder 反驳:"我感觉容易会忘,就是我可能经常想要改动下哪里的 UI 设计可能直接和 CLAUDE code 说了,不过不评估一下这种小改动是否需要再找 claude design?"
5. Claude 意识到**真正的痛点不是 Brief 生成,而是缺一个"改 UI 前的前置闸门"** — 反转方案:应该造一个新 skill 做**分类**(小改/大改),大改时才派生 Brief
6. Founder:"我感觉直接都进 skill 吧"(愿意把 Brief 生成也合并到 skill)
7. 接着 Founder 补充:"还有我感觉 feat-done.md 也可以作为 skill" — 基于同样的"自动触发更自然"逻辑
8. Claude 列方案:两个 skill(`ui-design-router` 吸收原 init-design-brief + 新增分类逻辑;`feat-done` 直接迁移),Founder 说"执行"

## 为什么这么改

**`ui-design-router` skill 替代 `/init-design-brief`**:

新 skill 比原命令多做两件事,因此价值更高:

1. **前置分类**(原命令没有):对照豁免白名单和触发阈值,判断本次改动是小改(直做)还是大改(派生 Brief),**解决"忘了该不该走闭环"这个核心痛点**
2. **EXTERNAL_REFS 守门**(原命令有但弱):未绑定 Claude Design 时自动拦下提示 `/ui-bootstrap`
3. **自动触发**:用户说"改 X UI" 立即介入,不依赖 Founder 记忆命令名
4. **Brief 派生**(原命令功能):大改路径里保留,模板不变

**`feat-done` skill 替代 `/feat-done`**:

- 触发条件"功能完成"可以从对话上下文识别(跨文件改动 + 测试通过 + 用户示意),不需要命令形式
- CLAUDE.md 已经用自动触发的文案描述它,保留命令形式是名义上的冗余
- 编排逻辑不变(Gate → 文档同步 → 静态分析 → 触发 git-workflow)
- **feat-done 的 Step 0 Gate 保留**:skill 是开工前的闸门(ui-design-router),feat-done 是提交前的复核,两道防线不冗余 — 用户可能绕过开工闸门(直接贴代码让 Claude 改),提交时还得查一次"基于哪个 bundle"

**保留为 command 的 UI 命令不变**(`/ui-bootstrap` / `/ui-vs` / `/ui-adopt` / `/init-ui-showcase`):
- `/ui-bootstrap`:一次性破坏性动作,必须用户主动触发
- `/ui-vs`:需要用户指出 export bundle 路径
- `/ui-adopt`:决策性动作 — 采纳后会改 SOURCES + 归档,不能自动做
- `/init-ui-showcase`:新项目一次性

判断标准是 `~/.claude/skills/README.md` § "Command → Skill 迁移策略":可以自动判断的 → skill,需要用户决策/破坏性 → command。

## 为什么不选其他方案

### 选项 A:保留 `/init-design-brief` 为 command,加一个单独的"改 UI 前分类器" skill

**否决原因**:分类成功后大改路径还是要触发 Brief 生成,"分类 + Brief 生成"放到两个工具里用户体验割裂 — 分类器说"这是大改",然后又要用户手动 `/init-design-brief`。合二为一更顺。

### 选项 B:让 Claude Code 在每次改代码前都自问"这需要走闭环吗"

**否决原因**:没有显式 skill 容易被 AI 模型"当下决策"忽略。Skill 有 description 触发短语,是**机器可执行的规则**,不是行为建议。

### 选项 C:只转 `/init-design-brief`,`/feat-done` 保留为 command

**否决原因**:两个命令的"可以自动触发"的属性是同质的。保留 `/feat-done` 为命令等于在两个表述(速查表说"自动调用"、命令定义说"即时命令")之间制造冲突。AI-Only 开发下,文档就是约束,矛盾的约束是 bug。

### 选项 D:把 `/ui-vs` 和 `/ui-adopt` 也转为 skill(全都进 skill)

**否决原因**:两者的触发需要用户携带**具体产物**(bundle 路径)或做**决策**(这一轮要采纳),不是可以从对话自动识别的"意图"。强制自动化会导致误触发。

## 影响半径

- `~/.claude/skills/ui-design-router/SKILL.md`(新建)
- `~/.claude/skills/ui-design-router/references/brief-template.md`(新建)
- `~/.claude/skills/feat-done/SKILL.md`(新建)
- `~/.claude/commands/init-design-brief.md`(删除)
- `~/.claude/commands/feat-done.md`(删除)
- `~/.claude/CLAUDE.md`(速查表 + 自动触发规则表调整)
- `~/.claude/commands/README.md`(功能开发段落 / UI 工程段落 / 典型迭代示例 / 命令总数 29 → 27)
- `~/.claude/skills/README.md`(新增两条 skill 登记)
- `~/.claude/guides/doc-structure.md`(4 处引用更新)
- 两份 memory 文件(`reference_claude_design_loop_design.md` 和 `project_flutter_claude_design_bootstrap_pending.md`)引用更新

## 验证凭证

```
[验证凭证: N/A - 规则文档调整,非业务代码。实际有效性要等 Founder 下次说"改一下 X 页的 Y" 时观察 ui-design-router 是否自动介入并分类正确]
```

本次修改**需要下一轮对话实战验证** — 预期行为:

1. Founder 在某个 Flutter 项目里说"我想改一下 search 页的 empty 态"
2. `ui-design-router` skill 自动触发
3. 判定为小改动(既有组件 empty 态) → 直接实施,不派生 Brief
4. 另一场景:"我想把整个 App 换个感觉,更暖一点" → 判定为大改 → 检查 EXTERNAL_REFS → 派生 Δ Brief 到 `docs/design/DESIGN_BRIEF.md`

如果 skill 不触发 / 触发但分类错误 / 触发但不生成 Brief → 反映在后续会话,回来调整 SKILL.md 的 description 或分类规则。
