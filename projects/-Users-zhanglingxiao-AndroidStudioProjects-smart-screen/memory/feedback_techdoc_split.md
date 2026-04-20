---
name: techdoc-split-preferences
description: User prefers lean tech docs - design overview without code/overengineering, implementation guide code-first, focus on core metrics only
type: feedback
---

技术文档拆分为设计综述 + 实施手册时，用户偏好：

1. **设计综述不要代码、类名、文件路径** -- 面向产品/管理层
2. **不要过度设计** -- 先做最核心的指标，不要一次铺太多
3. **不要工作量估算** -- 用户会自行评估
4. **不要看板+告警等后续阶段** -- 设计文档只写当前要做的
5. **实施手册不上传飞书** -- 仅本地使用，飞书只放设计综述

**Why:** 用户反馈原始方案指标太多太复杂，认为播放质量采集本质就是几个基础指标（丢帧/首帧/成功率），不需要过度包装。

**How to apply:** `/techdoc` 生成文档时，先确认核心范围再展开，宁可精简后续扩展也不要一开始铺满。
