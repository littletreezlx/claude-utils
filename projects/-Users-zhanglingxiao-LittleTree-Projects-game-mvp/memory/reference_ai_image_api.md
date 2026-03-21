---
name: AI Image Generation API
description: 内网 Windows 机器上的 AI 图片生成服务，用于游戏美术资产生产
type: reference
---

- **API 地址：** `http://192.168.0.121:5001/api/v1/ai-image/`
- **SSH 访问：** `ssh windows`（~/.ssh/config 已配置）
- **GPU：** RTX 4070 Ti, ComfyUI 后端，需手动启动 (`~/flux-ctl start`)
- **模型：** hassaku（anime/illustration, 推荐用于 KR 风格）、prefect_pony、cyber_realistic
- **项目集成文档：** `docs/AI_IMAGE_INTEGRATION.md`
- **关键参数：** 游戏资产建议 `no_llm: true` + `hassaku` + 手动 prompt
