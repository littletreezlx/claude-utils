# 2026-04-18-05 ai-explore v4.0：从"会探索"到"可证伪的质量基础设施"

## 背景

v3.2.0 已具备 Cyborg 能力：Flutter semantics tree + /cyborg/tap 语义注入 + State Oracle 三类端点。Founder 在真实使用中反馈整理 Gemini 讨论后要求全面改进。

会话时我先做了一轮 Gemini 5 条建议的技术评估（DOM interactiveOnly、Animation Idle Wait、Stale Node Guard、Crash Watchdog、感性体验纳入），然后用 /think dual 把事前验尸和 6 个挑战维度同时发给 Gemini 3.1 Pro 和 GPT-5.4。两路回复形成互补结构。

## 讨论过程

### 事前验尸（call think 前回答，Digest 回显锚）

按概率降序，3 个月后 ai-explore 彻底失败的最可能原因：

- P1 (40%) 可信度危机 — 报告 bug 证伪率高，Founder 形成"看到报告就跳过"的条件反射
- P2 (25%) 维护债务 — Flutter 升级导致 semantics tree 适配持续破损
- P3 (20%) 职责蔓延 — 随时间塞入审美/性能/多端，质量稀释
- P4 (10%) 覆盖率幻觉 — 单人设单轮 × N 次 ≠ N 维覆盖
- P5 (5%) State Oracle 底层前提被证伪

### Gemini 3.1 Pro 核心主张

停止在 Prompt 里堆砌规则，转向用**物理约束**建立硬证据机制：

- **Crime Scene 双快照**（before.png 画红框 + after.png + Oracle diff assertion）— 让 Founder 3 秒判断
- **信息抽干**（降采样/灰度截图）— 从物理上切断 AI 评判审美能力，防止职责蔓延
- **Behavioral Fuzzing**（Fat-Finger / Rage-Tap / Amnesia）替代角色扮演 — 真正模拟人类失败模式
- **Generation ID 锁死** stale node — 彻底阻断异步状态张冠李戴
- **Probe Contract Test** — Flutter 升级时只需跑通基础契约测试
- **quiet-frame 必须加 2s 硬超时** — 否则常驻动画（呼吸灯/进度条）下会永久挂起（这是对我原 ⭐⭐⭐⭐⭐ 评估的致命反驳）
- **State Teardown** `/cyborg/reset` — Claude Code 漏掉的关键：persona 切换时防止前序污染

### GPT-5.4 核心主张

ai-explore 缺的不是探索能力，而是**可证伪的可信度框架**：

- **A/B/C/D 报告分级** + 信用摘要页 — Founder 30 秒判断本次是否值得消费
- **最小证伪单元** 替代纯 curl 重放 — 重放只能证明稳定，不能排除替代解释
- **Oracle 非神谕化** — 三证据源（Interaction / System / Surface）任何一条单独成立都要降级
- **工具错误预算** — 每月追踪误报率，超阈值优先修 skill 而不是继续跑探索
- **persona × strategy 矩阵** — persona 是风格包装不是覆盖模型；引入 5 种策略（Goal-seeking / Boundary-pushing / Misread-first / Impatience / Constraint）提供正交覆盖
- **边界白名单硬卡** — 规则层明确"本 skill 不处理审美/性能/多端/a11y/埋点/安全"并路由到对应 skill

**事前验尸被证伪**：GPT 明确指出 **P4 不是独立问题而是 P1 的上游原因**——覆盖模型假 → 发现能力退化为表演。这修正了我原来的独立并列排序，正确战略顺序应为：可信度治理 → 边界治理 → 探索策略多样化 → 跨版本可持续性。

### 模型判优

**互补并采**。两方维度完全正交：

| 维度 | Gemini | GPT-5.4 |
|------|--------|---------|
| 问题视角 | 怎么强制 skill 不作死（how） | 怎么判断 skill 有没有堕落（measure） |
| 交付物 | 可编码的物理机制 | 可度量的治理指标 |
| 风险 | 有机制无量表，Founder 凭感觉判断 | 有量表无机制，分级变勾选动作 |

单取一方都会失败——Gemini 的 Crime Scene 需要 GPT 的 A/B/C/D 分级承载它的"3 秒判断"；GPT 的"Oracle 非神谕化"需要 Gemini 的 Generation ID 作为具体落地。

## 决策

**采纳选项 C：整合路线，分三 Phase 推进。**

### 不选项的理由

- **选项 A（仅 Gemini 物理约束）**：有机制无量表，3 个月后 skill 堕落时 Founder 没有信号察觉，最终凭主观感觉停用
- **选项 B（仅 GPT 信任治理）**：A/B/C/D 分级需要物理证据支撑，缺 Crime Scene 则分级只是 AI 自我宣称；缺 State Teardown 多 persona 会互相污染；缺 Behavioral Fuzzing 所有分级都建立在同一种行为偏见上
- **选项 D（仅 P0 止血）**：GPT 已指出 P1 可信度危机是头号风险，3 个月内几乎必然撞上——等于接受"退化为仪式"的结局

### Phase 分解

**Phase 0 止血（即刻，随本次交付落地）**：
1. screenshots 路径与 user memory 对齐 → `screenshots/cyborg/YYYY-MM-DD/step_N.png`
2. quiet-frame 契约声明 + 2s 硬超时（写入 skill 契约章节，Debug Server 端配合实现）
3. /think 评估输入附 Oracle 原始 JSON（防"让外审看摘要"）

**Phase 1 治理层（随本次交付落地）**：
4. A/B/C/D 报告分级 + 信用摘要页 + 自我否定统计
5. 最小证伪单元（A/B 级 bug 必填）
6. 工具错误预算追踪（`_scratch/ai-explore/tool-errors/YYYY-MM.md`）
7. 边界白名单（SKILL.md 硬卡不处理的维度 + 路由目标）
8. persona × strategy 矩阵（固定 5 种策略）
9. Oracle 非神谕化（三证据源三角校验）

**Phase 2 机制层（随本次交付落地 + 标注 Debug Server 契约）**：
10. Crime Scene 双快照（skill 端 Python PIL 实现红框）
11. Behavioral Fuzzing（利用现有 `/cyborg/tap?x=&y=` 坐标接口）
12. Generation ID 锁死（要求 Debug Server `/cyborg/dom` 返回 generation，`/cyborg/tap?generation=Y` 校验失败返回 `stale`）
13. Probe Contract Test（项目内 `test/cyborg_contract_test.dart` 契约回归）
14. State Teardown（要求 Debug Server 实现 `/cyborg/reset`，不存在则降级为重启 App）
15. Ignorance Hash 去重（`_scratch/ai-explore/known-hashes.json`）

**Phase 2 的 Debug Server 端改动**由使用 skill 的 Flutter 项目各自实现。skill 文档明确契约，端点不存在则自动降级运行并在报告中标注"能力受限"。

## 风险与反面检验

- **投入估计 3-4 周**：Phase 0+1 纯 skill 侧改动当日可完成，Phase 2 的 Debug Server 端点分散在各 Flutter 项目，按需实现
- **边界写硬可能错过跨维度复合问题**：接受 GPT 提出的中庸表述——"发现功能异常，可能与文案/视觉误导有关，但本 skill 不对审美维度下结论"
- **最小证伪单元提高了 A/B 级门槛，短期内高可信 bug 数量会下降**：这是设计目标，不是缺点（会筛选的系统才可信）
- **工具错误预算 30% 阈值是猜测**：首月运行数据校准后调整

## 下游影响

- 跨多个 Flutter 项目（barracks_clash / flametree_ai / ??）共享此 skill：Phase 2 的 Debug Server 契约需在各项目按需实现，skill 自身对端点存在性做优雅降级
- 与 `prep-cyborg-env`、`ai-qa-stories`、`ui-vision-advance` 的边界在 v4.0 的"边界白名单"章节显式化
- `/think` skill 的下游消费：ai-explore Step 4.5 改为默认 dual 模式（如报告含 Crime Scene 截图需 Gemini 多模态），--quick 仅在无截图且 API 配额紧张时使用

## 回滚条件

3 个月内观察到以下之一则回退评估：
- Founder 在连续 3 份报告里手动覆盖 A/B/C/D 分级（说明分级不准）
- 工具错误预算 D 级持续 ≥50%（说明 skill 自身问题多于产品 bug）
- Phase 2 的 Debug Server 契约在 2 个项目都未能落地（说明契约过度设计）

## 本次决策的反仪式性自检

如果去掉 /think dual 这一步，我的下一步行动会变吗？**会，大幅改变。**

我原本只会做 P0 止血 + 采纳 Gemini 建议 ①②。完全没想到：
- "信息抽干物理切断审美感知"（Gemini 独创）
- "Oracle 非神谕化三角校验"（GPT 独创）
- "工具错误预算作为信用保险丝"（GPT 独创）
- "P4 是 P1 的上游原因而非独立风险"（GPT 对事前验尸的证伪）
- "quiet-frame naive 实现会永久挂起"（Gemini 对我⭐⭐⭐⭐⭐ 评估的致命反驳）

这是高价值 call think，非仪式性调用。

## 参考

- 触发本次改进的对话：Founder 整理 Gemini 讨论后要求全面改进
- /think dual 完整对话：2026-04-18 会话中 Phase 3 的 Digest 与升级模板
- 相关 skill：`prep-cyborg-env`, `ai-qa-stories`, `ui-vision-advance`, `think`
- 相关 memory：`user_project_screenshots.md`（截图路径统一）
