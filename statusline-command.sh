#!/bin/bash
# Claude Code statusLine - 简洁版
# 格式: [green]project_dir[reset][magenta]  branch[reset][dim] · Model · ctx 85%[reset]

# === 配置 ===
RATE_INFO_PADDING=50  # rate_info 左侧空格数，调大则更靠右

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd // ""')
model_full=$(echo "$input" | jq -r '.model.display_name // ""')
remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')

# Project directory name only (basename)
dir_name=$(basename "$cwd")

# Git branch (skip optional locks to avoid conflicts)
git_branch=""
if git -C "$cwd" rev-parse --git-dir > /dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    git_branch="  $branch"
  fi
fi

# Abbreviated model name: strip leading "Claude " and anything in parentheses
# e.g. "Claude Opus 4.6 (1M context)" -> "Opus 4.6"
model_short=$(echo "$model_full" | sed 's/^Claude //; s/ (.*//')

# Context used (= 100 - remaining)
context_info=""
if [ -n "$remaining" ] && [ "$remaining" != "null" ]; then
  remaining_int=${remaining%.*}
  used=$((100 - remaining_int))
  context_info="$used%"
fi

# 5-hour rate limit info: "0% 2pm" (Asia/Shanghai)
rate_info=""
five_pct=$(echo "$input" | jq -r '.rate_limits.five_hour.used_percentage // empty')
five_resets=$(echo "$input" | jq -r '.rate_limits.five_hour.resets_at // empty')
if [ -n "$five_pct" ] && [ -n "$five_resets" ]; then
  pct_int=$(printf '%.0f' "$five_pct")
  reset_time=$(LC_TIME=C TZ="Asia/Shanghai" date -r "$five_resets" +%I%p 2>/dev/null | sed 's/^0//' | tr '[:upper:]' '[:lower:]')
  rate_info="${pct_int}% ${reset_time}"
fi

# Compose: [bold green]dir[reset][magenta] branch[reset][dim] · Model · [reset][bold green]ctx%[reset][dim] · rate[reset]
base_part=""
if [ -n "$model_short" ] && [ -n "$context_info" ]; then
  base_part=$(printf "\033[1;32m%s\033[0m\033[35m%s\033[0m\033[2m · %s · ctx \033[0m\033[1;32m%s\033[0m" \
    "$dir_name" "$git_branch" "$model_short" "$context_info")
elif [ -n "$model_short" ]; then
  base_part=$(printf "\033[1;32m%s\033[0m\033[35m%s\033[0m\033[2m · %s\033[0m" \
    "$dir_name" "$git_branch" "$model_short")
elif [ -n "$context_info" ]; then
  base_part=$(printf "\033[1;32m%s\033[0m\033[35m%s\033[0m\033[2m · ctx \033[0m\033[1;32m%s\033[0m" \
    "$dir_name" "$git_branch" "$context_info")
else
  base_part=$(printf "\033[1;32m%s\033[0m\033[35m%s\033[0m" \
    "$dir_name" "$git_branch")
fi

if [ -n "$rate_info" ]; then
  # Fixed padding (adjust RATE_INFO_PADDING at top of file)
  padding=$(printf '%*s' "$RATE_INFO_PADDING" '')

  printf "%s\033[2m%s%s\033[0m" "$base_part" "$padding" "$rate_info"
else
  printf "%s" "$base_part"
fi
