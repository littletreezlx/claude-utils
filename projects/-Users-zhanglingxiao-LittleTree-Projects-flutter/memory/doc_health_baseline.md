---
name: doc_health_baseline
description: 2026-03-18 文档健康全绿，329 条失效路径已全部修复
type: project
---

## 文档健康状态（2026-03-18 修复后）

原 329 条 FEATURE_CODE_MAP.md 失效路径已全部修复。当前状态：

| 项目 | 有效路径数 | 状态 |
|------|----------|------|
| flametree_ai | 354 | 🟢 健康 |
| flametree_rss_reader | 174 | 🟢 健康 |
| flametree_music | 163 | 🟢 健康 |
| flametree_pick | 78 | 🟢 健康 |
| littletree_x | 48 | 🟢 健康 |
| flametree_coffee | — | ⬜ 无文档体系 |

**Why:** 历史腐烂源于 flutter_common v2→v3 重构后目录结构大变但文档未同步。主要修复方式是将短路径补全为项目根目录相对路径。
**How to apply:** 日常开发中代码文件新增/删除/重命名后，用 `./scripts/doc-health.sh {project}` 检查是否引入新的路径失效。保持全绿状态。
