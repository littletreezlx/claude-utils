---
name: game-ui-advance
description: >
  This skill should be used when the user asks to look at, preview, evaluate,
  or improve a game UI screen, when the user says "看下", "看看", "审美",
  "评估一下界面", "全看", "截个图", "帮我看看这个界面", or requests any
  game UI visual review or generation. Fully autonomous: evaluates, generates
  replacements if needed, applies, and records. No user confirmation required.
version: 0.3.0
---

# Game UI Advance — 游戏界面审美预览与评估（全自动）

## 核心改变（vs v0.2）

- **全自动执行**：评估发现问题后直接生成候选图→应用→记录，不等用户确认
- **change_log 外迁**：JSON 只保留当前配置，历史记录到 `docs/ui/changelogs/{category}/{asset}.md`
- **世界观门控前置**：先判定世界观匹配度，不匹配直接触发替换流程

## 执行流程

### Step 0: 确认服务运行

```bash
curl -s --connect-timeout 3 localhost:9998/ping
```

- ✅ 有响应 → 跳 Step 1
- ❌ 无响应 → `tools/ui_preview.sh start` → 重试 ping

### Step 1: 解析目标

**"全看"** → 遍历已实现 `_setup_demo_state()` 的组件：
- UnitCard (`res://Features/UI/UnitCard.tscn`)
- TopBar (`res://Features/UI/TopBar.tscn`)
- SettingsPopup (`res://Features/UI/SettingsPopup.tscn`)

**指定界面** → 直接加载对应 .tscn

**未知界面** → 搜索 `Features/` 目录匹配

### Step 2: 截图

```bash
curl -s -X POST "http://localhost:9998/ui_preview/show" \
  -H "Content-Type: application/json" \
  -d '{"scene":"<scene_path>","variant":"full"}'
```

### Step 3: 三步评估（强制顺序）

#### Step 3a: 客观视觉描述（必须先说）

用 5-8 句话描述**实际看到的所有元素**，不套文档知识。

#### Step 3b: 世界观门控检查

对照 `docs/GAME_DESIGN.md` 的世界观定义（**奇幻商队护卫**）：

- **匹配**：继续 Step 3c
- **不匹配 → 触发全自动替换流程**（见 Step 4），不进入审美评估

#### Step 3c: 审美评估

- 列出 2-4 个实际观察到的视觉问题
- 每个问题附改进建议
- 评分 1-10

**严重程度判定**：
- **严重**（直接触发生成）：世界观不匹配 / 资产库有但未应用 / 关键 UI 元素缺失
- **一般**（记录到 audit 报告，不自动生成）：纯审美问题（颜色/间距/对比度）

### Step 4: 全自动替换流程（仅严重问题时执行）

**无需用户确认，AI 全自动执行**

1. **生成**：优先用本地 SDXL，效果更好且贴合游戏动漫美术风格
   ```bash
   # 本地 SDXL（默认，动漫风更配游戏 Chibi Q版）
   cd ~/LittleTree_Projects/ai-image-engine && python generate.py "<prompt>" \
     --width 1280 --height 720 --no-llm --output staging/<name>.png
   ```
   - 速度：~20秒
   - 默认 hassaku 模型 + flux_anime_flat LORA，动漫扁平感
   - 备用：MiniMax `python tools/gen_minimax_image.py`（照片级，构图准但风格不统一）
2. **预览**：Read 候选图确认效果
3. **应用**：复制到 `Assets/` 目录
4. **记录**：写入 `docs/ui/changelogs/{category}/{asset}.md`，中文理由
5. **重载验证**：`curl -X POST localhost:9998/ui_preview/reload` → Read 新截图确认
6. **写 audit 报告**：`docs/ui/audits/{date}_{asset}_audit.md`

### Step 5: 写 Audit 报告

每次评估都写报告，即使没有问题：

```markdown
# UI Audit Report — {界面名称}

## 基本信息
- **界面**：{scene_path}
- **时间**：{ISO date}
- **截图**：frame_XXXX.png

## 客观视觉描述
[5-8句]

## 世界观匹配
✅ 匹配 / ❌ 不匹配 — [原因]

## 审美问题
1. [问题] → [建议]（severity: high/mid/low）

## 建议动作
- [done] 已修复：{描述}
- [pending] 待处理：{描述}

## 严重程度
- **严重**：世界观不匹配 / 资产未应用 → 已自动处理
- **一般**：审美问题 → 记录待后续迭代
```

---

## 约束

- **必须 Read 截图**：不用代码/文档知识替代实际视觉输入
- **三步顺序强制**：先描述 → 再世界观判定 → 最后审美
- **全自动执行**：严重问题时直接执行，不问用户
- **记录必做**：每次评估必须写 audit 报告，每次替换必须写 changelog

## 目录结构

```
docs/ui/
├── changelogs/
│   ├── environments/camp_hub.md   ← 资产变更历史
│   └── ui/                        ← UI 元素变更历史
├── audits/
│   └── 2026-04-10_camp_hub_audit.md  ← 评估报告
└── UI_PREVIEW_GUIDE.md
```

## 踩坑点

1. **AI 脑补预训练知识** → 强制先输出"实际看到的内容"
2. **跳过世界观检查直接评审美** → 三步顺序强制，不匹配直接触发替换
3. **change_log 写在 JSON 里** → 必须写到 `docs/ui/changelogs/` 下 md 文件
4. **manifest "applied" 状态不可信** → 以运行时截图效果为准，不以 JSON 为准
