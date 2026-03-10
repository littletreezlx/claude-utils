---
name: screen
description: >
  This skill should be used to capture device/simulator screenshots for UI
  development context. Use when the user says "截屏", "screenshot", "screen",
  "截图", "看看界面", "看看效果", or when another workflow (like ui-vision-check
  or ui-redesign) needs fresh screenshots. Supports Flutter simulator screenshots
  (iOS/macOS), Android adb screenshots, and web page screenshots.
version: 1.0.0
---

# Screen - 智能截屏

## 目的

为 Claude Code 提供实时设备/模拟器的视觉上下文。智能检测项目类型，自动选择最佳截屏方式。

## 截屏策略（按优先级）

### 策略 1: Flutter 项目自动截图

**检测条件**：当前工作目录（或其父目录）存在 `scripts/take-screenshots.sh`

**执行流程**：
1. 定位项目的 `take-screenshots.sh` 脚本
2. **直接执行脚本，不需要预检查模拟器或构建产物** — 脚本内置了自动启动模拟器、查找设备等逻辑
3. 默认执行 `bash <script_path> ios`（移动端截图最常用）
   - 脚本会自动：启动模拟器（如果没有运行中的）→ 导航到每个页面 → 截图 → 清理
   - 如果用户指定 `macos`，执行 `bash <script_path> macos`
4. 截图自动保存到 `docs/ui/screenshots/`（脚本内置路径）
5. 用 Read 工具读取截图展示给用户

**重要**：
- **不要先检查模拟器状态再决定是否执行** — 直接执行脚本，让脚本处理一切
- 脚本**不会构建应用**，但会自动启动模拟器。如果应用未安装到模拟器，脚本会报错并提示构建命令
- 用户可指定单个页面：`/screen chat` → 只截 chat 页面（需脚本支持）
- 脚本执行时间较长（需等待模拟器启动+多页面截图），使用 timeout 300000（5 分钟）

### 策略 2: Android adb 截屏

**检测条件**：无 Flutter 截图脚本，或用户明确指定 `phone`/`手机`

**执行**：
```bash
bash /Users/zhanglingxiao/LittleTree_Projects/cs/scripts/common/phone-screencap.sh --no-open --resize 1280
```

**截图路径**：`/Users/zhanglingxiao/dev/phone_screencap/screenshot.png`

### 策略 3: 网页截屏

**检测条件**：用户提供了 URL 或明确指定 `web`

**执行**：使用项目已有的浏览器工具（Playwright/Puppeteer）或 headless Chrome

## 截图归档

截图成功后，如果当前在项目中（存在 `CLAUDE.md` 或 `pubspec.yaml`）：
- 自动**复制**到 `docs/ui/screenshots/`（原始文件保留）
- Flutter 项目的截图脚本已自动处理归档，无需额外操作

## 截图后动作

1. 用 Read 工具读取截图，展示给用户
2. 简要描述截图内容
3. 如发现明显 UI 问题，主动指出

## 参数

```
/screen                    # 自动检测：Flutter 项目用模拟器，否则用 adb
/screen ios                # 强制 iOS 模拟器截图
/screen macos              # 强制 macOS 截图
/screen phone              # 强制 adb 手机截图
/screen web [URL]          # 网页截屏
/screen [page_name]        # Flutter 项目：只截指定页面
```

## 约束

- **不构建应用** — 只截取已安装/已运行的应用界面
- **不创建新脚本** — 复用项目已有的截图工具链
- **adb 截图必须带** `--no-open --resize 1280` — 优化 token 消耗
- **截图失败时**给出明确的修复指引（设备未连接、应用未安装等）
