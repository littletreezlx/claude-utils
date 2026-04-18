---
name: cross-session-stacktrace-trust
description: 跨会话继承的"根因已定位"结论必须在当前会话用运行时凭证二次验证——上次捕获的堆栈只证明该位置抛过异常，不证明它是用户症状的根因
type: feedback
originSessionId: bc6667cf-34bb-46eb-af77-5905ecb1e2da
---
跨会话沿用 TODO / 上次 `/state/errors` 捕获的堆栈结论为"根因"，必须在当前会话用**用户症状路径**的 live 运行时证据复核，不得直接据此下药。

**Why**: 2026-04-18 E-1 实战教训。上次会话在 `/state/errors` 里捕获 50 条
`UnmountedRefException` 全指向 `library_viewmodel.dart:71`，TODO 把它记作"E-1
根因已定位"。本次 /todo-doit 按此结论给 LibraryViewModel 加 mounted 守卫后，
运行时复现 library→home 路径——发现首页仍空，`/state/errors` 新冒出一条
**完全不同**的异常：`Tried to modify a provider while the widget tree was
building`，堆栈指向 `HomeViewModel.initialize → _HomePageState.initState`。
Library 的 `UnmountedRefException` 是真实 bug 但**完全不是** E-1 的根因；
两个 bug 在同一探针视野里共存，响亮的那个（50 条刷屏）把安静的那个
（1 条、但路径更致命）掩盖了。如果我不跑运行时验证、直接 commit 凭"E-4
已坐实的根因"，首页空白 bug 会继续存在且下次 AI 仍会错误归因。

**How to apply**:
- 读到 TODO / 前会话总结里的"根因已定位 / 已坐实"时，自动降级为"前会话假设"
- 修复后必须**完整复现用户原症状路径**（本次：tap library → tap home）
  并读 `/state/errors` 的**新条目**（不是旧快照），以及终端消费者状态
  （`/state/home` 的实际数据字段）
- 若首次修复后症状残留，**优先假设"还有第二个根因"**，不要假设"修复不到位"
- `/state/errors` 是环形缓冲，修完重启后应该是空的；重启后出现的新条目
  才是当前代码路径的证据
