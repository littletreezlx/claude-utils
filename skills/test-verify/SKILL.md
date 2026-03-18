---
name: test-verify
description: >
  Adversarial test quality verification through semantic mutation testing.
  Use when AI has generated tests and their effectiveness needs validation,
  when delivery-workflow needs to verify core module test quality,
  when the user says "verify tests", "test quality", "测试验资", "红队检查",
  or when large batches of tests (>20) were generated in one session.
  Acts as the "Red Team" — injects business-logic bugs to prove tests can catch them.
version: 0.1.0
---

# Test Verify — 红队对抗验证

## 目的

验证测试的**真实防护能力**，而非覆盖率数字。通过语义变异（注入业务逻辑 Bug）验证测试能否检测到关键故障。

**隐喻**：现有测试工具是蓝队（建设 + 覆盖），本工具是红队（渗透 + 证伪）。

**核心问题**：AI 同时写代码和测试 = 自己出题自己答。本工具打破这个闭环。

## 触发条件

当以下**任一**条件满足时启动：

1. AI 在本次会话中一次性生成了大量测试（>20 个）
2. delivery-workflow 交付核心模块时抽样验证
3. 用户表达验证意图："verify tests"、"测试验资"、"红队检查"、"测试有效吗"
4. `/test-plan` 补齐测试后，对新生成的关键测试进行验资

**不触发**：
- 日常单文件修改后的测试运行（那是 test-workflow 的职责）
- 测试基础设施问题（那是 /test-audit 的职责）
- 测试缺口规划（那是 /test-plan 的职责）

## 工具链定位

```
/test-audit  → "能不能跑？"  （基础设施）
/test-plan   → "缺什么测试？" （扫盲 + 规划）
test-verify  → "测试真有用吗？"（验资 + 证伪）  ← 本工具
test-workflow → "跑一下看结果" （执行 + 诊断）
```

## 执行流程

### Step 0: 锁定目标

**输入**：目标源文件路径（或模块目录）

**目标筛选策略**（Token 成本敏感，精准点射）：

| 优先级 | 类型 | 验证强度 | 示例 |
|--------|------|---------|------|
| Tier 1 | 安全 / 支付 / 状态机 | 强制全量验证 | auth, payment, order state |
| Tier 2 | 普通业务 CRUD | 抽样 2-3 个变异点 | user profile, settings |
| Tier 3 | UI 展示 / 工具函数 | 不验证（跳过） | formatDate, ColorUtils |

**自动推导优先级**：
- 从 `docs/FEATURE_CODE_MAP.md` 识别核心模块
- 从测试文件中的 describe/group 名称推断业务重要性
- 含 `auth`、`payment`、`security`、`permission`、`token` 等关键词 → 自动升为 Tier 1

### Step 1: 生成变异清单（先出题，后验证）

**铁律：变异点必须先完整描述，再逐个执行。禁止"看完测试再决定怎么变异"。**

这是结构性防范 AI 同谋风险的关键——先承诺要注入什么 Bug，然后才去验证。

读取源文件，识别 1-5 个最致命的业务逻辑变异点：

| 变异类型 | 描述 | 示例 |
|---------|------|------|
| 权限越界 | 删除权限/角色校验 | 删掉 `if (!user.isAdmin) return;` |
| 状态截断 | 注释掉关键副作用 | 注释 `await db.save(data);` |
| 边界穿透 | 修改边界条件 | `amount > 0` → `amount >= 0` |
| 逻辑反转 | 反转条件判断 | `isValid` → `!isValid` |
| 默认值篡改 | 修改关键默认值 | `retryCount = 3` → `retryCount = 0` |

输出变异清单（在控制台展示）：

```
🎯 变异清单（共 3 个语义变异点）：
  M1: [权限越界] auth_service.dart:42 — 删除 admin 角色校验
  M2: [状态截断] auth_service.dart:78 — 注释掉 token 持久化
  M3: [边界穿透] auth_service.dart:95 — 允许空密码通过校验
```

### Step 2: 逐个变异 + 验证

对每个变异点执行：

1. **Inject** — 修改源文件，注入变异
2. **Execute** — 运行对应测试文件（精准测试，非全量）
3. **Verdict** — 判定结果：
   - 测试**失败** → `[CAUGHT]` 防御有效
   - 测试**通过** → `[ESCAPED]` 测试盲点！
4. **Restore** — `git checkout -- <file>` 立即还原源文件

**隔离保障**：
- 每次变异前确认工作区干净（`git diff <file>` 为空）
- 变异只修改源文件，不修改测试文件
- 还原后验证文件确实恢复（diff 再次为空）

### Step 3: 修复盲点

对所有 `[ESCAPED]` 的变异点：

1. AI 生成测试修复方案（新增断言或新增测试用例）
2. **优先更新现有测试 > 创建新测试**
3. 修复后重新注入同一变异，验证测试能 catch
4. **熔断**：同一变异点修复 2 次仍无法 catch → 标记 `[MANUAL]` 需人工介入

### Step 4: 输出验证报告

在控制台输出（不生成文件，除非用户要求）：

```markdown
# Red Team Verification Report

**Target:** `auth_service.dart` (Tier 1)
**Tests:** `auth_service_test.dart` (18 cases)

| # | Mutation (变异点) | Result | Assessment |
|---|------------------|--------|------------|
| M1 | [权限越界] 删除 admin 校验 (L42) | 🟢 CAUGHT | 防御有效 |
| M2 | [状态截断] 注释 token 持久化 (L78) | 🔴 ESCAPED | 盲点：无持久化断言 |
| M3 | [边界穿透] 允许空密码 (L95) | 🟢 CAUGHT | 防御有效 |

**Mutation Score:** 2/3 (66%)

**Actions Taken:**
- M2: 已在 auth_service_test.dart:L120 新增 token 持久化断言，重新验证通过

**Remaining Issues:**
- (无)
```

## 约束

### 铁律

- **先出题后验证**：变异清单必须在执行前完整输出，不能边看测试边选变异点
- **只变异源文件**：Step 2 中禁止修改测试文件（Step 3 修复盲点时才改测试）
- **即时还原**：每个变异执行后必须立即还原，不允许累积变异
- **工作区干净**：开始前 `git status` 确认无未提交更改（有则先提交或 stash）

### 资源控制

- 单文件最多 5 个变异点
- 单次调用最多处理 3 个源文件
- Tier 3 文件直接跳过，不浪费 Token
- 修复尝试每个变异点最多 2 次

### 与其他工具的关系

- 发现测试基础设施问题 → 建议先跑 `/test-audit`
- 发现大量测试缺失 → 建议先跑 `/test-plan`
- 修复盲点后需要提交 → 触发 `git-workflow` skill

## 灵感来源

Reddit r/ClaudeCode 社区讨论 "Claude Code generated hundreds of tests, how do I know they're useful?"
— 手动变异测试 + 对抗 agent 方案的自动化落地。
