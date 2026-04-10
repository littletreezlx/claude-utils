---
name: CLAUDE.md 拆分决策
description: 三服务 monorepo 应使用 1+2 拆分模式的 CLAUDE.md（根+pythonapi+nodejs-service），不要合并为单一文件
type: feedback
originSessionId: fa215f71-c167-4abf-bfe6-15ef4691302a
---
CLAUDE.md 采用 1+3 拆分架构：根(纯系统总览) + src/(前端) + pythonapi/ + nodejs-service/。

**Why:**
1. Claude Code 运行时按需加载子目录 CLAUDE.md，拆分后 Agent 在各服务工作时只看到相关指令
2. 条件指令（"如果在 nodejs 目录则用 Vitest"）降维为绝对指令，减少 Agent 推理错误
3. 三服务通过 HTTP 通信、代码级完全独立，指令架构应映射物理架构
4. 爆炸半径隔离：单服务工具链变更不会误伤其他服务的规则

**How to apply:**
- 修改某个服务的开发规范时，更新该服务的 CLAUDE.md，不要改根文件
- 根 CLAUDE.md 只放：系统拓扑、跨服务命令（dev.sh/deploy/flywheel）、全局禁止事项
- 前端规则放 src/CLAUDE.md（BaseRouteHandler 定义在 src/server-api/，工作时必然访问 src/）
- 新增全局规则时放根 CLAUDE.md，服务特异性规则放对应服务的 CLAUDE.md
