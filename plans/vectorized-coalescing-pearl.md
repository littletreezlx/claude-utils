# FollowContentList 状态列重构计划

## 目标

将「状态」列改为复合状态展示，清晰展示内容的完整生命周期（抓取 + AI优化），简化「优化内容」列的职责。

## 设计概要

### 复合状态优先级

| 优先级 | 状态 | 条件 | 标签文字 | Tag 颜色 |
|--------|------|------|----------|----------|
| 1 | `fetching` | `loadingOriginalContent.has(id)` | 抓取中 | processing |
| 2 | `no_content` | `!original_content` | 无内容 | default |
| 3 | `optimizing` | `optimization_status === "processing"` | 优化中 | processing |
| 4 | `optimize_failed` | `optimization_status === "failed"` | 优化失败 | error |
| 5 | `ready_to_optimize` | 有内容 + `pending` | 待优化 | warning |
| 6 | `optimized` | `optimization_status === "completed"` | 已优化 | success |
| 7 | `skipped` | `skipped` / `too_short` | 已跳过 | default |

### 三列职责划分

| 列 | 职责 |
|----|------|
| **状态** | 只展示复合状态标签（含图标） |
| **原始内容** | 有内容→「查看」；无内容→「获取」；抓取中→Spinner |
| **优化内容** | 已优化→「查看」；失败→「重试」；待优化→「优化」；其他→`-` |

## 修改文件清单

### 1. `src/types/follow.ts`
- 新增 `ContentCompositeStatus` 类型定义（~10行）

### 2. `src/components/follow/FollowContentList.tsx`（主要）
- 新增图标导入：`CheckCircleOutlined`, `CloseCircleOutlined`, `DownloadOutlined`, `EditOutlined`, `FileExclamationOutlined`, `LoadingOutlined`, `MinusCircleOutlined`, `ThunderboltOutlined`
- 新增函数：
  - `getCompositeStatus()` - 计算复合状态
  - `getCompositeStatusTagConfig()` - 获取标签配置
  - `CompositeStatusTag` - 状态标签组件
- 修改 `OriginalContentButton` - 简化逻辑，更新图标
- 修改 `OptimizedContentButton` - 简化逻辑，「重新优化」→「重试」
- 修改 `defaultRenderContentCard` - 状态列使用新的 `CompositeStatusTag`

### 3. `tests/unit/frontend/components/follow/FollowContentList.test.tsx`
- 新增 `getCompositeStatus()` 单元测试
- 更新状态标签渲染测试

## 实现步骤

### Step 1: 类型定义
在 `src/types/follow.ts` 添加：
```typescript
export type ContentCompositeStatus =
  | "fetching" | "no_content" | "optimizing"
  | "optimize_failed" | "ready_to_optimize"
  | "optimized" | "skipped";
```

### Step 2: 核心函数
在 `FollowContentList.tsx` 添加 `getCompositeStatus()` 和 `CompositeStatusTag`

### Step 3: 组件重构
修改 `OriginalContentButton`、`OptimizedContentButton`、`defaultRenderContentCard`

### Step 4: 测试更新
更新测试用例验证新的复合状态逻辑

### Step 5: E2E 验证
运行测试确保无回归

## 向后兼容

- Props 接口不变
- 轮询机制不变（`useOptimizationPolling` 继续工作）
- 回调函数不变（`onRefetchContent`、`onOptimizeContent`）

## 关键文件

- `src/components/follow/FollowContentList.tsx` - 主要重构
- `src/types/follow.ts` - 类型定义
- `tests/unit/frontend/components/follow/FollowContentList.test.tsx` - 测试更新
