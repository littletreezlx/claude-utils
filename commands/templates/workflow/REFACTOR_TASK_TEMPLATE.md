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

**🎯 目标**：验证所有修复无回归，生成 REFACTOR_RESULT.md

**📁 核心文件**：
- `docs/health-check/YYYY-MM-DD/REFACTOR_RESULT.md` - [生成]

**✅ 完成标志**：
- [ ] 所有测试通过
- [ ] REFACTOR_RESULT.md 已生成

验证: [项目测试命令]
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
