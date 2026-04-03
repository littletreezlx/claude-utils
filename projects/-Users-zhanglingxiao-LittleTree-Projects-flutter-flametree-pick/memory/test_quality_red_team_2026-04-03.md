---
name: 红队测试质量记录
description: 2026-04-03 红队验证结果与测试盲点修复记录
type: project
---

# 红队测试质量记录 - 2026-04-03

## 红队验证结果摘要

| 指标 | 修复前 | 修复后 |
|------|--------|--------|
| 全局 Mutation Score | 35% (7/20 caught) | 待重测 |
| Tier 1 得分 | 14% (2/14 caught) | 部分改善 |
| Tier 2 得分 | 83% (5/6 caught) | 稳定 |

## 已修复文件

### random_select.dart - 0/4 → 3/4 CAUGHT ✅
- **问题**: 测试只验证结果数量，不验证执行路径（shuffled vs loop）
- **修复**: 补充3个差异化断言测试
  - `count小于选项数时应走pool分支而非shuffled分支`
  - `FisherYates分支应只从有效选项中选择`
  - `pool耗尽时应停止循环不应抛出异常`
- **测试文件**: `test/unit/domain/usecases/random/random_select_usecase_test.dart`
- **结果**: 45个测试通过

### management_view_model.dart - 1/4 CAUGHT 🟡
- **问题**: 缺少副作用验证（流关闭/Provider同步/DB持久化）
- **修复**: 补充 selectGroup State Resonance 测试
  - `selectGroup 应同步更新 activeGroupIdProvider`
- **未解决**: reorderGroup 测试因 Riverpod 生命周期问题无法添加（`state.groups` 访问触发 ref 读取，异步操作过程中 ref 可能已 dispose）
- **测试文件**: `test/unit/presentation/features/management/management_view_model_test.dart`
- **结果**: 4个变异点中1个被捕获，3个因架构限制无法测试

### group_repository_impl.dart - 2/3 CAUGHT ✅
- **问题**: 单元素场景掩盖边界 bug，order 字段从未被断言
- **修复**: 补充3个排序/大小写用例
  - `getDefaultGroup 应该返回 order 最小的分组`（使用负数 order 绕过 shift 逻辑）
  - `isGroupNameExists 应该大小写不敏感`
  - `duplicateGroup 应该复制分组（不包含选项）`
- **测试文件**: `test/unit/infrastructure/repositories/group_repository_impl_test.dart`
- **结果**: 41个测试通过

### option_repo.dart - 2/3 CAUGHT 🟡
- **问题**: updatedAt 字段未被验证
- **修复**: 补充 updatedAt 验证测试
  - `toggleOptionSelection 应该更新 updatedAt`
- **测试文件**: `test/unit/infrastructure/repositories/option_repo_test.dart`
- **结果**: 33个测试通过

### share_service.dart - 1/2 CAUGHT 🟡
- **问题**: 边界值用例缺失（恰好6个选项）
- **修复**: 补充边界测试
  - `恰好6个选项应该截断显示（显示5个+还有1个）`
- **测试文件**: `test/unit/infrastructure/services/share_service_test.dart`
- **结果**: 25个测试通过

### random_selection_view_model.dart - 1/2 CAUGHT 🟡
- **决策**: 保留 modulo 护栏，添加安全说明注释
  ```dart
  // SAFETY: modulo is a defensive guard against physics simulation edge cases.
  // While PhysicsSimulationService should produce valid indices, the modulo
  // ensures safety if settledIndex is ever out of bounds [0, optionsToUse.length).
  ```
- **测试文件**: `test/unit/presentation/features/random_selection/random_view_model_test.dart`
- **结果**: 24个测试通过

## 架构限制记录

### Riverpod 生命周期问题
- **位置**: `management_view_model.dart` reorderGroup 测试
- **原因**: `state.groups` 访问触发 ref 读取，异步操作过程中 ref 可能已 dispose
- **影响**: 3个 reorderGroup 变异点无法通过单元测试覆盖
- **建议**: 考虑 E2E 测试覆盖此场景

## 逃逸变异根因分类

| 根因 | 涉及文件 | 状态 |
|------|---------|------|
| 执行路径未验证 | random_select | ✅ 已修复3/4 |
| 副作用未验证 | management_vm | 🟡 部分修复 |
| 单元素场景掩盖边界 bug | group_repo | ✅ 已修复 |
| 边界值用例缺失 | share_service | ✅ 已修复 |
| 时序/物理保证覆盖 | random_sel_vm | 🟡 已决策保留 |

## 关键发现

1. **Mockito + Riverpod 兼容性问题**: `Result<void>` 需要 `provideDummy<Result<void>>(Result.success(null))`
2. **Drift/Matcher import 冲突**: 使用 `!= null` 代替 `isNotNull` matcher
3. **shiftGroupOrdersFrom 干扰测试**: 使用负数 order 值绕过排序逻辑
4. **State Resonance 模式**: 跨 Provider 状态同步需要显式测试验证

## 验证命令

```bash
# 单元测试
../scripts/test.sh

# 红队验证（需 stryker-mutator）
flutter pub run stryker start
```
