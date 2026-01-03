---
description: 🚀 Flutter UI 文档系统全量初始化 (v3.0 - Pro Multi-Platform)

---

# Flutter UI 文档系统初始化

请基于当前项目，构建一套双平台 (macOS + iOS) 覆盖、自动化操作驱动的 UI 文档体系。

🎯 核心目标
多端截图基础设施：创建一个支持 macOS 窗口捕获和 iOS 模拟器捕获的自动化脚本。
响应式 UI 证言：通过多端对比截图，真实展现应用的响应式布局和跨端一致性。
全量文档体系：生成涵盖设计理念、多端详情、核心组件、主题规范和响应式策略的 Markdown 文档。
📋 第一阶段：跨端分析
进程与标识：识别 macOS PRODUCT_NAME 和 iOS CFBundleIdentifier。
环境预检：检查 scripts/ 是否有旧脚本，校验是否能连接 xcrun simctl 获取已启动的 iOS 模拟器。
适配扫描：识别代码中的 MediaQuery, PlatformAdapter 或 ScreenUtil 用量，定位多端差异点。
🛠️ 第二阶段：创建双端截图脚本 
scripts/take-screenshots.sh
脚本必须具备以下能力：

macOS 驱动：
使用 osascript 探测窗口，支持 
click_window_relative(x, y)
 比例点击。
iOS 模拟器驱动 (优先建议使用 iOS)：
检测已启动的模拟器：xcrun simctl booted。
捕获命令：xcrun simctl io booted screenshot <path>。
状态清理：截图前建议设置系统状态栏为完美状态（时间 9:41, 电量满格）。
关键函数集：
capture_macos(): 窗口裁剪模式。
capture_ios(): 模拟器捕获模式。
interaction_suite(): 包含键盘模拟 (keystroke, key code) 和坐标模拟。
自动化路径：支持一次运行自动生成三个核心场景的「双端对比」照片。
📝 第三阶段：双端文档设计
文件	要求
UI_SHOWCASE.md
主索引。列出项目 UI 核心理念，并提供 macOS/iOS 自动化运行指令。
docs/ui/screens.md
界面详情。每个页面应尽量展示 [macOS 截图] 与 [iOS 截图] 的并排对比。
docs/ui/responsive.md
适配规范。阐述 Tablet/Mobile/Desktop 的断点逻辑与 UI 演变。
docs/ui/theme.md
设计系统。动态解析 
ThemeConfig
，整理颜色、阴影、圆角规范。
docs/ui/components.md
组件库。按功能梳理通用 Widgets，并注明是否在移动端有特殊行为。
✅ 成功标准 (DoD)
 运行 ./scripts/take-screenshots.sh --auto 能在 docs/ui/screenshots/ 下生成 macos_*.png 和 ios_*.png。
 脚本具备容错功能：若未发现模拟器，则仅生成 macOS 截图并给出提示。
 文档包含详细的 UI 文档系统使用说明（如何扩展、如何重新生成）。
💎 严格禁止
❌ 禁止只关注 macOS 而忽略移动端的 UI 特性（如 Safe Area, 底部操作栏）。
❌ 禁止在未授予权限时反复重试导致进程僵死。
❌ 禁止使用纯文字描述代替真实截图。
💡 开发者备注 (给 AI 的额外提示)
优先使用 iOS 模拟器：因为它的 simctl 命令行工具比 Android 更加稳健且原生适配 macOS。
权限感知：在启动阶段，请以 GitHub Alert 格式提醒关于“辅助功能 (Accessibility)”的权限授予。
坐标点击：click_window_relative 是实现深层页面自动化的关键，请务必内置。
请先提供执行计划，在我确认后再开始