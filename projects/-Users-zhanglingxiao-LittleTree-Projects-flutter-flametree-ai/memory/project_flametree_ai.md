---
name: project_flametree_ai
description: flametree_ai 前后端分离项目，ai-qa-stories 时需 AI 自主启动后端
type: project
---

## 项目架构

- **前端**: `app/` (Flutter macOS/iOS/Android)
- **后端**: `server/` (独立 Node.js 服务)
- **Debug Server**: 内嵌在 Flutter app 中，端口 8793

## ai-qa-stories 执行规则（重要！）

**执行 `/ai-qa-stories` 时，必须自行启动 backend 服务：**

1. 启动 App 前，先启动 `server/` 目录下的后端服务
2. 后端启动命令参考：`cd server && npm run dev` 或 `pnpm dev`
3. 确认后端就绪后，再启动 Flutter app
4. 整个 QA 会话只启动一次 App，最多重启 1 次

**Why:** flametree_ai 是前后端分离架构，Debug Server 负责 app 状态管理，但 LLM 调用需要独立的后端服务。若后端未启动，session 选择后报"网络连接失败"。

## 已知状态

- **AI 回复网络错误**：QuickAsk 发送消息后 AI 回复"⚠️ 网络连接失败"，即使 server 在运行（端口 61003）。根因待查。
- **Debug Server 端点缺失**：`/data/images` 端点不存在，Story 04 验证失败。

## QA 验证记录 (2026-04-06)

| 故事 | 结果 |
|------|------|
| 01-first-time-user | 🐛 AI 回复网络错误 |
| 02-daily-chat | 🐛 AI 回复网络错误 |
| 03-document-organization | ✅ 端点正常 |
| 04-ai-drawing | 🐛 /data/images 端点缺失 |
| 05-role-management | ✅ 端点正常（已知限制：/data/roles 不存在） |

## 如何应用

执行 ai-qa-stories 时，先启动 server，再启动 app，最后执行验证。
