---
name: feedback_no_theoretical_problems
description: 不要把 AI 自己生成的理论性问题写入 to-discuss.md，只记录有实际痛点的议题
type: feedback
---

不要把"理论上成立但实际没痛感"的方法论建议写入 to-discuss.md。

**Why:** 用户指出 DRY 降级和文件碎片化两个议题都是 AI 自己生成的理论问题，实际开发中没有真实痛点。flutter_common 里的内容本来就是真正可复用的，文件结构也没有造成 AI 理解困难。

**How to apply:** to-discuss.md 的条目必须由真实的开发痛点驱动（"这次改代码时确实遇到了 X 问题"），而不是从方法论推导出的假设性问题（"理论上 AI 可能会遇到 X"）。如果没有具体的失败案例或阻塞场景，不要提出议题。
