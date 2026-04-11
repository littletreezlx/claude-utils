---
name: xcode_automation_learning
description: Xcode 自动化构建经验 - 打开后需要等待初始化
type: feedback
originSessionId: 77e9bd2c-d2cb-4c89-9f76-06eb3872a735
---
## Xcode 自动化构建规则

**事实**: `open -a Xcode <workspace>` 是异步启动的，Xcode 需要约 30 秒初始化才能接受 build 命令。

**为什么重要**: 直接在 `open` 后立即执行 `xcodebuild` 会失败或报错，因为 Xcode 还没完全准备好。

**如何应用**: 在 `prep-cyborg-env` 或相关 skill 中，当使用 `open -a Xcode` 启动 Xcode 后，**必须等待 30 秒**再执行 `xcodebuild`。

**例外**: 如果用户已经在 Xcode 中手动打开并等待，则不需要额外等待。
