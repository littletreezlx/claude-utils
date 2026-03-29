---
name: staff.csv 只增不删
description: school 项目的 staff.csv 人员名单不应因为某月无记录就移除人员
type: feedback
---

staff.csv 是人员花名册，不是月度考勤表。某月"无记录"可能是请假、未参与课后服务等正常情况，不代表人员离职。

**Why:** 误删人员后，下个月该人有数据时会变成"未知人员"，需要重新排查添加，反而制造问题。
**How to apply:** 只在用户明确确认人员离职时才从 staff.csv 中移除。遇到"无记录"人员时正常保留，不建议删除。
