#!/bin/bash

# Claude Code PreToolUse Hook
# 用途：拦截危险命令，防止 Mac 熄屏
# Exit code 0: 允许执行
# Exit code 2: 阻止执行，stderr 输出会显示给 Claude

# 从 stdin 读取 JSON 数据
INPUT=$(cat)

# 提取 tool_name 和 command
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name // empty' 2>/dev/null)
COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // empty' 2>/dev/null)

# 如果是 Bash 工具，检查是否包含 sleep 命令
if [ "$TOOL_NAME" = "Bash" ]; then
    # 检测独立的 sleep 命令（sleep N 格式）
    if echo "$COMMAND" | grep -qE '(^|;|\||&&)\s*sleep\s+[0-9]+(\s|;|\||&&|$)'; then
        # 输出到 stderr，这样 Claude 可以看到
        >&2 echo "❌ sleep 命令已被拦截（会导致 Mac 熄屏）"
        # 退出码 2 表示阻止执行
        exit 2
    fi
fi

# 允许其他命令通过
exit 0
