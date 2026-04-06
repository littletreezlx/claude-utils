---
name: AI Image Studio 项目背景
description: ai-image-studio 的产品定位、架构决策和后端集成信息
type: project
---

AI Image Studio 是独立的个人/家庭文生图 Flutter 客户端（2026-03-28 立项）。

**Why:** 后端 SDXL 引擎（ai-image-engine）已成熟，但 CLI 不适合家人使用，且无法承载灵感的连续演进（纹身设计迭代、回溯对比）。

**How to apply:**
- 项目目录: `ai-image-studio`（Flutter 项目集子目录）
- 后端直连 ai-image-engine（Caddy :8100），不经 device-control 网关
- V1 功能完成（2026-04-06）：生成 → 画廊 → 卡片背板 → 收藏 → 设置 → enhanced_prompt 展示
- 产品定位："家庭画坊"隐喻，暖白极简主题，**不含游戏管线功能**
- forge-studio/ 目录是游戏管线参考设计（HTML mockup），决策为不实现 GUI，保持 CLI + HTML
