# 2026-04-19-02 generate-stories v3.1：digest 梯度约束 + 压缩准则

## 背景

v3.0 落地同日 Founder 在 flametree_pick 跑 Generate Mode，Phase 1 产出 digest.md 244 行（未违反 300 行硬约束），Founder 仍提出两点质疑：

> "digest.md 是每次都要带上是吗？限制 300 行合理吗？这项目已经相对简单了。"

两个问题都准。

## 诊断

### 问题 1：每次子 TASK 都读 digest 是 DAG 架构本质

- 10 条 Story × 244 行 = 2440 行重复读取 ≈ 120k tokens 额外开销
- 这是"独立上下文 = 不偷懒"的架构税
- 相比让每个子会话读 SOUL+BEHAVIOR+features 原文（1000+ 行），digest 已经省很多
- 用户理解这笔账，不需要改架构

### 问题 2：300 行硬约束是拍脑袋的

v3.0 "≤ 300 行，超过 = 压缩失败重做" 的隐含假设：所有项目复杂度相似。实际上：

| 项目复杂度 | 合理 digest 范围 |
|----------|-----------------|
| 简单（单功能 + 几个 feature） | 150-250 行 |
| 中等（多模块 + 主流程分支） | 250-400 行 |
| 复杂（多角色 + 跨模块 + 同步/支付） | 400-600 行 |

硬约束 300 行会误杀中/复杂项目。同时对简单项目的 244 行没有约束（不违反就不反思）。

### 更深：flametree_pick 244 行暴露 v3.0 无压缩准则

v3.0 Phase 1 只说"压缩为事实摘要"，没说**什么该砍 / 什么该留**。AI 默认"先都塞进去"，导致简单项目也产 244 行。

正确原则：
- ✅ 进 digest：所有子 TASK 都可能用到的共享知识
- ❌ 不进 digest：某类 Story 专属的 feature 细节（下沉到"Story TASK 按需读 features/*.md 片段"）

## 决策

**v3.0 → v3.1：digest 梯度约束 + 压缩准则 + 自检 + 分片机制（选用）。**

### 1. 梯度约束替代硬 300 行

| 层级 | 行数 | 处理 |
|------|------|------|
| 目标 | ≤ 300 | 推荐，保持压缩锐度 |
| 软上限 | ≤ 500 | 打印 warning 继续（项目偏复杂，值得二次审视） |
| 硬上限 | ≤ 800 | **Fatal 停**（建议 digest 分片或进一步压缩） |

硬上限 800 行继续满足 CLAUDE.md DAG 强制清单 §3（静默失败拦截器，不允许 `--force` 绕过）。

### 2. 压缩准则表（Phase 1 执行时依据）

Phase 1 严格按下表决定内容：

| 类别 | 进 digest | 不进 digest（下沉） |
|------|----------|---------------------|
| 产品定位 | ✅ 一段话 | ❌ 市场分析 / 长篇 slogan |
| 用户画像 | ✅ 1-2 类核心用户 | ❌ 次要用户群细分 |
| 状态机 | ✅ 核心骨架（主路径 + 关键分叉）| ❌ 全状态枚举 / 边缘错误路径 |
| features | ✅ 功能清单一行描述 | ❌ 每个 feature 的完整交互流（下沉到 features/*.md）|
| 端点 | ✅ `/providers` 全量清单（紧凑格式） | ❌ 每个端点的返回结构细节 |
| 技术栈 | ✅ 核心技术 + 硬限制 | ❌ 开发工具链 / 测试框架细节 |
| 差异化点 | ✅ 核心差异化（1-3 条） | ❌ 竞品对比 / 营销卖点 |
| Known Issues | ✅ 影响 Story 生成的限制 | ❌ 历史 issue 流水账 |

### 3. Phase 1 末尾自检

每个章节/段落自问：**这段是 N 个子 TASK 都会用到的吗？还是只有 1-2 个会用？**

- 多 TASK 通用 → 保留
- 1-2 TASK 专用 → 删除，下沉到"该 Story TASK 按需读 features/*.md 相关段落"

自检不通过（有明显专用内容）→ 重做 Phase 1。

### 4. Digest 分片（高级模式，软上限触发时启用）

当项目复杂到 digest 超 500 行时：

```
.task-generate-stories/
├── digest.md              # 通用部分（产品定位/用户/核心状态机/端点）
├── digest-onboarding.md   # 首次使用相关专用（被 Story 01/02 引用）
├── digest-sharing.md      # 分享相关专用（被 Story 05/06 引用）
└── digest-settings.md     # 设置相关专用（被 Story 09 引用）
```

DAG 入口文件中每个 Story TASK 的"核心文件"显式列出它需要哪个分片：

```
**核心文件**：
- `.task-generate-stories/digest.md` - [参考] 通用
- `.task-generate-stories/digest-sharing.md` - [参考] 分享域专用
- `docs/features/share.md` - [参考] 仅读相关段
```

分片规则：
- 主 digest 仍 ≤ 500 行
- 每个分片 ≤ 300 行
- 分片总数 ≤ 5 个（超过说明项目应该拆多个 skill 或分阶段交付）

## 为什么不选其他方案

### ❌ 完全取消行数约束

"让 AI 自己决定长度" 在 v3.0 实测下会导致简单项目也 244 行。没有约束 AI 就不压缩。必须保留硬上限作为刹车。

### ❌ 引入更复杂的 token-based 约束

（比如 "≤ 10k tokens"）。行数约束 Founder 和 AI 都好理解、好验证（grep 一下就知道）。token 约束需要计算，不直观。

### ❌ 每次都用分片机制（不管项目复杂度）

简单项目分片是过度设计。梯度触发的选用分片是对的：简单项目单一 digest 简单直接，复杂项目分片减少冗余。

### ❌ 让用户在 Phase 1 时手动指定长度

违反 AI-Only 原则。AI 按准则压缩即可，用户不该介入压缩决策。

## 风险与反面检验

- **800 行硬上限对超大项目仍不够**：如果真的遇到（比如整个 SaaS 平台），建议按子域拆多次 `/generate-stories`（比如 `/generate-stories --scope onboarding`），而不是一次生成全量。但这是未来问题，v3.1 不实现。
- **压缩准则表 AI 可能理解偏差**：将 "features 的完整交互流" 错放进 digest。缓解：末尾自检会抓到（"1-2 TASK 专用 → 下沉"）。
- **分片机制引入路径复杂度**：多个 digest-*.md 文件 AI 可能读错。缓解：仅 > 500 行才启用，简单项目不触发。

## 回滚条件

3 个月内观察到：
- 简单项目 digest 仍 200+ 行 → 压缩准则表不够具体，补充示例
- 复杂项目 digest 超 800 行 → Founder 手动分片或接受硬上限拒绝
- 分片机制被频繁触发却没人维护 → 移除分片，改为"拆多个 skill"

## 联动影响

- ai-qa-stories / ai-explore 无影响
- 本次 flametree_pick 已生成的 digest 244 行（< 300 行）可保留继续 batchcc，v3.1 改动主要作用于未来 generate
- 如果 Founder 想重做 Phase 1 获得更紧凑 digest，`rm -rf .task-generate-stories/` 后重跑即可

## 参考

- 前置决策：`2026-04-19-01-generate-stories-v3-true-dag-mode.md`
- CLAUDE.md DAG 强制清单 §3（静默失败拦截器）
- 触发对话：Founder 在 flametree_pick 跑 v3.0 Generate Mode 后质疑 244 行 + 300 行约束合理性
