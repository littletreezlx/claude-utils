---
name: self_verification_ability
description: AI must self-verify without manual testing
type: feedback
originSessionId: 44c8c984-eb04-4404-9bc9-6444311a3ebb
---
## 规则：加强 AI 自闭环能力，禁止依赖人工手动测试

**Why:** 每次让用户手动测试会中断流程、浪费时间，降低 AI 独立作战能力。

**How to apply:**
- 代码修改后：优先用单元测试、类型检查、Schema 验证等代码级手段自验
- 运行时验证：尽量写自动化测试脚本或 mock 验证，不依赖人工 curl
- 服务启动失败：优先排查和修复，而不是标记"需人工"
- 遇到阻塞：先分析根本原因，尝试多种路径解决，实在不行才升级

**本 session 教训：** Gemma 分段修复明明可以用 Schema 验证 + splitContent 模拟验证，却因为服务启动有个 pre-existing bug 就放弃，等用户说"你确定你自己做不到吗"才去想办法做代码级验证。
