把一个已完成开发的功能推到飞书项目（shipd 空间），建立工作项 + 推文档 + 排期工时。

## 输入

[设计文档路径... (可选，空格分隔)]
  例：`/push-feishu-project docs/performance/runtime-jank-monitoring-design.md`

如果不传文档路径，直接走"只建工作项"流程。

## 执行流程（严格按序）

### 0. 确认基本信息（必做，禁止跳过）

每次调用都要先向用户 **一次性** 确认以下要点，不要猜：

1. **需求名称**（最重要！工作项顶部主标题），格式 `【POS/KDS/TV】简短功能描述`，用户可直接说名字
2. **业务线**：
   - POS 收银 → `675ba962962ffaffa73cdcee`
   - 智慧屏 TV → `675ba96b710814f251b11a67`
   - KDS 厨显 → `675ba92141a2b5c54eb18826`
3. **需求类型**（默认技术需求）：
   - 技术需求 → template=`574498`, field_97ef0c=`tbs7xiczf`
   - 产品需求 → template=`892574`, field_97ef0c=`mfbdomq1h`
   - BugFix → template=`598884`, field_97ef0c=`ws669y056`
4. **优先级**（默认 P2）：P0=`"0"` / P1=`"1"` / P2=`"2"` / P3=`"r7hy4v5d3"`（**字符串**）
5. **是否有工单**：无工单=`qlpqg04_a`（默认），有工单=`eyo6lmwnp`
6. **工时安排**（必须逐节点确认，单位：天）：
   - 给出默认方案让用户 Y/N 或改：
     - 技术评审 `waiting_for_rd_discussion`：1 天
     - 联调自测 `state_10`：1 天
     - 测试中 `waiting_for_ios_test`：1 天
     - 上线 `waiting_for_ios_merge`：1 天
   - 如果有跨天排期，给出具体开始/结束日期（北京时间 00:00）
7. **额外参与角色**（默认全张凌霄，王雷03 不再默认）：如有 QA 或其他同事要拉入，问用户

> **重要**：第 6 条工时是最容易被 AI 忽略的。哪怕用户已在对话里说"就排 3 天"，也要确认分到哪几个节点。

### 1. 推设计文档到飞书 wiki（如传入了路径）

对每个文档路径调用 `/push-feishu-doc <path>` 逻辑（或直接用 `mcp__feishu-docs__create-doc` + `wiki_node=https://shihengtech.feishu.cn/wiki/ALvRwaJbKiOA2EkvfAccJPmInAh`）：

- 去掉首行一级标题（飞书自动生成 title）
- 保留 mermaid / 表格 / 代码块
- 创建后把映射写进 `docs/.feishu-doc-map.json`
- 拿到 `doc_url`，后面贴到工作项技术文档字段

### 2. 创建工作项

调用 `mcp__feishu__create_workitem`：

```json
{
  "project_key": "shipd",
  "work_item_type": "story",
  "fields": [
    {"field_key": "template", "field_value": "574498"},
    {"field_key": "_name", "field_value": "【POS】XXX功能"},
    {"field_key": "field_name", "field_value": "【POS】XXX功能"}
  ]
}
```

> **陷阱**：
> - `_name` 是工作项**主标题**（飞书 UI 顶部显示）
> - `field_name` 是模板内部的"需求名称"文本字段
> - **两个都要填**，且通常内容一致
> - 如果只填 `field_name`，工作项主标题为空，用户会看到一堆乱字段

### 3. 填写其他字段

```json
[
  {"field_key": "priority", "field_value": "2"},
  {"field_key": "field_97ef0c", "field_value": "tbs7xiczf"},
  {"field_key": "field_24180c", "field_value": "qlpqg04_a"},
  {"field_key": "business", "field_value": "675ba962962ffaffa73cdcee"},
  {"field_key": "description", "field_value": "纯文本描述..."}
]
```

### 3.1 描述字段（description，multi-text）写作规则

**面向同事**，不是 AI 看的。**硬约束：总长度 ≤ 3 段 / ≤ 200 字**。超过 200 字一定是啰嗦了。

结构（每段一句话）：

1. **痛点 + 方案**（合成一段）：以前什么痛点 → 现在用什么技术 → 同事能从哪里看到产出
2. **当前状态**：什么分支、什么进度、什么节点可上线
3. **文档**：一行飞书 wiki 链接

**禁写**：
- 分章节（"一、背景""二、核心价值""三大指标"等）→ 全塞进一段
- 编号列表 / 子弹点嵌套
- 详细技术细节（TransactionContext、AtomicLong、差值法…）→ 全放 wiki
- 表格、markdown 粗体堆砌
- markdown 表格 / `|` / 过多 `#`（触发 `The color value is not within the specified range` 报错）
- "AI-Only" / "Claude Code" / "Anthropic" 字样（公司项目禁用，见 memory `feedback_no_ai_only_wording.md`）

**风格示例**：

> POS 之前只有接口耗时监控，看不到客户端卡顿。本方案用 AndroidX JankStats 采集每帧渲染耗时，页面级小时聚合后通过 Sentry 幽灵事务上报，产出卡顿率红黑榜和冻结帧趋势图。
>
> 开发+文档已完成，4.22 真机验证数据能进 Sentry Discover 后即可上线。
>
> 核心指标：Jank Rate（卡顿率）、Frozen Frames（冻结帧次数）。
>
> 详细方案见：飞书 wiki 链接

### 3.2 技术文档字段

- **`field_1`（link 类型）**：直接填飞书 wiki URL，飞书 UI 会渲染为蓝色链接
- **`field_179a9d`（multi-text 富文本）**：用纯文本写简要说明 + 链接。**别写 markdown 表格**

### 4. 配角色（role_operate）

**默认方案**（单人安卓需求）：

```json
{
  "role_operate": [
    {"op": "add", "role_key": "PM", "user_keys": ["7310303312383852547"]},
    {"op": "add", "role_key": "Android", "user_keys": ["7310303312383852547"]},
    {"op": "add", "role_key": "tech_owner", "user_keys": ["7310303312383852547"]},
    {"op": "add", "role_key": "QA", "user_keys": ["7310303312383852547"]},
    {"op": "add", "role_key": "ferd", "user_keys": ["7310303312383852547"]}
  ]
}
```

> **必填角色**（少一个流程会卡住）：
> - `PM`（PO）
> - `Android` 或后端角色
> - `tech_owner`（技术评审负责人）
> - `QA`（测试）
> - **`ferd`（前端开发）— 特别容易漏！没有它开发节点无负责人**
>
> **user_keys**：
> - 张凌霄 = `7310303312383852547`
> - 王雷03 = `7310185777596465156`（现在不再默认，需用户明确要求才加）

### 5. 节点排期 + 工时

story 模板走**节点流**（不是状态流），用 `mcp__feishu__update_node`。**不要用 `get_transitable_states`**（会报 "story work item flow mode not state flow"）。

常见节点 node_key：

| node_key | 名称 | 默认 owner 角色 | 典型工时 |
|---------|------|--------------|---------|
| `waiting_for_rd_discussion` | 技术评审 | PM/tech_owner | 1 天 |
| `state_8` | 测试用例 | QA | 视情况 |
| `state_10` | 联调(自测&冒烟通过) | 开发 | 1-2 天 |
| `state_11` | 待测试 | QA | 0.5 天 |
| `waiting_for_ios_test` | 测试中 | QA | 1 天 |
| `state_12` | Stage 回归 | QA | 0.5 天 |
| `state_14` | 产品验收 | PM | 0.5 天 |
| `waiting_for_ios_merge` | 上线 | PM | 0.5 天 |

**时间戳计算**（北京时间 00:00 的毫秒值）：

```python
import datetime
tz = datetime.timezone(datetime.timedelta(hours=8))
int(datetime.datetime(2026, 4, 20, tzinfo=tz).timestamp() * 1000)
# 2026-04-20 00:00 +0800 = 1776614400000
```

单日节点排期示例：

```json
{
  "project_key": "shipd",
  "work_item_id": "6974521579",
  "node_id": "waiting_for_rd_discussion",
  "node_schedule": {
    "estimate_start_date": 1776614400000,
    "estimate_end_date": 1776614400000,
    "owners": ["7310303312383852547"],
    "points": 1
  }
}
```

> **关键参数**：
> - `points`：估分/工期（天），飞书会按此计算 Gantt 长度。不填则 `is_auto=true` 时会按 start/end 差自动补
> - `owners`：节点负责人（和顶部角色独立）
> - `estimate_start_date` / `estimate_end_date`：**UTC+8 00:00 毫秒时间戳**

### 6. 输出

完成后向用户汇报：

```
✅ 飞书项目已建立
📌 工作项：<URL>
   - 需求名称：xxx
   - 模板：技术需求 / P2 / POS 业务线
   - 角色：PM/Android/tech_owner/QA/ferd = 张凌霄
   - 排期：4.20 评审 1d / 4.21 联调 1d / 4.22 测试+上线 1d
📄 设计文档：<wiki URL>
   - 已写入 docs/.feishu-doc-map.json
```

## 踩坑清单（严格遵守）

1. ❌ **只填 `field_name` 不填 `_name`** → 工作项主标题为空
2. ❌ **不填 `ferd` 角色** → 开发/联调节点无负责人，流程卡住
3. ❌ **description 用 markdown 表格** → `The color value is not within the specified range` 报错
4. ❌ **description 出现 "AI-Only" / "Claude Code"** → 公司项目禁用术语
5. ❌ **对 story 调用 `get_transitable_states`** → `story work item flow mode not state flow`，story 是节点流，用 `get_node_detail`
6. ❌ **`priority` 传数字 `2`** → 必须字符串 `"2"`
7. ❌ **时间戳按 UTC** → 必须 UTC+8 的 00:00，否则排期错位到前一天晚上
8. ❌ **跳过工时确认** → 飞书 Gantt 图会显示 0 天，用户体验差
9. ❌ **把实施手册也推上去** → 默认**只推设计综述**，实施手册是 AI 内部参考，同事一般不看
10. ❌ **用 `mcp__feishu-docs__create-doc` 时 markdown 保留首行 `# 标题`** → 与 title 参数重复，会报错

## 映射文件

- 飞书 wiki 默认挂靠节点：`https://shihengtech.feishu.cn/wiki/ALvRwaJbKiOA2EkvfAccJPmInAh`（Android POS 技术文档总目录）
- 本地映射：`docs/.feishu-doc-map.json`
- 空间 project_key：`shipd`（食亨IPD）
- 详细 user_key / field_key 速查见 memory `reference_feishu_project.md`
