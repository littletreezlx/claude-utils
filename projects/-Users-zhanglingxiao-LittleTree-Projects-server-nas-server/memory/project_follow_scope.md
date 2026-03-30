---
name: Follow 系统定位边界
description: Follow 系统只处理难以直接订阅的平台，通用 RSS/博客走 Miniflux
type: project
---

Follow 系统的核心价值是把**难以直接订阅的平台**标准化（微信要扫码、B站要 Playwright、Twitter 要爬虫等）。

通用 RSS/博客源**不应纳入 Follow 系统**，应直接在 Miniflux 中管理。

**Why:** 2026-03 讨论了在 Follow 系统新增 `blog` platform adapter 的方案（feedparser + readability-lxml），但经过设计审视发现：RSS 本身就是标准格式，Miniflux 原生支持 OPML 导入、全文抓取、Feed 自动发现、定时刷新等全部能力，在 Follow 系统中重建这些是错位的重复造轮子。

**How to apply:** 当用户提到订阅英文博客、Medium、个人网站 RSS 时，引导使用 Miniflux 而非在 Follow 系统中添加新平台。
