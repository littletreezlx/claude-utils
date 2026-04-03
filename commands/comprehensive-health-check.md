---
description: 全面健康检查（DAG）- 诊断调度 + 行动路线
---

# 全面健康检查

> 项目体检中心：运行工具收集客观数据 → 生成诊断报告 → 指向专项命令。**只诊断，不治疗。**

## 使用方式

```bash
/comprehensive-health-check        # 生成诊断任务文件
batchcc task-health-check            # 执行
```

产出：`docs/health-check/{YYYY-MM-DD}/SUMMARY.md`（诊断报告 + 行动路线）

> **格式规范**：
> - @templates/workflow/DAG_FORMAT.md - DAG 统一规范（**必须遵循**）
> - @templates/workflow/HEALTH_CHECK_TASK_TEMPLATE.md - 健康检查任务模板

---

## 核心理念

1. **诊断调度器**：收集客观数据，指向专项命令——不重复专项命令的工作
2. **工具驱动**：优先用客观工具（测试框架、静态分析），而非 AI 主观阅读
3. **失败即信息**：工具报错属于"诊断出的病症"，捕获输出写入报告
4. **只读不写**：除了生成报告文件，不修改任何项目代码和文档

---

## 与专项命令的分工

| 问题类型 | 本命令做什么 | 交给谁治疗 |
|---------|------------|-----------|
| 测试失败/缺失 | 运行全量测试，统计通过率 | `/test-plan`（补齐） `/test-run`（修复） |
| 代码质量 | 运行静态分析，统计警告数 | `/refactor-project`（重构） |
| 文档过时 | 抽查路径有效性和关键断言 | `/doc-update-context`（深度审查） |
| 基础设施问题 | 检测测试能否跑、配置完整性 | `/test-audit`（审计修复） |
| 四要素不一致 | 不做（这是快速对齐的事） | `consistency-check` skill（快速对齐） |

**原则**：本命令的诊断深度到"发现问题 + 量化严重程度"为止，具体分析和修复留给专项命令。

---

## 执行策略

### 第一步：探索与规划

1. 识别技术栈（读取 `package.json` / `pubspec.yaml` 等）
2. 根据技术栈选择诊断工具
3. 生成 DAG 任务文件

### 第二步：数据采集（Stage 1 并行）

每个 TASK 运行一类工具，捕获输出写入 `docs/health-check/temp/`：

| TASK | 工具 | 中间文件 | 采集内容 |
|------|------|---------|---------|
| 测试运行 | `npm test` / `flutter test` | `temp/test-result.md` | 通过率、失败清单 |
| 静态分析 | `dart analyze` / `eslint` | `temp/static-analysis.md` | 错误数、警告数 |
| 依赖安全 | `npm audit` | `temp/dependency.md` | 漏洞等级和数量 |
| 文档路径检查 | Glob 验证 | `temp/doc-paths.md` | 失效路径清单 |
| 架构不变量检查 | `invariants.sh`（或项目等效脚本） | `temp/invariants.md` | WARNING/VIOLATION 清单及持续轮次 |

> **注意**：不再扫描文件行数——文件大小不是架构问题，不应作为诊断维度。架构不变量（分层违规、依赖方向、接口契约）才是结构性健康指标。

### 第三步：汇总报告（Stage 2 串行）

1. 读取 `temp/` 下所有中间文件
2. 量化各维度健康度（0-100 分）
3. 生成行动路线
4. 输出 `docs/health-check/{YYYY-MM-DD}/SUMMARY.md`
5. 清理 `temp/` 目录

### 第四步：收尾审视（Stage 3 串行）

按 DAG_FORMAT 收尾模式执行：回顾诊断结果 → 评估诊断覆盖度 → /todo-write 留痕

---

## 严格禁止

1. **禁止修复代码** — 只读不写（除了报告文件）
2. **禁止重复专项命令** — 不做代码质量逐文件审查
3. **禁止主观判断** — 评分必须基于工具输出数据
4. **禁止中断** — 工具失败 ≠ 任务失败，捕获错误写入报告
5. **禁止以文件行数作为诊断维度** — 文件大小不是架构健康指标

## 相关文档

- @templates/workflow/DAG_FORMAT.md - **DAG 统一规范**
- @templates/workflow/HEALTH_CHECK_TASK_TEMPLATE.md - 健康检查模板
- `consistency-check` skill - 快速对齐
- `/refactor-project` - 项目级重构
