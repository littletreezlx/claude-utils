---
name: godot-explore
description: >
  Use when the user says "探索游戏", "自由探索", "用一下", "explore", "playtest",
  or after godot-qa-stories passed and deeper exploration is needed. AI
  role-plays as a player to discover bugs and UX issues via DebugPlayServer.
  Single mode: curl-driven exploration with Probe-provided screenshots as
  Surface evidence. Requires DebugPlayServer embedded in the game.
version: 4.0.0
---

# Godot Explore — 可证伪的自主质量基础设施（Godot 适配版）

AI 扮演玩家自由游玩游戏。通过 DebugPlayServer 36+ 个端点驱动操作,Probe 自带截图作为视觉证据,**双证据源校验**(System + Surface) 每一个判断,**A/B/C/D 分级**报告让 Founder 30 秒判定是否值得消费。

## 核心哲学（v4.0 升级自 v3.x）

- **双证据源校验 > 单链条证据链** — System (`/state/*` + `/debug/events`) / Surface (`/screenshot/<name>` PNG + 像素 diff) 两源同时支持才能 B 级,任何一条单独成立即降级为 C；A 级实质罕见(见下方分级段说明)
- **Oracle 不是神谕** — `/state/*` 是证据源之一,可能自己有 bug；只要 Surface 与 Oracle 冲突,按"工具疑点"标记
- **会筛选的系统才可信** — 高自毁率 > 高发现率；报告必须包含"候选 X → 证伪 Y → 降级 Z → 高可信 W"的自我否定统计
- **物理约束 > Prompt 规则** — 能在 DebugPlayServer 层卡住的(单任务锁 / 截图直连 viewport),就不用自然语言约束 AI
- **persona × strategy 正交** — persona 是风格包装,strategy(Goal-seeking / Boundary-pushing / Misread-first / Impatience / Constraint)才是覆盖模型
- **边界硬卡 > 温柔拒绝** — 审美 / 性能 / 多端 / a11y / 埋点 / 安全明确不处理,错过少量跨维度信号 > 变成垃圾总线
- **决策时是玩家,报告时是工程师** — 用人设决定操作顺序,但报告问题必须走证据链
- **只记录,不修复** — 发现问题记到报告,不在探索中改代码
- **不做故事验证** — 那是 `godot-qa-stories` 的职责

---

## 边界白名单（v4.0 新增 — 防职责蔓延的硬卡）

### 本 skill 负责

- 可交互游戏流程探索(导航 / 战斗 / 经济 / UI 切换)
- 由双证据源支撑的功能异常
- 状态机边界异常(连续操作 / 竞态 / 脏存档)
- Godot 特有的崩溃 / 错误日志(通过 `/debug/crash_log` 读取,属 System Evidence)

### 本 skill **不负责**(命中即拒绝并路由)

| 维度 | 路由到 |
|------|-------|
| 审美 / 品牌气质 / 视觉氛围 | `game-ui-advance` / `ui-vision-advance` |
| 单页跨版本一致性 / 设计债 | `ui-vision-check` |
| 帧率 / 性能 / 流畅度主观评价 | **能力空缺**(不要硬塞) |
| 数值平衡 / 难度曲线 | **能力空缺**(产品负责人决策) |
| 无障碍审计 | `accessibility-expert` agent |
| 文案策略优劣 | `content-marketer` agent |
| 安全性 | `security-auditor` agent |
| 用户故事回归 | `godot-qa-stories` |

### 中庸措辞(允许)

发现功能异常且疑似与视觉/文案误导相关时,可标注:
> "发现功能异常 X,可能与 UI 文案误导有关(见 Crime Scene 截图),但本 skill 不对审美维度下结论。建议链式调用 `game-ui-advance` 独立评审该界面。"

跨维度提示允许,**绝不在本报告里给审美下判断**。

---

## 模式说明(单一模式 — 无独立 Cyborg)

### 唯一模式: curl 主链 + Probe 自带截图

- **Action**: 永远通过 DebugPlayServer 的 `/play/*` POST 端点(36+ 个端点覆盖导航/战斗/经济/UI 显示)
- **Surface 视觉证据**: 通过 `/screenshot` `/screenshot/<name>` 端点直接获取 PNG(Probe 内部调用 Godot Viewport 截图,**平台无关**;WSL/Linux 需 Xvfb 虚拟显示器,见 Step 0a)
- **Surface 路由证据(强信号)**: **每个响应自动附带 `_scene` 字段**(DebugPlayServer.gd 已实装,`_handle_async` 在每个 result 上挂当前场景文件名)。route diff 直接读 JSON `_scene`,**不需要新端点也不需要 `/scene_tree`**
- **System 证据**: `/state/game` `/state/save` `/state/battle` `/state/commander` `/state/units` + `/debug/events` 结构化日志 + `/debug/crash_log`

### 为何不存在独立的 "Cyborg 视觉+点击" 模式

- **OS tap 在 WSL 不可达**: cliclick 是 macOS 专属,Linux/WSL 无对应替代
- **Godot 无 DOM 等价物**: 没有 `nodeId` / `bounds` / `generation` 概念,即使 macOS 下加 cliclick,也无法精准定位"点哪个按钮",只能盲点坐标
- **DebugPlayServer 端点已覆盖所有 UI 操作**: `/play/show_settings` `/play/show_tavern` `/play/select_commander` `/play/deploy_unit` 等已经把 UI 交互形式化为 HTTP 接口,坐标级 tap 是冗余

> WSL2 下用 Xvfb 启动 Godot,DebugPlayServer 端点全部可达,Probe 截图依赖 GL Compatibility 渲染器(项目当前选用)在 Xvfb 下渲染 — Step 0b 健康检查会验证截图是否非黑。

---

## DebugPlayServer 契约(v4.0 新增)

本 skill 期望的端点契约。端点不存在则对应能力降级,**在信用摘要页显式标注**。

### 必需端点(缺失即拒绝执行)

| 端点 | 契约 |
|------|------|
| `GET /ping` | Server 可达性 |
| `GET /state/game` | 经济/进度状态 — System Evidence |
| `GET /state/save` | 存档数据 |
| `GET /screenshot` `GET /screenshot/<name>` | Probe 内部 Viewport 截图,返回 `{name, path}` — Surface Evidence |
| 至少 1 个 `POST /play/*` | 否则无任何动作面 |

### 可选增强端点(实现则升级能力)

| 端点 | 实现后获得 |
|------|----------|
| `GET /state/battle` `GET /state/units` `GET /state/commander` | 战斗/单位/指挥官细粒度 System Evidence |
| `GET /debug/events?tag=xxx` | 结构化事件流(信号触发/状态转换/经济操作/伤害计算)— System Evidence 强信号 |
| `GET /debug/events/summary` | 事件摘要统计 |
| `GET /debug/crash_log` | 崩溃日志 — A 级证据(项目侧 ErrorRecorder 实装) |
| `GET /scene_tree` | 完整场景树 dump — 用于深度调试,日常 route diff 用响应里的 `_scene` 字段就够 |
| `POST /screenshots/capture_all` | 一键多场景截图(覆盖率验证用) |
| `POST /play/save_reset` | State Teardown,无需重启游戏(已实装) |
| `POST /time_scale` | 加速测试用,Impatience strategy 必备 |

### 项目侧契约示例(barracks-clash 现状)

已实装端点(36 个):
```
/ping
/state/game     /state/save     /state/battle    /state/commander    /state/units
/screenshot     /screenshot/{name}     /screenshots/capture_all
/scene_tree
/play/goto_menu     /play/goto_camp     /play/goto_battle     /play/goto_world_map
/play/show_settings     /play/show_tavern     /play/show_blacksmith
/play/show_command_tent     /play/show_settlement
/play/select_commander    /play/confirm_commander
/play/deploy_unit    /play/start_battle    /play/skip_wave    /play/kill_all_enemies
/play/wait_battle_end
/play/blacksmith_upgrade    /play/add_gold    /play/add_gems
/play/save_reset
/time_scale
/debug/events    /debug/events/summary    /debug/crash_log    /debug/clear_events
```

> 端点覆盖度极高,实质上 godot-explore 的 Fallback 等价于 ai-explore 的 Cyborg 上限——所以不存在"降级 Fallback"概念。

---

## 前置条件

1. **DebugPlayServer 可达** — Step 0 自动检测,不可达则报错并退出(脏状态禁行)
2. **端口动态发现** — 从 `Core/Autoloads/DebugPlayServer.gd` 读 `const PORT`(当前为 9999)
3. **基线数据就绪** — 有可用存档/关卡进度。基线不足时,只做最小 seed;想验证 stories 的用户应调用 `/godot-qa-stories`

**严禁脏状态下开始探索** — 双证据校验会在矛盾状态下给出错误结论,直接污染 D 级工具错误预算。

---

## 执行流程

### Step 0:环境初始化 + 契约健康检查

#### 0a. 端口发现 + 可达性 + Xvfb 自启(WSL/Linux)

```bash
PORT=$(grep -E '^const PORT' Core/Autoloads/DebugPlayServer.gd | grep -oE '[0-9]+' | head -1)
[ -z "$PORT" ] && { echo "PORT 常量未找到"; exit 1; }

# 可达性
curl -s -m 3 localhost:$PORT/ping >/dev/null 2>&1 && echo "DebugPlayServer 已就绪"
```

**Server 不可达时的启动流程**(注意:**严禁用 sleep** — game-mvp `踩坑记录` 已 codify "sleep 会被 pre-tool-call hook 拦截"。改用 Bash 工具的 `run_in_background:true` 配合等通知机制):

```bash
# 检测平台
if grep -qi microsoft /proc/version 2>/dev/null || \
   ([ "$(uname -s)" = "Linux" ] && [ -z "$DISPLAY" ]); then
  # WSL2 / Linux → Xvfb 路径(2026-04-26 实测可行)
  command -v Xvfb >/dev/null || { echo "需先 apt install xvfb"; exit 1; }
  pgrep -x Xvfb >/dev/null || Xvfb :99 -screen 0 1152x648x24 &  # 后台
  export DISPLAY=:99
fi
# 启动 Godot — 必须用 Bash 工具的 run_in_background:true,等通知再 ping
godot --path . &  # 占位写法,实际通过 Bash(run_in_background:true) 调用
```

**Bash 工具调用规约**(对齐 godot-qa-stories 进程管理段):
1. Xvfb 启动:用 Bash(run_in_background:true) 跑 `pgrep -x Xvfb >/dev/null || Xvfb :99 -screen 0 1152x648x24` — Xvfb 启动 < 100ms,不需要等
2. Godot 启动:用 Bash(run_in_background:true) 跑 `DISPLAY=:99 "$GODOT_BIN" --path "$PWD"` — 等 Claude Code 的"后台命令完成"通知
3. 收到通知后单次 `curl localhost:$PORT/ping` — 无需轮询

**落地规则**:
- **WSL/Linux 自启 Xvfb + Godot**: 本 skill 自己起,无需用户介入
- **macOS / 桌面 Linux 不自启**: 用户期望自己控制游戏窗口,skill 仅检测 + 报错指引(`/Applications/Godot.app/Contents/MacOS/Godot --path . &`)
- Godot 启动后 ping 仍 404/超时 → 明确报告失败原因(Xvfb 未装 / GL 上下文错 / 项目路径不对),**不进入探索**(脏状态禁行)

#### 0b. 契约健康检查

```bash
# 1. 列必需端点
for ep in /state/game /state/save /screenshot; do
  curl -s -m 2 -o /dev/null -w "%{http_code} $ep\n" localhost:$PORT$ep
done

# 2. 测可选端点(记入信用摘要)
EVENTS_OK=$(curl -s -m 2 -o /dev/null -w '%{http_code}' localhost:$PORT/debug/events)
CRASH_OK=$(curl -s -m 2 -o /dev/null -w '%{http_code}' localhost:$PORT/debug/crash_log)
RESET_OK=$(curl -s -m 2 -o /dev/null -w '%{http_code}' -X POST localhost:$PORT/play/save_reset)

# 3. 截图健康(Probe 内部 Viewport 是否真在工作 + 是否非黑图)
curl -s -m 5 localhost:$PORT/screenshot/health_check > /tmp/godot_health.json
SCREENSHOT_PATH=$(python3 -c "import json; print(json.load(open('/tmp/godot_health.json')).get('path',''))")
if [ -z "$SCREENSHOT_PATH" ]; then
  echo "⚠️ /screenshot 端点返回为空,Surface 视觉证据降级"
else
  # WSL2 + Xvfb 下 GL 可能渲染黑图,必须验证非全黑
  PNG_BYTES=$(stat -c%s "$SCREENSHOT_PATH" 2>/dev/null || stat -f%z "$SCREENSHOT_PATH" 2>/dev/null)
  python3 -c "
from PIL import Image
img = Image.open('$SCREENSHOT_PATH').convert('RGB')
pixels = list(img.getdata())
non_black = sum(1 for r,g,b in pixels if r+g+b > 30) / len(pixels)
print(f'screenshot: {non_black*100:.1f}% non-black')
assert non_black > 0.05, 'screenshot is essentially all black — Xvfb GL context broken or game in transition'
" || echo "⚠️ Probe 截图全黑,Surface 视觉证据失效,分级上限降为 B(仅 System+_scene)"
fi
```

**记录本次探索的工具健康状态**(信用摘要页要用):
- `/screenshot` 是否返回非空 path 且非全黑 → 全黑则 Surface 视觉证据失效,但 `_scene` 路由证据仍有效
- `/debug/events` 是否可读 → 不可读则 System 证据降级(只剩 `/state/*`)
- `/debug/crash_log` 是否可读 → 不可读则崩溃捕获降级
- `/play/save_reset` 是否可调 → 不可则 State Teardown 退化为提醒用户手动改存档

### Step 1:建立 persona × strategy

#### 1a. 动态生成 persona(风格包装)

调用 `/think --quick`(仅文本人设生成不需要多模态),输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要,要求生成 1 个贴合该游戏的玩家人设。格式:emoji+名称 / 背景 / 行为倾向 / 自然覆盖 / 游玩计划。

> `/think` 不可用时回退默认:🐣 新手小白 / 💰 经济运营玩家 / ⚡ 速攻玩家 / 🌱 养成玩家 / 🐒 混乱操作者

#### 1b. 强制选择 strategy(覆盖模型)

**persona 是风格包装,strategy 才是正交覆盖。本轮必须显式选 1 种 strategy**:

| Strategy | 行为规则 | 专攻 |
|----------|---------|------|
| **Goal-seeking** | 按最合理路径尽快推关 | 主干流程流畅度 |
| **Boundary-pushing** | 同一界面反复进退 / 部署同一格子多次 / 战斗中切场景 | 状态机边界 |
| **Misread-first** | 按最可能的错误理解操作(如把"撤退"当"暂停") | 文案/入口误导 |
| **Impatience** | `time_scale=8` + 不等 `wait_battle_end` 直接连发下一关 | 竞态 / 异步 bug |
| **Constraint** | 低注意力,只看局部 UI 线索(如只看金币不看人口) | 局部 UI 误解 |

**如何选**:读 `_scratch/godot-explore/coverage-log.md`(不存在则建),选上次运行**未覆盖**的 strategy。连续 5 轮覆盖满 5 种 → 重置循环。

报告开头声明:"本轮 persona = XX,strategy = YY,组合未在近 3 轮出现。"

### Step 2:感知-行动-验证(PAV-2T,双证据校验循环)

#### P — 感知

```bash
# 1. System 状态(每个响应自动附带 `_scene` 路由字段)
RESP=$(curl -s localhost:$PORT/state/game)
echo "$RESP" > /tmp/state_${N}_before.json
SCENE_BEFORE=$(echo "$RESP" | python3 -c "import sys,json; print(json.load(sys.stdin).get('_scene',''))")

curl -s localhost:$PORT/state/battle   > /tmp/battle_${N}_before.json   # 战斗中
curl -s localhost:$PORT/debug/events?tag=signal > /tmp/events_${N}_before.json

# 2. Surface 截图(Probe 内部 Viewport,Step 0b 已确认非黑)
curl -s localhost:$PORT/screenshot/step_${N}_before > /tmp/screenshot_${N}.json
SCREEN_BEFORE=$(python3 -c "import json; print(json.load(open('/tmp/screenshot_${N}.json'))['path'])")
```

> Probe 截图保存在 `res://screenshots/`,JSON 返回的 path 是绝对路径。Read 工具直接打开做视觉判断。
> `_scene` 字段是路由 diff 的强信号 — Step 2.V 用 `$SCENE_BEFORE` vs `$SCENE_AFTER` 判断场景切换是否如预期。

#### A — 行动(人设驱动)

**主力:DebugPlayServer 端点**

```bash
# 导航
curl -s -X POST localhost:$PORT/play/goto_camp
curl -s -X POST localhost:$PORT/play/goto_battle -d '{"level":1}'

# 战斗
curl -s -X POST localhost:$PORT/play/confirm_commander
curl -s -X POST localhost:$PORT/play/deploy_unit -d '{"unit_index":0,"grid_x":3,"grid_y":10}'
curl -s -X POST localhost:$PORT/play/start_battle -d '{"speed":8}'
curl -s    localhost:$PORT/play/wait_battle_end

# UI 切换
curl -s -X POST localhost:$PORT/play/show_tavern
curl -s -X POST localhost:$PORT/play/show_blacksmith

# 经济(谨慎使用 — 调试类操作破坏真实体验)
curl -s -X POST localhost:$PORT/play/add_gold -d '{"amount":500}'
```

**Strategy-specific 仅保留 Amnesia**(其他 Behavioral Fuzzing 因无 OS tap 砍掉):

- **Amnesia**(Boundary-pushing 可选):每 3 步 `curl -X POST .../play/save_reset` 强制清存档,验证全流程冷启动是否一致
- **Speed-up**(Impatience 必备):`curl -X POST .../time_scale -d '{"scale":8}'`,不等动画结束连续操作

**禁用**(Godot 不适用):
- ~~Fat-Finger~~ — 无 nodeId / bounds 可偏移
- ~~Rage-Tap~~ — curl 端点本身已经是单任务锁,连发会被 429
- 调试类操作(add_gold/add_gems/skip_wave)新手/速攻人设不该用;经济/养成人设也应尽量少用

#### V — 双证据校验(Triangulation 缩水版)

对每次"可疑"操作(预期发生变化的操作)产生 **2 条独立证据**:

| 证据源 | 采集方式 | 判定异常 |
|-------|---------|---------|
| **System** | `/state/*` 前后 diff + `_scene` 字段 route diff + `/debug/events?tag=xxx` 新增条目 + `/debug/crash_log` 新增 | 预期变化但未变 / 未预期事件 / `_scene` 未切换 / 出现错误日志 |
| **Surface** | `/screenshot/step_N_after` PNG + 像素级对比 | 预期 UI 变化缺失 / 截图全黑 / 视觉与 `_scene` 矛盾 |

**分级规则(双证据缩水版)**:

| 证据一致性 | 分级 |
|------------|-----|
| 2/2 都支持"异常存在" + 复现 2/2 + `/debug/crash_log` 有对应崩溃栈 | **A**(高可信,实质罕见 — 因 Godot 不抛 crash 时 A 级几乎只能是 B) |
| 2/2 都支持"异常存在"且二次复现成功 | **B**(中可信,标准上报标准) |
| 1/2 支持异常 | **C**(观察项,进盲区不进 bug) |
| 证据相互冲突(如 Oracle 异常但截图正常) | **D**(工具疑点,怀疑 DebugPlayServer 自身) |

> **A 级实质罕见声明**:相比 ai-explore 的三证据(Interaction/System/Surface),Godot 缺少独立的 Interaction 证据源(curl HTTP 200 不代表真实操作命中),且无 nodeId stale 校验。因此除非伴随 `/debug/crash_log` 新增崩溃栈,大部分异常上限为 B。这是已知降级,不是缺陷。

### Step 2.5:Crime Scene 双快照(发现 B 级及以上候选时)

命中"实际 ≠ 预期"瞬间:

```bash
SCREENSHOT_DIR="screenshots/godot-explore/$(date +%Y-%m-%d)"
mkdir -p "$SCREENSHOT_DIR"

# 1. 操作前截图(已在 Step 2.P 做过,直接复用)
cp "$SCREEN_BEFORE" "$SCREENSHOT_DIR/step_${N}_before.png"

# 2. 操作
curl -s -X POST localhost:$PORT/play/<action>

# 3. 操作后截图 + Oracle 快照 + 事件 diff
curl -s localhost:$PORT/screenshot/step_${N}_after > /tmp/after.json
SCREEN_AFTER=$(python3 -c "import json; print(json.load(open('/tmp/after.json'))['path'])")
cp "$SCREEN_AFTER" "$SCREENSHOT_DIR/step_${N}_after.png"

curl -s localhost:$PORT/state/game > "$SCREENSHOT_DIR/step_${N}_oracle.json"
curl -s "localhost:$PORT/debug/events?tag=signal" > "$SCREENSHOT_DIR/step_${N}_events.json"
curl -s localhost:$PORT/debug/crash_log > "$SCREENSHOT_DIR/step_${N}_crash.json"
```

**Crime Scene 三件套(Godot 缩水版,无红框标注 — 因无 nodeId/bounds 可标)**:
- `step_N_before.png`(原始截图)
- `step_N_after.png`(原始截图)
- `step_N_oracle.json` + `step_N_events.json` + `step_N_crash.json`(三合一 System 证据)

Founder 看 before+after 两张图 + Oracle/events diff + crash 状态,**3-5 秒判定**是否 bug。

### Step 3:数据恢复 + State Teardown

```bash
# 优先:save_reset(已实装)
curl -s -X POST localhost:$PORT/play/save_reset

# 无 save_reset 时降级:提醒用户手动恢复存档
echo "save_reset 不可用,用户存档已被本次探索修改 — 请手动还原"
```

### Step 4:A/B/C/D 分级报告

#### 4a. 报告落盘 + 打印

写入 `_scratch/godot-explore/explore-YYYY-MM-DD.md`,同日追加 `## 第 N 次探索`。同时打印到对话。

#### 4b. 报告结构(v4.0)

```markdown
## 探索报告 v4.0

### 🏷️ 信用摘要页(Founder 30 秒扫描)

| 指标 | 值 |
|------|---|
| 模式 | curl 主链 + Probe 自带截图(单一模式,无 Cyborg) |
| 端口 | 9999 |
| persona × strategy | 🐣 新手小白 × Boundary-pushing |
| 候选问题数 | N |
| 二次复现成功 | M |
| **A 级(高可信,需伴 crash 栈)** | X |
| B 级(中可信,标准上报) | Y |
| C 级(观察项) | Z |
| D 级(工具疑点) | W |
| New / Known-regressed / Known-still-open | a/b/c |
| 工具健康 | screenshot=✅/❌, debug/events=✅/❌, crash_log=✅/❌, save_reset=✅/❌ |
| 本月累计 D 级占比 | 12% ✅(阈值 30%) |

### 🎮 玩家体验(人设视角)

#### 🐣 新手小白: [背景故事一句话]
> strategy = Boundary-pushing
> [2-3 段体验描述,只在意外处详写]

### 🐛 技术问题清单(B 级及以上必填最小证伪单元)

#### A 级(高可信 — 罕见,需伴 crash)

##### A1. [一句话问题描述]
- **触发前提**: 关卡 1 第 3 波结束后,血量 ≤ 0 的指挥官在结算页
- **最小操作序列**:
  1. `POST /play/start_battle {"speed":8}` → `step_3_before.png`
  2. `GET /play/wait_battle_end` → `step_4_oracle.json`
- **双证据 + 崩溃栈**:
  - System: ✅ `/state/battle.phase` 从 `combat` 变为 `crashed`(预期 `settled`)
  - Surface: ✅ 截图显示黑屏 + 错误覆盖层(见 `step_4_after.png`)
  - **Crash**: ✅ `/debug/crash_log` 含 `Invalid get index 'commander' on null instance` at `BattleSettlement.gd:42`
- **预期**: 进入结算页,显示金币奖励
- **实际**: 黑屏 + null 引用崩溃
- **已排除的替代解释**:
  - ❌ 非 Probe 故障(其他端点正常响应)
  - ❌ 非偶发(2/2 复现)
- **Crime Scene**: screenshots/godot-explore/2026-04-26/step_{3,4}*.{png,json}
- **复现**: 2/2

#### B 级(中可信 — 标准上报)

##### B1. [一句话问题描述]
- **触发前提**: ...
- **最小操作序列**: ...
- **双证据**:
  - System: ✅ `/state/game.gold` 预期 +50 实际 +0
  - Surface: ✅ 截图金币数字未变(见 `step_5_after.png`)
- **未排除的替代解释**:
  - ⚠️ 可能是经济端点单任务锁延迟,需重跑确认
- **复现**: 1/2

#### C 级(观察项,不进 bug 清单)

- **现象**: ...
- **为什么是 C**: 仅 Surface 截图疑似异常,`/state/*` 无对应字段佐证
- **人工验证方法**: ...

#### D 级(工具疑点 → 计入错误预算)

- **现象**: ...
- **为什么是 D**: `/state/battle.phase=combat` 但 `/screenshot` 显示已结算,重取 3 次均不一致
- **怀疑对象**: DebugPlayServer / Probe 截图竞态 / skill 自身

### 📊 自我否定统计

- 候选数: 15
- 二次复现失败(已证伪): 6
- 从 B 降级到 C: 3
- D 级(工具疑点): 1
- **最终上报 A+B**: 5

### 🔭 盲区观察(C 级,不进 TODO.md)

- [略]

### 💡 跨维度提示(可选,禁止下判断)

- 在 B2 的 Crime Scene 中观察到 [UI 现象],疑似文案误导。建议后续链式调用 `game-ui-advance` 独立评审。
```

#### 4c. 工具错误预算追踪

写入 `_scratch/godot-explore/tool-errors/$(date +%Y-%m).md`:

```markdown
# Purpose: 本月 godot-explore 工具误报追踪
# Created: 2026-04-26

## 2026-04-26 第 N 次探索
- 候选: 15, D 级: 1
- 累计本月: 候选 87, D 级 9 = 10.3% ✅
```

超过 30% 阈值 → 报告顶部显著标注:"⚠️ 本月误报率 X% 超阈值,建议优先修 DebugPlayServer / Probe 截图链路而非继续跑探索。"

### Step 4.5:/think 评估(附原始证据)

报告写完后调用 `/think` 做独立视角 sanity check。

**输入契约(v4.0 强化)**:

- **必附**:A/B 级 bug 的完整 Crime Scene 三件套(before.png + after.png + oracle/events/crash 三合一 JSON 原文)
- **必附**:工具健康状态、本月误报率、Probe 截图是否真在工作
- **不附**:AI 的总结和主观评语

**模式选择**:
- 报告含 A/B 级 Crime Scene → 默认 **dual**(Gemini 多模态看截图,GPT 逻辑校验证据链 + crash 栈)
- 仅 C 级/纯文本 → `--quick`

**要求 /think 回答**:
1. Oracle 是否可能自己在撒谎?(对每个 A/B 级)
2. 有没有替代解释未被排除?
3. 本次是新信息还是重复已知问题?(对比 Ignorance Hash)
4. 工具错误预算趋势是否健康?

**Claude Code 最终决策**:`/think` 是参考意见,Claude Code 综合项目上下文拍板。拿不准的才进 `to-discuss.md`。

### Step 5:分流归档

| 级别 | 归档 |
|------|-----|
| A 级 | `TODO.md`(`todo-write` skill) |
| B 级 | `TODO.md`,标注"待复现 2/2" |
| C 级 | 留在 `_scratch/godot-explore/explore-*.md` 盲区章节 |
| D 级 | 计入 `_scratch/godot-explore/tool-errors/YYYY-MM.md` |
| `/think` 拿不准的 Founder-level 决策 | `to-discuss.md`(极少数,按 `/think` skill 契约) |

**Ignorance Hash 更新**:

```bash
# 每个进 TODO.md 的 bug,计算 hash 存入已知集
HASH=$(echo -n "$SCENE|$ACTION_ENDPOINT|$EXPECTED_FIELD" | sha256sum | cut -c1-16)
echo "$HASH  B1 第 3 波金币结算未触发" >> _scratch/godot-explore/known-hashes.json
```

下次探索命中 hash → 标 `[SEEN]`,**不进报告正文**,只在自我否定统计里计数。

**绝对禁止(v4.0 沿用)**:
- 把 C 级观察伪装成 B 级 bug(缺证据链 → C 就是 C)
- 跳过 `/think` 直接往 `to-discuss.md` 塞条目
- 从截图脑补因果,在本报告对审美/性能/数值平衡下判断
- TODO.md 与 to-discuss.md 之间设指针

---

## 注意事项(v4.0)

1. **单轮 1 persona × 1 strategy** — 用户多次运行覆盖不同 strategy(靠 coverage-log 辅助)
2. **不穷举边界、不跑故事** — 那是 `godot-qa-stories` 的事
3. **不过度探索** — 每个 persona 1 轮,总共不超过 2 轮
4. **保持人设一致** — 新手不会精确计算 DPS,经济玩家不会乱花钱
5. **Crime Scene 是硬证据层** — B 级及以上必附三件套(before/after/oracle+events+crash),口头描述不算
6. **会删自己的系统才可信** — 自我否定统计必填,不允许"候选 3 全部 B 级"这种零筛选输出
7. **超过错误预算立即暂停探索** — 优先修 DebugPlayServer / Probe 截图链路再继续
8. **跨维度提示允许,跨维度判断禁止** — 审美/性能/数值平衡只能标"疑似"并路由,不下结论
9. **curl 单任务锁** — DebugPlayServer 同时只处理一个请求,429 = 忙,**不要用并发 Rage-Tap**
10. **破坏性操作放到每轮末尾** — `save_reset` 在 Step 3 集中执行
11. **JSON 参数单引号包裹** — `-d '{"level":1}'`,避免 shell 转义吃掉双引号
12. **Probe 截图本质是 Godot Viewport** — 与游戏窗口同源,不存在"截到桌面"问题,但 headless 模式下不可用(memory `godot_headless_pitfalls.md` 已 codify)

---

## 变更历史

- **4.0.0** (2026-04-26):从 v3.0 缩范围对齐 ai-explore v4.0 的可证伪质量基础设施。仅 port 治理层,**不 port 视觉强耦合机制**。详见决策记录 `~/.claude/docs/decisions/2026-04-26-02-godot-explore-v4-governance-only.md`。

  **已 port**(治理层,平台无关):
  - 边界白名单(防职责蔓延,命中即路由)
  - DebugPlayServer 契约段(必需/可选端点定义 + barracks-clash 现状示例 36 个端点)
  - PAV-2T 双证据校验循环(System / Surface)
  - Crime Scene 三件套(before / after / oracle+events+crash 三合一 JSON,**无红框因无 nodeId/bounds**)
  - A/B/C/D 分级 + 信用摘要页 + 工具错误预算
  - persona × strategy 正交模型(5 种 strategy 强制选择 + coverage-log 防重)
  - Ignorance Hash 去重
  - `/think` dual 模式 + 必附原始证据

  **已砍**(视觉强耦合,WSL 不可用 / Godot 无对应能力):
  - Cyborg 视觉+点击主链 → 改为单一模式"curl 主链 + Probe 自带截图"(平台无关)
  - Generation ID + 2s 硬超时 → Godot 无 DOM 概念,无对象可标 stale
  - Behavioral Fuzzing 中的 Fat-Finger / Rage-Tap → 无 OS tap / curl 单任务锁
  - 红框 Crime Scene 标注 → 无 nodeId/bounds
  - 三角校验中的 Interaction 证据源 → curl HTTP 200 不构成独立证据,合并入 System

  **降级声明**:
  - A 级实质罕见(需伴 `/debug/crash_log` 新增崩溃栈),大部分异常上限为 B,这是已知降级不是缺陷
  - **不存在 Cyborg 视觉+点击主链**(无 nodeId / 无 OS tap),与平台无关 — macOS 下也不引入 cliclick(端点已覆盖 UI 操作,坐标 tap 是冗余)
  - 报告路径迁移:`_scratch/explore-YYYY-MM-DD.md` → `_scratch/godot-explore/explore-YYYY-MM-DD.md`(与 ai-explore / android-explore 命名空间对齐)

  **关键事实修正**(初版 v4.0 写作时漏看,Founder push 后查证):
  - DebugPlayServer.gd:72 已实装 `_scene` 字段附在每个响应,**不需要新加 `/state/route` 端点** — Step 2.P/V 直接读 `_scene` 做 route diff(强信号)
  - WSL2 + Xvfb 实测可启 Godot(参考 game-mvp/TODO.md 2026-04-26 godot-qa-stories 验证),**不再要求 Founder 在 macOS 跑** — Step 0a 自动起 Xvfb + Godot,Step 0b 验证 GL 渲染器在 Xvfb 下截图非黑

- **3.0.0** 及更早(2026 年初 commit `9965e37`):curl 主模式 + 可选 Cyborg(macOS screencapture+cliclick) + 单链条证据链 + PAV 循环 + 单人设单轮 + `/think --quick` 评估。已被 v4.0 治理层全面吸收。
