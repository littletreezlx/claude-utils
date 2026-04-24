# 验证卫生详细指引

本文件是全局 CLAUDE.md「铁律 2 / 铁律 5 / 紧急停止机制 / 代码规范」的补充参考。不自动加载到上下文，Claude 在需要深入排障/写流式代码/继承前会话结论时主动读取。

底层框架：**控制面（Control Plane）vs 数据面（Data Plane）**——AI 最常见的失败模式不是"信号缺失"，而是把控制面的成功（握手 / 信令 / 通道建立）当成数据面的成功（业务数据真送达），并把这种虚假成功传递给后续会话或排障决策。

---

## §1 控制面 vs 数据面法则

### 机械化自问

下结论"X 已工作"前，必须自问：
> 我手里这条凭证，是记录了【握手 / 信令 / 状态变化】（控制面），还是记录了【核心业务数据本身】被**最终接收端**确实接收/渲染（数据面）？

### 反面教材（控制面信号，**不可**作 E2E 凭证）

| 类别 | 例子 |
|------|------|
| 网络通道 | `ICE CONNECTED`、`HTTP 200 OK`、`TCP handshake done`、`WebSocket connected` |
| 信令/控制 | `track published`、`subscription confirmed`、`session created` |
| 资源生命周期 | `Camera started`、`MediaProjection granted`、`Foreground service running` |
| 构建/部署 | `build succeeded`、`docker container started`、`pod ready` |
| RPC/API | `request accepted`、`200 OK with empty body` |

这些都只证明**通道开着**，不证明**数据真的从 A 流到 B**。

### 正面凭证（数据面观测，**唯一**可作 E2E 凭证）

| 场景 | 数据面凭证 |
|------|-----------|
| 视频流 | `webrtc-internals` 的 `framesDecoded > 0` 且持续增长 / `videoWidth > 0 && readyState >= 3` / 浏览器渲染出可视画面 |
| 数据写入 | 数据库 SELECT 查到刚写入的具体 ID 和内容 |
| 消息队列 | 消费者侧实际处理了消息（业务副作用发生） |
| API 调用 | 响应体里有具体业务字段，且字段值符合预期 |
| 屏幕渲染 | 用户感知端真出现了预期 UI 元素（截图 / DOM 查询 / a11y 树） |
| 文件 IO | 文件真存在 + 内容 hash 匹配 |

### 经验：今天事故的具体投射

| 错误（控制面冒充） | 正确（数据面） |
|------------------|----------------|
| `Log.i("screen track published")` | `Log.i("first frame captured @ 1280x720, total frames=N")` |
| `dumpsys activity services` 显示 FG 跑着 | `dumpsys media_projection` 有 active session + 有具体 VirtualDisplay |
| Server 端 `track participant published` 日志 | tcpdump 显示 RTP 包大小 >500B（不是 STUN 心跳） |
| 浏览器 `TrackSubscribed` 事件 | `framesDecoded > 0` |

---

## §2 症状伪装识别（跨环境共享原因）

### 触发条件

同一**终点症状**（注意：终点而非表面字符串）在 ≥2 个不同运行环境复现 → 立即反转假设到代码 / 全局配置 / 基础设施。

### 「同一终点症状」的机械识别

不要对比 log 字符串本身，要对比**Terminal Failure**：
> 不管前面经过什么路径，最终的失败结局是不是同一类？

| 表面不同 | 终点相同 |
|---------|---------|
| 环境 A: `readyState=0` | "完全没有可解码视频帧" |
| 环境 B: `bytesReceived=1321` 只够握手 | "完全没有可解码视频帧" |
| 环境 C: ICE FAILED 循环 | "完全没有视频通信" |

→ 全部判定为同一症状（"数据面无有效流"），N=2 时即触发反转。

### 反例（不应触发反转）

不同环境出现真正不同根因的失败：
- 环境 A：编译失败（构造期问题）
- 环境 B：运行时崩溃（运行期问题）
→ 终点不同，不视为同一症状。

### 为什么 N=2 而不是 N=1 或 N=3

- N=1：刚切环境就反转，正当的环境问题（NAT / VPN / 防火墙）会被误判为代码问题，浪费时间在错方向
- N=3：今天事故的成本——前 3 轮都"换环境再说"，到第 4 轮才发现代码 bug，多烧了 2 轮
- N=2 的语义：在 1 个差异极大的环境跨度下复现（如 LAN → 公网云）就反转，环境特异解释概率 < 5%

---

## §3 跨会话信任 + 反向豁免

### 默认怀疑路径

读到 `TODO` / `_scratch` / 前会话总结里出现以下断言时：
- "已验证 X"
- "代码 100% 正确"
- "X 没问题"
- "X 已工作"

→ **默认行为**：检查引用凭证。

| 凭证类型 | 处理 |
|---------|------|
| 数据面硬凭证（具体输出值/帧数/payload） | **100% 信任**，不复验 |
| 控制面凭证（"connected"/"published"/"200 OK"） | 降级为 `[控制面已通 / 数据面待验证]`，本会话踏入该路径时自己跑数据面验证 |
| 无凭证（裸断言） | 视为**假设而非事实**，重新验证 |

### 反向豁免（防过度怀疑）

满足以下**全部**条件时，必须 100% 信任前会话结论，禁止重验（防止 TODO 复用机制被破坏）：

1. 前会话结论附了**数据面硬凭证**（具体变量值 / 终端日志原片段 / UI 截图）
2. 本会话**未修改**该执行路径沿途的代码
3. 路径上没有 `[MOCK_WARNING]` 标签

任一条件不满足，回到默认怀疑路径。

### 经验：今天事故的具体投射

前会话写："**已验证的事实**：代码 100% 没问题：Android SDK 的 publishVideoTrack、simulcast 禁用、**MediaProjection 链路**、DataChannel 全部正常。"

→ 检查凭证：基于 `track published`（控制面），无任何数据面观测（无 framesDecoded / 无 dumpsys media_projection 检查 / 无 tcpdump 包大小分析）。

→ 应降级为 `[控制面已通 / MediaProjection 数据面待验证]`，本会话第一次想踏入"假设代码无 bug"前先做一次数据面验证。

实际发生：本会话信了，导致 1 小时的误诊。

---

## §4 Mock/Stub 毒性继承警告

### 触发场景

AI 在 Session A 为快速推进给某模块写 `return true` / `return MOCK_DATA` 的桩，纪要写"X 模块测试通过"。Session B 在真环境疯狂调试数小时，因为它"在 Session A 已验证正确"。

### 写入规范

涉及 Mock/Stub 的验证凭证记入 `TODO` / `_scratch` 时，**必须**带醒目前缀：

```markdown
[MOCK_WARNING] X 模块在 Mock 下测试通过（见 _scratch/xxx.md），未在真实硬件/网络/依赖下验证
```

### 读取规范

读到 `[MOCK_WARNING]` 标签的结论时，§3 反向豁免立即失效——必须在本会话重验。

### 反向边界

不是所有 Mock 都需要 WARNING：
- 单元测试内部 mock 外部依赖 → 不需要（这是测试的本意）
- **集成路径**上用 Mock 替代真实依赖 → 必须 WARNING
- 用 Mock 验证"真实业务路径已工作" → 必须 WARNING

---

## §5 流式代码活性日志（构造侧）

### 适用范围

任何**流式 / 管道 / 异步**代码路径，包括但不限于：
- 媒体（音视频编解码、采集、推流）
- 消息（事件总线、MQ、WebSocket、SSE）
- 数据流（Pipeline、ETL、Stream API）
- 后台任务（Worker、Coroutine、定时任务）

### 必备日志结构（source 与 sink 两端各一组）

每端必须有 3 类日志：

#### 1. 生命周期事件（Lifecycle）
```
[X] started @ {config}
[X] stopped @ {reason}
```

#### 2. 首次数据信号（First-data marker）
告诉读者"数据真的开始流了"，不是"通道开着但空"。
```
[X] FIRST item received: {summary} @ t={timestamp}
[X] FIRST frame produced: {dims/size} @ t={timestamp}
```

#### 3. 周期计数器（Liveness counter）
固定周期（通常 5s 或 10s）输出累计 + 速率，让 grep 能直接看到"流速"。
```
[X] stats: total={N} rate={M/s} since_last={K} elapsed={T}s
```

### 经验：今天 LiveKitClient.kt 的反例

事故时 `LiveKitClient.kt` 的全部日志（截断前）：
```kotlin
Log.i(TAG, "connected to room ${r.name}")        // 控制面 lifecycle
Log.i(TAG, "screen track published")              // 控制面 lifecycle
// ❌ 无 first frame 信号
// ❌ 无周期统计
// ❌ 无 capture lifecycle
// ❌ 无 encoder output bitrate
```

如果有：
```kotlin
Log.i(TAG, "[Capture] FIRST frame @ ${w}x${h}, t=${t}")
// 周期任务：
Log.i(TAG, "[Capture] stats: frames=$frames rate=$fps/s bitrate=$kbps kbps")
```

→ 30 秒内就会看到 `frames=0` 然后定位到 `startCapture` 没调。

### 反例避免

- ❌ 只在生命周期点打日志（"started"/"stopped"），运行中沉默
- ❌ 日志只在 `error` 路径输出（"无错就无音"，活性不可见）
- ❌ 计数器不带速率（只有 total，看不出"现在还在不在流"）
- ❌ 不同流共享同一 tag（grep 时无法隔离）

### 触发时机

不在 CLAUDE.md 主文设触发，依赖以下机制激活：
- 写代码时 AI 自己识别"这段在做流式 / 异步" → 触发本节
- `feat-done` skill 检查"本次交付的流式代码是否埋了活性日志"
- `code-reviewer` skill 在 review 时核验
- **存量代码债务清理**：`/log-audit` skill（`~/.claude/skills/log-audit/`）项目级 sweep，输出按严重性分级的 TODO 清单

---

## §6 AI 查日志义务（消费侧）

### 默认行为

**禁止无说明地把日志/截图/数值粘贴义务推给用户**。请求用户前必须先穷尽本地可自查的 observability。

### 自查清单（按优先级）

| 来源 | 命令 | 注意 |
|------|------|------|
| 应用日志（Android） | `adb logcat -d -v time \| grep ...` | **filter 必须宽**，包含 SDK 内部 tag、相关系统服务 tag |
| 应用日志（其他 OS） | journalctl / 应用自身 log file | 同上 |
| 系统服务状态 | `dumpsys X` / `systemctl status X` / `ps` | 检查"应该在的进程是否真的在" |
| 网络抓包 | `tcpdump -i any 'port X'` | 包大小分布往往揭示"是否真有数据" |
| 服务端日志 | `docker logs X` / `kubectl logs X` | 双向都要看，不只看一侧 |
| 容器/进程内部状态 | `docker exec` / `kubectl exec` 进入查 | 比远程接口看到的更真 |

### 请求用户的合法情境

仅当满足以下**全部**条件时，才向用户请求：

1. 信号在用户机器上才能取（浏览器 DevTools / 用户感知 UI / 物理操作反馈）
2. 已穷尽自己能查的所有 observability，仍无法定位
3. 请求中显式声明：

> 已查过 X、Y、Z，仍需 W 因为它只能在 ___ 取

### 反例

❌ "请你贴一下 console 输出"（没说自己查过什么）
❌ "你看下浏览器 console" + 完全没跑 logcat / 没看 server log
❌ 一上来就要 webrtc-internals 数值，没先抓包看 RTP 是否到达

### 正例

✅ "Mac 端 tcpdump 显示 server → 浏览器有 length=100 的 RTP 包流入，但 video element `readyState=0`。Server 端 logs 看不到解码侧统计（因为是浏览器侧才知道）。请打开 chrome://webrtc-internals/ 找 inbound-rtp(video) 的 framesDecoded —— 这个数字只能在你的浏览器里取到。"

---

## 附：反仪式性自检

读完本 guide 后自问：
- 我现在的下一步行动会不会因为读了这份 guide 而改变？

如果答案是"不会改变"，说明这次读取是仪式性的（走过场），下次遇到类似场景时应跳过本 guide 直接执行。

累计 3 次"读完无影响"，向 Founder 报告，重新评估本 guide 的归属或措辞。
