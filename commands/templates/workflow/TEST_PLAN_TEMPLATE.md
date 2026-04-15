# [项目名] 测试补齐计划

> ⚠️ **此文件是入口文件，固定命名 `dag.md`，位于 `.task-test-plan/dag.md`**（与同阶段细节文件和 `state.json` 聚合在一个目录，清理时整刀切）

> **🏠 项目宏观目标**：
> [描述项目的测试补齐目标，为什么要这样做]

## STAGE ## name="stage-1" mode="serial"

## TASK ##
Stage 1: 测试分类（已完成）
详见 `.task-test-plan/stage-1-triage.md`

**✅ 完成标志**：
- [x] 现有测试已分类

## STAGE ## name="stage-2" mode="serial"

## TASK ##
Stage 2: 清理任务（如有）
详见 `.task-test-plan/stage-2-cleanup.md`

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

**目标**：确保所有新增测试通过

文件: test/unit/*.dart
验证: ../scripts/test.sh

## STAGE ## name="review" mode="serial"

## TASK ##
全局审视与收尾

**目标**：纵观所有测试阶段产出，整体梳理，将剩余工作记录到 TODO.md

**执行步骤**：
1. 回顾所有阶段的测试编写和修复结果
2. 评估测试覆盖度：关键路径是否都覆盖？
3. 记录关键决策和背景
4. 自问：还有什么测试缺口？还有什么可以进一步优化？
5. **直接写入项目根目录 TODO.md**（不依赖 /todo-write），包含测试覆盖摘要、遗留缺口、下一步行动项

**⚠️ 重要**：你没有前序任务的会话历史，必须通过 `git log`、`git diff --stat` 和文件系统自行发现前序产出。

**完成标志**：
- [ ] TODO.md 已写入项目根目录且包含遗留事项和下一步行动

文件: TODO.md
验证: test -f TODO.md && grep -c "\- \[ \]" TODO.md
