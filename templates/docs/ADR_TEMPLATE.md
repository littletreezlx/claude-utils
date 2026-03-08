# ADR-{编号}: {简短标题}

**标签**: `[State]` / `[UI]` / `[Network]` / `[Data]` / `[Architecture]`
**状态**: Proposed / Accepted / Deprecated
**日期**: YYYY-MM-DD

## Context

{100 字以内：为什么做这个决定？遇到了什么问题？}

## Decision

{明确的技术选型或产品路径，具体到代码层面}

## Consequences

{引入的技术债、限制、或对后续开发的约束}

---

## 示例

```markdown
# ADR-001: 使用 StateNotifierProvider 管理聊天列表状态

**标签**: `[State]`
**状态**: Accepted
**日期**: 2026-03-08

## Context

聊天列表需要支持实时更新、分页加载、以及多端同步。之前的 `StateProvider` 无法处理复杂的异步状态转换。

## Decision

采用 `StateNotifierProvider` + `AsyncValue` 组合，在 `ChatListNotifier` 中封装所有业务逻辑。

## Consequences

- 需要在 Widget 层处理 `AsyncValue` 的 loading/error/data 三态
- 状态变更逻辑集中在 Notifier 中，调试时需要关注状态流转
```

## 标签说明

| 标签 | 适用场景 |
|------|---------|
| `[State]` | Riverpod Provider、状态管理、数据流 |
| `[UI]` | Widget、主题、动画、交互 |
| `[Network]` | API 调用、缓存策略、离线同步 |
| `[Data]` | Drift/SQLite、数据模型、Schema 迁移 |
| `[Architecture]` | 模块划分、分层设计、依赖注入 |
