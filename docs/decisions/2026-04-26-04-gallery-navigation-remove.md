# 决策记录：Gallery + Blog 导航移除 + Tech Stack 页面不建

## 遇到什么问题

- Gallery 页面目前只有占位图（Unsplash），无真实素材
- Blog 页面只有 2 篇示例文章，不是真实内容
- Tech Stack 图标墙组件已完成，但不需要作为独立页面
- 导航上有 Gallery 和 Blog 链接，但内容为空，影响访客判断

## 讨论过程

用户认为：
- Gallery 无素材就不应该放（宁可空着也不要 "Coming Soon" 或占位图）
- Tech Stack 对独立工作室官网不是核心需求，用组件内嵌首页即可

## 为什么这么改

- **Gallery 无实质内容时隐藏导航**：避免访客点击后发现是占位图，降低品牌信任
- **Gallery 路由和组件保留**：等真实素材（AI 艺术作品/项目视觉/客户案例）到位后可直接恢复
- **Tech Stack 不建独立页**：Portfolio 站核心竞争力是"做了什么"而非"用什么做"，图标墙内嵌首页足够

## 为什么不选其他方案

| 方案 | 为什么不选 |
|------|-----------|
| 保留导航 + 加 Coming Soon | 访客点击后得到的是空承诺，不如不放 |
| 放占位图撑场面 | 与"温暖真实"品牌调性违背 |
| 建 Tech Stack 独立页 | Tech Stack 不是客户决策依据，反而分散注意力 |

## 改动内容

1. `src/layouts/Layout.astro` — 从 navLinks 移除 Gallery + Blog 入口，保留 Projects
2. `docs/ROADMAP.md` — Gallery/Blog 状态更新为"暂停"，Tech Stack 标注为"组件就绪不做页面"

## 恢复条件

**Gallery** — 当有以下任一素材时恢复：
- AI 艺术作品（Midjourney / Stable Diffusion 生成）
- 项目视觉截图（真实产品界面）
- 客户案例配图

**Blog** — 当有以下内容时恢复：
- 第一篇真实博客文章（技术心得 / 产品思考 / 独立开发之路）
- 路由和页面就绪，无需重建

---

*记录时间: 2026-04-26*
