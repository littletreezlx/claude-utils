---
name: ai-cli-design
description: >
  This skill should be used when writing, optimizing, or reviewing CLI tools,
  Python scripts, or shell scripts that will be invoked by AI agents or used
  within Claude Code. Use when the user says "write a CLI", "write a script",
  "optimize this script", "写个脚本", "写个 CLI", "优化脚本", "做个命令行工具",
  or when creating tools in scripts/ directories. Ensures tools are AI-friendly.
version: 0.1.0
---

# AI-Friendly CLI Design — 面向 AI 的命令行工具设计

## 目的

确保用户编写的 CLI 工具和脚本对 AI Agent 友好——能被 AI 自主发现、安全使用、高效消费输出。

> 灵感来源：飞书 lark-cli / Google gws 的 AI-native CLI 设计实践

## 触发条件

当以下**任一**条件满足时启动：

1. 用户要求编写 CLI 工具或 Python/Shell 脚本
2. 用户要求优化现有脚本的可用性
3. 正在创建 `scripts/` 目录下的工具
4. 工具的使用者包含 AI Agent（Claude Code、其他 LLM Agent）

## 四条设计原则

### 1. Help 即文档

`--help` 是 AI 认识工具的第一入口。不要只写 `Usage: tool [flags]`。

**必须包含**：每个参数的用途、默认值、使用示例。

```python
# argparse 示例
parser.add_argument(
    '--format', choices=['json', 'table', 'csv'], default='json',
    help='Output format. Use "json" for programmatic consumption, '
         '"table" for human reading. Default: json'
)
```

### 2. Dry-run 安全网

所有写入、删除、发送操作支持 `--dry-run`，先预览再执行。

```python
if args.dry_run:
    print(f"[DRY RUN] Would delete {len(records)} records:")
    for r in records:
        print(f"  - {r['name']} (created: {r['date']})")
    print("No changes made.")
    return
```

**规则**：AI 对写入/删除操作应默认先 `--dry-run`，确认后再真正执行。

### 3. 可执行的错误信息

AI 看到错误需要知道**怎么修**，不只是**出了什么错**。

每条错误包含三要素：**哪里错 + 错在哪 + 修复命令**。

```python
# Bad
print("Permission denied")

# Good
print("Error: Missing read permission for calendar API.\n"
      "Fix: Run `tool auth login --scope calendar:read`")
```

### 4. 结构化输出 + 控量

- 默认 `--output json`（AI 消费）；可选 `table`（人类阅读）
- 大数据量提供 `--limit` / `--page` 分页，避免撑爆上下文
- 输出只包含调用者需要的字段，不要 dump 全部内部状态

```python
parser.add_argument('--output', choices=['json', 'table'], default='json')
parser.add_argument('--limit', type=int, default=50,
                    help='Max items to return. Default: 50')
```

## 检查清单

编写或审查 CLI 工具时，逐条确认：

- [ ] `--help` 对每个参数有清晰说明和示例
- [ ] 写入/删除操作支持 `--dry-run`
- [ ] 错误信息包含修复建议（命令或步骤）
- [ ] 支持 JSON 输出格式
- [ ] 大数据量有分页/限量参数
- [ ] 退出码有意义（0=成功, 1=用户错误, 2=系统错误）

## 踩坑点

- **help 文本写了但没更新**：新增参数后忘记更新 help，AI 会用错误参数调用
- **dry-run 只打了个 log 就继续执行了**：`--dry-run` 必须 `return`/`exit`，不能只是多打一行日志
- **错误信息用了人类才懂的暗示**：如 "check your config"——AI 不知道 config 在哪，要给完整路径
- **JSON 输出混入了 print 调试信息**：导致 `json.loads()` 失败，调试输出走 stderr
