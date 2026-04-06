---
name: Cyborg 探索前必须确认代码已编译
description: ai-explore 前 force-reset 不够，需确认新代码已被 build（如 cyborg_probe.dart 已集成但旧 build 没包含）
type: feedback
---

探索前 `--force-reset` 重启 App 不等于新代码生效。如果有未编译的新代码（如新增的 `cyborg_probe.dart`），需要确保 flutter run 触发了完整 rebuild。

**Why:** 2026-04-06 Cyborg 探索中，`/cyborg/dom` 端点报 404，AI 以为代码未集成，实际 `debug_server.dart` 已正确注册了 `CyborgProbe.handle(path)`——只是 App 跑的还是旧 build。导致整轮探索回退到截图模式，60%+ 时间浪费在坐标校准上。

**How to apply:** 
1. ai-explore 开始前检查 `git status` 是否有 debug_server 相关的未提交改动
2. 如果有新的 dev_tools 代码，确保 `--force-reset` 后 flutter 完成了完整编译（检查 runtime log 中 "Xcode build done" 消息）
3. 启动后立即验证关键端点（如 `/cyborg/dom`），失败则排查是否是旧 build 问题而非代码问题
