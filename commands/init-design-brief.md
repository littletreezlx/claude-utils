---
description: 生成 Design Brief（供 frontend-design skill 或任意 AI 设计工具消费）
---

# 生成 Design Brief

## 目标

从产品经理和 UX 总监的角度分析当前项目，生成一份激发 AI 设计工具（Claude 的 frontend-design skill、或外部工具如 v0、Lovable 等）进行顶级视觉发明的 Design Brief。

## 产物定位

Design Brief 是**派生产物**，不是源文档。源是 `PRODUCT_SOUL.md` + `docs/ui/UI_SHOWCASE.md`（或等价 UI 文档）。一轮设计迭代里反复复用，因此需要持久化到磁盘而非仅打印到终端。

**文件位置**：`docs/design/DESIGN_BRIEF.md`（标准路径，已在 `~/.claude/guides/doc-structure.md` 登记）

**清理保护**：该路径已被文档结构规范标记为合法派生文档，`/doc-clean`、`inbox` 等清理类工作流不会误删。

## 执行策略

1. **深入分析项目上下文** — 读取 PRODUCT_SOUL、UI 文档、现有界面截图
2. **以设计简报（Design Brief）视角组织输出** — 不是 MVP 说明书，而是激发创意的设计方向
3. **写入 `docs/design/DESIGN_BRIEF.md`** — 若目录不存在先创建；存在则覆盖
4. **终端同步输出** — 方便当场复制到外部工具

## Design Brief 铁律

- **摒弃具体数值**：禁止 Hex 色值、pixel/dp 字号、边距数、动画毫秒数。只描述视觉意图（如"主背景是像纸一样的暖白"）
- **专注于字段与功能流**：罗列界面的数据字段，不规定布局方式。把布局发明权交给设计工具
- **鼓励全面突破**：确保功能元素不丢失，但可以完全重新设计排版、色调、卡片样式、导航结构
- **保留 Vibe 描述**：情绪化描述（如"静谧书房"、"无酸纸与暖台灯"）是激发 AI 创意的核心

## 文件头格式（强制）

写入 `docs/design/DESIGN_BRIEF.md` 时，第一段必须是以下溯源块：

```markdown
> **派生自** `PRODUCT_SOUL.md` + `docs/ui/UI_SHOWCASE.md`
> **生成命令**：`/init-design-brief`
> **过时请重跑**：上游源文件修改晚于本文件 mtime 即视为过时
> **消费者**：frontend-design skill / v0 / Lovable / 其他 AI UI 生成器

---
```

## 使用方式

写入完成后告知用户两条路径：

- **喂给 frontend-design skill**：在当前会话发起设计指令，引用 `docs/design/DESIGN_BRIEF.md` 作为上下文
- **复制到外部工具**：粘贴文件内容到 v0 / Lovable / 其他 AI UI 生成器

## 约束

- 不得把 Brief 写入根目录或 `_scratch/`（会被清理类工作流当作临时产物）
- 源文件（PRODUCT_SOUL / UI_SHOWCASE）不存在时，先提示用户而非生成空壳 Brief
- 若目标路径已有同名文件，默认覆盖（因为 Brief 是派生的，版本留在 git log 里）
