# 2026-04-24-06 think.mjs 加 `--out` 必选机制 — 根治 stdout 截断

**类型**:Skill 基础设施修补 + Harness Engineering(把缺失的 observability/约束变成可强制执行的信号)
**影响半径**:
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/shared.mjs`(新增 `parseOutFile` + `emitOutput` + `ask` 接受 `outFile` 选项)
- `~/LittleTree_Projects/other/nodejs_test/projects/ai/think.mjs`(CLI 解析 + 三条路径透传)
- `~/.claude/skills/think/SKILL.md`(Step 2 新增"必选"小节、所有调用示例加 `--out`、Step 3.1 强调 Read 工具、约束段、changelog)
- `~/.claude/skills/think/ADVANCED.md`(Dual + quick 调用示例同步加 `--out`)
**版本**:think 0.6.0 → 0.6.1

## 遇到什么问题

think.mjs 的输出走 `console.log(text)`,Gemini/GPT 单次回复动辄 5-10K 字符,撞 Claude Code 的 Bash stdout 输出上限 → 文本被截断在中间(常见停在第 2 个 section 的某句话里)。

**这次会话内连续踩了第 N 次**:Founder 一句"是否需要整改 think 这个 skill?遇到不止一次了"——明确告知这不是孤立事故。

每次踩坑的临场修复套路是:

1. 看到 stdout 末尾被截断
2. 重跑命令 + `> /tmp/xxx.md`(或者 `2>&1 | tee`)
3. 用 Read 读文件

这个套路**每次靠记忆重新发明**,没沉淀到 skill 里。不同会话的 Claude Code 有的会想到 `tee`,有的会重跑 `--quick` 试图缩短输出,还有的直接基于残缺 stdout 写 Digest(最差情况——决策基于不完整内容)。

## 这是 Harness Engineering 的典型场景

CLAUDE.md 里有一条:

> **遇阻时的提问范式**:我缺失了什么可见能力?如何让它变成下次可检查、可强制执行的信号?

stdout 截断恰好是这种情况:

- **缺失能力**:think.mjs 没有"长输出落盘"模式
- **解决方式**:不是"下次记得用 tee"(凭记忆),而是改 skill 让"必选 `--out`"成为可执行约束

所以这次必须沉淀,不能继续靠会话间的临场救火。

## 讨论过程

Founder 给出方向,Claude Code 提议:

> 给 `think.mjs` 加 `--out <path>` 参数,写入完整内容到文件、stdout 只打前 N 行摘要 + 文件路径;SKILL.md 把默认用法改成总是带 `--out /tmp/think-<ts>.md`,Claude Code 一律用 Read 分页读。

**权衡**:

- 👍 一次修改根治截断;还顺带留下每次思考的磁盘存档
- 👎 每次 think 多一次 Read 调用(可忽略);需同步改 `think.mjs` + `shared.mjs` + `SKILL.md` + `ADVANCED.md`

Founder 同意"动手改"。

## 为什么这么改(实现细节)

### 选项 A(采纳):基础设施放 `shared.mjs`,think.mjs 调用方贯穿

`shared.mjs` 新增两个 helper:

- `parseOutFile()`:从 `process.argv` 提取 `--out <path>` / `--out=<path>`,移除后返回路径(或 null)。设计为在其他 CLI 解析之前调用,这样后续 parser 看不到 `--out`
- `emitOutput(roleName, text, outFile)`:有 outFile 则 `fs.writeFileSync` + stdout 打一行 `[think] ✓ written to <path> (N lines, M chars)`;无则 `console.log(text)`(沿用旧行为,完全向后兼容)

`ask()` 新增 `outFile` 选项,改用 `emitOutput`。

`think.mjs` 在自己的 `--model/--solo` 解析之前先调一次 `parseOutFile()`,solo/quick 通过 `ask({ outFile })` 透传,dual 路径用 `emitOutput("think", formatDual(results), outFile)` 替换原 `console.log(formatDual(results))`。

### SKILL.md 端的强制约束

仅有基础设施不够,Claude Code 仍可能不传 `--out`。所以 SKILL.md 三处加约束:

1. Step 2 新增"`--out <path>` 是必选(铁律)"小节,显式说明为什么必须、推荐路径(`/tmp/think-$(date +%Y%m%d-%H%M%S).md`)、为什么不用项目目录
2. Step 3.1 改"展示原文":明确"必须用 Read 工具读取该文件"
3. 约束段加一条:"`--out <path>` 是必选——见 Step 2"

所有 CLI 示例(SKILL.md + ADVANCED.md 共 5 处)统一加 `--out` flag。

## 为什么不选其他方案

### 方案 B(否决):脚本里把 `--out` 设成默认行为(无需显式传入)

think.mjs 自动写 `/tmp/think-<auto-ts>.md`,stdout 永远短摘要。

- 👍 SKILL.md 不需要每个例子都带 `--out`
- 👎 **破坏向后兼容**:任何依赖 stdout 全文的现有调用(包括人手动跑、其他脚本管道)都会坏
- 👎 **隐式行为**:`console.log` 突然变成"写文件 + 打路径",对调试者不友好
- 👎 路径选择魔法化(到底写哪?谁清理?)

→ 选 A:opt-in flag + skill 强制约定。显式胜过隐式,向后兼容更稳。

### 方案 C(否决):让 Claude Code 调用时自己 redirect(`> /tmp/xxx.md`)

不改脚本,只在 SKILL.md 教 Claude Code 用 shell redirect。

- 👍 零代码改动
- 👎 **stderr 状态日志(`[think] OpenRouter / ...`、`[think] Done in 44.9s`)也会进 stdout 或被吞**,得 `2>&1` 或精细分流,易错
- 👎 没有 `lines / chars` 摘要,Claude Code 不知道写了多少
- 👎 没有错误处理(写盘失败默默吞)
- 👎 仍然是"靠记忆"——每次调用都得手写 redirect,Claude Code 容易忘

→ 选 A:在脚本里做更可靠、可被强制约束。

### 方案 D(否决):同时改所有姊妹脚本(`design.mjs` / `product.mjs` / `game-*.mjs`)

它们也用 `console.log`,同样有截断风险。

- 👍 一次根治整个脚本族
- 👎 **超出当次任务范围**——Founder 问的是"think 这个 skill",不是整个脚本族
- 👎 这些脚本由独立 skill(think-gem-project 等)消费,要同步改它们的 SKILL.md 才有意义,工作量翻倍
- 👎 `parseOutFile` / `emitOutput` 已放 `shared.mjs`,姊妹脚本将来想接入只是"加几行"的事,不需要现在做

→ 选 A 的范围:只改 `shared.mjs` + `think.mjs`,姊妹脚本下次它们的 skill 真踩坑时再接入(yagni)。

## 验证

[验证凭证]

```text
# Test 1: --quick + --out(机制核心)
$ node think.mjs --quick --out /tmp/think-test-out.md "用一句话回答:1+1 等于几?"
[think] DeepSeek / deepseek-reasoner
[think] Thinking...
[think] Done in 2.3s
[think] ✓ written to /tmp/think-test-out.md (1 lines, 1 chars)
$ cat /tmp/think-test-out.md
2

# Test 2: 不带 --out(向后兼容)
$ node think.mjs --quick "用一句话回答:2+2 等于几?"
[think] DeepSeek / deepseek-reasoner
[think] Thinking...
[think] Done in 3.7s
4

# Test 3: dual + --out(formatDual 路径)
$ node think.mjs --out /tmp/think-test-dual.md "一句话回答:什么是 SOLID 原则的 S?"
[think] DUAL mode — calling 🧠 Gemini (...) + 🤖 GPT-5.4 (...) in parallel
[think] DUAL done in 14.3s (wall time)
[think] ✓ written to /tmp/think-test-dual.md (5 lines, 281 chars)
$ cat /tmp/think-test-dual.md
═══ 🧠 Gemini (google/gemini-3.1-pro-preview) — 14.3s ═══
S 代表单一职责原则(...)
═══ 🤖 GPT-5.4 (openai/gpt-5.4) — 3.2s ═══
Single Responsibility Principle:(...)
```

三条路径(solo --quick / 无 --out 兼容 / dual)全部验证 stdout 干净 + 文件完整 + stderr 状态保留。

## 后续可能的演进

- 姊妹脚本(`design.mjs` / `product.mjs` / `game-*.mjs`)下次踩同类坑时接入 `parseOutFile + emitOutput`(基础设施已 ready)
- 若 think.mjs 的 stderr 日志也开始撞限制(目前未观察到),考虑把 stderr 也分流到独立 log 文件
