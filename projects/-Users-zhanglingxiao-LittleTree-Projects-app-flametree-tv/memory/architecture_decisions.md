---
name: Architecture Decisions
description: Key technical choices for FlameTree TV, validated through 2 rounds of Gemini Think consultation
type: project
---

经过两轮 Gemini Think 讨论确认的技术选型（2026-03-29）：

## Locked Decisions
- **Player**: Media3 ExoPlayer, 硬解视频，SurfaceView（不用 TextureView）
- **UI**: 纯原生 View，不用 Compose TV / Leanback
- **HTTP Server**: Ktor-server-CIO (port 9876)
- **Intent Channel**: `com.littletree.flametree_tv.COMMAND` action, 作为唤醒锚
- **Screenshot**: PixelCopy API（异步、不阻塞渲染管线）
- **Architecture**: 单 Activity + SharedFlow CommandDispatcher，手动 DI (AppContainer)
- **Module**: 单 app module + common_base submodule

## Key Risks (from Gemini)
1. **PixelCopy 黑屏**：TV SoC 的 HWC 直通可能导致截图全黑 → 必须先做 Spike Test
2. **Ktor 后台被杀**：TV 内存紧张会杀后台进程 → Intent 作为唤醒锚，HTTP 仅前台用
3. **24p Judder**：需开启 ExoPlayer 帧率匹配

**Why:** 经过两轮系统性推演，这是极简场景下认知摩擦力最低的技术组合
**How to apply:** 不要引入 Compose/Leanback/Hilt 到 app 模块；common_base 的 Hilt 是库内部的
