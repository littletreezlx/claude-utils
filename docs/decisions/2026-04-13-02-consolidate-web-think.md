# 合并 /feat-discuss-web-gemini 进 /web-think

- **Date**: 2026-04-13
- **Status**: Accepted
- **Scope**: commands/ (删除 feat-discuss-web-gemini, 增强 web-think Phase 3)

## 1. 问题 (What went wrong)

`/web-think` 和 `/feat-discuss-web-gemini` 两个命令同时存在，通道和 Gemini 侧预设完全一致（空白窗口 + 自包含 Prompt），用户难以区分用哪个。对比三个 Web 转发命令：

| 命令 | Gemini 侧预设 | Prompt 特点 |
|------|--------------|------------|
| `/web-think` | 空白窗口 | 自包含（通用话题） |
| `/feat-discuss-web-gemini` | **空白窗口（相同）** | 自包含 + 强制出 Spec |
| `/web-gem-project` | 已建 Gem | 只发 delta |

`feat-discuss-web-gemini` 的独特价值只剩"强制产出 Spec + 单文件 checklist"这一条硬轨道。

## 2. 讨论过程 (How we thought about it)

Founder 直接问："这俩什么关系？" → 进一步追问："是不是没必要存在？"

初步倾向：保留作为硬轨道，理由是 AI-Only 模式下"文档即约束"，柔性判断可能让 AI 偷懒不落库。

Founder 反驳："不要低估 AI 的智能。"

## 3. 决策 (What we decided)

**移除 `/feat-discuss-web-gemini`**，在 `/web-think` Phase 3 补一句：

> 如涉及新功能设计：必须产出 `docs/features/xxx.md` + 单文件粒度 checklist（`- [ ]`），作为后续 coding 的 Source of Truth

## 4. 为什么不选其他方案

- **保留双命令**：Gemini 侧预设相同时两个命令本质上是同一工具，冗余违反"一类问题一个命令"原则
- **保留为硬轨道**：Founder 明确表示不要低估 AI 的智能。AI-Only 模式下信任 AI 在 Phase 3 自行判断"这个讨论是否涉及功能设计"完全可行
- **合并到 `/web-gem-project`**：后者针对已建 Gem 场景（只发 delta），与 feat-discuss 的"自包含 Prompt"冲突

## 5. 影响范围

- 删除 `commands/feat-discuss-web-gemini.md`
- `commands/README.md`：索引和目录树替换为 `/web-think`
- `commands/web-think.md`：Phase 3 增加功能设计硬落库条款
- `skills/feat-discuss-local-gemini/SKILL.md`：分流提示改为 `/web-think`
- `skills/feat-discuss-local-gemini/references/design-decisions.md`：更新 v0.5.0 结构溯源表述
- `memory/feedback_web_gemini_output.md`：更新命令名引用

## 6. 验证凭证

[验证凭证: 运行 `grep -rn "feat-discuss-web-gemini" ~/.claude/` → 除本决策记录自身外无其他匹配]
