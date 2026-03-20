---
name: follow-cross-service-sync-risks
description: Follow 系统三端数据模型同步风险点追踪（2026-03-19 审计+修复）
type: project
---

Follow 数据模型在 Python/TypeScript/Node.js 之间的同步风险：

### 已修复 (2026-03-19)
1. ~~**is_profiled 字段缺失**~~: 已添加到 TS FollowContent 和 FollowContentTyped
2. ~~**optimized_content 幽灵字段**~~: FollowContentViewModal 已改为优先使用 3 阶段字段（content_analysis > content_refined > content_raw），optimized_content 作为兼容回退
3. ~~**platform_metadata 序列化歧义**~~: 已添加注释说明后端存储为 JSON string，类型安全版本见 FollowContentTyped

### 已验证无风险
4. ~~**Zhihu 适配器绕过 build_content_dict**~~: 误报，实际已在使用（zhihu_adapter.py:107）
5. ~~**时间戳规范化不完整**~~: 所有适配器均通过 build_content_dict → DataValidator.normalize_time 统一处理

### 仍需关注
- `optimized_content` 字段在 bilibili-entity.ts 和 youtube-entity.ts 中仍作为独立字段使用（非 Follow 系统，是旧的独立模块）
- 未来新增平台适配器时必须经过 build_content_dict，不能手动构造返回值

**How to apply:** 修改 Follow 数据模型后运行 `pnpm test:unit:backend -- --silent --no-coverage tests/unit/backend/contracts/`
