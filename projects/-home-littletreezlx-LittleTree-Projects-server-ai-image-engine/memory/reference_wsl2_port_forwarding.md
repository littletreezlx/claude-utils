---
name: WSL2 Caddy 反向代理架构
description: ai-image-engine 通过 Windows Caddy 反代对外暴露，内部端口 8101，对外 8100；含 netsh portproxy 冲突排查经验
type: reference
---

## 架构

ai-image-engine 采用与 device-control 相同的 Caddy 反代方案，解决 WSL2 mirrored 模式下端口转发不稳定问题。

```
Mac → Windows:8100 (Caddy, 0.0.0.0) → localhost:8101 (WSL uvicorn, 127.0.0.1)
```

**关键配置**:
- Caddy 配置: `~/LittleTree_Projects/device-control/ops/caddy/Caddyfile`
- Caddy Windows 路径: `C:\Tools\caddy\Caddyfile`（NSSM 服务读取此文件）
- uvicorn 监听: `127.0.0.1:8101`（仅 localhost，避免与 Caddy 端口冲突）
- 对外端口 8100 由 Caddy 独占

## 排查经验（2026-03-31）

### 问题现象
Mac 端 curl 返回 `Empty reply from server`（TCP 连上但 HTTP 无响应）

### 根因
旧的 `netsh interface portproxy` 规则残留，svchost.exe 也在 `0.0.0.0:8100` 上 LISTENING，抢走了 Mac 的请求（转发到过期的 WSL IP），导致 Caddy 收不到流量。

### 排查路径
1. WSL 引擎本地 `/ping` 正常 → 引擎没问题
2. Windows 侧 `Invoke-WebRequest localhost:8100` 正常 → Caddy 到引擎链路没问题
3. Mac 仍然 Empty reply → 外部流量没走 Caddy
4. `Get-NetTCPConnection -LocalPort 8100 -State Listen` 发现两个进程：caddy + svchost
5. `netsh interface portproxy show all` 发现残留规则

### 修复
```powershell
# 从 WSL 中执行
powershell.exe -Command "netsh interface portproxy delete v4tov4 listenport=8100 listenaddress=0.0.0.0"
powershell.exe -Command "Restart-Service -Name 'Caddy' -Force"
```

### 教训
- 迁移到 Caddy 方案后，必须清理旧的 netsh portproxy 规则
- 诊断"Empty reply"时，先查 `Get-NetTCPConnection` 确认端口是否被多个进程竞争
- 从 WSL 可以通过 `powershell.exe -Command "..."` 直接操作 Windows 服务和网络配置

### WSL 操作 Windows 常用命令
```bash
# 查服务状态
powershell.exe -Command "Get-Service -Name 'Caddy'"
# 重启服务
powershell.exe -Command "Restart-Service -Name 'Caddy' -Force"
# 查端口占用
powershell.exe -Command "Get-NetTCPConnection -LocalPort 8100 -State Listen"
# 查/清 portproxy
powershell.exe -Command "netsh interface portproxy show all"
powershell.exe -Command "netsh interface portproxy delete v4tov4 listenport=8100 listenaddress=0.0.0.0"
```
