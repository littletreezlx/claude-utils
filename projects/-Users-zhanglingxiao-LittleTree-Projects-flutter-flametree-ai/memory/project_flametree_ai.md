---
name: project_flametree_ai
description: flametree_ai 前后端分离项目，ai-qa-stories 时需 AI 自主启动后端
type: project
originSessionId: 9072f0a2-a8f8-47c7-b160-da9d7825e23b
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

## QA 执行规则更新 (2026-04-07)

执行 `/ai-qa-stories` 时，**必须自行启动 backend 服务**：

1. 先杀掉可能残留的 App 和 server 进程
2. 启动后端: `cd server && pnpm dev`（端口 61003）
3. 确认后端就绪后，再启动 Flutter app
4. 等待 App Debug Server 就绪（端口 8793）
5. 执行 QA 验证

**启动顺序很重要**：后端 → App，否则 App 启动时会立即崩溃（RoleSyncViewModel disposed ref bug）

## 已发现 Bug

**Riverpod disposed ref bug** (2026-04-07):
- `RoleSyncViewModel._updateInitialState` 在 provider disposed 后仍使用 ref
- 导致 App 启动时崩溃：`Cannot use the Ref of roleSyncViewModelProvider after it has been disposed`
- 出现在 App 启动阶段，影响 iOS Simulator

## QA 文件勘误 (2026-04-11)

**QA 文件 jq 路径问题（已全部修正）：**
- Debug Server 所有端点返回 `{ok: true, data: {...}}` envelope 格式
- 所有 state/data 端点的 jq 路径必须加 `.data` 前缀（如 `jq '.data.isAuthenticated'`）
- action 响应路径：`.ok` 在顶层，`.result.success` 在 `.result` 下

**已修正的具体问题：**
- Story 01: 所有 `.isAuthenticated` → `.data.isAuthenticated`；S4 改用 chatData state
- Story 02: overlay/roles/quickAsk 路径均已修正
- Story 03: organizeTasks 路径已修正
- Story 04/06: `/data/images` 端点实际存在（之前 QA 文件说不存在，已更正）
- Story 05: `.success` → `.result.success`
- Story 07: providers 路径 `.actions` → `.data.actions`

**新增 Debug 端点 (2026-04-11)：**
- `roles/switch` — 调用 `globalRoleStateViewModelProvider.notifier.setActiveRole(roleId)`
- `compareSessions/create|delete|select|exitCompareMode` — 对比会话 CRUD
- `compareChat/load|sendMessage|stopGenerating` — 对比聊天消息
- `state/compareSessions|compareChat` — 状态读取

**其他 QA 场景说明：**
- Story 01 S3: `/state/roles` 无 `selectedRoleId`，通过 `roles/switch` action 切换
- Story 02 S1/S2/S4: 需要键盘输入，无法自动化
- Story 05 S3/S4: `roles/sync` 和 `forceFullSync` 返回 `success: false` 是正常的（无 pending changes）
- Story 07: 右侧 Claude 可能因 API 限流返回空内容，非端点 bug

## P3 审查发现 (2026-04-06)

**user-stories 与 Debug Server API 不一致（已修正）：**
- `/data/messages` 需要 `sessionId` query 参数（Story 01, 05）
- `quickAsk` state 无 `isVisible` 字段，应用 `/state/overlay.isOverlayVisible` 替代
- 响应结构无 `.data` 包裹层：`quickAsk` 直接 `.messages`，`organizeTasks` 直接 `.tasks`，`images` 直接 `.images`

## Voice Agent (Phase 0A ✅, Phase 0B ⏳)

**状态**: Phase 0A Server 端管线验证 100% 完成 (2026-04-12)
**文档**: `docs/features/voice-agent/` 含完整文档体系
**延迟基线**: TTFT p50=11.6s (macOS 本地测试，~5.76s 中文语音)

**下一步**: Phase 0B - 用户可选 Android 手机测试（室内 WiFi）或比亚迪 DiLink 车机测试

**快速启动 voice agent 测试**:
```bash
# 1. 启动后端
cd server && pnpm dev > /tmp/server.log 2>&1 &

# 2. 跑端到端延迟回归
cd server && npx tsx scripts/smoke-cascade-latency.ts 3
```

## 如何应用

执行 ai-qa-stories 时，先启动 server，再启动 app，最后执行验证。

**启动命令（2026-04-11 确认）：**
1. `pkill -9 -f "flametree" && pkill -9 -f "flutter"` 清理
2. `cd server && pnpm dev > /tmp/server.log 2>&1 &`（端口 61003）
3. 等待 10 秒后 `cd app && flutter run -d macos > /tmp/flutter.log 2>&1 &`（端口 8793）
4. 等待 30 秒后 curl localhost:8793/providers 确认
