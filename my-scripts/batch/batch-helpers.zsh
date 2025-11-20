# Claude Code 批量工具 ZSH 配置
# 提供 batchcc, batchcx, batchcc-todo 等批量执行命令

# 设置批量工具脚本根目录
BATCH_TOOLS_ROOT="$HOME/.claude/my-scripts/batch"

# ==================== Claude Code 批量工具 ====================
# batchcc - 批量执行 Claude Code 命令 (增强版 - 默认并行执行)
# 用法: batchcc [template文件路径] [选项]
# 默认8个并发执行，使用--single强制串行
batchcc() {
    local default_script="$BATCH_TOOLS_ROOT/batchcc.py"

    if [ ! -f "$default_script" ]; then
        echo "❌ 找不到批量执行脚本: $default_script"
        return 1
    fi

    # 显示用法说明
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        echo "用法: batchcc [template文件路径] [选项]"
        echo ""
        echo "选项:"
        echo "  --single             强制串行执行 (一次只执行一个任务)"
        echo "  -p N, --parallel N   自定义并发数 (默认: 8)"
        echo "  -h, --help          显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  batchcc                    # 默认8并发执行当前目录的template"
        echo "  batchcc --single           # 串行执行当前目录的template"
        echo "  batchcc template           # 默认8并发执行指定template文件"
        echo "  batchcc template --single  # 串行执行指定template文件"
        echo "  batchcc -p 4               # 4并发执行当前目录的template"
        echo "  batchcc template -p 2      # 2并发执行指定template文件"
        return 0
    fi

    # 简化参数处理 - 直接传递所有参数到Python脚本
    local cmd="python \"$default_script\""

    # 如果有参数，直接追加
    if [ $# -gt 0 ]; then
        cmd="$cmd"
        for arg in "$@"; do
            cmd="$cmd \"$arg\""
        done
    fi

    echo "🚀 执行批量 Claude Code 命令..."

    # 检查是否有--single参数来确定执行模式
    if [[ "$*" == *"--single"* ]]; then
        echo "📋 串行模式已启用"
    else
        echo "🚀 并行模式已启用 (默认8并发)"
    fi

    eval "$cmd"
}

# batchcc-todo - 批量执行 /todo-doit 命令的快捷函数（强制串行）
# 用法: batchcc-todo <次数>
# 示例: batchcc-todo 5           # 串行执行5次 /todo-doit
#       batchcc-todo 10          # 串行执行10次 /todo-doit
batchcc-todo() {
    # 检查是否提供了次数参数
    if [ $# -eq 0 ]; then
        echo "❌ 错误: 必须提供执行次数参数"
        echo ""
        echo "用法: batchcc-todo <次数>"
        echo ""
        echo "参数:"
        echo "  <次数>               必填，执行 /todo-doit 的次数（串行执行）"
        echo ""
        echo "示例:"
        echo "  batchcc-todo 5       # 串行执行5次 /todo-doit"
        echo "  batchcc-todo 10      # 串行执行10次 /todo-doit"
        return 1
    fi

    # 获取执行次数（第一个参数）
    local count="$1"

    # 验证次数参数是否为数字
    if ! [[ "$count" =~ ^[0-9]+$ ]]; then
        echo "❌ 错误: 执行次数必须是正整数，得到: $count"
        return 1
    fi

    if [ "$count" -le 0 ]; then
        echo "❌ 错误: 执行次数必须大于0，得到: $count"
        return 1
    fi

    echo "🚀 开始串行执行 $count 次 /todo-doit"
    echo ""

    local success_count=0
    local fail_count=0

    # 循环执行 cc 命令
    for ((i=1; i<=count; i++)); do
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "📋 [$i/$count] 执行 /todo-doit"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

        # 执行 cc 命令
        cc "/todo-doit"

        if [ $? -eq 0 ]; then
            ((success_count++))
            echo "✅ [$i/$count] 执行成功"
        else
            ((fail_count++))
            echo "❌ [$i/$count] 执行失败"
        fi

        echo ""
    done

    # 输出执行总结
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📊 执行完成"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "总计: $count 次"
    echo "成功: $success_count 次"
    echo "失败: $fail_count 次"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    # 如果有失败的，返回错误码
    if [ $fail_count -gt 0 ]; then
        return 1
    fi

    return 0
}

# batchcx - 批量执行 Codex 命令 (增强版 - 默认并行执行)
# 用法: batchcx [template文件路径] [选项]
# 默认8个并发执行，使用--single强制串行
batchcx() {
    local default_script="$BATCH_TOOLS_ROOT/batchcx.py"

    if [ ! -f "$default_script" ]; then
        echo "❌ 找不到批量执行脚本: $default_script"
        return 1
    fi

    # 显示用法说明
    if [[ "$1" == "-h" ]] || [[ "$1" == "--help" ]]; then
        echo "用法: batchcx [template文件路径] [选项]"
        echo ""
        echo "选项:"
        echo "  --single             强制串行执行 (一次只执行一个任务)"
        echo "  -p N, --parallel N   自定义并发数 (默认: 8)"
        echo "  -h, --help          显示此帮助信息"
        echo ""
        echo "示例:"
        echo "  batchcx                    # 默认8并发执行当前目录的template"
        echo "  batchcx --single           # 串行执行当前目录的template"
        echo "  batchcx template           # 默认8并发执行指定template文件"
        echo "  batchcx template --single  # 串行执行指定template文件"
        echo "  batchcx -p 4               # 4并发执行当前目录的template"
        echo "  batchcx template -p 2      # 2并发执行指定template文件"
        return 0
    fi

    # 简化参数处理 - 直接传递所有参数到Python脚本
    local cmd="python \"$default_script\""

    # 如果有参数，直接追加
    if [ $# -gt 0 ]; then
        cmd="$cmd"
        for arg in "$@"; do
            cmd="$cmd \"$arg\""
        done
    fi

    echo "🚀 执行批量 Codex 命令..."

    # 检查是否有--single参数来确定执行模式
    if [[ "$*" == *"--single"* ]]; then
        echo "📋 串行模式已启用"
    else
        echo "🚀 并行模式已启用 (默认8并发)"
    fi

    eval "$cmd"
}
