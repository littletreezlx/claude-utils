---
name: godot-tscn-comment-trap
description: Godot 4.6 .tscn 文件注释分隔符导致节点解析失败
type: feedback
---

## Godot 4.6 .tscn 文件禁止使用 `#` 注释分隔符

**现象**: `Parent path './StatusPanel/VBox' has vanished when instantiating` + `Node not found: "TopBar"`

**根因**: Godot 4.6 的 .tscn 解析器对 `# ═══` 风格注释分隔符存在歧义，导致子节点（VBox、WavePreviewLabel 等）的父路径解析失败，场景实例化时找不到节点。

**为什么之前没发现**: GUT headless 测试不经过编辑器场景实例化流程，测试全部通过但编辑器运行时报错。

**How to apply**: 
- `.tscn` 文件只放纯节点定义，不放任何 `#` 注释
- 注释统一放在对应 `.gd` 脚本中
- `.tscn` 文件头部可放 `[gd_scene]` 元信息注释
