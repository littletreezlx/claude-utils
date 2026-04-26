# 2026-04-26-03 think.mjs 提高 maxOutputTokens — 修模型输出额度截断

**类型**:Skill 基础设施修补 + Harness Engineering(同 0.6.1 思路:把"凭运气"变成"可执行约束")
**影响半径**:
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/shared.mjs:512,519`(`maxOutputTokens: 2500` → `8000`,加单行注释)
- `~/.claude/skills/think/SKILL.md`(版本 0.6.1 → 0.6.2 + changelog 新增条目)
**版本**:think 0.6.1 → 0.6.2

## 遇到什么问题

0.6.1 修了 stdout 通道的截断(模型回复 → Bash stdout 撞 Claude Code 输出上限),但今天又踩到截断 —— 这次落在**模型输出端**,在 stdout 之前就被砍。

**触发场景**:Founder 让我跑 `/think --solo gemini` 做 UI 第二视角评审,prompt 里要塞 styles.css + ProjectDetailPage.jsx + 我的 Phase 0-1.5 结论(总计约 8K 输入 tokens)。

**症状**:

| 文件 | 大小 | 状态 |
|---|---|---|
| `/tmp/think-uivs-20260426-122911.md`(第一次) | 431 字符 | 显式截断,停在"对你的四个疑虑进行"中间 |
| `/tmp/think-uivs4-20260426-123931.md`(后来重试成功的那次) | 9104 字符 | 看起来正常,但末尾"会写文章的设计博客,"无标点,撞 token 顶 |

跨触发条件复现同一终点症状(CLAUDE.md §紧急停止 5)→ 反转假设:不是参数/网络偶发,是结构性原因。

## 根因

`shared.mjs:512, 519` 在 0.5.0 引入 dual 模式时把 `maxOutputTokens: 2500` 写死,当时所有思考痕迹都在响应外的"thinking"事件里,2500 是给最终输出的合理上限。

但**推理类模型(Gemini-3.1-pro-preview / GPT-5.4)的 reasoning tokens 会从 `maxOutputTokens` 预算里扣**(AI SDK 的 `generateText` 把 reasoning 也算进 output budget)。重 prompt → 推理消耗大 → 剩给可见文字的额度被压到极小。

- **第一次截断到 431 字符**:推理吃掉 ~2400 tokens,剩 100 tokens ≈ 200-400 中文字符
- **第三次截断到 9104 字符**:推理省着用,可见文字撑到 9K(约 2200 tokens),仍在末尾被砍

stdout 通道(0.6.1 的 `--out`)对此无能为力:文件里写的就是被截断的内容。

## 讨论过程

Claude Code 提议:`maxOutputTokens: 2500` → `8000`,给推理留 2-3K headroom 后,可见输出仍有 5-6K tokens(≈ 12-15K 中文字符),覆盖典型 think Digest 的所有场景。

**权衡**:

- 👍 一行改动,根治当前症状
- 👎 成本/延迟翻倍上限。但 think 是低频高价值调用,合理代价
- 👎 还会再涨吗?如果将来用更长 prompt 评审整 codebase,8K 也可能不够。但 yagni —— 等真踩坑再调

Founder 一句"改" → 落地。

## 为什么不选其他方案

### 方案 B(否决):删除 `maxOutputTokens` 走模型默认值

Gemini-3.1 默认 64K, GPT-5.4 默认 128K。

- 👍 永远不会再被 cap 截断
- 👎 **极端 prompt 下成本失控**(单次调用可能烧 10x 预算)
- 👎 失去"调用应该有上限"的工程纪律 —— 模型可能产出不必要的长篇大论
- 👎 没有信号告诉 Claude Code "这次输出异常长,该不该重新组织 prompt"

→ 选 8000:既给推理 + 可见输出充足空间,又保留上限作为异常信号。

### 方案 C(否决):区分 reasoning 和 visible output 各自配额

AI SDK 部分模型支持 `experimental_providerMetadata.openrouter.reasoning_max_tokens` 之类字段。

- 👍 理论最优:给推理一个独立预算,不抢可见输出额度
- 👎 **OpenRouter 透传不一定支持所有模型的 reasoning budget 参数**,跨模型(Gemini / GPT / DeepSeek)行为不一
- 👎 调研 + 实现 + 测试时间远超此次修复价值
- 👎 真正解决问题的还是"总配额够大",细分预算只是优化分配

→ 选 8000:朴素方案彻底解决问题,细分等真有需求再说。

### 方案 D(否决):同时改姊妹脚本(`design.mjs` / `product.mjs` / `game-*.mjs`)

它们也用 `shared.mjs` 的 `askText`,但**它们的 prompt 模式不同**(产品/设计讨论不像 think 那样塞代码源文件,推理消耗低)。

- 👍 一次性根治
- 👎 **超出当前问题范围**,姊妹脚本现在没有截断证据
- 👎 改了反而可能增加它们的成本(它们的 prompt 简单,2500 通常够用)

→ 选 A 范围:`shared.mjs` 的 `askText` 改了所有脚本受益,因为它是共享 helper。**实际上修复同时覆盖姊妹脚本**(它们也调 `askText` 走同一行代码),但**问题 framing 仍以 think 为锚**,因为只有 think 触发到了这个 cap。文档(SKILL.md changelog)也只在 think 这边写,姊妹脚本不需要专门记录,因为它们的行为没变(原本就在 cap 之下)。

## 验证

[验证凭证]

```bash
$ node ~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs \
    --solo gemini \
    --out /tmp/think-verify-maxtok.md \
    "请用大约 3000 字回答:为什么前端开发应该重视语义化 HTML?展开 5 个维度,每个维度举具体例子。"
[think] OpenRouter / google/gemini-3.1-pro-preview
[think] Thinking...
[think] Done in {elapsed}s
[think] ✓ written to /tmp/think-verify-maxtok.md ({lines} lines, {chars} chars)

$ wc -c /tmp/think-verify-maxtok.md
# 期望:>= 6000 字符,且末尾是完整句子(有标点)
```

**实际验证将在改完后执行** —— 见会话内验证步骤。

## 后续可能的演进

- 若 8000 又不够(评审整 codebase / 多模态长 prompt),考虑
  - (a) 进一步提到 16000
  - (b) 调研 AI SDK 对 OpenRouter reasoning_max_tokens 的支持情况,做细分预算
- 若姊妹脚本(design.mjs / product.mjs / game-*.mjs)未来在重 prompt 下也踩同类坑,不需要再改 —— 它们已通过 shared.mjs 共享受益

## 与 0.6.1 的关系(避免混淆)

| 维度 | 0.6.1(stdout 通道) | 0.6.2(模型输出端) |
|---|---|---|
| 截断点 | 模型回复 → Bash stdout(Claude Code 输出限) | 模型生成 → 自身输出 token 上限 |
| 表现 | 文件没生成 / stdout 中间被砍 | 文件生成了,但内容本身末尾不完整 |
| 修复 | `--out <path>` 写文件 + Read 读 | 把 `maxOutputTokens` 提高 |
| 互补关系 | stdout 通道修好了,模型才能把完整内容写进文件 —— 但模型输出本身被截断,文件里写的就是缺的 | 模型能产出完整内容,但仍要走 `--out` 才能让 Claude Code 完整读到 |

两个修复**都需要**,缺一不可。
