---
name: Docker Bridge 网络容器间通信
description: Synology NAS 上 bridge 网络容器无法通过宿主机物理 IP 互访，必须用 flametree_net 共享网络 + 容器名
type: feedback
---

Bridge 网络容器不能通过宿主机物理 IP（192.168.0.100）访问其他容器的端口映射，即使端口在宿主机上是通的。

**Why:** Synology NAS 的 iptables/防火墙阻断了 bridge 容器 → 宿主机物理 IP 的回路。`host-gateway`（host.docker.internal）在 Synology Docker 版本上也不支持。

**How to apply:**
- 容器间通信统一使用 `flametree_net` 共享网络 + 容器名直接访问
- 配置订阅源、API 调用等场景，用 `http://容器名:端口` 而非 `http://192.168.0.100:端口`
- 新服务需要被其他容器访问时，确保加入 `flametree_net` 网络
- `extra_hosts` + 宿主机 IP 的方案在 Synology 上无效，不要再尝试
