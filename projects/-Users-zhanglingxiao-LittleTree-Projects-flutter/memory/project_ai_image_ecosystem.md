---
name: AI 图片生态三项目协作关系
description: ai-image-engine / ai-image-studio / game-mvp 三项目的协作拓扑、API 契约和职责边界
type: project
---

三个项目围绕 AI 图片生成形成供需生态（2026-04-06 统一整合完成）。

## 架构拓扑

```
ai-image-engine（底层引擎，Python/FastAPI + ComfyUI）
        │
    Caddy (:8100)
     ┌───┴───┐
ai-image-studio    game-mvp (Barracks Clash)
(Flutter macOS)    (Godot 4.6 游戏)
 家庭创作端         游戏资产管线
```

## 职责边界

| 项目 | 定位 | 关键能力 |
|------|------|---------|
| **ai-image-engine** | "引擎，不是汽车" — 底层生成能力 | txt2img / img2img / inpaint / 元数据 sidecar / Multi-LoRA / 后处理 |
| **ai-image-studio** | "家庭画坊" — To-C 创作工具 | 单张生成 / 画廊历史 / enhanced_prompt 展示 / **不含游戏功能** |
| **game-mvp** | 游戏 + 资产管线 — To-Dev 工具链 | manifest 声明式系统 / batch_candidates.py / apply_candidate.py / build_dashboard.py |

## API 契约

- 统一直连 Engine（Caddy :8100），**不经 device-control 网关**
- API 权威参考: ai-image-engine 的 `docs/API_REFERENCE.md`
- 每张生成图有同名 `.json` sidecar（元数据持久化）
- `/generate` `/img2img` `/inpaint` 响应均包含 `enhanced_prompt` 字段

## 关键决策（2026-04-06 与 Gemini 讨论确认）

- **forge-studio 不做 GUI**：游戏资产管理保持 CLI + HTML dashboard，不新建 Flutter 项目
- **device-control 退出图片链路**：统一直连 Engine，减少网络跃点
- **Engine 做厚，上层做薄**：所有图像处理能力下沉到 Engine
- **风格一致性短期方案**：元数据血统追踪（seed + actual_params）+ Multi-LoRA；中长期靠 IP-Adapter（Engine Phase 3）

**How to apply:**
- 修改 Engine API 时检查两个消费方是否需要同步
- game-mvp 的 `art_pipeline/manifests/config.json` 中 `api_base` 指向 Engine
- studio 和 game 的连接方式不同（studio 用 hostname `windows`，game 用 IP `192.168.0.121`），但指向同一个 Caddy :8100
