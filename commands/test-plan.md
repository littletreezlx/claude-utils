---
description: 测试审查与补齐（DAG 编排）ultrathink
---

# 测试审查与补齐（DAG 编排）

> 审查已有测试质量 + 识别测试缺口 → 生成 DAG 任务文件

**典型场景**：AI 开发了大量功能代码，测试缺失或质量存疑（不能运行、断言无意义、覆盖非核心逻辑、过度冗余），需要系统性清理和补齐。

**关键约束**：产出必须是任务文件，不是分析报告。

```bash
/test-plan                                    # 生成测试任务
batchcc task-add-test               # 执行
```

## ⚠️ 重要：入口文件位置

**入口文件 `task-add-test` 必须放在项目根目录**，不是 `.test-tasks/` 目录！

```
✅ 正确：~/project/task-add-test.md           （根目录）
❌ 错误：~/project/.test-tasks/task-add-test.md
```

> **格式规范**：
> - @templates/workflow/DAG_FORMAT.md - DAG 统一规范（**必须遵循**）
> - @templates/workflow/TEST_PLAN_TEMPLATE.md - 测试计划模板（可直接使用）

---

## 执行策略

### 第一步：摸底 — 现有测试能不能跑

**先检查上一轮 test-plan 的遗留**：如果根目录存在 `task-add-test` 或 `.test-tasks/`，读取其 state.json 了解哪些任务已完成、哪些中断，避免重复摸底已覆盖的模块。

运行全量测试（精简输出），快速分类：
- **能跑且有意义** → 保留
- **能跑但断言无意义**（过于宽泛、测的是 mock 而非逻辑） → 标记待改写
- **跑不起来** → 标记待修复或删除
- **过度冗余**（同一逻辑重复测试、测 getter/setter） → 标记待清理

### 第二步：防错误复合——边界优先覆盖

> Agent 的错误会复合放大：A 模块边界错了 → B 模块在错误基础上继续 → 越错越远。
> 因此测试规划优先覆盖**模块边界和集成点**，建立"错误防火墙"。

**边界测试优先级**（高于功能内部测试）：

| 边界类型 | 示例 | 为什么重要 |
|---------|------|----------|
| 模块公共 API | Service 的 public 方法 | Agent 调用的入口，错了影响所有调用方 |
| 数据转换边界 | DTO ↔ Entity、API Response → Model | 数据形状错误会在下游复合 |
| 状态转换边界 | 状态机的合法转换 | 非法状态会导致不可预测行为 |
| 外部集成边界 | API Client、DB Repository | 外部依赖的契约变更是常见错误源 |

### 第三步：审查 — 已有测试写得怎么样

逐模块检查已有测试，判断：

| 问题 | 信号 |
|------|------|
| 测的不是核心逻辑 | 大量测试在验证 UI 文案、配置常量等低价值目标 |
| 断言形同虚设 | `toBeTruthy()`、只检查不抛异常、不验证具体值 |
| 过度 Mock | 整个依赖被 stub，测的是 mock 行为而非真实逻辑 |
| 脆弱不稳定 | 依赖外部状态、硬编码时间、CI 中间歇失败 |
| E2E 占比失衡 | 本该用单元测试验证的逻辑，全堆在 E2E 里（E2E 应仅保留 3-5 条核心生死线） |

### 第四步：补缺 — 还缺什么测试

按业务价值排优先级：

| 优先级 | 类型 | 示例 |
|--------|------|------|
| 🔴 必须 | 认证、支付、核心业务流程 | 登录、下单、支付回调 |
| 🟡 应该 | API 接口、复杂业务逻辑 | 状态机、规则引擎 |
| 🟢 可选 | 工具函数、配置 | 纯计算、常量定义 |

**不写**：getter/setter、纯展示组件、框架生成代码、一次性脚本

### 第五步：生成任务文件

**必须生成两个产出**：

1. **入口文件** `task-add-test`（项目根目录）— `batchcc` 直接执行
2. **任务细节目录** `.test-tasks/` — 存放各阶段详细说明

```
task-add-test                          # ← 入口文件（batchcc 执行这个）
.test-tasks/                           # 任务细节
├── stage-1-triage.md                 # 现有测试分类（保留/改写/删除）
├── stage-2-cleanup.md                # 清理无效和冗余测试
├── stage-3-critical-tests.md         # 关键路径测试（并行）
├── stage-4-important-tests.md        # 重要功能测试（并行）
├── stage-5-verification.md           # 全量运行验证
└── stage-6-review.md                 # 全局审视 + /todo-write 收尾
```

---

## 约束

- Mock 数据优先级：复用已有 fixtures > 复用已有 Factory > 创建共享 helper
- 业务逻辑不清晰时添加 `⚠️ 需要人工确认断言逻辑` 标记
- 自主决策，直接生成任务文件（不询问用户）

## 相关文档

- @templates/workflow/DAG_FORMAT.md - **DAG 统一规范**
- @templates/workflow/TEST_PLAN_TEMPLATE.md - 测试计划模板
- `/test-run` - 运行测试并修复失败
