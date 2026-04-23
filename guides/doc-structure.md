# 项目文档标准结构

本文件定义项目 docs/ 目录的标准文件体系。全局 CLAUDE.md 通过 `@` 引用本文件，避免每次会话都加载完整表格。

> **受众**：文档体系的首要读者是 AI（跨会话上下文传递），次要读者是产品负责人（做产品决策时偶尔阅读）。格式优先满足 AI 高效消费和人类偶尔阅读。
>
> **协作模式**：AI-Only 开发。所有文档由 AI 生成和维护，人类是产品负责人。工作流中不存在「人工审核代码」「人工走查」等环节。

## 根目录入口文件

- `README.md` — 人类入口
- `CLAUDE.md` — AI 入口
- `TODO.md` — 已决策行动队列（`/todo-doit` 消费）
- `to-discuss.md` — `/think` 也无法决策的事项队列（产品负责人最终裁决）

## 三文件协作架构（行动/决策/材料 分离）

| 文件 | 内容性质 | 谁来消费 |
|------|---------|---------|
| `TODO.md` | 已决策、可执行任务 | AI（`/todo-doit` 自动执行）|
| `to-discuss.md` | `/think` 也无法决策的事项 | 产品负责人最终裁决 |
| `_scratch/*.md` | 原始材料、探索报告、调试日志 | AI 查阅上下文用 |

**铁律**：
- 事实型 bug → `TODO.md`；观点/产品/设计判断 → **先借助 `/think` 获取外部视角，Claude Code 自己综合判断做最终决策**，能拍板则转 TODO 或丢弃，自己也拿不准才进 `to-discuss.md`；原始材料 → `_scratch/`
- **严禁把 AI 的观点伪装成已决策任务塞进 TODO.md**（会污染 `/todo-doit` 的执行流）
- **严禁跳过 `/think` 直接把观点丢进 `to-discuss.md`**（`/think` 引入独立视角后，Claude Code 能处理绝大部分产品+技术决策）
- TODO.md 与 to-discuss.md **物理独立，不设指针**（否则互相污染、变成视觉盲点）
- `to-discuss.md` 不是 backlog 而是 **Last-Resort Queue**：只放 `/think` 明确表示无法决策的事项。每条要么转 TODO，要么被驳回，不得无限积压
- **交互模式下绕过 to-discuss.md**：`/think` 在主动对话中触发时，升级决策直接在对话里展示模板让用户当场勾选（见 `skills/think/SKILL.md` § 3.3.2）。只有自主模式（`/loop`、cron、batch）或用户当场无法定夺时才落库到 `to-discuss.md`

### to-discuss.md 条目模板

> **前置条件**：写入 to-discuss.md 前必须已调用 `/think`，且 `/think` 明确表示无法决策。

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/xxx.md § 章节)
- **事实前提**: [基于什么客观现象，禁止加主观修饰]
- **/think 结论**: [/think 给出了什么判断，为什么它认为自己无法拍板]
- **决策选项**:
  - [ ] 采纳 → 转 TODO.md
  - [ ] 驳回 → 直接删
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
| `docs/design/DESIGN_BRIEF.md` | 设计工具**该怎么发挥** | 低频（派生） | 喂给 AI 设计工具（frontend-design / v0 / Lovable）的视觉意图简报，派生自 PRODUCT_SOUL + UI 文档，通过 `/init-design-brief` 生成 |

### 派生文档约定

`docs/design/DESIGN_BRIEF.md` 是**派生产物**，不是源文档：

- 源：`PRODUCT_SOUL.md` + `docs/ui/UI_SHOWCASE.md`（或等价 UI 文档）
- 生成：`/init-design-brief` 命令重新编译
- 文件头必须带 `> 派生自 PRODUCT_SOUL + UI_SHOWCASE，过时请跑 /init-design-brief 重新生成`
- **清理规则**：`/doc-clean`、`inbox` skill 等**不得**将该文件当作临时产物清理
- **过时判定**：PRODUCT_SOUL 或 UI_SHOWCASE 修改晚于该文件 mtime → 标记过时、重跑

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
