# 2026-04-18-02 /think skill 接入 GPT-5.4 + 默认 Dual 模式

**类型**：Skill 契约修改 + 脚本功能扩展
**影响半径**：
- `~/.claude/skills/think/SKILL.md`（版本 0.4.0 → 0.5.0）
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/shared.mjs`
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/.env.example`

## 问题

Founder 希望让 `/think` 同时调用 Gemini 和 OpenAI GPT-5.4 两个模型，最后由 Claude Code 做模型判优——依据是"GPT-5.4 逻辑链深度更强，Gemini 多模态更占优势，两者各有所长"。当前 `/think` 只调 Gemini（或 `--quick` 走 DeepSeek），无法享受多模型对冲带来的视角差。

## 讨论过程

1. Founder 明确要求："同时调用这两个 API，最后汇总分析，还要评估一下哪个 AI 的回答更好。openai/gpt-5.4"
2. Claude Code 分析 think.mjs 现状：
   - 已通过 OpenRouter 统一网关（DeepSeek 除外走直连 API）
   - 加一个新模型只需改 `DEFAULT_MODEL` 或新增 env 变量
   - 并发需要重构 `ask()` 把"调模型"和"打印"解耦
3. 设计选择：
   - **Dual 作为默认**（而非 opt-in 的 `--dual`）——Founder 原话是"我想让你在同时调用"，显式表达默认意图
   - **新增 `--solo gemini|gpt` 做 fallback** ——单模型成本对冲场景（Turn 2+、纯文本、无需对照）
   - **`--quick` (DeepSeek) 保持单路不变**——显式低成本场景不该被 dual 干扰
4. 冒烟测试：`node think.mjs "<简短方法论问题>"` 返回两路并发回复，wall time = 并发 max(两路耗时)，两路刚好给出相反观点，证明 dual 价值

## 决定

### 1. 模型接入

- 新增环境变量 `REASONING_MODEL`（默认 `openai/gpt-5.4`），走 OpenRouter 网关
- `.env.example` 添加该字段

### 2. shared.mjs 重构

- 原 `ask()` 被拆分：新增内部 `askText()`（返回 `{text, model, provider, elapsed}`，支持 `silent` 关闭 stderr 进度日志），`ask()` 变成打印包装器（向后兼容）
- 新增 `askDual(roleName, systemPrompt, payload, {modelA, modelB, labelA, labelB})` —— 用 `Promise.allSettled` 并发两模型，单路失败不拖垮另一路
- 新增 `formatDual(results)` —— 格式化带 `═══ label (model) — Xs ═══` 分隔的输出字符串

### 3. think.mjs CLI 扩展

- 默认走 `askDual(DEFAULT_MODEL, REASONING_MODEL)`，labels = `🧠 Gemini` / `🤖 GPT-5.4`
- `--solo gemini|gpt` → 单模型 `ask()`
- `--quick` → DeepSeek `ask()`（不变）

### 4. SKILL.md 契约更新（0.5.0）

- **Digest 新增两个字段**：`[GPT-5.4 核心主张]` + `[模型判优]`（Gemini 胜 / GPT 胜 / 互补并采 / 两败俱伤）
- **模型判优维度清单**：推理深度、盲区识别、具体性、反直觉检验、多模态理解、时效性（Step 3.2.5）
- **"互补并采" 不是偷懒选项**——只在两路指向不同维度且同时有价值时使用，观点重合只措辞不同时必须挑胜者
- **多轮追问格式**：两路共用同一份 Prompt，包含彼此上轮回复，让模型互相挑战（Step 3.2.6）
- **升级模板**：加入两方主张 + 判优字段

## 为什么不选其他方案

### 方案 X1：用第三个 AI 做 judge（如 Claude Haiku）

**否决原因**：
- 递归调 AI 增加延迟和成本
- Claude Code 在当前会话里已经持有完整 Prompt 上下文和事前验尸，天然是最合适的 judge——它比任何外部模型都更清楚 Founder 当前在纠结什么
- "Claude Code 担任 judge"反而强化了 Claude Code 的元认知纪律（必须显式做出胜负判断），是对抗仪式性咨询的天然机制

### 方案 X2：只加 GPT-5.4、替换掉 Gemini

**否决原因**：
- Gemini 在多模态（图片审美、UI 审视）场景有显著优势，替换会让截图 case 退化
- Dual 的核心价值是**两模型的差异**，不是选一个"更强的"

### 方案 X3：Dual 设为 opt-in `--dual` flag，默认仍单 Gemini

**否决原因**：
- Founder 原话已表达默认 dual 的意图
- Opt-in 意味着 Claude Code 每次要判断"要不要加 flag"——除非显式降级，否则 dual 应作为"更稳的默认"
- 成本顾虑用 `--solo` 显式降级解决，不应用默认值牺牲保护（防 bias）

### 方案 X4：顺序调用（先 Gemini 再 GPT）

**否决原因**：
- 串行耗时 ≈ 两路之和（本次实测 Gemini 9.4s + GPT 2.8s = 12.2s），并行 wall time = 9.4s
- 串行还会有"第二路看到第一路答案后附和"的风险（如果把前一路结果喂给后一路）；并行天然隔离

## 成本影响

- 默认模式 token 成本 ~2x（两路独立算 tokens）
- Wall time 通常持平 max(两路耗时)，GPT-5.4 响应快，Gemini 偏慢，瓶颈在 Gemini
- 降级通道：`--solo gpt` 仅 1x 成本 + 最快响应；`--solo gemini` 多模态场景；`--quick` 高频场景最便宜

Founder 若后续发现成本不可接受，调整 SKILL.md 默认模式即可，代码侧已经覆盖所有单/双路径。

## 验证凭证

- [验证凭证: 运行 `node think.mjs "对 AI-Only 开发项目..."` → STDOUT:
  ```
  [think] DUAL mode — calling 🧠 Gemini (google/gemini-3.1-pro-preview) + 🤖 GPT-5.4 (openai/gpt-5.4) in parallel
  [think] DUAL done in 9.4s (wall time)
  ═══ 🧠 Gemini (google/gemini-3.1-pro-preview) — 9.4s ═══
  **先写测试再写实现**更能防止该问题，因为交替开发或同步生成必然会触发...
  ═══ 🤖 GPT-5.4 (openai/gpt-5.4) — 2.8s ═══
  实现和测试交替开发更稳，因为它允许你持续用运行结果和真实行为校正断言...
  ```
  两路成功返回、观点相反、wall time = max(9.4s, 2.8s) 符合并发预期。]

## 后续

- 下次 `/think` 调用默认走 dual 模式，生成 7 字段 Digest（含 `[模型判优]`）
- 若 OpenRouter 未识别 `openai/gpt-5.4` 模型名（例如后续版本升级到 5.5），Founder 修改 `~/LittleTree_Projects/other/nodejs_test/projects/ai/.env` 里 `REASONING_MODEL` 即可，无需改代码
- 多轮追问时 Prompt 里必须保留两方上轮回复，这点需要实际使用时验证是否真的提升判优质量，如果没有显著提升可考虑简化
