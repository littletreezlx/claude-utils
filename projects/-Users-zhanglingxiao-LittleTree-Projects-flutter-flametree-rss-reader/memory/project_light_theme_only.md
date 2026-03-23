---
name: 仅亮色主题决策
description: RSS Reader 暂不考虑暗色模式，移除 Dark/OLED 主题，只保留 Light Theme (Warm Study)
type: project
---

RSS Reader 当前阶段只保留亮色主题（Light Theme - "Warm Study"），移除暗色模式和 OLED 模式。

**Why:** 产品处于视觉重构阶段，聚焦亮色主题的品质打磨，避免同时维护三套主题的成本。暗色模式分散精力且当前优先级低。

**How to apply:**
- 修改主题系统时只处理 Light Theme
- 移除 AppThemeMode.dark、OLED 相关代码和 Token
- 主题切换功能暂时移除
- 相关英文设计文档（DESIGN_PHILOSOPHY.md 等）需同步更新此决策
