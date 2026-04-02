---
name: project_exceptions
description: 各子项目偏离通用规范的关键例外，避免 AI 用错误模板
type: project
---

各项目偏离 CLAUDE.md 通用规范的地方，开发时必须注意：

## flametree_pick

- **状态管理**: 使用手写 `NotifierProvider`，**不用** `@riverpod` 注解（通用规范要求 @riverpod）
- **DI 模式**: SimplifiedDI (GetIt) + Riverpod 双轨，不是纯 Riverpod
- **Why:** 项目历史原因，迁移成本高，保持现状
- **How to apply:** 在 pick 项目中新增 ViewModel 时，照现有手写风格，不要用 @riverpod 注解

## flametree_ai

- **架构**: 前后端分离，flutter_common 不以 submodule 方式引入（app/ 子目录是 Flutter 客户端）
- **fleet-status.sh**: common 列会显示 n/a
- **How to apply:** 修改 flutter_common 后不需要 sync 到 flametree_ai

## flametree_coffee

- **文档**: 无 docs/ 目录，无 FEATURE_CODE_MAP.md，文档体系最薄弱
- **How to apply:** 如需开发此项目，先建文档体系再动代码

## flutter_test

- **定位**: 实验/学习项目，非正式产品，测试/文档要求可放宽
