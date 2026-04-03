---
description: 测试运行与修复 ultrathink
---

# 测试运行与修复

> 运行项目测试，识别并修复失败用例。

```bash
/test-run              # 运行所有测试
/test-run unit         # 仅单元测试
/test-run e2e          # 仅 E2E 测试
/test-run $ARGUMENTS
```

## 执行

调用 `test-workflow` skill，传入 `$ARGUMENTS` 作为测试范围。
