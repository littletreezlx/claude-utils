# Flutter 项目集 - 长期记忆

## 用户与偏好

- [user_preferences.md](user_preferences.md) — 用户角色、技术偏好、决策风格
- [feedback_autonomous_verification.md](feedback_autonomous_verification.md) — 运行时验证是默认行为，不要问用户去手动测试
- [feedback_ai_only_paradigm.md](feedback_ai_only_paradigm.md) — AI-Only 前提：工作流不假设人类程序员存在，决策按影响半径升级
- [feedback_screenshot_platform.md](feedback_screenshot_platform.md) — 截图时不要自作主张选平台，macOS 应用优先于后台模拟器

## 项目状态

- [project_exceptions.md](project_exceptions.md) — 各项目偏离通用规范的关键例外（pick 手写 Provider、ai 非 submodule 等）
- [doc_health_baseline.md](doc_health_baseline.md) — 文档健康基线（329 条失效路径，需分批修复）

## 技术参考

- [common_usage_summary.md](common_usage_summary.md) — flutter_common API 被哪些项目使用（影响分析）

## 架构决策

- **CI/CD 决策 (2026-03)**：暂不引入 CI/CD。原因：Claude Code 本地闭环成熟，云端 CI 增量价值接近零。触发条件：多设备开发、有协作者、或 flutter_common 跨项目回归成为痛点。

## 方法论

- [methodology_autonomous_dev.md](methodology_autonomous_dev.md) — AI 自主开发闭环：Debug State Server + 截图 + 日志（首发 flametree_pick）

## AI 图片生态

- [project_ai_image_ecosystem.md](project_ai_image_ecosystem.md) — 三项目协作拓扑：engine(底层) → studio(家庭创作) + game-mvp(游戏资产管线)
- [project_ai_image_studio.md](project_ai_image_studio.md) — AI Image Studio: 独立文生图 App（V1 完成），后端直连 ai-image-engine

# currentDate
Today's date is 2026-03-28.
