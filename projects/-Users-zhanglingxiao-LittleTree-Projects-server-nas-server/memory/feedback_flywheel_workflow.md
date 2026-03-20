---
name: flywheel-workflow
description: 维护飞轮工作流——会话开始/开发中/会话结束的标准操作
type: feedback
---

每次会话应遵循 flywheel 闭环：
- 会话开始：`./scripts/quality/flywheel.sh brief` 快速对齐状态
- 开发中改完代码：`./scripts/quality/flywheel.sh check` 检查影响+不变量+契约
- 会话结束：`./scripts/quality/flywheel.sh debrief` 记录趋势

**Why:** 离散工具不形成闭环，每次会话从零开始重新理解项目状态，浪费 token 且容易遗漏检查。
**How to apply:** 把 flywheel 当作开发仪表盘，不要跳过 brief 直接开始改代码。
