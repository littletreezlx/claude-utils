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

### 第一步：运行现有测试

**运行测试**（使用精简输出）：
```bash
# Node.js (Jest/Vitest)
npm test -- --silent 2>&1 | head -50

# Python
pytest -q --tb=short 2>&1 | tail -30

# Flutter ⭐ AI 友好模式
flutter test --reporter=silent --file-reporter=failures-only:test_failures.txt
```

> **Token 效率**：避免输出几万行堆栈，只看关键失败信息

### 第二步：识别缺失的关键测试

**快速判断优先级**：
- 🔴 **必须测试**：认证、支付/交易、核心业务流程
- 🟡 **应该测试**：API 接口、复杂业务逻辑
- 🟢 **可选测试**：工具函数、配置

**识别方式**：
1. 查看现有测试覆盖了什么
2. 检查 🔴🟡 功能是否有测试
3. 直接生成缺失部分的任务

### 第三步：生成任务文件

**任务排序**：按优先级排序（🔴 → 🟡 → 🟢）

```
项目根目录/
├── task-add-test                       # 主任务文件
└── .test-tasks/                        # 任务细节
    ├── stage-1-infrastructure.md       # 测试基础设施修复
    ├── stage-2-critical-tests.md       # 🔴 关键路径测试（并行）
    ├── stage-3-important-tests.md      # 🟡 重要功能测试（并行）
    └── stage-4-verification.md         # 验证
```

---

## 🎯 格式规范（必须遵守）

### 主任务文件格式（task-add-test）

```markdown
# 测试补充任务

## STAGE ## name="infrastructure" mode="serial"
@.test-tasks/stage-1-infrastructure.md

## STAGE ## name="critical-tests" mode="parallel" max_workers="4"
@.test-tasks/stage-2-critical-tests.md

## STAGE ## name="important-tests" mode="parallel" max_workers="4"
@.test-tasks/stage-3-important-tests.md

## STAGE ## name="verification" mode="serial"
@.test-tasks/stage-4-verification.md
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

## 相关文档
- @templates/workflow/DAG_TASK_FORMAT.md - 格式严格参照此详细格式规范
- `/test-run` - 运行测试并修复失败
- `/comprehensive-health-check` - 全面健康检查（包含测试诊断）
