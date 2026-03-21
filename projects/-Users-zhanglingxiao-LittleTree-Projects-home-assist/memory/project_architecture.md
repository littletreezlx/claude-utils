---
name: HA 项目架构决策
description: home-assist 项目的双模式架构（API-first + AppDaemon）及目录结构、同步策略等核心决策
type: project
---

## 架构决策（2026-03-21 与 Gemini 讨论确定）

**双模式架构**：
- `scripts/` — API-first 部署脚本（Mac 执行，REST + WebSocket 推送到 HA）
- `appdaemon/` — 运行时引擎（rsync 部署到 Pi，处理需要 subprocess/PIL 等的复杂逻辑）

**Why:** 两者互补：API 脚本创建 HA 原生自动化（简单定时/联动），AppDaemon 处理需要 Python 生态的复杂逻辑（ADB 截屏等）。

**How to apply:**
- 简单自动化（定时、状态触发）→ `scripts/setup_automations.py` 部署为 HA 原生
- 需要外部依赖/subprocess/复杂状态 → `appdaemon/apps/`
- 同步策略：rsync 做部署，sshfs 做按需调试（`tail -f` 日志）
- ha_api.py 需包含 REST + WebSocket（entity_registry/device_registry 操作只能走 WS）
- Namespace cleanup：所有 API 部署的自动化 ID 加前缀，部署时 diff + 删除 orphans

**ha-config-as-code 参考项目**：取其模式（API 封装 + 幂等脚本），不照搬代码（entity ID 是别人家的）。

**Pi 连接信息**：`root@192.168.0.102`，AppDaemon 路径 `/addon_configs/b93b5321_appdaemon`
