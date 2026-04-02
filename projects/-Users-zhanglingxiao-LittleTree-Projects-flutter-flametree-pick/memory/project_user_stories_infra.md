---
name: User Stories 基础设施与 AI 自主测试体系
description: docs/user-stories/ 统一格式、ai-qa-stories + ai-explore 双 skill 架构、generate-stories 生成流程、与现有 skill 生态的联动
type: project
---

## 核心决策（2026-04-01 与 Gemini 两轮讨论后锁定）

### 用户故事文档体系
- 统一用 `docs/user-stories/` 目录（不分项目大小）
- 格式：**意图-执行(curl)-断言** 三段式（见 `flutter/docs/USER_STORIES_TEMPLATE.md`）
- curl 中用 `$PORT` 变量，不硬编码端口

**Why:** 两次 AI QA 实战（Claude Code in RSS, MiniMax in Music）暴露核心问题——AI 只做 API 扫描不做用户旅程测试。根因是缺乏结构化的用户故事输入。

**How to apply:** 新项目先 `/generate-stories` 生成初稿 → 人工审核 commit → `/ai-qa-stories` 消费执行

### Skill 拆分
- `ai-qa-stories`：剧本执行（回归测试，高频，确定性）
- `ai-explore`：启发式探索（发现未知，低频，开放性）— 自动先跑 stories 作为基线
- `generate-stories`：从 SOUL + BEHAVIOR + features/ 生成 user-stories 初稿

**Why:** 两种本质不同的活动——验证已知 vs 发现未知。拆分后可独立触发，也允许不同频率使用。

### "ai-" 前缀的含义
ai-qa-stories 和 ai-explore 使用 "ai-" 前缀，区别于其他 skill。这标记的不是"AI 执行"（所有 skill 都是），而是"AI 自主闭环"——从发现到验证到修复的完整链路，不需要人类介入。

### 模型一视同仁
不为不同能力模型设计不同路径。输入质量（user-stories 的完整度）决定输出质量，不是模型特定引导。

### 文档边界（易混淆的三者）
- **BEHAVIOR** = 系统规则（状态机视角）
- **user-stories** = 用户叙事（用户视角）+ 可执行验证
- **features/** = 工程设计（实现视角）

### 防腐策略
以 QA 执行失败倒逼文档更新——curl 返回 404 或断言失败 = 故事过时。

### 生成与执行分离
生成故事和执行验证必须分离。如果 AI 既写剧本又演剧本，无法区分"App 有 bug"还是"剧本写错了"。

### Skill 联动
- `delivery-workflow` Step 1: 检查变更是否影响 user-stories
- `consistency-check` Step 4: 抽查 user-stories 存活性
- `doc-update-context`: 已知文档结构包含 user-stories
