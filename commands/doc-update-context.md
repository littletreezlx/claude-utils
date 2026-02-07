---
description: 项目文档结构管理 + Gemini Context Hub 同步 ultrathink
---

# 项目文档上下文管理

## 目标

维护项目的标准化 `docs/` 文档结构，并同步到 `~/.gemini-context-hub/` 供 Gemini 跨项目读取。

**两种模式**：
- **默认模式**：检查 → 初始化/更新 → 同步到 Hub
- **迁移模式**（`$ARGUMENTS` 含 `migrate`）：将旧文档体系统一迁移到新结构

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

## 默认模式：检查 + 同步

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

已归档旧文件:
  (无 / 列出已归档文件)
```

---

## 迁移模式：统一旧文档体系

当 `$ARGUMENTS` 包含 `migrate` 时执行。

### Step 1: 扫描旧文档

查找以下旧文档（可能存在也可能不存在）：

| 旧文件（根目录） | 操作 |
|--------|---------|
| `*context-for-gemini.md` | 拆分到三个核心文档 |
| `PROJECT_STATUS.md` | → 合并到 `docs/ROADMAP.md` |
| `TECHNICAL.md` | → 合并到 `docs/ARCHITECTURE.md` |
| `FEATURE_CODE_MAP.md` | → 移动到 `docs/FEATURE_CODE_MAP.md`（不改内容） |

**不存在的直接跳过，不报错。**

### Step 2: 合并策略

#### context-for-gemini.md → 三文档拆分

| 旧文件章节 | 目标文件 |
|-----------|---------|
| 产品识别与灵魂 / 设计隐喻 / 情感目标 / 交互质感 / 协作备注 / 设计标准附录 | `PRODUCT_SOUL.md` |
| 技术架构支撑 / 核心界面与交互逻辑 / 深度特性分析 | `ARCHITECTURE.md` |
| 快速状态总览 / 现状与待办 / 下一步可选方向 | `ROADMAP.md` |

#### PROJECT_STATUS.md → ROADMAP.md 吸收

- 功能完成度矩阵 → ROADMAP 的"已实现功能速查表"
- 健康度评分 / 综合评估 → ROADMAP 的"健康度评分"
- 已知问题 / 技术债务 → ROADMAP 的"Known Issues"
- 改进历史 → 精简保留最近 3 次，更早的丢弃

#### TECHNICAL.md → ARCHITECTURE.md 吸收

- 分层架构说明 → ARCHITECTURE 的"技术架构"
- 错误处理 / 依赖注入 / 平台适配 → ARCHITECTURE 的"技术设计"
- 避免重复：如果 context-for-gemini 的技术章节和 TECHNICAL.md 有重叠，以 TECHNICAL.md 为准（更详细）

### Step 3: 去重规则

- 功能速查表：只在 `ROADMAP.md` 保留一份
- 设计 Token / 色彩系统：只在 `PRODUCT_SOUL.md` 保留一份
- 技术栈描述：只在 `ARCHITECTURE.md` 保留一份
- 版本演进历史：放在 `PRODUCT_SOUL.md`

### Step 4: 归档旧文件

合并完成后：
- `*context-for-gemini.md` → 重命名为 `{原名}.archived`
- `PROJECT_STATUS.md` → 重命名为 `PROJECT_STATUS.md.archived`
- `TECHNICAL.md` → 重命名为 `TECHNICAL.md.archived`
- `FEATURE_CODE_MAP.md`（根目录）→ 移动到 `docs/FEATURE_CODE_MAP.md`（无需归档，只是搬家）

**不删除，留作备份。确认无误后用户自行删除。**

### Step 5: 执行默认模式

自动执行 Step 2（同步到 Hub）+ 输出报告。

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
