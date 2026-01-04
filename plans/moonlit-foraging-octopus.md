# Clipper 系统 - 网页剪藏到 RSS

> **功能定位**：独立模块，Push 模式（Chrome 插件推送内容），复用 AI 优化和 RSS 生成能力
>
> **数据流**：Chrome 插件 → 服务器任务队列 → AI 优化 → RSS → Miniflux → Reeder

---

## 核心决策

| 决策 | 选择 |
|------|------|
| 数据模型 | 独立 `clipper_tasks` 表，不复用 Follow 系统 |
| 任务处理 | 异步队列，Chrome 提交后立即返回 |
| RSS 内容 | 只输出 AI 优化完成的任务 |
| 图片处理 | Phase 1 原始链接，Phase 2 代理 |

---

## 文件清单

### 新建文件

```
database/init/
└── clipper_tables.sql                          # 数据库表结构

pythonapi/infrastructure/entities/
└── clipper_entities.py                         # SQLModel 数据模型

pythonapi/api/clipper/
├── __init__.py
└── clipper_routes.py                           # FastAPI 路由

pythonapi/services/clipper/
├── __init__.py
└── clipper_rss_service.py                      # RSS 生成服务

pythonapi/services/scheduler/processors/
└── clipper_processor.py                        # 任务处理器

app/api/clipper/
├── submit/
│   └── route.ts                               # Next.js 提交端点
└── rss/feed.xml/
    └── route.ts                               # Next.js RSS 端点
```

### 修改文件

```
pythonapi/services/scheduler/processor_registry.py    # 注册 ClipperTaskProcessor
pythonapi/internal/models/base_models.py              # 添加 CLIPPER_PROCESS 到 TaskType
~/LittleTree_Projects/other/chrome-extension-jina/js/modules/saver/serverCommunicator.js  # 修改目标端点
FEATURE_CODE_MAP.md                                    # 添加映射
```

---

## 数据模型

### clipper_tasks 表

```sql
CREATE TABLE clipper_tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- 任务状态
    status TEXT NOT NULL DEFAULT 'pending',  -- pending | processing | completed | failed
    created_at TEXT DEFAULT (datetime('now')),
    processed_at TEXT,
    error_message TEXT,

    -- 原始内容（Chrome 提交）
    source_url TEXT NOT NULL,
    title TEXT NOT NULL,
    raw_content TEXT NOT NULL,               -- Readability 清洗后的 HTML
    source TEXT DEFAULT 'chrome-extension',

    -- AI 处理结果
    ai_summary TEXT,                         -- ANALYZE 阶段
    ai_optimized_content TEXT,               -- REFINE 阶段（HTML 格式）

    -- 元数据
    metadata TEXT                            -- JSON
);

CREATE INDEX idx_clipper_tasks_status ON clipper_tasks(status);
CREATE INDEX idx_clipper_tasks_created_at ON clipper_tasks(created_at DESC);
```

---

## API 设计

### 1. 提交端点

```
POST /api/clipper/submit
Request: { url, title, content }
Response: { success: true, task_id: 123, status: "pending" }
```

### 2. RSS Feed

```
GET /api/clipper/rss/feed.xml
Response: RSS 2.0 XML（只包含 status=completed 的任务）
```

### 3. 任务状态（可选）

```
GET /api/clipper/tasks/{id}
Response: { task_id, status, created_at, processed_at, has_result }
```

---

## 实施步骤

### Phase 1：核心功能（MVP）

1. **数据库**
   - 创建 `database/init/clipper_tables.sql`
   - 运行初始化脚本

2. **后端数据层**
   - 创建 `pythonapi/infrastructure/entities/clipper_entities.py`
   - 定义 `ClipperTask` 和 `ClipperTaskStatus` 枚举

3. **后端 API**
   - 创建 `pythonapi/api/clipper/clipper_routes.py`
   - 实现 `POST /submit` 端点

4. **任务处理器**
   - 创建 `pythonapi/services/scheduler/processors/clipper_processor.py`
   - 继承 `BaseTaskProcessor`，调用 AI 优化服务
   - 注册到 `processor_registry.py`

5. **RSS 服务**
   - 创建 `pythonapi/services/clipper/clipper_rss_service.py`
   - 复用 `BaseRSSGenerator` 生成 XML

6. **前端 API**
   - 创建 `app/api/clipper/submit/route.ts`（继承 `BaseRouteHandler`）
   - 创建 `app/api/clipper/rss/feed.xml/route.ts`（继承 `BaseRSSFeedHandler`）

7. **Chrome 插件**
   - 修改 `serverCommunicator.js` 目标端点为 `/api/clipper/submit`

8. **测试**
   - 端到端测试：Chrome 提交 → 验证任务状态 → 检查 RSS 输出

### Phase 2：前端 UI（可选）

1. 侧边栏添加 "临时收藏" 入口
2. 任务状态页面（查看队列）
3. RSS 订阅 URL 显示

---

## 关键代码参考

### 复用的能力

| 能力 | 文件 |
|------|------|
| AI 优化 | `pythonapi/services/ai_content_optimization/http_client.py` |
| RSS 生成 | `pythonapi/services/follow/rss/base_rss_generator.py` |
| 处理器注册 | `pythonapi/services/scheduler/processor_registry.py` |
| API 基类 | `src/server-api/base-route-handler.ts` |

### 处理器注册模式

```python
# processor_registry.py 修改

TASK_TYPE_TO_PROCESSOR: Dict[str, str] = {
    # ... 现有 ...
    "clipper_process": "clipper",  # 新增
}

def _initialize_processors(self) -> None:
    self._processors = {
        # ... 现有 ...
        "clipper": ClipperTaskProcessor(),  # 新增
    }
```

---

## 风险与缓解

| 风险 | 缓解 |
|------|------|
| AI 服务不可用 | 任务标记为 failed，保留原始内容，可手动重试 |
| 内容过大 | 验证 content 长度，拒绝 > 500KB |
| 重复提交 | 可选：基于 source_url 去重 |
| RSS 认证 | Phase 1 不加认证，Phase 2 API Key |

## 确认的决策

1. **失败处理**：失败后标记为 `failed`，保留 `raw_content`，可手动重试
2. **数据保留**：已完成任务 30 天后自动删除
3. **内容存储**：同时保留 `raw_content`（原始）和 `ai_optimized_content`（优化后）

---

## RSS 订阅 URL

```
https://your-nas-server.com:61000/api/clipper/rss/feed.xml
```

用户在 Miniflux 中手动订阅此 URL，分类设为 "临时收藏"。
