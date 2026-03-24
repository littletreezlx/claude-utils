---
name: remote_linux_workflow
description: 用户从 Linux (WSL2) 远程开发时的协作模式——用户只提需求，Claude 负责实现+测试+提交全闭环
type: user
---

用户有时会从 Mac SSH 到家里 Windows 的 WSL2 上工作。此时：
- 用户角色：需求方/产品经理，只提需求和反馈，不自行运行 Godot 验证
- Claude 角色：全权负责实现、跑测试、提交的完整闭环
- 视觉/UI 效果需要用户回 Mac 时再人眼验证
- Linux 环境下没有 Godot GUI，但 headless 测试仍可运行（如果配置了 Linux 版 Godot）
