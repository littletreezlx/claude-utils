---
name: Project Goal
description: FlameTree TV — personal Android TV player for silent screenshot capture via Home Assistant workflow
type: project
---

FlameTree TV 是一个纯个人 Android TV 视频播放器，核心目标是打通"观影-灵感捕获"工作流：

1. 极简播放容器：全屏黑盒，无海报墙/推荐/菜单
2. 隐形 Hook：HA 物理按键 → 局域网指令 → 静默截图+时间戳 → NAS → Obsidian
3. 零打断铁律：不暂停、不弹窗、不 Toast，最多边缘微光反馈

**Why:** 市面 TV 播放器太臃肿，用户需要完全掌控的纯粹播放体验
**How to apply:** 所有设计决策优先考虑"是否打断观影"，任何 UI 反馈必须无感
