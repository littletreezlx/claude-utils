---
name: Autonomous Runtime Verification
description: Debug Server verification is default behavior like breathing - never ask user to manually test, never wait for confirmation
type: feedback
---

运行时验证是默认行为，像呼吸一样自然。

**Why:** 用户反复强调 AI 能做的事不要推给用户：
- "模拟器你也可以自己打开啊"
- "这个你也可以自己执行啊"
- "就像呼吸一样是不用多说的"

**How to apply:**
- 项目有 `lib/dev_tools/debug_server.dart` → 改完代码自动 curl 验证，不需要 skill 触发
- 自动启动模拟器、运行 App、轮询等 server ready（不要问"启动了吗"）
- 业务逻辑改动 → `curl /data/` 和 `/action/` 验证
- UI 改动 → `/screen` 截图 + 视觉分析
- 验证失败 → 自己修，不要报给用户等指示
- 只有需要人类判断的事（审美、产品决策）才问用户
