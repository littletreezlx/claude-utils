---
name: Ollama Docker 配置要点
description: Ollama 容器 volume 选择、dolphin-nemo 模型配置、WSL2 bind mount 陷阱
type: project
---

Ollama 容器使用 Docker named volume `ollama_data`（非 bind mount）存储模型。

**Why:** WSL2 的 `/mnt/f/` (9P 协议) 不支持 mmap，导致模型只能加载 1/41 层到 GPU；bind mount 到 `/home/` 时容器内 `df` 显示只有 12GB（Docker Desktop 限制），无法容纳两个 7GB 模型。Docker named volume 使用 overlay 存储，支持 mmap 且空间充足（921GB）。

**How to apply:**
- 重建 Ollama 容器时必须用 `-v ollama_data:/root/.ollama`（named volume），禁止用 bind mount 到 `/mnt/` 或 `/home/`
- 当前模型 `dolphin-nemo` = 基于 `CognitiveComputations/dolphin-mistral-nemo` 的自定义模型，`num_ctx=4096`（原版 128K 上下文会 OOM）
- 41/41 层全部在 GPU
- `.env` 中 `OLLAMA_MODEL=dolphin-nemo`
- 容器创建命令: `docker run -d --gpus all --name ollama -v ollama_data:/root/.ollama -p 11434:11434 -e OLLAMA_HOST=0.0.0.0:11434 --restart unless-stopped ollama/ollama`
