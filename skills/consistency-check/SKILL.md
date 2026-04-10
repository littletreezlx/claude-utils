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

### Step 6: 分流归档（严禁混流）

consistency-check 的产出混合了事实和判断，必须分流：

#### 6a. 客观缺失 / 强制违反 → 直接修复 或 TODO.md
- CLAUDE.md 规则与代码不符、失效的文档路径、invariants.sh 的 VIOLATION → 本 skill 已在 Step 2/4 直接修复
- 若有需要代码级修复的（如模式冲突需要 /refactor）→ 调用 `todo-write` 写入 `TODO.md`，带 `§ 模式一致性` 引用

#### 6b. 模式/架构判断 → 先 /think 决策
"是否引入了第二种做法"、"这个模式是否应该统一"等**需要架构决策**的事项 → 调用 `/think --quick` 做决策：

- `/think` 能拍板 → 直接转 TODO.md 或丢弃
- `/think` 无法决策 → 追加到项目根 `to-discuss.md`：

```markdown
## [Arch|Pattern|Convention] 简短标题 (Ref: consistency-check 报告 § 模式一致性)
- **事实前提**: [观察到的模式分叉，带文件路径和代码行号]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md（/refactor）
  - [ ] Reject → 两种模式都接受，更新 CLAUDE.md 说明原因
```

**关键区分**：
- "CLAUDE.md 说用 Riverpod 但代码还在用 Provider" = 事实 → 修 CLAUDE.md 或代码
- "建议统一用 Repository 模式替代直接调用 DAO" = 观点 → 先 /think 决策，无法拍板才进 to-discuss.md

## 约束

- 执行时间控制在 5 分钟内（抽查而非全量扫描）
- 只修复 CLAUDE.md 和文档，不修复业务代码
- 报告在对话中输出；模式判断型 findings 先经 `/think` 决策
