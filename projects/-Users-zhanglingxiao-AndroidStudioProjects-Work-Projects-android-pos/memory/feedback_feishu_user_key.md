---
name: feishu-user-key-gotcha
description: Feishu docs open_id is NOT the same as Feishu project user_key - must extract user_key from existing work item node details
type: feedback
---

飞书文档系统的 `open_id`（如 `ou_xxx`）与飞书项目系统的 `user_key`（如 `7310303312383852547`）是**不同的标识符**，不能互用。

**Why:** `mcp__feishu-docs__get-user` 返回的 open_id 传入 `mcp__feishu__update_field` 的 role_operate 会报 "Can not find user info" 错误。`mcp__feishu__search_user_info` 也搜不到用户。

**How to apply:** 获取 user_key 的可靠方法是从已有工作项的节点详情中提取：
1. 用 `get_node_detail` 查询用户参与过的已有工作项
2. 从返回的 JSON 中 regex 提取 `user_key` 字段
3. 通过上下文中的 name/email 确认对应关系

已知的 user_key 已记录在 `reference_feishu_project.md` 中，优先查表避免重复提取。
