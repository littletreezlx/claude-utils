---
name: android-explore
description: >
  Use when the user says "探索应用", "自由探索", "用一下", "explore", "find bugs",
  or after android-qa-stories passed and deeper exploration is needed. AI
  role-plays as a user to discover bugs and UX issues in a running native Android
  app. Supports Cyborg mode (Vision + adb tap + State Oracle) when an emulator/device
  is connected, and Fallback mode (curl-only). Requires Debug Server embedded in the app.
version: 3.0.0
---

# Android Explore — Cyborg 自主探索

AI 扮演用户自由使用应用。Cyborg 模式下通过**截图识别 + adb tap**真正操作 UI，State Oracle 验证状态变化。

## 核心原则

- **Cyborg = 皮（Vision+Tap），Oracle = 骨（State 验证）** — 截图感知 UI，adb tap 驱动交互，curl 验证状态。三层配合，缺一不可
- **同源坐标系** — adb screencap 和 adb input tap 天然使用同一设备像素坐标，无需转换
- **决策时是用户，报告时是工程师** — 用人设决定点哪里，但报告问题必须走证据链
- **归因必须有证据链** — Bug = 操作 X → State Oracle 返回 Y → 与预期 Z 不符。缺任一环 → 盲区观察，不是 bug
- **不做故事验证** — 那是 android-qa-stories 的职责
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码

---

## 模式选择（自动判断）

```bash
# 发现端口（从源码读取，禁止硬编码）
# 按优先级尝试常见位置：
PORT=$(grep -rE 'const\s+(val\s+)?PORT\s*[:=]' app/src/main/java app/src/main/kotlin 2>/dev/null | grep -oE '[0-9]{4,5}' | head -1)
[ -z "$PORT" ] && PORT=$(grep -rE 'port\s*=\s*[0-9]+' app/src/main 2>/dev/null | grep -i 'debug' | grep -oE '[0-9]{4,5}' | head -1)
echo "Android debug port: ${PORT:-NOT_FOUND}"

# 端口转发 + Cyborg 前置条件检测
adb forward tcp:$PORT tcp:$PORT 2>/dev/null
adb devices 2>/dev/null | grep -q 'device$' && \
  curl -s localhost:$PORT/providers >/dev/null 2>&1
```

> 端口发现失败时，需在项目 CLAUDE.md 中声明 `DEBUG_SERVER_PORT`，或检查源码中 DebugServer 类的 port 常量命名。

| 条件 | 模式 | 探索能力 |
|------|------|---------|
| adb 设备连接 + Debug Server 就绪 | **Cyborg** | 真实 UI 交互 + 导航 + 手势 + State 验证 + Logcat |
| 仅 Debug Server 可用 | **Fallback** | 端点覆盖测试（诚实声明：探索范围 = 端点数量） |

---

## 前置条件

### 共同条件
1. Debug Server 运行中（App 已启动，端口已转发）
2. 基线数据就绪

### Cyborg 额外条件
3. `adb devices` 显示已连接设备/模拟器
4. 端口转发已建立：`adb forward tcp:$PORT tcp:$PORT`

**基线不足时，只做最小 seed**。想验证 stories 的用户应调用 `/android-qa-stories`。

---

## Cyborg 模式执行流程

### Step 0: 环境初始化

```bash
# 确认设备连接
adb devices

# 获取屏幕尺寸（用于理解坐标范围）
adb shell wm size
# 返回示例: Physical size: 1080x2400
```

坐标系说明（Android 天然同源）：
- `adb exec-out screencap -p` → 设备像素坐标的截图
- `adb shell input tap X Y` → 设备像素坐标的点击
- **无需任何坐标转换**

### Step 1: 建立用户认知

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
curl localhost:$PORT/providers  → 可用的 state/data 端点（验证用）
```

**动态生成本轮用户人设**（每次探索 1 个，多次运行覆盖不同维度）：

调用 `/think --quick`，输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要，要求生成 **1 个**贴合该 App 的用户人设：

```
请根据以下产品信息，生成一个用户人设用于 App 探索测试。

产品信息：
[粘贴 PRODUCT_SOUL 核心段落 + PRODUCT_BEHAVIOR 核心交互]

要求输出格式：
- 人设名称：[emoji + 2-4字名称]
- 背景故事：[1句话，这个人是谁、为什么会用这个App]
- 行为倾向：[2-3个关键词，如"急躁、目标导向、不看说明"]
- 自然覆盖：[这个人设天然会测到的维度]
- 使用计划：[3-5句，以第一人称描述这次打开App要干什么]

要求：
- 人设必须贴合这个 App 的目标用户群，不要通用角色
- 行为倾向要具体到能指导"点哪里、跳过什么"
- 随机发挥，不要每次都生成类似的角色
```

> **不做去重** — 靠 DeepSeek 自身随机性 + 产品文档上下文自然分散。
>
> **/think 不可用时**，回退到默认人设：
> 🐣 新手小白 | ⚡ 效率达人 | 🐒 混乱操作者 | 🔄 回归用户 | 🧹 洁癖用户

收到 /think 返回后，**在探索开头写出完整人设信息**，然后进入 PAV 循环。

### Step 2: 感知-行动-验证循环

每步操作遵循 **PAV 循环**（Perceive → Act → Verify）：

#### P — 感知（截图 + 读状态）

```bash
# 截取设备屏幕
adb exec-out screencap -p > /tmp/android_screen_N.png
```

用 Read 工具查看截图 → AI 分析当前界面，识别元素的设备像素坐标。

**辅助定位**：结合 State Oracle 缩小搜索范围：
```bash
curl -s localhost:$PORT/state/route     # 当前页面（如有）
curl -s localhost:$PORT/state/overlays  # 弹窗状态（如有）
```

#### A — 行动（基于人设决策点击）

```bash
# 直接用设备像素坐标点击 — 无需转换
adb shell input tap X Y

# 滑动（如需要）
adb shell input swipe X1 Y1 X2 Y2 duration_ms

# 返回键
adb shell input keyevent KEYCODE_BACK
```

#### V — 验证（State Oracle + Logcat 确认效果）

每次点击后 **必须** 验证：

```bash
# 1. 截图确认 UI 变化
adb exec-out screencap -p > /tmp/android_screen_N_after.png

# 2. State Oracle 验证
curl -s localhost:$PORT/state/...

# 3. Logcat 检查异常（第三证据源）
adb logcat -d -t 30 *:E
```

**异常处理**：
- 点击无反应 → 重新截图定位，调整坐标再试（最多 2 次）
- State Oracle 返回异常 → 记录为技术问题（含截图 + curl 响应 + Logcat）
- UI 变化与 State 不一致 → 记录为可疑 bug，需人工确认

### 截图策略（节省 token）

**必须截图**：每轮起始、页面切换、弹窗出现/消失、预期外变化
**不需截图**：连续同类操作（只截最后一张）、State Oracle 已确认正确

### 使用规则

1. **破坏性操作放到每轮末尾**
2. **遇到异常时**：技术异常→记录（附截图+curl+Logcat）；UI 不确定→盲区观察；体验困惑→体验报告
3. **过程中只在遇到意外时写反应**

### Step 3: 数据恢复

探索结束后，**必须恢复基线数据**（运行 seed 脚本，或提醒用户数据已被修改）。

### Step 4: 输出报告

**同时做两件事**：写入 `_scratch/explore-YYYY-MM-DD.md` + 打印到对话。

报告格式：

```markdown
## 探索报告

### 环境
- 项目: xxx | 包名: com.xxx | 端口: xxxx | 时间: xxx
- 模式: Cyborg / Fallback
- 设备: [adb devices 输出]
- 基线: [seed 数据 / 用户提供数据]
- 本轮人设: 🐣 新手小白

### 🎮 用户体验
#### [人设名]: [背景故事一句话]
> [使用计划 3-5 句]
> [2-3 段体验描述，只在意外处详写]

**体感问题**:
1. [描述] — 感受：[困惑/沮丧/...]

### 🐛 技术问题清单（证据链必备）
| # | 操作（截图+tap/curl） | 预期 | 实际（State Oracle/Logcat） | 归因 | 严重程度 |
|---|---------------------|------|---------------------------|------|---------|

### 🔭 debug 盲区观察（需人工复核）
- **现象** / **为什么是盲区** / **人工验证方法**

### 💡 设计建议（可选）
```

### Step 4.5: /think 评估+决策（质量关卡）

报告写完后、分流归档前，调用 `/think --quick` **同时做技术判断和产品决策**：

1. **Bug 真实性** — 证据链完整吗？是真 bug 还是 debug server 限制？
2. **建议合理性** — 值得修复吗？维持现状成本多高？
3. **产品+技术决策** — 对每个发现直接拍板：进 TODO / 丢弃 / 无法决策
4. **Skill 自检** — 执行中 skill 本身有问题吗？（有 → TODO 由 AI 自行修复）

> 用 `--quick`（DeepSeek），cheap sanity check。不可用时跳过，标注"未经评估"。
> `/think` 能拍板的直接转 TODO 或丢弃，**只有明确无法决策的才进 to-discuss.md**。

### Step 5: 分流归档

#### 5a. /think 已决策 → TODO.md 或丢弃
有证据链的技术问题 + `/think` 确认的产品/架构决策 → TODO.md。噪音 → 丢弃。
**盲区观察不进 TODO.md**。

#### 5b. /think 无法决策 → to-discuss.md（极少数情况）

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/explore-YYYY-MM-DD.md § 章节)
- **事实前提**: [一句话客观现象 + Ref 引用，不重复展开]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Reject → 直接删
```

**绝对禁止**：观点伪装成 bug、盲区伪装成 bug、跳过 `/think` 直接塞 to-discuss、从截图脑补因果、加置信度、TODO/to-discuss 设指针。

---

## Fallback 模式（纯 curl）

当 adb 设备不可用时自动降级。

**诚实声明**：Fallback 模式下探索范围 = Debug Server 端点数量。无法覆盖页面导航、手势交互、动画流程。

**执行流程**：同 Cyborg 的 Step 1 → Step 4 → Step 4.5 → Step 5，但 Step 2 改为 curl 端点操作 + Logcat 辅助。

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮，总共不超过 2 轮
2. **不穷举边界、不跑故事** — 那是 android-qa-stories 的事
3. **三证据源** — 截图（UI）+ State Oracle（状态）+ Logcat（异常），配合归因
4. **保持人设一致**
5. **探索后必须恢复数据**
6. **报告落盘** — `_scratch/` + TODO.md（/think 已决策）+ to-discuss.md（仅 /think 无法决策时）+ 盲区留在报告
