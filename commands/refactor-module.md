---
description: 模块重构（DAG）

---

# 模块级重构

> **用途**：单个模块内的职责优化和数据流重构
>
> **特性**：DAG 任务编排 + 断点续传 + 状态管理

**关键约束**：生成的任务将由**低智能模型**（如 GLM4.7）执行，必须遵循"执行模型友好规范"。

---

## 🤖 自主执行原则

**⛔ 强制前置阅读**：
1. @templates/workflow/DAG_TASK_FORMAT.md 的"自主执行原则"章节
2. @templates/workflow/DAG_TASK_FORMAT.md 的"执行模型友好规范"章节 ⭐

**核心**：完全自动化、无人值守执行

✅ **应该做**：自主分析 → 自主决策方案 → 直接执行 → 记录理由
❌ **不应该**：询问用户、列拆分方案让用户选

---

## 🎯 执行目标

```bash
# 1. 生成任务文件
/refactor-module "模块名"

# 2. 预览执行计划
python batchcc.py task-refactor-module-[模块名] --dry-run

# 3. 执行（自动断点续传）
python batchcc.py task-refactor-module-[模块名]
```

**生成文件结构**：
```
项目根目录/
├── task-refactor-module-[模块名]              # 主任务文件
├── task-refactor-module-[模块名].state.json   # 状态文件（自动）
└── .refactor-tasks/module-[模块名]/           # 阶段详情
    ├── stage-1-analysis.md
    ├── stage-2-refactor.md
    ├── stage-3-test.md
    └── stage-4-documentation.md
```

---

## 📋 阶段编排

### STAGE 1: 分析和规划（serial）
- 读取模块所有文件，分析职责和依赖
- 识别问题：职责混乱、循环依赖、耦合过度
- 制定重构计划和目标架构

### STAGE 2: 重构实施（serial）
- 拆分职责混乱的类
- 消除循环依赖
- 优化接口设计

### STAGE 3: 测试验证（serial）
- 运行模块测试
- 验证接口兼容性

### STAGE 4: 文档更新（serial）
- 更新 TECHNICAL.md
- 更新 FEATURE_CODE_MAP.md
- 创建 ADR（如有重要架构变化）

---

## ⭐ 任务格式（执行模型友好版）

每个 TASK 必须使用增强格式，确保低智能执行模型能正确理解：

```markdown
## TASK ##
拆分 UserService 的认证职责

**🏠 项目背景**：
电商后台系统，NestJS + TypeORM。
当前重构 user 模块，UserService 职责混乱（30+ 方法）。

**🎯 任务目标**：
将认证相关方法（login, logout, refreshToken 等）提取到 UserAuthService。

**📁 核心文件**：
- `src/modules/user/user.service.ts` - [修改] 移除认证方法
- `src/modules/user/user-auth.service.ts` - [新建] 认证服务
- `src/modules/user/user.module.ts` - [修改] 注册新服务
- `src/modules/user/user.controller.ts` - [修改] 更新依赖注入

**🔨 执行步骤**：
1. 创建 `user-auth.service.ts`，添加 @Injectable() 装饰器
2. 从 `user.service.ts` 迁移 login, logout, refreshToken, validateToken 方法
3. 在 `user.module.ts` 的 providers 中注册 UserAuthService
4. 更新 `user.controller.ts` 中的依赖注入
5. 运行测试验证

**✅ 完成标志**：
- [ ] UserAuthService 包含所有认证相关方法
- [ ] UserService 不再有认证相关方法
- [ ] `npm test -- user` 全部通过

**⚠️ 注意事项**：
- 保持方法签名不变
- 注意依赖注入的顺序

文件: src/modules/user/**/*.ts
验证: npm test -- user --silent
```

---

## 🔧 决策标准

### 自动决策范围（无需询问）

| 情况 | 决策方向 |
|------|----------|
| God Class（25+ 方法） | 按功能拆分，每类 ≤10 方法 |
| 循环依赖 | 引入抽象层打破循环 |
| 重复代码 | 提取到工具类（有明确复用场景） |
| 参数过多（5+） | 提取参数对象 |

### 需标记失败的情况

- ❌ 多种拆分方式同等合理（如按功能 vs 按层次）
- ❌ 需要业务规则判断（如某逻辑属于哪个模块）
- ❌ 涉及跨模块的数据迁移

**失败处理**：标记 `failed` + 说明原因 + 列出可选方案和利弊

---

## ⚠️ 重要约束

1. **模块边界** - 仅重构单个模块，不调整跨模块关系
2. **测试驱动** - 重构前后都运行测试，测试不过不提交
3. **不要过度设计** - 解决现有问题，不为"可能的未来"设计
4. **Git 安全** - 重构前确保工作区干净

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| @templates/workflow/DAG_TASK_FORMAT.md | DAG 语法规范 |
| @refactor-project.md | 项目级重构（多模块） |

---

## 开始执行

**执行步骤**：
1. 深入分析模块，识别重构需求
2. 自主决策重构方案
3. 生成任务文件（DAG 格式 + 阶段详情文件）
4. 输出文件路径和执行命令
