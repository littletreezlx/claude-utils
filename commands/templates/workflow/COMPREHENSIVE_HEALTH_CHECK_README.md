# 全面健康检查系统 - 使用说明

> **最新更新**：2025-11-12
> **版本**：2.0 (两阶段工作流)

---

## 🎯 系统概述

这是一个完全自动化的项目健康检查和修复系统，采用**两阶段工作流**：

```
阶段1：诊断（Diagnosis）
  → 全面检查项目健康状况
  → 生成详细的问题报告
  → 自动生成修复任务

阶段2：治疗（Treatment）
  → 自动执行修复任务
  → 验证修复结果
  → 生成修复报告
```

---

## 📁 文件结构

```
.claude/commands/
├── comprehensive-health-check.md           # 主命令文件
└── templates/workflow/
    ├── HEALTH_CHECK_TASK_TEMPLATE.md      # 健康检查任务模板
    ├── REFACTOR_TASK_TEMPLATE.md          # 修复任务模板
    └── COMPREHENSIVE_HEALTH_CHECK_README.md  # 本文档
```

**运行时生成的文件**：

```
项目根目录/
├── task-health-check                      # 主任务文件（诊断）
├── task-refactor                          # 修复主任务（自动生成）
│
├── .health-check-tasks/                   # 检查任务细节
│   ├── stage-1-test-health.md            # 测试健康检查
│   ├── stage-2-code-quality.md           # 代码质量检查
│   ├── stage-3-architecture.md           # 架构一致性检查
│   ├── stage-4-documentation.md          # 文档一致性检查
│   └── stage-5-summary.md                # 生成总结和修复任务
│
├── .refactor-tasks/                       # 修复任务细节（自动生成）
│   ├── fix-critical-tests.md             # 修复失败的测试
│   ├── fix-critical-architecture.md       # 修复架构问题
│   ├── fix-high-missing-tests.md         # 补充缺失测试
│   ├── fix-high-outdated-docs.md         # 更新过时文档
│   └── fix-medium-code-quality.md        # 优化代码质量
│
└── docs/health-check/YYYY-MM-DD/          # 检查结果输出目录
    ├── SUMMARY.md                         # 总结报告
    ├── REFACTOR_RESULT.md                # 修复结果报告
    ├── test-[模块].md                    # 各模块测试检查结果
    ├── code-[模块].md                    # 各模块代码质量结果
    ├── arch-*.md                          # 架构检查结果
    └── doc-*.md                           # 文档检查结果
```

---

## 🚀 完整使用流程

### 步骤1: 生成健康检查任务

```bash
/comprehensive-health-check
```

**AI 会做什么**：
1. 扫描项目结构（读取 FEATURE_CODE_MAP.md、PROJECT_STATUS.md 等）
2. 识别所有核心模块
3. 生成以下文件：
   - `task-health-check`（主任务文件，精简）
   - `.health-check-tasks/*.md`（各阶段详细任务）

**输出提示**：
```
✅ 健康检查任务已生成！

文件结构：
├── task-health-check
└── .health-check-tasks/
    ├── stage-1-test-health.md (12个模块检查)
    ├── stage-2-code-quality.md (12个模块检查)
    ├── stage-3-architecture.md (3个架构检查)
    ├── stage-4-documentation.md (2个文档检查)
    └── stage-5-summary.md (生成报告和修复任务)

下一步：
python batchcc.py task-health-check

预计耗时：15-20 分钟
输出目录：docs/health-check/2025-11-12/
```

### 步骤2: 执行健康检查

```bash
python batchcc.py task-health-check
```

**batchcc.py 会做什么**：
1. 解析 DAG 任务文件
2. 按 STAGE 顺序执行：
   - STAGE 1: 测试健康检查（并行执行12个模块）
   - STAGE 2: 代码质量检查（并行执行12个模块）
   - STAGE 3: 架构一致性检查（串行执行3个检查）
   - STAGE 4: 文档一致性检查（并行执行2个检查）
   - STAGE 5: 生成总结报告 + 自动生成修复任务
3. 输出进度和结果

**执行过程示例**：
```
[STAGE 1/5] test-health (parallel, max_workers=4)
├─ [1/12] 检查微信模块的测试健康度 ... ✅ Done (2.3s)
├─ [2/12] 检查B站模块的测试健康度 ... ✅ Done (1.8s)
├─ [3/12] 检查RSS模块的测试健康度 ... ✅ Done (2.1s)
...

[STAGE 2/5] code-quality (parallel, max_workers=4)
├─ [1/12] 检查微信模块的代码质量 ... ✅ Done (3.2s)
...

[STAGE 5/5] summary (serial)
└─ [1/1] 生成健康检查总结报告并自动生成修复任务 ... ✅ Done (4.5s)

✅ 健康检查完成！

📊 总结报告：docs/health-check/2025-11-12/SUMMARY.md

关键发现：
- Critical 问题：2 个（必须修复）
- High 问题：8 个（建议修复）
- Medium 问题：15 个（可选修复）

🔧 已自动生成修复任务：task-refactor

下一步：
1. 查看报告：cat docs/health-check/2025-11-12/SUMMARY.md
2. 决定是否修复
3. 如果修复：git commit -am "Before refactor" && python batchcc.py task-refactor
```

### 步骤3: 查看诊断报告

```bash
cat docs/health-check/$(date +%Y-%m-%d)/SUMMARY.md
```

**报告内容示例**：
```markdown
# 项目健康检查报告

生成时间：2025-11-12 14:30
检查范围：微信、B站、RSS、下载、影视、任务调度、认证、Twitter、日志、咖啡

## 整体评分：B+ (78/100)

- 测试健康度：7/10
- 代码质量：8/10
- 架构一致性：7/10
- 文档完整性：8/10

## 关键问题（Critical - 必须修复）

- [critical-1] 微信模块：3个测试失败
  - 文件：tests/wechat/test_message.py
  - 详情：docs/health-check/2025-11-12/test-wechat.md

- [critical-2] B站模块：存在循环依赖
  - 文件：src/bili/service.py ↔ src/bili/repository.py
  - 详情：docs/health-check/2025-11-12/arch-circular.md

## 重要问题（High - 建议修复）

- [high-1] 小红书模块：缺少集成测试
- [high-2] 功能映射文档过时（5处）
- [high-3] 类型注解缺失（8个文件）

## 一般问题（Medium - 可选修复）

- [medium-1] 代码注释不足（8个文件）
- [medium-2] 部分函数过长（3个函数）

## 统计信息

- 检查模块数：12
- 发现问题总数：45
  - Critical: 2
  - High: 8
  - Medium: 15
  - Low: 20

## 建议的修复顺序

1. 修复 Critical 问题（阻塞开发）
2. 修复 High 问题（影响稳定性）
3. 选择性修复 Medium 问题（提升质量）

## 下一步

已自动生成修复任务文件：task-refactor
运行方式：python batchcc.py task-refactor
```

### 步骤4: 【人工决策】是否修复

此时你需要决定：
- ✅ **修复**：运行 `python batchcc.py task-refactor`
- ❌ **暂不修复**：跳过，以后再处理
- 🔧 **部分修复**：编辑 `.refactor-tasks/*.md` 删除不想修的任务

**如果你决定修复，先提交代码**（便于回滚）：
```bash
git commit -am "Before refactor"
```

### 步骤5: 执行修复

```bash
python batchcc.py task-refactor
```

**batchcc.py 会做什么**：
1. 解析修复任务文件
2. 按 STAGE 顺序执行：
   - STAGE 1: 修复阻塞性问题（串行）
   - STAGE 2: 修复重要问题（并行）
   - STAGE 3: 修复一般问题（并行）
   - STAGE 4: 最终验证（运行全量测试）
3. 每个任务完成后运行验证命令
4. 失败则停止，提示回滚

**执行过程示例**：
```
[STAGE 1/4] fix-critical (serial)
├─ [1/2] 修复微信模块的失败测试 ... ✅ Done (3.5s)
│  验证: pytest tests/wechat/ -v ... ✅ Passed
├─ [2/2] 解决B站模块的循环依赖 ... ✅ Done (4.2s)
│  验证: pytest tests/bili/ -v ... ✅ Passed

[STAGE 2/4] fix-high (parallel, max_workers=3)
├─ [1/2] 为小红书模块补充集成测试 ... ✅ Done (5.1s)
│  验证: npm run test:e2e -- tests/xiaohongshu/ ... ✅ Passed
├─ [2/2] 更新功能映射文档 ... ✅ Done (1.2s)
│  验证: [ -f FEATURE_CODE_MAP.md ] && echo "✅ 文档已更新" ... ✅ Passed

[STAGE 4/4] final-verification (serial)
└─ [1/1] 运行全量测试验证 ... ✅ Done (8.5s)
   验证: pytest tests/ -v && npm test ... ✅ All Passed

✅ 修复完成！

修复的问题：
- [critical-1] 微信模块：3个测试失败 ✅
- [critical-2] B站模块：存在循环依赖 ✅
- [high-1] 小红书模块：缺少集成测试 ✅
- [high-2] 功能映射文档过时 ✅

测试通过率：100% (89/89 passed)

详细报告：docs/health-check/2025-11-12/REFACTOR_RESULT.md

建议提交代码：
git add .
git commit -m "refactor: fix critical and high issues from health check"
```

### 步骤6: 查看修复报告

```bash
cat docs/health-check/$(date +%Y-%m-%d)/REFACTOR_RESULT.md
```

**报告内容示例**：
```markdown
# 项目修复结果报告

修复时间：2025-11-12 15:45
基于报告：docs/health-check/2025-11-12/SUMMARY.md

## 修复概况

### 成功修复的问题（4个）
- [critical-1] 微信模块：3个测试失败 ✅
- [critical-2] B站模块：存在循环依赖 ✅
- [high-1] 小红书模块：缺少集成测试 ✅
- [high-2] 功能映射文档过时 ✅

### 遗留问题（11个）
- [medium-1] 代码注释不足（8个文件）- 未修复（需手动处理）
- [medium-2] 部分函数过长（3个函数）- 未修复（需手动处理）

## 测试验证结果

- E2E测试通过率：100% (45/45 passed)
- 单元测试通过率：100% (44/44 passed)
- 总体健康度提升：B+ (78/100) → A- (85/100)

## 代码变更统计

- 修改文件数：8
- 新增测试数：5
- 删除废弃代码行数：120

## 建议的后续行动

1. 提交代码：git commit -am "refactor: fix critical and high issues from health check"
2. 推送到远程：git push
3. 更新项目文档（如有需要）
4. 安排时间处理遗留的 Medium 问题
```

---

## 🎯 核心特性

### 1. 两阶段工作流

**诊断阶段**（只读，安全）：
- 全面检查项目健康状况
- 不修改任何代码
- 生成详细的问题报告

**治疗阶段**（修改代码）：
- 基于诊断结果自动修复
- 每个修复都有验证
- 失败可回滚

**优势**：
- 避免 AI 过度干预（先看病再开药）
- 保持掌控感（用户决定修复什么）
- 降低风险（诊断零风险，修复可回滚）

### 2. 完全自动化

- 使用 `batchcc.py` 批量执行任务
- 无需多次运行命令
- 无需新建多个会话
- 一次运行完成所有检查或修复

### 3. 模块化文件引用

- 主任务文件精简（使用 `@文件引用` 语法）
- 详细任务独立文件
- 便于维护和调试
- 避免单个文件过大

### 4. 智能任务编排

- **并行执行**：同类检查（测试、代码质量）
- **串行执行**：需要全局视角的检查（架构、总结）
- **依赖管理**：修复任务按优先级和依赖关系编排
- **冲突检测**：避免并发修改同一文件

### 5. 自动生成修复任务

- 在诊断阶段自动生成修复任务
- 基于问题类型智能分组
- 自动判断串行/并行策略
- 每个任务都有验证机制

---

## 📋 检查维度

### 阶段1: 测试健康检查

**检查内容**：
- E2E 测试是否通过？
- 单元测试是否通过？
- 测试覆盖率如何？
- 是否有过时的测试？
- 是否缺少关键场景的测试？

**输出**：
- 每个模块的测试健康度报告
- 失败测试的详细信息
- 缺失测试的建议

### 阶段2: 代码质量检查

**检查内容**：
- 函数是否过长？（>60行）
- 文件是否过大？（>600行）
- 嵌套层次是否过深？（>4层）
- 类型注解是否完整？
- 是否有足够的注释？

**输出**：
- 每个模块的代码质量评分
- 需要重构的代码位置
- 改进建议

### 阶段3: 架构一致性检查

**检查内容**：
- 是否遵循分层架构？
- 是否有跨层调用？
- 是否有循环依赖？
- 错误处理是否一致？

**输出**：
- 架构违规点列表
- 循环依赖链
- 修复建议

### 阶段4: 文档一致性检查

**检查内容**：
- FEATURE_CODE_MAP.md 是否准确？
- docs/testing/COVERAGE_MAP.md 是否过时？
- 是否有遗漏的功能未记录？

**输出**：
- 文档过时条目列表
- 遗漏功能清单
- 更新建议

### 阶段5: 生成总结和修复任务

**做什么**：
- 汇总所有检查结果
- 按优先级排序问题
- 生成 SUMMARY.md
- **自动生成 task-refactor**
- **自动生成 .refactor-tasks/*.md**

**输出**：
- 总结报告（SUMMARY.md）
- 修复主任务文件（task-refactor）
- 各类修复任务文件（.refactor-tasks/*.md）

---

## 🔧 修复任务类型

### 1. 修复测试失败（Critical）

**做什么**：
- 分析失败原因（代码 bug vs 测试过时）
- 修复代码或更新测试
- 验证测试通过

**策略**：
- 串行执行（避免冲突）
- 优先信任测试意图

### 2. 修复架构问题（Critical）

**做什么**：
- 解决循环依赖（引入接口、事件驱动）
- 修复跨层调用（补充 Service 层）
- 验证测试通过

**策略**：
- 串行执行（架构变更影响大）
- 保持原有功能不变

### 3. 补充缺失测试（High）

**做什么**：
- 识别缺失的测试场景
- 编写 E2E 或集成测试
- 遵循测试规范

**策略**：
- 并行执行（不同模块独立）
- 添加指导性的错误消息

### 4. 更新过时文档（High）

**做什么**：
- 更新 FEATURE_CODE_MAP.md
- 更新 docs/testing/COVERAGE_MAP.md
- 添加遗漏的功能记录

**策略**：
- 并行执行（文档修改不冲突）
- 验证路径准确性

### 5. 优化代码质量（Medium）

**做什么**：
- 重构过长函数
- 补充类型注解
- 添加必要注释

**策略**：
- 并行执行（不同模块独立）
- 保持原有行为不变
- 失败3次立即回滚

---

## ⚠️ 注意事项

### 执行前

1. **提交当前代码**：
   ```bash
   git commit -am "Before health check"
   ```

2. **确保测试环境就绪**：
   - 依赖已安装
   - 数据库已初始化
   - 环境变量已配置

### 执行中

1. **监控输出**：
   - batchcc.py 会实时输出进度
   - 注意 ❌ 失败标记
   - 查看详细日志（如果有）

2. **失败处理**：
   - 诊断阶段失败：检查环境，重新运行
   - 修复阶段失败：立即回滚，分析原因

### 执行后

1. **审查结果**：
   - 查看 SUMMARY.md 了解问题全貌
   - 查看 REFACTOR_RESULT.md 了解修复情况

2. **提交代码**（如果修复成功）：
   ```bash
   git add .
   git commit -m "refactor: fix critical and high issues from health check"
   ```

3. **回滚**（如果修复失败）：
   ```bash
   git reset --hard HEAD
   ```

---

## 🎓 最佳实践

### 1. 定期运行健康检查

- **建议频率**：每月一次
- **最佳时机**：
  - 项目里程碑完成后
  - 接手项目时
  - 重大重构前

### 2. 分批修复问题

- **第一批**：修复 Critical 问题（阻塞开发）
- **第二批**：修复 High 问题（影响稳定性）
- **第三批**：选择性修复 Medium 问题（提升质量）

### 3. 保持文档同步

- 修复后及时更新：
  - FEATURE_CODE_MAP.md
  - docs/testing/COVERAGE_MAP.md
  - PROJECT_STATUS.md

### 4. 持续改进

- 根据检查结果调整开发规范
- 补充缺失的测试场景
- 优化架构设计

---

## 🆚 与其他命令的对比

### vs `/health-check`（快速健康检查）

| 特性 | comprehensive-health-check | health-check |
|------|----------------------------|--------------|
| 检查深度 | 深度审查（实际运行测试，逐文件审查） | 快速扫描（只看文件结构） |
| 执行方式 | 两阶段工作流，完全自动化 | 单次运行，快速完成 |
| Token 消耗 | 高（15k-20k） | 低（5k-8k） |
| 适用场景 | 定期体检、接手项目、重大重构前 | 日常快速检查 |
| 修复能力 | 自动生成修复任务，可批量修复 | 只提供建议，不修复 |

### vs `/refactor-project`（重构前检查）

| 特性 | comprehensive-health-check | refactor-project |
|------|----------------------------|------------------|
| 目的 | 全面诊断 + 修复 | 重构前评估风险 |
| 输出 | 问题报告 + 修复任务 | 风险评估 + 重构建议 |
| 适用场景 | 定期体检 | 重构前专项评估 |

---

## 📚 相关文档

- **主命令文件**：`.claude/commands/comprehensive-health-check.md`
- **健康检查模板**：`.claude/commands/templates/workflow/HEALTH_CHECK_TASK_TEMPLATE.md`
- **修复任务模板**：`.claude/commands/templates/workflow/REFACTOR_TASK_TEMPLATE.md`
- **DAG 任务格式**：`.claude/commands/templates/workflow/DAG_TASK_FORMAT.md`

---

## 🐛 故障排查

### 问题1: 生成任务文件时报错

**可能原因**：
- 项目关键文档缺失（FEATURE_CODE_MAP.md 等）

**解决方案**：
- 检查项目根目录是否有关键文档
- 如果没有，AI 会基于目录结构识别模块

### 问题2: batchcc.py 执行失败

**可能原因**：
- batchcc.py 不存在或版本过旧
- Python 环境问题

**解决方案**：
- 确保 batchcc.py 已更新到最新版本
- 检查 Python 版本（需要 3.8+）

### 问题3: 检查任务失败

**可能原因**：
- 测试环境未就绪
- 依赖缺失

**解决方案**：
- 检查环境变量
- 运行 `npm install` 或 `pip install -r requirements.txt`
- 确保数据库已初始化

### 问题4: 修复任务失败

**可能原因**：
- AI 生成的修复代码有问题
- 测试本身有问题

**解决方案**：
- 立即回滚：`git reset --hard HEAD`
- 查看详细日志分析原因
- 手动修复或跳过该任务

---

**最后更新**：2025-11-12
**维护者**：Claude Code AI
