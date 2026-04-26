---
name: godot_headless_tres_png_bug
description: Godot 4.6 headless ext_resource PNG loading bug - cannot load .tres files with PNG dependencies in headless mode
type: reference
originSessionId: 4a9b583d-1168-4c84-8108-f306c4a4b614
---
# Godot 4.6 Headless Screenshot Blockers

## 核心阻塞：`.tres` ext_resource PNG 加载 bug

**现象**: Godot 4.6 headless 模式下，`[ext_resource]` 引用的 PNG 文件无法加载
```
ERROR: No loader found for resource: res://Assets/Sprites/Units/soldier.png (expected type: Texture2D)
ERROR: res://Assets/Data/Units/soldier.tres:14 - Parse Error: [ext_resource] referenced non-existent resource at: res://Assets/Sprites/Units/soldier.png.
```

**触发**: `--headless` 或 `--script` 模式，任何调用 `ResourceLoader.load()` 的路径

**影响**: 所有 `.tres` 文件（UnitData, CommanderData, TechUpgrade, LevelData, etc.）

**与 WSL2 无关**: Windows 原生路径同样失败，不是路径问题

**workaround**: 必须用有 GUI 的编辑器截图（Mac/Windows 编辑器 Edit → Take Screenshot）

## WSL2 GUI: 原生不可行,Xvfb 可行(2026-04-26 修正)

- WSL2 原生 X11/Wayland 不可达（无 WSLg）
- `DISPLAY=:0 godot` / 无显示标志的 godot 都启不来
- **`Xvfb :99 -screen 0 1152x648x24` 实测可用**(godot-qa-stories 2026-04-26 跑通全 9 个故事,见 game-mvp/TODO.md):
  - 启动: `Xvfb :99 -screen 0 1152x648x24 & DISPLAY=:99 godot --path .`
  - 项目用 GL Compatibility 渲染器(见项目级 CLAUDE.md),在 Xvfb 下能渲染(早期"GL black screen"判断已过时)
  - DebugPlayServer 端点 + `/screenshot` 截图均可用
- godot-explore v4.0 SKILL 的 Step 0a 已实装 Xvfb 自启 + Step 0b 验证截图非黑

## Windows Godot 自解压路径

- `C:\Tools\godot\Godot_v4.6.2-stable_win64.exe` 是**自解压目录**
- 实际 exe 在: `C:\Tools\godot\Godot_v4.6.2-stable_win64.exe\Godot_v4.6.2-stable_win64.exe`
- 另一个可用 Godot 在 WSL2: `/home/littletreezlx/.local/bin/godot` (Linux 版 4.6)

## wslpath -w 会损坏路径

- `wslpath -w` 输出包含 `\x0b` 字符
- 使用显式 UNC: `\\wsl.localhost\Ubuntu-22.04\...`
- 或复制项目到 Windows 原生路径避免路径问题
