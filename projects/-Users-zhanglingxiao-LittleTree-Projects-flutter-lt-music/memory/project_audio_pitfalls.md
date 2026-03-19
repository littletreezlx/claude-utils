---
name: audio-platform-pitfalls
description: 音频播放在各平台上的历史踩坑记录，避免重复踩坑
type: project
---

音频相关的平台踩坑（从旧版 MEMORY.md 迁移，已验证仍有效）：

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| iOS 后台播放中断 | audio_session 配置不当 | 正确设置 AudioSessionCategory |
| macOS 无法播放 | HTTPS 证书问题 | 添加 App Transport Security 例外 |
| 播放进度不准 | just_audio position 延迟 | 使用 positionStream 而非轮询 |
| 播放状态不一致 | 多音频源状态未同步 | 通过 AudioStateManager 统一管理 |

**Why:** 这些都是实际踩过的坑，文档或代码中不一定有记录，但重构音频模块时容易再踩。

**How to apply:** 修改 AudioService 或其子模块时回顾此列表，特别是涉及平台特定行为（iOS 后台、macOS 网络）时。
