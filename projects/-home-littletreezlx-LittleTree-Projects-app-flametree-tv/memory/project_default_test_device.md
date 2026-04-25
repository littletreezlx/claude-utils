---
name: FlameTree TV 默认测试设备
description: 192.168.0.51 是一部小米手机（21091116AC），不是 TV；在手机上跑 TV App 是 Founder 接受的设定
type: project
originSessionId: efe768d4-1bb0-447f-82da-abd6cf0a9cf9
---
默认测试设备 = Xiaomi 21091116AC 手机，地址 `192.168.0.51:5555`，通过 `adb connect 192.168.0.51:5555` 连接。**不是 Android TV**，屏幕 1080x2400 竖屏，`ro.build.characteristics=default`。

**Why:** FlameTree TV 虽然代码路径是 TV 形态（D-pad、SurfaceView、1920x1080 横屏、PixelCopy 截图），但 Founder 的日常测试设备就是这部小米手机。2026-04-25 确认："就是小米手机！先跑着，不用要求太高"。WSL 环境无 emulator 二进制与 AVD，且 macOS 路径 `~/Library/Android/sdk/...` 是 CLAUDE.md 旧残留，不要试图用。

**How to apply:**
1. 凡是 android-qa-stories / android-explore / 任何 adb skill，开头直接 `adb devices`，未连则 `adb connect 192.168.0.51:5555`，不要启本地 emulator、不要问 Founder。
2. 在这台手机上跑 TV App 会出现 form factor 失配（竖屏拉伸、焦点光圈被裁、D-pad 操作用 adb input keyevent 模拟、PixelCopy 截图可能异常），这些**不应**一律记为 bug。报告时先区分：是"手机上跑 TV App 的预期失配"还是"代码真缺陷"。前者写盲区观察或 Founder 已知降级，不进 TODO；后者才进 TODO。
3. Debug Server 端口 9877，HTTP 命令端口 9876，见项目 CLAUDE.md。
