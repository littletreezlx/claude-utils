---
name: Cloudflare Pages + Astro 踩坑记录
description: Astro + Cloudflare Pages 部署中的关键陷阱：R2 命名空间隔离、Pages Functions 失效、绑定配置源
type: feedback
---

## 1. Pages Functions (`functions/`) 在 Astro 项目中无效

`@astrojs/cloudflare` adapter 会在 `dist/` 中生成 `_worker.js`，接管所有路由。
`functions/` 目录会被 Cloudflare Pages 完全忽略。

**Why:** Cloudflare Pages 在检测到 `_worker.js` 时进入 "Advanced Mode"，绕过 `functions/` 路由。
**How to apply:** 所有 API 端点必须用 Astro API Routes (`src/pages/api/*.ts`)，并设置 `export const prerender = false`。

## 2. R2 CLI 上传 vs Worker 绑定 = 不同命名空间

`wrangler r2 object put` 上传的数据，Worker 通过 R2 binding 读取时**看不到**（反之亦然）。
它们访问的是同名但隔离的 R2 存储空间。

**Why:** `wrangler pages deploy` 通过 `wrangler.jsonc` 创建的 R2 绑定似乎走不同的命名空间路径。经实测确认：Worker 写入的对象 CLI 获取不到，CLI 写入的对象 Worker 列表为空。
**How to apply:** R2 数据初始化必须通过 Worker 自身完成（临时 PUT 端点或 seed 脚本），不能依赖 `wrangler r2 object put`。数据一旦通过 Worker 写入，跨部署持久化正常。

## 3. `wrangler.jsonc` 是 `wrangler pages deploy` 的唯一绑定来源

Dashboard 中配置的 R2 bindings / KV bindings 对 `wrangler pages deploy` 部署**不生效**。
所有绑定必须写在 `wrangler.jsonc` 的对应字段中。

**Why:** Dashboard 绑定可能仅对 GitHub 集成部署有效。`wrangler pages deploy` 完全以 wrangler.jsonc 为准。
**How to apply:** 确保 `wrangler.jsonc` 中包含所有需要的 `r2_buckets`、`kv_namespaces` 等绑定。Dashboard 可作为备份但不能依赖。

## 4. `ASSETS` 绑定名是保留字

Pages 项目中 `"binding": "ASSETS"` 会报错。

**How to apply:** 使用 `pages_build_output_dir` 替代 `main` + `assets` 配置。

## 5. GitHub 自动部署可能静默失效

`git push` 后未触发 Cloudflare 自动构建（上次部署 2 个月前）。
需手动 `npx wrangler pages deploy dist --project-name=flametree-lab --branch=master`。

**How to apply:** 部署后务必检查 `wrangler pages deployment list` 确认新部署生成。
