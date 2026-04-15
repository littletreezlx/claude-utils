# 废弃 /create-page-doc 命令

**日期**: 2026-04-15
**类型**: Command 废弃

## 问题

`commands/create-page-doc.md` 为指定模块生成双文档体系（README.md 功能文档 + TECHNICAL.md 技术文档），长期未被使用。Founder 提出疑问：AI-Only 模式下还需要这种模块级文档吗？

## 讨论过程

**第一轮**：保留还是废弃？

按全局记忆 `feedback_skill_value_not_frequency`——"最近没用"不是废弃理由。初判：保留，因为它解决的问题域（模块级双文档）与 `techdoc` / `ui-spec` 不重复。

**第二轮**：TECHNICAL.md 在 AI-Only 模式下的价值？

- AI 直接读代码几秒就能还原架构，TECHNICAL.md 变成滞后的副本
- 维护成本 = 每次重构都要同步，违反"务实主义"铁律
- 结论：TECHNICAL.md 应废弃

**第三轮**：README.md（功能导向）还有必要吗？

- 代码 + 命名 + 头部注释足以告诉 AI "做什么"
- 产品意图 / 用户场景 / 存在理由 → 已由 `docs/features/*.md` 和 `docs/PRODUCT_SOUL.md` 承载
- 模块级 README 要么重复代码（冗余），要么重复 features/（错位）
- 它是人类团队"每个目录放 README 方便同事"的习惯遗留，不适合 AI-Only

**结论**：整个命令废弃。

## 决策

- 删除 `commands/create-page-doc.md`
- 删除 `commands/templates/docs/`（README_TEMPLATE.md、TECHNICAL_TEMPLATE.md，仅被此命令引用）
- 清理 `commands/README.md` / `commands/CLAUDE.md` / `commands/templates/README.md` 中的引用

## 为什么不选其他方案

- **降级为单文档（只生成 README）**：驳回。功能意图已有 features/ 承载，模块级 README 仍是冗余
- **让 `techdoc` 吸收场景**：不需要。`techdoc` 是工作项目用的技术文档撰写，场景不同，无需承接
- **保留作低频工具**：驳回。它不仅低频，而且**产出与 AI-Only 文档体系重复**。低频 ≠ 低价值的准则前提是"价值独立存在"，此处价值已被 features/ 替代

## 元原则

AI-Only 模式下，**文档应按领域组织（features/architecture/stories），而非按目录组织**。模块级文档是人类团队协作的产物；AI 读代码不需要导航性的 README，它需要的是代码里不存在的产品意图——而那应该在 features/ 里。

Co-Authored-By: Founder (zhanglingxiao)
