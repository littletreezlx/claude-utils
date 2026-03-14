#!/bin/bash
# Claude Code statusLine script
# Inspired by oh-my-zsh amuse theme: dirname + git branch + model + context %

input=$(cat)

cwd=$(echo "$input" | jq -r '.cwd // .workspace.current_dir // ""')

# Last directory name only (basename)
dir_name=$(basename "$cwd")

# Git branch (skip locks to avoid conflicts with running git operations)
git_branch=""
if git -C "$cwd" rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git -C "$cwd" --no-optional-locks symbolic-ref --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    git_branch=" (${branch})"
  fi
fi

# Context used: prefer env var, fall back to JSON field
remaining="${CLAUDE_CONTEXT_WINDOW_REMAINING_PERCENT:-}"
if [ -z "$remaining" ]; then
  remaining=$(echo "$input" | jq -r '.context_window.remaining_percentage // empty')
fi

# Context display: show used % (100 - remaining)
context_info=""
if [ -n "$remaining" ]; then
  remaining_int=${remaining%.*}
  used=$((100 - remaining_int))
  context_info="ctx ${used}%"
fi

# Build status line with ANSI colors (terminal will display dimmed)
# Green: dirname, Magenta: git branch, Cyan: context used
printf "\033[1;32m%s\033[0m\033[35m%s\033[0m  \033[36m%s\033[0m" \
  "$dir_name" \
  "$git_branch" \
  "$context_info"
