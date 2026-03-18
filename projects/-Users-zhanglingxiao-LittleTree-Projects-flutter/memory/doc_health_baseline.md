---
name: doc_health_baseline
description: 2026-03-18 文档健康基线，329 条失效路径需分批修复
type: project
---

## 文档腐烂基线（2026-03-18）

运行 `./scripts/doc-health.sh` 发现 329 条 FEATURE_CODE_MAP.md 失效路径。

| 项目 | 失效/总数 | 严重程度 |
|------|----------|---------|
| littletree_ai | 119/175 | 🔴 严重（68% 腐烂） |
| lt_music | 88/130 | 🔴 严重（68% 腐烂） |
| flametree_rss_reader | 84/107 | 🔴 严重（79% 腐烂） |
| flametree_pick | 38/74 | 🟡 中等（51% 腐烂） |
| littletree_x | 0/48 | 🟢 健康 |
| flametree_coffee | — | ⬜ 无文档 |

**Why:** 项目经历大规模重构（flutter_common v2→v3、目录结构调整），文档未同步更新。
**How to apply:** 日常开发中遇到某项目时，顺手用 `/doc-health.sh {project}` 检查并修复该项目的失效路径。不要一次性全部修复（工作量太大），优先修复当前活跃开发的项目。
