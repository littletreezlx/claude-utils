Flutter UI 文档系统初始化
深度分析项目后自动构建「macOS 原生截图系统」+「全量 UI 文档」

🎯 核心原则
理解驱动 - 必须先读取 AppInfo.xcconfig 和路由配置，拒绝盲目硬编码。
截图闭环 - 无截图必创建，有截图必校验，拒绝 .txt 占位符。
原生优先 - 必须使用 macOS screencapture 方案，因为它在桌端比 Flutter Integration Test 稳健得多。
权限感知 - 在运行自动脚本前，必须提醒用户关于“辅助功能 (Accessibility)”的权限。
📋 执行策略
第一阶段：精准定位
环境分析：识别 PRODUCT_NAME (AppInfo.xcconfig) 和 CFBundleName (Info.plist)。
路由扫描：分析页面列表、常用主页 Tab 切换方式。
现状检查：若 docs/ui/screenshots/ 无真实 PNG，则强制进入第二阶段。
第二阶段：截图基础设施 (核心增强版)
创建 scripts/take-screenshots.sh。脚本设计要求：

鲁棒启动：先尝试 open，若返回 -600 错误则直接执行二进制文件副本。
窗口探测：放弃 pgrep，改用 osascript 实时统计窗口数量，确保 UI 渲染后才按键或截图。
模拟导航：内置一套基于 osascript 的键盘模拟逻辑（如：tab, space, command + [）。
参数支持：支持 --auto (全自动), --capture (单次捕获), --clean (清理)。
第三阶段：文档体系化生成
文件	要求	关键来源
UI_SHOWCASE.md	主索引，<150行，必须含截图运行指南	项目 README & 路由
docs/ui/screens.md	关联真实代码路径，描述页面核心功能	*_page.dart, *_screen.dart
docs/ui/theme.md	动态解析颜色、阴影、圆角规范	ThemeConfig 或 ThemeData
docs/ui/components.md	梳理通用 Widgets，按功能分类	lib/presentation/shared/widgets
✅ 产出标准 (Definition of Done)
 脚本生产力：运行 ./scripts/take-screenshots.sh --auto 能在 30s 内生成 main_page.png。
 视觉真实：docs/ui/screenshots/ 目录必须包含真实的应用窗口图片。
 链接完整：Markdown 文档中所有 file:/// 链接必须指向存在的代码文件。
 零占位符：禁止出现 "TODO: Replace with screenshot" 等字样。
💎 严格禁止 (The Red Lines)
❌ 禁止不检查权限就运行脚本导致 AI 连续报错
❌ 禁止在没有真实获取 UI 逻辑的情况下编写 theme.md
❌ 禁止使用全屏截图（必须使用窗口坐标裁剪）
🔧 常见故障处理预案
窗口找不到：强制检查进程名是否包含空格或大小写。
截图全黑/全屏：校验 screencapture -R 参数中的 X,Y,W,H 是否由 osascript 正确返回。
💡 为什么这样优化？ (开发者复盘)
进程名陷阱：在 macOS 桌面端，二进制文件名是 flame_tree，但 System Events 里的进程名可能是 flame_tree 也可以是 littletree_x。优化版要求 AI 必须读取 Info.plist。
窗口检测逻辑：原版使用 pgrep 只能代表进程启动了，不代表窗口弹出来了。优化版建议用 osascript ... count windows，这能完美解决“截屏截到桌面”的问题。
模拟导航：增加这一项后，AI 就有意识地去寻找如何切换 Tab（比如刚才我用 Tab + Space），从而一次性生成“全家桶”截图，而不是只给一张主页。
权限前导：自动化脚本最怕的就是静默失败。加上权限感知后，AI 会先像刚才一样问你“请给权限”，而不是尝试 10 次报错 10 次。