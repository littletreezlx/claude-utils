---
name: asset_pipeline_decisions
description: AI 资产管线架构决策 — manifest 驱动、自更新端点、质量门控策略
type: project
---

Phase 2 视觉包装的自动化资产管线决策（2026-03-21，Claude + Gemini 共同讨论）：

**基础设施**：
- `POST /api/v1/self-update` 已就绪，彻底替代 SSH 手动同步
- `POST /api/v1/ai-image/start` 已就绪，ComfyUI 自动启动
- `post_resize` 服务端处理已修复（Pillow 依赖）
- generate.py 内置 auto-start，调用即用

**Manifest 管线**：
- `assets_manifest.json` 是批量执行的机器层，TODO.md 是人类层，通过 task ID 关联
- 状态机：pending → generating → staging → approved → applied → error
- 幂等设计：新会话只执行 `status == pending` 的任务，支持断点续传

**质量策略**：
- 背景类（高影响）：batch=4 多候选 + 人工选择
- 单位/UI 类（可迭代）：单张生成 + Claude 视觉 QA（多模态预览）
- Claude 能看图但看不到 Godot 编辑器中的合成效果 — 最终视觉整合需人工

**风格一致性**：
- v1（当前）：prompt 前缀统一 + seed 记录
- v2（资产 >50 时考虑）：IP-Adapter 参考图控制

**Why:** Gemini 分析指出这套方案本质是 "TA 自动化资源管线" 的单人复刻版，需要 manifest 驱动和质量门控才能规模化。
**How to apply:** 批量执行资产任务时读取 manifest 而非 TODO.md。背景类资产走多候选流程。
