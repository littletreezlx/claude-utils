# android-explore 升级到 v4.0 — 与 ai-explore 可证伪质量基础设施对齐

**Date**: 2026-04-26
**Scope**: 跨项目 skill 修改 — `~/.claude/skills/android-explore/SKILL.md`
**Status**: Adopted

---

## 问题

ai-explore（Flutter）在 2026-04-18 升级到 v4.0「可证伪的质量基础设施」并在 2026-04-19 修补 P0 缺口（commit `4682be6` 等），引入了一整套基建：

- 边界白名单（防职责蔓延）
- Debug Server 契约段（必需/可选端点定义 + 项目侧契约回归测试）
- PAV-3T 三角校验（Interaction / System / Surface）
- Behavioral Fuzzing（Fat-Finger / Rage-Tap / Amnesia）
- Crime Scene 双快照
- A/B/C/D 分级 + 信用摘要页 + 工具错误预算
- persona × strategy 正交模型
- Ignorance Hash 去重

但 android-explore 自上次跨平台对齐 commit `9965e37`（更早）后没跟上。当前 v3.0 (272 行) vs ai-explore v4.0 (494 行) 差距明显 —— Founder 在本次会话中提出："`~/.claude/skills/ai-explore` 已经迭代过很多轮，android-ai-explore 是否需要优化？"

后果：FlameTree TV 的探索（小米手机 / TCL TV）报告质量、自我证伪能力、与 `/think` 的衔接**整体落后于 Flutter 项目**，相当于同一套质量纪律在 Android 上被悄悄豁免。

## 平台差异不能直接 port 的部分

ai-explore v4.0 有几个机制深度耦合 Flutter Probe，无法直接搬到 Android：

| ai-explore 机制 | 不能直接 port 的原因 | Android 等价方案 |
|---|---|---|
| `/cyborg/dom` + generation ID | Android 没有 Cyborg Probe，FlameTree Debug Server 也不暴露 DOM 端点 | `adb shell uiautomator dump` XML，每次重 dump 即视为最新（弱版本，无 stale 校验，靠"用之前重 dump"自然纪律） |
| `/cyborg/tap?nodeId=X&generation=Y` | 无 nodeId 概念 | 从 uiautomator XML 解析 bounds 中心 → `adb shell input tap X Y`（Android 天然同源坐标系，无需 DPR 转换） |
| `prep-cyborg-env` 自动调用 | 该 skill 是 Flutter 专属（明确说"Flutter App + Debug Server"） | 内嵌 Step 0a 简版恢复（adb connect + 唤醒解锁 + 启动 + forward + 健康轮询） |
| `/cyborg/reset` State Teardown | 项目无此端点 | `adb shell am force-stop` + 冷启动 + 项目 seed 脚本（如有） |
| `screencapture` (macOS) | WSL 环境无 macOS 命令 | `adb exec-out screencap -p`（设备直接截屏） |

## 平台特异性必须保留 / 新增的部分

Android 有 ai-explore 没有的特殊性，必须在 v4.0 升级时显式 codify：

1. **唤醒 + 解锁强制 Step 0** — Android 默认连上即 `mWakefulness=Asleep`，直接 screencap 全黑。已有 memory `feedback_wake_unlock_before_explore.md` 教训：2026-04-25 探索中踩过坑，Founder 当场要求"加个上滑解锁"
2. **Logcat 升级为第三独立证据源** — Flutter 没有等价物。Logcat 捕获 ANR / 崩溃 / 系统级警告 / InputDispatcher 异常，与 State Oracle 互补，A 级 Crime Scene 由三件套升级为**四件套**（多一份 logcat.txt）
3. **形态失配排除规则** — FlameTree 在小米手机（1080x2400 竖屏）上跑会有竖屏拉伸 / 焦点环被裁 / D-pad 用 keyevent 模拟，这些**不一律算 bug**（已 codify 在项目级 CLAUDE.md 和 memory `project_default_test_device.md`）。报告"自我否定统计"段必须显式记录"形态失配排除 N 条"
4. **设备双机决策** — 小米手机（日常调试，可直接 installDebug）vs TCL TV（最终目标，必须走 OTA）。Step 0a 默认选小米手机，TV 形态测试改 192.168.0.105
5. **adb daemon 跨 session 不持久** — 每个新会话第一个 adb 命令前必须先 connect
6. **D-pad 注入** — Android TV 形态特有，作为 Behavioral Fuzzing 的一种（`adb shell input keyevent KEYCODE_DPAD_*`）

## 决策

把 ai-explore v4.0 的全部治理层（哲学 / 边界白名单 / 契约段 / PAV-3T / Behavioral Fuzzing / Crime Scene / 分级报告 / 工具错误预算 / persona×strategy / Ignorance Hash）port 到 android-explore，并新增上述 Android 特异性段。

最终文件 564 行（介于原 272 和 ai-explore 494 之间，因为 Android 简化掉部分 Flutter Probe 复杂度但增加平台特异性段）。version: 3.0.0 → 4.0.0。

## 不选其他方案的原因

**不选「保持 v3.0 + 不优化」**：直接违反"AI-Only 模式下，文档就是可执行约束"原则 —— Flutter 项目享受 v4.0 严格质量纪律，Android 项目却悄悄豁免，会让 FlameTree TV 的探索结论可信度系统性低于 Flutter 项目，且 Founder 无法察觉差距。

**不选「直接 import / 引用 ai-explore 的章节」**：skill 文档应自包含。引用结构会让 AI 在执行时频繁跳转两个文件，增加 token 消耗和上下文遗忘风险，且平台差异过多（adb vs Cyborg / uiautomator vs DOM / 形态失配 vs 桌面环境）—— 引用机制下这些差异要么以 if-else 形式塞入 ai-explore（污染 Flutter 端），要么放 Android 子文件（仍需要全文重写）。

**不选「等 ai-explore 再迭代后一并对齐」**：ai-explore v4.0 已稳定 8 天（4-18 → 4-26），对齐窗口已成熟。继续等只是给 Founder 推迟一次"AI 优化建议"的体感成本，没有实际收益。

**不选「v3.5 渐进 port（只搬 1-2 章）」**：A/B/C/D 分级和信用摘要页是相互依赖的——分级标准引用证据源，证据源依赖三角校验，三角校验依赖 Crime Scene，Crime Scene 又要写进信用摘要。截断式 port 会留下半成品体系，反而让报告结构更乱。

## 操作

- 重写 `~/.claude/skills/android-explore/SKILL.md`：v3.0 → v4.0，272 行 → 564 行
- 沿用 ai-explore v4.0 的章节顺序和命名（核心哲学 / 边界白名单 / Debug Server 契约 / Cyborg 流程 Step 0-5 / Fallback / 注意事项）
- 平台差异处明确替换（不留 Flutter 残留），并在「变更历史」段列清楚映射表
- 保留 v3.0 中本土化的好内容："决策时是用户，报告时是工程师" / "同源坐标系" 解释 / 端口动态发现

## 影响

- **使用面**：FlameTree TV（主力使用者）。其他 Android 项目用得少
- **新增 _scratch 目录**：`_scratch/android-explore/coverage-log.md` / `tool-errors/YYYY-MM.md` / `known-hashes.json`（首次运行时由 skill 自建）
- **报告路径变化**：`_scratch/explore-YYYY-MM-DD.md` → `_scratch/android-explore/explore-YYYY-MM-DD.md`（与 ai-explore 的 `_scratch/ai-explore/...` 对齐，避免与其他 explore 流程串目录）
- **不破坏既有探索数据**：FlameTree 已有 `_scratch/ai-explore/explore-2026-04-25-*.md` 是过渡期产物，新版不会自动迁移，下次探索由 skill 直接写入新路径
- **依赖**：本 skill 假设项目级 CLAUDE.md 含 Default Test Devices 段（FlameTree 已就位 commit `6429eb8`）

---

## 后续可能的迭代点（不在本次范围）

1. uiautomator dump XML 解析助手脚本化（避免每次都内嵌 Python heredoc）
2. Android 版的契约回归测试（Espresso/UIAutomator 极简 UI 上断言 Debug Server 行为）
3. FlameTree TV 当前没有 `/state/route` 这种通用端点，未来若添加可强化 System Evidence
