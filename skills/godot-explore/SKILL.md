---
name: godot-explore
description: >
  Use when the user says "探索游戏", "自由探索", "用一下", "explore", "playtest",
  or after godot-qa-stories passed and deeper exploration is needed. AI
  role-plays as a player to discover bugs and UX issues via DebugPlayServer.
  Primary mode: curl-driven exploration. Optional Cyborg mode (Vision + cliclick)
  for UI-heavy scenes. Requires DebugPlayServer embedded in the game.
version: 3.0.0
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

1. DebugPlayServer 运行中（端口从 `Core/Autoloads/DebugPlayServer.gd` 动态发现）
2. 基线数据就绪（存档/关卡进度可用于游玩）

**基线不足时，只做最小 seed**。想验证 stories 的用户应调用 `/godot-qa-stories`。

---

## 执行流程

### Step 0: 发现端口

```bash
# 从源码读取 PORT 常量（禁止硬编码）
PORT=$(grep -E '^const PORT' Core/Autoloads/DebugPlayServer.gd | grep -oE '[0-9]+' | head -1)
echo "Godot debug port: $PORT"

# 检查 Server 可达
curl -s --connect-timeout 3 localhost:$PORT/ping
```

### Step 1: 建立玩家认知

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
curl localhost:$PORT/providers → 可用端点（验证用）
```

**动态生成本轮玩家人设**（每次探索 1 个人设，多次运行覆盖不同维度）：

调用 `/think --quick`，输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要，要求生成 **1 个**贴合该游戏的玩家人设：

```
请根据以下游戏信息，生成一个玩家人设用于游戏探索测试。

游戏信息：
[粘贴 PRODUCT_SOUL 核心段落 + PRODUCT_BEHAVIOR 核心玩法]

要求输出格式：
- 人设名称：[emoji + 2-4字名称]
- 背景故事：[1句话，这个玩家是谁、为什么会玩这个游戏]
- 行为倾向：[2-3个关键词，如"急躁、目标导向、乱花钱"]
- 自然覆盖：[这个人设天然会测到的维度]
- 游玩计划：[3-5句，以第一人称描述这次打开游戏要干什么]

要求：
- 人设必须贴合这个游戏的目标玩家群，不要通用角色
- 行为倾向要具体到能指导"打什么关、升什么、跳过什么"
- 随机发挥，不要每次都生成类似的角色
```

> **不做去重** — 靠 DeepSeek 随机性 + 产品上下文自然分散，用户多次运行覆盖。
>
> **/think 不可用时**，回退到以下任一默认人设：
> 🐣 新手小白 | 💰 经济运营玩家 | ⚡ 速攻玩家 | 🌱 养成玩家

收到 /think 返回后，**在探索开头写出完整人设信息**，然后进入 PAV 循环。

### Step 2: 自由游玩

每步操作遵循 **PAV 循环**（Perceive → Act → Verify）：

#### P — 感知

```bash
# 通过 DebugPlayServer 的截图端点（如有）或直接查看游戏窗口
curl -s localhost:$PORT/state/game    # 当前经济/进度
curl -s localhost:$PORT/state/battle  # 战斗中状态
```

如需视觉确认（Cyborg 可选）：
```bash
# 截取 Godot 窗口
screencapture -R {win_x},{win_y},{win_w},{win_h} /tmp/godot_screen_N.png
```

#### A — 行动（人设驱动）

```bash
# 导航
curl -s -X POST localhost:$PORT/play/goto_camp
curl -s -X POST localhost:$PORT/play/goto_battle -d '{"level":1}'

# 战斗
curl -s -X POST localhost:$PORT/play/confirm_commander
curl -s -X POST localhost:$PORT/play/deploy_unit -d '{"unit_index":0,"grid_x":3,"grid_y":10}'
curl -s -X POST localhost:$PORT/play/start_battle -d '{"speed":8}'
curl -s localhost:$PORT/play/wait_battle_end

# 经济（谨慎使用 — 调试类操作破坏真实体验）
curl -s -X POST localhost:$PORT/play/add_gold -d '{"amount":500}'
```

> 调试类操作（add_gold 等）新手/速攻人设不该用；经济/养成人设也应尽量少用。

#### V — 验证

```bash
curl -s localhost:$PORT/state/game      # 金币/人口变化
curl -s localhost:$PORT/state/save      # 存档状态
curl -s localhost:$PORT/state/units     # 兵种状态
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
curl -s -X POST localhost:$PORT/play/save_reset
```

无重置端点时提醒用户存档已被修改。

### Step 4: 输出报告

写入 `_scratch/explore-YYYY-MM-DD.md` + 打印到对话。

```markdown
## 探索报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx
- 模式: curl 驱动 / Cyborg 辅助
- 基线: [seed 数据 / 用户提供存档]
- 本轮人设: 🐣 新手小白

### 🎮 玩家体验

#### [人设名]: [背景故事一句话]
> 行为倾向: [关键词]
> 自然覆盖: [维度]
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

### Step 4.5: /think 评估+决策（质量关卡）

报告写完后、分流归档前，调用 `/think --quick` **同时做技术判断和产品决策**：

1. **Bug 真实性** — 证据链完整吗？是真 bug 还是 server 限制？
2. **建议合理性** — 值得修复吗？
3. **产品+技术决策** — 对每个发现直接拍板：进 TODO / 丢弃 / 无法决策
4. **Skill 自检** — 执行中 skill 本身有问题吗？（有 → TODO 由 AI 自行修复）

> 用 `--quick`（DeepSeek）。不可用时跳过，标注"未经评估"。
> `/think` 能拍板的直接转 TODO 或丢弃，**只有明确无法决策的才进 to-discuss.md**。

### Step 5: 分流归档

#### 5a. /think 已决策 → TODO.md 或丢弃
有证据链的技术问题 + `/think` 确认的产品/架构决策 → TODO.md。噪音 → 丢弃。
**盲区观察不进 TODO.md**。

#### 5b. /think 无法决策 → to-discuss.md（极少数情况）

```markdown
## [UX|Gameplay|Economy|Workflow] 简短标题 (Ref: _scratch/explore-YYYY-MM-DD.md § 章节)
- **事实前提**: [一句话客观现象 + Ref 引用，不重复展开]
- **/think 结论**: [/think 给出了什么判断，为什么无法拍板]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Reject → 直接删
```

**绝对禁止**：观点伪装成 bug、盲区伪装成 bug、跳过 `/think` 直接塞 to-discuss、从截图脑补因果、加置信度、TODO/to-discuss 设指针。

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮，总共不超过 2 轮
2. **不穷举边界、不跑故事** — 那是 godot-qa-stories 的事
3. **保持人设一致** — 新手不会精确计算 DPS，经济玩家不会乱花钱
4. **探索后必须恢复数据**
5. **报告落盘** — `_scratch/` + TODO.md（/think 已决策）+ to-discuss.md（仅 /think 无法决策时）+ 盲区留在报告
