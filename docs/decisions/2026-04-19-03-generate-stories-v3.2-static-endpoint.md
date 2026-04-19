# 2026-04-19-03 generate-stories v3.2：端点静态提取 + 职责边界收紧

## 背景

v3.1 落地后 Founder 继续观察运行实际问题：

> "实际大多项目的 Debug Server 也不完善，generate-stories 这个任务也是会同步检查的是吧？"

我初次回答提议 v3.2 = "三级端点发现（curl `/providers` → 读源码 → 读 CLAUDE.md）"。Founder 立即质疑：

> "可是 Debug Server 源码都在项目内啊，为什么要启动，这是不是做的太重了？"

## 诊断：我之前的 v3.2 方案违反职责边界

v3.1 对"Debug Server 不完善"的处理有漏洞：
- Phase 1 只说"读 CLAUDE.md 端点段"，但 CLAUDE.md 容易过时
- Gate 1 的"端点缺失率 ≤ 30%"数字没有来源
- Phase 4 子 TASK 才实际对账，太晚（batchcc 跑起来才发现全缺 = 浪费子会话）

我最初的 v3.2 提议是加"curl `/providers` 作为优先级 1"，理由是运行时验证更权威。**这个理由错了**：

1. **源码是真相**：`lib/dev_tools/debug_server.dart` 里的 route 注册表等同于 `/providers` 的序列化输出。静态 grep 和运行时 curl 得到同一个清单。
2. **启动 Server 的成本**：AI-Only 下要额外跑 `start-dev.sh`、等待编译、处理失败、清理进程——纯开销。
3. **职责错位**：`/providers` 相比源码唯一多出来的信息是 **SERVER_BUG 检测**（providers 声明但 handler 出 bug）。但这**不是 generate-stories 的职责**——它是 `ai-qa-stories` 的三态对账（MATCH/MISSING/**SERVER_BUG**）负责的，已归因为 `server-handler-bug` 计入工具错误预算。

强行在 generate-stories 做 SERVER_BUG 检测 = 重复劳动 + 违反职责边界。

## 决策

**v3.1 → v3.2：端点静态提取 + 收紧职责边界。**

### Phase 1 加端点静态提取

从 `lib/dev_tools/debug_server.dart`（或项目 CLAUDE.md 指定的路径）用 grep / regex 提取所有 route：

```bash
# 典型模式：'/action/xxx'、'/state/xxx'、'/data/xxx'、'/cyborg/xxx'
grep -oE "'/(action|state|data|cyborg)/[a-zA-Z0-9/_-]+'" lib/dev_tools/debug_server.dart | sort -u
```

三级优先级：
1. **源码 grep**（首选）—— Dart 源码里的 route 注册表
2. **CLAUDE.md 端点段**（回退）—— 如果源码结构不易解析
3. **都不可得**（降级）—— digest 标"端点未知"，**Gate 1 直接触发**

端点清单附进 `digest.md` 的"可用端点清单"章节（紧凑格式分类：action / state / data / cyborg）。

### Phase 2 加端点预对账

每条候选 Story 估算需要的端点（基于 Story 意图），与 Phase 1 清单比对：

```markdown
## 端点预对账

| Story | 预计端点 | 实际状态 | 缺失 |
|-------|---------|---------|-----|
| 01 首次使用 | /action/auth/login, /state/auth, /data/profile | ✅ ✅ ✅ | 0 |
| 05 分享 | /action/share/upload | ⏭️ MISSING | 1 |
| ... | | | |

总预计端点数: N
缺失数: M
**缺失率: M/N = X%**
```

产出到 `.task-generate-stories/behavior-audit.md` 末尾。

### Gate 1 自检扩展

| 自查项 | 达标条件 | v3.2 变化 |
|--------|---------|----------|
| 覆盖率 | ≥ 85% | 不变 |
| 落选归因 | 100% 有明确理由 | 不变 |
| **端点信息来源** | ✅ 源码 或 ✅ CLAUDE.md（不允许完全不可得）| **新增** |
| **端点缺失率** | ≤ 30% | 原有，但数字来源改为 Phase 2 预对账 |
| 产品优先级分叉 | 无 | 不变 |

任一不达标 → 只弹出相关分叉问 Founder。

### 职责边界（新增章节）

**generate-stories 负责**：
- 提取代码里**声明**的端点（静态 grep）
- 判断候选 Story 预计需要的端点是否在清单里
- 生成的 QA 中，缺失端点标 `# TODO: 缺少端点 <name>`

**generate-stories 不负责**：
- 启动 Debug Server
- 运行时 curl `/providers` 验证
- **SERVER_BUG 检测**（handler 声明存在但返回 `Unknown state/action`）—— 这是 `ai-qa-stories` 三态对账的职责，归因 `server-handler-bug` 计入工具错误预算

这条边界写进 SKILL.md 约束章节，避免将来再被带偏重复造轮子。

## 不选"启动 Server"方案的完整理由

- **信息等价性**：静态 grep 和 `/providers` 输出等价（都来自同一 route 注册表）
- **成本**：启动 Server 需要编译 Flutter app + 处理启动失败 + 进程清理，纯开销
- **职责重叠**：运行时额外能提供的只有 SERVER_BUG 检测，而这是 ai-qa-stories 的职责
- **AI-Only 协作模式**：多一个"启动服务"步骤 = 多一个失败点

## 风险与反面检验

- **源码 grep 正则可能遗漏非标准 route 写法**：缓解——首次运行后手动抽查，发现遗漏模式补正则。
- **CLAUDE.md 降级路径可能过时**：接受——如果项目 CLAUDE.md 端点清单已过时，说明文档腐烂，Gate 1 触发让 Founder 知道问题在哪（"端点信息来源降级到 CLAUDE.md，请确认是否过时"）。
- **Phase 2 预对账准确性依赖 AI 对 Story 意图的判断**：这是可接受的估算，不是严格保证。即使漏估或过估，Phase 4 子 TASK 实际编译 QA 时还会对账一次，产出的 QA 本身是准的。预对账的价值是**提前暴露大面积缺失**，不是精确计数。

## 回滚条件

3 个月内观察到：
- 源码 grep 误判率 > 20%（漏抓或错抓） → 改为更复杂的 AST 解析或加项目级配置
- Phase 2 预对账与 Phase 4 实际对账差异 > 30% → 预对账无价值，移除

## 联动影响

- **ai-qa-stories v2.5**：三态对账 MATCH/MISSING/SERVER_BUG 继续生效，generate-stories 和它形成完整分工
- **Gate 1 v3.2 条件**：Debug Server 完全不可知时 Gate 必触发，这是对"项目文档腐烂"的硬卡
- **Debug Server 源码路径灵活**：不同项目可能叫 `lib/dev_tools/debug_server.dart` 或 `lib/debug/server.dart`，SKILL.md 里给降级查找策略（`grep -rE "class DebugServer" lib/`）

## 参考

- 前置决策链：`2026-04-19-01`（v3.0 真 DAG）→ `2026-04-19-02`（v3.1 digest 梯度）→ 本次
- 联动 skill：`ai-qa-stories` SKILL.md § 端点对账三态判定
- 触发对话：Founder 连续两轮质询（"Debug Server 不完善怎么办" → "为什么要启动，太重了"）
