---
name: AI Image Generation 多项目参考
description: 内网 AI 图片生成服务的三个相关项目路径和文档位置
type: reference
---

## 项目路径（Mac 本地，通过 Git 与 Windows WSL 同步）

| 项目 | Mac 路径 | 角色 |
|------|---------|------|
| ai-image | `~/LittleTree_Projects/ai-image` | 生成引擎（generate.py + ComfyUI） |
| device-control | `~/LittleTree_Projects/device-control` | 网关层（FastAPI + Caddy + 后处理） |
| game-mvp | `~/LittleTree_Projects/game-mvp` | 消费方（Barracks Clash 游戏项目） |

## 关键文档

| 文档 | 路径 | 内容 |
|------|------|------|
| 网关 API 指南（最权威） | `~/LittleTree_Projects/device-control/docs/AI_IMAGE_API_GUIDE.md` | 完整 HTTP API，含 post_resize/transparent_bg/webhook |
| 引擎 API 参考 | `~/LittleTree_Projects/ai-image/docs/API_REFERENCE.md` | 引擎侧 HTTP API 参考（部分过时，缺少后处理功能） |
| 游戏集成工作流 | `~/LittleTree_Projects/game-mvp/docs/AI_IMAGE_INTEGRATION.md` | Barracks Clash 专用的资产生成工作流 |

## 连接信息

- **HTTP API:** `http://192.168.0.121:5001/api/v1/ai-image/`
- **SSH:** `ssh windows`（~/.ssh/config: 192.168.0.121, user: littletree）
- **Git 同步:** Mac 修改 → `ssh windows` 上 `cd ~/LittleTree_Projects/<project> && git pull`

## 架构分工

- `ai-image/generate.py`：纯生成（seed/negative/output-json），不含后处理
- `device-control` handler：后处理层（post_resize/transparent_bg/rembg），异步任务，webhook
- 后处理在 CPU/Pillow/rembg 执行，不占 GPU
