# feat-discuss-local-gemini 重命名为 think-gem-project

- **Date**: 2026-04-13
- **Status**: Accepted
- **Scope**: skill:feat-discuss-local-gemini → think-gem-project

## 1. 问题 (What went wrong)

`feat-discuss-local-gemini` 命名与其他 Gemini 协作命令/skill 不成体系：

| 维度 | 通用话题 | 项目话题 |
|------|---------|---------|
| Local API（自动） | `think` skill | **feat-discuss-local-gemini** ← 名字不统一 |
| Web（手动） | `/web-think` | `/web-gem-project` |

"feat-discuss" 还暗示只讨论 feature，但实际支持 product/design/game-product/game-design 四种项目级角色。

## 2. 讨论过程 (How we thought about it)

紧接决策记录 02（合并 `/feat-discuss-web-gemini` 到 `/web-think`）后，Founder 问"feat-discuss-local-gemini 有必要吗？都走 /think？"

分析下来 skill 的独特价值是**多脚本路由**（FlameTree 与 Game 项目用不同底座 prompt，避免哲学交叉污染）+ Handshake + Feature Brief 落库，不能简单合并到 /think。但命名确实需要对齐。

Founder 提议："改名成 think-gem-project 吧？"——形成清晰的 `think / think-gem-project / web-think / web-gem-project` 四格体系。

## 3. 决策 (What we decided)

重命名 `feat-discuss-local-gemini` → `think-gem-project`，与 Web 侧的 `web-gem-project` 形成对称。命名体系：

- `think` = 通用 Local API（方法论/哲学，无 Handshake）
- `think-gem-project` = 项目 Local API（产品/设计/游戏，有 Handshake + Feature Brief）
- `/web-think` = 通用 Web 手动（自包含 Prompt）
- `/web-gem-project` = 项目 Web 手动（增量 Prompt 给已建 Gem）

## 4. 为什么不选其他方案

- **合并进 /think**：会让 /think 失去"轻量"定位，且多脚本路由（`game-product.mjs` vs `product.mjs`）的硬技术约束无法优雅整合
- **保留旧名 `feat-discuss-local-gemini`**：命名不对齐，且 "feat-discuss" 窄化了实际覆盖面（design / game-*）
- **用 `local-gem-project`**：失去与 `think` / `web-think` 的同族感

## 5. 影响范围

- 目录：`skills/feat-discuss-local-gemini/` → `skills/think-gem-project/`
- `SKILL.md` frontmatter：`name` 字段更新，description 改为聚焦项目级讨论
- 引用更新：`CLAUDE.md`、`commands/README.md`、`skills/README.md`、`skills/think/SKILL.md`、`commands/prd-to-doc.md`、`references/design-decisions.md` 标题
- **历史文档不改**：`docs/decisions/2026-04-13-02-*`、`memory/purity-bias-lesson.md`、本 skill 内 references 中引用旧名的历史决策段落保持原样（历史记录不追溯）

## 6. 验证凭证

[验证凭证: 运行 `grep -rn "feat-discuss-local-gemini" ~/.claude/ --include="*.md"` → 仅剩历史决策 2026-04-13-02、memory 的 purity-bias-lesson、design-decisions.md 中的历史章节，所有活跃引用已切换]
