---
description: 红队对抗验证 — 通过语义变异验证测试质量
---

# 红队测试验证

> 通过注入业务逻辑 Bug，验证测试是否真的能抓到问题。

```bash
/test-verify path/to/service.dart          # 验证单文件
/test-verify src/auth/                     # 验证模块
/test-verify                               # 验证本次会话中修改的核心文件
```

## 执行

调用 `test-verify` skill，传入 `$ARGUMENTS` 作为目标路径。

如果未指定路径，从本次会话的 `git diff` 中提取修改的源文件，按 Tier 优先级筛选目标。
