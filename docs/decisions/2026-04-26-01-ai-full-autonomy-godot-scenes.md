# AI 全权闭环改 .tscn / .tres + 截图验证替代"AI 不动场景"硬规则（game-mvp）

- **Date**: 2026-04-26
- **Status**: Accepted
- **Scope**: 项目级 `~/LittleTree_Projects/game-mvp/CLAUDE.md`（"测试金字塔" / "视觉参数隔离 (BattleConfig)" / "UI 组件开发规范" / "禁止事项" 四段）
- **Triggered by**: 评估 godot-mcp（https://github.com/Coding-Solo/godot-mcp）接入时，Founder 反问"AI 直接改 .tscn 和编辑器拖拽的区别在哪里？"

## 1. 问题 (What went wrong)

`game-mvp/CLAUDE.md` 原有两条规则：

> - **AI 不做**：布局微调（留给人在编辑器中拖拽）
> - **AI 只改 .gd 逻辑，不改 .tres 数值**（数值由产品负责人在 Godot 编辑器中调整）

这两条规则的隐含前提是「人类会在编辑器里调」。但 game-mvp 的协作模式是 **AI-Only**（全局 CLAUDE.md 第一段已声明：Founder 是产品负责人，定义需求、审批方向、验收效果，**不存在人类程序员介入**）。

实际效果：Founder 自述不做编辑器操作 → AI 又被规则禁止做 → UI / 视觉数值流程**整体停滞**。

讨论触发点是 godot-mcp 评估，AI 用"AI 不动 .tscn 的边界冲突"作为不接入的核心论据。Founder 反问："那我又不去做拖拽，你这个能力到底有没有？编辑器和直接写代码的区别到底在哪？"——直接戳穿了规则与协作模式不一致的盲点。

这是一个典型的 **AI 沿用前置假设、未对齐 AI-Only 协作模式** 的规则腐烂案例。

## 2. 讨论过程 (How we thought about it)

### Round 1：重新检查 AI 改 .tscn 的真实能力边界

| 任务 | AI 直接写文本 vs 编辑器 | 评估 |
|---|---|---|
| 加节点 / 连脚本 / 设属性 / `anchors_preset` | 等价 | ✅ 可做 |
| StyleBoxFlat 颜色 / 圆角 / Margin | 数字写得了，但盲调 | ⚠️ 需截图反馈 |
| UID / 资源 `id="N_xxx"` 管理 | 手写易撞 ID | ⚠️ 需校验 |
| AnimationPlayer 关键帧时间轴 | 文本啰嗦但可做 | ⚠️ 慢 |
| TileMap 绘制 / 曲线编辑 / Shader 可视调参 | 没有图形界面 | ❌ 做不了 |

结论：**除了少数必须图形界面的操作，AI 直接编辑文本和编辑器拖拽等价**。"AI 不能改 .tscn"在能力层面就是错判。

### Round 2：闭环是否成立的关键 = 截图反馈链

原规则"AI 看不见结果"的隐含前提，已被 **Debug Play Server**（项目 2026-04 之前已实现的内嵌 HTTP server）推翻：

- `localhost:9999/play/goto_xxx` 返回 JSON 状态 + `_screenshot` 路径
- AI 用 `Read` 工具读截图，自己判断渲染是否符合预期
- 不满意再改 → 再截 → 再判断

这是一个真正的自主闭环，与"改 `.gd` → 跑 GUT 测试 → 失败再改"同构。规则当年写下时如果 Debug Play Server 还没成熟可以理解，但现在它已经是项目支柱。

### Round 3：godot-mcp 评估的真实结论

godot-mcp 的 `add_node` / `create_scene` / `load_sprite` 本质是 .tscn 文本编辑的**薄封装**，不解锁新能力（`Write` + `Edit` 已能做）。真正决定 UI 闭环成立的是**截图反馈链**（项目自有的 Debug Play Server），不是这个 MCP。

不接入 godot-mcp 的理由换成：

1. 工具是 .tscn 文本编辑的封装，`Write` / `Edit` + `tools/scene_index.sh` 已覆盖
2. UI 闭环的真正发动机在 Debug Play Server，不在 MCP
3. 引入需要 Node.js ≥18 进程，违反全局铁律 6"依赖审慎"

## 3. 决议 (What we decided)

### 3.1 game-mvp/CLAUDE.md 规则变更（已落地）

**视觉参数隔离 (BattleConfig)**：删除"AI 只改 .gd，不改 .tres"，改为 AI 可改 .tres 数值，但必须通过 Debug Play Server 实战验证手感（截图 + 关键数值快照作为凭证）。

**UI 组件开发规范**：删除"AI 不做布局微调"，改为 "AI 全权负责 .tscn / .tres / 数据绑定 / 事件连接"，强制配套截图验证闭环。新增 **UID / 资源 ID 安全**子条款（手写场景文件易撞 ID 的兜底）。

**让位项明确收敛**：仅以下三类需要 Founder 介入（因为没有截图能闭环）：
- Shader 可视调参（实时预览滑块）
- TileMap 绘制（瓦片批量摆放）
- AnimationPlayer 复杂时间轴关键帧（贝塞尔曲线手调）

**禁止事项 +1**：不在缺截图凭证的情况下交付 UI / .tscn / .tres 改动。

**测试金字塔**：UI 渲染从"靠人眼验证"改为"通过 Debug Play Server 截图闭环"。

### 3.2 godot-mcp 不接入

理由换为：

1. `add_node` / `create_scene` 是 .tscn 文本编辑的薄封装，`Write` / `Edit` 已覆盖
2. UI 闭环的真正发动机在 Debug Play Server
3. 引入需要 Node.js ≥18 进程，违反"依赖审慎"

## 4. 拒绝的方案 (What we did not pick)

### 选项 A：接入 godot-mcp 让它做场景操作

拒因：
- 不解锁新能力（只是文本编辑封装）
- 增加 Node.js 依赖和一个常驻 MCP 进程
- 项目自有 Debug Play Server 已是更高层次抽象（业务级 `deploy_unit` / `start_battle`）

### 选项 B：保持原规则，Founder 偶尔在编辑器里调

拒因：
- 与 AI-Only 协作模式直接冲突（Founder 自述不做编辑器操作）
- 实际效果是流程卡死，UI / 数值长期停滞

### 选项 C：AI 改 .tscn 但不强制截图验证

拒因：
- 与全局铁律 5"完成 = 亲眼观测到代码在 Runtime 生效"冲突
- UI 改动盲改是高风险（anchors / StyleBox 是数字游戏，改错了不报错只是丑）
- 失去截图凭证 = 失去与铁律 5 的衔接

## 5. 验证 (How to verify)

下次 UI / .tscn 改动应该呈现：

- AI 直接编辑场景文件，不再让位 Founder
- 提交前必须 curl Debug Play Server 拿截图，`Read` 后作为验证凭证
- commit message / 交付总结里包含截图路径或场景启动验证记录

如果发现 AI 在缺截图凭证时交付，或仍声称"不做布局微调"留给 Founder，说明规则没生效，需要回查本决策记录。

## 6. 元层教训 (Meta lesson)

**AI-Only 项目里，写规则时要警惕"假定人类在场"的暗夹层**。原规则不是技术错误，而是**协作模式漂移**：项目早期可能仍有 Founder 偶尔动手的预期，全局 CLAUDE.md 后来声明 AI-Only，但项目级规则没同步刷新。

**触发器**：当 AI 用某条规则反对一个操作时，先问自己"这条规则的隐含前提里有没有'人类会做 X'？AI-Only 模式下这个前提还成立吗？"。本次是 Founder 反问把这个盲点打出来的，AI 自己应该能更早自检。
