# 项目修复任务模板

> **用途**：作为自动生成 task-refactor 和修复任务文件的参考模板
> **使用方式**：在健康检查的 Summary 阶段，基于发现的问题自动生成修复任务

---

## 主任务文件结构（task-refactor）

```markdown
# 项目修复任务

基于健康检查报告：docs/health-check/YYYY-MM-DD/SUMMARY.md
生成时间：YYYY-MM-DD HH:MM

---

## STAGE ## name="fix-critical" mode="serial"
# 阶段1：修复阻塞性问题（串行，避免冲突）

@.refactor-tasks/fix-critical-tests.md
@.refactor-tasks/fix-critical-architecture.md

## STAGE ## name="fix-high" mode="parallel" max_workers="3"
# 阶段2：修复重要问题（并行，提高效率）

@.refactor-tasks/fix-high-missing-tests.md
@.refactor-tasks/fix-high-outdated-docs.md

## STAGE ## name="fix-medium" mode="parallel" max_workers="4"
# 阶段3：修复一般问题（并行）

@.refactor-tasks/fix-medium-code-quality.md

## STAGE ## name="final-verification" mode="serial"
# 阶段4：最终验证

## TASK ##
运行全量测试验证

**背景**：
确保所有修复都已成功，没有引入新的问题。

**任务**：
1. 运行所有测试：
   - E2E测试：npm run test:e2e 或 pytest tests/e2e/ -v
   - 单元测试：npm test 或 pytest tests/ -v
2. 检查是否有新的失败
3. 生成修复报告：docs/health-check/YYYY-MM-DD/REFACTOR_RESULT.md

**REFACTOR_RESULT.md 格式**：
```markdown
# 项目修复结果报告

修复时间：YYYY-MM-DD HH:MM
基于报告：docs/health-check/YYYY-MM-DD/SUMMARY.md

## 修复概况

### 成功修复的问题（X个）
- [critical-1] 微信模块：3个测试失败 ✅
- [critical-2] B站模块：存在循环依赖 ✅
- [high-1] 小红书模块：缺少集成测试 ✅
- [high-2] 功能映射文档过时 ✅

### 遗留问题（Y个）
- [medium-1] 代码注释不足（8个文件）- 未修复（需手动处理）

## 测试验证结果

- E2E测试通过率：100% (X/X passed)
- 单元测试通过率：100% (Y/Y passed)
- 总体健康度提升：B+ (78/100) → A- (85/100)

## 代码变更统计

- 修改文件数：X
- 新增测试数：Y
- 删除废弃代码行数：Z

## 建议的后续行动

1. 提交代码：git commit -am "refactor: fix critical and high issues from health check"
2. 推送到远程：git push
3. 更新项目文档（如有需要）
\```

验证: pytest tests/ -v && npm test
```

---

## 修复测试失败任务模板（fix-critical-tests.md）

```markdown
## TASK ##
修复 [模块名] 的失败测试

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/test-[模块].md
- 问题ID：critical-test-[模块]-1
- 失败数：X 个测试失败

**失败测试清单**：
- test_parse_message (tests/[模块]/test_message.py:45)
  - 原因：预期JSON格式变化
- test_send_reply (tests/[模块]/test_api.py:67)
  - 原因：API签名算法错误
- test_upload_media (tests/[模块]/test_upload.py:89)
  - 原因：文件路径错误

**任务**：
1. 逐个分析失败测试
2. 阅读测试文件和实现代码
3. 判断失败原因：
   - 代码有 bug → 修复代码
   - 测试过时 → 更新测试（需谨慎，优先信任测试意图）
   - API/数据格式变更 → 同步更新代码和测试
4. 修复后运行测试验证
5. 确保全部通过

**修复原则**：
- 优先信任测试的意图（测试定义了预期行为）
- 如果确认测试过时，需要理解原始测试意图再修改
- 每修复一个测试，立即运行验证
- 不要在错误代码基础上继续修改（失败3次立即回滚）

文件: src/[模块]/**/*
文件: tests/[模块]/**/*.test.*
验证: pytest tests/[模块]/ -v

## TASK ##
修复其他模块的失败测试

[重复上述结构，为每个有失败测试的模块生成一个任务]
```

---

## 修复架构问题任务模板（fix-critical-architecture.md）

```markdown
## TASK ##
解决 [模块名] 的循环依赖

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/arch-circular.md
- 问题ID：critical-circular-1
- 循环链：BiliService ↔ BiliRepository

**任务**：
1. 分析循环依赖链：
   - 哪个方向是合理的？（应该 Service → Repository）
   - 为什么会产生反向依赖？
2. 设计解决方案：
   - 方案1：引入接口抽象（推荐）
   - 方案2：使用事件驱动解耦
   - 方案3：重构模块职责
3. 实施重构
4. 运行测试验证
5. 更新文档：FEATURE_CODE_MAP.md（如果文件路径有变化）

**重构示例**（接口抽象方案）：
```typescript
// Before（循环依赖）
// BiliService → BiliRepository → BiliService

// After（引入接口）
// BiliService → IBiliRepository ← BiliRepository
// BiliService 依赖接口，Repository 实现接口，打破循环
```

文件: src/[模块]/service.ts
文件: src/[模块]/repository.ts
验证: pytest tests/[模块]/ -v

## TASK ##
修复跨层调用问题

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/arch-layer.md
- 问题ID：critical-arch-1
- 违规：UserController 直接调用 UserRepository（跳过 Service 层）

**任务**：
1. 识别跨层调用位置
2. 重构代码：
   - Controller → Service → Repository（正确）
   - 如果 Service 层缺失，创建 Service 层
3. 运行测试验证

文件: src/api/[模块].controller.ts
文件: src/services/[模块].service.ts
验证: pytest tests/[模块]/ -v
```

---

## 补充测试任务模板（fix-high-missing-tests.md）

```markdown
## TASK ##
为 [模块名] 补充集成测试

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/test-[模块].md
- 问题ID：high-test-[模块]-1
- 缺失：完整的用户流程集成测试

**任务**：
1. 阅读 E2E 测试规范：docs/standards/E2E_STANDARDS.md（如果存在）
2. 识别缺失的测试场景：
   - 核心业务流程
   - 错误处理场景
   - 边界条件
3. 编写测试：
   - 遵循项目测试规范
   - 使用清晰的测试描述
   - 添加指导性的错误消息
4. 运行测试验证
5. 更新测试覆盖度地图：docs/testing/COVERAGE_MAP.md（如果维护此文档）

**测试示例**：
```typescript
test('用户完整登录流程', async () => {
  // 1. 打开登录页
  await page.goto('/login')

  // 2. 输入凭证
  await page.fill('[data-testid="username"]', 'testuser')
  await page.fill('[data-testid="password"]', 'password123')

  // 3. 提交登录
  await page.click('[data-testid="login-button"]')

  // 4. 验证登录成功
  await expect(page.locator('[data-testid="user-profile"]')).toBeVisible()
})
```

文件: tests/[模块]/integration/**/*.test.ts
验证: npm run test:e2e -- tests/[模块]/
```

---

## 更新文档任务模板（fix-high-outdated-docs.md）

```markdown
## TASK ##
更新功能映射文档

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/doc-feature-map.md
- 问题ID：high-doc-1, high-doc-2, medium-doc-1
- 过时条目数：5

**过时条目清单**：
- 微信模块路径：src/wechat/ → src/services/wechat/
- B站模块路径：src/bili/ → src/services/bili/
- 遗漏功能：小红书模块（src/services/xiaohongshu/）

**任务**：
1. 读取问题清单
2. 验证实际文件路径
3. 更新 FEATURE_CODE_MAP.md
4. 检查是否有其他遗漏
5. 验证更新后的准确性

文件: FEATURE_CODE_MAP.md
验证: [ -f FEATURE_CODE_MAP.md ] && echo "✅ 文档已更新"

## TASK ##
更新测试覆盖度文档

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/doc-coverage.md
- 问题ID：medium-doc-2
- 过时条目数：3

**任务**：
1. 读取 docs/testing/COVERAGE_MAP.md
2. 对比实际测试文件
3. 更新过时条目
4. 添加缺失的测试文件记录
5. 验证准确性

文件: docs/testing/COVERAGE_MAP.md
验证: [ -f docs/testing/COVERAGE_MAP.md ]
```

---

## 代码质量优化任务模板（fix-medium-code-quality.md）

```markdown
## TASK ##
重构 [模块名] 的过长函数

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/code-[模块].md
- 问题ID：high-code-[模块]-1, high-code-[模块]-2
- 函数数：3 个函数过长（>60行）

**过长函数清单**：
- src/[模块]/xxx.py:87 - process_data() (120行)
  - 建议拆分：validate_data() + transform_data() + save_data()
- src/[模块]/yyy.ts:45 - calculateTotal() (85行)
  - 建议拆分：applyDiscounts() + calculateTax() + formatResult()

**任务**：
1. 逐个重构过长函数
2. 拆分原则：
   - 单一职责（一个函数只做一件事）
   - 语义化命名（函数名清晰表达意图）
   - 保持原有功能不变
3. 运行测试验证（确保行为未改变）
4. 如果测试失败，回滚重新设计

**重构原则**：
- 保持原有函数签名（避免破坏调用者）
- 提取的子函数可以是私有函数（内部使用）
- 优先信任现有测试（测试定义了正确行为）
- 失败3次立即回滚，重新思考

文件: src/[模块]/**/*.ts
文件: src/[模块]/**/*.py
排除: src/[模块]/**/*.test.*
验证: pytest tests/[模块]/ -v

## TASK ##
补充类型注解

**背景**：
- 来源：docs/health-check/YYYY-MM-DD/code-[模块].md
- 问题ID：medium-code-[模块]-1
- 缺失注解数：8 个文件

**任务**：
1. 为函数添加参数和返回值类型注解
2. 启用 TypeScript strict mode 或 Python mypy 验证
3. 修复类型错误
4. 运行测试验证

文件: src/[模块]/**/*.ts
文件: src/[模块]/**/*.py
验证: tsc --noEmit 或 mypy src/[模块]/
```

---

## 自动生成修复任务的逻辑

在 `stage-5-summary.md` 任务中，基于问题清单自动生成修复任务：

```python
# 伪代码：自动生成修复任务的逻辑

def generate_refactor_tasks(问题清单):
    # 1. 按问题类型分组
    问题分组 = {
        'critical-tests': [],       # 测试失败
        'critical-architecture': [], # 循环依赖、跨层调用
        'high-tests': [],           # 缺失测试
        'high-docs': [],            # 过时文档
        'medium-code': []           # 代码质量
    }

    for 问题 in 问题清单:
        if 问题.id.startswith('critical-test'):
            问题分组['critical-tests'].append(问题)
        elif 问题.id.startswith('critical-circular') or 问题.id.startswith('critical-arch'):
            问题分组['critical-architecture'].append(问题)
        elif 问题.id.startswith('high-test'):
            问题分组['high-tests'].append(问题)
        elif 问题.id.startswith('high-doc') or 问题.id.startswith('medium-doc'):
            问题分组['high-docs'].append(问题)
        elif 问题.id.startswith('medium-code') or 问题.id.startswith('high-code'):
            问题分组['medium-code'].append(问题)

    # 2. 为每组生成修复任务文件
    if 问题分组['critical-tests']:
        生成文件('.refactor-tasks/fix-critical-tests.md', 问题分组['critical-tests'])

    if 问题分组['critical-architecture']:
        生成文件('.refactor-tasks/fix-critical-architecture.md', 问题分组['critical-architecture'])

    if 问题分组['high-tests']:
        生成文件('.refactor-tasks/fix-high-missing-tests.md', 问题分组['high-tests'])

    if 问题分组['high-docs']:
        生成文件('.refactor-tasks/fix-high-outdated-docs.md', 问题分组['high-docs'])

    if 问题分组['medium-code']:
        生成文件('.refactor-tasks/fix-medium-code-quality.md', 问题分组['medium-code'])

    # 3. 生成主任务文件 task-refactor
    生成主任务文件('task-refactor', 问题分组)
```

---

## 使用说明

1. **自动生成时机**：
   - 在健康检查的 Summary 阶段（stage-5-summary.md）
   - 读取所有检查结果后自动触发

2. **文件生成规则**：
   - Critical 问题 → serial 模式（串行修复，避免冲突）
   - High/Medium 问题 → parallel 模式（并行修复，提高效率）
   - 每个任务都有明确的验证命令

3. **验证机制**：
   - 每个修复任务完成后运行测试验证
   - 失败则停止，不继续后续任务
   - 建议用户先提交代码再运行修复（便于回滚）

4. **回滚策略**：
   - 修复前提示用户：`git commit -am "Before refactor"`
   - 失败时提示：`git reset --hard HEAD`
   - 每个 STAGE 可以独立回滚
