---
description: screen - 截屏辅助命令

---

# screen - 截屏辅助命令

## 目标

为 Claude Code 提供移动端或网页端的视觉上下文，帮助进行 UI 开发、调试和问题诊断。

## 执行方式

根据用户参数自动选择截屏目标：

### 手机截屏（默认）
- **执行命令**：`bash /Users/zhanglingxiao/LittleTree_Projects/cs/scripts/common/phone-screencap.sh --no-open --resize 1280`
- 使用 adb 工具截取 Android 设备屏幕
- 自动调整到 1280px 宽度（节省 55% token 消耗）
- 保存到固定位置：`/Users/zhanglingxiao/dev/phone_screencap/screenshot.png`
- 不打开 Finder（避免干扰用户）

### 网页截屏（可选）
- 使用 Playwright/Puppeteer 截取指定 URL 的网页截图
- 支持全页面截图和视口截图
- 保存到同一目录：`/Users/zhanglingxiao/dev/phone_screencap/webpage-{timestamp}.png`

## 约束条件

### 手机截屏
- **必须**：设备已通过 USB 连接并开启 adb 调试
- **必须**：adb 工具已安装且在 PATH 中
- **必须**：调用脚本时使用参数 `--no-open --resize 1280`（优化 token 消耗）
- **复用**：直接调用现有脚本，不重复实现

### 网页截屏
- **必须**：提供有效的 URL
- **可选**：指定截图尺寸（默认使用常见移动设备尺寸）
- **可选**：是否全页面截图（默认视口截图）

### 通用约束
- **禁止**：创建新的截图工具脚本（复用现有方案）
- **必须**：截图成功后使用 Read 工具读取图片并展示给用户
- **必须**：提供清晰的错误提示（设备未连接、URL 无效等）

## 输出要求

### 成功输出
1. **执行反馈**：
   - 截图类型（手机/网页）
   - 截图保存路径
   - 截图预览（使用 Read 工具读取图片）

2. **上下文建议**：
   - 基于截图内容给出分析建议
   - 如检测到 UI 问题，主动指出

### 失败输出
- **手机截屏失败**：
  - 检查 adb 设备连接状态（`adb devices`）
  - 提供连接设备的操作指导

- **网页截屏失败**：
  - URL 可访问性检查
  - 浏览器工具安装检查

## 参数说明

```bash
/screen                    # 默认手机截屏
/screen phone             # 明确指定手机截屏
/screen web [URL]         # 网页截屏
/screen web [URL] --full  # 网页全页截图
```

## 实现提示

### 手机截屏实现
```bash
# 直接调用现有脚本（已优化分辨率和 token 消耗）
bash /Users/zhanglingxiao/LittleTree_Projects/cs/scripts/common/phone-screencap.sh --no-open --resize 1280

# 然后读取并展示截图
Read /Users/zhanglingxiao/dev/phone_screencap/screenshot.png
```

### 网页截屏实现
- **优先选择**：项目已有的浏览器工具（Playwright/Puppeteer/Cypress）
- **备选方案**：使用 headless Chrome 命令行
- **移动端模拟**：默认使用 iPhone 12 尺寸（390x844）

## 典型使用场景

### 场景 1：调试移动端 UI 问题
```
用户："屏幕上的按钮位置不对"
操作：/screen
结果：Claude 看到实际界面截图，精准定位 UI 问题
```

### 场景 2：网页响应式布局验证
```
用户："帮我看看这个页面在手机上的显示效果"
操作：/screen web https://example.com
结果：Claude 获取网页在移动端视口的截图
```

### 场景 3：对比设计稿和实现
```
用户：（上传设计稿）"帮我看看和实际效果的差异"
操作：/screen
结果：Claude 对比设计稿和实机截图，指出差异
```

## 价值

- **可视化上下文**：让 Claude Code 看到实际的 UI 效果
- **精准调试**：基于实际截图定位问题，而非猜测
- **快速验证**：无需手动截图并上传，一键获取上下文
- **跨平台支持**：同时支持移动端和网页端开发场景

---

**实现原则**：简单够用，复用现有工具，专注提供视觉上下文给 Claude Code
