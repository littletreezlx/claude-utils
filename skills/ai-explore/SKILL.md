---
name: ai-explore
description: >
  Use when the user says "探索应用", "自由探索", "用一下", "explore", "find bugs",
  or after ai-qa-stories passed and deeper exploration is needed. AI role-plays
  as a user to discover bugs and UX issues in a running Flutter app. Supports
  Cyborg mode (Vision + OS Tap + State Oracle triangulation) when Simulator is
  available, and Fallback mode (curl-only). Requires Debug State Server running.
version: 4.0.0
---

# AI Explore — 可证伪的自主质量基础设施

AI 扮演用户自由使用应用。Cyborg 模式下通过**视觉 + 语义事件注入**真正操作 UI，**三证据源三角校验**每一个判断，**A/B/C/D 分级**报告让 Founder 30 秒判定是否值得消费。

## 核心哲学（v4.0 升级自 v3.x）

- **三证据源三角校验 > 单链条证据链** — Interaction（操作命中）/ System（Oracle 状态）/ Surface（截图/语义）三者同时支持才能 A 级，任何一条单独成立即降级
- **Oracle 不是神谕** — 它是三证据源之一，可能自己有 bug；只要表层或 Interaction 与 Oracle 冲突，按"工具疑点"标记
- **会筛选的系统才可信** — 高自毁率 > 高发现率；报告必须包含"候选 X → 证伪 Y → 降级 Z → 高可信 W"的自我否定统计
- **物理约束 > Prompt 规则** — 能在 Debug Server 层卡住的（Generation ID / 2s 硬超时 / /cyborg/reset），就不用自然语言约束 AI
- **persona × strategy 正交** — persona 是风格包装，strategy（Goal-seeking / Boundary-pushing / Misread-first / Impatience / Constraint）才是覆盖模型
- **边界硬卡 > 温柔拒绝** — 审美 / 性能 / 多端 / a11y / 埋点 / 安全明确不处理，错过少量跨维度信号 > 变成垃圾总线
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码
- **不做故事验证** — 那是 `ai-qa-stories` 的职责

---

## 边界白名单（v4.0 新增 — 防职责蔓延的硬卡）

### 本 skill 负责

- 可交互 UI 流程探索
- 由三证据源支撑的功能异常
- 状态机边界异常（连续点击 / 竞态 / 脏状态）

### 本 skill **不负责**（命中即拒绝并路由）

| 维度 | 路由到 |
|------|-------|
| 审美 / 品牌气质 / 情绪感受 | `ui-vision-advance` |
| 单页跨版本一致性 / 设计债 | `ui-vision-check` |
| 性能 / 流畅度 / 帧率主观评价 | **能力空缺**（不要硬塞） |
| 多端一致性 | **能力空缺** |
| 无障碍审计 | `accessibility-expert` agent |
| 文案策略优劣 | `content-marketer` agent |
| 埋点正确性 | **能力空缺** |
| 安全性 | `security-auditor` agent |
| 用户故事回归 | `ai-qa-stories` |

### 中庸措辞（允许）

发现功能异常且疑似与视觉/文案误导相关时，可标注：
> "发现功能异常 X，可能与文案/视觉误导有关（见 Crime Scene 截图），但本 skill 不对审美维度下结论。建议链式调用 ui-vision-advance 独立评审该页。"

这是允许的"跨维度提示"，但 **绝不在本报告里给审美下判断**。

---

## 模式选择（自动判断）

```bash
# 动态发现端口
PORT=$(grep 'static const int port' lib/dev_tools/debug_server.dart | grep -oE '[0-9]+$' | tail -1)

# 检测 Cyborg 模式前置条件
pgrep -x Simulator >/dev/null 2>&1 && \
  curl -s localhost:$PORT/providers >/dev/null 2>&1 && \
  curl -s "localhost:$PORT/cyborg/dom" | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; assert d['totalCount']>0" 2>/dev/null
```

| 条件 | 模式 | 能力 |
|------|------|------|
| Simulator + Debug Server + `/cyborg/dom` 返回节点 | **Cyborg** | 真实交互 + 三证据源三角校验 + Behavioral Fuzzing |
| 仅 Debug Server 可用 | **Fallback** | 端点覆盖测试（A/B/C/D 分级仍适用，但三角校验仅剩 Interaction+System 两条） |

---

## 前置条件

1. ✅ `prep-cyborg-env` 已执行（环境干净，每次探索前必须）
2. Debug State Server 运行中（端口从 `lib/dev_tools/debug_server.dart` 动态发现）
3. 基线数据就绪（可用 group/option 等）
4. Cyborg 额外：iOS Simulator + `/cyborg/dom` 返回节点 + macOS 环境（screencapture）

**严禁脏状态下开始探索** — 三角校验会在矛盾状态下给出错误结论，直接污染 D 级工具错误预算。

---

## Debug Server 契约（v4.0 新增）

本 skill 期望的端点契约。端点不存在则对应能力降级，**在信用摘要页显式标注**。

### 必需端点（缺失即 Fallback）

| 端点 | 契约 |
|------|------|
| `/cyborg/dom` | 返回 `{nodes, totalCount, screenSize, generation}` — **generation 是递增 int，DOM 结构变化时 +1** |
| `/cyborg/tap?nodeId=X&generation=Y` | generation 失配返回 `{ok:false, error:"stale", currentGeneration:N}`；tap 完成前等待 quiet-frame（连续 100ms 无 scheduledFrame），**绝对超时 2000ms 强制返回** `{ok:true, dirty:true}` 防永久挂起 |
| `/state/route` `/state/overlays` `/state/providers` | 基础三样，用于 System Evidence |

### 可选增强端点（实现则升级能力）

| 端点 | 实现后获得 |
|------|----------|
| `/cyborg/reset` | State Teardown，persona 切换时清路由栈 + state 缓存，无需重启 App |
| `/cyborg/dom?interactiveOnly=true` | Token 节省档（默认仍返回全量，以便发现"可见但不可点"的死按钮 bug） |
| `/cyborg/tap?x=&y=` | 坐标注入，用于 Behavioral Fuzzing（Fat-Finger 边缘偏移） |
| `/cyborg/longPress?nodeId=` `/cyborg/input?nodeId=&text=` `/cyborg/scroll?nodeId=&direction=` | 非 tap 交互 |

### 项目侧契约回归测试（推荐）

`test/cyborg_contract_test.dart`：极简 UI（几个 Button + Text）上断言 `/cyborg/dom` 和 `/cyborg/tap` 行为。Flutter 升级只需跑通此测试 + 修 Probe 内部适配，skill 完全无感。

---

## Cyborg 模式执行流程

### Step 0：环境初始化 + 契约健康检查

```bash
# 1. 验证 DOM 返回节点 + generation 字段
curl -s localhost:$PORT/cyborg/dom | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
assert d['totalCount']>0, 'semantics 未启用，重启 App --force-reset'
gen = d.get('generation')
print(f'Nodes: {d[\"totalCount\"]}, generation: {gen if gen is not None else \"[MISSING]\"}')
"

# 2. 探测可选端点（实现状态记入信用摘要）
RESET_OK=$(curl -s -o /dev/null -w '%{http_code}' localhost:$PORT/cyborg/reset)
INT_ONLY_OK=$(curl -s "localhost:$PORT/cyborg/dom?interactiveOnly=true" | python3 -c "import sys,json; print(json.load(sys.stdin).get('ok',False))")
```

**记录本次探索的工具健康状态**，后面信用摘要页要用：
- generation 字段是否存在（不存在 → 无法检测 stale node，分级上限为 B）
- `/cyborg/reset` 是否存在（不存在 → persona 切换需重启 App，探索成本高）

### Step 1：建立 persona × strategy

#### 1a. 动态生成 persona（风格包装）

调用 `/think --quick`（仅文本人设生成不需要多模态），输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要，要求生成 1 个贴合该 App 的用户人设。格式见 v3.x（emoji+名称 / 背景 / 行为倾向 / 自然覆盖 / 使用计划）。

> `/think` 不可用时回退默认：🐣 新手 / ⚡ 效率达人 / 🐒 混乱操作者

#### 1b. 强制选择 strategy（覆盖模型）

**persona 是风格包装，strategy 才是正交覆盖。本轮必须显式选 1 种 strategy**：

| Strategy | 行为规则 | 专攻 |
|----------|---------|------|
| **Goal-seeking** | 按最合理路径尽快完成目标 | 主干流程流畅度 |
| **Boundary-pushing** | 重复点 / 撤销 / 循环跳转 / 在 loading 中操作 | 状态机边界 |
| **Misread-first** | 按最可能的错误理解操作（如把 "取消" 当 "返回"） | 文案/入口误导 |
| **Impatience** | 不等 Oracle 返回、不等动画结束连续操作 | 竞态 / 动画窗口 bug |
| **Constraint** | 低注意力，只看局部 UI 线索不理解全局 | 局部 UI 误解 |

**如何选**：读 `_scratch/ai-explore/coverage-log.md`（不存在则建），选上次运行**未覆盖**的 strategy。连续 5 轮覆盖满 5 种 → 重置循环。

报告开头声明："本轮 persona = XX，strategy = YY，组合未在近 3 轮出现。"

### Step 2：感知-行动-验证（PAV-3T，三角校验循环）

#### P — 感知

```bash
# 查询 DOM，记录 generation
curl -s localhost:$PORT/cyborg/dom > /tmp/dom-$$.json
GEN=$(python3 -c "import json; print(json.load(open('/tmp/dom-$$.json'))['data'].get('generation',0))")
echo "Current DOM generation: $GEN"

# 结合 Oracle 缩小搜索范围
curl -s localhost:$PORT/state/route
curl -s localhost:$PORT/state/overlays
```

#### A — 行动（支持 Behavioral Fuzzing）

**主力：语义节点注入 + generation 校验**

```bash
# 默认 tap
RESP=$(curl -s "localhost:$PORT/cyborg/tap?nodeId=12&generation=$GEN")
echo "$RESP" | python3 -c "
import sys,json
r=json.load(sys.stdin)
if not r['ok'] and r.get('error')=='stale':
    print('⚠️  Stale DOM, current gen=', r.get('currentGeneration'))
    exit(42)  # 强制重取 DOM
print('Tap ok, dirty=', r['data'].get('dirty',False))
"
```

**Behavioral Fuzzing（strategy-specific）**

- **Fat-Finger**（Constraint strategy 可选启用）：用 `?x=&y=` 打在 rect edge 而非 center
  ```bash
  # 计算边缘坐标（rect.x + width*0.9 而非 center.x）
  curl -s "localhost:$PORT/cyborg/tap?x=${EDGE_X}&y=${EDGE_Y}"
  ```
- **Rage-Tap**（Impatience / Boundary-pushing 必备）：同一 nodeId 连发 3 次，不等 Oracle
  ```bash
  for i in 1 2 3; do curl -s "localhost:$PORT/cyborg/tap?nodeId=$ID&generation=$GEN" & done; wait
  ```
- **Amnesia**（Boundary-pushing 可选）：每 3 步调 `/cyborg/reset` 或强制路由回退

#### V — 三角校验（Triangulation）

对每次"可疑"操作（预期发生变化的操作）产生 **3 条独立证据**：

| 证据源 | 采集方式 | 判定异常 |
|-------|---------|---------|
| **Interaction** | tap 响应的 `ok` 和 `dirty` 字段 | ok=false 或 stale error |
| **System** | `/state/route` `/state/overlays` 前后对比 | 预期变化但未变 / 未预期变化出现 |
| **Surface** | 截图 + `/cyborg/dom` label 集合前后对比 | 预期 UI 变化缺失 / 语义节点异常 |

**分级规则**：

| 三证据一致性 | 分级 |
|------------|-----|
| 3/3 都支持"异常存在"且二次复现成功 | **A**（高可信） |
| 2/3 支持异常 | **B**（中可信，归因未闭环） |
| 1/3 支持异常 | **C**（观察项，进盲区不进 bug） |
| 证据相互冲突（如 Oracle 异常但 Surface 正常） | **D**（工具疑点，怀疑 Probe / Oracle 自己） |

### Step 2.5：Crime Scene 双快照（发现 A/B 级候选时）

命中"实际 ≠ 预期"瞬间：

```bash
# 1. 操作前截图（已在 Step 2.P 做过可复用）
SCREENSHOT_DIR="screenshots/cyborg/$(date +%Y-%m-%d)"
mkdir -p "$SCREENSHOT_DIR"
./scripts/screenshot-simulator.sh "$SCREENSHOT_DIR/step_${N}_before.png"

# 2. 在 before.png 上画红框标出即将点击的节点（用 Python PIL）
python3 <<'PY'
from PIL import Image, ImageDraw
import json, os
dom = json.load(open('/tmp/dom-$$.json'))['data']
# 找到目标 nodeId 的 rect
target = next(n for n in dom['nodes'] if n['id'] == TARGET_ID)
r = target['rect']
img = Image.open(f'{os.environ["SCREENSHOT_DIR"]}/step_${N}_before.png')
draw = ImageDraw.Draw(img)
draw.rectangle([r['x'], r['y'], r['x']+r['width'], r['y']+r['height']], outline='red', width=4)
img.save(f'{os.environ["SCREENSHOT_DIR"]}/step_${N}_before_annotated.png')
PY

# 3. 操作
curl -s "localhost:$PORT/cyborg/tap?nodeId=$TARGET_ID&generation=$GEN"

# 4. 操作后截图 + Oracle 快照
./scripts/screenshot-simulator.sh "$SCREENSHOT_DIR/step_${N}_after.png"
curl -s localhost:$PORT/state/route > "$SCREENSHOT_DIR/step_${N}_oracle.json"
```

**Crime Scene 三件套**：
- `step_N_before_annotated.png`（带红框）
- `step_N_after.png`
- `step_N_oracle.json`

Founder 看 before+after 两张图 + 一行 Oracle diff 断言（"预期 route=/detail，实际 /home"），**3 秒判定**是否 bug。

### Step 3：数据恢复 + State Teardown

```bash
# 优先：State Teardown（如 /cyborg/reset 可用）
curl -s localhost:$PORT/cyborg/reset

# 无论是否 reset，最后一轮都要恢复 seed 数据
./scripts/seed-test-data.sh clean
./scripts/seed-test-data.sh
```

### Step 4：A/B/C/D 分级报告

#### 4a. 报告落盘 + 打印

写入 `_scratch/explore-YYYY-MM-DD.md`，同日追加 `## 第 N 次探索`。同时打印到对话。

#### 4b. 报告结构（v4.0）

```markdown
## 探索报告 v4.0

### 🏷️ 信用摘要页（Founder 30秒扫描）

| 指标 | 值 |
|------|---|
| 模式 | Cyborg / Fallback |
| persona × strategy | 🐣 新手小白 × Boundary-pushing |
| 候选问题数 | N |
| 二次复现成功 | M |
| **A 级（高可信）** | X |
| B 级（中可信） | Y |
| C 级（观察项） | Z |
| D 级（工具疑点） | W |
| New / Known-regressed / Known-still-open | a/b/c |
| 工具健康 | DOM generation=✅/❌, /cyborg/reset=✅/❌, Oracle=✅/❌ |
| 本月累计 D 级占比 | 12% ✅（阈值 30%） |

### 🎮 用户体验（人设视角）

#### 🐣 新手小白: [背景故事一句话]
> strategy = Boundary-pushing
> [2-3 段体验描述，只在意外处详写]

### 🐛 技术问题清单（A/B 级必填最小证伪单元）

#### A 级（高可信）

##### A1. [一句话问题描述]
- **触发前提**: 首次进入 /groups 页，存在 ≥2 个 group
- **最小交互序列**:
  1. tap nodeId=12 (label="更多") → `step_3_before_annotated.png`
  2. tap nodeId=18 (label="删除") → `step_4_oracle.json`
- **三证据**:
  - Interaction: ✅ tap ok, dirty=false
  - System: ✅ `/data/groups.count` 从 2 变为 2（未删除）
  - Surface: ✅ UI 仍显示被删 item（见 `step_4_after.png`）
- **预期**: count=1，item 消失
- **实际**: count=2，item 保留
- **已排除的替代解释**:
  - ❌ 非 stale DOM（generation 校验通过）
  - ❌ 非动画中间态（2s 后仍如此）
  - ❌ 非 Oracle 滞后（重取 3 次一致）
- **Crime Scene**: screenshots/cyborg/2026-04-18/step_{3,4}*.png
- **复现**: 2/2

#### B 级（中可信）

##### B1. ...
（同上，但允许"归因未闭环"或"复现 1/2"，列出未排除的替代解释）

#### C 级（观察项，不进 bug 清单）

- **现象**: ...
- **为什么是 C**: 仅 Surface 证据，Oracle 无对应端点
- **人工验证方法**: ...

#### D 级（工具疑点 → 计入错误预算）

- **现象**: ...
- **为什么是 D**: Oracle 说异常但 Surface 完全正常，重取 3 次均不一致
- **怀疑对象**: Debug Server / Probe / skill 自身

### 📊 自我否定统计

- 候选数: 15
- 二次复现失败（已证伪）: 6
- 从 A 降级到 B: 2
- 从 B 降级到 C: 3
- D 级（工具疑点）: 1
- **最终上报 A+B**: 3

### 🔭 盲区观察（C 级，不进 TODO.md）

- [略]

### 💡 跨维度提示（可选，禁止下判断）

- 在 A2 的 Crime Scene 中观察到 [UI 现象]，疑似文案误导。建议后续链式调用 `ui-vision-advance` 独立评审。
```

#### 4c. 工具错误预算追踪

写入 `_scratch/ai-explore/tool-errors/$(date +%Y-%m).md`：

```markdown
# Purpose: 本月 ai-explore 工具误报追踪
# Created: 2026-04-18

## 2026-04-18 第 N 次探索
- 候选: 15, D 级: 1
- 累计本月: 候选 87, D 级 9 = 10.3% ✅
```

超过 30% 阈值 → 报告顶部显著标注："⚠️ 本月误报率 X% 超阈值，建议优先修 Cyborg Probe 而非继续跑探索。"

### Step 4.5：/think 评估（附原始证据）

报告写完后调用 `/think` 做独立视角 sanity check。

**输入契约（v4.0 强化）**：

- **必附**：A/B 级 bug 的完整 Crime Scene 三件套（before_annotated.png + after.png + oracle.json 原文）
- **必附**：工具健康状态、本月误报率
- **不附**：AI 的总结和主观评语

**模式选择**：
- 报告含 A/B 级 Crime Scene → 默认 **dual**（Gemini 多模态看图，GPT 逻辑校验证据链）
- 仅 C 级/纯文本 → `--quick`

**要求 /think 回答**：
1. Oracle 是否可能自己在撒谎？（对每个 A 级）
2. 有没有替代解释未被排除？
3. 本次是新信息还是重复已知问题？（对比 Ignorance Hash）
4. 工具错误预算趋势是否健康？

**Claude Code 最终决策**：/think 是参考意见，Claude Code 综合项目上下文拍板。拿不准的才进 `to-discuss.md`。

### Step 5：分流归档

| 级别 | 归档 |
|------|-----|
| A 级 | `TODO.md`（todo-write skill） |
| B 级 | `TODO.md`，标注"待复现 2/2" |
| C 级 | 留在 `_scratch/explore-*.md` 盲区章节 |
| D 级 | 计入 `_scratch/ai-explore/tool-errors/YYYY-MM.md` |
| `/think` 拿不准的 Founder-level 决策 | `to-discuss.md`（极少数，按 /think skill 契约） |

**Ignorance Hash 更新**：

```bash
# 每个进 TODO.md 的 bug，计算 hash 存入已知集
HASH=$(echo -n "$ROUTE|$NODE_LABEL|$ACTION_TYPE" | shasum -a 256 | cut -c1-16)
echo "$HASH  A1 在 group 页删除不生效" >> _scratch/ai-explore/known-hashes.json
```

下次探索命中 hash → 标 `[SEEN]`，**不进报告正文**，只在自我否定统计里计数。

**绝对禁止（v4.0 沿用）**：
- 把 C 级观察伪装成 A/B 级 bug（缺证据链 → C 就是 C）
- 跳过 /think 直接往 `to-discuss.md` 塞条目
- 从截图脑补因果，在本报告对审美/性能/多端下判断
- TODO.md 与 to-discuss.md 之间设指针

---

## Fallback 模式

Simulator 或 Cyborg Probe 不可用时自动降级。

**诚实声明**：Fallback 下**三角校验只剩 Interaction + System 两条**（无 Surface），分级上限为 **B**。无法覆盖导航流程、手势、动画。

执行流程：Step 0 → Step 1（persona×strategy 仍然强制）→ Step 2 改为 `curl /action/*` + `curl /state/*` → Step 4 报告（A 级条目为 0）→ Step 4.5 /think（用 --quick 即可）→ Step 5 分流。

**Fallback 特别声明（写入报告信用摘要页）**：
- 本次为 Fallback，操作绕过 UI 层不经过确认弹窗不触发动画
- 发现的问题可能是 Debug Server 限制而非真实 bug
- A 级分级自动禁用

---

## 注意事项（v4.0）

1. **单轮 1 persona × 1 strategy** — 用户多次运行覆盖不同 strategy（靠 coverage-log 辅助）
2. **不穷举边界、不跑故事** — 那是 `ai-qa-stories` 的事
3. **nodeId + generation 双重锁** — 默认 generation 校验失败强制重取 DOM，不要靠"每次页面切换后重新查询" 这种自然语言纪律
4. **Crime Scene 是硬证据层** — A/B 级必附三件套，口头描述不算
5. **会删自己的系统才可信** — 自我否定统计必填，不允许 "候选 3 全部 A 级" 这种零筛选输出
6. **超过错误预算立即暂停探索** — 优先修 Probe 再继续
7. **跨维度提示允许，跨维度判断禁止** — 审美/性能只能标"疑似"并路由，不下结论

---

## 变更历史

- **4.0.0** (2026-04-18)：从"会探索"升级为"可证伪的质量基础设施"。引入 GPT-5.4 治理层（A/B/C/D 分级 / 信用摘要 / 最小证伪单元 / 工具错误预算 / persona×strategy / Oracle 非神谕化 / 边界白名单）+ Gemini 机制层（Crime Scene 双快照 / Behavioral Fuzzing / Generation ID / quiet-frame 2s 硬超时 / State Teardown / Ignorance Hash / Probe Contract Test）+ P0 止血（screenshots 路径与 user memory 对齐 / /think 评估附原始 JSON）。事前验尸 P4 被 GPT 证伪为 P1 上游原因，战略顺序改为"可信度治理 → 边界治理 → 探索策略多样化 → 跨版本可持续性"。详见 `~/.claude/docs/decisions/2026-04-18-05-ai-explore-v4-trust-framework.md`。

- **3.2.0** 及更早：Cyborg 基础能力（/cyborg/dom + /cyborg/tap 语义注入 + State Oracle 单链条证据）、PAV 循环、单人设单轮、/think --quick 评估。已被 v4.0 全面吸收并扩展。
