# 深度分析框架（Deep Analysis Framework）

> **用途**：解决 Claude Code "只见森林，不见树木" 的问题
>
> **核心创新**：多会话归并策略 + 强制执行机制 + 分层验证

---

## 🎯 核心问题

### "只见森林，不见树木"的根本原因

**用户观察**：
> "只看到表面代码结构文档测试都完整，实际内部有很多问题没有观察到"

**5 个根本原因**：

1. **缺少强制执行** ⚠️
   - AI 通过"读文件"就勾选检查项，而不实际运行工具
   - 示例：检查测试覆盖度 → 只读了 tests/ 目录 → ✅ 有测试
   - 实际：测试可能失败、覆盖度可能很低

2. **缺少验证层级** ⚠️
   - 只验证"有没有"，不验证"对不对"、"准不准"
   - 示例：文档存在 ✅ → 但内容可能过时

3. **缺少负面检查** ⚠️
   - 只检查"应该有什么"，不检查"不应该有什么"
   - 示例：临时文件、调试代码、过时注释堆积

4. **缺少抽样深度** ⚠️
   - 全面浅层扫描 vs 抽样深度验证
   - AI context 有限，不可能深度分析所有文件

5. **单次会话限制** ⚠️
   - 试图在一次会话中完成所有分析
   - 导致只能浅层扫描
   - 无法深入每个模块

---

## 🔄 解决方案：多会话归并策略

### 核心理念（归并算法思想）

不在单次会话中完成所有分析，而是：

```
Planning Phase（规划阶段）
→ 快速扫描项目结构
→ 分解为 10+ 个独立任务
→ 保存到本地文件

Execute Phase × N（执行阶段）
→ 每次会话分析一个任务
→ 深度分析（实际运行测试、逐文件审查）
→ 保存结果，更新任务清单

Merge Phase（归并阶段）
→ 归并所有分析结果
→ 生成最终报告
```

### 为什么有效？

| 维度 | 单次会话方案 | 多会话归并方案 |
|------|--------------|----------------|
| **任务粒度** | 试图一次性分析所有模块 | 每次专注分析单个模块 |
| **分析深度** | 浅层扫描 | 深度分析（实际运行测试、逐文件审查） |
| **覆盖范围** | 抽样 3-5 个模块 | 全部核心模块（10+） |
| **可中断性** | 中断后重新开始 | 随时中断和恢复 |
| **上下文效率** | 每次重新扫描项目 | 读取保存的 context.md |

---

## 📂 任务持久化机制

### 文件结构

```
docs/health-check/analysis-tasks/
├── TODO.md                       # 任务清单（多会话共享）
├── context.md                    # 项目上下文（避免重复扫描）
├── task-01-wechat-deep.md       # 任务描述
├── task-01-wechat-deep-RESULT.md # 分析结果
├── task-02-bili-deep.md
├── task-02-bili-deep-RESULT.md
└── ...
```

### TODO.md 格式

```markdown
# 任务清单

## 总体进度：3/12 (25%)

## 优先级 P0
- [x] task-01-wechat-deep.md ✅ 2025-11-08
  - 发现问题：1 个 P0，3 个 P1，2 个 P2

- [x] task-02-bili-deep.md ✅ 2025-11-08
  - 发现问题：1 个 P0，5 个 P1，3 个 P2

- [ ] task-03-rss-deep.md ← 下一个任务

## 优先级 P1
- [ ] task-04-download-deep.md
...

## ✅ 已完成
- task-01-wechat-deep.md (2025-11-08)
  → 分析结果：task-01-wechat-deep-RESULT.md
- task-02-bili-deep.md (2025-11-08)
  → 分析结果：task-02-bili-deep-RESULT.md
```

### context.md 格式

```markdown
# 项目上下文（供后续会话参考）

> **用途**：避免每次会话都重新扫描项目，快速恢复上下文

## 项目基本信息
- 项目名称：
- 架构：
- 技术栈：

## 核心模块列表
1. 模块名
   - 前端：路径
   - 后端：路径
   - 测试：路径
   - 覆盖度：XX%
   - 状态：🟢/🟡/🔴

## 关键文档位置
- 功能映射：FEATURE_CODE_MAP.md
- 测试覆盖：docs/testing/COVERAGE_MAP.md
...

## 已知问题（从 PROJECT_STATUS.md）
- ⚠️ 模块 A - 问题描述
- ⚠️ 模块 B - 问题描述
```

### task-XX.md 格式（任务描述）

```markdown
# Task XX: [模块名] 深度分析

**优先级**：P0/P1/P2
**预计发现问题**：5-10

---

## 🎯 分析目标
深度分析 [模块名] 的代码质量、测试覆盖、文档一致性

## 📂 分析范围
- 前端代码：路径
- 后端代码：路径
- 测试代码：路径
- 相关文档：路径

## 🔍 分析维度

### 1. 强制执行检查
（必须实际运行的命令列表）

### 2. 三层验证
（Layer 1/2/3 检查清单）

### 3. 深度代码审查
（抽样 3-5 个关键文件逐行审查）

### 4. 负面检查
（不应该存在的内容）

## 📊 输出格式
生成 `task-XX-RESULT.md`

## 🎯 成功标准
（完成的标准）
```

### task-XX-RESULT.md 格式（分析结果）

```markdown
# [模块名] 深度分析结果

分析时间：YYYY-MM-DD HH:MM
分析者：Claude Code AI

---

## 📊 总体评分：X/10

- 代码质量：X/10
- 测试可靠性：X/10
- 文档完整性：X/10
- 一致性：X/10

---

## 🚨 P0 问题（阻塞，必须修复）

### 1. 问题标题
- **文件**：路径:行号
- **问题**：具体描述
- **原因**：根本原因
- **影响**：影响范围
- **修复**：具体修复建议
- **优先级**：P0

---

## ⚠️ P1 问题（重要，建议修复）

（类似格式）

---

## 💡 P2 问题（优化建议）

（类似格式）

---

## ✅ 优点（值得保持）

- ✅ 优点 1
- ✅ 优点 2

---

## 📈 详细分析数据

### 测试运行结果
- E2E 测试：X/Y 通过
- 单元测试：X/Y 通过
- 覆盖度：XX%

### 代码质量检查
- MyPy：X errors
- Ruff：X warnings

### 代码统计
- 总文件数：X
- 总行数：X
- 平均函数长度：X 行
- 最长函数：X 行（文件:行号）

---

## 🔄 建议的改进顺序

1. 立即修复（P0）
2. 本周完成（P1）
3. 下次迭代（P2）
```

---

## 🔧 五大核心机制

### 1. 强制执行机制

**原则**：禁止只读文件就勾选检查项，必须实际运行工具

#### 示例 1：测试覆盖度

❌ **错误做法**：
```
检查测试覆盖度 → 读了 tests/ 目录 → ✅ 有测试
```

✅ **正确做法**：
```bash
# 实际运行测试
pytest --cov=pythonapi --cov-report=term

# 分析输出
总覆盖度：62%（低于目标 80%）

覆盖度 < 80% 的文件：
- pythonapi/services/wechat/core/processor.py: 45%
- pythonapi/services/bili/facade.py: 58%
- ...

具体缺失测试：
- processor.py:87-120 - process_article() 函数未测试
- facade.py:45-60 - error handling 未测试
```

#### 示例 2：E2E 测试

❌ **错误做法**：
```
检查 E2E 测试 → 文件存在 → ✅ 有测试
```

✅ **正确做法**：
```bash
# 实际运行测试
bash scripts/test-helpers/run-e2e-test.sh tests/e2e/wechat/

# 分析输出
测试结果：
- ✅ wechat-workflow.e2e.test.ts: 5/5 通过
- ❌ wechat-mp-management.e2e.test.ts: 2/3 通过
  - 失败：Line 45 - timeout waiting for '[data-testid="article-list"]'
  - 原因：前端 testid 已改为 'wechat-article-list'
  - 修复建议：更新测试选择器
```

#### 示例 3：代码质量

❌ **错误做法**：
```
检查代码质量 → 代码结构清晰 → ✅ 质量良好
```

✅ **正确做法**：
```bash
# 实际运行类型检查
python -m mypy pythonapi/services/wechat/

# 输出
Found 3 errors in 2 files:
- services/wechat/core/processor.py:45 - Missing return type
- services/wechat/facade.py:67 - Incompatible types

# 实际运行代码风格检查
ruff check pythonapi/services/wechat/

# 输出
Found 5 warnings:
- Unused import (F401): services/wechat/routes/article.py:5
- Line too long (E501): services/wechat/core/processor.py:120
```

---

### 2. 三层验证机制

**Layer 1: 存在性检查**（文件/目录是否存在）
```bash
- [ ] pythonapi/services/wechat/ 存在
- [ ] tests/e2e/wechat/ 存在
- [ ] docs/ 中有微信相关文档
```

**Layer 2: 完整性检查**（内容是否完整、格式是否正确）
```bash
- [ ] 代码是否符合规范？
  → 使用 BaseRouteHandler ✅
  → 类型注解完整 ✅
  → 错误处理规范 ⚠️（部分缺失）

- [ ] 测试是否覆盖关键场景？
  → 正常流程 ✅
  → 错误处理 ⚠️（部分缺失）
  → 边界情况 ❌（缺失）

- [ ] 文档是否包含必要章节？
  → 功能说明 ✅
  → API 文档 ⚠️（部分过时）
  → 设计决策 ✅
```

**Layer 3: 一致性检查**（代码-测试-文档是否同步）
```bash
# 检查代码行为与测试断言是否一致
运行测试 → 测试通过 ✅
阅读测试代码 → 断言合理 ✅
对比代码实现 → 行为一致 ✅

# 检查代码实现与文档描述是否一致
文档说明：支持 AI 优化功能
代码实现：article_processor.py:234 新增 AI 优化
文档更新：❌ README.md 未提及此功能

# 检查 API 响应格式是否符合 API_STANDARDS.md
运行 API 测试 → 获取实际响应
对比 API_STANDARDS.md → ✅ 符合 StandardResponse 格式
```

**示例**：
```markdown
检查 API 文档：

Layer 1: ✅ docs/standards/API_STANDARDS.md 存在

Layer 2: ✅ 包含 BaseRouteHandler、StandardResponse 示例

Layer 3: 一致性检查
→ grep -r "BaseRouteHandler" pythonapi/routes/
→ 发现 82% 路由使用 BaseRouteHandler
→ 18% 路由仍使用旧 APIRouter
→ 结论：⚠️ 部分 API 未迁移到 BaseRouteHandler
```

---

### 3. 抽样深度验证

**原则**：不可能深度分析所有文件，必须抽样

**执行步骤**：

1. **识别关键模块**（3-5 个核心功能）
   - 基于 FEATURE_CODE_MAP.md
   - 基于 PROJECT_STATUS.md 已知问题
   - 基于业务重要性

2. **每个模块抽样 1-2 个关键文件**
   - 核心业务逻辑文件（如 processor.py, facade.py）
   - 关键 UI 组件（如 page.tsx）
   - 重要测试文件（如 workflow.e2e.test.ts）

3. **深度分析每个文件**
   - 运行相关测试
   - 逐行阅读代码（检查复杂度、命名、注释）
   - 检查文档是否同步
   - 记录具体问题（文件路径 + 行号）

**示例**：

```markdown
抽样深度验证 - 微信模块

### 文件 1: pythonapi/services/wechat/core/article_processor.py

**实际运行测试**：
```bash
pytest pythonapi/services/wechat/core/tests/test_article_processor.py -v
```

**测试结果**：
- ✅ 所有测试通过（12/12）

**代码质量检查**：
逐行审查 article_processor.py：

- ⚠️ Line 87: 函数 process_article() 过长（120 行）
  → 建议拆分为 3 个子函数：
    - validate_article()
    - transform_content()
    - save_article()

- ⚠️ Line 45-60: 嵌套层级 5 层
  → 示例代码：
    ```python
    if condition1:
        if condition2:
            if condition3:
                if condition4:
                    if condition5:  # 第 5 层
                        # 业务逻辑
    ```
  → 建议提取为独立函数

- ✅ Line 12: 类型注解完整
  ```python
  def process_article(self, article: Article) -> ProcessedArticle:
  ```

- ⚠️ Line 100-110: 复杂业务逻辑缺少注释
  → 建议添加注释解释业务规则

**文档同步检查**：
- ❌ README.md 未提及 AI 优化功能（Line 234 新增）
  → 建议更新 README.md

---

### 文件 2: tests/e2e/wechat/wechat-workflow.e2e.test.ts

**实际运行测试**：
```bash
bash scripts/test-helpers/run-e2e-test.sh tests/e2e/wechat/wechat-workflow.e2e.test.ts
```

**测试结果**：
- ✅ 通过（5/5）

**测试质量检查**：
逐行审查测试代码：

- ✅ Line 15: 使用 data-testid 选择器
  ```typescript
  await page.locator('[data-testid="article-list"]').click()
  ```

- ⚠️ Line 45: 断言过于宽松
  ```typescript
  await expect(page.locator('[data-testid="success-msg"]'))
    .toBeVisible()
  ```
  → 建议改为更具体的断言：
  ```typescript
  await expect(page.locator('[data-testid="success-msg"]'))
    .toContainText('文章处理成功')
  ```

- ❌ Line 67: 缺少错误处理测试
  → 建议添加测试场景：
    - 网络错误
    - 无效文章格式
    - 权限不足

---

### 文件 3: app/(dashboard)/wechat/page.tsx

（类似深度分析）
```

---

### 4. 负面检查清单

**原则**：不仅检查"应该有什么"，也检查"不应该有什么"

#### ❌ 不应该存在的文件

```bash
# 临时文件
find . -name "*.tmp" -o -name "*.bak" -o -name "*.swp"
find . -name "summary.md" -o -name "TODO.md" -o -name "notes.md"

# 过时的 BACKUP 文件（超过 7 天）
find . -name "*BACKUP*" -mtime +7

# 未使用的测试文件（文件存在但从未被 import）
（需要静态分析工具）

检查清单：
- [ ] 项目根目录是否有临时文件？（summary.md, TODO.md）
- [ ] 是否有过时的 BACKUP 文件？
- [ ] 是否有未使用的测试文件？
```

#### ❌ 不应该存在的代码

```bash
# 调试代码
grep -r "console.log" app/ | grep -v "// 日志系统"
grep -r "print(" pythonapi/ | grep -v "# 日志" | grep -v "logger"

# 大段被注释的代码（超过 20 行）
（需要手动审查或工具）

# 硬编码的敏感信息
grep -r "API_KEY\s*=\s*['\"]" . --exclude-dir=node_modules
grep -r "password\s*=\s*['\"]" . --exclude-dir=node_modules

# 未使用的 import
ruff check --select F401 pythonapi/

检查清单：
- [ ] 是否有 console.log / print() 调试代码？
- [ ] 是否有大段被注释的代码（> 20 行）？
- [ ] 是否有硬编码的敏感信息？
- [ ] 是否有未使用的 import/依赖？
```

#### ❌ 不应该存在的测试问题

```bash
# 跳过的测试
grep -r "test.skip\|it.skip" tests/
grep -r "pytest.mark.skip" pythonapi/

# test.only（调试用，不应提交）
grep -r "test.only\|it.only" tests/

# 空的测试或 TODO 注释
grep -r "test(.*\{\s*\}\)" tests/
grep -r "TODO.*test" tests/

# 超过 10 秒的慢测试（无必要理由）
（需要实际运行测试并分析）

检查清单：
- [ ] 是否有 test.skip() 或 test.only()？
- [ ] 是否有空的 test() 或 TODO 注释？
- [ ] 是否有超过 10 秒的慢测试？
```

#### ❌ 不应该存在的文档问题

```bash
# 过时的文档（修改时间 > 3 个月）
find docs/ -mtime +90 -type f

# 文档中的失效链接
（需要工具或手动检查）

# 文档与代码不一致
（需要 Layer 3 一致性验证）

检查清单：
- [ ] 是否有超过 3 个月未更新的文档？
- [ ] 文档中是否有失效链接？
- [ ] 文档描述与代码实现是否一致？
```

**示例**：

```markdown
负面检查结果：

### 临时文件（发现 5 个）
- ❌ ./summary.md（78 KB，创建于 2025-10-15）
  → 建议：删除或移至 docs/archive/

- ❌ ./TODO-2024.md（12 KB，创建于 2024-12-20）
  → 建议：已完成的任务删除，未完成的迁移到 PROJECT_STATUS.md

- ❌ ./pythonapi/services/wechat/test.tmp
  → 建议：删除

- ❌ ./CLAUDE-OLD-BACKUP-2.md
  → 建议：归档到 docs/archive/

- ❌ ./app/(dashboard)/wechat/debug.log
  → 建议：删除（已有统一日志系统）

### 调试代码（发现 8 处）
- ❌ app/(dashboard)/wechat/page.tsx:67
  ```typescript
  console.log('DEBUG: article list', articles)
  ```
  → 建议：删除或使用日志系统

- ❌ pythonapi/services/bili/core/video_processor.py:123
  ```python
  print(f"DEBUG: processing video {video_id}")
  ```
  → 建议：使用 logger.debug()

### 跳过的测试（发现 3 处）
- ❌ tests/e2e/twitter/twitter-workflow.e2e.test.ts:45
  ```typescript
  test.skip('Twitter 用户关注', async ({ page }) => {
  ```
  → 原因：API 变更
  → 建议：修复并取消 skip

### 过时的文档（发现 2 个）
- ⚠️ docs/architecture/OLD_DESIGN.md
  → 最后修改：2024-08-01（120 天前）
  → 建议：归档到 docs/archive/ 或删除

- ⚠️ docs/api/legacy-endpoints.md
  → 最后修改：2024-07-15（135 天前）
  → 建议：确认端点是否仍然使用，更新或删除
```

---

## 📊 会话恢复机制

### 第 N 次会话开始时

```bash
1. 读取 TODO.md
   → 了解总体进度（X/Y 完成）
   → 找到下一个待办任务

2. 读取 context.md
   → 恢复项目上下文
   → 避免重新扫描项目

3. 读取下一个任务文件
   → 明确本次分析目标
   → 了解分析范围和维度
```

### 第 N 次会话结束时

```bash
1. 生成 RESULT.md
   → 详细记录发现的问题（文件路径 + 行号）

2. 更新 TODO.md
   → 标记当前任务完成 [x]
   → 记录发现问题数量

3. 提示用户下一步
   → 下一个任务是什么
   → 预计剩余会话数
```

---

## 🎯 使用场景

### 场景 1：全面健康检查

**命令**：`/comprehensive-health-check`

**适用**：
- 项目定期体检（建议每月）
- 接手项目时快速了解
- 重大重构前全面评估

**特点**：
- 多会话归并式分析
- 覆盖所有核心模块
- 深度分析每个模块

---

### 场景 2：专项检查

**命令**：
- `/health-check` - 快速健康检查（单次会话）
- `/e2e-readiness` - E2E 测试专项
- `/refactor-project` - 重构前评估

**适用**：
- 只需要快速检查某个方面
- 时间紧急，无法进行全面检查

**特点**：
- 单次会话完成
- 聚焦特定维度
- 快速给出结论

---

## 💡 最佳实践

### 1. 任务分解原则

**按模块分解**（推荐）：
```
大型项目 → 10+ 个核心模块
每个模块 → 1 个独立任务文件
单个任务 → 足够专注可深度分析
```

**任务独立性要求**：
- 每个任务可独立完成
- 任务之间无依赖关系
- 可随时中断和恢复

**按优先级分解**（推荐）：
```
P0 任务（核心模块）→ 优先执行
P1 任务（重要模块）→ 其次执行
P2 任务（全局检查）→ 最后执行
```

### 2. 深度分析要求

**每个任务必须包含**：
- ✅ 实际运行相关测试
- ✅ 深度审查 3-5 个关键文件
- ✅ 记录具体问题（文件路径 + 行号）
- ✅ 生成详细的 RESULT.md

**禁止行为**：
- ❌ 只读文件不运行测试
- ❌ 浅层扫描不深入审查
- ❌ 模糊问题描述（缺少具体位置）

### 3. 优先级排序

**P0 - 核心模块**（业务关键）：
- 用户注册/登录
- 支付流程
- 核心业务逻辑

**P1 - 重要模块**（功能重要）：
- 内容管理
- 搜索功能
- 通知系统

**P2 - 全局检查**（质量保障）：
- 文档一致性
- 负面检查
- 代码质量全局

### 4. 会话管理

**任务独立性**：
- 每个任务可独立完成
- 任务之间无依赖关系
- 完成一个任务就可中断

**进度持久化**：
- TODO.md 记录完成状态
- RESULT.md 保存分析结果
- context.md 保存项目上下文

**无缝恢复**：
- 新会话自动读取 TODO.md
- 自动定位下一个未完成任务
- 无需重新扫描项目

---

## 🔗 相关文档

- **主检查 command**：`~/.claude/commands/comprehensive-health-check.md`
- **专项检查 commands**：
  - `~/.claude/commands/health-check.md`
  - `~/.claude/commands/e2e-readiness.md`
  - `~/.claude/commands/refactor-project.md`

---

**最后更新**：2025-11-08
**维护者**：Claude Code AI
**核心理念**：多会话归并 + 强制执行 + 分层验证 + 抽样深度 + 负面检查
