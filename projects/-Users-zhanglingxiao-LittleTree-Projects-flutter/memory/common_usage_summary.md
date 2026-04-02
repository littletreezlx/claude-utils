---
name: common_usage_summary
description: flutter_common 各 API 模块被哪些项目使用，修改前查影响范围
type: reference
---

flutter_common API 使用概况（2026-03-18 扫描）。精确数据运行 `./scripts/common-usage-map.sh`。

## 重度使用（修改需谨慎）

| API | 主要用户 |
|-----|---------|
| **LogUtil (Log.d/i/w/e)** | flametree_pick(39), flametree_rss(27), flametree_music(10), littletree_x(1) |
| **Result<T>** | flametree_music(24), flametree_pick(8), flametree_coffee(1) |
| **AdaptiveSize (.aw/.ah/.asp)** | flametree_music(24) |
| **PlatformAdapter** | flametree_music(23), flametree_pick(4) |
| **DesignTokens** | flametree_music(17) |

## 中度使用

| API | 主要用户 |
|-----|---------|
| **AppError** | flametree_music(5), flametree_pick(1) |
| **GlobalErrorHandler** | flametree_music(5) |
| **BaseViewModel** | flametree_pick(4) |
| **BaseUseCase** | flametree_pick(5) |
| **SkeletonLoader** | flametree_rss(4) |

## 轻度使用（修改影响小）

| API | 用户 |
|-----|------|
| BouncingWidget | flametree_pick(3) |
| FullscreenImageViewer | flametree_coffee(3) |
| AppDialog | flametree_music(2) |
| AdaptiveLayout | flametree_rss(2) |
| HtmlSanitizer | flametree_rss(2) |
| ShareHelper | flametree_rss(1) |
| GlassContainer | flametree_music(1) |
| AppButton | flametree_pick(1) |
| Debouncer | flametree_music(1) |

## 未被使用（可大胆重构）

SimpleViewModel, ListViewModel, BaseAsyncNotifier, ApiClient, SimpleHttpClient, SseParser, HiveStorageService, ServiceContainer, AppToast, LoadingWidget, EmptyWidget, AppErrorWidget, KeyboardShortcutManager, HapticService
