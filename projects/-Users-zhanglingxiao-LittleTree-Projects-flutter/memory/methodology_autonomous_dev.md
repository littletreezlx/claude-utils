---
name: AI Autonomous Development Methodology
description: Debug State Server + screenshots + logs = fully autonomous Flutter development loop, first implemented in flametree_pick
type: feedback
---

AI 自主开发闭环方法论（2026-03-31 在 flametree_pick 首次实现）。

**核心理念：** 将 Flutter App 变成可被 AI 程序化控制的微服务，消除人工点击验证的瓶颈。

**三条验证通道：**
1. **业务逻辑** — Debug State Server（curl localhost:8788）读写数据库和 ViewModel 状态
2. **UI 外观** — `/screen` skill 截图 + 视觉分析
3. **运行稳定** — `view-dev-log.sh` 日志分析

**技术方案：**
- shelf + shelf_router HTTP server，kDebugMode 守卫
- 手动 Registry 映射（Dart/Flutter 无运行时反射）
- ProviderContainer 通过 `ProviderScope.containerOf(context)` 在 postFrameCallback 获取
- 两层读取：ViewModel 内存状态 + Repository 直读数据库
- Action 执行后自动返回最新数据

**Why:** 用户指出 AI 辅助开发的最大瓶颈是"写完代码要等人手动验证"。Debug State Server 让 AI 自己完成 95% 的验证。

**How to apply:**
- 新 Flutter 项目可参考 flametree_pick 的 `lib/dev_tools/` 和设计文档快速启用
- Flutter-level CLAUDE.md 已记录启用步骤
- 开发时主动使用：改代码 → 运行 App → curl 验证 → 截图确认 → 提交
