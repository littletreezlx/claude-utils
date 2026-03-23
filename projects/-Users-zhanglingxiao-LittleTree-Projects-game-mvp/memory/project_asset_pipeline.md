---
name: asset_pipeline_decisions
description: AI 资产管线架构决策 — manifest v2 多候选 + 批量生成 + 预览 Dashboard
type: project
---

Phase 2 视觉包装的自动化资产管线（2026-03-21 建立，持续迭代）：

**基础设施**：
- `POST /api/v1/self-update` 已就绪，彻底替代 SSH 手动同步
- `POST /api/v1/ai-image/start` 已就绪，ComfyUI 自动启动
- `post_resize` 服务端处理已修复（Pillow 依赖）
- generate.py 内置 auto-start，调用即用

**Manifest v2 多候选管线（2026-03-21 实装）**：
- `assets_manifest.json` v2 — 每个 asset 有 `asset_id`、`candidates[]`、`selected_variant`
- `candidate_config` 全局配置：default_count=5, default_mode=seed_variant, preset=quick
- `tools/batch_candidates.py` — 批量生成脚本，支持 --resume/--count/--tasks/--dry-run
- 生成完自动产出 `staging/dashboard.html` — 纸娃娃式可视化预览
- 混合变体策略：seed 变体（精炼构图）+ LLM prompt 变体（探索方向）

**Dashboard 预览系统**：
- 单文件 HTML，零依赖，浏览器直接打开
- 左侧：候选图库（按资产分组，缩略图网格，双击放大）
- 右侧：1152x648 画布，支持拖拽资产到画布、自由移动位置
- 可导出选择结果（asset_id → variant_id 映射）

**质量策略**：
- 所有资产统一走多候选流程（默认 5 个候选）
- quick preset 用于快速预览迭代，final preset 用于最终产出
- Claude 能看图但看不到 Godot 编辑器中的合成效果 — 最终视觉整合需人工

**风格一致性**：
- v1（当前）：prompt 前缀统一 + seed 记录
- v2（资产 >50 时考虑）：IP-Adapter 参考图控制

**Why:** 单人团队需要"挂机批量生成 + 回头快速挑选"的工业化流程。manifest 驱动保证幂等和断点续传。
**How to apply:** 运行 `python tools/batch_candidates.py` 批量生成 → 打开 `staging/dashboard.html` 挑选 → 将选中的候选复制到 Assets/ 目录。
