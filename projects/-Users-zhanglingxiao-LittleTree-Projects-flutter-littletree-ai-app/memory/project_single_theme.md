---
name: 单一主题决策
description: LittleTree AI 暂不支持深色/浅色切换，仅使用 Espresso Dark 主题
type: project
---

LittleTree AI 项目暂时不考虑深色模式/浅色模式切换，仅使用单一的 Espresso Dark 主题。

**Why:** 用户明确指出不需要主题切换功能，当前阶段专注于打磨单一视觉体验。

**How to apply:**
- 不维护 light/dark 两套色值，所有 UI 代码直接使用 Espresso Dark 色板
- 移除或忽略 ThemeMode 切换相关逻辑
- AppColors / AppColorsDark 合并为单一色值系统
