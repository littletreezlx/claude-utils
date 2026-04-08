---
name: ai-explore
description: >
  AI autonomously explores a running Flutter app as a user, discovering bugs
  and UX issues through role-play. Supports two modes: Cyborg (Vision + OS Tap
  + State Oracle, default when Simulator available) and Fallback (curl-only,
  when no Simulator). Use when the user says "探索应用", "自由探索", "用一下",
  "explore", "find bugs", or after qa-stories passed and deeper exploration
  is needed. Requires Debug State Server running.
version: 3.0.0
---

# AI Explore — Cyborg 自主探索

AI 扮演用户自由使用应用。Cyborg 模式下通过**视觉识别 + OS 级点击**真正操作 UI，State Oracle 验证状态变化。

## 核心原则

- **Cyborg = 皮（Vision+Tap），Oracle = 骨（State 验证）** — 截图感知 UI，`/cyborg/tap` 内部注入驱动交互，curl 验证状态。三层配合，缺一不可
- **零坐标转换** — `/cyborg/tap?nodeId=X` 通过语义节点 ID 注入事件，绕过坐标系转换，100% 精准命中
- **决策时是用户，报告时是工程师** — 用人设决定点哪里，但报告问题必须走证据链
- **归因必须有证据链** — Bug = 操作 X → State Oracle 返回 Y → 与预期 Z 不符。缺任一环 → 盲区观察，不是 bug
- **不做故事验证** — 那是 qa-stories 的职责
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码

---

## 模式选择（自动判断）

启动时执行环境检测，决定探索模式：

```bash
# 检测 Cyborg 模式前置条件
pgrep -x Simulator >/dev/null 2>&1 && \
  curl -s localhost:8788/providers >/dev/null 2>&1 && \
  curl -s 'localhost:8788/cyborg/dom' | python3 -c "import sys,json; d=json.load(sys.stdin)['data']; assert d['totalCount']>0" 2>/dev/null
```

| 条件 | 模式 | 探索能力 |
|------|------|---------|
| Simulator + Debug Server + `/cyborg/dom` 返回节点 | **Cyborg** | 真实 UI 交互 + 导航 + 手势 + State 验证 |
| 仅 Debug Server 可用（无 Simulator 或 Cyborg Probe 不可用） | **Fallback** | 端点覆盖测试（诚实声明：探索范围 = 端点数量，无法覆盖导航/手势/动画） |

---

## 前置条件

### ⚠️ 必须先运行 prep-cyborg-env

**每次开始探索前，必须先调用 `prep-cyborg-env` Skill 或运行 `./scripts/prep-env.sh`**，确保环境干净。

详见 `prep-cyborg-env` Skill 文档。核心流程：
1. Kill 所有 Flutter 进程
2. Seed 测试数据
3. `--force-reset` 启动 App
4. 验证 State 和 Data 一致

**严禁在脏状态下开始探索**——三角验证会在矛盾的状态下给出错误结论。

### 共同条件
1. ✅ prep-cyborg-env 已执行（环境干净）
2. Debug State Server 运行中（localhost:8788）
3. 基线数据就绪（有可用 group/option 等数据）

### Cyborg 额外条件
4. iOS Simulator 运行中且 App 已启动
5. `/cyborg/dom` 返回节点（semantics tree 启用）
6. macOS 环境（screencapture、osascript，仅截图用）

---

## Cyborg 模式执行流程

### Step 0: 环境初始化

验证 Cyborg Probe 端点可用：

```bash
# 验证 /cyborg/dom 返回节点（semantics tree 已启用）
curl -s localhost:8788/cyborg/dom | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
print(f'Nodes: {d[\"totalCount\"]}, screen={d[\"screenSize\"]}')
"

# 验证 /cyborg/tap 可用
curl -s 'localhost:8788/cyborg/tap?nodeId=0' | python3 -c "import sys,json; print(json.load(sys.stdin))"
```

> /cyborg/dom 返回 0 nodes → semantics 未启用，需要重启 App（`start-dev.sh --force-reset`）

获取 Simulator 窗口参数（仅截图用，tap 不需要）：

```bash
osascript -e 'tell application "System Events" to tell process "Simulator" to get {position, size} of front window'
# 返回示例: {393, 30}, {237, 558}
```

### Step 1: 建立用户认知

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
curl localhost:8788/providers  → 可用的 state/data 端点（验证用）
```

**动态生成本轮用户人设**（每次探索 1 个人设，用户多次运行覆盖不同维度）：

调用 `/think --quick`，输入 PRODUCT_SOUL + PRODUCT_BEHAVIOR 摘要，要求生成 **1 个**贴合该 App 的用户人设：

```
请根据以下产品信息，生成一个用户人设用于 App 探索测试。

产品信息：
[粘贴 PRODUCT_SOUL 核心段落 + PRODUCT_BEHAVIOR 核心交互]

要求输出格式（严格遵守）：
- 人设名称：[emoji + 2-4字名称]
- 背景故事：[1句话，这个人是谁、为什么会用这个App]
- 行为倾向：[2-3个关键词，如"急躁、目标导向、不看说明"]
- 自然覆盖：[这个人设天然会测到的维度，如"流程流畅度、错误提示"]
- 使用计划：[3-5句，以第一人称描述这次打开App要干什么]

要求：
- 人设必须贴合这个 App 的目标用户群，不要通用角色
- 行为倾向要具体到能指导"点哪里、跳过什么"
- 随机发挥，不要每次都生成类似的角色
```

> **为什么用 DeepSeek 生成？** 静态人设表无法贴合每个 App 的用户画像。动态生成让人设与产品上下文对齐，每次运行自然覆盖不同维度。
> 
> **不做去重** — 靠 DeepSeek 自身随机性 + 产品文档上下文自然分散。用户多次运行即可覆盖。
> 
> **如果 /think 不可用**（API 故障等），回退到以下任一默认人设继续探索：
> 🐣 新手小白（不看引导随手点）| ⚡ 效率达人（最快完成目标）| 🐒 混乱操作者（逆序操作密集请求）

收到 `/think` 返回后，**在探索开头写出完整人设信息**，然后进入 PAV 循环。

### Step 2: 感知-行动-验证循环

每步操作遵循 **PAV 循环**（Perceive → Act → Verify）：

#### P — 感知（语义树 + 截图）

**优先使用 Cyborg Probe 语义树获取精准坐标**：

```bash
# 1. 查询语义树（获取 widget 坐标）
curl -s localhost:8788/cyborg/dom | python3 -m json.tool
```

语义树返回结构化 JSON：
```json
{
  "nodes": [
    {
      "id": 1,
      "label": "骰子",
      "role": "button",
      "rect": {"x": 100, "y": 200, "width": 50, "height": 50},
      "center": {"x": 125, "y": 225},
      "hasTap": true
    }
  ],
  "screenSize": {"width": 390, "height": 844}
}
```

**AI 直接使用 `center` 坐标进行点击**：
- 找到目标 widget（如 `label="骰子"`）
- 使用 `center.x` 和 `center.y` 作为点击坐标
- 无需截图和坐标转换

**截图仅用于视觉确认**（当语义树不足以判断 UI 状态时）：

```bash
# 激活 Simulator 窗口
osascript -e 'tell application "Simulator" to activate'
sleep 0.3

# 截取 Simulator 窗口（-R = region, macOS 屏幕点坐标）
screencapture -R {win_x},{win_y},{win_w},{win_h} /tmp/cyborg-poc/step_N.png
```

**辅助定位**：结合 State Oracle 缩小搜索范围：
```bash
curl -s localhost:8788/state/route     # 当前在哪个页面
curl -s localhost:8788/state/overlays  # 是否有弹窗
```

#### A — 行动（内部事件注入，无需坐标转换）

**主力方式：`/cyborg/tap?nodeId=X`（语义动作注入）**

```bash
# 直接用 node ID 触发 tap — 零坐标转换，100% 精准
curl -s 'localhost:8788/cyborg/tap?nodeId=12'
# → {"ok":true,"data":{"action":"tap","nodeId":12,"status":"dispatched"}}

# 长按
curl -s 'localhost:8788/cyborg/longPress?nodeId=12'

# 文字输入（直接注入到 TextField，绕过键盘）
curl -s 'localhost:8788/cyborg/input?nodeId=7&text=hello'

# 滚动
curl -s 'localhost:8788/cyborg/scroll?nodeId=8&direction=down'
```

**⚠️ 关键：导航后 node ID 会变！** 每次页面切换后必须重新查询 DOM 获取最新 ID。

**查找目标节点的标准流程**：

```bash
# 1. 获取 DOM
# 2. 找到目标（如 label 包含关键字 + hasTap=true）
# 3. 用 nodeId 执行操作
curl -s localhost:8788/cyborg/dom | python3 -c "
import sys,json
d=json.load(sys.stdin)['data']
def find(nodes):
    for n in nodes:
        if n.get('hasTap') and '管理' in n.get('label',''):
            print(f'Found: [{n[\"id\"]}] \"{n[\"label\"]}\"')
        if 'children' in n:
            find(n['children'])
find(d['nodes'])
"
```

**点击决策由人设驱动**：
- 新手会点最显眼的按钮
- 效率达人直奔目标
- 洁癖用户先找删除/整理入口

**备选方式：坐标点击（测试触摸区域大小时）**

```bash
# 用 Flutter 逻辑坐标直接注入 PointerEvent
curl -s 'localhost:8788/cyborg/tap?x=200&y=300'
```

#### V — 验证（State Oracle 确认效果）

每次点击后 **必须** 验证：

```bash
# 1. 截图确认 UI 变化（如有必要）
screencapture -R {win_x},{win_y},{win_w},{win_h} /tmp/cyborg-poc/step_N_after.png

# 2. State Oracle 验证状态变化
curl -s localhost:8788/state/route      # 页面是否切换
curl -s localhost:8788/state/overlays   # 弹窗是否出现/消失
curl -s localhost:8788/state/management # 数据是否变化（如适用）
curl -s localhost:8788/data/groups      # DB 层数据验证（如适用）
```

**异常处理**：
- 点击无反应 → 检查 `/cyborg/dom` 返回的坐标是否正确，重新尝试（最多 2 次）
- `/cyborg/dom` 返回错误 → 回退到截图分析模式，但需在报告中标注
- State Oracle 返回异常 → 记录为技术问题（含操作截图 + curl 响应）
- UI 变化与 State 不一致 → 记录为可疑 bug，需人工确认

### 截图黑暗降级策略

如果 macOS screencapture 截图全黑或模糊：
1. **主要依赖**：`/cyborg/dom` 语义树获取坐标
2. **截图降级**：截图仅作为辅助验证，不作为主要感知手段
3. **端点不可用时**：Fallback 模式降级，诚实声明探索范围受限

### 截图策略（节省 token）

**必须截图的时机**：
- 每轮探索的起始状态
- 页面切换后（路由变化）
- 弹窗出现/消失后
- 预期外的 UI 变化

**不需要截图的时机**：
- 连续同类操作（如连续删 5 个选项，只截最后一张）
- State Oracle 已确认状态正确且无 UI 异常

### 使用规则

1. **破坏性操作放到每轮末尾**：delete/clear 等不可逆操作，确认只读探索完成后再执行
2. **遇到异常时**：
   - 技术异常（状态不一致）→ 记录到技术问题清单，**附操作截图 + curl 响应**
   - UI 元素识别不确定 → 记录为盲区观察，**不进 bug 清单**
   - 体验困惑（不知道该干嘛）→ 记录到体验报告
   - Server 完全无响应 → 停止，输出已收集的报告
3. **过程中只在遇到意外时写反应**（不需要每步都写独白）

### Step 3: 数据恢复

探索结束后，**必须恢复基线数据**：

```bash
# 如项目有 seed 脚本
./scripts/seed-test-data.sh clean   # 清理探索产生的数据
./scripts/seed-test-data.sh         # 重新播种基线数据
```

无 seed 脚本时提醒用户数据已被修改。

### Step 4: 输出报告

**同时做两件事**：

1. **写入本地文件**：`_scratch/explore-YYYY-MM-DD.md`
   - 目录不存在则创建
   - 同日多次追加 `## 第 N 次探索`
   - 头部加 `# Purpose:` + `# Created:`

2. **打印到对话**：便于用户直接阅读

报告格式：

```markdown
## 探索报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx
- 模式: Cyborg / Fallback
- 基线: [seed 数据 / 用户提供数据]
- 本轮人设: [DeepSeek 生成的人设名称]
- 人设来源: /think --quick 动态生成 | 默认回退

### 🎮 用户体验

#### [人设名]: [背景故事一句话]
> 行为倾向: [关键词]
> 自然覆盖: [维度]
> [使用计划 3-5 句]
> [2-3 段体验描述，只在意外处详写]

**体感问题**:
1. [描述] — 感受：[困惑/沮丧/无聊/...]

### 🐛 技术问题清单（证据链必备）
| # | 操作（截图+点击/curl） | 预期 | 实际（State Oracle 返回） | 归因 | 严重程度 |
|---|----------------------|------|--------------------------|------|---------|
| 1 | 点击 X 按钮 (step_3.png) + `curl /state/overlays` | 弹窗出现 | count=0 | 直接 | 高 |

- **归因=直接**：State Oracle 返回与预期明确矛盾
- **归因=间接**：操作后读状态发现不一致
- **不满足证据链 → 不进此表，转"盲区观察"**

### 🔭 debug 盲区观察（需人工复核）
- **现象**：[描述]
- **为什么是盲区**：[如 State Oracle 无对应端点 / 纯视觉动画]
- **人工验证方法**：[如何手动复现]

### 💡 设计建议（可选）
- [建议] — 基于 [哪个人设的体验]
```

### Step 4.5: /think 评估（质量关卡）

报告写完后、分流归档前，调用 `/think --quick` 对发现进行 sanity check：

**输入给 /think 的内容**：
- 报告中的技术问题清单（含证据链）
- 盲区观察列表
- 设计建议
- 探索模式（Cyborg / Fallback）和实际覆盖范围

**要求 /think 评估**：
1. **Bug 真实性** — 证据链是否完整？是真 bug 还是 debug server 限制？
2. **建议合理性** — 建议是否过度设计？维持现状的成本有多高？
3. **Filing 决策** — 哪些进 TODO（事实型 bug）、哪些进 to-discuss（需判断）、哪些直接丢弃（噪音）
4. **Skill 自检** — 本次执行中 skill 本身是否暴露了系统性问题？（如有 → 作为 to-discuss 条目输出，不自动改 skill）

**输出**：过滤后的 filing 清单，Step 5 按此清单执行。

> 用 `--quick`（DeepSeek）而非默认 Gemini — 这是自主调用的 sanity check，不需要最高质量。
> 如果 /think 不可用（API 故障等），跳过此步直接进 Step 5，但在报告中标注"未经 /think 评估"。

### Step 5: 分流归档（严禁混流）

#### 5a. 事实型 bug → TODO.md
触发条件：有证据链的技术问题（操作 + State Oracle 异常）。
用 `todo-write` skill 写入，带 `_scratch/explore-YYYY-MM-DD.md § 章节` 引用。
**盲区观察不进 TODO.md**。

#### 5b. 观点/判断型 → to-discuss.md
追加到 `to-discuss.md`，格式：

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/explore-YYYY-MM-DD.md § 章节)
- **事实前提**: [一句话客观现象 + Ref 引用，不重复展开]
- **AI 观点**: [我认为应该...]
- **反面检验**: [可能错在哪 / 维持现状的理由]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Discuss → /think 或 /feat-discuss-local-gemini
  - [ ] Reject → 直接删
```

**绝对禁止**：
- 把观点伪装成 bug 塞进 TODO.md
- 把盲区观察伪装成 bug（没有 State Oracle 证据 → 不是 bug）
- 从截图脑补因果
- 给 AI 观点加置信度字段
- TODO.md 与 to-discuss.md 之间设指针

---

## Fallback 模式（纯 curl）

当 Simulator 或 Cyborg Probe 端点不可用时自动降级。

**诚实声明**：Fallback 模式下探索范围 = Debug Server 端点数量。无法覆盖页面导航、手势交互、动画流程。这些是 Cyborg 模式的职责。

**执行流程**：与 Cyborg 模式相同的 Step 1（认知）→ Step 4（报告）→ Step 4.5（/think 评估）→ Step 5（分流），但 Step 2 改为：

1. 通过 `curl /action/*` 端点执行操作
2. 通过 `curl /state/*` + `curl /data/*` 验证状态
3. 每次路由/数据变更后用 `quick-screenshot.sh` 截图观察 UI（非连续同类操作）
4. 人设驱动操作顺序和破坏性决策时机

**Fallback 限制**（必须在报告中声明）：
- 无法验证导航流程、手势交互、动画效果
- 操作绕过 UI 层（不经过确认弹窗、不触发动画）
- 发现的问题可能是 Debug Server 限制而非真实 bug

---

## 注意事项

1. **单人设单轮** — 每次探索只跑 1 个人设，用户多次运行覆盖不同维度
2. **不穷举边界、不跑故事** — 那是 qa-stories 的事
3. **Cyborg 模式下截图 = 感知手段**，不是额外成本 — 但仍按截图策略控制频率
4. **保持人设一致** — 新手不会精确计算，效率达人不会慢慢浏览
5. **nodeId 点击精度 100%** — 但 DOM 中未暴露的 UI 元素无法操作，需结合截图发现盲区
6. **探索后必须恢复数据** — 运行 seed 脚本或提醒用户
7. **报告落盘** — 完整报告写入 `_scratch/`；有证据链的 bug → `TODO.md`；观点 → `to-discuss.md`；盲区留在报告
