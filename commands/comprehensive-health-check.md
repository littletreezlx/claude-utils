---
description: 全面健康检查 (DAG 编排) - 深度诊断与报告生成
---

# 全面健康检查 (Comprehensive Health Check)

> 项目级深度体检系统。通过自动化工具运行测试、静态分析和架构扫描，生成结构化的诊断报告，为后续重构提供决策依据。

## 🌟 核心理念
1.  **先诊断，后治疗**：只发现问题，**绝不**在检查阶段尝试修复代码。
2.  **数据总线模式**：由于任务间上下文隔离，必须通过**中间文件**传递诊断结果。
3.  **工具驱动**：优先使用 `npm test`, `madge`, `tsc` 等客观工具，而非仅靠 AI 主观阅读。
4.  **失败即信息**：测试失败属于“诊断出的病症”，**不应**导致任务本身报错停止。

---

## 🚀 使用方式

```bash
# 1. 生成检查计划
/comprehensive-health-check

# 2. 执行诊断（完全自动化）
python batchcc.py task-health-check

# 3. 阅读报告
open docs/health-check/$(date +%Y-%m-%d)/SUMMARY.md

```

---

## 📂 数据流转架构 (关键)

由于 `batchcc` 的每个 TASK 运行在独立会话中，必须严格遵守以下数据流转规范：

1. **中间产物 (Stage 1-4)**：
* 所有诊断任务必须将结果写入 `docs/health-check/temp/` 目录。
* 命名规范：`{stage}-{module}.md` (例: `test-backend-results.md`)。
* 内容格式：结构化的 Markdown 片段，包含“问题列表”、“严重等级”、“相关文件”。


2. **最终汇总 (Stage 5)**：
* 读取 `docs/health-check/temp/` 下的所有文件。
* 整合生成最终报告 `docs/health-check/{YYYY-MM-DD}/SUMMARY.md`。
* 完成后清理 temp 目录。



---

## 📋 执行策略

### 第一步：探索与规划

1. **识别技术栈**：读取 `package.json` 确认测试框架 (Jest/Vitest/Mocha) 和构建工具。
2. **规划阶段**：
* Stage 1: **测试健康度** (Unit/E2E Tests)
* Stage 2: **代码质量** (Lint, Type Check)
* Stage 3: **架构分析** (Circular Deps, Dead Code)
* Stage 4: **文档/安全** (Security Audit, Readme Check)
* Stage 5: **汇总报告** (Summary)



### 第二步：生成任务文件

生成主任务文件 `task-health-check` 及子任务目录 `.health-check-tasks/`。

---

## 🎯 任务格式规范 (必须遵守)

所有生成的 `.health-check-tasks/*.md` 文件中的任务，必须严格遵循以下格式：

### 1. 诊断任务模板 (Stage 1-4)

```markdown
## TASK ##
[模块名] 循环依赖扫描

**🏠 项目背景**：
[简述]

**🎯 任务目标**：
使用工具扫描 [模块/目录] 的循环依赖情况，将结果写入中间文件。

**📁 核心文件**：
- `src/modules/` - [扫描] 目标目录
- `docs/health-check/temp/arch-circular.md` - [新建] 中间诊断结果

**🛠️ 诊断工具 (优先使用)**：
- 循环依赖：`npx madge --circular --extensions ts ./src`
- 类型检查：`npx tsc --noEmit`
- 依赖安全：`npm audit`
- 测试运行：`npm test` (务必带上 CI 参数如 --watch=false)

**🔨 执行步骤**：
1. 确保 `docs/health-check/temp/` 目录存在
2. 执行 `npx madge ...` 捕获输出
3. 分析输出内容（即使工具返回错误代码，也要捕获 stderr）
4. 将分析结果按以下 Markdown 格式写入 `docs/health-check/temp/arch-circular.md`：
   ```markdown
   ### 🔴 循环依赖 (Critical)
   - `A.ts` -> `B.ts` -> `A.ts`

```

**✅ 完成标志**：

* [ ] 诊断工具已执行（**即使发现大量问题，任务也算成功**）
* [ ] 中间结果文件已生成
* [ ] **未**尝试修复任何代码

文件: src/
验证: ls docs/health-check/temp/arch-circular.md

```

### 2. 汇总任务模板 (Stage 5)

```markdown
## TASK ##
生成最终健康诊断报告

**🎯 任务目标**：
读取所有中间诊断文件，生成汇总报告，并提出修复建议。

**📁 核心文件**：
- `docs/health-check/temp/*.md` - [读取] 所有中间结果
- `docs/health-check/{Date}/SUMMARY.md` - [新建] 最终报告

**🔨 执行步骤**：
1. 创建日期目录 `docs/health-check/202X-XX-XX/`
2. 读取 `temp/` 目录下所有 Markdown 文件
3. 按照 Critical > High > Medium > Low 优先级整合问题
4. 生成 `SUMMARY.md`，包含：
   - 🏥 **总体健康评分** (0-100)
   - 🔴 **高危问题清单** (必须修复)
   - 🟡 **警告问题清单** (建议修复)
   - 💡 **后续重构建议** (具体的 /refactor-project 策略)
5. 删除 `temp/` 目录

**✅ 完成标志**：
- [ ] SUMMARY.md 已生成且内容完整
- [ ] temp 目录已清理

文件: docs/health-check/
验证: ls docs/health-check/*/SUMMARY.md

```

---

## 💎 严格禁止 (Constraints)

1. **禁止修复** ⛔：此命令只读不写（除了生成报告）。发现 Bug 不要改，记下来。
2. **禁止中断** ⛔：如果 `npm test` 失败，**不要**让 Task 失败。捕获错误日志写入报告，然后让 Task 标记为完成。
3. **禁止幻觉** ⛔：不要凭空猜测代码问题，必须基于工具输出（Run log）或明确的代码模式。
4. **禁止交互** ⛔：不要生成“请用户检查...”的步骤，所有检查必须自动化完成。

## 🛠️ 推荐工具清单

* **Madge**: 循环依赖 (`npx madge`)
* **TypeScript**: 类型检查 (`tsc --noEmit`)
* **Tests**: 单元测试 (`npm test`)
* **Audit**: 依赖漏洞 (`npm audit`)
* **Duplication**: 代码重复率 (`jscpd` 或手动分析)

```