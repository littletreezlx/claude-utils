---
name: feishu-project-shipd
description: Feishu project space info for 食亨IPD - project key, user keys, template IDs, role keys, common field values for creating work items
type: reference
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

| 姓名 | user_key | 邮箱 |
|------|----------|------|
| 张凌霄 | `7310303312383852547` | lingxiao.zhang@shihengtech.com |
| 王雷03 | `7310185777596465156` | lei.wang03@shihengtech.com |

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

| 字段 | field_key | 类型 | 常用值 |
|------|-----------|------|--------|
| 需求名称 | `name` | text | - |
| 流程模版 | `template` | select | 见上方模板表 |
| 优先级 | `priority` | select | P0=`0`, P1=`1`, P2=`2` |
| 业务线 | `business` | tree-select | 收银POS&APP=`675ba962962ffaffa73cdcee` |
| 描述 | `description` | multi-text | markdown |
| 需求类型 | `field_97ef0c` | select | 技术需求=`tbs7xiczf`, 产品需求=`mfbdomq1h` |
| 是否存在工单 | `field_24180c` | select | 无工单=`qlpqg04_a` |
| 技术文档链接 | `field_1` | link | URL |

### 默认角色指派（安卓 POS 技术需求）

- PO + 技术评审负责人 + Android开发 → 张凌霄
- 测试 → 王雷03
