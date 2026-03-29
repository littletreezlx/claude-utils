---
name: AI Image Studio 项目背景
description: 新 Flutter 项目 ai-image-studio 的产品定位、架构决策和后端集成信息
type: project
---

AI Image Studio 是独立的个人/家庭文生图 Flutter 客户端（2026-03-28 立项）。

**Why:** 后端 SDXL 引擎（ai-image-engine）已成熟，但 CLI 不适合家人使用，且无法承载灵感的连续演进（纹身设计迭代、回溯对比）。

**How to apply:**
- 项目路径: `~/LittleTree_Projects/flutter/ai-image-studio`
- 后端直连 ai-image-engine（不经 device-control 网关），API: `http://windows:5001/api/v1/ai-image/*`
- 后端源码: `~/LittleTree_Projects/ai-image-engine`
- 需求文档: `ai-image-studio/docs/PRODUCT_REQUIREMENTS.md`
- forge-studio/ 目录是游戏管线参考设计（暗色主题），本项目采用暖色极简
- 关键决策: 不放进 FlameTree X（心智模型冲突）、不融入 FlameTree AI（架构不同）、不含 game 管线功能
