---
name: feat-done
description: >
  This skill should be used when a complete feature, bug fix, or refactor unit
  has finished implementation — signals include: multi-file changes are staged,
  tests have passed, the user says "done", "完成", "交付", "ship it", "收尾",
  or a natural endpoint is reached where delivery is appropriate. Orchestrates
  the wrap-up flow: Design-First Gate bundle check → doc sync → static analysis
  → hands off to git-workflow skill for commit. Blocks commit when UI changes
  crossed the Gate threshold without a corresponding docs/design/generated/
  bundle reference. Not for partial/in-progress work — only invoke at true
  endpoints.
version: 0.1.0
---

# Feat-Done — 功能收尾交付

## 目的

完整功能落地后的统一收尾:**验收设计闭环 → 同步文档 → 静态分析 → 触发提交**。让 Founder 不用记步骤,也防止 UI 漂移绕过闭环。

## 触发条件

**同时满足**以下条件才启动:

1. 对话中已进行了**跨文件**的代码修改(不是单行小补)
2. 相关测试已通过(或明确不需要测试)
3. 出现以下信号**之一**:
   - 用户说"完成"、"交付"、"收尾"、"done"、"ship it"
   - 功能 / bugfix / refactor 的完整单元已结束(自然终点)
   - 另一个 skill(如 `test-workflow`)报告"修复完成"

**不触发**:
- 修改仍在进行中,只是阶段性暂停
- 用户明确说"先别提交"、"再看看"
- 代码有已知未解决的失败

## 执行流程

### Step 0: Design-First Gate 自检

检查本次改动是否涉及 UI 视觉变化。触发条件(任一):

- 改动涉及 ≥3 个页面的视觉
- 触及 UI_SHOWCASE Invariants(OKLCH 色板 / 字阶 / 间距档位 / 圆角 / 阴影)
- 引入体系之外的新视觉模式

**触发后必问两问**:

1. 本次改动是否触发 Design-First Gate?
2. 若触发,**基于哪个 bundle** 做的 pixel-perfect recreate?

期望回答格式:
```text
基于 docs/design/generated/2026-04-24-warm-ceramic-v2/project/ 做 pixel-perfect recreate。
```

**触发但无 bundle** → 停流程,提示走闭环:

```text
检测到 UI 改动触发 Design-First Gate(理由:___),但找不到对应 docs/design/generated/{ts}/project/ 的 bundle。
这说明本次改动**没走设计闭环**,直接在代码里改的 UI 很容易让设计体系漂移。

建议顺序:
1. 调 `ui-design-router` 生成 Δ Brief → Claude Design 里迭代
2. Export bundle 到本地
3. `/ui-vs` 评审
4. `/ui-adopt` 反哺 + 归档
5. 基于归档的 bundle 在代码里 pixel-perfect recreate(本次工作重做)

确定要跳过闭环直接提交?(y/N)
```

用户明确 y 才继续 Step 1。N 则停止。

**豁免**(直接进 Step 1):
- 单文件 bug 修复
- 既有组件用法调整(不改定义)
- 字符串 / 文案修改
- 本次就是"响应已采纳设计的落地实现"(用户能指出 bundle 路径即放行)

### Step 1: 文档同步

检查本次代码变更是否与项目文档体系矛盾:
- `docs/FEATURE_CODE_MAP.md` 路径是否需要更新?
- `docs/ARCHITECTURE.md` 是否有描述不符?
- `CLAUDE.md` 是否有过时规则?

发现矛盾直接更新对应文档,不转 TODO。

### Step 2: 静态分析

运行项目静态分析工具(`dart analyze` / `eslint` / `tsc --noEmit` / `ruff` 等),可自动修复的直接修复。

### Step 3: Git 提交

**触发 `git-workflow` skill** 完成提交(不在本 skill 内重写提交逻辑)。

## 约束

- 不写新代码(除非修复 Step 2 发现的明显 bug)
- 不新增/删除文件(Step 1 的文档更新除外)
- 不修改依赖文件
- **禁止绕过 Step 0 的 Gate 检查**:UI 改动未走闭环时不得静默放行
- **禁止 push**:`git-workflow` 只做 commit,push 需用户明确指令
- **禁止 --amend**:始终创建新 commit
- **禁止 --no-verify**:pre-commit hook 失败必须修根因
