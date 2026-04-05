---
name: App Update Service API Key
description: flametree-lab.com API 鉴权密钥和端点信息
type: reference
---

## API 端点 (生产)

基础 URL: `https://flametree-lab.pages.dev` (自定义域名 flametree-lab.com 待修复)

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/apps.json` | GET | 完整应用清单 |
| `/api/apps/{appId}` | GET | 单应用信息 |
| `/api/download/{key}` | GET | 流式文件下载 |

## 鉴权

- **API Key**: `ftk_7f8e5779822b728da8545b83266daaeb5ceb31bd4dd613d4`
- Header: `X-API-Key: ftk_xxx...`
- Origin 白名单: `https://flametree-lab.com,https://www.flametree-lab.com`

## R2 桶

- 桶名: `flametree-apps`
- 绑定变量: `APPS_BUCKET`
- 注意: 数据必须通过 Worker 写入（见 feedback_cloudflare_pages_pitfalls.md）
