# 微信模块 Follow 系统统一重构计划

## 目标

将微信模块的冗余处理逻辑统一到 Follow 系统，删除废弃的 coordinators、微信专用数据表及相关代码。

## 背景

- 调度器已迁移：`WechatTaskProcessor` 使用 `BatchRefreshService`（Follow 系统）
- `WechatFollowAdapter` 已完整实现，复用微信核心能力
- 项目在开发阶段，可直接删除旧表和数据

---

## 重构步骤

### 阶段 1: 准备与验证

- [ ] 运行现有测试确保通过：`./scripts/test.sh e2e && ./scripts/test.sh unit`
- [ ] 创建回滚点：`git stash` 或记录当前 commit

### 阶段 2: 删除 Coordinators 目录

**删除文件**：
```
pythonapi/services/wechat/coordinators/
├── __init__.py
├── article_fetch_coordinator.py
├── article_pipeline.py
├── batch_fetch_coordinator.py
├── content_update_coordinator.py
└── CODE_OPTIMIZATION_ANALYSIS.md
```

**删除相关测试**：
```
pythonapi/services/wechat/tests/unit/
├── test_article_fetch_coordinator.py
├── test_article_pipeline.py
├── test_batch_fetch_coordinator.py
├── test_content_update_coordinator.py
└── test_factory_functions.py
```

### 阶段 3: 简化 Facade

**修改文件**：`pythonapi/services/wechat/facade.py`

- 移除 coordinator 导入
- 删除 `execute_articles_fetch()` 方法
- 删除 `batch_fetch_articles()` 方法
- 保留：`_mp_service`（提供 api_client）、`_content_extractor`、健康检查

### 阶段 4: 删除微信专用数据表相关代码

**删除 Models**（部分）：
- `pythonapi/internal/models/wechat_models.py` - 删除 `WechatFeed`、`WechatArticle` 类

**删除 Repositories**：
```
pythonapi/infrastructure/database/repositories/
├── wechat_feed_repository.py
└── wechat_article_repository.py
```

**删除 Services**：
```
pythonapi/services/wechat/services/
├── mp_service.py
├── article_service.py
└── rss_service.py  （重构或删除，由 FollowRssService 替代）
```

**删除 API 层**：
```
pythonapi/api/wechat/
├── routes/wechat_feed_routes.py
├── controllers/wechat_feed_controller.py
├── services/wechat_feed_service.py
├── models/wechat_feed_models.py
└── tests/unit/test_wechat_feed_service.py
```

### 阶段 5: 更新依赖引用

**修改文件**：
| 文件 | 修改内容 |
|------|---------|
| `pythonapi/api/dependencies.py` | 移除 `WechatFeedRepository`、`WechatArticleRepository` |
| `pythonapi/api/wechat/__init__.py` | 移除 `wechat_feed_router` 注册 |
| `pythonapi/services/wechat/task/manager.py` | 改用 `FollowSourceRepository`（如需要） |
| `pythonapi/infrastructure/database/database.py` | 移除表创建逻辑 |

### 阶段 6: 前端调整

**修改文件**：
| 文件 | 修改内容 |
|------|---------|
| `src/hooks/media-hooks.ts` | `/api/wechat/mps` → `/api/follow/wechat/sources` |

**API 映射**：
- `/api/wechat/mps` → `/api/follow/wechat/sources`
- `/api/wechat/mps/{id}/articles` → `/api/follow/wechat/contents?source_id={id}`

### 阶段 7: 删除数据库表

```sql
DROP TABLE IF EXISTS wechat_articles;
DROP TABLE IF EXISTS wechat_feeds;
```

### 阶段 8: 清理与验证

- [ ] 运行 lint 检查未使用导入
- [ ] 运行全量测试
- [ ] 启动服务验证健康检查
- [ ] 前端验证 Follow 系统微信功能正常

---

## 保留的核心模块

```
pythonapi/services/wechat/core/
├── api_login.py           # 微信登录
├── wx_api.py              # API客户端
├── wx_http_client.py      # HTTP请求
├── wx_config.py           # 配置
├── wx_credentials_provider.py  # 凭证管理
├── wx_error_handler.py    # 错误处理
├── wx_session_service.py  # 会话管理
├── wx_qr_service.py       # 二维码服务
└── extractors/            # 内容提取器
```

---

## 关键文件

1. `pythonapi/services/wechat/facade.py` - 核心入口需大幅简化
2. `pythonapi/services/follow/adapters/wechat_adapter.py` - Follow 系统微信适配器
3. `pythonapi/internal/models/wechat_models.py` - 删除 WechatFeed/WechatArticle
4. `pythonapi/services/scheduler/processors/wechat_processor.py` - 验证其正确性
5. `pythonapi/api/dependencies.py` - 移除旧依赖

---

## 验证检查点

1. ✅ 启动服务后健康检查正常
2. ✅ 前端可以搜索微信公众号
3. ✅ 可以添加新的微信关注源
4. ✅ 批量刷新任务正常执行
5. ✅ RSS 订阅正常生成

---

## 回滚方案

```bash
git reset --hard <重构前commit>
```
