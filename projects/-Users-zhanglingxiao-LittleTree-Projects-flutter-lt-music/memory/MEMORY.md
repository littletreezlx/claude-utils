# lt_music 项目记忆

## 项目约定

- **app_config.dart 中的密码是故意硬编码的**，用户明确允许提交真实密码到仓库。不要将其视为安全问题或跳过提交。

## UI 设计方向 (2026-03)

- **设计哲学**: Warm Essentialism (温润的精要主义)
- **视觉隐喻**: 白釉陶瓷底板与漫射光 (Ceramic & Diffused Light)
- **核心色彩**: 背景 Warm Ivory #FCFBF9, 强调色 Warm Amber #D97757 (2026-03-22 终版, 历史: #E26A2C → #D86B45 → #D97757), 文字主 #1C1917, 文字副 #78716C, Dark 背景 #181615, Dark 文字 #F5F5F4
- **签名时刻**: Glowing Deck — 播放器条提取封面主色做漫射光背景（ColorScheme.fromImageProvider, 饱和度钳制 0.4）
- **交互系统**: ScaleTapWrapper(scale 0.98 + opacity 0.85), NoSplash 全局禁涟漪, FadeThrough 页面过渡 300ms
- **阴影系统**: 禁止纯黑阴影，统一使用 tinted brown #0C3E2723
- **边框**: 方向性微光边框 (Glaze Border) — 顶/左亮，底/右暗
- **交互**: ScaleTapWrapper 组件统一处理（lib/core/widgets/scale_tap_wrapper.dart）

## 记忆索引

- [project_maintenance_infra.md](project_maintenance_infra.md) — 2026-03-19 建立的维护基础设施（ADR/SNIPPETS/影响矩阵）
- [project_high_risk_modules.md](project_high_risk_modules.md) — 高风险模块清单（ServiceLocator/AudioService/离线下载）
- [project_audio_pitfalls.md](project_audio_pitfalls.md) — 音频平台踩坑记录（iOS后台/macOS证书/进度延迟）
- [feedback_session_discipline.md](feedback_session_discipline.md) — 会话纪律（结束时保存/开始时检查 TODO）
