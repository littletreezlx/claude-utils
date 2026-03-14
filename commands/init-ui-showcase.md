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
- 检查项目的 `scripts/take-screenshots.sh` 是否已存在
- 检查 `docs/ui/` 是否已有文档结构

### Phase 2: 创建项目截图脚本

> **架构说明**：截图能力分两层：
> - **通用库** `~/LittleTree_Projects/flutter/scripts/screenshot-lib.sh` — 已有，提供 macOS/iOS 截图驱动，**不需要创建**
> - **项目配置脚本** `scripts/take-screenshots.sh` — 每个项目各自创建，source 通用库 + 定义项目参数

创建 `scripts/take-screenshots.sh`（已存在则跳过），模板：

```bash
#!/bin/bash
# [项目名] - 截图脚本
set -e

# ===== 项目配置 =====
PROCESS_NAME="应用进程名"      # AppInfo.xcconfig 中的 PRODUCT_NAME
BUNDLE_ID="com.xxx.xxx"         # iOS Bundle ID

# 页面配置：名称:路由
PAGES=(
    "page_name:route"
)

# ===== 加载通用库并执行 =====
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
FLUTTER_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"  # 路径层级按项目结构调整

source "$FLUTTER_ROOT/scripts/screenshot-lib.sh"
run_main "$@"
```

注意 `FLUTTER_ROOT` 的相对路径需根据项目在 flutter 目录下的层级调整（如 `littletree_ai/app/` 是两层，普通项目是一层）。

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
