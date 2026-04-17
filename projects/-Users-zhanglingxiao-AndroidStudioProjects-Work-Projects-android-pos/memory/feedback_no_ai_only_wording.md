---
name: 公司项目代码/文档禁用 "AI-Only" 字样
description: android-pos 等公司项目的源码、注释、docs 不得出现 "AI-Only"、"AI-only"、"AI Only" 等协作模式术语
type: feedback
originSessionId: c8da26d9-931f-4fac-abb2-03205243a093
---
公司项目的代码、注释、docs/ 下的文档不得出现 "AI-Only"、"AI-only"、"AI Only" 等协作模式术语。

**Why**：这些是个人全局 CLAUDE.md 里描述与 Claude 协作方式的术语，不是公司共识，进公司仓库会让同事困惑甚至误以为是公司规范。用户 2026-04-16 明确要求。

**How to apply**：
- 在 android-pos / android-kds / smart-screen 三个公司项目中的源码、注释、docs/、commit message、PR description 里一律不写 "AI-Only" 及其变体
- 需要解释"设计在无人类介入下容易失效"这类理由时，改用中性措辞，如"隐式合约难以在编译期强制"、"靠代码走查难以发现"、"规模扩大时容易漏写"
- 个人全局 memory / decision records / ~/.claude/ 目录下保留此术语无妨，仅限公司项目禁用
- 写前检查：凡是要提交到公司仓库的文件，grep 一下 "AI-Only|AI-only|AI Only" 确保无遗留
