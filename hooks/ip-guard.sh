#!/usr/bin/env bash
# SessionStart notifier: 启动时一行提示 IP + OTEL 隔离状态
# 不阻塞会话、不阻塞消息
set -u

ALLOWED_IP="198.3.124.235"

# === IP 守卫 ===
IP="$(curl -fsS --max-time 5 https://ping0.cc/ip 2>/dev/null | tr -d '[:space:]')"
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

msg="${ip_msg} · ${otel_msg}"

# systemMessage 会在 UI 里显示给用户；additionalContext 注入给模型
jq -nc --arg m "$msg" '{
  systemMessage: $m,
  hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: $m }
}'
exit 0
