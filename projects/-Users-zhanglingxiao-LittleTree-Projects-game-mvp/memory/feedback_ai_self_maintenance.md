---
name: ai-self-maintenance-infrastructure
description: 2026-03-29 建立的 AI 自主维护基础设施：架构 linter、影响分析、%UniqueName、TestHelpers、GODOT_AI_TRAPS
type: feedback
---

## AI 自主维护项目的基础设施（2026-03-29 与 Gemini Think 讨论后建立）

### 核心理念
防御手段从「描述性文档」向「计算性契约」转移。把规则内化为脚本/断言能拦截的实体，对抗 AI 自身的幻觉与遗忘。

### 工具链
- `tools/check_architecture.sh` — 跨模块依赖 linter，交付前必跑
- `tools/impact_check.sh <file>` — 改代码前跑，看影响范围
- `tools/gen_code_index.sh` — 自动索引，检查 ARCHITECTURE.md 是否过期
- `tools/signal_map.sh` — 改信号前跑（已有）

### 关键约定
- UI 场景节点用 `%UniqueName` 引用，禁止深层 `$Path/To/Node`（防人类在编辑器中移动节点后代码静默失效）
- `tests/test_helpers.gd` (class_name TestHelpers) 提供标准 fixture factory
- `TestHelpers.assert_gold_conservation()` 用于经济系统不变量测试
- `docs/GODOT_AI_TRAPS.md` — 修改复杂 Node 交互前必读的陷阱速查

**Why:** Gemini 指出 AI 最大盲区是 .tscn 节点路径漂移（AI 看不到编辑器中的场景树变化）。项目从 29 文件扩展到 100+ 时，纯文档维护不可持续。
**How to apply:** 每次 session 开始如果涉及 Node 交互修改，先扫 GODOT_AI_TRAPS.md；交付前跑 check_architecture.sh；写测试用 TestHelpers 工厂方法。
