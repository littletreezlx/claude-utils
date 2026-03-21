---
name: 用户 HA 环境信息
description: 用户的 Home Assistant 硬件环境、已有设备和自动化资产
type: user
---

- 树莓派 4 运行 Home Assistant OS，IP 192.168.0.102
- Mac 为主力开发机，通过 sshfs 挂载 Pi（`sshfs root@192.168.0.102:/addon_configs/b93b5321_appdaemon`）
- 已有 AppDaemon 自动化：玄关开关定时、电热地毯定时、小厨宝工作日控制、TV 蓝牙截屏（ADB+PIL+NAS）
- 有统一的 LoggedHass 基类和 apps.yaml 配置化 entity ID 实践
- NAS: 192.168.0.100（群晖，用于截屏存储）
- 电视: TCL 192.168.0.105 (ADB 控制)
