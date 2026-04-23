# 飞书 MQL 速查（个人季度述职专用）

## 前置准备

```bash
# 1. 确认空间
mcp__feishu__search_project_info(project_key="shipd")           # 食亨IPD
mcp__feishu__search_project_info(project_key="shihengconsole")  # 食亨数字化（工单在这）

# 2. 拿当前用户的 user_key
mcp__feishu__search_user_info(project_key="shipd", user_keys=["current_login_user()"])
# → user_key 用于 MQL 中的 '<id:xxx>' 匹配

# 3. 拿飞书文档的 ou_ open_id（与上面 user_key 不同！）
mcp__feishu-docs__get_user()
# → open_id 形如 ou_xxx，用于 search-doc 的 owners 字段
```

## 字段名注意

- **必须用字段 key 而非中文名**（key 用反引号包裹）
- 常用 key：`name` / `work_item_status` / `start_time` / `priority` / `business` / `tags` / `work_item_id`
- 不同工作项类型字段不同时，用 `mcp__feishu__list_workitem_field_config` 查
- "all_participate_persons()" 不一定能拉到所有相关——复盘类用 `field_cc0657`（负责人）等具体角色字段

## 模板 1：拉本季需求（story）

```sql
SELECT `name`, `work_item_status`, `start_time`, `priority`, `business`, `tags`, `field_e4ca95`, `work_item_id`
FROM `shipd`.`产研需求`
WHERE `start_time` between '<季初>' and '<季末>'
  AND array_contains(all_participate_persons(), current_login_user())
ORDER BY `start_time` DESC
```

## 模板 2：拉本季缺陷（bug）

```sql
SELECT `name`, `work_item_status`, `start_time`, `priority`, `business`, `work_item_id`
FROM `shipd`.`缺陷`
WHERE `start_time` between '<季初>' and '<季末>'
  AND array_contains(all_participate_persons(), current_login_user())
ORDER BY `start_time` DESC
```

## 模板 3：拉本季复盘（case_study）

```sql
SELECT `name`, `start_time`, `work_item_id`, `field_cc0657`, `field_c2951e`
FROM `shipd`.`复盘`
WHERE `start_time` between '<季初>' and '<季末>'
  AND (array_contains(`field_cc0657`, current_login_user())
    OR array_contains(`field_c2951e`, current_login_user()))
ORDER BY `start_time` DESC
```

## 模板 4：拉本季运维工单（work_order_system，在 shihengconsole 空间）

```sql
SELECT `name`, `start_time`, `work_item_id`
FROM `shihengconsole`.`工单`
WHERE `start_time` between '<季初>' and '<季末>'
  AND array_contains(all_participate_persons(), current_login_user())
ORDER BY `start_time` DESC
```

## 模板 5：拉本季创建的飞书文档

```python
mcp__feishu-docs__search-doc(
    query="",
    filters={
        "owners": ["<ou_xxx>"],          # 必须 ou_ 开头，不是 on_/user_key
        "create_time": "[<季初>, <季末>]",  # 跨度 ≤ 3 个月（硬规则）
        "sort_rule": "CREATE_TIME"
    },
    page={"size": 20, "offset": 0}
)
# has_more=true 时用 page_token 翻页，最多通常 2-3 页
```

## 保存约定

每类工作项保存为独立 md 文件，便于后续做素材综合汇总：

```
<本季>/飞书拉取/
├── 00-素材综合汇总.md      # 三因子分析 + 大纲推荐（最后写）
├── 01-需求story.md
├── 02-缺陷bug.md
├── 03-复盘casestudy.md
├── 04-工单workorder.md
└── 05-技术文档.md
```

每份 md 的内容结构：
1. 拉取条件（MQL 原文 / 时间窗 / 总数）
2. 主题分类（按"性能 / 业务主线 / 客户专项 / 其他"等聚类）
3. 关键观察（事实陈述，不做叙事判断）
4. 述职可用方向（暂存，不入定稿）

## 常见错误

| 错误 | 原因 | 修正 |
|---|---|---|
| `attr label not found` | SELECT 用了中文字段名 | 用字段 key 并反引号包裹 |
| 复盘 0 项但实际有 | 用 `all_participate_persons()` 但开发非默认参与人 | 改用 `field_cc0657`（负责人）/ `field_c2951e`（CR 负责人） |
| 工单 0 项 | 工单不在 `shipd` 空间 | 切到 `shihengconsole` 空间 |
| search-doc owner 失效 | 传了 user_key 或 on_xxx | 必须用 get-user 拿到的 ou_xxx |
| 字段值匹配失败 | 用了 label 没用 id | 写 `<id:option_xxx>` 或 `<id:7310...>` |
