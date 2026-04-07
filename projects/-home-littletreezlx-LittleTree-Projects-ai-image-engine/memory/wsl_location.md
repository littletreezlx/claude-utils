---
name: wsl_location
description: 我在 Windows WSL2 环境下运行，localhost 是 WSL 而非 Windows
type: user
---

## 关键前提：我在哪里

**我在 Windows WSL2 (Ubuntu) 内部运行**，而不是在 Windows 主机或 macOS/Linux 物理机上。

### 网络访问规则

| 目标地址 | 能否访问 | 说明 |
|----------|----------|------|
| `localhost` / `127.0.0.1` | ❌ WSL 内部 | WSL 自己的 loopback，**不是 Windows** |
| `172.17.128.1` | ✅ WSL → Windows | WSL 的 gateway（`/etc/resolv.conf` 中的 nameserver），即 Windows 宿主机 |
| `host.docker.internal` | ✅ Docker 容器内 | Windows Docker Desktop 提供的宿主机引用 |

### Windows 服务的端口

| 服务 | Windows 监听端口 | WSL 访问地址 |
|------|-----------------|-------------|
| Caddy 反代 | 8100 | `http://172.17.128.1:8100` |
| ComfyUI | 8188 | `http://172.17.128.1:8188` |
| AI Image Engine (FastAPI) | 8101 | `http://172.17.128.1:8101` |

**每次会话开始时**：先确认 `curl --connect-timeout 3 http://172.17.128.1:8100/ping` 是否通，再决定下一步操作。禁止直接用 `localhost` 发请求到 Windows 服务。
