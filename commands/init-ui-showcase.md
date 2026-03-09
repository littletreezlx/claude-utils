---
description: Flutter UI 文档系统一次性初始化 ultrathink

---

# Flutter UI 文档系统初始化

## 目标

为项目搭建 UI 文档基础设施。**纯初始化**，只创建骨架，不填充内容。

> 已存在的文件一律跳过，不覆盖。

## 执行流程

### Phase 1: 环境探测

- 识别项目平台：macOS / iOS / Android（检查 Runner 目录和配置文件）
- 检查 `scripts/` 是否已有截图脚本
- 检查 `docs/ui/` 是否已有文档结构

### Phase 2: 创建截图脚本

创建 `scripts/take-screenshots.sh`（已存在则跳过）：

- macOS 驱动：`osascript` 窗口探测 + `click_window_relative(x, y)` 比例点击
- iOS 模拟器驱动：`xcrun simctl io booted screenshot` + 状态栏清理（9:41）
- 容错：未检测到模拟器时只做 macOS 截图并提示
- 入口：`./scripts/take-screenshots.sh --auto` 一键生成 `docs/ui/screenshots/` 下的截图

### Phase 3: 创建文档骨架

创建以下文件的空骨架（已存在则跳过）：

| 文件 | 内容 |
|------|------|
| `docs/ui/UI_SHOWCASE.md` | 主索引，留空待填充 |
| `docs/ui/screens.md` | 界面详情骨架 |
| `docs/ui/responsive.md` | 适配规范骨架 |
| `docs/ui/theme.md` | 设计系统骨架 |
| `docs/ui/components.md` | 组件库骨架 |
| `docs/ui/specs/` | 创建目录 |
| `docs/ui/screenshots/` | 创建目录 |

每个骨架文件只包含标题和"待填充"提示，不做内容生成。

### Phase 4: 引导下一步

初始化完成后，告知用户：
- 运行 `/screen` 截图
- 使用 `ui-showcase-refresh` skill 填充文档内容
- 使用 `/ui-spec` 为单个页面生成 Spec

## 约束

- **幂等**：重复运行不破坏已有内容
- **不生成内容**：只建骨架，内容由 `ui-showcase-refresh` 和 `ui-spec` 负责
- **不运行截图**：截图由 `/screen` 独立完成
- 请先提供执行计划，在用户确认后再开始
