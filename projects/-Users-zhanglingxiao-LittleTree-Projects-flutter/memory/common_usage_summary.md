---
name: common_usage_summary
description: flutter_common 各 API 模块被哪些项目使用，修改前查影响范围
type: reference
---

flutter_common API 使用概况（2026-03-18 扫描）。精确数据运行 `./scripts/common-usage-map.sh`。

## 重度使用（修改需谨慎）

| API | 主要用户 |
|-----|---------|
| **LogUtil (Log.d/i/w/e)** | flametree_pick(39), flametree_rss(27), lt_music(10), littletree_x(1) |
| **Result<T>** | lt_music(24), flametree_pick(8), flametree_coffee(1) |
| **AdaptiveSize (.aw/.ah/.asp)** | lt_music(24) |
| **PlatformAdapter** | lt_music(23), flametree_pick(4) |
| **DesignTokens** | lt_music(17) |

## 中度使用

| API | 主要用户 |
|-----|---------|
| **AppError** | lt_music(5), flametree_pick(1) |
| **GlobalErrorHandler** | lt_music(5) |
| **BaseViewModel** | flametree_pick(4) |
| **BaseUseCase** | flametree_pick(5) |
| **SkeletonLoader** | flametree_rss(4) |

## 轻度使用（修改影响小）

| API | 用户 |
|-----|------|
| BouncingWidget | flametree_pick(3) |
| FullscreenImageViewer | flametree_coffee(3) |
| AppDialog | lt_music(2) |
| AdaptiveLayout | flametree_rss(2) |
| HtmlSanitizer | flametree_rss(2) |
| ShareHelper | flametree_rss(1) |
| GlassContainer | lt_music(1) |
| AppButton | flametree_pick(1) |
| Debouncer | lt_music(1) |

## 未被使用（可大胆重构）

SimpleViewModel, ListViewModel, BaseAsyncNotifier, ApiClient, SimpleHttpClient, SseParser, HiveStorageService, ServiceContainer, AppToast, LoadingWidget, EmptyWidget, AppErrorWidget, KeyboardShortcutManager, HapticService
