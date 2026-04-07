---
name: test-verify
description: >
  Adversarial test quality verification through semantic mutation testing.
  Use when AI has generated tests and their effectiveness needs validation,
  when feat-done needs to verify core module test quality,
  when the user says "verify tests", "test quality", "测试验资", "红队检查",
  or when large batches of tests (>20) were generated in one session.
  Acts as the "Red Team" — injects business-logic bugs to prove tests can catch them.
  Supports three modes: precise (指定文件), incremental (git diff), global (all — 全项目扫描).
version: 0.2.0
---

# Test Verify — 红队对抗验证

## 目的

验证测试的**真实防护能力**，而非覆盖率数字。通过语义变异（注入业务逻辑 Bug）验证测试能否检测到关键故障。

**隐喻**：现有测试工具是蓝队（建设 + 覆盖），本工具是红队（渗透 + 证伪）。

**核心问题**：AI 同时写代码和测试 = 自己出题自己答。本工具打破这个闭环。

## 触发条件

当以下**任一**条件满足时启动：

1. AI 在本次会话中一次性生成了大量测试（>20 个）
2. feat-done 交付核心模块时抽样验证
3. 用户表达验证意图："verify tests"、"测试验资"、"红队检查"、"测试有效吗"
4. `/test-plan` 补齐测试后，对新生成的关键测试进行验资
5. `/test-verify all` — 全项目测试质量体检

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

## 运行模式

| 模式 | 调用方式 | 行为 |
|------|---------|------|
| **精准模式** | `/test-verify path/to/service.dart` | 仅验证指定文件 |
| **增量模式** | `/test-verify`（无参数） | 从 `git diff --name-only` 提取本次修改的源文件 |
| **全局模式** | `/test-verify all` | 扫描全项目，按 Tier 分级，并行 subagent 执行 |

## 执行流程

### Step 0: 锁定目标

#### 精准模式 / 增量模式

**输入来源**（按优先级）：
1. 用户指定路径 → 精准模式
2. 未指定时，从 `git diff --name-only` 提取本次会话修改的源文件 → 增量模式
3. 目录输入时，扫描目录下所有源文件

这两种模式下，主 Agent 串行处理所有目标文件（与 v0.1 行为一致）。

#### 全局模式（`all`）

当参数为 `all`、`全局`、`全量` 时进入此模式：

1. **扫描项目测试文件**：找到所有 `*_test.dart` / `*.test.ts` / `test_*.py` 等测试文件
2. **反推源文件**：从测试文件路径推导对应的源文件路径
3. **Tier 分级**（见下方筛选策略）
4. **生成目标清单**：在控制台输出扫描结果，等用户确认后执行

```
📋 全局扫描结果：
  Tier 1 (强制验证, 3 files):
    - auth_service.dart → auth_service_test.dart
    - payment_service.dart → payment_service_test.dart
    - order_state_machine.dart → order_state_machine_test.dart
  Tier 2 (抽样验证, 5 files):
    - user_profile_service.dart → user_profile_service_test.dart
    - settings_repository.dart → settings_repository_test.dart
    - ...
  Tier 3 (跳过, 8 files):
    - date_utils.dart, color_utils.dart, ...

  预计派发 SubAgent: 3 (Tier 1) + 2 (Tier 2 抽样) = 5
  确认执行？[Y/n]
```

5. **并行派发 SubAgent**：每个目标文件分配一个 subagent，在同一工作区并行执行 Step 1-2
6. **汇总报告**：收集所有 subagent 结果，输出全局报告
7. **统一修复**：对所有 ESCAPED 变异点，由主 Agent 统一执行 Step 3

#### 前置检查（所有模式通用）

- 目标源文件必须有对应测试文件，无测试则跳过并提示
- 对应测试当前必须通过（先跑一遍确认绿灯）
- 工作区必须干净（无未提交修改）

#### 目标筛选策略（Token 成本敏感，精准点射）

| 优先级 | 类型 | 验证强度 | 示例 |
|--------|------|---------|------|
| Tier 1 | 安全 / 支付 / 状态机 | 强制全量验证（3-5 变异点） | auth, payment, order state |
| Tier 2 | 普通业务 CRUD | 抽样验证（1-2 变异点） | user profile, settings |
| Tier 3 | UI 展示 / 工具函数 | 跳过 | formatDate, ColorUtils |

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
4. **熔断**：同一变异点修复 2 次仍无法 catch → 标记 `[ESCALATION]` AI 升级调试策略（代码设计评审/重构后重试），仍无法解决则写入 to-discuss.md

### Step 4: 输出验证报告

在控制台输出（不生成文件，除非用户要求）。

#### 精准/增量模式（单文件报告）

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

#### 全局模式（汇总报告）

主 Agent 收集所有 subagent 返回的结果，汇总输出：

```markdown
# Global Red Team Verification Report

## Summary

| Tier | Files | Mutations | Caught | Escaped | Score |
|------|-------|-----------|--------|---------|-------|
| Tier 1 | 3 | 12 | 10 | 2 | 83% |
| Tier 2 | 2 | 4 | 3 | 1 | 75% |
| **Total** | **5** | **16** | **13** | **3** | **81%** |

## Details by File

### auth_service.dart (Tier 1) — 3/3 CAUGHT ✅
| M1 | [权限越界] 删除 admin 校验 (L42) | 🟢 CAUGHT |
| M2 | [状态截断] 注释 token 持久化 (L78) | 🟢 CAUGHT |
| M3 | [边界穿透] 允许空密码 (L95) | 🟢 CAUGHT |

### payment_service.dart (Tier 1) — 2/4 CAUGHT ⚠️
| M1 | ... | 🟢 CAUGHT |
| M2 | ... | 🔴 ESCAPED |
| ...

## Escaped Mutations (需修复)

| File | Mutation | Fix Status |
|------|----------|------------|
| payment_service.dart:L67 | [状态截断] 跳过扣款确认 | ✅ 已修复 |
| order_service.dart:L112 | [逻辑反转] 反转退款条件 | ⚠️ ESCALATION |

## Verdict

全局 Mutation Score: 81% (16 mutations, 13 caught)
测试盲点已修复: 2/3 | 需升级处理: 1
```

## 约束

### 铁律

- **先出题后验证**：变异清单必须在执行前完整输出，不能边看测试边选变异点
- **只变异源文件**：Step 2 中禁止修改测试文件（Step 3 修复盲点时才改测试）
- **即时还原**：每个变异执行后必须立即还原，不允许累积变异
- **工作区干净**：开始前 `git status` 确认无未提交更改（有则先提交或 stash）
- **文件独占**（全局模式）：每个源文件只分配给一个 subagent，不允许两个 agent 同时操作同一文件

### 资源控制

**精准/增量模式：**
- 单文件最多 5 个变异点
- 单次调用最多处理 3 个源文件
- Tier 3 文件直接跳过，不浪费 Token
- 修复尝试每个变异点最多 2 次

**全局模式：**
- Tier 1 文件：全部验证，每文件 3-5 个变异点
- Tier 2 文件：最多抽样 5 个文件，每文件 1-2 个变异点
- Tier 3 文件：跳过
- 并行 subagent 上限：5 个（超出则分批执行）
- 每个 subagent 只负责变异检测 + 判定，不做修复（修复统一由主 Agent 处理）
- 修复尝试每个变异点最多 2 次

### 全局模式 SubAgent Prompt 模板

派发 subagent 时，使用以下 prompt 结构：

```
你是 test-verify 红队验证的 subagent。你的任务是对单个源文件执行变异测试。

**目标文件**: {source_file_path}
**测试文件**: {test_file_path}
**Tier**: {tier}
**变异点数量**: {mutation_count}
**测试运行命令**: {test_command}

**执行步骤**：
1. 读取源文件，识别 {mutation_count} 个最致命的业务逻辑变异点
2. 输出变异清单（先出题）
3. 逐个执行：注入变异 → 运行测试 → 判定 CAUGHT/ESCAPED → git checkout 还原
4. 返回结构化结果（JSON 格式）

**铁律**：
- 只修改源文件，不修改测试文件
- 每次变异后立即 git checkout -- {source_file_path} 还原
- 还原后 git diff {source_file_path} 确认干净

**返回格式**：
{
  "file": "{source_file_path}",
  "tier": {tier},
  "mutations": [
    {"id": "M1", "type": "权限越界", "line": 42, "desc": "...", "result": "CAUGHT|ESCAPED"}
  ],
  "score": "2/3"
}
```

### 与其他工具的关系

- 发现测试基础设施问题 → 建议先跑 `/test-audit`
- 发现大量测试缺失 → 建议先跑 `/test-plan`
- 修复盲点后需要提交 → 触发 `git-workflow` skill

## 灵感来源

Reddit r/ClaudeCode 社区讨论 "Claude Code generated hundreds of tests, how do I know they're useful?"
— 手动变异测试 + 对抗 agent 方案的自动化落地。
