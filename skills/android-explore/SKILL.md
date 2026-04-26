---
name: android-explore
description: >
  Use when the user says "探索应用", "自由探索", "用一下", "explore", "find bugs",
  or after android-qa-stories passed and deeper exploration is needed. AI
  role-plays as a user to discover bugs and UX issues in a running native Android
  app. Supports Cyborg mode (Vision + adb tap + State Oracle + Logcat triangulation)
  when an emulator/device is connected, and Fallback mode (curl-only). Requires
  Debug Server embedded in the app.
version: 4.0.0
---

# Android Explore — 可证伪的自主质量基础设施（Android 适配版）

AI 扮演用户自由使用应用。Cyborg 模式下通过 **截图 + uiautomator + adb tap** 真正操作 UI，**三证据源三角校验**每一个判断，**A/B/C/D 分级**报告让 Founder 30 秒判定是否值得消费。

## 核心哲学（v4.0 升级自 v3.x）

- **三证据源三角校验 > 单链条证据链** — Interaction（操作命中）/ System（Oracle 状态 + Logcat）/ Surface（截图 + uiautomator 语义）三者同时支持才能 A 级，任何一条单独成立即降级
- **Oracle 不是神谕** — 它是三证据源之一，可能自己有 bug；只要表层或 Interaction 与 Oracle 冲突，按"工具疑点"标记
- **会筛选的系统才可信** — 高自毁率 > 高发现率；报告必须包含"候选 X → 证伪 Y → 降级 Z → 高可信 W"的自我否定统计
- **Logcat 是 Android 独有的第三证据源** — 比 Flutter 的 Probe 更天然，捕获 ANR / 崩溃 / 系统级警告 / InputDispatcher 异常，与 State Oracle 互补
- **persona × strategy 正交** — persona 是风格包装，strategy（Goal-seeking / Boundary-pushing / Misread-first / Impatience / Constraint）才是覆盖模型
- **边界硬卡 > 温柔拒绝** — 审美 / 性能 / 多端 / a11y / 埋点 / 安全明确不处理，错过少量跨维度信号 > 变成垃圾总线
- **决策时是用户，报告时是工程师** — 用人设决定点哪里，但报告问题必须走证据链
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码
- **不做故事验证** — 那是 `android-qa-stories` 的职责

---

## 边界白名单（v4.0 新增 — 防职责蔓延的硬卡）

### 本 skill 负责

- 可交互 UI 流程探索
- 由三证据源支撑的功能异常
- 状态机边界异常（连续点击 / 竞态 / 脏状态）
- Android 特有的崩溃 / ANR / Logcat 异常（属 System Evidence）

### 本 skill **不负责**（命中即拒绝并路由）

| 维度 | 路由到 |
|------|-------|
| 审美 / 品牌气质 / 情绪感受 | `ui-vision-advance` |
| 单页跨版本一致性 / 设计债 | `ui-vision-check` |
| 性能 / 流畅度 / 帧率主观评价 | **能力空缺**（不要硬塞） |
| 多设备一致性 / form factor 适配 | 项目级 CLAUDE.md 的形态失配声明（不进 bug） |
| 无障碍审计 | `accessibility-expert` agent |
| 文案策略优劣 | `content-marketer` agent |
| 埋点正确性 | **能力空缺** |
| 安全性 | `security-auditor` agent |
| 用户故事回归 | `android-qa-stories` |

### 中庸措辞（允许）

发现功能异常且疑似与视觉/文案误导相关时，可标注：
> "发现功能异常 X，可能与文案/视觉误导有关（见 Crime Scene 截图），但本 skill 不对审美维度下结论。建议链式调用 ui-vision-advance 独立评审该页。"

跨维度提示允许，**绝不在本报告里给审美下判断**。

---

## 模式选择（自动判断）

```bash
# 1. 端口动态发现（从源码读取，禁止硬编码）
PORT=$(grep -rE 'const\s+(val\s+)?PORT\s*[:=]' app/src/debug app/src/main 2>/dev/null | grep -oE '[0-9]{4,5}' | head -1)
[ -z "$PORT" ] && PORT=$(grep -rE 'port\s*=\s*[0-9]+' app/src 2>/dev/null | grep -i 'debug' | grep -oE '[0-9]{4,5}' | head -1)
echo "Android debug port: ${PORT:-NOT_FOUND}"

# 2. adb 设备 + Debug Server 可达性 + uiautomator 可用
adb devices 2>/dev/null | grep -q 'device$'
adb forward tcp:$PORT tcp:$PORT 2>/dev/null
curl -s -m 2 localhost:$PORT/providers >/dev/null 2>&1
adb shell uiautomator dump /sdcard/ui_test.xml 2>/dev/null && adb shell rm /sdcard/ui_test.xml
```

| 条件 | 模式 | 能力 |
|------|------|------|
| adb 设备 + Debug Server + uiautomator 可用 | **Cyborg** | 真实交互 + 三证据源三角校验 + Behavioral Fuzzing |
| 仅 Debug Server 可用 | **Fallback** | 端点覆盖测试（A/B/C/D 分级仍适用，但三角校验仅剩 Interaction+System 两条，Surface 缺位） |

> 端口发现失败时，需在项目 CLAUDE.md 中声明 `DEBUG_SERVER_PORT`，或检查源码中 DebugServer 类的 port 常量命名。

---

## 前置条件

1. **Debug Server 可达** — Step 0 自动检测；不可达则按"Step 0a 内嵌环境恢复"流程恢复，30s 超时仍失败 → 报告失败原因，**不进入探索**（脏状态禁行）
2. **adb 设备已连接** — 注意 **adb daemon 跨 session 不持久**，新会话必须先 `adb connect <ip>:5555` 重建（参考项目级 CLAUDE.md 的 Default Test Devices 段决定连哪台）
3. **设备已唤醒+解锁** — Android 默认连上即 `mWakefulness=Asleep`，直接 screencap 全黑。Step 0 强制执行唤醒序列
4. **基线数据就绪** — 想验证 stories 的用户应调用 `/android-qa-stories`

**严禁脏状态下开始探索** — 三角校验会在矛盾状态下给出错误结论，直接污染 D 级工具错误预算。

---

## Debug Server 契约（v4.0 新增）

本 skill 期望的端点契约。端点不存在则对应能力降级，**在信用摘要页显式标注**。

> Android 没有 Flutter 的 `/cyborg/dom` + generation 机制。等价物：**`adb shell uiautomator dump` 输出 XML，每次重 dump 即视为最新版本**（无 generation 校验，靠"操作前重 dump"自然纪律）。

### 必需端点（缺失即 Fallback）

| 端点 | 契约 |
|------|------|
| `/providers` | 返回所有可用端点清单 — 用于 Step 0 探测 |
| `/state/*` | 至少 1 个项目级 state 端点（如 FlameTree 的 `/state/screen` `/state/player` `/state/focus`），用于 System Evidence |

### 可选增强端点（实现则升级能力）

| 端点 | 实现后获得 |
|------|----------|
| `/state/screen` 或类似当前路由端点 | route diff 作为 System Evidence 强信号 |
| `/data/crashes`（项目实现 CrashRecorder） | 绕过 logcat UID 限制读崩溃栈（FlameTree TV 已实现） |
| `/action/*` POST 端点 | Fallback 模式下的语义动作注入（如 `/action/openFolder`） |

### 项目侧契约示例（FlameTree TV）

```
/providers                                 # 端点清单
/state/screen   /state/player   /state/smb   /state/focus
/data/homeRows  /data/folderContents  /data/playbackHistory
/data/uploadQueue  /data/captures  /data/thumbnailCache  /data/crashes
/action/openFolder  /action/playVideo  /action/navigateBack
/action/seekTo  /action/reloadHome
```

其他项目按自己的端点适配。

---

## Cyborg 模式执行流程

### Step 0：环境初始化 + 契约健康检查

#### 0a. 内嵌环境恢复（强制，无外部 prep skill）

> Android 平台**没有** `prep-cyborg-env` skill（那是 Flutter 专属）。本 skill 自带简版恢复流程。

```bash
# 1. 选设备（按项目级 CLAUDE.md 的 Default Test Devices 决策）
DEVICE=192.168.0.51:5555  # 默认日常调试机；TV 形态测试改 192.168.0.105:5555

# 2. adb 连接（跨 session 不持久，每次必跑）
adb connect $DEVICE
adb -s $DEVICE devices | grep -q 'device$' || { echo "ADB 未连接 $DEVICE"; exit 1; }

# 3. 唤醒 + 解锁（Android 必须，否则 screencap 全黑）
adb -s $DEVICE shell input keyevent KEYCODE_WAKEUP
adb -s $DEVICE shell input swipe 540 2000 540 800 200    # 1080x2400 屏幕无锁屏密码
adb -s $DEVICE shell dumpsys power | grep -q "mWakefulness=Awake" || { echo "唤醒失败"; exit 1; }

# 4. 启动 App（如未在前台）
adb -s $DEVICE shell monkey -p $PKG -c android.intent.category.LAUNCHER 1

# 5. 端口转发
adb -s $DEVICE forward tcp:$PORT tcp:$PORT

# 6. Debug Server 可达轮询，最多 30s
for i in $(seq 1 15); do
  curl -s -m 2 localhost:$PORT/providers >/dev/null && break
  if [ $i = 15 ]; then echo "Debug Server 30s 仍不可达 → 报告失败，不进入探索"; exit 1; fi
done
```

**落地规则**：
- 任一步骤失败 → 明确报告失败原因，**不进入探索**
- 全部通过 → 进入 0b 契约健康检查

#### 0b. 契约健康检查

```bash
# 1. 列出 /providers 报告的端点，对比期望
curl -s localhost:$PORT/providers | python3 -m json.tool

# 2. 探测 uiautomator 是否可用（Surface 证据源）
adb -s $DEVICE shell uiautomator dump /sdcard/ui_dump.xml >/dev/null 2>&1
UI_OK=$([ $? = 0 ] && echo ✅ || echo ❌)

# 3. 探测 screencap（Surface 证据源）
adb -s $DEVICE exec-out screencap -p > /tmp/health_screen.png 2>/dev/null
SCREEN_OK=$([ -s /tmp/health_screen.png ] && echo ✅ || echo ❌)

# 4. 探测 logcat（System 补充证据源）
adb -s $DEVICE logcat -d -t 5 >/dev/null 2>&1
LOG_OK=$([ $? = 0 ] && echo ✅ || echo ❌)
```

**记录本次探索的工具健康状态**，后面信用摘要页要用：
- uiautomator dump 是否可用（不可用 → 无法对节点 bounds 提取语义信息，分级上限为 B）
- screencap 是否输出非黑图（黑图 → 唤醒序列失败，立即重跑 0a）
- logcat 是否可读（不可读 → 第三证据源缺失，A 级置信度下降）

### Step 1：建立 persona × strategy

#### 1a. 动态生成 persona（风格包装）

调用 `/think --quick`（仅文本人设生成不需要多模态），输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要，要求生成 1 个贴合该 App 的用户人设。格式：emoji+名称 / 背景 / 行为倾向 / 自然覆盖 / 使用计划。

> `/think` 不可用时回退默认：🐣 新手 / ⚡ 效率达人 / 🐒 混乱操作者 / 🔄 回归用户 / 🧹 洁癖用户

#### 1b. 强制选择 strategy（覆盖模型）

**persona 是风格包装，strategy 才是正交覆盖。本轮必须显式选 1 种 strategy**：

| Strategy | 行为规则 | 专攻 |
|----------|---------|------|
| **Goal-seeking** | 按最合理路径尽快完成目标 | 主干流程流畅度 |
| **Boundary-pushing** | 重复点 / 撤销 / 循环跳转 / 在 loading 中操作 | 状态机边界 |
| **Misread-first** | 按最可能的错误理解操作（如把"取消"当"返回"） | 文案/入口误导 |
| **Impatience** | 不等 Oracle 返回、不等动画结束连续操作 | 竞态 / 动画窗口 bug |
| **Constraint** | 低注意力，只看局部 UI 线索不理解全局 | 局部 UI 误解 |

**如何选**：读 `_scratch/android-explore/coverage-log.md`（不存在则建），选上次运行**未覆盖**的 strategy。连续 5 轮覆盖满 5 种 → 重置循环。

报告开头声明："本轮 persona = XX，strategy = YY，组合未在近 3 轮出现。"

### Step 2：感知-行动-验证（PAV-3T，三角校验循环）

#### P — 感知

```bash
# 1. 截屏（Surface 视觉源）
SCRSHOT=/tmp/android_screen_${N}.png
adb -s $DEVICE exec-out screencap -p > "$SCRSHOT"

# 2. uiautomator dump（Surface 语义源 — 节点 + bounds）
adb -s $DEVICE shell uiautomator dump /sdcard/ui_${N}.xml >/dev/null
adb -s $DEVICE pull /sdcard/ui_${N}.xml /tmp/ui_${N}.xml >/dev/null
adb -s $DEVICE shell rm /sdcard/ui_${N}.xml

# 3. 项目 state（System 源）
curl -s localhost:$PORT/state/screen
curl -s localhost:$PORT/state/focus    # FlameTree 示例，按项目调整
```

**找节点中心坐标**（替代 Flutter 的 nodeId）：

```bash
python3 <<PY
import xml.etree.ElementTree as ET, re
root = ET.parse('/tmp/ui_${N}.xml').getroot()
# 按 text 或 resource-id 查节点
for node in root.iter('node'):
    if 'Library' in (node.get('text') or ''):
        bounds = node.get('bounds')  # "[x1,y1][x2,y2]"
        m = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
        x1, y1, x2, y2 = map(int, m.groups())
        print(f"center: {(x1+x2)//2} {(y1+y2)//2}")
        break
PY
```

#### A — 行动（支持 Behavioral Fuzzing）

**主力：坐标 tap（Android 天然同源坐标系，screencap 与 input tap 共用设备像素）**

```bash
adb -s $DEVICE shell input tap $X $Y
```

**Behavioral Fuzzing（strategy-specific）**

- **Fat-Finger**（Constraint strategy 可选）：tap 在节点 bounds 边缘而非中心
  ```bash
  # 用 bounds 右下角 90% 而非中心
  EDGE_X=$((x1 + (x2-x1)*9/10))
  EDGE_Y=$((y1 + (y2-y1)*9/10))
  adb -s $DEVICE shell input tap $EDGE_X $EDGE_Y
  ```
- **Rage-Tap**（Impatience / Boundary-pushing 必备）：同坐标连发 3 次，不等响应
  ```bash
  for i in 1 2 3; do adb -s $DEVICE shell input tap $X $Y & done; wait
  ```
- **Amnesia**（Boundary-pushing 可选）：每 3 步 `adb shell input keyevent KEYCODE_HOME` 强制回桌面，再冷启 App
- **手势 fuzzing**：长按用 `adb shell input swipe X Y X Y 1500`（同坐标 1.5s）；scroll 用 `adb shell input swipe X1 Y1 X2 Y2 200`
- **D-pad 注入**（TV 形态）：`adb shell input keyevent KEYCODE_DPAD_{LEFT,RIGHT,UP,DOWN,CENTER}`

#### V — 三角校验（Triangulation）

对每次"可疑"操作（预期发生变化的操作）产生 **3 条独立证据**：

| 证据源 | 采集方式 | 判定异常 |
|-------|---------|---------|
| **Interaction** | `adb shell input tap` 命令退出码 + logcat InputDispatcher 行 | tap 命令报错 / InputDispatcher 报"no focused window" |
| **System** | `/state/*` 前后对比 + `adb logcat -d -t 30 *:E` | 预期变化但未变 / 未预期 logcat error 出现 / `/data/crashes` 新增条目 |
| **Surface** | screencap 前后对比 + `uiautomator dump` XML 节点集合 diff | 预期 UI 变化缺失 / 语义节点异常 |

**分级规则**：

| 三证据一致性 | 分级 |
|------------|-----|
| 3/3 都支持"异常存在"且二次复现成功 | **A**（高可信） |
| 2/3 支持异常 | **B**（中可信，归因未闭环） |
| 1/3 支持异常 | **C**（观察项，进盲区不进 bug） |
| 证据相互冲突（如 Oracle 异常但 Surface 正常） | **D**（工具疑点，怀疑 Debug Server / uiautomator / skill 自身） |

### Step 2.5：Crime Scene 双快照（发现 A/B 级候选时）

命中"实际 ≠ 预期"瞬间：

```bash
SCREENSHOT_DIR="screenshots/cyborg/$(date +%Y-%m-%d)"
mkdir -p "$SCREENSHOT_DIR"

# 1. 操作前截图（已在 Step 2.P 做过可复用）
cp /tmp/android_screen_${N}.png "$SCREENSHOT_DIR/step_${N}_before.png"

# 2. 在 before.png 上画红框标出即将点击的节点（用 Python PIL）
python3 <<PY
from PIL import Image, ImageDraw
import os
# bounds 来自 uiautomator XML 解析（见 Step 2.P）
img = Image.open(f'{os.environ["SCREENSHOT_DIR"]}/step_${N}_before.png')
draw = ImageDraw.Draw(img)
draw.rectangle([${X1}, ${Y1}, ${X2}, ${Y2}], outline='red', width=4)
img.save(f'{os.environ["SCREENSHOT_DIR"]}/step_${N}_before_annotated.png')
PY

# 3. 操作
adb -s $DEVICE shell input tap $X $Y

# 4. 操作后截图 + Oracle 快照 + Logcat 快照
adb -s $DEVICE exec-out screencap -p > "$SCREENSHOT_DIR/step_${N}_after.png"
curl -s localhost:$PORT/state/screen > "$SCREENSHOT_DIR/step_${N}_oracle.json"
adb -s $DEVICE logcat -d -t 50 *:W > "$SCREENSHOT_DIR/step_${N}_logcat.txt"
```

**Crime Scene 四件套（Android 比 Flutter 多一份 logcat）**：
- `step_N_before_annotated.png`（带红框）
- `step_N_after.png`
- `step_N_oracle.json`
- `step_N_logcat.txt`

Founder 看 before+after 两张图 + 一行 Oracle diff 断言 + logcat 关键行，**3 秒判定**是否 bug。

### Step 3：数据恢复 + State Teardown

```bash
# Android 没有 /cyborg/reset。State Teardown = force-stop + 冷启动 + seed
adb -s $DEVICE shell am force-stop $PKG
adb -s $DEVICE shell pm clear $PKG       # 谨慎使用，会清 SharedPreferences
# 或更轻量：仅 force-stop + 冷启
adb -s $DEVICE shell monkey -p $PKG -c android.intent.category.LAUNCHER 1

# 项目有 seed 脚本则跑（FlameTree 走 publish-to-nas.sh + 实机数据，无 seed 脚本）
[ -x ./scripts/seed-test-data.sh ] && ./scripts/seed-test-data.sh
```

### Step 4：A/B/C/D 分级报告

#### 4a. 报告落盘 + 打印

写入 `_scratch/android-explore/explore-YYYY-MM-DD.md`，同日追加 `## 第 N 次探索`。同时打印到对话。

#### 4b. 报告结构（v4.0）

```markdown
## 探索报告 v4.0

### 🏷️ 信用摘要页（Founder 30秒扫描）

| 指标 | 值 |
|------|---|
| 模式 | Cyborg / Fallback |
| 设备 | 小米手机 192.168.0.51 / TCL TV 192.168.0.105 |
| persona × strategy | 🐣 新手小白 × Boundary-pushing |
| 候选问题数 | N |
| 二次复现成功 | M |
| **A 级（高可信）** | X |
| B 级（中可信） | Y |
| C 级（观察项） | Z |
| D 级（工具疑点） | W |
| New / Known-regressed / Known-still-open | a/b/c |
| 工具健康 | uiautomator=✅/❌, screencap=✅/❌, logcat=✅/❌, Oracle=✅/❌ |
| 本月累计 D 级占比 | 12% ✅（阈值 30%） |

### 🎮 用户体验（人设视角）

#### 🐣 新手小白: [背景故事一句话]
> strategy = Boundary-pushing
> [2-3 段体验描述，只在意外处详写]

### 🐛 技术问题清单（A/B 级必填最小证伪单元）

#### A 级（高可信）

##### A1. [一句话问题描述]
- **触发前提**: 首次进入 /folder 页，存在 ≥2 个文件夹
- **最小交互序列**:
  1. tap (540, 1200) bounds=[300,1100][780,1300] label="Movies" → `step_3_before_annotated.png`
  2. tap (540, 1500) bounds=[300,1400][780,1600] label="返回" → `step_4_oracle.json`
- **三证据**:
  - Interaction: ✅ adb tap exit=0, InputDispatcher 无 error
  - System: ✅ `/state/screen` 前 `route=folder`，后仍 `route=folder`（未返回）
  - Surface: ✅ screencap UI 仍显示 folder 内容（见 `step_4_after.png`）
- **预期**: route=home，UI 显示首页
- **实际**: route=folder，UI 不变
- **已排除的替代解释**:
  - ❌ 非 stale uiautomator dump（操作前重新 dump）
  - ❌ 非动画中间态（2s 后仍如此）
  - ❌ 非 Oracle 滞后（重取 3 次一致）
  - ❌ 非形态失配（手机和 TV 上均复现）
- **Crime Scene**: screenshots/cyborg/2026-04-26/step_{3,4}*.{png,json,txt}
- **复现**: 2/2

#### B 级（中可信）

##### B1. ...
（同上，但允许"归因未闭环"或"复现 1/2"，列出未排除的替代解释）

#### C 级（观察项，不进 bug 清单）

- **现象**: ...
- **为什么是 C**: 仅 Surface 证据，State 端点未覆盖该状态
- **人工验证方法**: ...

#### D 级（工具疑点 → 计入错误预算）

- **现象**: ...
- **为什么是 D**: Oracle 说异常但 Surface 完全正常，重取 3 次均不一致
- **怀疑对象**: Debug Server / uiautomator dump / skill 自身

### 📊 自我否定统计

- 候选数: 15
- 二次复现失败（已证伪）: 6
- 从 A 降级到 B: 2
- 从 B 降级到 C: 3
- D 级（工具疑点）: 1
- 形态失配排除（手机跑 TV App 的预期失配 → 不报）: 4
- **最终上报 A+B**: 3

### 🔭 盲区观察（C 级，不进 TODO.md）

- [略]

### 💡 跨维度提示（可选，禁止下判断）

- 在 A2 的 Crime Scene 中观察到 [UI 现象]，疑似文案误导。建议后续链式调用 `ui-vision-advance` 独立评审。
```

#### 4c. 工具错误预算追踪

写入 `_scratch/android-explore/tool-errors/$(date +%Y-%m).md`：

```markdown
# Purpose: 本月 android-explore 工具误报追踪
# Created: 2026-04-26

## 2026-04-26 第 N 次探索
- 候选: 15, D 级: 1
- 累计本月: 候选 87, D 级 9 = 10.3% ✅
```

超过 30% 阈值 → 报告顶部显著标注："⚠️ 本月误报率 X% 超阈值，建议优先修 Debug Server / uiautomator 工具链而非继续跑探索。"

### Step 4.5：/think 评估（附原始证据）

报告写完后调用 `/think` 做独立视角 sanity check。

**输入契约（v4.0 强化）**：

- **必附**：A/B 级 bug 的完整 Crime Scene 四件套（before_annotated.png + after.png + oracle.json + logcat.txt 原文）
- **必附**：工具健康状态、本月误报率、设备形态（避免把形态失配判成 bug）
- **不附**：AI 的总结和主观评语

**模式选择**：
- 报告含 A/B 级 Crime Scene → 默认 **dual**（Gemini 多模态看图，GPT 逻辑校验证据链 + logcat）
- 仅 C 级/纯文本 → `--quick`

**要求 /think 回答**：
1. Oracle 是否可能自己在撒谎？（对每个 A 级）
2. 有没有替代解释未被排除？（特别是"手机跑 TV App"形态失配）
3. 本次是新信息还是重复已知问题？（对比 Ignorance Hash）
4. 工具错误预算趋势是否健康？

**Claude Code 最终决策**：/think 是参考意见，Claude Code 综合项目上下文拍板。拿不准的才进 `to-discuss.md`。

### Step 5：分流归档

| 级别 | 归档 |
|------|-----|
| A 级 | `TODO.md`（todo-write skill） |
| B 级 | `TODO.md`，标注"待复现 2/2" |
| C 级 | 留在 `_scratch/android-explore/explore-*.md` 盲区章节 |
| D 级 | 计入 `_scratch/android-explore/tool-errors/YYYY-MM.md` |
| 形态失配（手机跑 TV App） | 不进 TODO，留在报告"自我否定统计"章节 |
| `/think` 拿不准的 Founder-level 决策 | `to-discuss.md`（极少数，按 /think skill 契约） |

**Ignorance Hash 更新**：

```bash
HASH=$(echo -n "$ROUTE|$NODE_LABEL|$ACTION_TYPE" | sha256sum | cut -c1-16)
echo "$HASH  A1 在 folder 页返回不生效" >> _scratch/android-explore/known-hashes.json
```

下次探索命中 hash → 标 `[SEEN]`，**不进报告正文**，只在自我否定统计里计数。

**绝对禁止（v4.0 沿用）**：
- 把 C 级观察伪装成 A/B 级 bug（缺证据链 → C 就是 C）
- 把形态失配（手机跑 TV App 的预期表现）报为 bug
- 跳过 /think 直接往 `to-discuss.md` 塞条目
- 从截图脑补因果，在本报告对审美/性能/多端下判断
- TODO.md 与 to-discuss.md 之间设指针

---

## Fallback 模式

adb 设备 / uiautomator / screencap 任一不可用时自动降级。

**诚实声明**：Fallback 下**三角校验只剩 Interaction + System 两条**（无 Surface），分级上限为 **B**。无法覆盖导航流程、手势、动画。

执行流程：Step 0 → Step 1（persona×strategy 仍然强制）→ Step 2 改为 `curl /action/*` + `curl /state/*` + `adb logcat` → Step 4 报告（A 级条目为 0）→ Step 4.5 /think（用 --quick 即可）→ Step 5 分流。

**Fallback 特别声明（写入报告信用摘要页）**：
- 本次为 Fallback，操作绕过 UI 层不经过焦点系统不触发动画
- 发现的问题可能是 Debug Server 限制而非真实 bug
- A 级分级自动禁用

---

## 注意事项（v4.0）

1. **单轮 1 persona × 1 strategy** — 用户多次运行覆盖不同 strategy（靠 coverage-log 辅助）
2. **不穷举边界、不跑故事** — 那是 `android-qa-stories` 的事
3. **同源坐标系** — `adb screencap` 和 `adb input tap` 天然同设备像素坐标，无需 DPR 转换；但**屏幕方向变化（横竖屏切换）后必须重新 `adb shell wm size` 确认**
4. **每次操作前重 dump uiautomator** — Android 没有 generation 校验机制，靠"用之前重 dump"自然纪律避免 stale bounds
5. **Crime Scene 是硬证据层** — A/B 级必附四件套（含 logcat），口头描述不算
6. **会删自己的系统才可信** — 自我否定统计必填，不允许"候选 3 全部 A 级"这种零筛选输出
7. **超过错误预算立即暂停探索** — 优先修 Debug Server / uiautomator 工具链再继续
8. **跨维度提示允许，跨维度判断禁止** — 审美/性能只能标"疑似"并路由，不下结论
9. **形态失配不是 bug** — FlameTree 在小米手机上跑会有竖屏拉伸 / 焦点环被裁 / D-pad 用 keyevent 模拟，这些不报；只在 TCL TV 上首次出现的才算（参考项目级 CLAUDE.md 的 Default Test Devices 段）
10. **adb daemon 跨 session 不持久** — 每个新会话第一个 adb 命令前必须先 connect，不要假设上轮的连接还在
11. **唤醒+解锁是 Step 0 强制项** — 不是"发现黑屏后再补救"，而是"无条件先做"
12. **探索后必须恢复数据** — force-stop + 冷启动 + seed 脚本（如有）

---

## 变更历史

- **4.0.0** (2026-04-26)：从 v3.0 全面对齐 ai-explore v4.0 的可证伪质量基础设施。引入：
  - **边界白名单**（防职责蔓延，命中即路由）
  - **Debug Server 契约段**（必需/可选端点定义 + FlameTree 项目侧示例）
  - **PAV-3T 三角校验循环**（Interaction / System / Surface 三证据源，Logcat 作为 Android 独有 System 增强）
  - **Behavioral Fuzzing**（Fat-Finger / Rage-Tap / Amnesia / 手势 fuzzing / D-pad 注入）
  - **Crime Scene 四件套**（before_annotated + after + oracle.json + logcat.txt）
  - **A/B/C/D 分级 + 信用摘要页 + 工具错误预算**
  - **persona × strategy 正交模型**（5 种 strategy 强制选择 + coverage-log 防重）
  - **Ignorance Hash**（去重已知问题）

  Android 平台特异性保留 / 新增：
  - **没有 cyborg/dom + generation** → 用 `uiautomator dump` 等价，每次重 dump 即视为最新（无 stale 校验）
  - **没有 prep-cyborg-env 外部 skill** → 内嵌 Step 0a 简版恢复（连接 / 唤醒解锁 / 启动 App / 端口转发 / 健康轮询）
  - **没有 /cyborg/reset** → State Teardown 用 `am force-stop` + 冷启动 + seed
  - **Logcat 升级为第三独立证据源**（Flutter 没有等价物）
  - **形态失配排除**（手机跑 TV App 的预期表现不报，参考项目级 CLAUDE.md）
  - **设备双机决策**（小米手机日常 / TCL TV 最终目标，按用途选）
  - **唤醒+解锁强制 Step 0**（Android 默认连上即 Asleep）

- **3.0.0** 及更早：Cyborg 基础能力（adb screencap + adb tap 同源坐标 + State Oracle 单链条证据 + Logcat）、PAV 循环、单人设单轮、/think --quick 评估。已被 v4.0 全面吸收并扩展。
