---
name: adb 探索前必须先唤醒 + 解锁
description: 小米手机通过 adb connect 默认熄屏，直接截图只能拿到黑屏，必须 KEYCODE_WAKEUP + swipe 上滑
type: feedback
originSessionId: efe768d4-1bb0-447f-82da-abd6cf0a9cf9
---
通过 `adb connect 192.168.0.51:5555` 连上小米手机后，**默认 `mWakefulness=Asleep`，屏幕熄灭**。此时：
- `adb exec-out screencap -p` 输出全黑 PNG（但 State Oracle 仍可正常响应）
- `am start` 能启动 Activity 但用户看不见
- 用黑色截图做 Vision 分析 → 全盘误判

**正确唤醒序列（加入所有 Cyborg 流程 Step 0）**：
```bash
adb shell input keyevent KEYCODE_WAKEUP           # 亮屏
adb shell input swipe 540 2000 540 800 200        # 从下往上滑解锁（1080x2400 屏幕，无锁屏密码）
adb shell dumpsys power | grep mWakefulness       # 验证变成 Awake
```

**Why:** 2026-04-25 探索中踩坑：检测到 `mWakefulness=Asleep` 却没主动处理，继续往下走再截图再诊断，被 Founder 打断要求"要使用 adb 解除锁屏幕加个上滑的"。原因：懒得在 skill 第一步主动做唤醒，把 power state 当背景信息而不是阻塞信号。

**How to apply:**
1. android-explore / android-qa-stories / 任何需要截图的 skill，**Step 0 环境初始化时就应该无条件执行唤醒序列**，不是发现黑屏后再补救
2. 检测到 `mWakefulness=Asleep` = 阻塞信号，不是背景信息，必须先处理再继续
3. 如果未来手机设了锁屏密码，swipe 之后还要 input text 密码 —— 遇到时再加
4. 小米手机的 home launcher 在解锁后可能抢焦点，唤醒+解锁后要再 `am start` 一次目标 Activity
