# 2026-04-24-02: Command → Skill 迁移候选审查

## 审查范围

全部 27 个 command(`~/.claude/commands/*.md` 除 `README.md` 和 `CLAUDE.md`)

> 本次会话刚完成 `/feat-done` 和 `/init-design-brief` 的 skill 迁移(commit `04c8bae`)。本报告对剩余 27 个逐一判断,**不执行迁移** — Founder 根据报告逐条决策。

## 判断框架(沿用本次会话已确立)

| 信号 | 判定 |
|------|------|
| 用户极少主动调用,Claude 能从对话识别意图 | ✅ 转 skill |
| 触发条件明确、上下文可自动判断 | ✅ 转 skill |
| 用户经常显式 `/xxx` 调用、必须传参数 | ❌ 保留 command |
| 破坏性 / 决策性 / 一次性 | ❌ 保留 command |
| DAG 型(`batchcc task-xxx` 模式) | ❌ 保留 command |
| Founder 价值观: 频率不是衡量标准, **触发是否可从对话自动识别** 才是 | — |

---

## 分类总览

- ✅ **建议转 skill** (2 个): `learn-new-project`, `test-run`
- ⚠️ **模糊地带** (5 个): `claudemd`, `doc-clean`, `inbox`, `test-audit`, `test-verify`
- ❌ **保留 command** (20 个):
  - DAG 7 个: `comprehensive-health-check`, `doc-quality-review`, `doc-update-context`, `refactor-module`, `refactor-project`, `test-plan`, `todo-huge-task`
  - UI 闭环 4 个: `ui-bootstrap`, `ui-vs`, `ui-adopt`, `init-ui-showcase`
  - Web 跨工具 2 个: `web-think`, `web-gem-project`
  - 必传参数 7 个: `create-e2e-test`, `learn-article`, `note`, `prd-to-doc`, `refactor`, `techdoc`, `push-feishu-project`

合计: 2 + 5 + 20 = 27 ✓

---

## 逐命令分析

### ✅ 建议转 skill 的 (2 个)

#### `/learn-new-project`

- **现状 description**: "你将分析陌生项目代码,快速建立对业务、架构与改进方向的认知,生成结构化中文报告"
- **触发条件**: 用户进入陌生项目,Claude 可从对话/上下文识别(无 CLAUDE.md / 用户明说"我刚 clone 了一个项目"/"帮我熟悉下代码库"/"分析下这个项目")
- **为什么建议转**:
  - 用户几乎不会记得"哦我可以用 `/learn-new-project`",更可能直接问"这是个什么项目"
  - Claude 当前默认行为已经会在陌生项目里主动探索代码,但缺一个**输出结构化报告**的强制约束 — skill 可以补上
  - 触发短语很容易识别且不易误触发(必须有"陌生项目"信号)
- **建议 skill description**(英文,含触发短语):
  ```yaml
  description: >
    This skill should be used when the user is exploring an unfamiliar codebase,
    when the user says "分析这个项目", "帮我熟悉代码库", "this is a new project",
    "what does this project do", "explain this codebase", or when the project lacks
    CLAUDE.md and the user is starting work on it. Generates a structured Chinese
    report covering project overview, business flows, core components, and improvement
    suggestions. Marks low-confidence assumptions explicitly.
  ```
- **合并机会**: 无。`claudemd` 是生成 CLAUDE.md(可执行约束),`learn-new-project` 是输出分析报告(认知建立),目标不同,不应合并。

#### `/test-run`

- **现状 description**: "测试运行与修复 ultrathink"
- **现状实质**: 已经是 thin wrapper —— `## 执行` 段只写"调用 `test-workflow` skill,传入 `$ARGUMENTS` 作为测试范围"
- **触发条件**: `test-workflow` skill 已经声明触发条件:"代码已修改需要测试验证"/"用户说'run tests'/'check if it works'/'verify the fix'" — 完全覆盖 `/test-run` 的使用场景
- **为什么建议转**:
  - 命令本体只有 4 行有效内容,纯转发
  - skill 触发已经覆盖,保留 command 反而让用户/Claude 困惑"该用哪个入口"
  - 删 command 不损失功能(skill 还在),减一个噪音入口
- **建议处理**: **直接删除 `commands/test-run.md`**(skill 已存在不需要再建)
- **合并机会**: 已有 `test-workflow` skill,无需新建

---

### ⚠️ 模糊地带的 (5 个)

#### `/claudemd`

- **理由 — 偏 skill**:
  - 部分场景触发可识别:进入项目无 CLAUDE.md → Claude 应主动建议生成
  - 默认无参数模式("无 CLAUDE.md 则生成,有则增量更新")是典型 skill 触发场景
- **理由 — 偏 command**:
  - 有三种模式参数: `init`(强制覆盖) / `audit`(深度审计) / `$ARGUMENTS`(定向更新)
  - `init` 是破坏性操作 — 覆盖现有 CLAUDE.md,需用户主动决策
  - `audit` 模式输出报告等用户确认 — 是显式触发的"审视性动作"
- **倾向**: **偏保留 command**,但建议拆分:
  - 自动场景(无 CLAUDE.md → 建议生成 + 增量更新)→ 独立 skill,如 `claudemd-maintainer`
  - 显式动作(`init` / `audit` / 定向更新)→ 保留 `/claudemd` command
- **需要 Founder 决策**: 是否值得拆分?如果觉得拆了反而碎,就整体保留 command

#### `/doc-clean`

- **理由 — 偏 skill**:
  - 触发短语明确:"清理一下文档"/"归档临时文件"/"根目录乱了"
  - 用户极少记得 `/doc-clean` 这个名字
- **理由 — 偏 command**:
  - 触发频率极低(项目根目录通常不会频繁堆临时文件)
  - 已经有 `inbox` skill 在处理"自动归档"语义 — 再加一个 skill 触发条件容易混
  - 操作目标明确(根目录扫描),用户主动触发更可控
- **倾向**: **偏保留 command**。低频且用户能记住的"批量清理"动作,主动触发更安全
- **需要 Founder 决策**: 如果 Founder 觉得"我从来想不起来 `/doc-clean`",再转 skill

#### `/inbox`

- **理由 — 偏 skill**:
  - 触发短语明确:"整理 inbox"/"归档收件箱"/"处理待办文档"
  - 用户极少记得 `/inbox` 这个名字
- **理由 — 偏 command**:
  - 路径硬编码到 `~/LittleTree_Projects/my-forest/`,只在该知识库下有意义
  - 与代码项目工作流无关,跨项目噪音风险低
  - 中置信度场景需要等用户确认("📋 文件名.md — 检测到多个可能归属"),自动触发会增加交互成本
- **倾向**: **偏保留 command**。仅在特定知识库下使用 + 需用户在歧义时确认,主动触发更清晰
- **需要 Founder 决策**: 如果 Founder 觉得"我经常想整理 inbox 但忘记命令名",可转 skill,但 description 必须严格限定"only when working in `~/LittleTree_Projects/my-forest/`"

#### `/test-audit`

- **理由 — 偏 skill**:
  - 触发场景可识别:"测试跑不起来"/"没有测试命令"/"测试基础设施有问题"
  - 用户不会记得有这个命令
- **理由 — 偏 command**:
  - 频率极低(测试基础设施一般在项目初期建一次后就稳定)
  - 是"审计 + 修复"动作,有破坏性(会改 package.json / 测试配置)
  - 自动触发风险:Claude 可能在用户只是"跑个测试看看"时误触发整套基础设施重建
- **倾向**: **偏保留 command**。低频 + 半破坏性,显式触发更安全
- **需要 Founder 决策**: 如果想转 skill,description 要严格写"仅在用户**明说**测试基础设施有问题时触发,不在测试失败时自动触发"避免误触发

#### `/test-verify`

- **理由 — 偏 skill**:
  - 已经是 thin wrapper(调 `test-verify` skill)
  - skill 本身已声明触发条件
- **理由 — 偏 command**:
  - 用户可能想**显式手动**对某文件做红队验证(`/test-verify path/to/service.dart`)
  - 带路径参数,显式入口更直接
- **倾向**: **偏保留 command**。和 `/test-run` 区别在于:`/test-verify` 经常带显式路径参数(单文件 / 模块)且是用户主动想"对这块做对抗验证",显式入口价值更大
- **需要 Founder 决策**: 如果 skill 触发已经覆盖了所有想触发场景,可以一并删

---

### ❌ 保留 command 的 (20 个,简略一行理由)

#### DAG 型 (7 个,本轮不挑战)
- `/comprehensive-health-check`: DAG,需 `batchcc` 显式起点
- `/doc-quality-review`: DAG,需 `batchcc` 显式起点
- `/doc-update-context`: DAG(已读 — Phase 0/0.5 + 串行 STAGE),需 `batchcc` 显式起点
- `/refactor-module`: DAG,需 `batchcc` 显式起点
- `/refactor-project`: DAG,需 `batchcc` 显式起点
- `/test-plan`: DAG,需 `batchcc` 显式起点
- `/todo-huge-task`: DAG,需 `batchcc` 显式起点

#### UI 闭环 (4 个,本轮已决策保留)
- `/ui-bootstrap`: 一次性破坏性接入(2026-04-24 已决策保留)
- `/ui-vs`: 评审需用户指出 bundle 路径(2026-04-24 已决策保留)
- `/ui-adopt`: 决策性动作 — 采纳会改 SOURCES + 归档(2026-04-24 已决策保留)
- `/init-ui-showcase`: 新项目一次性初始化(2026-04-24 已决策保留)

#### Web 跨工具 (2 个,本轮已决策保留)
- `/web-think`: 产物是给 Founder 复制的 prompt,需用户主动跨工具协作
- `/web-gem-project`: 同上

#### 必传参数(7 个)
- `/create-e2e-test`: 必须传"目标功能模块或页面名称"
- `/learn-article`: 必须传"文章内容或 URL"
- `/note`: 必须传"内容"(`/note <内容>`)
- `/prd-to-doc`: 必须传"PRD 文档路径或内容"
- `/refactor`: 文件/类级别重构,通常带 $ARGUMENTS,且**用户经常主动调用**(已在判断框架明确)
- `/techdoc`: 必须传"主题"(如 `/techdoc "用户管理系统统一认证方案"`)
- `/push-feishu-project`: 破坏性外部操作(创建飞书工作项 + 推 wiki 文档),必须用户主动触发

---

## 推荐迁移顺序

如果 Founder 采纳建议,按风险从低到高:

1. **Step 1**: 删除 `/test-run` command(已是 wrapper,test-workflow skill 完整覆盖)— **零风险**
2. **Step 2**: 把 `/learn-new-project` 转 skill — **中风险**(触发条件需仔细写,避免在用户只是问个项目细节时误生成全套报告)
3. **Step 3**(可选): 把 `claudemd` 拆分(自动场景转 skill,显式 init/audit 保留 command)— **较高风险**,跨度大,需先看效果再决定

模糊地带的其他 4 个(`doc-clean` / `inbox` / `test-audit` / `test-verify`)建议**先观察使用模式**,再决定是否转。

---

## 值得警惕的风险

### 1. Skill 触发短语写太宽 → 误触发污染主流程

**示例**: `/learn-new-project` 转 skill,description 写成"when user asks about a project" — 用户只是问"这个项目用了什么状态管理库",Claude 触发整套结构化报告生成,污染对话。

**对策**: description 必须包含**明确的"陌生项目"信号词**(如 "starting work on""不熟悉""刚 clone"),并在 SKILL.md 里再写一段"DO NOT trigger when..."否定清单。

### 2. Command 和 Skill 同名共存 → 入口分裂

**示例**: 当前 `test-verify` command 和 `test-verify` skill 同时存在(`commands/test-verify.md` 是 thin wrapper,`skills/test-verify/SKILL.md` 是实质实现)。Claude 看到两个同名入口可能困惑。

**对策**: 任何 command 转 skill 后,**必须删除 command 文件**(`commands/CLAUDE.md` § Command → Skill 迁移已声明此规则,但要严格执行)。`test-verify` 当前的"command 作为显式入口 + skill 作为自动触发"模式只有在确认 skill 触发不够覆盖时才合理。

### 3. 把"低频 = 价值低"误解为"低频 = 应该删"

Founder 价值观明确:**频率不是衡量标准**(memory `feedback_skill_value_not_frequency.md`)。低频高价值的 `/test-audit` / `/doc-clean` 即便很少用,也应保留 — 转 skill 的理由必须是"触发可识别",不是"减少 command 数量"。

### 4. DAG 命令的"显式起点"特性不可压缩

DAG 命令的 `## STAGE ##` `## TASK ##` 入口需要 `batchcc` 主动消费,转 skill 会破坏这个执行模型。本报告对所有 DAG 直接判 ❌,**不要后续审查时翻案**。

### 5. UI 闭环 4 个命令本轮已决策保留 → 别再质疑

`/ui-bootstrap` `/ui-vs` `/ui-adopt` `/init-ui-showcase` 是本会话刚定下的设计闭环骨架,各自有不可替代的破坏性/决策性/一次性特征。短期内重新评估转 skill 会破坏闭环稳定性。

---

## 附:本次审查的元观察

- 27 个 command 中,真正"thin wrapper"只有 2 个(`test-run` / `test-verify`)→ 说明 commands 整体仍有独立价值,不是 skill 的简单别名
- DAG 命令占 7/27 (26%),反映项目对**显式无人值守工作流**的强需求 — 这部分 command 不会被 skill 替代
- UI 闭环命令占 4/27 (15%),都是 2026-04-24 本会话刚迁出的"非 skill 部分" — 体系已稳定
- 真正适合转 skill 的只有 1-2 个,符合"二八定律":**大部分 command 各司其职,少数适合 AI 自动接管**

---

## 实际执行记录

### 2026-04-24 当天落地

报告生成后,Founder 当场决策:**采纳 Step 1 — 删除 `/test-run` command**(零风险,test-workflow skill 完整覆盖)。

**操作**:
1. `rm ~/.claude/commands/test-run.md` — 删除 thin wrapper
2. 更新 `~/.claude/commands/README.md`:
   - 快速选择树里"运行与修复"项改指向 `test-workflow` skill 自动触发
   - 测试工程命令表移除 `/test-run` 行,追加说明
   - 命令总数 27 → 26
   - "矫正坏状态工作流"第 2 步从 `/test-run` 改为 `test-workflow` skill

**未执行**:
- Step 2 (`/learn-new-project` 转 skill)— 等 Founder 确认触发短语后再做
- Step 3 (`claudemd` 拆分)— 风险较高,先观察
- 模糊地带 4 个保持现状

### 后续追踪

如果 Founder 后续采纳更多迁移建议,应在本报告或新的决策记录中追加,保持决策可追溯。
