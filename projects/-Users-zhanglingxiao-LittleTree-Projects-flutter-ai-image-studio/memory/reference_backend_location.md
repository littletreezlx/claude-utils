---
name: Backend Project Location
description: ai-image-engine 后端项目在 Mac 和 Windows 上的路径，以及部署方式
type: reference
---

- **Mac 本地路径**: `~/LittleTree_Projects/ai-image-engine`
- **Windows 部署**: 通过 SSH `windows` (192.168.0.121) 访问，项目在 `~/LittleTree_Projects/ai-image-engine`
- **技术栈**: FastAPI + Uvicorn + ComfyUI (SDXL 图像生成)
- **默认端口**: 8100 (`AI_ENGINE_PORT` env var)
- **Flutter 客户端连接**: `http://windows:5001` (可能有反向代理)
- **API 前缀**: `/api/v1/ai-image/` (2026-03-29 修复对齐)
