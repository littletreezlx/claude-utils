---
name: godot-explore
description: >
  AI autonomously explores a running Godot game as a player, discovering bugs
  and UX issues through role-play. Primary mode: curl-driven exploration via
  DebugPlayServer's rich endpoint set. Optional Cyborg mode (Vision + cliclick)
  for UI-heavy scenes. Use when the user says "探索游戏", "自由探索", "��一下",
  "explore", "playtest", or after qa-stories passed and deeper exploration
  is needed. Requires DebugPlayServer running (port 9999).
version: 2.0.0
---

# Godot Explore — 角色扮演式自主探索

AI 扮演玩家自由游玩游戏。通过 DebugPlayServer 的丰富端点驱动游戏流程，截图观察画面效果，State Oracle 验证状态变化。

## 核心原则

- **决策时是玩家，报告时是工程师** — 用玩家人设决定操作顺序，但报告问题必须走证据链
- **归因必须有证据链** — Bug = 操作 X → State Oracle 返回 Y → 与预期 Z 不符。缺任一环 → 盲区观察，不是 bug
- **端点丰富 ≠ 自由探索** — DebugPlayServer 有导航/战斗/经济端点，覆盖远好于 Flutter Debug Server，但仍无法覆盖纯客户端动效和精确输入操作
- **不做故事验证** — 那是 godot-qa-stories 的职责
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码

---

## 模式说明

**主模式：curl 驱动**（DebugPlayServer 端点覆盖度高）
- 导航：goto_camp / goto_battle / goto_world_map / goto_menu
- 战斗：deploy_unit / start_battle / wait_battle_end / skip_wave
- 经济：add_gold / add_gems / blacksmith_upgrade
- 状态：/state/game / /state/save / /state/battle / /state/units

**可选 Cyborg 模式**（桌面 Godot 窗口 + screencapture + cliclick）
- 适用场景：UI 菜单交互、按钮点击等 DebugPlayServer 未覆盖的界面操作
- 技术方案与 Flutter Cyborg 相同：`screencapture -R` + `cliclick c:X,Y` + 公式 `screen = win_origin + image_px/2`
- **非必需**：大多数探索场景靠 curl 端点就够了

---

## 前置条件

1. DebugPlayServer 运行中（端口 9999）
2. 基线数据就绪（存档/关卡进度可用于游玩）

**基线不足时，只做最小 seed**。想验证 stories 的用户应调用 `/godot-qa-stories`。

---

## 执行流程

### Step 1: 建立玩家认知

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
读 Core/Autoloads/DebugPlayServer.gd 的 _route 函数 → 可用操作
```

**选择本轮玩家人设**（1-2 轮，每轮换人设）：

| 人设 | 行为倾向 | 自然覆盖 |
|------|---------|---------|
| 🐣 新手小白 | 不看教程，乱点，金币乱花 | 引导缺失、容错性 |
| 💰 经济运营玩家 | 精打细算，攒钱升级 | 经济平���、升级体验 |
| ⚡ 速攻玩家 | 最快速度推完 | 流程流畅度、跳过逻辑 |
| 🌱 养成玩家 | 反复刷关卡，关注成长 | 存档、跨局养成、重复体验 |

**每轮开头写 3-5 句游玩计划**：
> "我是新手小白，第一次打开游戏。计划：看看营地有什么 → 随便选个指挥官 → 打第一关试试 → 看看钱够不够升级。"

### Step 2: 自由游玩

每步操作遵循 **PAV 循环**（Perceive → Act → Verify）：

#### P — 感知

```bash
# 通过 DebugPlayServer 的截图端点（如有）或直接查看游戏窗口
curl -s localhost:9999/state/game    # 当前经济/进度
curl -s localhost:9999/state/battle  # 战斗中状态
```

如需视觉确认（Cyborg 可选）：
```bash
# 截取 Godot 窗口
screencapture -R {win_x},{win_y},{win_w},{win_h} /tmp/godot_screen_N.png
```

#### A — 行动（人设驱动）

```bash
# 导航
curl -s -X POST localhost:9999/play/goto_camp
curl -s -X POST localhost:9999/play/goto_battle -d '{"level":1}'

# 战斗
curl -s -X POST localhost:9999/play/confirm_commander
curl -s -X POST localhost:9999/play/deploy_unit -d '{"unit_index":0,"grid_x":3,"grid_y":10}'
curl -s -X POST localhost:9999/play/start_battle -d '{"speed":8}'
curl -s localhost:9999/play/wait_battle_end

# 经济（谨慎使用 — 调试类操作破坏真实体验）
curl -s -X POST localhost:9999/play/add_gold -d '{"amount":500}'
```

> 调试类操作（add_gold 等）新手/速攻人设不该用；经济/养成人设也应尽量少用。

#### V — 验证

```bash
curl -s localhost:9999/state/game      # 金币/人口变化
curl -s localhost:9999/state/save      # 存档状态
curl -s localhost:9999/state/units     # 兵种状态
```

**异常处理**：
- State Oracle 返回异常 → 记录为技术问题（含触发 curl + 响应）
- 截图与 State 不一致 → 记录为可疑 bug
- Server 429 → 单任务锁，稍后重试

### 截图策略

**必须截图**（如有视觉通道）：每轮起始、场景切换、战斗结束、预期外变化
**不需截图**：连续同类操作、State Oracle 已确认正确

### 使用规则

1. **破坏性操作放到每轮末尾**（save_reset 等）
2. **过程中只在遇到意外时写反应**
3. **curl JSON 参数**用单引号包裹：`-d '{"level":1}'`
4. **单任务锁**：Server 同时只处理一个请求，429 = 忙

### Step 3: 数据恢复

```bash
# 如有存档重置端点
curl -s -X POST localhost:9999/play/save_reset
```

无重置端点时提醒用户存档已被修改。

### Step 4: 输出报告

写入 `_scratch/explore-YYYY-MM-DD.md` + 打印到对话。

```markdown
## 探索报告

### 环境
- 项目: xxx | 端口: 9999 | 时间: xxx
- 模式: curl 驱动 / Cyborg 辅助
- 基线: [seed 数据 / 用户提供存档]
- 本轮人设: 🐣 新手小白

### 🎮 玩家体验
#### 第一轮: [人设名]
> [游玩计划 3-5 句]
> [2-3 段体验描述，只在意外处详写]

**体感问题**:
1. [描述] — 感受：[困惑/沮丧/无聊/...]

### 🐛 技术问题清单（证据链必备）
| # | 触发 curl | 预期 | 实际（State Oracle） | 归因 | 严重程度 |
|---|----------|------|---------------------|------|---------|

### 🔭 debug 盲区观察（需人工复核）
- **现象** / **为什么是盲区** / **人工验证方法**

### 💡 设计建议（可选）
```

### Step 4.5: /think 评估（质量关卡）

报告写完后、分流归档前，调用 `/think --quick` 对发现进行 sanity check：

1. **Bug 真实性** — 证据链完整吗？是真 bug 还是 server 限制？
2. **建议合理性** — 值得 filing 吗？
3. **Filing 决策** — TODO / to-discuss / 丢弃
4. **Skill 自检** — 执行中 skill 本身有问题吗？（有 → to-discuss）

> 用 `--quick`（DeepSeek）。不可用时跳过，标注"未经评估"。

### Step 5: 分流归档（严禁混流）

#### 5a. 事实型 bug → TODO.md
有证据链的技术问题。带 Ref 引用。**盲区观察不进 TODO.md**。

#### 5b. 观点/判断型 → to-discuss.md

```markdown
## [UX|Gameplay|Economy|Workflow] 简短标题 (Ref: _scratch/explore-YYYY-MM-DD.md § 章节)
- **事实前提**: [一句话客观现象 + Ref 引用，不重复展开]
- **AI 观点**: [我认为应该...]
- **反面检验**: [可能错在哪 / 维持现状的理由 / 是否人设偏见]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Discuss → /think 或 /feat-discuss-local-gemini
  - [ ] Reject → 直接删
```

**绝对禁止**：观点伪装成 bug、盲区伪装成 bug、从截图脑补因果、加置信度、TODO/to-discuss 设指针。

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮，总共不超过 2 轮
2. **不穷举边界、不跑故事** — 那是 godot-qa-stories 的事
3. **保持人设一致** — 新手不会精确计算 DPS，经济玩家不会乱花钱
4. **探索后必须恢复数据**
5. **报告落盘** — `_scratch/` + TODO.md + to-discuss.md + 盲区留在报告
