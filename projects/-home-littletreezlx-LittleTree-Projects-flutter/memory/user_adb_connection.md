---
name: user_adb_connection
description: 用户默认 ADB 连接配置（WSL2 + Android 手机）
type: user
originSessionId: ca1294e1-a2ba-4572-b193-c8a656de6f53
---

## 默认 ADB 连接

- **设备**: Xiaomi Mi 11 (Android 13)
- **地址**: `192.168.0.51:5555`
- **环境**: WSL2
- **触发方式**: 如果用户不说明，则默认使用此连接

**Why:** 用户在 WSL2 环境下开发 Flutter/Android，每次连接手机不需要重复说明。
**How to apply:** 当用户提到"android"、"adb"、"手机"、"设备"时，默认使用 `adb connect 192.168.0.51:5555`。

---

## 解锁方法

Xiaomi Mi 11 解锁屏幕的完整流程：

```bash
# 1. 按电源键唤醒屏幕
adb shell input keyevent 26

# 2. 从屏幕底部向上滑动解锁（需要等待一下让屏幕亮起）
sleep 0.5
adb shell "input swipe 540 1600 540 800"
```

**注意**: `input keyevent 224` (wake) 单独使用无法解锁，必须配合滑动解锁手势。

**Why:** Xiaomi Mi 11 的锁屏策略要求真实的滑动手势来解锁，仅发送 wake keyevent 不会解除锁屏状态。
**How to apply:** 在需要唤醒设备进行测试时，先执行 keyevent 26 再执行 swipe 命令。
