# 项目健康检查任务模板

> **用途**：作为生成 task-health-check 的参考模板
> **使用方式**：Claude Code 基于项目实际情况，使用此模板生成具体的健康检查任务

---

## 主任务文件结构（task-health-check）

```markdown
# 项目健康检查任务

项目：[项目名称]
生成时间：YYYY-MM-DD HH:MM
输出目录：docs/health-check/YYYY-MM-DD/

---

## STAGE ## name="test-health" mode="parallel" max_workers="4"
# 阶段1：测试健康检查（并行执行）

@.health-check-tasks/stage-1-test-health.md

## STAGE ## name="code-quality" mode="parallel" max_workers="4"
# 阶段2：代码质量检查（并行执行）

@.health-check-tasks/stage-2-code-quality.md

## STAGE ## name="architecture" mode="serial"
# 阶段3：架构一致性检查（串行执行）

@.health-check-tasks/stage-3-architecture.md

## STAGE ## name="documentation" mode="parallel" max_workers="2"
# 阶段4：文档一致性检查（并行执行）

@.health-check-tasks/stage-4-documentation.md

## STAGE ## name="summary" mode="serial"
# 阶段5：生成总结报告并自动生成修复任务

@.health-check-tasks/stage-5-summary.md
```

---

## 测试健康检查任务模板（stage-1-test-health.md）

```markdown
## TASK ##
检查 [模块名] 的测试健康度

**背景**：
检查 [模块名] 模块的所有测试是否正常运行，识别失败测试和测试覆盖盲区。

**任务**：
1. 运行所有测试：
   - E2E测试：[命令]
   - 单元测试：[命令]
2. 分析测试覆盖率（如果支持）
3. 检查测试质量：
   - 是否有失败的测试？
   - 测试是否过时？（选择器、API 不匹配）
   - 是否缺少关键场景的测试？
4. 记录问题到：docs/health-check/YYYY-MM-DD/test-[模块].md

**输出格式**：
```markdown
# [模块名] 测试健康检查

## 测试运行结果
- E2E测试通过率：X/Y (Z%)
- 单元测试通过率：X/Y (Z%)
- 失败测试列表：[...]

## 发现的问题
- [Critical] 测试失败：test_xxx (原因：...)
  - 问题ID：critical-test-[模块]-1
  - 文件：tests/[模块]/xxx.test.ts:45
  - 原因：选择器已变更，需要更新测试

- [High] 缺少测试：功能 XXX 没有测试覆盖
  - 问题ID：high-test-[模块]-1
  - 缺失功能：用户登出流程

- [Medium] 测试过时：test_yyy 使用了废弃的 API
  - 问题ID：medium-test-[模块]-1
  - 文件：tests/[模块]/yyy.test.ts:78

## 建议优先级
- Critical（必须修复）：[critical-test-[模块]-1]
- High（建议修复）：[high-test-[模块]-1]
- Medium（可选修复）：[medium-test-[模块]-1]
\```

文件: tests/[模块]/**/*.test.ts
文件: tests/[模块]/**/*.py
验证: [ -f docs/health-check/YYYY-MM-DD/test-[模块].md ]
```

---

## 代码质量检查任务模板（stage-2-code-quality.md）

```markdown
## TASK ##
检查 [模块名] 的代码质量

**背景**：
深度审查 [模块名] 模块的代码质量，识别需要重构的代码。

**任务**：
1. 读取测试检查结果：docs/health-check/YYYY-MM-DD/test-[模块].md
2. 代码审查（抽样 3-5 个关键文件）：
   - 函数复杂度（>60行需要拆分）
   - 文件大小（>600行需要拆分）
   - 嵌套层次（>4层需要简化）
   - 类型注解完整性（TypeScript strict mode, Python mypy）
   - 循环依赖检测
3. 检查注释和文档：
   - 关键函数是否有注释？
   - 是否有文件头部注释说明模块用途？
   - 复杂逻辑是否有解释？
4. 记录问题到：docs/health-check/YYYY-MM-DD/code-[模块].md

**输出格式**：
```markdown
# [模块名] 代码质量检查

## 质量评分：B+ (78/100)

## 审查文件列表
- src/[模块]/file1.ts (核心业务逻辑)
- src/[模块]/file2.py (数据访问层)
- src/[模块]/file3.ts (API 路由)

## 发现的问题
- [High] 函数过长：src/[模块]/xxx.py:87 (120行)
  - 问题ID：high-code-[模块]-1
  - 函数名：process_data()
  - 建议：拆分为 validate_data(), transform_data(), save_data()

- [Medium] 缺少类型注解：src/[模块]/yyy.ts:45
  - 问题ID：medium-code-[模块]-1
  - 函数名：calculateTotal()
  - 建议：添加参数和返回值类型

- [Low] 缺少注释：src/[模块]/zzz.py:100-110
  - 问题ID：low-code-[模块]-1
  - 复杂业务逻辑缺少解释

## 建议优先级
- Critical（必须修复）：[]
- High（建议修复）：[high-code-[模块]-1]
- Medium（可选修复）：[medium-code-[模块]-1]
- Low（优化建议）：[low-code-[模块]-1]
\```

文件: src/[模块]/**/*
排除: src/[模块]/**/*.test.*
验证: [ -f docs/health-check/YYYY-MM-DD/code-[模块].md ]
```

---

## 架构检查任务模板（stage-3-architecture.md）

```markdown
## TASK ##
检查分层架构一致性

**背景**：
检查项目是否遵循分层架构规范，识别跨层调用和反向依赖。

**任务**：
1. 读取所有代码质量检查结果
2. 检查分层规范（如果项目使用分层架构）：
   - Service 层是否包含业务逻辑？
   - Repository 层是否只负责数据访问？
   - Controller 层是否只负责 API 路由？
   - 是否有跨层调用？
3. 检查依赖流动方向：
   - Controller → Service → Repository (正确)
   - 是否有反向依赖？(错误)
4. 记录问题到：docs/health-check/YYYY-MM-DD/arch-layer.md

**输出格式**：
```markdown
# 分层架构一致性检查

## 检查结果
- 遵循分层架构：是/否
- 发现违规点数：X

## 发现的问题
- [Critical] 跨层调用：Controller 直接调用 Repository
  - 问题ID：critical-arch-1
  - 文件：src/api/user.controller.ts:45
  - 违规：UserController → UserRepository (应该 → UserService → UserRepository)

- [High] 反向依赖：Repository 依赖 Service
  - 问题ID：high-arch-1
  - 文件：src/repositories/order.repository.ts:67
  - 违规：OrderRepository → OrderService (依赖方向错误)

## 建议优先级
- Critical（必须修复）：[critical-arch-1]
- High（建议修复）：[high-arch-1]
\```

验证: [ -f docs/health-check/YYYY-MM-DD/arch-layer.md ]

## TASK ##
检查循环依赖

**背景**：
识别模块间的循环依赖，这会导致维护困难和潜在的运行时问题。

**任务**：
1. 分析模块间的依赖关系
2. 识别循环依赖：ModuleA → ModuleB → ModuleA
3. 分析依赖深度和复杂度
4. 记录问题到：docs/health-check/YYYY-MM-DD/arch-circular.md

**输出格式**：
```markdown
# 循环依赖检查

## 检查结果
- 发现循环依赖数：X

## 发现的问题
- [Critical] 循环依赖：BiliService ↔ BiliRepository
  - 问题ID：critical-circular-1
  - 文件：src/bili/service.ts:23 → src/bili/repository.ts:45 → src/bili/service.ts:67
  - 建议：引入接口或事件解耦

## 建议优先级
- Critical（必须修复）：[critical-circular-1]
\```

验证: [ -f docs/health-check/YYYY-MM-DD/arch-circular.md ]
```

---

## 文档检查任务模板（stage-4-documentation.md）

```markdown
## TASK ##
检查功能映射文档的准确性

**背景**：
验证 docs/FEATURE_CODE_MAP.md 文档是否与实际代码一致。

**任务**：
1. 读取 docs/FEATURE_CODE_MAP.md（如果存在，不存在则跳过）
2. 验证每个功能的文件路径是否存在
3. 验证是否有遗漏的功能（代码存在但文档未记录）
4. 记录问题到：docs/health-check/YYYY-MM-DD/doc-feature-map.md

**输出格式**：
```markdown
# 功能映射文档准确性检查

## 检查结果
- 文档存在：是/否
- 路径准确率：X/Y (Z%)
- 遗漏功能数：X

## 发现的问题
- [High] 路径过时：微信模块路径已变更
  - 问题ID：high-doc-1
  - 文档路径：src/wechat/ (已移至 src/services/wechat/)

- [Medium] 遗漏功能：小红书模块未记录
  - 问题ID：medium-doc-1
  - 实际路径：src/services/xiaohongshu/

## 建议优先级
- High（建议修复）：[high-doc-1]
- Medium（可选修复）：[medium-doc-1]
\```

验证: [ -f docs/health-check/YYYY-MM-DD/doc-feature-map.md ]
```

---

## 总结任务模板（stage-5-summary.md）

```markdown
## TASK ##
生成健康检查总结报告并自动生成修复任务

**背景**：
汇总所有检查结果，生成可操作的问题清单和修复任务文件。

**任务**：
1. 读取所有阶段的输出文件（test-*.md, code-*.md, arch-*.md, doc-*.md）
2. 汇总所有问题，按优先级排序（Critical/High/Medium/Low）
3. 统计整体健康评分
4. 生成 SUMMARY.md：docs/health-check/YYYY-MM-DD/SUMMARY.md
5. **自动分析问题类型，生成对应的修复任务**：
   - 提取所有问题ID和详情
   - 按问题类型分组（测试失败、循环依赖、缺失测试、过时文档、代码质量等）
   - 为每类问题生成修复任务文件：.refactor-tasks/fix-[priority]-[type].md
   - 生成修复主任务文件：task-refactor
6. 输出提示信息

**自动生成 task-refactor 的关键逻辑**：

1. 从所有检查结果中提取问题清单
2. 按问题类型分组：
   - 测试失败（critical-test-*） → fix-critical-tests.md
   - 循环依赖（critical-circular-*） → fix-critical-architecture.md
   - 跨层调用（critical-arch-*） → fix-critical-architecture.md
   - 缺失测试（high-test-*） → fix-high-missing-tests.md
   - 过时文档（high-doc-*, medium-doc-*） → fix-high-outdated-docs.md
   - 代码质量（medium-code-*） → fix-medium-code-quality.md
3. 为每组生成修复任务文件（参考 REFACTOR_TASK_TEMPLATE.md）
4. 生成主任务文件 task-refactor，引用这些修复任务

**输出格式**：
```markdown
# 项目健康检查报告

生成时间：YYYY-MM-DD HH:MM
检查范围：[模块列表]

## 整体评分：B+ (78/100)

- 测试健康度：7/10
- 代码质量：8/10
- 架构一致性：7/10
- 文档完整性：8/10

## 关键问题（Critical - 必须修复）

- [critical-1] 微信模块：3个测试失败
  - 详情：docs/health-check/YYYY-MM-DD/test-wechat.md

- [critical-2] B站模块：存在循环依赖
  - 详情：docs/health-check/YYYY-MM-DD/arch-circular.md

## 重要问题（High - 建议修复）

[列出所有 High 优先级问题]

## 一般问题（Medium - 可选修复）

[列出所有 Medium 优先级问题]

## 统计信息

- 检查模块数：X
- 发现问题总数：Y
  - Critical: X
  - High: Y
  - Medium: Z
  - Low: W

## 建议的修复顺序

1. 修复 Critical 问题（阻塞开发）
2. 修复 High 问题（影响稳定性）
3. 选择性修复 Medium 问题（提升质量）

## 下一步

已自动生成修复任务文件：task-refactor
包含修复任务文件：
- .refactor-tasks/fix-critical-tests.md
- .refactor-tasks/fix-critical-architecture.md
- .refactor-tasks/fix-high-missing-tests.md
- .refactor-tasks/fix-high-outdated-docs.md
- .refactor-tasks/fix-medium-code-quality.md

运行方式：
1. 查看报告：cat docs/health-check/YYYY-MM-DD/SUMMARY.md
2. 审查修复任务：cat task-refactor
3. 执行修复：git commit -am "Before refactor" && python batchcc.py task-refactor
\```

验证: [ -f task-refactor ] && [ -f docs/health-check/YYYY-MM-DD/SUMMARY.md ]
```

---

## 使用说明

1. **Claude Code 生成任务时**：
   - 基于项目实际情况调整任务数量和内容
   - 为每个模块生成独立的检查任务
   - 使用 `@文件引用` 语法保持主文件精简

2. **输出文件命名规范**：
   - 使用当前日期：`YYYY-MM-DD`（如：2025-11-12）
   - 问题ID格式：`[priority]-[type]-[module]-[number]`（如：critical-test-wechat-1）

3. **验证命令要求**：
   - 每个任务都有明确的验证方式
   - 验证通过标准：输出文件存在且格式正确

4. **模块化原则**：
   - 主文件精简，只包含 STAGE 定义和文件引用
   - 详细任务放在独立文件中
   - 便于维护和调试
