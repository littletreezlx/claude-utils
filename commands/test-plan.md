# 测试规划（DAG 编排）

> 诊断测试现状，生成可被 batchcc.py 执行的测试任务

## 🚀 使用方式/DAG_TASK_FORMAT.md

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

**⛔ 强制前置阅读**：@templates/workflow/DAG_TASK_FORMAT.md 的"自主执行原则"章节

✅ **应该做**：自主诊断 → 自主决策 → 直接生成任务文件
❌ **不应该**：询问用户、生成"报告"而非任务文件

---

## 📋 执行策略

### 第一步：诊断测试现状

**基础设施检查**：
- 测试框架配置（Jest/Vitest/Pytest/Playwright）
- 覆盖率工具、测试命令

**运行现有测试** ⚠️ 必须执行（使用精简输出）：
```bash
# Node.js (Jest/Vitest)
npm test -- --silent 2>&1 | head -50

# Python
pytest -q --tb=short 2>&1 | tail -30

# Flutter ⭐ AI 友好模式
flutter test --reporter=silent --file-reporter=failures-only:test_failures.txt
# 成功: 无输出，退出码 0
# 失败: 查看 test_failures.txt
```

> **Token 效率**：避免输出几万行堆栈，只看关键失败信息

**质量评估**（抽样 5-10 个测试文件）：
- flaky 测试？超时问题？测试隔离？

**代码可测性评估**：
- 难以 mock → 依赖太多（加入重构任务）
- setup 复杂 → 接口设计问题（加入重构任务）

### 第二步：生成任务编排文件

```
项目根目录/
├── task-add-test                       # 主任务文件
└── .test-tasks/                        # 任务细节
    ├── stage-1-infrastructure.md       # 测试基础设施
    ├── stage-2-test-writing.md         # 测试编写（并行）
    └── stage-3-verification.md         # 验证
```

---

## 🎯 格式规范（必须遵守）

### 主任务文件格式（task-add-test）

```markdown
# 测试补充任务

## STAGE ## name="infrastructure" mode="serial"
@.test-tasks/stage-1-infrastructure.md

## STAGE ## name="test-writing" mode="parallel" max_workers="4"
@.test-tasks/stage-2-test-writing.md

## STAGE ## name="verification" mode="serial"
@.test-tasks/stage-3-verification.md
```

### ⚠️ 子文件 TASK 格式（关键！）

被引用的子文件中，**每个任务必须使用 `## TASK ##` 标记**：

```markdown
# Stage 2: 测试编写

## TASK ##
用户模块单元测试

**📖 背景**：用户模块缺少单元测试
**🔨 要做什么**：为 UserService 添加核心方法测试
**✅ 完成标志**：测试通过，覆盖主要分支

文件: src/modules/user/**/*.ts
验证: npm test -- user

## TASK ##
订单模块集成测试

**📖 背景**：订单创建流程无测试覆盖
**🔨 要做什么**：测试订单创建到支付的完整流程
**✅ 完成标志**：E2E 测试通过

文件: src/modules/order/**/*.ts
验证: npm test -- order
```

**格式要点**：
- 使用 `## TASK ##`（注意两边都有 `##`）
- 任务标题在标记下一行
- `文件:` 字段必填（用于冲突检测）
- `验证:` 字段必填（任务完成后执行，使用精简输出命令）

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

## 🔧 测试优先级判断

| 必须测 | 可选测 | 不用测 |
|--------|--------|--------|
| 核心业务逻辑 | 边界情况 | getter/setter |
| 用户主流程 | 性能测试 | 纯展示组件 |
| 易破坏模块 | 错误处理 | 一次性脚本 |

---

## 相关文档
- @templates/workflow/DAG_TASK_FORMAT.md - 详细格式规范
- `/test-run` - 运行测试并修复失败
- `/comprehensive-health-check` - 全面健康检查（包含测试诊断）
