# 项目修复任务模板

> 基于健康检查报告自动生成 `task-refactor` 的参考骨架。

## 主任务文件结构

```markdown
# 项目修复任务

> **🏠 项目宏观目标**：
> 基于健康检查报告 docs/health-check/YYYY-MM-DD/SUMMARY.md 修复所有问题

## STAGE ## name="fix-critical" mode="serial"
# 阶段1：修复阻塞性问题（串行，避免冲突）
@.refactor-tasks/fix-critical-tests.md
@.refactor-tasks/fix-critical-architecture.md

## STAGE ## name="fix-high" mode="parallel" max_workers="3"
# 阶段2：修复重要问题（并行）
@.refactor-tasks/fix-high-missing-tests.md
@.refactor-tasks/fix-high-outdated-docs.md

## STAGE ## name="fix-medium" mode="parallel" max_workers="4"
# 阶段3：修复一般问题（并行）
@.refactor-tasks/fix-medium-code-quality.md

## STAGE ## name="final-verification" mode="serial"
# 阶段4：全量测试验证 + 生成修复报告
## TASK ##
运行全量测试并生成修复结果报告

**目标**：验证所有修复无回归，生成 REFACTOR_RESULT.md

**核心文件**：
- `docs/health-check/YYYY-MM-DD/REFACTOR_RESULT.md` - [生成]

**完成标志**：
- [ ] 所有测试通过
- [ ] REFACTOR_RESULT.md 已生成

验证: [项目测试命令]

## STAGE ## name="review" mode="serial"

## TASK ##
全局审视与收尾

**目标**：纵观所有修复阶段产出，整体梳理，将剩余工作记录到 TODO.md

**执行步骤**：
1. 回顾所有已完成阶段的实际产出和变更
2. 评估整体完成度：哪些问题已修复？哪些有偏差？
3. 记录关键决策和背景
4. 自问：还有什么没做完？还有什么可以进一步优化？
5. **直接写入项目根目录 TODO.md**（不依赖 /todo-write），包含已完成清单、遗留问题、下一步行动项

**⚠️ 重要**：你没有前序任务的会话历史，必须通过 `git log`、`git diff --stat` 和文件系统自行发现前序产出。

**完成标志**：
- [ ] TODO.md 已写入项目根目录且包含遗留事项和下一步行动

文件: TODO.md
验证: test -f TODO.md && grep -c "\- \[ \]" TODO.md
```

## 修复任务分类规则

根据健康检查的问题ID前缀自动分组：

| 问题ID前缀 | 生成文件 | STAGE |
|------------|---------|-------|
| `critical-test-*` | `fix-critical-tests.md` | fix-critical (serial) |
| `critical-circular-*`, `critical-arch-*` | `fix-critical-architecture.md` | fix-critical (serial) |
| `high-test-*` | `fix-high-missing-tests.md` | fix-high (parallel) |
| `high-doc-*`, `medium-doc-*` | `fix-high-outdated-docs.md` | fix-high (parallel) |
| `high-code-*`, `medium-code-*` | `fix-medium-code-quality.md` | fix-medium (parallel) |

## 修复原则

- **信任测试意图**：代码 ≠ 测试时，优先信任测试定义的预期行为
- **每修一个立即验证**：不要批量修完再测
- **失败3次回滚**：连续失败3次立即 `git reset --hard HEAD`，重新思考方案
- **保持函数签名**：重构时不破坏调用者
