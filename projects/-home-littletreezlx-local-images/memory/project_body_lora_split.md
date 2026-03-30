---
name: Body LoRA 拆分训练架构
description: 脸/身材 LoRA 分离训练 + 生成端 -f/-b 参数 + Scene YAML V9 body 字段拆分待做
type: project
---

## 已完成 (2026-03-30)

**训练端**:
- `--type face/body/character` 控制 WD14 打标的标签过滤策略
- `--model v1/v3` 选择训练底模（Janku / Perfect Doll）
- `BODY_TAGS` / `FACE_TAGS` 在 `core/wd14_tagger.py` 中定义
- CyberRealistic Pony 已删除，Perfect Doll 已加入 TRAIN_MODELS

**生成端**:
- `-f` / `--face` + `-b` / `--body` 拆分模式（与 `-c` 互斥）
- `--face-weight` 默认 0.5，`--body-weight` 默认 0.65
- `--prompt-file` 短标志从 `-f` 改为 `--pf`

**A/B 测试教训**:
- 第一次训练未用 `--type body`，面部标签稀释了身材学习
- 重训命令：`python train_character.py -i lora-input/body --type body --model v3 --retag --retrain`

## 待做 (下次会话)

**Scene YAML V9 — body 字段拆分**:
- `character` 字段拆出 `body` 字段：`character` 只留身份标签，`body` 放身材描述
- 涉及：`core/schemas.py` (ScenePreset)、`core/scene_loader.py`、prompt 组装逻辑
- 现存大量 YAML 的 `character` 字段含身材标签（`large breasts, thick thighs` 等），需批量迁移
- 生成逻辑：`-c` 模式注入 character + body；`-f/-b` 模式注入 character + body LoRA（忽略 body 字段）

**Why:** body LoRA 注入的身材和 YAML 中文字描述的身材会冲突（如 LoRA 学了 huge breasts，YAML 写了 small breasts）

**How to apply:** 等 body LoRA 重训 A/B 验证效果满意后再拆，更有依据
