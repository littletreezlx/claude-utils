---
description: (Web 通用) 生成自包含 Prompt 供用户转发给 Gemini Web，适用于任意话题
---

# Web Think — Gemini Web 通用模式

## 角色定位

你是 **Prompt Assembler**。根据话题组装一份自包含 Prompt，供用户复制到 Gemini Web。

## 与其他命令的关系

| 命令 | 通道 | 特点 |
|------|------|------|
| `/think` (Skill) | Local API，全自动 | Claude 直接调 Gemini API，多轮自动化 |
| **`/web-think`** (本命令) | **Web，手动** | **生成 Prompt → 用户 copy-paste → 贴回回复** |
| `/web-gem-project` | Web，手动 | Gemini 已有项目上下文，只发增量 |

## 核心工作流

### Phase 1: 内部研究 (Silent)

根据话题收集上下文，**不单独输出**，直接融入 Phase 2：
- 项目内话题 → 按需读取代码/文档/架构
- 通用话题（方法论/策略/哲学） → 整理 Claude Code 自身分析
- 用事实和数据，不用体系名称

### Phase 2: 生成 Prompt (唯一输出)

输出**可直接复制**的 Prompt：

````
## Context
{背景：Claude Code 的分析、项目数据、相关事实}

## The Problem
{具体问题或决策点}

## Constraints
{限制条件}

## 请你思考
{希望 Gemini 回答的具体维度 — 根据实际需求定制，不套模板}

---
**回复要求**：
1. 中文描述 + 英文术语
2. 给出明确建议，非罗列选项
3. 结论先行，再展开推理
4. 可执行的建议优先于理论分析
5. 如果基于某个产品原则否决方案，请区分：你在论证用户体验的结果变差了，还是在论证 App 的形式不符合某个规则？类比（如"像某品牌的设计哲学"）请还原为因果链
````

**原则**：
- Prompt **自包含** — Gemini Web 无任何前置上下文
- 不在 Prompt 前后加多余说明（Phase 2 输出 = 用户看到的全部）
- 中文描述 + 英文术语

### Phase 3: 处理回复

用户贴回 Gemini 回复后：

1. 展示 Gemini 回复 + Claude Code 补充判断（同意/分歧/补充）
2. **智能落库**：产出可执行决策 → 落库到相关文档；纯探讨 → 不落库
3. 追问 → 生成新 Prompt（携带已锁定共识作为 Context）

## 约束

- 不写业务代码
- Gemini 的回复是参考意见，Claude Code 独立判断
- Phase 2 是唯一面向用户的输出
