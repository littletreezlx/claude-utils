---
name: feedback_no_founder_gated_regression_in_todo
description: flametree_ai 项目的 TODO.md 不要列 Founder-gated 真机回归任务；代码修复完成即视为 AI 任务完成
type: feedback
originSessionId: 9f0f873e-b039-4684-bc7b-76d02232293f
---
Founder-gated 真机回归（例如 `/ai-qa-stories macos` 全量回归、真机两通电话续聊验证、真机 E2E 报告生成等）不要列入 `flametree_ai/TODO.md` 作为待办任务，也不要在交付小结里把"等待 Founder 回归"当成未完成项。

**Why**: AI 无权触发真机 E2E，把这类条目放在 AI TODO 里会导致 /todo-doit 把它错误地当成下一步的"阻塞项"，反复进入"转做其他任务"分支说明，污染后续会话判断。Founder 2026-04-19 明确提出要把此类任务删除。

**How to apply**:
- 写 TODO 条目时，一旦识别出必须由 Founder 在真机 / 模拟器上人工完成的回归 E2E / 验收步骤，就**不要**放进 `- [ ] ...` 清单，而是作为"由 Founder 自行执行，不纳入 AI TODO"的文字说明
- 交付收尾时，代码层 + 静态分析 + 相关单元/集成测试通过即视为 AI 任务完成；不要在"下一步行动"里指向 Founder 真机回归
- 依赖关系（例如"T-I 依赖 Phase 6 真机回归"）要改写，不要留悬挂到已删除的 Founder-gated 任务的指针
- 纯"Founder UX 实测"（产品体验判断，不是 pass-rate 回归）不在此列，保留即可；但若任务描述含"真机回归/regression/E2E/pass 率"，按本条处理
