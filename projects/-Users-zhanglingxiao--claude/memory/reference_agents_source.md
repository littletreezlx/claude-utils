---
name: agents-source
description: ~/.claude/agents/ subagent 集合的来源仓库和更新方法
type: reference
---

`~/.claude/agents/` 下的 subagent 定义文件来源于 [wshobson/agents](https://github.com/wshobson/agents)（MIT License）。

上游仓库已重构为 plugin 体系（`plugins/*/agents/*.md`），不再是根目录扁平 `.md` 文件。
本地采用**提取 + 去重**方式维护：从各 plugin 中提取 agent 文件，同名取最大文件。

**Why:** 上游不支持直接 `git clone` 到 agents/ 使用，submodule 方案也不可行。手动提取是当前最简方案。

**How to apply:** 更新时运行 `~/.claude/agents/README.md` 中的脚本。上次更新 2026-03-31，117 个 agent。
