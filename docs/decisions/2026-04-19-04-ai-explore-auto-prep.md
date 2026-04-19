# 2026-04-19-04 ai-explore：prep-cyborg-env 从"前置假设"改为"Step 0 主动调用"

## 背景

v4.0 (2026-04-18) 发布后，Founder 在 flametree_pick 项目首次跑 `/ai-explore`，触发如下断链：

- `prep-cyborg-env` 在 SKILL.md 前置条件里列为 "✅ 已执行"
- 但 skill 并不真的主动调用它——只是跑 Step 0 契约检查，发现 Debug Server 不可达就退出报错
- Founder 的反应：「@/Users/zhanglingxiao/.claude/skills/ai-explore/ 是不是有问题，这应该是自动启动准备好环境的啊」

换句话说：SKILL 把前置检查写成了"假设别人已经做过"，这在 AI-Only 协作模式下是伪约束——没有"别人"会去做。

## 讨论过程

### 问题本质

这是一个典型的 "假设 vs 责任" 错位：
- SKILL 作者（我）当时认为 "列为前置条件就是规则"
- 但 AI-Only 模式下，规则不会被"记得"——必须被执行步骤编码
- 映射到全局 CLAUDE.md 的原则：「文档即约束」「工作流中不应包含不会执行的步骤」

### 方案对比

**Option A（采用）：Step 0 开头主动调用 prep-cyborg-env**
- 优点：最简单，符合 Skill tool 可嵌套调用的原生能力；失败可追溯
- 缺点：prep-cyborg-env 自己的执行耗时（冷启动时完整 app build 几分钟）会计入 ai-explore 耗时——但这是 inherent 成本，不是设计缺陷

**Option B：把 prep 逻辑内联到 ai-explore Step 0**
- 优点：少一次 skill 调用开销
- 缺点：违反 DRY，prep-cyborg-env 已经是 ai-qa-stories 等其他 skill 的共享前置。复制粘贴维护灾难。

**Option C：让 Claude Code harness 在 skill 触发时自动注入 prep**
- 优点：最纯粹
- 缺点：需要改 harness，scope 远超 skill 自身；且 prep 不是所有 ai-explore 调用都需要（已经 warm 的情况不该重复跑）

**选 A** —— 最小侵入、符合 AI-Only 原则、利用 Skill tool 原生能力。

### Step 0 拆分

顺带把原 Step 0（DOM/reset/interactiveOnly 契约检查）拆成 0a/0b：

- **0a**：环境就绪（探测 → 不可达就调 prep-cyborg-env → 再次轮询 → 30s 仍失败则明确退出）
- **0b**：契约健康（原有 DOM/reset/interactiveOnly 探测）

**关键语义**：0a 失败 ≠ 静默 fallback 到旧行为。skill 必须明确报告"Simulator 未启动 / 无 prep-env.sh"等原因，不能蒙混着往下跑——脏状态下三角校验给出的结论会污染 D 级错误预算。

### prep-env.sh 的顺序 bug（本次会话发现）

flametree_pick 的 `scripts/prep-env.sh` 有独立 bug——它在 Step 4 试图 seed 数据，但那时 App 还没启动（Debug Server 不可达），seed 必然失败。需要项目侧修：seed 应在 start-dev 之后。

**此 bug 归项目维护责任**，已写入 `TODO.md`（T 系列契约任务同层）。不在本决策 scope 内——本决策只负责 skill 编排。

## 落地内容

### 1. `~/.claude/skills/ai-explore/SKILL.md`

- 前置条件 #1：从 "✅ prep-cyborg-env 已执行" 改为 "Step 0 自动检测 + 主动调用"
- 新增 "Skill 编排原则" 声明段：前置 skill 由本 skill 主动调用，不依赖人类记忆
- Step 0 拆 0a/0b
- 变更历史追加 4.0.1 条目

### 2. 本决策记录

就是这份文件。

## 为什么不选其他方案

- **不选 "让 prep-cyborg-env 自己变成全局 SessionStart hook"**：不是所有会话都需要跑探索；hook 会过度触发。
- **不选 "写个外层编排 skill"**：增加一层间接调用，认知成本高于收益。ai-explore 本身就是流程 skill，把 prep 内联到 Step 0 是最自然的。
- **不选 "在 ai-explore Step 0 手写 prep 逻辑（kill/seed/start）"**：会让 prep-cyborg-env 失去存在意义，违反 DRY。

## 后续观察点

1. 首次在真实项目（flametree_pick）验证 auto-prep 是否顺利——**本决策已触发实际修复，但修复后的 skill 尚未在干净环境里跑过一次完整 0a → 0b → Step 1-5**。下次 `/ai-explore` 时观察。
2. 如果 prep-cyborg-env 内部报错（如 prep-env.sh 的 seed 顺序 bug），ai-explore 能否给出清晰的路由信息？当前错误消息是"30s 仍失败"，可能信息不足。——如被证实为问题，再开 4.0.2 修。

## 关联

- v4.0 原决策：`2026-04-18-05-ai-explore-v4-trust-framework.md`
- 同批发现的项目侧 bug：flametree_pick `TODO.md`（B1/B2/T1-T4）
