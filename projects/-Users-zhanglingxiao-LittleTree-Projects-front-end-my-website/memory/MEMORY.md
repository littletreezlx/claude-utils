# FlameTree Lab - 项目记忆

## 项目概况
- **类型**: Astro 5.x + React 19 + Tailwind CSS v4 (静态页面 + SSR API)
- **部署**: Cloudflare Pages (`npm run deploy` 一键构建+部署)
- **域名**: flametree-lab.com + flametree-lab.pages.dev
- **状态**: MVP UI ~95%，App Update Service API 已上线

## 文档体系 (docs/)
已完成完整文档审查和生成 (2026-02-08):
- `PRODUCT_SOUL.md` - 品牌灵魂
- `PRODUCT_BEHAVIOR.md` - 导航/流程/交互/状态
- `ARCHITECTURE.md` - 技术架构
- `FEATURE_CODE_MAP.md` - 功能代码映射
- `ROADMAP.md` - 路线图 + Known Issues

## 关键路径
- 导航栏: `src/layouts/Layout.astro`
- 首页: `src/pages/index.astro` (6 个区块)
- API 路由: `src/pages/api/` (apps.json, apps/[appId], download/[...path], upload/[...path])
- 鉴权中间件: `src/middleware.ts`
- 组件: `src/components/` (6 个 .astro 组件)
- 全局样式: `src/styles/global.css`
- 内容: `src/content/config.ts` (projects + posts 两个 collection)

## 经验与注意事项
- [Cloudflare Pages 踩坑记录](feedback_cloudflare_pages_pitfalls.md) — R2 命名空间隔离、Pages Functions 失效等
- [API Key 和端点信息](reference_api_key.md) — App Update Service 鉴权密钥
- 构建命令: `npm run build` (无测试框架)
- 部署命令: `npm run deploy`
- 主题切换: 不跟随系统偏好，仅 localStorage
- Gallery 布局: CSS Columns (非 Masonry.js)
- GitHub 导航链接是占位 (github.com)
