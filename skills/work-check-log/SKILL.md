---
name: work-check-log
description: >
  This skill should be used when a user hands over a runtime log file
  (log.log / logcat / crash dump / server trace) and asks to diagnose
  what went wrong. Triggers on phrases like "排查日志", "查下日志",
  "帮我看看这个日志", "日志里能看出啥吗", "log 分析", "诊断一下",
  "为什么出问题", "check log", "triage log", or when the user pastes
  a log path alongside a bug description. Produces a structured
  version-sliced timeline, root-cause hypotheses with evidence, and
  an explicit list of what the user still needs to confirm — never
  auto-concludes when evidence is only control-plane.
  Distinct from log-audit (which reviews code-side log coverage);
  this skill reads the logs the user already has and hunts for bugs.
version: 0.1.0
---

# work-check-log — 通用日志排查

## Role

读用户提交的运行时日志（log.log / logcat / crash dump / 服务端 trace），定位问题根因。产物是 **"给排查者下一步的导航图"**，不是"替用户拍板结论"。默认保留怀疑，明确把"需要用户补的证据"和"已经由日志验证的事实"分开。

## When to use

- 用户提交 log 文件（路径或粘贴）并描述现象
- 线上问题反馈需要从日志反推根因
- 多版本混合时段的日志需要切片分析

## When NOT to use

- 代码侧"日志够不够写"审计 → 用 `log-audit`
- 只有崩溃堆栈没有上下文日志 → 直接上 `debugger` agent
- 用户只要统计（QPS、错误率）而非定位根因 → 普通脚本即可

## 启动前必读

**每次执行前先 Read 一次本 skill 目录下的 `LESSONS_LEARNED.md`**（若存在），把里面累积的检查项加到本轮分析中。这是 skill 的自我进化机制 —— 旧坑不再踩，新坑持续补。

## Core Flow

### Step 1 — 版本切片（最重要的第一步）

**铁律：跨版本不合并分析**。同一设备跨版本的现象放在一起推理必出错，先切片再诊断。

- Grep 以下模式找版本边界：`version=`, `versionName`, `BuildConfig`, `app_version`, `User-Agent`, 构建号
- 按时间戳排序，画出"时段 → 版本"映射表
- 若用户描述的现象横跨多个版本，显式拆分为"版本 A 下 N 次 / 版本 B 下 M 次"

> 真实案例：排查打印问题时忽略了日志中途 `1.53.7 → 1.58.0` 的升级，把旧版本连续失败和新版本零星失败混在一起，得出错误结论。用户指正后才发现。

### Step 2 — 错误簇频次直方图

用 Grep + 聚类找出"什么最常失败"，而不是盯着某一条具体错误：

- 关键词: `error`, `Error`, `Exception`, `failed`, `Failed`, `timeout`, `-1`, `null`, 中文的"失败"/"异常"/"超时"
- 按 `tag | message 前缀` 聚合计数，输出频次 top N
- 对高频错误做时间轴散点——是"持续失败"还是"突发失败"？

### Step 3 — 正常 vs 异常 对比

找出**同版本下**成功路径和失败路径的"最小差异"：

- 输入参数差异（同接口不同参数）
- 配置差异（同功能不同设置）
- 环境差异（同设备不同时段）

如果"正常 vs 异常"的差异找不到差别 → 说明问题可能在**日志以外**（固件/物理环境/第三方服务），这本身就是重要结论。

### Step 4 — 控制面 vs 数据面（铁律）

对应全局 CLAUDE.md 铁律 5 与 `~/.claude/guides/validation-hygiene.md` §1/§3。

**任何"成功"日志都要先问一句：这是哪一面的成功？**

| 信号 | 属于 | 能证明什么 |
|---|---|---|
| `bulkTransfer > 0`, `HTTP 200`, `connected`, `published`, `send success` | 控制面 | 通道建好了，字节写出去了 |
| `framesDecoded > 0`, UI 像素变化, DB 里实际查得 payload, 用户亲眼看见出票 | 数据面 | 用户感知的最终结果发生了 |

**结论里凡涉及用户感知的效果，必须标注 `[控制面已通 / 数据面待验证]`**，并在"待用户补证据"清单里列出怎么取数据面凭证。

### Step 5 — 结构化诊断报告

固定输出格式（下方有模板）。关键：
- 时间线表（每条带版本号）
- 根因假设（每个假设列出证据 + **反例** + 置信度描述用文字而非数字）
- 待用户补证据清单（用户配合项显式列出）
- **不自动下结论** —— 多个假设并列时保留多个

### Step 6 — Self-Reflection（强制）

报告输出后**必须**做一轮反思，写入 `LESSONS_LEARNED.md`（见下节 "Lessons Learned 协议"）：

1. 本次哪些步骤低效/走了弯路？哪步发现得晚了？
2. 本次新暴露的日志关键字段/模式 —— 项目侧是不是应该补日志？
3. 本次应该加进 skill 检查清单的新痛点是什么？

即使排查顺利，也要问：**"这次顺利是因为方法对，还是因为案例简单？"** 把方法论上的反思也记进去。

## Anti-patterns Checklist（执行时反复对照）

- [ ] **找不到版本号就开始诊断**。必须先搜 `version=` / `versionName` / `BuildConfig`，找不到就问用户。
- [ ] **配置变更藏在大 JSON 里肉眼找**。主动 grep 字段名（如 `paperHeight=`、`timeout=`、`enabled=`）+ 时间线对齐，不要翻上下文靠眼睛找。
- [ ] **看到"发送成功/returned OK"就停**。一定要确认这是控制面还是数据面。
- [ ] **同一 exception 的 stack trace 散成 30+ 行**。按时间戳/thread/tag 聚合成单个事件，不要被刷屏欺骗。
- [ ] **跨会话继承陷阱**。读到前会话 `TODO` / `_scratch` / 前总结里的"已验证 X"、"代码 100% 正确"：若凭证只是控制面，本会话必须把该结论**降级**为 `[控制面已通 / 数据面待验证]`，不得据此跳过排查。
- [ ] **同一终点症状在 ≥2 个不同环境复现**：立即反转假设，从"每个环境各自坏"转向"有一个跨环境共享原因"。环境越多样，环境特异性解释的后验概率越低。

## Output Template

固定 7 段式（输入 / 版本切片 / 错误簇 / 正常-异常对比 / 根因假设 / 待补证据 / 自反思）。完整模板和填写要点见 `references/output-template.md`，执行 Step 5 前先 Read 一次。

## Lessons Learned 协议

- 位置: `~/.claude/skills/work-check-log/LESSONS_LEARNED.md`
- 每次 Step 6 执行后 **追加**（不是覆盖）一段
- 格式:
  ```markdown
  ## {yyyy-mm-dd} · {项目名 / 脱敏}
  - **场景**: 一句话
  - **弯路**: 具体哪步走偏了
  - **补位**: 下次应该先做 X
  - **新增检查项**: "..." （同步抄到 SKILL.md Anti-patterns Checklist 的候选）
  ```
- 每积累 10 条反思，回到 SKILL.md 把高频痛点固化为正式检查项

## Gotchas

- **别替用户拍板"物理层面"结论**。日志看不到出票/出图/出声的物理结果，必须让用户回灌。
- **频次直方图不等于根因**。高频错误可能是症状的"回声"，真正的根因在少见的触发事件。
- **不要因为日志"干净"就说没问题**。日志干净也可能是"该打的没打"；反向查一下这段关键操作是否有任何打印。
- **版本切片后的结论别回填到其他版本**。版本 A 的假设不能无条件套用到版本 B。

## 参考案例

见 `references/case-study-printing.md`（脱敏的打印问题排查复盘，示范版本切片如何反转结论）。
