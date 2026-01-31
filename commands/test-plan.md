---
description: 测试规划（DAG 编排）ultrathink

---

# 测试规划（DAG 编排）

> 运行测试 → 识别缺失 → 直接生成任务

**关键约束**：任务描述要清晰简洁，目标明确可验证。

## 🚀 使用方式

```bash
# 1. 生成测试任务
/test-plan

# 2. 预览执行计划
python batchcc.py task-add-test --dry-run

# 3. 执行（自动断点续传）
python batchcc.py task-add-test
```

---

## 🤖 自主执行原则

> **⛔ 强制阅读**：@templates/workflow/DAG_TASK_FORMAT.md（自主执行原则 + 执行模型友好规范）
>
> 核心：识别缺失测试 → 自主决策 → 直接生成任务文件（不询问用户）

---

## 📋 执行策略

### 第一步：运行现有测试并收集信号

**⭐ Flutter 项目特殊处理**：

**检测条件**：
- 存在 `pubspec.yaml`
- 项目路径包含 `flutter/` 目录

**使用统一测试脚本**：
```bash
# 检查上层统一脚本是否存在
if [ -f ../../scripts/test.sh ]; then
    # 使用统一脚本（AI 友好输出）
    ../../scripts/test.sh 2>&1 | head -50
    ../../scripts/run-e2e.sh 2>&1 | head -50
else
    # 回退到标准命令
    flutter test --reporter=compact 2>&1 | head -50
fi
```

**其他项目运行测试**（使用精简输出）：
```bash
# Node.js (Jest/Vitest)
npm test -- --silent 2>&1 | head -50

# Python
pytest -q --tb=short 2>&1 | tail -30

# Flutter（非统一脚本环境）
flutter test --reporter=compact 2>&1 | head -50
```

> **Token 效率**：避免输出几万行堆栈，只看关键失败信息

### 第二步：三维度测试审计 ⭐ NEW

**不仅补全缺失，更要审查质量**。

#### 维度 A：覆盖率缺口（原有逻辑）

| 优先级 | 类型 | 示例 |
|--------|------|------|
| 🔴 必须测试 | 认证、支付/交易、核心业务流程 | 登录、下单、支付回调 |
| 🟡 应该测试 | API 接口、复杂业务逻辑 | 状态机、规则引擎 |
| 🟢 可选测试 | 工具函数、配置 | 纯计算、常量定义 |

#### 维度 B：测试质量审查 ⭐ NEW

**检查现有测试是否存在以下问题**：

| 问题类型 | 信号 | 示例 |
|----------|------|------|
| **过时测试** | 测试的逻辑与当前代码不符 | 测试期望返回 `User`，实际返回 `UserDTO` |
| **无效断言** | 测试总是通过，没有实际验证 | `expect(result).toBeTruthy()` 过于宽泛 |
| **过度 Mock** | Mock 掉了被测逻辑 | 整个函数被 mock，测试的是 mock |
| **脆弱测试** | 依赖外部状态或硬编码时间 | 测试偶发失败 |
| **重复测试** | 多个测试验证同一件事 | 同一 edge case 写了 3 遍 |

#### 维度 C：业务价值评估 ⭐ NEW

**检查测试是否"值得写"**：

| 不值得写的测试 | 原因 | 替代方案 |
|----------------|------|----------|
| getter/setter | 无逻辑 | - |
| 纯展示组件 | E2E 已覆盖 | - |
| 框架生成代码 | 框架保证其正确性 | - |
| 一次性脚本 | 用完即弃 | - |
| 过度抽象的测试 | 测试本身比业务逻辑还复杂 | 简化或删除 |

### 第三步：生成任务文件（包含清理任务）

**任务排序**：按优先级排序（🔴 → 🟡 → 🟢）

```
项目根目录/
├── task-add-test                       # 主任务文件
└── .test-tasks/                        # 任务细节
    ├── stage-1-audit.md                # 📊 现有测试质量审计
    ├── stage-2-cleanup.md              # 🧹 清理过时/无效测试
    ├── stage-3-critical-tests.md       # 🔴 关键路径测试补充（并行）
    ├── stage-4-important-tests.md      # 🟡 重要功能测试补充（并行）
    └── stage-5-verification.md         # ✅ 最终验证
```

**⚠️ 关键变化**：
- 新增 `stage-1-audit`：全面审查现有测试质量
- 新增 `stage-2-cleanup`：清理过时/无效测试
- 后续阶段只补充**有价值**的测试

---

## 🎯 格式规范（必须遵守）

### 主任务文件格式（task-add-test）

```markdown
# 测试审计与补充任务

## STAGE ## name="audit" mode="serial"
@.test-tasks/stage-1-audit.md

## STAGE ## name="cleanup" mode="parallel" max_workers="4"
@.test-tasks/stage-2-cleanup.md

## STAGE ## name="critical-tests" mode="parallel" max_workers="4"
@.test-tasks/stage-3-critical-tests.md

## STAGE ## name="important-tests" mode="parallel" max_workers="4"
@.test-tasks/stage-4-important-tests.md

## STAGE ## name="verification" mode="serial"
@.test-tasks/stage-5-verification.md
```

### ⚠️ 子文件 TASK 格式（执行模型友好版）

被引用的子文件中，**每个任务必须使用增强格式**：

```markdown
# Stage 2: 关键路径测试 🔴

> **🏠 项目背景**：电商后台系统，NestJS + TypeORM + PostgreSQL。
> 本阶段为核心业务功能补充测试覆盖。

## TASK ##
用户认证流程测试

**🏠 项目背景**：
电商后台系统，NestJS + TypeORM。
认证模块使用 JWT，当前无测试覆盖，属于关键路径。

**🎯 任务目标**：
为认证模块编写单元测试，覆盖登录、注册、Token 刷新等核心场景。

**📁 核心文件**：
- `src/modules/auth/auth.service.ts` - [测试目标] 认证服务
- `src/modules/auth/auth.controller.ts` - [测试目标] 认证控制器
- `src/modules/auth/__tests__/auth.service.spec.ts` - [新建] 服务测试
- `src/modules/auth/__tests__/auth.controller.spec.ts` - [新建] 控制器测试
- `src/modules/user/__tests__/user.service.spec.ts` - [参考] 查看测试写法

**🔨 执行步骤**：
1. 阅读 `auth.service.ts`，了解认证逻辑
2. 参考 `user.service.spec.ts` 了解项目测试风格
3. 创建 `auth.service.spec.ts`，编写测试用例：
   - 登录成功场景
   - 登录失败（密码错误）
   - Token 刷新逻辑
4. 创建 `auth.controller.spec.ts`，编写 E2E 测试
5. 运行测试验证

**✅ 完成标志**：
- [ ] `auth.service.spec.ts` 已创建，包含 ≥5 个测试用例
- [ ] `auth.controller.spec.ts` 已创建
- [ ] `npm test -- auth` 全部通过
- [ ] 覆盖率 ≥ 80%

**⚠️ 注意事项**：
- 使用项目现有的 mock 工具（查看 `jest.config.js`）
- 不要修改被测试的代码

文件: src/modules/auth/**/*.ts
验证: npm test -- auth --silent

## TASK ##
订单创建流程测试

**🏠 项目背景**：
电商后台系统，订单是核心业务流程。
git log 显示近期频繁修改，需要测试保护。

**🎯 任务目标**：
为订单模块编写测试，覆盖订单创建、库存扣减、支付回调。

**📁 核心文件**：
- `src/modules/order/order.service.ts` - [测试目标]
- `src/modules/order/__tests__/order.service.spec.ts` - [新建]

**🔨 执行步骤**：
1. 阅读 `order.service.ts`，了解订单创建流程
2. 创建测试文件，编写用例
3. 运行测试验证

**✅ 完成标志**：
- [ ] 测试文件已创建
- [ ] `npm test -- order` 全部通过

文件: src/modules/order/**/*.ts
验证: npm test -- order --silent
```

**格式要点**：
- 使用 `## TASK ##`（注意两边都有 `##`）
- **必须包含**：🎯 任务目标、📁 核心文件、✅ 完成标志
- **推荐包含**：🏠 项目背景、🔨 执行步骤
- `文件:` 字段必填（用于冲突检测）
- `验证:` 字段必填（使用 `--silent` 减少输出）

**⚠️ 业务逻辑不清晰时**：
- 在任务描述中添加标记：`⚠️ 需要人工确认断言逻辑`
- 说明哪些断言需要确认（防止把 Bug 当 Feature 测试通过）
- 示例：`⚠️ 需要人工确认：订单取消后库存是否应该自动恢复？`

---

## 📏 字数约束

- **单个 TASK 描述**：15-30 行
- **每个 stage 文件**：60-120 行
- **禁止生成"报告"**：只生成任务文件

---

## 💎 严格禁止

1. **生成诊断报告** ⛔ - 必须生成 DAG 任务文件，不是分析报告
2. **错误的 TASK 格式** ⛔ - 必须用 `## TASK ##`
3. **错误的引用路径** ⛔ - 必须用 `@.test-tasks/`（注意点号），不是 `@test-tasks/`
4. **缺少文件/验证字段** ⛔ - 每个任务必须有
5. **时间估算** ⛔ - 不写"预计时间: 30分钟"
6. **过度详细** ⛔ - 任务描述精简，不写长篇分析

---

## 🧪 Mock 数据策略

**优先级顺序**（从高到低）：

1. **复用已有 fixtures** - 查找 `test/fixtures/`、`__fixtures__/`、`test/factories/`
2. **复用已有 Factory** - 查找 `Factory`、`Builder`、`Faker` 模式
3. **创建共享 helper** - 如果都不存在，**先**创建 `test/test-helpers.ts`

**⛔ 严禁**：在每个 spec 文件里硬编码大量 JSON 测试数据

**任务描述示例**：
```markdown
**📁 核心文件**：
- `test/fixtures/user.fixture.ts` - [参考/扩展] 已有用户测试数据
- `test/test-helpers.ts` - [参考] 已有 mock 工具
```

> 生成任务前先扫描项目的 mock 基础设施，在任务中明确指向

---

## 🔧 测试优先级判断

### 如何识别优先级

| 信号 | 优先级 | 示例 |
|------|--------|------|
| git log 高频修改 | 🔴 | 频繁变更 = 高业务价值 |
| 涉及金钱/交易 | 🔴 | 支付、订单、结算 |
| 用户核心路径 | 🔴 | 认证、主功能入口 |
| API 对外暴露 | 🟡 | 公开接口需要稳定 |
| 复杂业务逻辑 | 🟡 | 状态机、规则引擎 |
| 工具函数 | 🟢 | 纯函数、无副作用 |

### 不需要测试

| 类型 | 原因 |
|------|------|
| getter/setter | 无逻辑 |
| 纯展示组件 | E2E 已覆盖 |
| 一次性脚本 | 用完即弃 |
| 配置常量 | 无行为 |

---

## 📊 测试审计任务示例 ⭐ NEW

### Stage 1: 现有测试质量审计

```markdown
# Stage 1: 测试质量审计 📊

> **🏠 项目背景**：电商后台系统，现有测试 150+ 个。
> 本阶段对现有测试进行全面体检，识别过时、无效、重复的测试。

## TASK ##
审计用户模块测试质量

**🏠 项目背景**：
用户模块有 23 个测试文件，近期认证逻辑从 Session 迁移到 JWT。
需要检查测试是否同步更新。

**🎯 任务目标**：
逐个审查 `src/modules/user/**/__tests__/*.spec.ts`，识别：
1. 过时测试（测试逻辑与代码不符）
2. 无效断言（过于宽泛的断言）
3. 过度 Mock（被测逻辑被 mock 掉）
4. 重复测试（同一场景多次验证）

**📁 核心文件**：
- `src/modules/user/**/*.spec.ts` - [审查目标] 所有测试文件
- `src/modules/user/user.service.ts` - [对比参考] 当前实现
- `src/modules/auth/auth.service.ts` - [对比参考] 新认证逻辑

**🔨 执行步骤**：
1. 列出所有测试文件：`find src/modules/user -name "*.spec.ts"`
2. 逐个阅读测试文件，对照当前实现
3. 标记问题测试：
   - 过时：记录"期望 X，实际 Y"
   - 无效：记录"断言过于宽泛"
   - 过度 mock：记录"被测逻辑被 mock"
4. 生成清理建议清单

**✅ 完成标志**：
- [ ] 输出审计报告：`.test-tasks/audit-user-module.md`
- [ ] 报告包含：问题分类、影响范围、优先级建议

**⚠️ 注意事项**：
- 不修改任何测试文件，仅生成审计报告
- 报告格式：使用 Markdown 表格，清晰列出问题

文件: src/modules/user/**/*.spec.ts
输出: .test-tasks/audit-user-module.md

## TASK ##
审计订单模块测试覆盖率

**🏠 项目背景**：
订单模块是核心业务，测试覆盖率 45%（低于阈值 80%）。
需要识别遗漏的测试场景。

**🎯 任务目标**：
分析订单模块代码，识别未测试的关键路径。

**📁 核心文件**：
- `src/modules/order/order.service.ts` - [分析目标]
- `src/modules/order/__tests__/` - [对比参考] 现有测试

**🔨 执行步骤**：
1. 阅读 `order.service.ts`，列出所有公共方法
2. 对照现有测试，标记未测试的方法
3. 对每个已测试方法，检查分支覆盖：
   - 正常路径
   - 异常路径
   - 边界条件
4. 生成补充测试建议

**✅ 完成标志**：
- [ ] 输出审计报告：`.test-tasks/audit-order-coverage.md`
- [ ] 报告包含：未测试方法列表、分支覆盖分析

文件: src/modules/order/**/*.ts
输出: .test-tasks/audit-order-coverage.md
```

### Stage 2: 清理过时/无效测试

```markdown
# Stage 2: 清理过时与无效测试 🧹

> **🏠 项目背景**：基于 Stage 1 审计结果。
> 本阶段清理过时、无效、重复的测试。

## TASK ##
清理用户模块过时测试

**🏠 项目背景**：
审计发现 `user.service.spec.ts` 中有 3 个过时测试。
这些测试期望 Session 返回，但代码已迁移到 JWT。

**🎯 任务目标**：
修复或删除过时测试，确保测试反映当前业务逻辑。

**📁 核心文件**：
- `src/modules/user/__tests__/user.service.spec.ts` - [修改目标]
- `.test-tasks/audit-user-module.md` - [参考] 审计报告

**🔨 执行步骤**：
1. 阅读审计报告，定位过时测试
2. 确认当前业务逻辑（参考 auth.service.ts）
3. 决策：
   - 如果场景仍有效 → 修复测试断言
   - 如果场景已废弃 → 删除测试
4. 运行测试验证

**✅ 完成标志**：
- [ ] 过时测试已修复或删除
- [ ] `npm test -- user` 全部通过

文件: src/modules/user/__tests__/user.service.spec.ts
验证: npm test -- user --silent

## TASK ##
删除订单模块重复测试

**🏠 项目背景**：
审计发现 `order.service.spec.ts` 中有 5 个测试验证同一边界条件。
重复测试降低维护效率，未增加价值。

**🎯 任务目标**：
合并重复测试，保留最清晰的那个。

**📁 核心文件**：
- `src/modules/order/__tests__/order.service.spec.ts` - [修改目标]

**🔨 执行步骤**：
1. 阅读测试文件，识别重复场景
2. 选择最清晰的测试用例保留
3. 删除其他重复测试
4. 运行测试验证覆盖率未下降

**✅ 完成标志**：
- [ ] 重复测试已删除
- [ ] 测试数量减少，覆盖率未降
- [ ] `npm test -- order` 全部通过

文件: src/modules/order/__tests__/order.service.spec.ts
验证: npm test -- order --silent
```

### 测试问题分类速查表

| 问题类型 | 识别信号 | 处理建议 |
|----------|----------|----------|
| **过时测试** | 测试期望与代码不符 | 修复断言或删除 |
| **无效断言** | `expect().toBeTruthy()` 等 | 改为精确断言 |
| **过度 Mock** | 整个函数被 stub | 减少 mock，测试真实逻辑 |
| **脆弱测试** | 依赖 `Date.now()` 或外部状态 | 注入时间依赖，隔离状态 |
| **重复测试** | 同一断言多次出现 | 合并或删除 |
| **无价值测试** | 测试 getter 或框架代码 | 删除 |

---

## 相关文档
- @templates/workflow/DAG_TASK_FORMAT.md - 格式严格参照此详细格式规范
- `/test-run` - 运行测试并修复失败
- `/comprehensive-health-check` - 全面健康检查（包含测试诊断）
