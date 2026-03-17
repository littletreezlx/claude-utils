# FlameTree Lab - 项目记忆

## 项目概况
- **类型**: Astro 5.x + React 19 + Tailwind CSS v4 静态站点
- **部署**: Cloudflare Pages
- **状态**: MVP UI ~95%

## 文档体系 (docs/)
已完成完整文档审查和生成 (2026-02-08):
- `PRODUCT_SOUL.md` - 品牌灵魂
- `PRODUCT_BEHAVIOR.md` - 导航/流程/交互/状态 (新生成)
- `ARCHITECTURE.md` - 技术架构
- `FEATURE_CODE_MAP.md` - 功能代码映射
- `ROADMAP.md` - 路线图 + Known Issues

## Known Issues (P0)
1. Flame Tree Pick 描述不一致: `projects/index.astro:31` 写 "RSS reader"，应为"决策玩具"
2. LittleTree 无真实产品截图

## 关键路径
- 导航栏: `src/layouts/Layout.astro`
- 首页: `src/pages/index.astro` (6 个区块)
- 组件: `src/components/` (6 个 .astro 组件)
- 全局样式: `src/styles/global.css`
- 内容: `src/content/config.ts` (projects + posts 两个 collection)

## 经验教训
- 构建命令: `npm run build` (无测试框架)
- 主题切换: 不跟随系统偏好，仅 localStorage
- Gallery 布局: CSS Columns (非 Masonry.js)
- GitHub 导航链接是占位 (github.com)
