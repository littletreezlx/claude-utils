# Flutter UI 文档系统初始化

> 深度分析项目后生成 UI 文档体系 + 截图自动化基础设施

## 核心理念
- **理解驱动** - 先深度分析项目，再基于实际生成文档
- **截图必备** - 没有截图系统的项目必须创建
- **可执行优先** - 生成的测试/脚本必须能运行

---

## 📋 执行策略

### 第一阶段：深度分析（必须完成）

**项目架构分析**：
- 扫描 lib/ 目录所有 .dart 文件，统计数量
- 识别所有页面（*_page.dart, *_screen.dart）
- 识别核心组件（widgets/ 目录）
- 分析路由结构（如何导航到每个页面）
- **识别应用进程名**（查看 macos/Runner/Configs/AppInfo.xcconfig 中的 PRODUCT_NAME）

**截图系统检查**（关键）：
```bash
# 检查以下是否存在
scripts/*screenshot*.sh              # 截图脚本
docs/ui/screenshots/*.png            # 真实截图（非 .txt 占位符）
```

**检查结果分类**：
- **有完整截图系统** → 跳到第三阶段（文档生成）
- **有部分截图系统** → 修复/补充缺失部分
- **无截图系统** → 必须执行第二阶段

### 第二阶段：创建截图基础设施（无截图系统时必须执行）

**必须创建的文件**：

#### 1. 截图脚本 `scripts/take-screenshots.sh`（macOS 原生方案）

```bash
#!/bin/bash
# [项目名] - macOS 截图脚本
#
# 使用方式:
#   ./scripts/take-screenshots.sh          # 手动模式
#   ./scripts/take-screenshots.sh --auto   # 自动模式
#
set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# ===== 项目配置（根据实际项目修改）=====
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_DIR="$PROJECT_ROOT/app"           # Flutter 应用目录（或 $PROJECT_ROOT）
SCREENSHOTS_DIR="$PROJECT_ROOT/docs/ui/screenshots"
PROCESS_NAME="app"                    # 应用进程名（查看 AppInfo.xcconfig）
# ==========================================

AUTO_MODE=false
[[ "$1" == "--auto" ]] && AUTO_MODE=true

echo "========================================"
echo "  UI 截图工具"
echo "========================================"

# 检查环境
log_info "检查环境..."
command -v flutter &>/dev/null || { log_error "Flutter 未安装"; exit 1; }
[ -d "$APP_DIR" ] || { log_error "应用目录不存在: $APP_DIR"; exit 1; }
log_success "环境检查通过"

# 准备目录
mkdir -p "$SCREENSHOTS_DIR"
cd "$APP_DIR"

# 构建应用
log_info "构建 macOS 应用..."
flutter build macos --debug

APP_PATH="$APP_DIR/build/macos/Build/Products/Debug/${PROCESS_NAME}.app"
[ -d "$APP_PATH" ] || { log_error "应用构建失败"; exit 1; }
log_success "应用构建完成"

# 截图函数
take_window_screenshot() {
    local OUTPUT_PATH="$1"

    BOUNDS=$(osascript -l JavaScript -e "
var app = Application('System Events');
var proc = app.processes.byName('$PROCESS_NAME');
if (proc.windows.length > 0) {
    var win = proc.windows[0];
    var pos = win.position();
    var size = win.size();
    pos[0] + ',' + pos[1] + ',' + size[0] + ',' + size[1];
} else { ''; }
" 2>/dev/null)

    if [ -z "$BOUNDS" ]; then
        log_error "无法获取窗口边界"
        return 1
    fi

    IFS=',' read -r X Y W H <<< "$BOUNDS"
    screencapture -R"$X,$Y,$W,$H" "$OUTPUT_PATH"
    log_success "截图完成: $(basename $OUTPUT_PATH) (${W}x${H})"
}

if [ "$AUTO_MODE" = true ]; then
    log_info "自动截图模式..."

    # 关闭已有实例
    pkill -f "${PROCESS_NAME}.app" 2>/dev/null || true

    # 启动应用
    open "$APP_PATH"
    log_info "等待应用启动..."

    # 等待窗口出现
    for i in {1..10}; do
        pgrep -f "${PROCESS_NAME}.app" > /dev/null && break
        printf "."
        perl -e 'select(undef, undef, undef, 1)'
    done
    echo ""

    # 等待 UI 渲染
    perl -e 'select(undef, undef, undef, 3)'

    # 截图主页面
    log_info "截取主界面..."
    take_window_screenshot "$SCREENSHOTS_DIR/main_page.png"

    # TODO: 添加其他页面截图
    # 例如：导航到设置页面后截图
    # osascript -e 'tell application "System Events" to keystroke "," using command down'
    # perl -e 'select(undef, undef, undef, 1)'
    # take_window_screenshot "$SCREENSHOTS_DIR/settings_page.png"

    log_success "截图已保存到: $SCREENSHOTS_DIR"

    # 关闭应用
    pkill -f "${PROCESS_NAME}.app" 2>/dev/null || true
else
    log_info "启动应用（手动模式）..."
    open "$APP_PATH"

    echo ""
    echo "========================================"
    echo "📸 手动截图指南"
    echo "========================================"
    echo ""
    echo "应用已启动，请手动截图："
    echo "  1. 按 Cmd+Shift+4，然后按空格选择窗口"
    echo "  2. 截图保存到桌面后移动到: $SCREENSHOTS_DIR/"
    echo ""
fi

# 显示结果
echo ""
if ls "$SCREENSHOTS_DIR"/*.png 1>/dev/null 2>&1; then
    log_success "已有截图:"
    ls -la "$SCREENSHOTS_DIR"/*.png
fi
```

**验证截图系统**：
```bash
chmod +x scripts/take-screenshots.sh
./scripts/take-screenshots.sh --auto

# 检查是否生成了真实图片
ls -la docs/ui/screenshots/*.png
```

### 第三阶段：文档生成

**必须生成的文档**：

| 文件 | 内容 | 要求 |
|-----|------|-----|
| `UI_SHOWCASE.md` | 主索引导航 | 基于实际页面和组件，<200行 |
| `docs/ui/screens.md` | 界面详情 | 列出所有 *_page.dart |
| `docs/ui/components.md` | 组件详情 | 列出所有 widgets/ |
| `docs/ui/theme.md` | 主题设计 | 基于实际 theme/ 目录 |
| `docs/ui/responsive.md` | 响应式规范 | 基于实际断点定义 |

**UI_SHOWCASE.md 必须包含截图系统说明**：
```markdown
## 📸 截图系统

### 运行截图
\`\`\`bash
./scripts/take-screenshots.sh          # 手动模式
./scripts/take-screenshots.sh --auto   # 自动模式
\`\`\`

### 截图输出
截图保存在 `docs/ui/screenshots/` 目录
```

### 第四阶段：验证

**必须通过的检查**：
- [ ] `./scripts/take-screenshots.sh --auto` 可执行且生成真实 PNG
- [ ] 所有文档引用的文件路径存在
- [ ] 文档中的组件名与代码一致

---

## ✅ 产出清单

**必须输出**：
- [ ] `UI_SHOWCASE.md` - 主索引（含截图系统说明）
- [ ] `docs/ui/screens.md` - 界面详情
- [ ] `docs/ui/components.md` - 组件详情
- [ ] `docs/ui/theme.md` - 主题设计
- [ ] `docs/ui/responsive.md` - 响应式规范
- [ ] `scripts/take-screenshots.sh` - 截图脚本

**验证项**：
- [ ] 截图脚本可运行
- [ ] 生成真实 PNG 截图
- [ ] 文档路径与代码结构一致

---

## 💎 严格禁止

```
❌ 不检查截图系统就跳过第二阶段
❌ 生成占位符 .txt 文件冒充截图
❌ 使用 Flutter Integration Test 的 takeScreenshot()（macOS 上不可靠）
❌ 文档引用不存在的文件路径

✅ 必须使用 macOS 原生 screencapture 方案
✅ 必须验证截图脚本可运行
✅ 必须生成真实可用的脚本
```

---

## 📏 成功标准

**立即验证**：
- 运行 `./scripts/take-screenshots.sh --auto` 成功
- `docs/ui/screenshots/` 有真实 PNG 文件
- 文档中所有引用路径有效

---

## 🔧 常见问题处理

### 截图失败："无法获取窗口边界"

**原因**：应用窗口未显示或进程名错误

**排查步骤**：
1. 确认应用已启动并有窗口显示
2. 检查 `PROCESS_NAME` 是否正确（查看 `macos/Runner/Configs/AppInfo.xcconfig`）
3. 确保已授予"辅助功能"权限

### 截图是全屏而非窗口

**原因**：`screencapture -R` 坐标错误

**解决**：检查 `osascript` 返回的坐标是否正确
```bash
osascript -l JavaScript -e '
var app = Application("System Events");
var proc = app.processes.byName("app");
var win = proc.windows[0];
win.position() + " " + win.size();
'
```

### 权限问题

需要在"系统偏好设置 → 安全性与隐私 → 隐私 → 辅助功能"中添加终端或 IDE。
