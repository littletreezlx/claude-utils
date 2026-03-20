---
description: 全面健康检查（DAG）- 诊断调度 + 行动路线
---

# 全面健康检查

> 项目体检中心：运行工具收集客观数据 → 生成诊断报告 → 指向专项命令。**只诊断，不治疗。**

## 使用方式

```bash
/comprehensive-health-check        # 生成诊断任务文件
python batchcc.py task-health-check --dry-run  # 预览
python batchcc.py task-health-check            # 执行
```

产出：`docs/health-check/{YYYY-MM-DD}/SUMMARY.md`（诊断报告 + 行动路线）

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
| 四要素不一致 | 不做（这是快速对齐的事） | `/codebase-align`（快速对齐） |

**原则**：本命令的诊断深度到"发现问题 + 量化严重程度"为止，具体分析和修复留给专项命令。

---

## 执行策略

### 第一步：探索与规划

1. 识别技术栈（读取 `package.json` / `pubspec.yaml` 等）
2. 根据技术栈选择诊断工具（见下表）
3. 生成 DAG 任务文件

### 第二步：生成任务文件

> **格式规范**：遵循 @templates/workflow/DAG_TASK_FORMAT.md

```
task-health-check                    # 主任务文件
.health-check-tasks/                 # 子任务目录
├── stage-1-data-collection.md      # 数据采集（并行）
└── stage-2-summary.md              # 汇总报告（串行）
```

### Stage 1: 数据采集（并行）

**每个 TASK 运行一类工具，捕获输出写入中间文件 `docs/health-check/temp/`：**

| TASK | 工具 | 中间文件 | 采集内容 |
|------|------|---------|---------|
| 测试运行 | `npm test` / `flutter test` / `pytest` | `temp/test-result.md` | 通过率、失败清单、耗时 |
| 静态分析 | `dart analyze` / `eslint` / `tsc --noEmit` | `temp/static-analysis.md` | 错误数、警告数、按文件分布 |
| 依赖安全 | `npm audit` / `pip-audit` | `temp/dependency.md` | 漏洞等级和数量 |
| 文档路径检查 | Glob 验证 FEATURE_CODE_MAP 路径 | `temp/doc-paths.md` | 失效路径清单 |
| 文件规模扫描 | 统计超过 600 行的文件 | `temp/file-size.md` | 大文件清单 |

> 根据项目实际技术栈选择工具，不限于此表。没有的工具跳过，不强求。

### Stage 2: 汇总报告（串行）

1. 读取 `temp/` 下所有中间文件
2. 量化各维度健康度（0-100 分）
3. 生成行动路线（指向具体专项命令）
4. 输出 `docs/health-check/{YYYY-MM-DD}/SUMMARY.md`
5. 清理 `temp/` 目录

---

## 报告输出格式

```markdown
## 项目健康检查报告

**项目**：[名称] | **日期**：[YYYY-MM-DD] | **技术栈**：[xxx]

### 健康评分

| 维度 | 评分 | 数据来源 |
|------|------|---------|
| 测试通过率 | X/100 | [通过/总数] |
| 静态分析 | X/100 | [错误 N 个，警告 N 个] |
| 依赖安全 | X/100 | [高危 N / 中危 N / 低危 N] |
| 文档有效性 | X/100 | [失效路径 N 个 / 总路径 N 个] |
| 代码规模 | X/100 | [超标文件 N 个] |

**综合评分**：X/100

### 问题清单（按优先级）

#### Critical
- [问题描述] — 数据：[工具输出摘要]

#### High / Medium / Low
...

### 行动路线

| 优先级 | 问题 | 推荐命令 | 预估范围 |
|--------|------|---------|---------|
| 🔴 | 12 个测试失败 | `/test-run` | 先修复，再考虑补齐 |
| 🔴 | 3 个高危依赖 | 手动处理 | 需评估兼容性 |
| 🟡 | 静态分析 47 个警告 | `/refactor-project` | 建议批量修复 |
| 🟡 | 8 个文档路径失效 | `/doc-update-context` | 文档需同步 |
| 🟢 | 5 个文件超 800 行 | `/refactor` | 按需拆分 |
```

---

## 严格禁止

1. **禁止修复代码** — 只读不写（除了报告文件）
2. **禁止重复专项命令** — 不做代码质量逐文件审查、不做文档内容深度比对
3. **禁止主观判断** — 评分必须基于工具输出数据，不基于 AI 阅读印象
4. **禁止中断** — 工具失败 ≠ 任务失败，捕获错误写入报告

---

## 相关文档

- @templates/workflow/DAG_TASK_FORMAT.md - DAG 格式规范
- @templates/workflow/HEALTH_CHECK_TASK_TEMPLATE.md - 检查任务模板
- `/codebase-align` - 快速对齐（轻量级，发现不一致直接修复）
- `/refactor-project` - 项目级重构（基于诊断结果执行）
