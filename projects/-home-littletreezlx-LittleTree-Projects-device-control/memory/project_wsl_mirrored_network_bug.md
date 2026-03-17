---
name: wsl-mirrored-network-bug
description: WSL2 mirrored 模式端口转发偶发中断，外部请求 TCP 连上但无响应，需 wsl --shutdown 恢复
type: project
---

WSL2 `networkingMode=mirrored` 下，外部请求到 Windows IP:5000 偶发性失败：TCP 握手成功但无 HTTP 响应（curl 返回 exit 52 或 exit 28）。localhost:5000 始终正常。

**Why:** mirrored 模式的端口镜像转发通道在休眠唤醒、长时间空闲、网络适配器变化后会断开。Windows 网络栈仍监听端口（TCP 握手成功），但数据未送达 WSL 内进程。Microsoft WSL GitHub 已知 issue，未根本修复。

**How to apply:**
- 症状：Mac 调 Agent 返回空响应/超时，但 WSL 内 `curl localhost:5000/ping` 正常
- 修复：Windows PowerShell 执行 `wsl --shutdown`，重开终端后 Agent 自动启动
- 排查顺序：先本地 ping 确认 Agent 存活 → 再判断是 WSL 网络转发问题
