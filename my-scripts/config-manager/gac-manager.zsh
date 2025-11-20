# Claude Code 配置管理
# 快速切换不同的 Claude Code 配置（GLM、官方等）

# ============================================
# 环境变量动态加载
# ============================================
# 根据 ~/.gaccode_profile 自动设置环境变量
# 可选值：main/little/official

if [[ -f ~/.gaccode_profile ]]; then
    GACCODE_PROFILE=$(cat ~/.gaccode_profile)
    case $GACCODE_PROFILE in
        main)
            # export ANTHROPIC_BASE_URL=https://gaccode.com/claudecode
            # export ANTHROPIC_API_KEY=sk-ant-oat01-8ef3230646a811c42bced02d2c1b5b9b45ec951d97a4f4c6acc17a03980d07a7
            ;;
        little)
            # export ANTHROPIC_BASE_URL=https://gaccode.com/claudecode
            # export ANTHROPIC_API_KEY=sk-ant-oat01-e00903ffb061fd32f5e470d6a2ca9888456eb9273a574ed416031ff60c03f45a
            ;;
        official)
            # 不设置环境变量，使用官方配置
            ;;
    esac
fi

# ============================================
# 辅助函数：添加 API Key 到 Claude 批准列表
# ============================================
_add_to_claude_approved() {
    local api_key="$1"

    if ! command -v jq &> /dev/null; then
        echo "⚠️  未安装 jq，跳过 ~/.claude.json 更新"
        return
    fi

    # 使用网上推荐的方法：添加 API Key 后20位到批准列表
    (cat ~/.claude.json 2>/dev/null || echo 'null') | \
    jq --arg key "${api_key: -20}" \
    '(. // {}) | .customApiKeyResponses.approved |= ([.[]?, $key] | unique)' \
    > ~/.claude.json.tmp && mv -f ~/.claude.json.tmp ~/.claude.json

    if [[ $? -eq 0 ]]; then
        echo "✅ 已添加 API Key 到 ~/.claude.json 批准列表"
    else
        echo "⚠️  更新 ~/.claude.json 失败"
    fi
}

# ============================================
# 辅助函数：从 Claude 批准列表移除 gaccode API Key
# ============================================
_remove_from_claude_approved() {
    if ! command -v jq &> /dev/null; then
        echo "⚠️  未安装 jq，跳过 ~/.claude.json 清理"
        return
    fi

    # 移除包含 gaccode API Key 特征的条目
    # main key 后8位: 980d07a7
    # little key 后8位: c03f45a
    local main_suffix="980d07a7"
    local little_suffix="c03f45a"

    (cat ~/.claude.json 2>/dev/null || echo 'null') | \
    jq --arg main "$main_suffix" --arg little "$little_suffix" \
    '(. // {}) | .customApiKeyResponses.approved |= ([.[]? | select((. | contains($main) | not) and (. | contains($little) | not))])' \
    > ~/.claude.json.tmp && mv -f ~/.claude.json.tmp ~/.claude.json

    if [[ $? -eq 0 ]]; then
        echo "✅ 已从 ~/.claude.json 批准列表中移除 gaccode API Key"
    else
        echo "⚠️  清理 ~/.claude.json 失败"
    fi
}

# ============================================
# 切换到主账户配置（高推理努力）
# ============================================
cc-gac-main() {
    echo "🔄 切换到主账户配置..."

    # 定义主账户 API Key
    local MAIN_API_KEY="sk-ant-oat01-8ef3230646a811c42bced02d2c1b5b9b45ec951d97a4f4c6acc17a03980d07a7"

    # 保存配置类型到文件（新终端会自动加载）
    echo "main" > ~/.gaccode_profile

    # 更新 codex config 文件
    cat > ~/.codex/config << 'EOF'
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ5Mjg0LCJlbWFpbCI6ImxpdHRsZXRyZWUwNzE4QGdtYWlsLmNvbSIsImFjY2Vzc1Rva2VuIjoiM2M3ZWIzYjU0YjZjMmNmN2UwZDFjZWU5ZWQ4ZmNmNGJmYjBlMjlhNDI4OTUzZjk4ZDA3ZDFiOTVlNjg4MDA0ZSIsImlhdCI6MTc2MTE3ODEwMiwiZXhwIjoxNzYzNzcwMTAyfQ.MTnmELHoB_F5IV2JfCRlLWPI0jGDep1gbigtGUFRtEs",
  "userId": 49284,
  "email": "littletree0718@gmail.com",
  "timestamp": "2025-10-23T00:08:27.113Z"
}
EOF

    # 更新 claudecode config 文件
    cat > ~/.claudecode/config << 'EOF'
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ5Mjg0LCJlbWFpbCI6ImxpdHRsZXRyZWUwNzE4QGdtYWlsLmNvbSIsImFjY2Vzc1Rva2VuIjoiM2M3ZWIzYjU0YjZjMmNmN2UwZDFjZWU5ZWQ4ZmNmNGJmYjBlMjlhNDI4OTUzZjk4ZDA3ZDFiOTVlNjg4MDA0ZSIsImlhdCI6MTc2MTE3ODEwMiwiZXhwIjoxNzYzNzcwMTAyfQ.MTnmELHoB_F5IV2JfCRlLWPI0jGDep1gbigtGUFRtEs",
  "userId": 49284,
  "email": "littletree0718@gmail.com",
  "timestamp": "2025-10-23T00:08:27.113Z"
}
EOF

    # 更新 config.toml 中的推理努力级别
    if [[ -f ~/.codex/config.toml ]]; then
        sed -i '' 's/model_reasoning_effort = .*/model_reasoning_effort = "high"/' ~/.codex/config.toml
    else
        echo "⚠️  config.toml 文件不存在"
    fi

    # 在当前 shell 中立即生效
    export ANTHROPIC_BASE_URL=https://gaccode.com/claudecode
    export ANTHROPIC_API_KEY="$MAIN_API_KEY"

    # 添加到 Claude 批准列表
    _add_to_claude_approved "$MAIN_API_KEY"

    echo ""
    echo "✅ 已切换到主账户配置"
    echo "   📧 用户: littletree0718@gmail.com"
    echo "   🧠 推理级别: high"
    echo "   💡 当前终端立即生效，新终端也会自动加载此配置"
}

# ============================================
# 切换到小号配置（低推理努力）
# ============================================
cc-gac-little() {
    echo "🔄 切换到小号配置..."

    # 定义小号 API Key
    local LITTLE_API_KEY="sk-ant-oat01-e00903ffb061fd32f5e470d6a2ca9888456eb9273a574ed416031ff60c03f45a"

    # 保存配置类型到文件（新终端会自动加载）
    echo "little" > ~/.gaccode_profile

    # 更新 codex config 文件
    cat > ~/.codex/config << 'EOF'
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ3ODY0LCJlbWFpbCI6IjYwMjc4ODQ1OEBxcS5jb20iLCJhY2Nlc3NUb2tlbiI6ImM1MDM0NWQyMDVlMzEyYzdmMDM3YTIyNjJkMzlmYTZjMWQ5NDQxYTYzNDU0MDVkYTBiYTBhNjliOGM4ZDJlZmMiLCJpYXQiOjE3NTg5NDczMTIsImV4cCI6MTc2MTUzOTMxMn0.QM5TSq67JfavLAPZJVFElIN9npOA_HaIZW6C2aioHLo",
  "userId": 47864,
  "email": "602788458@qq.com",
  "timestamp": "2025-09-27T04:30:57.838Z"
}
EOF

    # 更新 claudecode config 文件
    cat > ~/.claudecode/config << 'EOF'
{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOjQ3ODY0LCJlbWFpbCI6IjYwMjc4ODQ1OEBxcS5jb20iLCJhY2Nlc3NUb2tlbiI6ImM1MDM0NWQyMDVlMzEyYzdmMDM3YTIyNjJkMzlmYTZjMWQ5NDQxYTYzNDU0MDVkYTBiYTBhNjliOGM4ZDJlZmMiLCJpYXQiOjE3NTg5NDczMTIsImV4cCI6MTc2MTUzOTMxMn0.QM5TSq67JfavLAPZJVFElIN9npOA_HaIZW6C2aioHLo",
  "userId": 47864,
  "email": "602788458@qq.com",
  "timestamp": "2025-09-27T04:30:57.838Z"
}
EOF

    # 更新 config.toml 中的推理努力级别
    if [[ -f ~/.codex/config.toml ]]; then
        sed -i '' 's/model_reasoning_effort = .*/model_reasoning_effort = "low"/' ~/.codex/config.toml
    else
        echo "⚠️  config.toml 文件不存在"
    fi

    # 在当前 shell 中立即生效
    export ANTHROPIC_BASE_URL=https://gaccode.com/claudecode
    export ANTHROPIC_API_KEY="$LITTLE_API_KEY"

    # 添加到 Claude 批准列表
    _add_to_claude_approved "$LITTLE_API_KEY"

    echo ""
    echo "✅ 已切换到小号配置"
    echo "   📧 用户: 602788458@qq.com"
    echo "   🧠 推理级别: low"
    echo "   💡 当前终端立即生效，新终端也会自动加载此配置"
}

# ============================================
# 切换到 GLM Claude Code 配置
# ============================================
cc-glm() {
    echo "🔄 切换到 GLM Claude Code 配置..."

    # 保存配置类型到文件（新终端会自动加载）
    echo "glm" > ~/.gaccode_profile

    # 更新 Claude Code settings 文件
    if [[ -f ~/.claude/settings-glm.json ]]; then
        command cp -f ~/.claude/settings-glm.json ~/.claude/settings.json
        echo "✅ 已更新 settings.json 为 GLM 配置"
    else
        echo "⚠️  settings-glm.json 文件不存在"
        return 1
    fi

    echo ""
    echo "✅ 已切换到 GLM 配置"
    echo "   💡 当前终端立即生效，新终端也会自动加载此配置"
}

# ============================================
# 切换到官方 Claude Code 配置
# ============================================
cc-official() {
    echo "🔄 切换到官方 Claude Code 配置..."

    # 保存配置类型到文件（新终端会自动加载）
    echo "official" > ~/.gaccode_profile

    # 更新 Claude Code settings 文件
    if [[ -f ~/.claude/settings-official.json ]]; then
        command cp -f ~/.claude/settings-official.json ~/.claude/settings.json
        echo "✅ 已更新 settings.json 为官方配置"
    else
        echo "⚠️  settings-official.json 文件不存在"
        return 1
    fi

    # 在当前 shell 中取消环境变量
    unset ANTHROPIC_BASE_URL
    unset ANTHROPIC_API_KEY

    # 备份 gaccode 配置文件
    if [[ -f ~/.codex/config ]]; then
        mv ~/.codex/config ~/.codex/config.gac.bak
        echo "📦 已备份 codex config 到 config.gac.bak"
    fi

    if [[ -f ~/.claudecode/config ]]; then
        mv ~/.claudecode/config ~/.claudecode/config.gac.bak
        echo "📦 已备份 claudecode config 到 config.gac.bak"
    fi

    # 从 Claude 批准列表移除 gaccode API Key
    _remove_from_claude_approved

    echo ""
    echo "✅ 已切换到官方配置"
    echo "   💡 环境变量已清除，请使用官方 API Key 或登录方式"
    echo "   💡 当前终端立即生效，新终端也会自动使用官方配置"
}

# ============================================
# 查看当前配置状态
# ============================================
gac-status() {
    echo "📋 当前配置状态："
    echo ""

    # 显示配置文件状态
    if [[ -f ~/.gaccode_profile ]]; then
        local profile=$(cat ~/.gaccode_profile)
        echo "=== 配置文件 (~/.gaccode_profile) ==="
        case $profile in
            main)
                echo "🎯 当前配置: 主账户 (main)"
                ;;
            little)
                echo "🎯 当前配置: 小号 (little)"
                ;;
            glm)
                echo "🎯 当前配置: GLM (glm)"
                ;;
            official)
                echo "🎯 当前配置: 官方 (official)"
                ;;
            *)
                echo "⚠️  未知配置: $profile"
                ;;
        esac
        echo ""
    else
        echo "⚠️  配置文件 ~/.gaccode_profile 不存在"
        echo ""
    fi

    # 显示环境变量状态
    echo "=== 环境变量（当前终端） ==="
    if [[ -n "$ANTHROPIC_BASE_URL" ]]; then
        echo "🌐 ANTHROPIC_BASE_URL: $ANTHROPIC_BASE_URL"
    else
        echo "🌐 ANTHROPIC_BASE_URL: 未设置（使用官方）"
    fi

    if [[ -n "$ANTHROPIC_API_KEY" ]]; then
        echo "🔑 ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:0:20}...${ANTHROPIC_API_KEY: -8}"
    else
        echo "🔑 ANTHROPIC_API_KEY: 未设置"
    fi
    echo ""

    # 显示 Codex 配置
    echo "=== Codex 配置 ==="
    if [[ -f ~/.codex/config ]]; then
        echo "🔑 当前用户："
        jq -r '.email // "未知"' ~/.codex/config 2>/dev/null || echo "JSON解析失败"
        echo ""
    else
        echo "❌ config 文件不存在（使用官方配置）"
        if [[ -f ~/.codex/config.gac.bak ]]; then
            echo "📦 找到备份文件 config.gac.bak"
        fi
        echo ""
    fi

    if [[ -f ~/.codex/config.toml ]]; then
        echo "🧠 推理努力级别："
        grep "model_reasoning_effort" ~/.codex/config.toml || echo "未找到推理级别配置"
        echo ""
    else
        echo "❌ config.toml 文件不存在"
        echo ""
    fi

    # 显示 Claude Code 配置
    echo "=== Claude Code 配置 ==="
    if [[ -f ~/.claudecode/config ]]; then
        echo "🔑 当前用户："
        jq -r '.email // "未知"' ~/.claudecode/config 2>/dev/null || echo "JSON解析失败"
    else
        echo "❌ config 文件不存在（使用官方配置）"
        if [[ -f ~/.claudecode/config.gac.bak ]]; then
            echo "📦 找到备份文件 config.gac.bak"
        fi
    fi
    echo ""

    # 显示 Claude 批准列表状态
    echo "=== Claude 批准列表 (~/.claude.json) ==="
    if [[ -f ~/.claude.json ]] && command -v jq &> /dev/null; then
        local approved_count=$(jq -r '.customApiKeyResponses.approved | length' ~/.claude.json 2>/dev/null)
        if [[ "$approved_count" =~ ^[0-9]+$ ]]; then
            echo "✅ 已批准的 API Key 数量: $approved_count"
            if [[ $approved_count -gt 0 ]]; then
                echo "📝 批准的 Key (后20位):"
                jq -r '.customApiKeyResponses.approved[]' ~/.claude.json 2>/dev/null | sed 's/^/   - /'
            fi
        else
            echo "⚠️  批准列表为空或格式异常"
        fi
    else
        echo "❌ ~/.claude.json 不存在或未安装 jq"
    fi
}

# ============================================
# 别名
# ============================================
alias gacm='cc-gac-main'
alias gacl='cc-gac-little'
alias glmg='cc-glm'
alias gaco='cc-official'
alias gacs='gac-status'
