---
description: 项目文档结构管理 + Gemini Context Hub 同步 ultrathink
---

# 项目文档上下文管理

## 目标

维护项目的标准化 `docs/` 文档结构，并同步到 `~/.gemini-context-hub/` 供 Gemini 跨项目读取。

检查 → 初始化/更新 → 同步到 Hub

---

## 标准文档结构

### 核心三文档（docs/ 下，按更新频率分层）

```
docs/
├── PRODUCT_SOUL.md    # [极少变] 产品愿景、设计隐喻、情感目标、核心哲学
├── ARCHITECTURE.md    # [中频]   技术架构、数据流、技术决策、目录结构
└── ROADMAP.md         # [高频]   当前状态、Known Issues、Next Steps、待办
```

**PRODUCT_SOUL.md** — 产品灵魂
- 一句话定义、核心设计隐喻、情感目标
- 目标用户画像、产品哲学
- 设计语言（Design Tokens、色彩系统、交互质感）
- 给 Gemini 的协作备注
- 写一次几乎不改，除非产品方向大转

**ARCHITECTURE.md** — 技术架构
- 技术栈速查、目录结构说明
- 核心数据流（Mermaid 图）
- 关键技术约束（Local-First / Offline-ready 等）
- 核心界面与交互逻辑（页面构成、导航架构）
- 深度特性分析（选 1-2 个最有特色的功能）
- 分层架构、错误处理、依赖注入等技术设计

**ROADMAP.md** — 动态状态
- TL;DR 快速总览（当前阶段、完成度）
- 已实现功能速查表
- Known Issues（按优先级排列）
- Next Steps（等待决策的可选方向）
- 健康度评分、技术债务汇总
- TODO/FIXME 扫描结果

### 其他 docs/ 文档（独立职责，不合并到核心三文档）

| 文件 | 职责 |
|------|------|
| `docs/FEATURE_CODE_MAP.md` | 功能→代码路径索引（"改这个功能改哪个文件"） |
| `docs/ui/UI_SHOWCASE.md` | 设计系统工程参考（Token 值、组件参数、截图规范） |

### 根目录只留入口文件

| 文件 | 理由 |
|------|------|
| `README.md` | 人类入口 |
| `CLAUDE.md` | AI 入口 |
| `TODO.md` | `/todo-write` + `/todo-doit` 的工作文件 |

---

## 执行流程

### Step 1: 检查 docs/ 结构

扫描项目：
- `docs/PRODUCT_SOUL.md` 是否存在？
- `docs/ARCHITECTURE.md` 是否存在？
- `docs/ROADMAP.md` 是否存在？

**缺失文件**：通过阅读项目代码和现有文档，自动生成。

**已存在**：检查 `ROADMAP.md` 是否需要更新（扫描 TODO/FIXME、对比功能完成度）。

### Step 2: 同步到 Gemini Context Hub

目标目录：`~/.gemini-context-hub/`

1. 确保 Hub 目录存在
2. 检测项目名（从 `basename $(pwd)` 或 package name 推断）
3. 创建软链接，**带项目名前缀**防冲突：
   - `docs/PRODUCT_SOUL.md` → `~/.gemini-context-hub/{项目名}_SOUL.md`
   - `docs/ARCHITECTURE.md` → `~/.gemini-context-hub/{项目名}_ARCH.md`
   - `docs/ROADMAP.md` → `~/.gemini-context-hub/{项目名}_ROADMAP.md`
4. 清理已失效的软链接

### Step 3: 输出报告

```
docs/ 结构状态:
  PRODUCT_SOUL.md  ✅ (128行)
  ARCHITECTURE.md  ✅ (245行)
  ROADMAP.md       ✅ (89行)

Gemini Context Hub:
  ~/.gemini-context-hub/{项目名}_SOUL.md    → ✅
  ~/.gemini-context-hub/{项目名}_ARCH.md    → ✅
  ~/.gemini-context-hub/{项目名}_ROADMAP.md → ✅

```

---

## 质量标准

1. **产品语言优先**：PRODUCT_SOUL 和 ROADMAP 面向产品合伙人，用用户体验描述
2. **Single Source of Truth**：每条信息只在一个文件中定义
3. **图表用 Mermaid**
4. **ROADMAP 可操作**：Next Steps 必须包含优先级

## 约束

- 不修改 `README.md`、`CLAUDE.md`、`docs/ui/UI_SHOWCASE.md`
- 软链接必须用**绝对路径**
- Hub 中只放软链接，不复制文件内容
- `docs/features/`、`docs/ui/specs/` 等子目录不动
