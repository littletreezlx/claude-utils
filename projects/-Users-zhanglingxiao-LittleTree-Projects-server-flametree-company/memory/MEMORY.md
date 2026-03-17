# FlameTree 项目记忆

## 关键事实 (2026-02-09 审查确认)

### 服务状态
- **MySQL**: 端口 50010（非 50025）
- **LobeChat**: 端口 50033，简化版无 PG/MinIO/Casdoor（lobechat/ 目录，非 lobe-chat-db/）
- **SSL**: acme.sh + 阿里云 DNS (Let's Encrypt ECC)，脚本 `nginx/ssl/renew-acme-cert.sh`
- **已移除服务**: chrome, qbittorrent, auto-bangumi, auto-sub, music-dl, youtube_downloader, navidrome, lobe-chat-db, nas-media-center
- **nas-media-center → pikpak-sync**: 2026-02-22 已删除 nas-media-center 目录，端口 50035 保留给独立项目 `~/LittleTree_Projects/pikpak-sync`
- **非 Docker**: clash (二进制), wireguard (SPK)
- **push_nas_git.py**: 不存在！文档曾错误引用
- **归档目录**: `_archive/tools/`（非 `_archive_tools/`）
- **50028 端口冲突**: Playwright VNC 与 Whisper API 共用

### Nginx 架构 (2026-02-24 变更)
- **网络模式**: `network_mode: host`（原 bridge `flametree_net`，因容器无法访问宿主机 192.168.0.100 导致所有 HTTPS 代理超时）
- **监听端口**: 直接监听 60000(HTTP) / 60443(HTTPS)，不再用容器内 80/443 + 端口映射
- **排查经验**: bridge 网络下 TLS 握手正常但 proxy_pass 超时 → 容器内到宿主机路由失效 → 切 host 模式解决

### 外部依赖
- [Windows Task Agent 远程部署通道](reference_remote_deploy.md) — 部署脚本在 `cs/zsh/remote-win/deploy.zsh`，非本项目

### 文档审查结果
- 2026-02-09 完成全部 7 个核心文档审查
- 修改文件: NAS端口表.md, FEATURES_MAP.md, README.md, ARCHITECTURE.md, DEVELOPMENT.md, CLAUDE.md, TOOLS.md
- 待用户决策: lobe-chat-db/ 空目录是否删除
