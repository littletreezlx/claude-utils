---
description: 全面健康检查 (DAG 编排) - 深度诊断与报告生成
---

# 全面健康检查 (Comprehensive Health Check)

> 项目级深度体检系统。通过自动化工具运行测试、静态分析和架构扫描，生成结构化的诊断报告，为后续重构提供决策依据。

## 核心理念

1. **先诊断，后治疗**：只发现问题，**绝不**在检查阶段尝试修复代码
2. **数据总线模式**：任务间上下文隔离，必须通过**中间文件**传递诊断结果
3. **工具驱动**：优先使用客观工具（测试框架、静态分析），而非仅靠 AI 主观阅读
4. **失败即信息**：测试失败属于"诊断出的病症"，不应导致任务本身报错停止

---

## 使用方式

```bash
/comprehensive-health-check        # 生成检查计划
python batchcc.py task-health-check # 执行诊断
```

---

## 数据流转架构

1. **中间产物 (Stage 1-4)**：写入 `docs/health-check/temp/`，命名 `{stage}-{module}.md`
2. **最终汇总 (Stage 5)**：读取 temp/ → 整合生成 `docs/health-check/{YYYY-MM-DD}/SUMMARY.md` → 清理 temp/

---

## 执行策略

### 第一步：探索与规划

1. 识别技术栈（读取 `package.json`/`pubspec.yaml` 等）
2. 根据技术栈选择对应的诊断工具
3. 规划 5 个阶段的任务

### 第二步：生成任务文件

```
task-health-check                    # 主任务文件
.health-check-tasks/                 # 子任务目录
├── stage-1-test-health.md          # 测试健康度
├── stage-2-code-quality.md         # 代码质量
├── stage-3-architecture.md         # 架构分析
├── stage-4-docs-security.md        # 文档/安全
└── stage-5-summary.md              # 汇总报告
```

---

## 任务格式规范

### 诊断任务 (Stage 1-4)

每个 TASK 必须：
- 明确诊断工具和命令（根据项目技术栈选择）
- 将结果写入 `docs/health-check/temp/` 中间文件
- 即使工具报错，也要捕获输出写入报告（失败即信息）
- **禁止修复代码**

> 格式遵循上下文中已加载的 DAG_TASK_FORMAT 规范（通过 @templates/workflow/DAG_TASK_FORMAT.md 注入）

### 汇总任务 (Stage 5)

- 读取 `temp/` 下所有中间文件
- 按 Critical > High > Medium > Low 优先级整合
- 生成 SUMMARY.md（健康评分 0-100、高危清单、警告清单、重构建议）
- 完成后清理 `temp/` 目录

---

## 常用诊断工具（按技术栈选择）

| 诊断类型 | Node.js | Flutter/Dart | Python |
|---------|---------|-------------|--------|
| 测试运行 | `npm test` | `flutter test` | `pytest` |
| 类型检查 | `tsc --noEmit` | `dart analyze` | `mypy` |
| 循环依赖 | `npx madge --circular` | - | - |
| 依赖安全 | `npm audit` | - | `pip-audit` |
| 代码重复 | `jscpd` | - | - |

> 根据项目实际情况选择工具，不限于此表

---

## 严格禁止

1. **禁止修复** - 只读不写（除了生成报告）
2. **禁止中断** - 工具失败不等于任务失败，捕获错误写入报告
3. **禁止幻觉** - 必须基于工具输出或明确的代码模式
4. **禁止交互** - 不生成"请用户检查..."的步骤

---

## 相关文档

- @templates/workflow/DAG_TASK_FORMAT.md - DAG 格式规范
- @templates/workflow/HEALTH_CHECK_TASK_TEMPLATE.md - 检查任务模板
- `/health-check` - 快速健康检查（轻量版）
- `/refactor-project` - 项目级重构（基于诊断结果执行）
