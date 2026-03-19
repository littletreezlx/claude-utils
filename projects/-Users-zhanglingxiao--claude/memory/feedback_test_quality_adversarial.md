---
name: feedback_test_quality_adversarial
description: AI 生成的测试需要对抗性验证，用户偏好自动化变异测试方案而非手动审查
type: feedback
---

AI 同时写代码和测试 = 自己出题自己答，测试可能"断言 bug 的存在"而非预期行为。用户明确偏好自动化对抗方案。

**Why:** 用户在 Reddit 社区讨论中确认自己也深受此问题困扰。核心矛盾：AI 生成 500+ 测试时，人类无法逐一审查，需要自动化验证机制。

**How to apply:**
- 大批量生成测试后（>20个），自动触发 `test-verify` skill 进行红队变异验证
- 测试设计遵循"人类定义 What，AI 实现 How"原则
- 已在 CLAUDE.md 测试策略中增加"AI 测试陷阱"铁律
- 已创建 `test-verify` skill（语义变异 + Tier 分层 + 先出题后验证）
