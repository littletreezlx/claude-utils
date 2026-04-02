---
name: screen
description: >
  Lightweight screenshot of the current simulator/device screen. Use when the
  user says "截屏", "screenshot", "screen", "截图", "看看界面", "看看效果",
  or when another workflow needs fresh visual context. Does NOT restart the app.
version: 2.0.0
---

# Screen - 轻量截屏

## 核心理念

**截屏 = 1 秒操作**。不重启应用、不遍历页面、不构建产物。就是截当前屏幕。

## 默认行为：快速截屏

**执行脚本**（在 Flutter 项目根目录或子项目目录下均可）：

```bash
# 定位脚本（向上查找 flutter 项目根）
FLUTTER_ROOT=$(cd "$(pwd)" && while [[ "$PWD" != "/" ]]; do [[ -f "scripts/quick-screenshot.sh" ]] && echo "$PWD" && break; cd ..; done)
bash "$FLUTTER_ROOT/scripts/quick-screenshot.sh"
```

- 自动检测平台：macOS 应用正在运行 → macOS 优先；否则 iOS 模拟器
- 强制平台：`bash "$FLUTTER_ROOT/scripts/quick-screenshot.sh" ios` 或 `macos`
- 截图保存到 `/tmp/flutter_screenshots/`，最后一行输出为截图路径
- **timeout: 30000**（30 秒足够）

**截图后**：用 Read 工具读取截图路径，展示给用户。如发现明显 UI 问题，主动指出。

## 参数

```
/screen                    # 快速截屏（默认，1-3 秒）
/screen ios                # 强制 iOS 模拟器
/screen macos              # 强制 macOS 应用窗口
/screen macos <name>       # macOS 指定进程名
/screen phone              # Android adb 手机截图（见下方策略 B）
/screen full               # 全量文档截图（重量级，见下方策略 C）
/screen full ios           # 全量截图指定平台
```

## 策略 B: Android adb 截屏

**触发条件**：用户明确指定 `phone` / `手机`

```bash
bash /Users/zhanglingxiao/LittleTree_Projects/cs/scripts/common/phone-screencap.sh --no-open --resize 1280
```

截图路径：`/Users/zhanglingxiao/dev/phone_screencap/screenshot.png`

## 策略 C: 全量文档截图（仅 `/screen full`）

**触发条件**：用户明确说 `/screen full`、"全量截图"、"文档截图"、"所有页面截图"

**注意**：这是重量级操作 — 会重启应用、遍历所有配置页面、每页等待渲染。

**执行**：定位项目的 `scripts/take-screenshots.sh` 并执行：
```bash
bash <project>/scripts/take-screenshots.sh [ios|macos|all]
```
- 不传平台参数 → 让脚本决定默认值
- **timeout: 300000**（5 分钟）
- 截图保存到项目的 `screenshots/` 目录

## 约束

- **不构建应用** — 只截取已运行的界面
- **不创建新脚本** — 复用已有工具链
- **默认永远是轻量截屏** — 除非用户明确要求 full
