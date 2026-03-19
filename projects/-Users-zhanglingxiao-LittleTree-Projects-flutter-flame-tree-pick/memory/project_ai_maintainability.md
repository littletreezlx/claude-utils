---
name: AI 自主维护能力增强
description: 2026-03-19 实施的防呆工程三支柱架构，用脚本和测试替代文档约束
type: project
---

## 防呆工程三支柱（2026-03-19 实施）

核心哲学：**能编码进约束的就不写文档**。对无状态 AI，可执行的检查永远优于文档描述。

**Why:** Gemini think 角色指出——AI 用人类社会学模型（积累信任、反思错误）套无状态函数是认知盲点。正确做法是让项目本身物理阻止错误。

**How to apply:**

### 支柱一：Bootloader
- `scripts/ai-preflight.sh` — 新会话第一步运行，替代 8-12 次文件读取
- `scripts/doc-health.sh` — 验证文档路径有效性

### 支柱二：Contract Tests（test/integration/architecture/）
- `clean_architecture_test.dart` — 层级依赖（含 Data→Infra, Presentation→Data）
- `coupling_guard_test.dart` — **权威来源**，替代 CLAUDE.md 隐式耦合表
- `code_convention_test.dart` — @riverpod 禁令、print 禁令、sealed class、codegen 完整性
- `helpers/` — file_scanner.dart + import_analyzer.dart

### 支柱三：Context Radar
- `scripts/get-context.sh <module>` — 按需拉取模块上下文（FILES/VIEWMODEL/IMPORTS/IMPORTED_BY/TESTS/SPEC/RECENT_CHANGES）

### 已否决方案
- AI 失误日志 (FAILURE_LOG.md) — AI 无法从文字学习，失误应转为测试
- 信任阶梯 (TRUST_PROFILE.md) — 对无状态 AI 无意义
