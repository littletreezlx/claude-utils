---
name: 开发环境测试验证的陷阱与改进
description: Docker 容器遮蔽本地服务、nvm 路径缺失、端口冲突等问题的经验教训和改进方案
type: feedback
---

## 陷阱记录

### 1. Docker 容器遮蔽本地服务（最严重）
Docker 容器（nas-content-aggregation 等）长期运行占用 61000/61001/61002 端口，`./dev.sh` 启动本地服务时端口被占，但 curl 测试仍能打通——打到的是 Docker 里的旧代码。导致所有测试结果都是旧代码的输出，浪费大量时间排查。

**Why:** 没有在测试前确认端口归属。`lsof` 和 `fuser` 在 WSL 中对 Docker 端口的显示不一致。

**How to apply:** 测试 Node.js 服务改动前，先运行 `docker ps | grep 6100` 确认无 Docker 容器占用端口。如需停 Docker：`docker stop nas-content-aggregation nas-python-backend nas-frontend`。

### 2. `npm run build` 包含 prompt 文件复制
`nodejs-service` 的 build 脚本是 `tsc && cp -r src/ai/prompts dist/ai/prompts`。单独运行 `npx tsc` 只编译 TypeScript，不会复制 prompt 文件到 dist。改了 prompt 文件后必须完整执行 `npm run build` 或手动 `cp -r src/ai/prompts dist/ai/prompts`。

**Why:** prompt 文件是纯文本 .txt，TypeScript 编译器不处理。

**How to apply:** 改 prompt 文件后不要只跑 `npx tsc`，用完整的 build 命令。

### 3. nvm 路径在非交互 shell 中不可用
`./dev.sh` 和直接 `node` 命令在 Claude Code 的 shell 环境中找不到 Node.js，因为 nvm 没有被加载。

**How to apply:** 需要显式设置 `PATH="$HOME/.nvm/versions/node/v22.21.1/bin:$PATH"` 或使用完整路径。

### 4. 端口占用后 kill 不干净
在 WSL 环境中，`pkill` 和 `kill -9` 有时无法杀掉 Node.js 进程（尤其是 nodemon 启动的子进程），导致新进程 EADDRINUSE。

**How to apply:** 优先使用 `./stop.sh` 停服务。如果仍不行，用 `ss -tlnp | grep 61002` 确认端口状态，必要时 `docker stop` 检查是否是容器。

## 改进建议

1. **在 `dev.sh` 中增加 Docker 冲突检测**：启动前自动检查 `docker ps` 是否有端口冲突的容器，有则提示或自动停止
2. **为 Claude Code 创建一个测试入口脚本**（如 `scripts/test-local-ai.sh`），自动处理：停 Docker → 设 nvm PATH → build → 启动 Node.js → 运行测试 → 显示结果
3. **考虑 `dev.sh` 中 nvm 自动检测**：已有 `未检测到 Node.js` 报错，可加 nvm 自动 source 逻辑
