# 项目文档标准结构

本文件定义项目 docs/ 目录的标准文件体系。全局 CLAUDE.md 通过 `@` 引用本文件，避免每次会话都加载完整表格。

## 根目录入口文件

- `README.md` — 人类入口
- `CLAUDE.md` — AI 入口
- `TODO.md` — 临时工作文件

## docs/ 标准文件

| 文件 | 回答的问题 | 更新频率 | 内容 |
|------|----------|---------|------|
| `docs/PRODUCT_SOUL.md` | **为谁**做、**为什么**存在 | 极少变 | 产品愿景、用户画像、设计隐喻、情感目标 |
| `docs/PRODUCT_BEHAVIOR.md` | 系统**怎么运转** | 中频 | 状态机、导航规则、交互模式、全局状态策略 |
| `docs/user-stories/*.md` | 用户**会做什么** | 中频 | 用户视角操作序列 + 可执行验证步骤（`/ai-qa-stories` 消费） |
| `docs/features/*.md` | 功能**怎么设计** | 中频 | 功能架构、API 契约、交互细节、实现决策 |
| `docs/ARCHITECTURE.md` | 系统**怎么搭建** | 中频 | 技术架构、数据流、关键技术决策、目录结构 |
| `docs/ROADMAP.md` | 项目**去向哪** | 高频 | 当前阶段状态、Known Issues、Next Steps |
| `docs/FEATURE_CODE_MAP.md` | 代码**在哪里** | 中频 | 功能→代码路径索引（GPS 导航） |
| `docs/ui/UI_SHOWCASE.md` | 界面**长什么样** | 低频 | 设计系统工程参考手册 |

## 文档边界（易混淆的三者）

- **BEHAVIOR** = 系统规则（"状态 A 在条件 X 下转移到 B"）
- **user-stories** = 用户叙事（"小明不知道吃什么→打开 App→摇→火锅"）+ 可执行 curl 验证
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
- user-stories 中的 curl 命令返回 404 或断言失败 → 故事过时，需更新
