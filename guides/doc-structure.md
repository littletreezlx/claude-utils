# 项目文档标准结构

本文件定义项目 docs/ 目录的标准文件体系。全局 CLAUDE.md 通过 `@` 引用本文件，避免每次会话都加载完整表格。

> **受众**：文档体系的首要读者是 AI（跨会话上下文传递），次要读者是产品负责人（做产品决策时偶尔阅读）。格式优先满足 AI 高效消费和人类偶尔阅读。
>
> **协作模式**：AI-Only 开发。所有文档由 AI 生成和维护，人类是产品负责人。工作流中不存在「人工审核代码」「人工走查」等环节。

## 根目录入口文件

- `README.md` — 人类入口
- `CLAUDE.md` — AI 入口
- `TODO.md` — 已决策行动队列（`/todo-doit` 消费）
- `to-discuss.md` — AI 待决策事项队列（产品负责人决策 或 `/think` / `/feat-discuss-local-gemini` 代理消费）

## 三文件协作架构（行动/决策/材料 分离）

| 文件 | 内容性质 | 谁来消费 |
|------|---------|---------|
| `TODO.md` | 已决策、可执行任务 | AI（`/todo-doit` 自动执行）|
| `to-discuss.md` | 未决策、需产品负责人决策的 AI 建议 | 产品负责人（或触发 `/think` / `/feat-discuss-local-gemini`）|
| `_scratch/*.md` | 原始材料、探索报告、调试日志 | AI 查阅上下文用 |

**铁律**：
- 事实型 bug → `TODO.md`；观点/产品/设计判断 → `to-discuss.md`；原始材料 → `_scratch/`
- **严禁把 AI 的观点伪装成已决策任务塞进 TODO.md**（会污染 `/todo-doit` 的执行流）
- TODO.md 与 to-discuss.md **物理独立，不设指针**（否则互相污染、变成视觉盲点）
- `to-discuss.md` 不是 backlog 而是 **Force-Decision Queue**：每条要么转 TODO，要么被 Reject，不得无限积压

### to-discuss.md 条目模板

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/xxx.md § 章节)
- **事实前提**: [基于什么客观现象，禁止加主观修饰]
- **AI 观点**: [我认为应该...]
- **反面检验**: [这个建议可能错在哪 / 维持现状的理由]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Discuss → /think 或 /feat-discuss-local-gemini
  - [ ] Reject → 直接删
```

**禁止给 AI 观点加置信度字段** —— AI 在胡说时极度自信，置信度是噪音。

## docs/ 标准文件

| 文件 | 回答的问题 | 更新频率 | 内容 |
|------|----------|---------|------|
| `docs/PRODUCT_SOUL.md` | **为谁**做、**为什么**存在 | 极少变 | 产品愿景、用户画像、设计隐喻、情感目标 |
| `docs/PRODUCT_BEHAVIOR.md` | 系统**怎么运转** | 中频 | 状态机、导航规则、交互模式、全局状态策略 |
| `docs/user-stories/*.md` | 用户**会做什么** | 中频 | 用户视角操作序列 + 可执行验证步骤（`/ai-qa-stories` 消费） |
| `docs/user-stories/qa/*.qa.md` | 怎么**自动验证** | 中频 | 结构化验证脚本（编译自 story，AI 专属） |
| `docs/features/*.md` | 功能**怎么设计** | 中频 | 功能架构、API 契约、交互细节、实现决策 |
| `docs/ARCHITECTURE.md` | 系统**怎么搭建** | 中频 | 技术架构、数据流、关键技术决策、目录结构 |
| `docs/ROADMAP.md` | 项目**去向哪** | 高频 | 当前阶段状态、Known Issues、Next Steps |
| `docs/FEATURE_CODE_MAP.md` | 代码**在哪里** | 中频 | 功能→代码路径索引（GPS 导航） |
| `docs/ui/UI_SHOWCASE.md` | 界面**长什么样** | 低频 | 设计系统工程参考手册 |

## 文档边界（易混淆的三者）

- **BEHAVIOR** = 系统规则（"状态 A 在条件 X 下转移到 B"）
- **user-stories** = 用户叙事（"小明不知道吃什么→打开 App→摇→火锅"），qa/ 子目录存放编译的验证脚本
- **features/** = 工程设计（"随机选择用 Fisher-Yates 算法"）

> User Stories 格式模板：`docs/USER_STORIES_TEMPLATE.md`

## 模块质量标签

在 ROADMAP.md 或架构文档中给各模块标注状态：

- 🟢 稳定（可大刀阔斧）
- 🟡 缺测试（需小心）
- 🔴 债务高（谨慎操作）

## 文档保鲜原则

- FEATURE_CODE_MAP.md 中引用的代码路径必须实际存在，失效路径视为文档腐烂
- 代码文件新增/删除/重命名后，检查文档索引是否需要同步
- user-stories/qa/ 中的 curl 命令返回 404 或断言失败 → 故事过时，需从 story 重新编译 qa
