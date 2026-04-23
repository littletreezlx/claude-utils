---
name: project-path-migration
description: 项目从 flametree_company 迁移到 docker-server，已完成路径修复和容器清理
type: project
originSessionId: 4aaf52d6-1f9c-41dc-bb7d-22bba8169437
---
## 迁移完成状态

**项目路径**: `~/LittleTree_Projects/flametree_company` → `~/LittleTree_Projects/server/docker-server`

**已处理**:
- ✅ `pikpak-sync/systemd/autolink-watch.service` 路径更新
- ✅ 系统服务 `/etc/systemd/system/autolink-watch.service` 更新并重启
- ✅ Playwright 容器重新部署（50032 端口恢复）
- ✅ 清理已停止容器: mkvtoolnix, lobechat, 115-browser, mysql-server, festive_booth

**未处理**:
- ⚠️ 5 个 unhealthy 服务: xiaoai-server, cloudflared, miniflux, gotify, yacd（需要排查）
- ⚠️ `_archive/` 目录仍包含旧路径引用（废弃文件，无需处理）

**关键文件位置**:
- autolink-watch.service (系统): `/etc/systemd/system/autolink-watch.service`
- autolink-watch.service (源码): `pikpak-sync/systemd/autolink-watch.service`
- Playwright noVNC: `http://192.168.0.100:50032/vnc.html`
