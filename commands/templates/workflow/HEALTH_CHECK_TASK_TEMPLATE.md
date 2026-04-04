# 项目健康检查任务模板

> 生成 `task-health-check` 的参考骨架。基于项目实际情况调整模块和工具。

## 主任务文件结构

```markdown
# 项目健康检查任务

> **🏠 项目宏观目标**：
> 全面诊断项目健康度，生成结构化报告和修复任务文件

## STAGE ## name="test-health" mode="parallel" max_workers="4"
# 阶段1：测试健康检查 - 每个模块一个 TASK
@.health-check-tasks/stage-1-test-health.md

## STAGE ## name="code-quality" mode="parallel" max_workers="4"
# 阶段2：代码质量检查 - 每个模块一个 TASK
@.health-check-tasks/stage-2-code-quality.md

## STAGE ## name="architecture" mode="serial"
# 阶段3：架构一致性 + 循环依赖检查
@.health-check-tasks/stage-3-architecture.md

## STAGE ## name="documentation" mode="parallel" max_workers="2"
# 阶段4：文档一致性检查
@.health-check-tasks/stage-4-documentation.md

## STAGE ## name="summary" mode="serial"
# 阶段5：汇总报告 + 自动生成 task-refactor
@.health-check-tasks/stage-5-summary.md

## STAGE ## name="review" mode="serial"

## TASK ##
全局审视与收尾

**目标**：纵观所有诊断阶段产出，整体梳理，将剩余工作记录到 TODO.md

**执行步骤**：
1. 回顾所有阶段的诊断结果
2. 评估诊断覆盖度：有没有遗漏的模块或维度？
3. 记录关键发现和背景
4. 自问：还有什么没检查到？还有什么可以进一步优化？
5. **直接写入项目根目录 TODO.md**（不依赖 /todo-write），包含诊断摘要、遗留问题、下一步行动项

**⚠️ 重要**：你没有前序任务的会话历史，必须通过 `git log`、`git diff --stat` 和文件系统自行发现前序产出。

**完成标志**：
- [ ] TODO.md 已写入项目根目录且包含遗留事项和下一步行动

文件: TODO.md
验证: test -f TODO.md && grep -c "\- \[ \]" TODO.md
```

## 各阶段 TASK 骨架

### Stage 1: 测试健康检查

每个模块生成一个 TASK，输出到 `docs/health-check/temp/test-[模块].md`：

- 运行测试（E2E + 单元），记录通过率和失败清单
- 检查测试质量（过时/无效/脆弱）
- 问题按 Critical/High/Medium 分级，带唯一 ID（如 `critical-test-user-1`）

### Stage 2: 代码质量检查

每个模块生成一个 TASK，输出到 `docs/health-check/temp/code-[模块].md`：

- 抽样审查 3-5 个关键文件（函数复杂度、文件大小、嵌套层次、类型注解）
- 问题带唯一 ID（如 `high-code-order-1`）

### Stage 3: 架构检查

两个 TASK：分层一致性 + 循环依赖，输出到 `docs/health-check/temp/arch-*.md`

### Stage 4: 文档检查

验证 FEATURE_CODE_MAP 等文档与代码一致性，输出到 `docs/health-check/temp/doc-*.md`

### Stage 5: 汇总 + 生成修复任务

1. 读取 `temp/` 下所有中间文件
2. 按优先级汇总 → `docs/health-check/YYYY-MM-DD/SUMMARY.md`
3. 按问题类型分组，自动生成 `task-refactor`（参考 REFACTOR_TASK_TEMPLATE.md）
4. 清理 `temp/` 目录

### Stage 6: 收尾审视

按 DAG_FORMAT 收尾模式执行：回顾诊断结果 → 评估覆盖度 → 直接写入 TODO.md 留痕

## 关键规则

- **问题ID格式**：`[priority]-[type]-[module]-[number]`（如 `critical-test-wechat-1`）
- **中间产物**：写入 `docs/health-check/temp/`，最终汇总后清理
- **只诊断不修复**：Stage 1-4 只读不写（除了报告文件）
- **模块化**：主文件只含 STAGE 定义和 `@` 文件引用
