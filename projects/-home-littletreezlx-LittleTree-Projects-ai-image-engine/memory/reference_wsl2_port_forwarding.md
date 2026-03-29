---
name: WSL2 端口转发配置
description: Mac 无法访问 WSL2 内引擎时，需要在 Windows 上配置 netsh portproxy 端口转发
type: reference
---

WSL2 运行在独立虚拟网络中，端口不会自动暴露到 Windows 宿主机的局域网接口。Mac 等外部设备访问引擎 (port 8100) 需要手动配置端口转发。

**Windows PowerShell (管理员) 中执行：**

```powershell
# 1. 在 WSL 终端中运行 hostname -I 获取当前 IP
# 2. 添加端口转发
netsh interface portproxy add v4tov4 listenport=8100 listenaddress=0.0.0.0 connectport=8100 connectaddress=<WSL2_IP>

# 3. 防火墙放行
netsh advfirewall firewall add rule name="AI Image Engine" dir=in action=allow protocol=TCP localport=8100

# 验证
netsh interface portproxy show all
```

**注意**: WSL2 重启后 IP 可能变化，需重新设置 `connectaddress`。
