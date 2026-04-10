# Memory Index

## Feedback
- [feedback_web_gemini_output.md](feedback_web_gemini_output.md) — web-gemini 命令只输出可复制 Prompt，不要单独输出现状分析
- [feedback_test_quality_adversarial.md](feedback_test_quality_adversarial.md) — AI 生成的测试需要对抗性验证，用户偏好自动化变异测试方案
- [feedback_design_docs_mutable.md](feedback_design_docs_mutable.md) — 设计文档是可变参考背景而非合规标尺，所有 UI 工作流都应允许突破现有设计系统
- [feedback_batchcc_shortcut.md](feedback_batchcc_shortcut.md) — DAG 任务结尾用 `batchcc task-xxx`，不追问不解释
- [feedback_think_handles_product_decisions.md](feedback_think_handles_product_decisions.md) — /think 应同时做产品+技术决策，只有真正拿不准的才进 to-discuss

## Reference
- [reference_skills_taxonomy.md](reference_skills_taxonomy.md) — Anthropic 内部 Skills 9 类分类体系，规划新 Skill 时用作自检清单
- [reference_agents_source.md](reference_agents_source.md) — ~/.claude/agents/ 来源于 wshobson/agents，提取+去重方式维护

## User
- [user_project_screenshots.md](user_project_screenshots.md) — 所有项目截图统一放在项目根目录 screenshots/ 下，UI 工作流直接读取无需询问

## Project
- [project_ondemand_hooks_idea.md](project_ondemand_hooks_idea.md) — /careful 和 /freeze 按需钩子模式，未来可实现为安全护栏 Skill
