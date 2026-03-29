---
name: project-renamed-to-ai-image-engine
description: ai-images project renamed to ai-image-engine with built-in FastAPI HTTP API (2026-03-28)
type: project
---

Project renamed from `ai-images` to `ai-image-engine` on 2026-03-28.

**Why:** The project evolved from a CLI tool to a standalone HTTP service. device_control's 600-line handler was essentially engine logic misplaced in a proxy layer.

**How to apply:**
- Directory is now `~/LittleTree_Projects/ai-image-engine/`
- GitHub remote is still `ai-image.git` (not renamed yet)
- HTTP API at port 8100 (`python server.py`)
- device_control now uses `AI_IMAGE_ENGINE_URL=http://localhost:8100` to proxy requests
- `generate.py` CLI still works as before (thin adapter over `services/engine.py`)
