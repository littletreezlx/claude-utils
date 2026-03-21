# lt_music 项目记忆

## 项目约定

- **app_config.dart 中的密码是故意硬编码的**，用户明确允许提交真实密码到仓库。不要将其视为安全问题或跳过提交。

## UI 设计方向 (2026-03)

- **设计哲学**: Warm Essentialism (温润的精要主义)
- **视觉隐喻**: 白釉陶瓷底板与漫射光 (Ceramic & Diffused Light)
- **核心色彩**: 背景 Warm Ivory #FBF9F6, 强调色 Warm Amber #D86B45 (2026-03-21 从 #E26A2C 更新), 文字主 #2C2A28, 文字副 #8A847F
- **阴影系统**: 禁止纯黑阴影，统一使用 tinted brown #0C3E2723
- **边框**: 方向性微光边框 (Glaze Border) — 顶/左亮，底/右暗
- **交互**: 禁用 InkWell 默认涟漪，改用 scale 变换 + opacity 反馈

## 记忆索引

- [project_maintenance_infra.md](project_maintenance_infra.md) — 2026-03-19 建立的维护基础设施（ADR/SNIPPETS/影响矩阵）
- [project_high_risk_modules.md](project_high_risk_modules.md) — 高风险模块清单（ServiceLocator/AudioService/离线下载）
- [project_audio_pitfalls.md](project_audio_pitfalls.md) — 音频平台踩坑记录（iOS后台/macOS证书/进度延迟）
- [feedback_session_discipline.md](feedback_session_discipline.md) — 会话纪律（结束时保存/开始时检查 TODO）
