---
name: consistency-check
description: >
  This skill should be used when starting work on a new feature, when
  onboarding to a project, when significant code changes have been made
  across multiple files, when the user mentions "alignment", "consistency",
  "check project state", "对齐", "自洽", or when code/test/doc inconsistencies
  are suspected. Verifies and fixes alignment between code, tests, docs,
  and CLAUDE.md.
version: 0.1.0
---

# Consistency Check — 代码库自洽性对齐

## 目的

快速验证代码库的"自洽性"——确保代码、测试、文档、CLAUDE.md 四者不矛盾，Agent 不会被错误信息误导。适合在开始新功能开发或引入 Agent 协作前执行。

## 触发条件

当以下**任一**条件满足时启动：

1. 开始一个新功能的开发（Pre-flight 检查）
2. 首次进入一个项目
3. 跨多文件的大规模变更之后
4. 用户提到项目健康度、对齐、一致性等关注
5. 工作过程中发现文档与代码存在矛盾

## 执行策略

### Step 1: 静态分析 + 测试合约验证

运行静态分析（`dart analyze` / `eslint` / `tsc --noEmit` 等），修复 AI 可理解的报错（Linter 信息中含修复指令的直接修复）。

然后运行测试（静默模式），确认当前测试状态：
- 全通过 → 继续
- 有失败 → 报告失败数量，建议先触发 test-workflow

### Step 1.5: 架构约束检查

如果项目有 `scripts/quality/invariants.sh`，运行它并检查 WARNING/VIOLATION。
有 VIOLATION → 直接报告，建议先修复再开始新功能。

### Step 2: CLAUDE.md 时效性检查

对比 CLAUDE.md 中的规则与实际代码：
- 执行命令是否正确可用？
- 技术栈版本是否匹配？
- 架构决策是否反映实际？（如声明"使用 Provider"但代码已迁移 Riverpod）
- 发现不一致 → **直接更新 CLAUDE.md**

### Step 3: 模式一致性抽查

抽查 3-5 个核心模块：
- 是否遵循 CLAUDE.md 声明的模式？
- 有无新引入的"第二种做法"？
- 发现不一致 → 记录到报告（代码修复交给 `/refactor`）

### Step 4: 文档-代码一致性验证

- **FEATURE_CODE_MAP 路径遍历**：用 Glob 验证文档中所有代码路径是否实际存在，不存在的 → 直接修复或标记删除
- **User Stories 存活性**（如有 `docs/user-stories/`）：抽查 1-2 条故事中的 curl 端点是否仍存在于 Debug Server，返回格式是否与断言匹配
- ROADMAP 中"进行中"任务与代码状态一致？
- 模块质量标签（🟢🟡🔴）是否反映实际？
- 发现不一致 → **直接修复文档**

### Step 5: 输出对齐报告

## 输出格式

在对话中直接输出（不生成文件）：

```
## 代码库自洽性报告

**状态**: 🟢 就绪 / 🟡 有小问题 / 🔴 需要修复

### 测试合约: ✅/❌
[通过/失败数量]

### CLAUDE.md 时效性: ✅/⚠️
[已修复的项 / 仍需注意的项]

### 模式一致性: ✅/⚠️
[发现的模式冲突，建议用 /refactor 修复]

### 文档-代码一致性: ✅/⚠️
[已修复的项 / 需要 /doc-update-context 深度处理的项]

### 建议
- [下一步行动]
```

## 约束

- 执行时间控制在 5 分钟内（抽查而非全量扫描）
- 只修复 CLAUDE.md 和文档，不修复业务代码
- 不生成文件，只在对话中输出
