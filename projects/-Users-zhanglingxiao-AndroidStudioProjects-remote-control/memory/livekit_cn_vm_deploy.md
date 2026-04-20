---
name: LiveKit 国内云 VM 部署的踩坑点
description: 在国内云 VM（腾讯云/阿里云/TencentOS）上部署 livekit-server 时几个必知的环境陷阱，避免下次重复消耗
type: project
originSessionId: fe5435a9-75c0-4b7a-80fc-922cf0e3a93c
---
**部署 playbook 主文档**：`docs/远程协助/livekit-server-deploy.md`（照做即可，5-10 分钟完工）

## 非显而易见的核心陷阱（浪费过大量时间）

1. **不要 Docker，直接二进制 + systemd**
   - **Why**：`get.docker.com` 不支持 TencentOS；即使装上 Docker 也多一层网络/日志复杂度。二进制更透明
   - **How to apply**：任何国内云 VM 部 LiveKit 都走 binary，用户明确要 Docker 再改

2. **下载二进制必须走 GitHub 镜像**
   - **Why**：国内到 github.com releases CDN 极不稳，`curl: (56)` 失败率高
   - **How to apply**：用 `https://ghfast.top/https://github.com/...` 前缀镜像在服务器侧下载

3. **GitHub release URL 必须带版本号**
   - **Why**：`/releases/latest/download/<name>` 这个简写路径要求文件名完全匹配，LiveKit 实际文件名是 `livekit_1.10.1_linux_amd64.tar.gz`（带版本），简写 `livekit_linux_amd64.tar.gz` 会 404
   - **How to apply**：先 `curl api.github.com/repos/.../releases/latest | grep browser_download_url` 拿真实 URL

4. **不要 scp 大文件上腾讯云**
   - **Why**：家庭宽带上行带宽低（~1MB/s）且连接易断，16MB 可能传 3 分钟还挂
   - **How to apply**：让服务器直接从镜像下载，scp 只用于 <1MB 的配置文件

5. **LiveKit 没有"禁用 UDP"的配置开关**
   - **Why**：livekit.yaml 里无此选项；服务器启动时仍会广播 UDP host candidate（默认 50000-60000 range）
   - **How to apply**：TCP-only 测试时只能靠云安全组阻断 UDP，接受客户端首帧 3-5s 的 UDP 超时 fallback 延迟；不要花时间找"disable UDP"的配置

6. **`gen-token.mjs --profile X --write` 一次回写三处**
   - **Why**：这脚本同时更新 `envs/X.env` 引用的 token、`local.properties`（Android BuildConfig）、`tools/web-console/config.local.js`（web 端）
   - **How to apply**：改完 env 文件跑 `npm run use:<profile>` 即可，**不要手改** local.properties 或 config.local.js（会被覆盖）

7. **改完 server URL 必须 `pm clear` 客户端**
   - **Why**：AppViewModel 启动时 DataStore 优先于 BuildConfig，只 installDebug 不 pm clear 客户端仍连旧地址
   - **How to apply**：`adb shell pm clear com.shiheng.remotecontrol`（副作用：会清无障碍授权，需手动重开）

## 已验证工作的目标服务器

- 腾讯云 **124.220.9.200**（TencentOS 4.4，2C3.5G，对应 `envs/cn-vm.env`）
- 已废弃：146.56.216.121（原 cn-vm 指向，未知云厂商）
