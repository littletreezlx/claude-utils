---
name: project-split-local-images-ai-images
description: 2026-03-20 项目拆分 — ai-image 重命名为 local-images (R18), 新建 ai-images (SFW SDXL)
type: project
---

项目已拆分为两个独立项目:

- `~/local-images` — R18 项目 (原 `~/ai-image`, 2026-03-20 重命名)
- `~/LittleTree_Projects/ai-images` — SFW 通用文生图 (SDXL-based, 2026-03-20 新建)

**Why:** R18 内容(风格系统/LLM prompts/scenes/characters)会污染 SFW 工作流, AI 上下文也被 R18 术语干扰。SFW 项目可能需要 Git 与 Mac 同步, R18 项目仅在 WSL 本地使用。

**How to apply:**
- local-images 修改共享核心模块 (comfy_utils, lifecycle, workflow_nodes, lora_config, lora_stack, extractors) 时, 需检查是否同步到 ai-images
- 新建 ai-images 以 SDXL 为基础 (非 Flux), 因 12GB 显卡上 SDXL 快 10x + LoRA 训练可行
- 两个项目的 model_registry, style/tag 系统, llm_client, prompts 各自独立维护
- Shell 别名需从 `~/ai-image` 更新为 `~/local-images` (windows-ai.zsh, windows.zsh)
