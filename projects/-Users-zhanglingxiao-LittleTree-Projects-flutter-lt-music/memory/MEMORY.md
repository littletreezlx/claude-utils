# lt_music 项目记忆

## 项目约定

- **app_config.dart 中的密码是故意硬编码的**，用户明确允许提交真实密码到仓库。不要将其视为安全问题或跳过提交。

## UI 设计方向 (2026-03)

- **设计哲学**: Warm Essentialism (温润的精要主义)
- **视觉隐喻**: 白釉陶瓷底板与漫射光 (Ceramic & Diffused Light)
- **核心色彩**: 背景 Warm Ivory #FBF9F6, 强调色 Ceramic Orange #E26A2C, 文字 #2C2A28
- **阴影系统**: 禁止纯黑阴影，统一使用 tinted brown #0C3E2723
- **边框**: 方向性微光边框 (Glaze Border) — 顶/左亮，底/右暗
- **交互**: 禁用 InkWell 默认涟漪，改用 scale 变换 + opacity 反馈
