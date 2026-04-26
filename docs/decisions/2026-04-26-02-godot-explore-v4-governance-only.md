# godot-explore 升级到 v4.0 — 仅 port 治理层,砍 Cyborg 视觉强耦合机制

**Date**: 2026-04-26
**Scope**: 跨项目 skill 修改 — `~/.claude/skills/godot-explore/SKILL.md`
**Status**: Adopted

---

## 问题

ai-explore（Flutter）在 2026-04-18 升级到 v4.0「可证伪的质量基础设施」并在 2026-04-19 修补 P0 缺口（commit `4682be6` 等），引入了一整套基建。同日 android-explore 在 2026-04-26 完成对齐（commit `42193ae`，决策记录 `2026-04-26-01-android-explore-v4-alignment.md`）。

但 godot-explore 自上次跨平台对齐 commit `9965e37`（2026 年初）后没跟上。当前 v3.0 (245 行) 仍是「单链条证据链 + curl 主模式 + 可选 Cyborg(macOS cliclick)」，与 v4.0 的差距明显。

Founder 在本次会话中提出："`~/.claude/skills/ai-explore` 已经迭代过很多轮，android-ai-explore 已经 port 完了，godot-explore 是否需要同样优化？"

后果：barracks-clash（项目活跃度极高，近 30 天 188 个非 AutoSave commit）的探索质量、自我证伪能力、与 `/think` 的衔接整体落后于 Flutter / Android 项目，相当于同一套质量纪律在 Godot 上被悄悄豁免。

## 关键差异：Godot 不是 Android 的 port 镜像

调研发现 Godot 项目的实际使用模式与 Flutter / Android 在两点上**根本不同**，不能照搬 android-explore 的 port 模式：

### 1. 没有 OS-level 视觉+点击主链

| 维度 | ai-explore | android-explore | godot-explore |
|---|---|---|---|
| 截图工具 | `screencapture` (macOS Simulator) | `adb exec-out screencap` (设备) | `/screenshot` 端点(**Probe 内部 Viewport，平台无关**) |
| OS tap | `/cyborg/tap` (Probe 注入) | `adb shell input tap X Y` | **不存在** — cliclick 仅 macOS、Linux/WSL 无替代、且 memory `godot_headless_pitfalls.md` 明确 WSL2 GUI 不可行 |
| 语义节点 | `/cyborg/dom` + nodeId + generation | `uiautomator dump` XML + bounds | **不存在** — `/scene_tree` 仅返回当前场景文件名 |

### 2. DebugPlayServer 端点覆盖度反而极高

barracks-clash 已实装 36 个端点（导航/战斗/经济/UI 显示/截图/事件/崩溃日志），覆盖度**反超 ai-explore 的 Flutter Probe**。这意味着：

- 不需要 OS tap 来"模拟 UI 点击"——所有 UI 切换已经形式化为 `POST /play/show_*` 端点
- 不需要外部 screencapture——Probe 自带 `/screenshot/<name>` 直接输出 Viewport PNG
- 不存在 Fallback 概念——curl 主模式实质上就是 ai-explore Cyborg 模式的上限

## 平台差异不能直接 port 的部分

| ai-explore / android-explore 机制 | 不能直接 port 到 godot-explore 的原因 | 处理 |
|---|---|---|
| Cyborg vs Fallback 双模式选择 | Godot 没有"视觉+点击" Cyborg 主链可与 Fallback 对照 | **改为单一模式** "curl 主链 + Probe 自带截图" |
| `/cyborg/dom` + generation ID | Godot 无 DOM 概念，无 `nodeId` 可被 stale | **整段砍掉**，PAV-3T 的 Interaction 证据源合并入 System |
| Behavioral Fuzzing - Fat-Finger | 需 nodeId/bounds 偏移坐标 | **砍掉**(无对象可偏移) |
| Behavioral Fuzzing - Rage-Tap | curl 单任务锁会 429，并发 Rage-Tap 物理上不可能 | **砍掉**(端点物理约束) |
| Crime Scene 红框标注 | 无 nodeId/bounds 可标 | **缩水为 2 件套**(原始 before/after + 三合一 JSON) |
| `prep-cyborg-env` / 内嵌环境恢复 | Godot 启动需 GUI，本 skill 不替代用户启动游戏（与 Flutter Simulator/Android adb 不同，无标准化"自启" API） | **不实现自启**，Step 0 仅可达性检测 + 报错指引 |
| `/cyborg/reset` State Teardown | 项目已实装等价物 `POST /play/save_reset` | **直接复用** |

## 平台特异性必须保留 / 新增的部分

Godot 有 ai-explore / android-explore 没有的特殊性，必须在 v4.0 升级时显式 codify：

1. **Probe 自带截图是平台无关 Surface 证据源** — Godot 的 `/screenshot/<name>` 端点直接调用 Viewport，比 Flutter（依赖 `screencapture`）和 Android（依赖 `adb screencap`）都更稳，但仅在 GUI 模式下可用（headless 模式有 PNG/.tres 加载 bug，已 codify 在 memory `godot_headless_pitfalls.md`）

2. **A 级实质罕见声明** — Flutter / Android 都有"独立 Interaction 证据源"（Probe tap 响应 / adb input tap 退出码 + InputDispatcher logcat）。Godot 缺少这一源（curl HTTP 200 不代表真实操作命中，且无 nodeId stale 校验），因此除非伴随 `/debug/crash_log` 新增崩溃栈，大部分异常上限为 B。这是已知降级，必须在分级段、信用摘要页、变更历史中显式声明，避免使用者误以为是缺陷

3. **/debug/events 是项目侧独有的强 System Evidence** — barracks-clash 已实装结构化事件流（信号触发/状态转换/经济操作/伤害计算），比 Flutter 的 `/state/*` 和 Android 的 logcat 都更精确。v4.0 SKILL 必须在契约段把它列为可选增强端点

4. **Strategy 中仅保留 Amnesia + Speed-up** — Fat-Finger / Rage-Tap 因 OS 限制和单任务锁砍掉，但 Amnesia（用 save_reset 实现）和 Impatience 的 Speed-up（用 `/time_scale` 实现）仍是有效的 Behavioral Fuzzing

5. **不存在 Fallback 模式** — 因为 curl 主链就是上限。SKILL 不再写 Fallback 段，避免误导

## 决策

把 ai-explore v4.0 / android-explore v4.0 的**治理层**（哲学 / 边界白名单 / 契约段 / PAV 缩水版 / Crime Scene 缩水版 / 分级报告 / 工具错误预算 / persona×strategy / Ignorance Hash / `/think` dual + 必附原始证据）port 到 godot-explore，**不 port 视觉强耦合机制**（Cyborg 视觉+cliclick / Generation ID / Fat-Finger/Rage-Tap / 红框 Crime Scene）。

最终文件 526 行（v3.0 245 行 → v4.0 526 行，净增 281 行；介于 ai-explore 494 和 android-explore 564 之间，因为 Godot 简化掉视觉强耦合段而专注治理层 + 增加大段 Crime Scene 模板和 DebugPlayServer 项目侧契约示例）。version: 3.0.0 → 4.0.0。

## 不选其他方案的原因

**不选「整套 port，与 android-explore 同等待遇」**：android-explore 之所以 port 全套，是因为 Android 有真实的视觉+adb tap 主链可用（uiautomator 替代 DOM，logcat 升级为第三证据源）。Godot 既无 cliclick（macOS 专属）也无 DOM 等价物，强行加 Cyborg 段会产生 100+ 行死代码（永远进不了的 if 分支），且会迷惑 AI（AI 看到 Cyborg 段会试图启用，发现 cliclick 不存在又找不到替代）。**死代码比缺失能力更危险**。

**不选「保持 v3.0 + 不优化」**：直接违反"AI-Only 模式下，文档就是可执行约束"原则——Flutter / Android 项目享受 v4.0 严格质量纪律，Godot 项目却悄悄豁免，会让 barracks-clash（高活跃度项目）的探索结论可信度系统性低于另两类项目，且 Founder 无法察觉差距。考虑历史 0 次跑，Founder 第一次跑必定遇到大量噪音，没有分级滤网会直接放弃这个 skill。

**不选「v3.5 渐进 port（只搬 1-2 章）」**：A/B/C/D 分级和信用摘要页是相互依赖的——分级标准引用证据源，证据源依赖双证据校验，双证据校验依赖 Crime Scene，Crime Scene 又要写进信用摘要。截断式 port 会留下半成品体系，反而让报告结构更乱。

**不选「等 godot 项目接入更多视觉能力后再 port」**：Godot 视觉+点击的瓶颈是 OS 层（cliclick / WSL GUI），不是项目层。等多久都不会变。继续等只是给 Founder 推迟一次"AI 优化建议"的体感成本，没有实际收益。

**不选「直接复用 ai-explore SKILL，加 Godot 适配 if-else 分支」**：skill 文档应自包含。引用结构会让 AI 在执行时频繁跳转两个文件，增加 token 消耗和上下文遗忘风险，且平台差异过多（Probe DOM vs `/scene_tree` / Cyborg tap vs `/play/*` / cliclick vs 不存在）——引用机制下这些差异要么以 if-else 形式塞入 ai-explore（污染 Flutter 端），要么放 Godot 子文件（仍需要全文重写）。

## 操作

- 重写 `~/.claude/skills/godot-explore/SKILL.md`：v3.0 → v4.0，245 行 → 526 行
- 沿用 ai-explore v4.0 的章节顺序和命名（核心哲学 / 边界白名单 / 模式说明 / 契约段 / 前置条件 / 流程 Step 0-5 / 注意事项 / 变更历史）
- 平台差异处明确替换（不留 Flutter/Android 残留），并在「变更历史」段列清楚"已 port / 已砍 / 降级声明"三段映射表
- 保留 v3.0 中本土化的好内容："决策时是玩家，报告时是工程师" / 端口动态发现 / 调试类操作的人设约束（add_gold 不该被新手用）

## 影响

- **使用面**：barracks-clash（主力使用者）。其他 Godot 项目用得少
- **新增 _scratch 目录**：`_scratch/godot-explore/coverage-log.md` / `tool-errors/YYYY-MM.md` / `known-hashes.json`（首次运行时由 skill 自建）
- **报告路径变化**：`_scratch/explore-YYYY-MM-DD.md` → `_scratch/godot-explore/explore-YYYY-MM-DD.md`（与 ai-explore `_scratch/ai-explore/...` / android-explore `_scratch/android-explore/...` 命名空间对齐）
- **不破坏既有探索数据**：barracks-clash 的 `_scratch/` 目录目前为空（历史 0 次跑），无迁移负担
- **依赖**：本 skill 假设项目级 CLAUDE.md 含「Debug Play Server」段（barracks-clash 已就位）
- **首次运行的预期**：Founder 首次跑时大概率会看到一批 D 级（Probe 截图竞态）和 C 级（仅 Surface 证据），需要 1-2 轮迭代调优 DebugPlayServer 截图链路

---

## 后续可能的迭代点（不在本次范围）

1. ~~**DebugPlayServer 增加 `/state/route` 通用端点**~~ — **作废**。事后核查 DebugPlayServer.gd:72 已实装 `_scene` 字段附在每个响应（`result["_scene"] = _get_current_scene_name()`），SKILL v4.0 已修订为直接读 `_scene`
2. **Probe 截图同步等 Tween 完成** — 当前 `_take_screenshot` 等 3 帧（line 151），动画/Tween 长于 3 帧时截图会捕到中间态。可加 `await get_tree().create_timer(0.1).timeout` 或更精准的 Tween 完成回调
3. **godot-qa-stories 的契约对齐** — 那是另一个 skill，本次不动；TODO.md 已标记 godot-qa-stories 需适配 Xvfb，未来 godot-explore 的 Xvfb 自启逻辑可与之共享

## 二次修订（Founder push 后的事实纠错）

初版 v4.0 写完后 Founder 质疑"为什么要等"。复查发现两个事实错误：

| 初版断言 | 实际事实 | 来源 |
|---|---|---|
| "需要新加 `/state/route` 通用端点" | `_scene` 字段已在每个响应自动附带 | `Core/Autoloads/DebugPlayServer.gd:72` |
| "WSL/Linux 永久不存在 Cyborg 模式 → 需 Founder 在 macOS 跑" | WSL2 + Xvfb 实测可启 Godot + DebugPlayServer | `game-mvp/TODO.md` 2026-04-26 godot-qa-stories 验证记录 |

教训：写 SKILL 契约段前应先**精读项目侧 Probe 实现**而非凭印象推断。memory `godot_headless_pitfalls.md`（15 天前的 point-in-time 记录）说 "Xvfb 可启动但 GL black screen"，被 TODO.md 里 4-26 的最新实测推翻 — system-reminder 已在我读取 memory 时提醒"15 days old"，但我没足够重视过时风险。

修订后的 SKILL：
- Step 0a 自启 Xvfb + Godot（WSL/Linux 路径）
- Step 0b 截图健康检查加"非黑图"校验（防 GL 渲染器在 Xvfb 下失败的边角情况）
- Step 2.P/V 直接读 `_scene` 做 route diff，不再说"弱信号 `/scene_tree`"
- 变更历史段加"关键事实修正"小节
