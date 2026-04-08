---
name: principle-reification
description: AI 协作中的 Principle Reification（原则实体化）陷阱及其防御机制
type: feedback
---

## 核心教训

当基于产品原则否决一个方案时，必须追问：这个原则关注的是**结果**（用户决策负担变少）还是**机制**（App 设置项变少）？漂亮的类比不是论证。"徕卡不会这样做"不等于"我们不应该这样做"。

## 根因链

1. **文档表述模糊**：启发式原则没有给出可量化的判断标准
2. **AI 顺势推导**：在模糊语境下，LLM 沿最省力的语义路径滑下去
3. **Upstream Skepticism 缺失**：Claude 没有对自己接受的前提进行质疑——接受了"简单=不加设置"作为约束条件，而非作为需要 tradeoff 的目标函数

## 关键概念

- **Principle Reification（原则实体化）**：把作为指南的启发式原则，当作有明确适用边界的规则来使用
- **Upstream Skepticism**：接受一个假设前先审视其上下文约束，而非无条件接受
- **Means-ends inversion**：把手段当目的
- **Anti-purity bias**：把启发式规则（heuristic）当铁律（rule）使用

## 防御机制

### 可执行的判断标准（写入 PRODUCT_SOUL.md）

如果一个功能需要用户在完成目标前做 N 次额外选择，且 N > 该功能未来消灭的平均选择次数，则该功能不满足轻量原则。

### Prompt 层防御（写入 CLAUDE.md）

调用 Gemini API 时必须附加"关注结果而非机制"的元提醒。

### 方案无法判断时的正确行为

标记 `[NEEDS_HUMAN_DECISION]`，而不是强行用现有原则套。

## 来源

 Flametree Pick 项目讨论（AI-Only 协作场景），2026-04-08
