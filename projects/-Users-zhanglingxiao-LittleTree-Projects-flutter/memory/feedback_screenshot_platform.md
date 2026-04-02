---
name: 截图平台选择不要自作主张
description: 截图时如果用户没指定平台且多个平台都可用，不要自动选 — 或至少选运行中的 macOS 应用而非后台模拟器
type: feedback
---

截图时不要在用户没指定平台的情况下默认选 iOS 模拟器。macOS 应用正在运行时应该优先截 macOS。

**Why:** 用户明确说了"macOS应用开着"但 AI 自作主张截了 iOS 模拟器主屏幕，浪费了一轮交互。

**How to apply:** quick-screenshot.sh 的 auto 模式已改为 macOS 优先。在 /screen skill 调用时，如果用户提到了具体平台，传对应参数；如果没提到，就用 auto（会优先检测 macOS 应用）。
