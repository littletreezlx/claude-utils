# NAS Server 项目记忆

## 工作流与规范
- [CLAUDE.md 拆分决策](feedback_claudemd_split.md) — 1+3 拆分：根(纯总览)+src/(前端)+pythonapi+nodejs-service
- [flywheel-workflow](feedback_flywheel_workflow.md) — 维护飞轮闭环：brief → check → debrief
- [DAG 任务格式](project_dag_format.md) — batchcc.py 的 STAGE/TASK 声明格式
- [禁用 git hooks](feedback_no_pre_commit_check.md) — 不要安装 pre-commit/post-commit hooks
- [文档元数据 sed bug](feedback_doc_metadata_hook.md) — sed 日期正则必须匹配 YYYY-MM-DD 全格式
- [记忆纪律](feedback_memory_discipline.md) — 禁止存可从代码/文档推导的信息（架构、文件路径等）
- [禁止远程热修改](feedback_no_remote_hotfix.md) — 不要 docker cp/sed 改容器产物，走正常部署

## 外部服务与参考
- [Gotify 通知中心](reference_gotify.md) — 自建 Gotify 推送通知，NAS Server 关键告警
- [日志系统设计原则](reference_logging_design_principles.md) — 多服务统一 schema、AI 排查入口、降噪策略

## 用户画像
- [投资者画像](user_investor_profile.md) — A股/港股散户，哑铃型配置，核心痛点是情绪化操作和信息盲区

## 项目状态与风险
- [Follow 跨服务同步风险](project_follow_sync_risks.md) — 5 个已知的三端数据模型不一致风险点
- [Follow 系统定位边界](project_follow_scope.md) — Follow 只处理难订阅平台，通用 RSS/博客走 Miniflux
