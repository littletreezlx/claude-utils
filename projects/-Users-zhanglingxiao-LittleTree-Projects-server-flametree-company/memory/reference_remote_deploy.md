---
name: Windows Task Agent 远程部署通道
description: Mac 通过 Windows Task Agent (port 5000) 远程触发 NAS 服务部署的完整链路，脚本位于 cs/zsh 项目
type: reference
---

flametree_company 的远程部署通道由外部项目 `~/LittleTree_Projects/cs/zsh/remote-win/` 维护：

- **deploy.zsh**: 定义 `deploy-win-nas` 等 zsh 函数，通过 HTTP POST 触发 Windows Task Agent
- **Task Agent**: Windows 上的 HTTP 服务 (port 5000)，接收请求后执行 `git pull` + `deploy-win.sh --smart`
- **环境变量**: `TASK_AGENT_URL` 默认 `http://windows:5000`
- **链路**: Mac → HTTP → Windows Task Agent → git pull → deploy
