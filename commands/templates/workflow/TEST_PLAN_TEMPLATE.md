# [项目名] 测试补齐计划

> ⚠️ **此文件是入口文件，必须放在项目根目录，命名为 `task-add-test`**（不是 `.test-tasks/task-add-test.md`）

> **🏠 项目宏观目标**：
> [描述项目的测试补齐目标，为什么要这样做]

## STAGE ## name="stage-1" mode="serial"

## TASK ##
Stage 1: 测试分类（已完成）
详见 `.test-tasks/stage-1-triage.md`

**✅ 完成标志**：
- [x] 现有测试已分类

## STAGE ## name="stage-2" mode="serial"

## TASK ##
Stage 2: 清理任务（如有）
详见 `.test-tasks/stage-2-cleanup.md`

**✅ 完成标志**：
- [x] 无需清理（或已清理）

## STAGE ## name="stage-3-critical" mode="parallel" max_workers="2"

## TASK ##
T3-1: [模块名] 测试

**🎯 目标**：[描述要测试什么]

**📁 核心文件**：
- `lib/xxx/yyy.dart` - [参考] 理解业务逻辑
- `test/unit/yyy_test.dart` - [新建]

**✅ 完成标志**：
- [ ] 测试用例 1
- [ ] 测试用例 2

文件: test/unit/yyy_test.dart
验证: ../scripts/test.sh test/unit/yyy_test.dart

## TASK ##
T3-2: [另一个模块] 测试

**🎯 目标**：[描述要测试什么]

文件: test/unit/zzz_test.dart
验证: ../scripts/test.sh test/unit/zzz_test.dart

## STAGE ## name="stage-4" mode="serial"

## TASK ##
T4-1: 全量测试验证

**🎯 目标**：确保所有新增测试通过

文件: test/unit/*.dart
验证: ../scripts/test.sh
