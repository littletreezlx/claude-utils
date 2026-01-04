# 清理平台聚合 RSS 功能

## 背景
项目已实现单独 follow RSS 订阅源颗粒度控制（`/api/follow/{platform}/rss/sources/{source_id}/feed.xml`），因此不再需要整个平台的聚合 RSS 功能（`/api/follow/{platform}/rss/aggregate/feed.xml`）。

## 清理范围

### 需要删除的功能
- **平台聚合 RSS**：将所有关注源的内容合并成一个 RSS feed
- 保留：单个关注源 RSS（`/sources/{source_id}/feed.xml`）

---

## 清理任务列表

### 1. Python 后端代码

#### 1.1 路由层
**文件**: `pythonapi/api/follow/rss_routes.py`
- [ ] 删除 `get_platform_rss` 端点（行 29-52）
- [ ] 删除 `get_rss_stats` 端点（行 91-106）
- [ ] 更新文件头注释，移除"生成平台聚合 RSS Feed"

#### 1.2 服务层
**文件**: `pythonapi/services/follow/rss/follow_rss_service.py`
- [ ] 删除 `generate_platform_rss` 方法（行 40-57）
- [ ] 删除 `get_platform_stats` 方法（行 83-108）
- [ ] 更新类文档字符串

**文件**: `pythonapi/services/follow/rss/rss_service_config.py`
- [ ] 删除 `DEFAULT_PLATFORM_RSS_MAX_ITEMS` 常量

#### 1.3 路由模型
**文件**: `pythonapi/api/follow/models.py`
- [ ] 删除 `RssStatsResponse` 模型

#### 1.4 微信配置
**文件**: `pythonapi/services/wechat/core/config_manager.py`
- [ ] 删除 `aggregate_rss_max_articles` 配置项（行 104）
- [ ] 删除相关描述（行 114）

**文件**: `pythonapi/services/wechat/core/config_validator.py`
- [ ] 删除 `aggregate_rss_max_articles` 验证逻辑（行 51-52）

---

### 2. Next.js 前端代码

#### 2.1 API 路由
**删除整个目录**: `app/api/follow/[platform]/rss/aggregate/`

---

### 3. RSSHub Node.js 代码

#### 3.1 删除整个目录
**删除**: `src/rss/routes/bilibili/` （整个目录，只有聚合功能）
- index.ts
- implementation.ts
- route-config.ts
- README.md

**删除**: `src/rss/routes/wechat/` （整个目录，只有聚合功能）
- index.ts
- implementation.ts
- route-config.ts

#### 3.2 路由注册
**文件**: `src/rss/routes/initialize-routes.ts`
- [ ] 删除 bilibili 路由注册（行 21-23）
- [ ] 删除 wechat 路由注册（行 25-27）
- [ ] 删除相关注释（行 174）

---

### 4. 文档更新

#### 4.1 FEATURE_CODE_MAP.md
- [ ] 删除聚合 RSS 相关条目

#### 4.2 RSS 架构文档
**文件**: `docs/05-architecture/RSS_ARCHITECTURE.md`
- [ ] 移除 B站/微信聚合 RSS 相关描述

#### 4.3 RSS 模块文档
**文件**: `src/rss/CLAUDE.md`
- [ ] 从"支持的RSS路由"中移除 `/bilibili/aggregate` 和 `/wechat/aggregate`（行 231-232）

**文件**: `src/rss/README.md`
- [ ] 移除 B站关注源和微信公众号关注源路由（行 24-25）

#### 4.4 微信模块文档
**文件**: `pythonapi/services/wechat/CLAUDE.md`
- [ ] 移除聚合 RSS 相关描述

---

### 5. 测试文件

#### 5.1 Python 测试
**文件**: `tests/unit/backend/follow/test_follow_rss_service.py`
- [ ] 删除聚合相关测试

**文件**: `pythonapi/tests/unit/follow/test_follow_rss_service_simple.py`
- [ ] 删除聚合相关测试

#### 5.2 RSSHub 测试
**文件**: `src/rss/routes/__tests__/route-registry-example.ts`
- [ ] 移除 wechat/aggregate 示例路由（行 83-92）

---

### 6. 清理缓存和覆盖率
**删除目录**:
- `coverage/app/api/follow/[platform]/rss/aggregate/`
- `coverage/lcov-report/app/api/follow/[platform]/rss/aggregate/`

---

## 执行顺序

1. **后端代码**（Python）- 核心逻辑删除
2. **前端代码**（Next.js）- API 路由删除
3. **RSSHub 代码**（Node.js）- 聚合路由删除
4. **测试文件** - 删除相关测试
5. **文档更新** - 同步更新
6. **验证** - 运行测试确保单源 RSS 仍正常工作

---

## 验证清单

- [ ] 单个源 RSS 仍可访问: `GET /api/follow/{platform}/rss/sources/{id}/feed.xml`
- [ ] 聚合 RSS 端点返回 404
- [ ] 相关测试通过
- [ ] 无遗留的死代码或导入错误
- [ ] TypeScript 和 Python 类型检查通过
