# Claude Code Subagents

Sourced from [wshobson/agents](https://github.com/wshobson/agents) (MIT License).

## Update

The upstream repo restructured into a plugin system (`plugins/*/agents/*.md`).
Agent files are extracted and deduplicated (largest version wins) into this flat directory.

```bash
# Update script:
rm -rf /tmp/wshobson-agents && git clone --depth 1 https://github.com/wshobson/agents.git /tmp/wshobson-agents

mkdir -p /tmp/agents-deduped
for name in $(find /tmp/wshobson-agents/plugins -path "*/agents/*.md" -exec basename {} \; | sort -u); do
  largest=$(find /tmp/wshobson-agents/plugins -path "*/agents/$name" -exec wc -c {} \; | sort -rn | head -1 | awk '{print $2}')
  cp "$largest" "/tmp/agents-deduped/$name"
done

rm -f ~/.claude/agents/*.md
cp /tmp/agents-deduped/*.md ~/.claude/agents/
rm -rf /tmp/wshobson-agents /tmp/agents-deduped
```

## Stats

- **Last updated**: 2026-03-31
- **Agent count**: 117
- **New since last update**: +45 agents (from 74)
