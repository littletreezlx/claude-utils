# Flutter 项目集 - 长期记忆

## 架构决策

- **CI/CD 决策 (2026-03)**：暂不引入 CI/CD。
  原因：Claude Code 在本地已形成"改代码 → 跑测试 → 通过才 commit"闭环，云端 CI 增量价值接近零。CD（自动打包发布）更不需要，本地 `flutter build` 几分钟搞定，配云端证书要花几天。未来触发条件：多设备开发、有协作者、或 flutter_common 跨项目回归成为痛点时再考虑。如需轻量兜底，可加 git pre-push hook 本地跑测试。
