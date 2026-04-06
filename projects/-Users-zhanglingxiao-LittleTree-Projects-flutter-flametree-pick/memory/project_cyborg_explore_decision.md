---
name: Cyborg Explore 架构决策
description: 2026-04-06 决策+POC 验证通过：explore 演进为 Vision+OS Tap+State Oracle 模式（方案 D），下一步重写 explore skills
type: project
---

2026-04-06 与 Gemini 两轮 think 讨论后决策：ai-explore 从"curl 操纵业务状态"演进为"Cyborg 模式"。

**Why:** 现有 explore 用 curl 模拟"用户探索"存在本质矛盾——没有 debug 端点的 UI（如 SuperDock ✨ 按钮）永远是盲区。归因纪律只修报告诚实度，不修能力缺口。Computer Use 2024-2025 已成熟。

**How to apply:**
- Cyborg 模式：Vision+OS Tap 做交互，L1.5 /state/* 做验证（唯一真理锚点）
- 严禁仅靠截图验证状态（视觉欺骗风险）
- Debug Server 从"操纵通道"变为"seed + oracle"
- qa-stories 保持 curl-driven 不变（确定性逻辑验收）
- 2026-04-05 同步更新了 3 个 explore skills 的归因证据链纪律（作为过渡期保障）

**POC Round 2 验证通过（2026-04-06）:**
- 同源坐标系方案：screencapture -R 窗口截图 + cliclick 同坐标系点击
- 坐标公式：`screen_pt = window_origin + image_px / 2`（@2x Retina）
- State Oracle 路由追踪：`/` ↔ `/management` 双向验证通过
- 自动化脚本：`scripts/cyborg-poc.sh`（含自动和交互两种模式）
- 已知缺口：`/state/overlays` 不追踪 Navigator-pushed dialog → 待 TODO 第二项修复
- 下一步：修复 overlays 盲区 → 重写 3 个 explore skills
