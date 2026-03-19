# 防呆工程哲学 (Poka-Yoke for AI)

> **日期**: 2026-03-19
> **来源**: Claude Code + Gemini Think 协作讨论
> **适用范围**: 全局——所有 AI 辅助维护的项目

---

## 核心原则

> **能编码进约束（脚本、Lint、测试）的规则不写文档。**
> 对无状态的 AI，可执行的检查永远优于文档描述。

## 为什么

传统的项目文档为"有记忆的人类"设计——渐进式、叙事性、有大量解释。但 AI（Claude Code）每次会话完全无状态。让它"读文档记住规则"有两个根本性问题：

1. **不可靠**：AI 可能不完整理解，或在复杂上下文中遗忘
2. **不可验证**：你无法确认 AI 是否真的遵守了文档中的规则

**Gemini 的关键洞察**（2026-03-19 讨论）：

> "你在用碳基生物的社会学模型（积累信任、反思错误）套用在硅基的无状态请求上。
> 正确的解法不是教 AI 记住错误，而是让系统物理阻止相同的错误再次发生。"

## 三支柱架构

| 支柱 | 替代什么 | 示例 |
|------|---------|------|
| **Bootloader** (scripts/) | AI 手动读 8-12 个文件 | `ai-preflight.sh` SessionStart hook |
| **Contract Tests** (test/architecture/) | CLAUDE.md 中的规范描述 | 层级依赖、耦合守护、代码规范测试 |
| **Context Radar** (scripts/) | AI 启动时全局加载文档 | `get-context.sh` 按需拉取（P2） |

## 实践指南

### 遇到新规则时

```
❌ 在 CLAUDE.md 写一条规范
✅ 问自己：能不能写成测试/lint/脚本检查？
   → 能：写测试，CLAUDE.md 只引用测试文件
   → 不能（如产品哲学）：写文档
```

### 遇到 AI 犯错时

```
❌ 在 FAILURE_LOG.md 记录失误
✅ 把失误转化为：
   → 测试（回归守护）
   → 脚本检查（preflight alert）
   → lint 规则（编译时拦截）
```

### 已否决的方案

| 方案 | 否决原因 |
|------|---------|
| AI 失误日志 (FAILURE_LOG.md) | AI 无法从文字学习，失误应转化为测试 |
| 信任阶梯 (TRUST_PROFILE.md) | 对无状态 AI 无意义，可能制造安全隐患 |
| 更多规范文档 | 用文档解决文档过多问题，南辕北辙 |

## 相关文件

- `~/.claude/docs/AI_PREFLIGHT_DESIGN.md` — Hook 设计说明
- `/flutter/CLAUDE.md` 核心原则第 5 条 — 防呆工程声明
- `/flutter/flame_tree_pick/docs/superpowers/specs/2026-03-19-ai-maintainability-design.md` — 完整设计 spec
- `/flutter/flame_tree_pick/test/integration/architecture/` — Contract Tests 实现
