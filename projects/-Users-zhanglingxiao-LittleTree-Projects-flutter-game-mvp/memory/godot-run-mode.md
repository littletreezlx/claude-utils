---
name: godot-run-mode
description: Godot 启动模式与 DebugPlayServer 关系
type: feedback
originSessionId: b474a584-be3c-4fd6-8113-6449abf3f2b2
---
## Godot 启动模式区分

**启动编辑器（不运行游戏）：**
```bash
/Applications/Godot.app/Contents/MacOS/Godot --path <project> --editor
# DebugPlayServer 不会启动
```

**运行游戏（DebugPlayServer 生效）：**
```bash
/Applications/Godot.app/Contents/MacOS/Godot --path <project>
# 不带 --editor 参数，游戏直接运行
```

**为什么重要：**
- `--editor` 启动 Godot 编辑器，DebugPlayServer 不会监听端口 9999
- 只有游戏直接运行时 DebugPlayServer 才生效
- 之前误用 `--editor` 启动，导致验证失效，浪费大量时间排查

**How to apply:**
- 验证 Phase 16 视觉修复前，先确认 Godot 是以游戏模式运行（非 editor）
- 如果 `curl localhost:9999/ping` 无响应，先检查是否错误加了 `--editor` 参数
