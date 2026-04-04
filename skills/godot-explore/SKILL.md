---
name: godot-explore
description: >
  This skill should be used when AI should autonomously explore a running
  Godot game as a player, discovering bugs and UX issues through role-play.
  AI picks a player persona, plays the game freely via DebugPlayServer,
  and reports experience + technical issues. Use when the user says
  "探索游戏", "自由探索", "玩一下", "explore", "playtest", or after
  qa-stories passed and deeper exploration is needed. Requires DebugPlayServer
  running (port 9999).
version: 0.1.0
---

# Godot Explore — 角色扮演式自主探索

AI 扮演玩家自由游玩游戏，通过第一人称体验发现 bug 和设计问题。不是机械测试，而是真正在"玩"。

## 核心原则

- **我是玩家，不是测试工程师** — 用玩家思维做决策，不穷举边界
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码
- **主观感受和客观 bug 都记** — 体验报告 + 技术问题清单
- **每步看截图** — 操作后用 Read 查看 `_screenshot`，观察 UI 反馈

---

## 前置条件

1. DebugPlayServer 运行中（端口 9999）
2. `godot-qa-stories` 已在本会话通过

如果 qa-stories 未执行，**先调用它**。在故障基线上探索只会产生噪音。

---

## 执行流程

### Step 1: 建立玩家认知

读取项目文档，理解"我是谁、我为什么玩这个游戏"：

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
读 Core/Autoloads/DebugPlayServer.gd 的 _route 函数 → 我能执行哪些操作
```

**选择本轮玩家人设**（从预设池选一个，或根据项目特点自拟）：

| 人设 | 行为倾向 | 自然覆盖的系统 |
|------|---------|--------------|
| 🐣 新手小白 | 不看教程，乱点，金币乱花 | 引导缺失、容错性 |
| 💰 经济运营玩家 | 精打细算，攒钱升级，晚出高级兵 | 经济平衡、升级体验 |
| ⚡ 速攻玩家 | 最快速度推完，跳过一切 | 流程流畅度、跳过逻辑 |
| 🌱 养成玩家 | 反复刷关卡，关注兵团成长 | 存档、跨局养成、重复体验 |

### Step 2: 自由游玩

**每轮 = 一次完整游玩循环**（营地 → 战斗 × N → 结算 → 回营地）。建议 1-3 轮，每轮换人设。

#### 游玩规则

1. **第一人称内心独白**：每步操作前，用玩家视角写一句决策理由：
   > "金币只有 200，士兵要 80…我只能放 2 个，先放弓箭手试试远程"

2. **每步操作后看截图**：`Read` 查看 `_screenshot` 路径，观察 UI 反馈

3. **做符合人设的决策**：
   - 新手会乱点、不看说明
   - 经济玩家会先查价格再决定
   - 速攻玩家会跳过一切直接开打

4. **遇到异常时**：
   - 技术异常（curl 报错/状态不一致）→ 记录到技术问题清单，继续玩
   - 体验困惑（不知道该干嘛/UI 看不懂）→ 记录到体验报告，继续玩
   - Server 完全无响应 → 停止，输出已收集的报告

#### 可用操作速查

**导航**：
```bash
curl -s -X POST localhost:9999/play/goto_camp
curl -s -X POST localhost:9999/play/goto_battle -d '{"level":1}'
curl -s -X POST localhost:9999/play/goto_world_map
curl -s -X POST localhost:9999/play/goto_menu
```

**战斗**：
```bash
curl -s -X POST localhost:9999/play/confirm_commander
curl -s -X POST localhost:9999/play/deploy_unit -d '{"unit_index":0,"grid_x":3,"grid_y":10}'
curl -s -X POST localhost:9999/play/start_battle -d '{"speed":8}'
curl -s localhost:9999/play/wait_battle_end
curl -s -X POST localhost:9999/play/skip_wave
curl -s -X POST localhost:9999/play/kill_all_enemies
```

**状态查询**：
```bash
curl -s localhost:9999/state/game      # 金币、人口
curl -s localhost:9999/state/save      # 存档
curl -s localhost:9999/state/battle    # 战斗状态（仅战斗中）
curl -s localhost:9999/state/commander # 指挥官
curl -s localhost:9999/state/units     # 兵种
```

**调试**：
```bash
curl -s -X POST localhost:9999/play/add_gold -d '{"amount":500}'
curl -s -X POST localhost:9999/play/add_gems -d '{"amount":100}'
curl -s -X POST localhost:9999/play/save_reset
curl -s -X POST localhost:9999/time_scale -d '{"scale":8}'
curl -s -X POST localhost:9999/play/select_commander -d '{"index":0}'
curl -s -X POST localhost:9999/play/blacksmith_upgrade -d '{"unit_id":"soldier","stat":"hp"}'
```

> 调试类操作（add_gold 等）新手/速攻人设不该用；经济/养成人设也应尽量少用，保持真实体验。

### Step 3: 输出报告

```markdown
## 探索报告

### 环境
- 项目: Barracks Clash | 端口: 9999 | 时间: xxx
- 基线: qa-stories 全部通过
- 本轮人设: 🐣 新手小白

### 🎮 玩家体验

#### 第一轮: [人设名]
> [2-3 段第一人称体验描述]
> "打开游戏，看到三个建筑但不知道先去哪个…"
> "第一场战斗金币不够，只放了一个兵就开打了，被秒了…"

**体感问题**:
1. [描述] — 感受：[困惑/沮丧/无聊/...]
2. ...

#### 第二轮: [人设名]
> ...

### 🐛 技术问题清单
| # | 描述 | 复现 curl | 实际返回 | 严重程度 |
|---|------|----------|---------|---------|
| 1 | xxx | `curl ...` | `{...}` | 高/中/低 |

### 💡 设计建议（可选）
- [建议] — 基于 [哪个人设的体验]

### 建议补充的 User Stories
- [如果发现了重要但未被故事覆盖的路径]
```

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮游玩循环，总共不超过 3 轮
2. **不穷举边界** — 那是 qa-stories 的事。这里靠自然游玩发现问题
3. **截图是关键输入** — 每步操作后必须 Read 截图，UI 反馈是体验的核心
4. **curl JSON 参数** — 单引号包裹：`-d '{"level":1}'`
5. **单任务锁** — Server 同时只处理一个请求，429 = 忙，稍后重试
6. **保持人设一致** — 新手不会精确计算 DPS，经济玩家不会乱花钱
