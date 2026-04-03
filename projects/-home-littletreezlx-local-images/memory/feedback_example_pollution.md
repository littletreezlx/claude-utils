---
name: 示例污染陷阱
description: Prompt 中的示例会被 LLM 当作模板复制而非参考 — 写 prompt 时必须防御这一模式
type: feedback
---

给 LLM 的 prompt 中的"例子"会被当作"正确答案"大量复制，而不是"可能性之一"。

**已发生的案例**：
- `distinctive` 字段示例写了 "lip ring, scar across nose, beauty mark, tattoo" → 19 个角色中 14 个有 scar，8 个有 tattoo，8 个有 lip ring
- `aura` 字段示例写了 "confident smirk, hands on hips, relaxed slouch" → 11/19 直接复制这个 aura
- 本质：LLM 把示例当模板抄，而非理解"这只是众多可能性之一"

**Why:** LLM 倾向于锚定在 prompt 中出现的具体值上（anchoring bias）。示例越具体、越少，被复制的概率越高。

**How to apply:**
1. **写 prompt 示例时，必须同时写反例或免责声明**："these are just examples, do NOT copy them directly"
2. **示例数量 ≥ 5 且风格跨度大**：如果只给 2-3 个示例，LLM 会在这 2-3 个之间轮换
3. **高频字段用 "e.g." + "vary widely"** 而非直接列值
4. **审查 prompt 时专门检查**：哪些具体值出现在 schema 描述或示例中？这些值是否会在输出中高频重现？
5. **数据验证**：每批生成后统计各字段值的分布，检测聚类/重复
