# 验证卫生：控制面/数据面 + 跨会话信任 + 日志活性 + AI 查日志义务

- **Date**: 2026-04-14
- **Status**: Accepted
- **Scope**: `~/.claude/CLAUDE.md`（铁律 2 扩展、铁律 5 扩展、紧急停止机制 +1 项、文档规范 guide 引用 +1 行）+ 新增 `~/.claude/guides/validation-hygiene.md`

## 1. 问题 (What went wrong)

Android remote-control 项目（POS 屏幕 LiveKit 推流到 Mac 浏览器）连续 4 轮会话（LAN / LiveKit Cloud 新加坡 / 家庭 NAS / 国内云 VM）调试视频出画。每轮都卡住，每轮都把根因写成"环境问题"传给下一轮 TODO/scratch。

前 3 轮都观察到完全一致的症状：浏览器 video 元素 `w=0 h=0 readyState=0 muted=true`（订阅成功但零帧）。每轮分别用「路由器 UDP 流表回收」「跨区域 RTP 丢」「家用 NAT TURN 端口范围」解释。

第 4 轮（今天）我从 ICE CONNECTED 信号开始，又花了 1 小时往浏览器侧排查（webrtc-internals、浏览器 console、track 状态），最后通过 **`dumpsys media_projection: null`** 才发现真正根因：`LiveKitClient.kt` 缺一行 `track.startCapture()`，MediaProjection 从未被真正消费过——4 轮全部在推送空帧。

修复就一行：

```kotlin
videoTrack = track
+ track.startCapture()
local.publishVideoTrack(track, ...)
```

这是 LiveKit Android SDK 2.8.1 的硬性要求（源码 `LocalParticipant.setScreenShareEnabled` 的内部实现就是 `createScreencastTrack → startForegroundService → startCapture → publishVideoTrack`），但 SDK 文档没明说。

### 真正的反思层级

具体的 SDK API 漏调不重要，重要的是**为什么 4 个会话都没发现**：

1. **控制面/数据面混淆**：所有"已验证"的凭证都基于控制面（`track published` / `ICE CONNECTED` / `Foreground service running`），从未取过数据面观测（`framesDecoded` / `dumpsys media_projection` 内容 / RTP 包大小）。`track published` 是 LiveKit 信令层事件，跟"是否真有视频帧编码"完全无关。

2. **跨会话毒资产继承**：前会话在从未端到端成功的前提下写了"代码 100% 没问题：MediaProjection 链路、publishVideoTrack 全部正常"。这条断言基于的是控制面凭证，但被后续会话当成了"跳过排查"的依据。

3. **日志构造缺失**：`LiveKitClient.kt` 全部日志只有 2 条 `Log.i` 生命周期事件，零运行时活性日志。如果有 `Log.i("first frame captured")` 或周期性的 `frames=N rate=M/s`，30 秒内就能看到 `frames=0` 然后定位到 `startCapture` 没调。

4. **AI 查日志义务缺失**：本次调试中我多次让用户去查 webrtc-internals / 浏览器 console / 截图，但**没先穷尽自己能查的 observability**（logcat filter 太窄、漏扫 SDK 内部 tag、没主动跑 tcpdump 看包大小分布）。

5. **跨环境共享症状盲区**：连续 3 个不同环境下出现完全一致的"`readyState=0` 零帧"症状，没有任何一轮反思"为什么换什么环境都长一样"。环境越多样，环境特异解释的后验概率应越低，结果反而被 4 个不同的"环境理由"麻痹了。

## 2. 讨论过程 (How we thought about it)

### Round 1：Claude Code 自己起的草案

Claude 提出 4 条规则：
- A. 新铁律：跨会话"已验证"断言本会话首次踏入必须降级
- B. 紧急停止扩展：同一症状跨环境 ≥2 次反转假设
- C. 速查表加 2 行
- D. `_scratch` 写"已验证"必须附运行凭证

Claude 自己预写的 Failure_Premise（5 条潜在失败模式）：E2E 观测定义不清、相同症状边界模糊、过度怀疑反弹、规则边界重叠、长会话稀释。

### Round 2：`/think` 调 Gemini（gemini-3.1-pro-preview）

Gemini 的核心反构（见 `_scratch/2026-04-14-think-gemini-cross-session-hygiene.md`）：

1. **重构问题定性**："你不是面临『继承问题』，是『认识论危机』。真正的根因是 AI 混淆控制面和数据面。继承机制坏了只是症状，源头是『资产录入』时没区分这两类成功。"

2. **直接否决 Rule A**："会引发灾难性的过度怀疑，彻底摧毁 TODO 复用价值。"

3. **极度认同 Rule D**："这是第一性原理。只要 _scratch 里贴的是数据面凭证，就不需要 A 的降级机制。"

4. **抽象 B/C 的触发条件**：把"相同症状"抽象为"Terminal Failure 一致"，不是 log 字符串对比。

5. **加反向豁免**：本会话未改代码 + 前会话有数据面硬凭证 → 100% 信任，禁止重验。

6. **指出遗漏的同类 failure mode**：Mock/Stub 毒性继承（Session A 的 mock 让 Session B 死都不怀疑该模块）。

7. **归属建议**：CLAUDE.md 只加 hook，详细判定下沉到 `guides/validation-hygiene.md`。

### Round 3：Claude Code 二阶反思（user 要求"全面思考是否合理"）

发现 3 处自己思考的漏洞：

- **N=1 vs N=2 是误读**：Gemini §2 写"跨越 1 次环境边界后仍存在"，§3 写"N=2 是完美阈值"，这两个等价（"切 1 次后仍复现" = "在第 2 个环境也出现" = N=2）。我之前在 to-discuss.md 写成"裁决点 B"是伪争议。
- **代码规范的"日志活性"hook 触发性弱**：写代码时 AI 不会停下来"考虑日志设计"，hook 在这里会沉默失效。应下沉到 guide 内部，通过 `/feat-done` 或 `code-reviewer` skill 触发。
- **文档规范 hook 实际是铁律 5 的延伸**：今天事故的本质是"验证凭证被空心化"——铁律 5 已要求验证凭证，但"凭证"一词太宽。应直接收紧铁律 5 的凭证定义（要求数据面），而不是新增一条独立 hook。

### Round 4：最终方案确认（user 拍板）

按 user 指令：用倾向方案 A1（Gemini 框架）+ B2（N=2）+ C1（Gemini 分层归属），并补充 user 提出的"日志"（构造侧 + 消费侧）两条。

## 3. 决定 (What we decided)

### CLAUDE.md 修改（3 处扩展，零新条目）

#### 3.1 铁律 2 扩展（消费侧 / AI 查日志义务）

原文末尾追加：

> 在请求用户粘贴日志/截图/数值前，必须先穷尽本地可自查的 observability（日志/运行时状态/抓包/dumpsys 等），并在请求中声明"已查过 X，仍需 Z 因为它只能在 ___ 取"。详见 `guides/validation-hygiene.md` §6。

#### 3.2 铁律 5 扩展（控制面/数据面 + 跨会话凭证）

在"验证凭证"格式约束之后追加两条：

> - **凭证必须来自数据面**：观测必须取自最终消费者侧/用户感知输出端（如 `framesDecoded > 0`、UI 像素、数据库实际查得的 payload），**不能用控制面成功日志**（握手 / 信令 / `HTTP 200` / `connected` / `published` / `build succeeded` 等"通道建立"信号）顶替。
>
> - **跨会话继承同样适用**：读到 TODO / `_scratch` / 前会话总结里的"已验证 X"等断言时，沿用此标准——若引用的凭证是控制面的，本会话必须把该结论降级为 `[控制面已通 / 数据面待验证]`。详见 `guides/validation-hygiene.md` §1, §3。

#### 3.3 紧急停止机制 +1 项（跨环境共享症状反转）

原 4 项后加第 5 项：

> 5. 同一终点症状（数据未达 / 流转断裂 / 输出异常）在 ≥2 个不同运行环境复现 → 立即停止换环境，反转假设：从"每个环境各自坏法不同"转向"有一个跨环境共享原因（代码 / 全局配置 / 基础设施）"。环境越多样，环境特异性解释的后验概率越低。详见 `guides/validation-hygiene.md` §2。

#### 3.4 文档规范 guide 引用 +1 行

在"详细指引"列表加：

> - 验证卫生（控制面/数据面、跨会话信任、日志活性、Mock 毒性）：`~/.claude/guides/validation-hygiene.md`

### 新建 `~/.claude/guides/validation-hygiene.md`

6 节内容：
- §1 控制面 vs 数据面法则（机械化自问 + 正反例表）
- §2 症状伪装识别（Terminal Failure 概念 + N=2 阈值）
- §3 跨会话信任 + 反向豁免（默认怀疑路径 + 豁免三条件）
- §4 Mock/Stub 毒性继承警告（`[MOCK_WARNING]` 标签 + 反向边界）
- §5 流式代码活性日志（构造侧三类日志：lifecycle + first-data + liveness counter）
- §6 AI 查日志义务（自查清单 + 合法请求情境 + 反例/正例）

每节都附今天事故的具体投射作为正反例。

## 4. 为什么这样而不那样 (Alternatives considered)

### 为什么收紧铁律 5 而不是新增独立铁律 9

候选方案：新增"铁律 9：跨会话结论需可追溯到 E2E 观测"作为独立条目。

否决理由：
- 铁律 5 已存在"验证凭证"概念，今天事故的本质是这个概念被空心化（"凭证"一词太宽，AI 用任何成功日志冒充）
- 收紧已有定义比新增条目更经济：避免规则膨胀（铁律平均权重下降 = 没铁律），且明确"控制面/数据面"是验证凭证的内涵而非外延
- 跨会话继承本质是同一标准的应用，不需要独立条目——只是把"本会话产出"扩展到"前会话遗留"

### 为什么"日志活性"不进 CLAUDE.md hook

候选方案：在「代码规范」section 加 hook：「流式/管道代码必须在 source 与 sink 两端各埋一条运行时活性日志（首次事件 + 周期计数器）」

否决理由：
- 触发条件弱：写代码是高频持续行为，AI 不会每次写 `Log.i()` 就停下来想"我现在该读 validation-hygiene.md 吗"
- hook 在 CLAUDE.md 应该锚在**读取/排障/交付**这些 AI 主动会经过的环节，不锚在"持续写代码"这种隐性时机
- 正确归属：guide §5 内部讲清楚，通过 `/feat-done`（交付前检查）和 `code-reviewer` skill（review 时核验）来激活

### 为什么 N=2 而不是 N=1 或 N=3

- N=1 误触率高：刚切环境就反转，正当的环境问题（NAT/VPN/防火墙）会被错判为代码问题，浪费时间在错方向
- N=3：今天事故的成本——前 3 轮都"换环境再说"，到第 4 轮才发现，多烧了 2 轮
- N=2 语义：在 1 个差异极大的环境跨度下（如 LAN → 公网云）复现就反转，环境特异解释概率 < 5%
- Gemini §2 和 §3 的措辞看似 N=1 vs N=2，实际等价（"切 1 次后仍复现" = "在第 2 个环境也出现" = N=2）

### 为什么单一 guide 而不拆 3 个文件

候选方案：拆为 `control-vs-data-plane.md` / `cross-session-trust.md` / `observability-discipline.md`

否决理由：
- 7 节内容都共享一个底层框架（控制面/数据面），分开会失去内在逻辑
- 它们是同一次事故反思的产物，物理分散反而让"为什么这些规则在一起"变得费解
- 一次性读完 ~250 行不构成认知负担
- 跨节引用更方便（`§3` 引用 `§1` 的法则定义）

### 为什么不用第二轮 /think 验证

- 这次方案修订主要是结构归并和误读修正，没引入新策略
- Gemini 已给完整框架，二轮边际价值低
- User 拍板放行，不必延后

## 5. 验证凭证

[验证凭证: 本次为规则文档变更，已 `Read` 验证全部 4 处编辑落到 `~/.claude/CLAUDE.md` 正确位置（铁律 2 line 35、铁律 5 line 42-44 之间、紧急停止机制 line 65、文档规范 line 184）；`Write` 创建 `~/.claude/guides/validation-hygiene.md` 和本决策文件。规则类文档不可填 N/A——凭证为编辑后立即 Read 重验内容]

## 6. 后续 follow-up

- TODO（remote-control）：第二条"到 LiveKit Cloud 控制台 revoke 已泄露的测试 Key" 仍待处理
- TODO（remote-control）：UX 改进——auto-start MediaProjection 应等无障碍授权确认后才弹出（user 今天提的）
- 可选：在 `git-workflow` 或 `feat-done` skill 内部加一步"检查本次提交的流式代码是否符合 §5 的活性日志规范"
- 监测：累计 3 次"读完本 guide 无影响"应主动报告 Founder 重审
