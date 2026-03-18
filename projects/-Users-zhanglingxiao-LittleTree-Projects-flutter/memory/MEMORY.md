# Flutter 项目集 - 长期记忆

## 用户与偏好

- [user_preferences.md](user_preferences.md) — 用户角色、技术偏好、决策风格

## 项目状态

- [project_exceptions.md](project_exceptions.md) — 各项目偏离通用规范的关键例外（pick 手写 Provider、ai 非 submodule 等）
- [doc_health_baseline.md](doc_health_baseline.md) — 文档健康基线（329 条失效路径，需分批修复）

## 技术参考

- [common_usage_summary.md](common_usage_summary.md) — flutter_common API 被哪些项目使用（影响分析）

## 架构决策

- **CI/CD 决策 (2026-03)**：暂不引入 CI/CD。原因：Claude Code 本地闭环成熟，云端 CI 增量价值接近零。触发条件：多设备开发、有协作者、或 flutter_common 跨项目回归成为痛点。

# currentDate
Today's date is 2026-03-18.
