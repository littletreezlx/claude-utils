# FlameTree Company 项目记忆

## 当前运行环境判断

**当前在 NAS (DS224plus) 上运行**，不在 Mac 上。

判断依据：
- `hostname` 输出 `DS224plus`
- 当前目录 `/var/services/homes/littletreezlx/LittleTree_Projects/flametree_company/pikpak-sync`
- `/volume1/video/` 路径存在

## NAS 关键路径

| 路径 | 说明 |
|------|------|
| `/volume1/video/Media_Library` | 媒体库（动漫、电影等） |
| `/volume1/video/PikPak_Sync` | PikPak 同步目标目录 |
| `~/LittleTree_Projects/flametree_company/` | 项目根目录 |
| `/usr/local/bin/` | 宿主机脚本目录 |

## pikpak-sync 项目关键路径

- Adapter 容器：pikpak-adapter（端口 50035）
- 宿主机脚本：`/usr/local/bin/pikpak-sync.sh`
- Rclone RC：`127.0.0.1:5572`
- 代理端口：`7899`（clash-download）

## 注意事项

1. NAS 上所有 Docker 命令必须用：`sudo /usr/local/bin/docker <command>`
2. 同步源：PikPak Cloud → `/volume1/video/PikPak_Sync`
3. `.partial` 文件通常是 rclone 传输残留，不代表同步失败
