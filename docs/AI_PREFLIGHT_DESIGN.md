# AI Preflight Hook — 设计说明

> **日期**: 2026-03-19
> **状态**: Active
> **适用范围**: 全局（所有项目）

---

## 这是什么

一个 `SessionStart` hook，在每次 Claude Code 新会话启动时自动运行 `ai-preflight.sh`，将项目状态快照注入 AI 上下文。

## 为什么需要它

**核心问题**：Claude Code 每次会话完全无状态。之前的方案是在 CLAUDE.md 中写"会话启动协议"，要求 AI 手动读 8-12 个文件来恢复上下文。这有两个问题：

1. **慢**：8-12 次文件读取消耗 token 和时间
2. **不可靠**：依赖 AI "记住"要读哪些文件——而 AI 是无状态的

**解决思路**（与 Gemini Think 讨论后确定）：

> "不要教 AI 怎么做（通过文档），而是让系统自动完成。"
> — 防呆工程哲学

Hook 让这个过程**零手动**：会话启动 → 脚本自动运行 → AI 立刻获得项目全貌。

## 设计决策

### 为什么是 SessionStart hook 而非 CLAUDE.md 指令？

| 方案 | 问题 |
|------|------|
| CLAUDE.md 写"第一步运行脚本" | 依赖 AI 遵守指令，不可靠 |
| UserPromptSubmit hook | 每次用户发消息都运行，浪费 |
| **SessionStart hook** | ✅ 每次会话只运行一次，自动注入 |

### 为什么输出要极度精简（异常驱动）？

Hook 输出占用 AI 上下文 token。经 Gemini Think 讨论后确定：

- **正常状态 = 一个词**（clean / sync / none）
- **只有异常才展开**（错误详情、broken paths 等）
- **目标 5-10 行**（实测一切正常时 4 行）

### 为什么不输出 git status？

Claude Code 启动时有**内置的 gitStatus 注入**（branch, uncommitted changes, recent 10 commits）。preflight 再输出一遍是纯冗余。

### 为什么输出 TODO 内容而非数量？

"TODO.md exists (3 pending items)" 对 AI 毫无用处——它不知道第一条是什么。
直接输出前 1-2 条任务内容，让 AI 立刻知道 **Resume Point**。

## 技术实现

### Hook 配置（`~/.claude/settings.json`）

```json
{
  "hooks": {
    "SessionStart": [{
      "hooks": [{
        "type": "command",
        "command": "... | python3 -c 'import sys,json; ...'",
        "timeout": 60,
        "statusMessage": "Running AI preflight..."
      }]
    }]
  }
}
```

- 用 `python3` 包装输出为 JSON，通过 `hookSpecificOutput.additionalContext` 注入 AI 上下文
- 同时通过 `systemMessage` 展示给用户看
- 60 秒超时（`dart analyze` 可能较慢）

### 脚本查找顺序

```
./scripts/ai-preflight.sh    → 项目定制版（优先）
../scripts/ai-preflight.sh   → Flutter 通用版（fallback）
都没有                        → 静默跳过（不影响非 Flutter 项目）
```

### 输出格式（异常驱动）

一切正常时：
```
# project_name Preflight
- Next: 实现用户认证功能
- Analyze: clean
- Codegen: sync
```

有问题时：
```
# project_name Preflight
- Next: no TODO.md (ask user for task)
- Analyze: 3 issues
    warning • Unused import • lib/xxx.dart:5
- Codegen: 2 files missing — run build_runner
- Coupling: recently touched management, settings
- Alerts:
  ⚠ 5 broken paths in FEATURE_CODE_MAP.md — run doc-health.sh
  ⚠ flutter_common submodule updated — review changes
```

## 相关文件

| 文件 | 说明 |
|------|------|
| `~/.claude/settings.json` | Hook 配置 |
| `/flutter/scripts/ai-preflight.sh` | 通用版脚本 |
| `/flutter/scripts/doc-health.sh` | 文档健康检查（preflight 内部调用逻辑） |
| `docs/superpowers/specs/2026-03-19-ai-maintainability-design.md` | 完整设计 spec |

## 演进历史

1. **v1** (2026-03-19 16:05): 完整版——18 行，含 git status + uncommitted changes
2. **v2** (2026-03-19 16:36): 异常驱动版——4 行（正常时），删除与内置 gitStatus 的冗余
