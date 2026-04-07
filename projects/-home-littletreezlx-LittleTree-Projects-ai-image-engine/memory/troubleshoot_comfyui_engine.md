---
name: troubleshoot_comfyui_engine
description: ComfyUI 和 AI Image Engine 联合排查指南
type: reference
---

## 排查经验

### 关键脚本：~/comfyui-ctl

ComfyUI 在 Windows 上运行，通过 `~/comfyui-ctl` 控制。

| 操作 | 命令 |
|------|------|
| 启动 | `~/comfyui-ctl start` |
| 停止 | `~/comfyui-ctl stop` |
| 状态 | `~/comfyui-ctl status` |
| 日志 | `~/comfyui-ctl log` |

**代码路径依赖**：`core/comfy_utils.py` 中 `FLUX_CTL_PATH = ~/flux-ctl`，但实际脚本名是 `~/comfyui-ctl`。需建 symlink：
```bash
ln -s ~/comfyui-ctl ~/flux-ctl
```

### 有效风格列表

`style` 参数有效值：`default, anime, watercolor, wc, cg, scene, minimal, custom`

**无效值**：`base` — 会抛异常导致任务卡在 running

### 从 WSL 管控 Windows 进程

通过 `powershell.exe -Command` 或 `cmd.exe /c` 在 WSL 内执行 Windows 命令：

```bash
# 查找端口占用
powershell.exe -Command "Get-NetTCPConnection -LocalPort 8188"

# 杀掉进程（PID）
powershell.exe -Command "Stop-Process -Id <PID> -Force"

# 找 ComfyUI PID（监听 8188）
powershell.exe -Command "Get-NetTCPConnection -LocalPort 8188 | Select-Object OwningProcess"
```

### AI Image Engine 服务（systemd in WSL）

服务名：`ai-image-engine`，由 WSL systemd 管理，**不是 Windows 服务**（不能用 `sc` 或 `Get-Service` 查看）。

**从 Windows PowerShell 重启 WSL systemd 服务**（绕开 sudo 密码）：
```bash
powershell.exe -Command "wsl.exe -e bash /home/littletreezlx/LittleTree_Projects/ai-image-engine/ops/engine-ctl.sh restart"
```

**从 WSL 内重启**（需要 sudo）：
```bash
sudo systemctl restart ai-image-engine
sudo systemctl status ai-image-engine
```

**wslrelay** 是 WSL 到 Windows 的桥接进程（PID 不固定，如 19064）。它监听 Windows 端的 127.0.0.1:8101 并转发到 WSL 内的服务。杀 wslrelay 会断 FastAPI，Windows 会自动重启新的 wslrelay 实例（同时 systemd 会拉起新的 ai-image-engine）。

### 典型故障判断

| 现象 | 原因 |
|------|------|
| `ComfyUI is not running` 但 ComfyUI 实际在线 | `~/flux-ctl` 不存在 → `ln -s ~/comfyui-ctl ~/flux-ctl` |
| 任务卡 `running`，ComfyUI 队列空 | **Bug: `style='base'` 无效**；或 `workflow=` 参数重复传入 |
| ComfyUI 有任务，引擎状态不更新 | wslrelay 异步事件循环卡死 → 重启服务 |
| ComfyUI history 有任务但 `status=None` | 任务提交了但从未执行（workflow 节点问题） |

### 已知 Bug（已修复）

1. **`workflow=` 重复参数**：commit `49105e0` 把 `load_and_submit_workflow()` 签名从 `workflow_path + workflow_kwarg` 合并成单一参数，但 9 处 `services/*.py` 调用未同步更新，造成 `TypeError: got multiple values for argument 'workflow'`。已修复。
2. **`style='base'` 不存在**：有效值是 `default, anime, watercolor, wc, cg, scene, minimal, custom`。
