---
name: feedback_feishu_mcp_workitem
description: 飞书 workitem 创建/更新 MCP 经验：字段格式、常见报错处理
type: feedback
originSessionId: 65382f9d-2d37-4571-8c62-76b96db3aa81
---
## 飞书 workitem 字段格式经验

### create_workitem 后 update_field 顺序
1. 先 `create_workitem` 传 `template` + `field_name`
2. 再 `update_field` 传 `priority` + `field_97ef0c` + `field_24180c` + `business`（这些字段放一起没问题）
3. 再单独处理 `field_179a9d`（技术文档/multi-text）
4. 最后用 `role_operate` 添加角色

### priority 字段
- option_id 是**字符串** `"2"`（不是数字），对应 `P2`

### multi-text 字段（field_179a9d）报错处理
- **报错**: `The color value is not within the specified range. [black white blue yellow green red purple]`
- **原因**: markdown 特殊字符（`|`、`#`、`(`、`) `等）在 multi-text 字段中触发颜色解析异常
- **解决**: 使用纯文本（无 markdown 表格、无标题符号），或先写其他字段再单独写 multi-text
- **临时方案**: 写入纯文本版描述，复杂格式放到飞书云文档，字段中只写链接

### role_operate 使用方式
```json
{
  "role_operate": [
    {"op": "add", "role_key": "Android", "user_keys": ["7310303312383852547"]},
    {"op": "add", "role_key": "QA", "user_keys": ["7310185777596465156"]}
  ]
}
```

**Why**: 飞书 multi-text 字段底层渲染逻辑会把 `|` 和 `#` 识别为某种颜色锚点，导致 `bytedance.bits.workitem_public` 报错。将 markdown 内容写进飞书云文档，字段只填纯文本或链接，可规避此问题。
