---
name: test-workflow
description: >
  This skill should be used when code has been modified and needs test
  verification, when tests fail and need diagnosis and fixing, when the user
  asks to "run tests", "check if it works", "verify the fix", or when
  another workflow (like delivery or consistency-check) needs test validation.
  Handles test execution, failure diagnosis, and automated fix loops.
version: 0.1.0
---

# Test Workflow — 运行、诊断、修复

## 目的

代码修改后自动运行测试、诊断失败、修复问题。测试是 Agent 的**行为合约**——通过的测试定义了"什么是正确的"。

## 触发条件

当以下**任一**条件满足时启动：

1. 代码已修改，需要验证正确性
2. 开发过程中遇到测试失败
3. consistency-check 或 delivery-workflow 请求测试验证
4. 用户表达验证意图："能跑通吗？"、"run tests"、"验证一下"

## 执行策略

1. **识别环境** — 定位测试命令和框架，确认环境就绪
   - 测试基础设施本身有问题（命令缺失、框架未配置）→ 建议先执行 `/test-audit`
2. **运行测试** — 使用精准测试（指定文件/模块），而非盲目全量运行
   - 输出重定向到文件，避免终端阻塞
3. **诊断修复** — 优先修复代码 bug，谨慎修改测试用例
4. **验证闭环** — 修复后重新运行，确认没有引入新问题

### 精准测试选择

| 修改范围 | 运行测试 |
|---------|---------|
| 单文件 | 对应测试文件 |
| 模块 | 模块目录测试 |
| 跨模块/架构 | 全量测试 |

```bash
# ✅ 正确 — 指定文件 + 静默模式
jest path/to/specific.test.ts --silent --no-coverage
pytest path/to/test.py -q --tb=short
../scripts/test.sh test/specific_test.dart

# ❌ 错误 — 无脑全量
jest / pytest / flutter test
```

### 大量失败时（>10 个）

先获取失败概览 → 识别共同根因（修一个可能修复多个） → 按目录分批处理

### 死循环熔断

同一测试修复 **3 次仍失败**：停止修复，标记"需要人工介入"，记录已尝试方向，跳过处理下一个。

## 约束

- **测试即合约**：优先修复代码 bug，修改测试 = 修改合约，必须理解原始设计意图
- **防止错误复合**：测试失败时停下来修复，不在失败基础上继续开发
- E2E 使用稳定选择器（data-testid 优先），多次运行验证稳定性

### Flutter 项目特殊说明

- 日常迭代：只跑 unit + widget test（`../scripts/test.sh`）
- **禁止自动跑 E2E**：`integration_test` 需要模拟器，耗时且脆弱，Agent 无法区分环境抖动和真实 Bug
- E2E 仅发布前由用户人工触发
