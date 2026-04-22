# Claude Code Provider Switcher
# Switch API backends via env vars — supports parallel multi-terminal usage
# Each terminal can run a different provider simultaneously

# ============================================
# Internal: reset all provider env vars before switching
# ============================================
_cc_reset_provider_env() {
    unset ANTHROPIC_AUTH_TOKEN
    unset ANTHROPIC_BASE_URL
    unset ANTHROPIC_API_KEY
    unset ANTHROPIC_MODEL
    unset ANTHROPIC_SMALL_FAST_MODEL
    unset ANTHROPIC_DEFAULT_OPUS_MODEL
    unset ANTHROPIC_DEFAULT_SONNET_MODEL
    unset ANTHROPIC_DEFAULT_HAIKU_MODEL
    unset CLAUDE_CODE_SUBAGENT_MODEL
    unset ENABLE_TOOL_SEARCH
    unset API_TIMEOUT_MS
    unset CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC
}

# ============================================
# Provider functions (env-var only, no file mutation)
# ============================================

cc-official() {
    _cc_reset_provider_env
    echo "official" > ~/.cc-provider
    echo "cc-official  |  using OAuth/subscription"
}

cc-kimi() {
    _cc_reset_provider_env
    echo "kimi" > ~/.cc-provider

    export ANTHROPIC_AUTH_TOKEN="sk-kimi-oTjrCrqQwYLX81Z0zkDHbkEKkbBgTLuak5NM6dhN8IJScgSQQa5iU2iSO0yEjqGq"
    export ANTHROPIC_BASE_URL="https://api.kimi.com/coding"
    export ANTHROPIC_MODEL="kimi-k2.5"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="kimi-k2.5"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="kimi-k2.5"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="kimi-k2.5"
    export CLAUDE_CODE_SUBAGENT_MODEL="kimi-k2.5"
    export ENABLE_TOOL_SEARCH="false"

    echo "cc-kimi  |  kimi-k2.5  |  api.kimi.com"
}

cc-minimax() {
    _cc_reset_provider_env
    echo "minimax" > ~/.cc-provider

    export ANTHROPIC_AUTH_TOKEN="sk-cp-74m9QxrVIY3s3cOOrflLcyAgyVv1IeM9ffzARalrFclsECUiHzdwUIjZ_jKGqfPcryqIcV2Rdjh492qSGNWdvzIIOecdMC5L0acnESWAbbMSEh91OABW1mU"
    export ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
    export ANTHROPIC_MODEL="MiniMax-M2.7-highspeed"
    export ANTHROPIC_SMALL_FAST_MODEL="MiniMax-M2.7-highspeed"
    export ANTHROPIC_DEFAULT_OPUS_MODEL="MiniMax-M2.7-highspeed"
    export ANTHROPIC_DEFAULT_SONNET_MODEL="MiniMax-M2.7-highspeed"
    export ANTHROPIC_DEFAULT_HAIKU_MODEL="MiniMax-M2.7-highspeed"
    export API_TIMEOUT_MS="3000000"
    export CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC="1"
    echo "cc-minimax  |  MiniMax-M2.7-highspeed  |  api.minimaxi.com"
}

# ============================================
# Auto-load on new terminal
# ============================================
if [[ -f ~/.cc-provider ]]; then
    case $(cat ~/.cc-provider) in
        kimi)    cc-kimi    >/dev/null 2>&1 ;;
        minimax) cc-minimax >/dev/null 2>&1 ;;
        official) ;;
    esac
fi

# Migrate old profile file
if [[ -f ~/.gaccode_profile && ! -f ~/.cc-provider ]]; then
    case $(cat ~/.gaccode_profile) in
        kimi)    echo "kimi" > ~/.cc-provider ;;
        minimax) echo "minimax" > ~/.cc-provider ;;
        *)       echo "official" > ~/.cc-provider ;;
    esac
fi

# ============================================
# Status
# ============================================
cc-status() {
    echo "=== Claude Code Provider ==="
    if [[ -f ~/.cc-provider ]]; then
        echo "Profile:  $(cat ~/.cc-provider)"
    else
        echo "Profile:  (not set)"
    fi
    if [[ -n "$ANTHROPIC_BASE_URL" ]]; then
        echo "URL:      $ANTHROPIC_BASE_URL"
    else
        echo "URL:      (official)"
    fi
    if [[ -n "$ANTHROPIC_MODEL" ]]; then
        echo "Model:    $ANTHROPIC_MODEL"
    fi
    if [[ -n "$ANTHROPIC_AUTH_TOKEN" ]]; then
        echo "Token:    ${ANTHROPIC_AUTH_TOKEN:0:12}...${ANTHROPIC_AUTH_TOKEN: -6}"
    elif [[ -n "$ANTHROPIC_API_KEY" ]]; then
        echo "Key:      ${ANTHROPIC_API_KEY:0:12}...${ANTHROPIC_API_KEY: -6}"
    else
        echo "Auth:     OAuth/subscription"
    fi
}
