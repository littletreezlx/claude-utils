---
name: user_adb_connection
description: 用户默认 ADB 连接配置（WSL2 + Android 手机）
type: user
originSessionId: ca1294e1-a2ba-4572-b193-c8a656de6f53
---
## 默认 ADB 连接

- **地址**: `192.168.0.51:5555`
- **环境**: WSL2
- **触发方式**: 如果用户不说明，则默认使用此连接

**Why:** 用户在 WSL2 环境下开发 Flutter/Android，每次连接手机不需要重复说明。
**How to apply:** 当用户提到"android"、"adb"、"手机"、"设备"时，默认使用 `adb connect 192.168.0.51:5555`。
