#!/usr/bin/env bash
# SessionStart notifier: 若经白名单域名的出口 IP 不是 ALLOWED_IP，则在启动时
# 向用户弹一条提示。不阻塞会话、不阻塞消息。
set -u

ALLOWED_IP="50.114.173.48"

# 链式代理：必须用白名单域名 (ping0.cc) 探测经代理的真实出口 IP
IP="$(curl -fsS --max-time 5 https://ping0.cc/ip 2>/dev/null | tr -d '[:space:]')"
[[ "$IP" =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]] || IP=""

if [[ "$IP" == "$ALLOWED_IP" ]]; then
  msg="✅ IP 守卫：出口 IP = ${ALLOWED_IP}，链式代理正常。"
elif [[ -z "$IP" ]]; then
  msg="⚠️ IP 守卫：无法通过 ping0.cc 获取公网出口 IP。链式代理可能异常，请检查。"
else
  msg="⚠️ IP 守卫：经白名单域名的出口 IP 是 ${IP}，不是预期的 ${ALLOWED_IP}。链式代理可能没走对，请检查路由。"
fi

# systemMessage 会在 UI 里显示给用户；additionalContext 注入给模型
jq -nc --arg m "$msg" '{
  systemMessage: $m,
  hookSpecificOutput: { hookEventName: "SessionStart", additionalContext: $m }
}'
exit 0
