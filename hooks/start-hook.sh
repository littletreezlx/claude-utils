#!/usr/bin/env bash
# SessionStart hook: 会话启动时注入 IP + OTEL 状态到模型上下文，
# 并在项目根目录存在 TODO.md 时提醒用户。不阻塞会话、不阻塞消息。
set -u

ALLOWED_IP="198.3.124.235"

# === IP 守卫 ===
IP="$(curl -fsS --max-time 15 https://ping0.cc/ip 2>/dev/null | tr -d '[:space:]')"
[[ "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || IP=""

if [[ "$IP" == "$ALLOWED_IP" ]]; then
  ip_msg="✅ IP ${ALLOWED_IP}"
elif [[ -z "$IP" ]]; then
  ip_msg="⚠️ IP 不可达"
else
  ip_msg="⚠️ IP ${IP}（应为 ${ALLOWED_IP}）"
fi

# === OTEL 隔离状态 ===
if [[ "${CLAUDE_CODE_ENABLE_TELEMETRY:-0}" == "1" ]]; then
  device_id="$(printf '%s' "${OTEL_RESOURCE_ATTRIBUTES:-}" | sed -n 's/.*device\.id=\([^,]*\).*/\1/p')"
  otel_msg="⚠️ OTEL 开 ${device_id:-无ID}"
else
  otel_msg="✅ OTEL 关"
fi

# === TODO 提醒 ===
# SessionStart hook 的 cwd 由 CC 通过 stdin JSON 传入；用 jq 从 stdin 读
input="$(cat)"
project_dir="$(printf '%s' "$input" | jq -r '.cwd // empty' 2>/dev/null)"
[[ -z "$project_dir" ]] && project_dir="$PWD"

msg="${ip_msg} · ${otel_msg}"
if [[ -f "$project_dir/TODO.md" ]]; then
  msg="${msg} · 有 TODO"
fi

# systemMessage 显示在 UI；additionalContext 注入给模型
jq -nc --arg m "$msg" '{
  systemMessage: $m,
  hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: $m }
}'
exit 0
