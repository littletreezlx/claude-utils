---
name: Plugin evaluation decisions (2026-04-18)
description: claude-plugins-official marketplace 插件的评估结论——留哪些、删哪些、为什么。防止下次看到 marketplace 冲动重装。
type: project
originSessionId: ace81150-7675-4c05-a10d-e53d6b0647be
---
# Marketplace 插件决策(2026-04-18 一次性评估)

## 当前保留(6 个)

| 插件 | 类型 | 留的理由 |
|---|---|---|
| `superpowers` | skill 合集 | `brainstorming` / `subagent-driven-development` / `TDD` / `executing-plans` 等核心 skill 来源,有 5.0.7 的 Stop hook |
| `frontend-design` | skill | 填补"前端组件/页面生成"能力,本地无对等 skill |
| `context7` | MCP | 拉第三方库最新文档,不抢触发 |
| `playwright` | MCP | E2E 浏览器驱动,不抢触发 |
| `code-review` | slash command | `/code-review:code-review` 手动触发,不抢路由 |
| `ralph-loop` | slash command + Stop hook | 完成驱动的迭代循环。**hook 只在 `.claude/ralph-loop.local.md` 存在时才拦截 exit,session_id 隔离,日常无影响**。用时必须配 `--max-iterations 20`,否则违反"连续 3 次失败停止"铁律 |

## 已评估并删除(4 个)——下次别再装

**Why**: 每个都和本地体系冲突,不是因为插件本身差。
**How to apply**: 下次在 `/plugin` marketplace 里看到这 4 个名字,直接跳过,不要手痒。

| 插件 | 删除理由 |
|---|---|
| `commit-commands` | `commit-push-pr` 一键推送违反"push 才需确认"的 CLAUDE.md 铁律;`commit` 与本地 `git-workflow` skill 重复 |
| `skill-creator`(官方版) | 和本地 `~/.claude/skills/skill-creator/` 触发词完全重叠(都是 "create skill / improve skill"),Claude 纠结该用哪个。本地版有"踩坑点章节""SKILL.md ≤100 行""注册到 skills/README.md"等体系特有约定,官方 480 行评测工具链目前用不上 |
| `code-simplifier` | subagent 描述 "Focuses on recently modified code" 会 push 主 Claude 在 `feat-done` 流水线里调它 → 测试通过后又 simplify → 重测 → 提交,打乱自动化节奏。更坏:subagent 独立进程改完代码,主会话验证凭证测的是改前版本,造成三位一体裂缝。和本地 `code-quality` skill 分工不清 |
| `claude-md-management` | 官方 `claude-md-improver` skill 用通用 A-F 评分表,侧重"commands 是否齐全"的结构性检查。本地 `/claudemd audit` 有独有的 Means-as-End Detection(机制型 vs 结果型规则)、Deadlock Detection、删除测试——来自"手段≠目的"铁律。官方 skill 会自动触发抢走 `/claudemd` 的路由 |

## 规则(给未来的 AI)

1. **Skill 类插件最危险**:会自动触发,可能抢本地 skill 的路由 → 装前必须对比 description 触发词重叠度
2. **Subagent 类插件看 description 的推销语**:"proactively / focuses on recently modified" 这类词会让主 Claude 在自动化流水线里主动调,可能打乱 feat-done/test-workflow 节奏
3. **MCP / slash command 最安全**:MCP 只在需要工具时被调用,slash command 必须用户显式输入,都不抢路由
4. **Hook 类插件要读 `hooks/hooks.json` + 脚本源码**,确认激活条件(如 ralph 的 state file gating),不要盲目担心
