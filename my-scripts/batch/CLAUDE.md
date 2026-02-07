# CLAUDE.md - Batch Executor 项目指南

> 本文档指导 Claude Code 如何维护和开发 DAG 批量执行工具

## 项目定位

**批量任务执行引擎**，支持串行/并行混合执行、文件冲突检测、自动断点续传。

**核心价值**：
- 让大型重构任务可以自动化执行（节省时间）
- 支持任务中断后自动继续（不浪费已完成的工作）
- 智能调度并行任务（提高执行效率）

## 项目结构

```
batch/
├── batchcc.py              # 主入口（Claude Code 批量执行器）
├── batchcx.py              # X 平台批量执行器（不同命令格式）
├── dag_parser.py           # DAG 格式解析器
├── dag_executor.py         # DAG 执行引擎
├── state_manager.py        # 状态管理（断点续传）
├── batch_executor_base.py  # 基础执行器（复用）
├── CLAUDE.md               # 本文档
└── test-state.md           # 测试用例
```

## 核心模块职责

### 1. batchcc.py（主入口）
**职责**：
- 解析命令行参数
- 检测任务文件格式（DAG 或简单格式）
- 调用对应的执行器
- 处理 --restart 参数

**关键点**：
- 自动检测 `## STAGE ##` 标记来判断是否 DAG 格式
- 默认开启状态管理（use_state=True）
- 只保留必要参数（--dry-run, --restart）

### 2. dag_parser.py（解析器）
**职责**：
- 解析 DAG 任务文件（STAGE 和 TASK）
- 支持文件引用（@文件路径）
- 提取文件范围和排除规则
- 文件冲突检测

**关键类**：
- `DAGParser` - 解析任务文件
- `StageNode` - 阶段节点
- `TaskNode` - 任务节点
- `ConflictDetector` - 冲突检测器

**文件引用**：
- 使用当前工作目录作为基准（不是文件所在目录）
- 支持嵌套引用

### 3. dag_executor.py（执行引擎）
**职责**：
- 顺序执行 STAGE
- STAGE 内根据 mode（serial/parallel）执行任务
- 集成状态管理（自动续传）
- 冲突检测和批次调度

**执行流程**：
```
1. 加载状态（如果存在）
2. 检测到未完成任务 → 自动从断点继续
3. 顺序执行每个 STAGE
4. STAGE 内：
   - serial mode → 任务顺序执行
   - parallel mode → 检测冲突 → 分批并行
5. 每个任务完成后立即保存状态
```

**关键点**：
- 不询问用户，自动处理断点续传
- 跳过已完成的任务
- 失败立即停止

### 4. state_manager.py（状态管理）
**职责**：
- 加载/保存状态文件（JSON）
- 记录每个 STAGE 和 TASK 的状态
- 记录开始时间、结束时间、耗时
- 记录失败原因

**状态值**：
- `pending` - 未开始
- `in_progress` - 进行中
- `completed` - 已完成
- `failed` - 失败

**文件位置**：`<任务文件>.state.json`

### 5. batch_executor_base.py（基础执行器）
**职责**：
- 提供通用的命令提取逻辑
- 提供串行/并行执行方法
- 提供结果打印方法

**复用性**：batchcc.py 和 batchcx.py 都继承这个基类

## DAG 任务格式

> **权威规范**：`~/.claude/commands/templates/workflow/DAG_TASK_FORMAT.md`
>
> 本文件不重复格式定义，修改格式请更新上述文件。

## 开发规范

### 1. 添加新功能
**步骤**：
1. 在对应模块添加功能
2. 更新类型注解
3. 添加测试用例
4. 更新 DAG_TASK_FORMAT.md（如果涉及格式变化）

**禁止**：
- 不要添加过度设计的参数（如 --from-stage, --no-state）
- 不要添加用户选择（保持自动化）
- 不要破坏向后兼容性

### 2. 修改核心逻辑
**影响范围检查**：
```
dag_parser.py 修改 → 影响：dag_executor.py
dag_executor.py 修改 → 影响：batchcc.py
state_manager.py 修改 → 影响：dag_executor.py
```

**必须验证**：
- 运行测试用例（test-state.md）
- 确保状态文件格式兼容
- 确保向后兼容

### 3. 文档更新
**单一信息源**：
- DAG 格式规范 → `~/.claude/commands/templates/workflow/DAG_TASK_FORMAT.md`
- 引擎维护指南 → 本文档（CLAUDE.md）
- 不要在多处重复定义同一信息

## 测试策略

### 单元测试
暂无自动化测试，依赖手动测试：

```bash
# 测试状态管理
python batchcc.py test-state.md

# 测试断点续传
python batchcc.py test-state.md
# 中断后再次执行
python batchcc.py test-state.md

# 测试重新开始
python batchcc.py test-state.md --restart
```

### 集成测试
使用真实项目的任务文件测试：

```bash
# 测试大型重构任务
cd /path/to/nas-server
python batchcc.py task-refactor --dry-run
```

## 常见问题

### Q1: 为什么不添加 --from-stage 参数？
**A**: 过度设计。状态管理会自动检测未完成的阶段，不需要手动指定。

### Q2: 为什么不询问用户是否继续？
**A**: 自动化优先。检测到未完成任务，自动继续，不打断用户。

### Q3: 为什么状态文件用 JSON 而非数据库？
**A**:
- 简单直观，用户可以直接查看
- 不需要额外依赖
- 文件级别的状态足够用

### Q4: 并行任务如何检测冲突？
**A**:
- 检查 `文件:` 字段的 glob 模式
- 相同目录或文件 → 冲突
- 使用 `排除:` 字段可以避免误判

### Q5: 任务失败后如何修复？
**A**:
1. 查看状态文件找到失败原因
2. 修复问题
3. 再次执行（自动从失败任务继续）

## 设计理念

### 极简主义
**只保留必要功能**：
- ✅ 自动断点续传
- ✅ 串行/并行混合执行
- ✅ 文件冲突检测
- ❌ 复杂的依赖关系（用 STAGE 顺序表达）
- ❌ 失败策略配置（统一：失败即停止）
- ❌ 重试机制（失败就失败，重新跑）

### 自动化优先
**减少用户干预**：
- 自动检测格式
- 自动检测状态
- 自动继续执行
- 自动保存状态

### 务实原则
**够用即可**：
- AI 执行任务快，重新跑的成本不高
- 状态管理解决 90% 的场景
- 简单的设计更容易维护

## 维护检查清单

### 添加功能前
- [ ] 确认功能是否必要（避免过度设计）
- [ ] 检查是否可以复用现有代码
- [ ] 评估对现有功能的影响

### 开发过程中
- [ ] 保持代码简洁（函数 < 60 行）
- [ ] 添加必要的类型注解
- [ ] 添加清晰的注释（说明 why，不是 what）
- [ ] 使用语义化命名

### 完成后
- [ ] 手动测试核心功能
- [ ] 更新相关文档
- [ ] 检查向后兼容性
- [ ] 更新本文档（如有架构变化）

## 相关文档

- `~/.claude/commands/templates/workflow/DAG_TASK_FORMAT.md` - DAG 格式权威规范
- `~/.claude/commands/todo-huge-task.md` - DAG 任务生成命令
