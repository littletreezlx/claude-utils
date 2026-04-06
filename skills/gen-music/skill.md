---
name: gen-music
description: >
  Generate game background music via MiniMax music-2.5 API for Barracks Clash.
  Manages the iterative music generation workflow: review manifest → select
  scene → generate → listen → rate/select/reject. Use when the user says
  "生成音乐", "做音乐", "gen music", "generate music", "music for",
  "配乐", "BGM", or when working on audio integration for game scenes.
version: 1.0.0
---

# Gen Music — AI 游戏配乐生成与迭代管理

通过 MiniMax music-2.5 API 为 Barracks Clash 生成场景 BGM。每天 7 次额度，需要精打细算。

## 核心原则

- **额度珍贵** — 每天 7 次，每次调用前必须确认 prompt 和结构标签
- **配器词 > 情绪词** — 用 `pizzicato, woodwinds, marimba` 锚定 Q 版风格，避免 `epic, cinematic` 等会拉向暗黑风的词
- **Loop 在 Godot 端处理** — 不追求 AI 生成完美 loop，用 AudioStream Loop Mode + Tween fade 处理
- **一轨两用** — Victory 前 5-8 秒做 stinger，后段做结算背景 BGM
- **Manifest 是 Single Source of Truth** — 所有生成记录都写入 manifest

## 文件位置

| 文件 | 用途 |
|------|------|
| `art_pipeline/manifests/music/music_manifest.json` | 场景定义 + 候选记录 |
| `tools/gen_music.py` | 生成脚本（调 MiniMax API） |
| `staging/music/` | 候选音乐文件（.gitignore） |
| `Assets/Audio/Music/` | 最终选定的音乐文件 |

## 工作流

### Step 1: 查看当前状态

```bash
python3 tools/gen_music.py --list
```

展示所有场景、候选数量、是否已选定。帮用户决定今天的 7 次额度分配策略。

### Step 2: 与用户确认生成计划

根据当前状态，向用户建议今天的额度分配。优先级参考：

| 优先级 | 场景 | 理由 |
|--------|------|------|
| **关键** | `battle_combat` | 核心游戏体验，必须最先确立 |
| **高** | `main_menu` | 第一印象，与 battle 构成风格双支柱 |
| **高** | `camp`, `victory` | 高频接触场景 |
| **中** | `world_map`, `battle_deploy`, `defeat` | 重要但可稍后 |
| **低** | `battle_boss` | 初期可复用 battle_combat |

**首日建议**: main_menu × 3 + battle_combat × 3 + 1 备用

### Step 3: 生成前 Dry Run

每次生成前必须先 dry-run 确认 payload：

```bash
python3 tools/gen_music.py --scene <scene_id> --dry-run
```

如果用户想微调 prompt：

```bash
python3 tools/gen_music.py --scene <scene_id> --prompt "custom prompt here" --dry-run
```

### Step 4: 生成

确认 payload 后执行：

```bash
python3 tools/gen_music.py --scene <scene_id>
```

或带 prompt 覆盖：

```bash
python3 tools/gen_music.py --scene <scene_id> --prompt "custom prompt here"
```

生成完成后，脚本会：
1. 下载 mp3 到 `staging/music/`
2. 更新 manifest 候选记录
3. 输出文件路径（供用户 `open` 试听）

### Step 5: 用户评审

告诉用户文件路径，等待反馈。用户可能说：
- "这个不错" / "选这个" → 执行 select
- "不行" / "太沉重了" / "重来" → 执行 reject + 调整 prompt 再生成
- "差不多但是 XX 需要改" → 记录反馈到 rating_notes，调整 prompt 再试

```bash
# 选定
python3 tools/gen_music.py --select <candidate_id>

# 拒绝
python3 tools/gen_music.py --reject <candidate_id>
```

### Step 6: 应用到游戏（用户确认后）

当候选被 select 后，需要：
1. 复制 `staging/music/<id>.mp3` → `Assets/Audio/Music/<scene_id>.mp3`
2. 在 Godot 中导入并设置 Loop 参数
3. 更新 AudioManager 播放逻辑

**这一步不自动执行，需要用户确认。**

## Prompt 工程经验

### 结构标签与时长关系
- 3 标签 ≈ 30 秒（适合 stinger）
- 4 标签 ≈ 40-50 秒
- 5 标签 ≈ 50-60 秒

### Q 版风格锚定词
✅ `pizzicato, woodwinds, marimba, light orchestral, bouncy, celtic folk, playful, whimsical`
❌ `epic, cinematic, dark, heavy, dramatic choir, orchestral hit`

### 循环友好技巧
- Prompt 加 `ostinato, steady repetitive motif, ambient loop`
- 避免 `[Climax]` 和 `[Drop]`（能量波动大，难循环）
- 尾标签用 `[Outro]` 或 `[Fade]`

### 器乐 Workaround
music-2.5 不支持 `is_instrumental`，用空结构标签替代：
```
[Intro]\n[Instrumental]\n[Build Up]\n[Climax]\n[Outro]
```
标签内不放任何歌词文字。

## 迭代记录

每次 prompt 实验的经验应更新到 manifest 的 candidate `rating_notes` 字段：
- "太沉重，去掉 brass" → 下次移除 brass 关键词
- "节奏太快" → 下次加 moderate tempo
- "这个 pizzicato 感觉很好" → 固化到场景 prompt

## 约束

- **不自动消耗额度** — 每次生成必须经用户确认（dry-run 先行）
- **不修改 .tres 文件** — 音频导入和 Godot 参数调整留给人在编辑器中操作
- **不修改 AudioManager.gd** — 播放逻辑的修改是独立任务，不在此 skill 范围内
- API key 从 `MINIMAX_API_KEY` 环境变量或 `~/.claude.json` MCP 配置读取
