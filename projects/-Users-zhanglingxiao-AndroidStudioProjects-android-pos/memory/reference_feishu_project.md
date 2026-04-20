---
name: feishu-project-shipd
description: Feishu project space info for 食亨IPD - project key, user keys, template IDs, role keys, common field values for creating work items (shared across POS/TV/KDS)
type: reference
originSessionId: 7a9c4acb-439a-4283-b3b9-23ffc7779279
---
## 飞书项目空间：食亨IPD

- **project_key**: `shipd` (full: `6573e752a04ba3400dbcec89`)
- **work_item_type**: `story` (产研需求)

### 常用模板 ID

| 模板名称 | option_id |
|---------|-----------|
| 技术需求 | `574498` |
| 产品需求 | `892574` |
| BugFix | `598884` |
| 运维开发 | `1841719` |

### 团队 user_key

| 姓名 | user_key | 邮箱 | 团队 |
|------|----------|------|------|
| 张凌霄 | `7310303312383852547` | lingxiao.zhang@shihengtech.com | 智慧门店-Android |
| 王雷03 | `7310185777596465156` | lei.wang03@shihengtech.com | 智慧门店-测试 |

**How to apply:** `search_user_info` 经常搜不到人，优先查此表。需要新用户时从 `list_team_members` + `search_user_info(user_keys=[...])` 批量查。

### 常用角色 key

| 角色名 | role_key |
|--------|----------|
| PO | `PM` |
| 技术评审负责人 | `tech_owner` |
| Android开发 | `Android` |
| 测试 | `QA` |
| 前端开发 | `ferd` |
| 后端开发 | `berd` |

### 常用必填字段

| 字段 | field_key | 类型 | 说明 |
|------|-----------|------|------|
| 需求名称 | `field_name` | text | 格式: 【项目名】功能描述 |
| 流程模版 | `template` | select | 见上方模板表 |
| 优先级 | `priority` | select | P0=`0`, P1=`1`, P2=`2`, P3=`r7hy4v5d3` |
| 业务线 | `business` | tree-select | 见下方业务线表 |
| 描述 | `description` | multi-text | markdown 格式 |
| 需求类型 | `field_97ef0c` | select | 技术需求=`tbs7xiczf`, 产品需求=`mfbdomq1h`, BugFix=`ws669y056` |
| 是否存在工单 | `field_24180c` | select | 无工单=`qlpqg04_a`, 有工单=`eyo6lmwnp` |
| 技术文档(链接) | `field_1` | link | 飞书文档 URL |
| 技术文档(富文本) | `field_179a9d` | multi-text | markdown，可放链接 |

### 各项目业务线 option_id

| 项目 | 业务线路径 | option_id |
|------|-----------|-----------|
| POS 收银 | 智慧门店 / 收银POS&APP | `675ba962962ffaffa73cdcee` |
| 智慧屏 TV | 智慧门店 / 增值业务 / 智慧屏(广告、叫号、菜单屏) | `675ba96b710814f251b11a67` |
| KDS 厨显 | 智慧门店 / 增值业务 / KDS厨显 | `675ba92141a2b5c54eb18826` |

### 默认角色指派（安卓技术需求）

- PO + Android开发 + 前端开发 + 测试 + 技术评审负责人 → 张凌霄 (`7310303312383852547`)
- **前端开发（ferd）必填**：不填的话开发节点无负责人，流程卡住；即使是纯 Android 需求也要挂自己
- 王雷03 (`7310185777596465156`) **不再默认**当 QA；需要时再手动指派

### 创建工作项完整流程

1. `create_workitem` 传 `template` + `field_name`
2. `update_field` 传 `priority` + `field_97ef0c` + `field_24180c` + `business` + `description`
3. `update_field` 的 `role_operate` 添加角色成员
4. `update_field` 传 `field_1` 或 `field_179a9d` 写技术文档链接
