# 全面健康检查

> 项目全面深度体检，适合定期检查或接手项目时使用

## 核心价值
- 🔍 真正的深度分析（实际运行测试）
- 🤖 完全自动化执行（AI 自主诊断和决策）
- 📊 结构化问题报告（按优先级分类）
- 🔄 两阶段工作流（诊断 → 治疗）

**关键约束**：生成的任务将由**低智能模型**（如 GLM4.7）执行，必须遵循"执行模型友好规范"。

---

## 🚀 使用方式

```bash
# 1. 生成健康检查任务
/comprehensive-health-check

# 2. 执行健康检查（完全自动化）
python batchcc.py task-health-check

# 3. 查看诊断报告
cat docs/health-check/$(date +%Y-%m-%d)/SUMMARY.md

# 4. 如需修复，执行自动生成的修复任务
git commit -am "Before refactor"
python batchcc.py task-refactor
```

---

## 🤖 自主执行原则

**⛔ 强制前置阅读**：
1. @templates/workflow/DAG_TASK_FORMAT.md 的"自主执行原则"章节
2. @templates/workflow/DAG_TASK_FORMAT.md 的"执行模型友好规范"章节 ⭐

**核心**：完全自动化、无人值守执行

✅ **应该做**：自主诊断 → 自主判断严重性 → 自主决策修复方案 → 直接执行
❌ **不应该**：询问"是否需要修复？"、列选项让用户选择

### 问题分级标准

| 级别 | 问题类型 | 处理方式 |
|------|---------|---------|
| **Critical** | 核心测试失败、严重循环依赖、数据安全 | 必须修复 → task-refactor |
| **High** | 重要功能缺测试、文档严重过时 | 建议修复 → task-refactor |
| **Medium** | 代码重复、部分文档缺失 | 仅记录 |
| **Low** | 代码风格、注释不足 | 仅记录 |

---

## 📋 执行策略

### 第一步：了解项目状态
快速读取关键文档（如存在）：
- `FEATURE_CODE_MAP.md` - 功能模块位置
- `PROJECT_STATUS.md` - 已知技术债务
- `package.json` / `pubspec.yaml` / `pyproject.toml` - 技术栈

**记录项目背景信息**（用于生成任务时填充）：
- 项目类型：Web 应用 / 移动端 / CLI 工具 / ...
- 技术栈：React + TypeScript / Flutter / Python FastAPI / ...
- 当前状态：新项目 / 已上线 / 重构中 / ...

### 第二步：生成任务编排文件

```
项目根目录/
├── task-health-check                    # 主任务文件
├── .health-check-tasks/                 # 检查任务细节
│   ├── stage-1-test-health.md
│   ├── stage-2-code-quality.md
│   ├── stage-3-architecture.md
│   ├── stage-4-documentation.md
│   └── stage-5-summary.md
└── task-refactor                        # 修复任务（stage-5 自动生成）
```

---

## 🎯 格式规范（必须遵守）

### 主任务文件格式（task-health-check）

```markdown
# 项目健康检查任务

## STAGE ## name="test-health" mode="parallel" max_workers="4"
@.health-check-tasks/stage-1-test-health.md

## STAGE ## name="code-quality" mode="parallel" max_workers="4"
@.health-check-tasks/stage-2-code-quality.md

## STAGE ## name="architecture" mode="serial"
@.health-check-tasks/stage-3-architecture.md

## STAGE ## name="documentation" mode="parallel" max_workers="2"
@.health-check-tasks/stage-4-documentation.md

## STAGE ## name="summary" mode="serial"
@.health-check-tasks/stage-5-summary.md
```

### ⚠️ 子文件 TASK 格式（执行模型友好版）

被引用的子文件（如 `stage-1-test-health.md`）中，**每个任务必须使用增强格式**：

```markdown
# Stage 1: 测试健康检查

> **🏠 项目背景**：[项目类型] + [技术栈] + [当前状态]
> 本阶段检查测试基础设施健康状况。

## TASK ##
后端测试执行与分析

**🏠 项目背景**：
[继承自 STAGE 头部，或单独说明]

**🎯 任务目标**：
运行后端测试套件，统计通过/失败数量，记录失败详情。

**📁 核心文件**：
- `server/` - [分析] 后端代码目录
- `server/package.json` - [参考] 查看测试命令
- `docs/health-check/YYYY-MM-DD/server-tests.md` - [新建] 输出诊断报告

**🔨 执行步骤**：
1. 阅读 `server/package.json` 找到测试命令（通常是 `npm test`）
2. 运行测试命令，捕获输出
3. 统计测试通过/失败数量
4. 将失败详情写入诊断报告

**✅ 完成标志**：
- [ ] 测试命令已执行完成
- [ ] 诊断报告已生成到指定路径
- [ ] 报告包含通过/失败统计

文件: server/

## TASK ##
前端测试执行与分析

**🎯 任务目标**：
运行前端测试套件，统计结果，记录失败详情。

**📁 核心文件**：
- `app/` - [分析] 前端代码目录
- `app/package.json` - [参考] 查看测试命令

**🔨 执行步骤**：
1. 阅读 `app/package.json` 找到测试命令
2. 运行测试命令，使用 `--silent` 减少输出
3. 统计结果，记录失败详情

**✅ 完成标志**：
- [ ] 测试命令已执行完成
- [ ] 诊断报告已生成

文件: app/
```

**格式要点**：
- 使用 `## TASK ##`（注意两边都有 `##`）
- **必须包含**：🎯 任务目标、📁 核心文件、✅ 完成标志
- **推荐包含**：🏠 项目背景（可在 STAGE 头部统一）、🔨 执行步骤
- 执行模型需要知道**具体做什么**和**如何验证完成**

---

## 📏 字数约束

- **Stage 1-4 任务文件**：60-120 行
- **Stage 5 汇总任务**：100-150 行
- **单个 TASK 描述**：20-40 行

---

## 💎 严格禁止

1. **错误的 TASK 格式** ⛔ - 必须用 `## TASK ##`，不能用 `## TASK:` 或其他变体
2. **内嵌详细示例** ⛔ - 只说明生成逻辑（<10行）
3. **硬编码具体命令** ⛔ - 让 AI 根据项目配置查找
4. **过度详细步骤** ⛔ - 描述目标和维度，而非具体步骤

---

## 相关文档
- @templates/workflow/DAG_TASK_FORMAT.md - 详细格式规范
- `/health-check` - 快速健康检查（即时执行）
