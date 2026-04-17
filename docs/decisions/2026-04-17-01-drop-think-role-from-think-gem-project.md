# 从 think-gem-project 移除 pass-through 的 think role

- **Date**: 2026-04-17
- **Status**: Accepted
- **Scope**: `skills/think-gem-project/SKILL.md`（v0.7.0 → v0.8.0）

## 1. 问题 (What went wrong)

`think-gem-project` 的 roles 列表里包含 `think`，但 Step 3 明确写着「`think` 角色 — 委托给 think skill」。它其实是个 pass-through：进入 think-gem-project 发现是 think role，立刻转给独立的 `think` skill 执行。

这造成两层混乱：

1. **入口歧义**——用户看到两个 skill 都能处理"方法论讨论"（think-gem-project 的 description 列了 think role；think skill 自己也接），触发时选哪个不清晰
2. **文档冗余**——同一套 think 执行流程在两个 skill 文件里各有引用，更新时需要同步两处

## 2. 讨论过程 (How we thought about it)

Founder 问"think-gem-project 是不是不需要？think skill 够了吗？"。

分析下来两个 skill 是**不同问题域**（依据 `feedback_skill_value_not_frequency` 的鉴定规则），不能合并：

| 维度 | `think` | `think-gem-project` |
|---|---|---|
| 输入契约 | Claude 自己的分析 | 强制读 PRODUCT_SOUL / ARCHITECTURE 等项目文档 |
| 产出 | Digest 5 字段 | Feature Brief 落库 `docs/features/*.md` |
| Gemini 脚本 | 通用 `think.mjs` | 角色专属 `product.mjs` / `design.mjs` / `game-*.mjs`（各有专属 baseSystemPrompt） |
| 独有机制 | Failure_Premise、反仪式自检 | Inbox Zero、Engineering Handshake (Fast Track/Escalation) |

Founder 又追问"Claude 不能自己分析要不要走 think-gem-project 吗？"。能判断**入口**，但 skill 的价值不止于判断——它固化了外部脚本选择、产出契约、不可推理的流程（Inbox Zero / Handshake）。把这些塞进 `think` 会让 `think` 失去轻量定位。

真正冗余的是 **think-gem-project 内部的 `think` role**——它既不使用项目文档，也不用专属脚本，也不走 Handshake，就是个 pass-through。保留它只会让触发时产生歧义。

## 3. 决策 (What we decided)

从 `think-gem-project` 移除 `think` role，保留四个项目级角色：`product` / `design` / `game-product` / `game-design`。方法论/哲学/跨项目话题统一走独立的 `think` skill。

具体修改：
- `description`：roles 列表删除 `think`；明确提示「do NOT pass `think` as a role here」；版本 0.7.0 → 0.8.0
- **目的**段：五种角色 → 四种角色；显式指引方法论话题走 `think` skill
- **触发条件**：删除"讨论方法论 → think"的触发项
- **不触发**段：新增"方法论 / 工程哲学 / 跨项目策略讨论 → 用独立的 `think` skill"
- **Step 1 角色映射 / 上下文收集表**：删除 think 行和"think 角色特殊规则"
- **硬性约束**：删除"think 角色可在任意目录工作"
- **Step 2**：脚本调用说明去掉 think.mjs 引用
- **Step 3**：删除"`think` 角色 — 委托给 think skill"分支，Handshake 适用范围显式列出四个项目角色

## 4. 为什么不选其他方案

- **合并两个 skill**：违反 `feedback_skill_value_not_frequency` 的"不同问题域保留"原则。Gemini 脚本物理分离（不同 baseSystemPrompt），产出契约不同（Digest vs Feature Brief），合并只是把两条路压进一个 skill 文件用 role 分流——复杂度没消除只是转移
- **保留 pass-through 不动**：用户已指出触发歧义。继续保留 = 每次读 skill 文件都要扫描 think role 相关段落，却不产生任何实质执行路径
- **彻底删除 think skill，只保留 think-gem-project**：think skill 有独立价值（Failure_Premise 合约、反仪式自检、可在任意目录运行），删除会失去方法论讨论的轻量通道

## 5. 影响范围

- `skills/think-gem-project/SKILL.md`：9 处结构性修改（见决策 3）
- 不需要改动 `skills/think/SKILL.md`：其已正确描述 think-gem-project 的角色为"product + design + game-product + game-design"（无 think），本次修改让实际情况与它的描述对齐
- 不需要改动全局 `CLAUDE.md`：它只在"自动触发规则"表里引用 skill 名，不引用内部 role 列表

## 6. 验证凭证

[验证凭证: 运行 `grep -n "think" ~/.claude/skills/think-gem-project/SKILL.md | grep -v "think-gem-project" | grep -v "think skill" | grep -v "think.mjs"` → 残留匹配均为"方法论话题走 think skill"的指引，无 `think` 作为本 skill 内部 role 的定义性引用；版本号从 0.7.0 → 0.8.0]
