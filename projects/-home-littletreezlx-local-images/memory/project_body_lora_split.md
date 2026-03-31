---
name: Body LoRA 拆分训练架构
description: 脸/身材 LoRA 分离训练 + 生成端 -f/-b 参数 + Block Weight 发现 + 最终训练配方
type: project
---

## 已完成 (2026-03-31)

**训练端**:
- `--type face/body/character` 控制 WD14 打标的标签过滤策略
- `--model v1/v3` 选择训练底模（Janku / Perfect Doll）
- body 类型使用**反向标签策略**：删除身材标签（BODY_TAGS），保留所有其他标签，触发词吸收身材概念
- body 类型参数：dim=32, alpha=16, train_text_encoder=False

**生成端**:
- `-f` / `--face` + `-b` / `--body` 拆分模式（与 `-c` 互斥）
- `--face-weight` 默认 0.5，`--body-weight` 默认 0.8
- `-b` 支持 `--scene` 场景预设，自动跳过 YAML body 字段
- `batch_scenes.py` 支持 `-f`/`-b` 参数
- `--prompt-file` 短标志从 `-f` 改为 `--pf`

**Body LoRA 训练配方（最终版）**:
- 反向标签：删身材标签 + 保留服装/配饰/脸等全部标签 → 触发词独占身材概念
- dim=32（信息瓶颈，过滤高频画风细节，只学低频几何形变）
- 不训练 TE（从源头避免文本编码器污染）
- 底模：Perfect Doll (V3)
- 命令：`python train_character.py -i lora-input/body --type body --model v3 --retag --retrain`
- 默认权重：0.8（1.0 身材更极致但背景开始泄漏训练数据场景）

**Block Weight 发现**:
- TE 是画风/服装泄漏的主要源头（去 TE 保留 UNet 全层效果最佳）
- `scripts/lora_block_filter.py` 可按层过滤 LoRA（IN/MID/OUT/TE）
- 最终方案不需要 block filter，因为训练时就不训 TE

**迭代历程**:
1. dim=64 + 旧标签策略（保留身材标签）→ 效果弱，身材不明显
2. dim=128 + emphasis → 身材有但画风/丝袜/脸型全泄漏
3. Block Weight (去 OUT+TE) → 画风干净但身材太弱
4. Block Weight (只去 TE) → 画风干净 + 身材适中 → 发现 TE 是泄漏主凶
5. **dim=32 + 反向标签 + 不训 TE** → 最佳平衡（当前方案）

## 待做 (下次会话)

**Scene YAML V9 — body 字段拆分**:
- `character` 字段拆出 `body` 字段（schemas.py 已加 body 字段）
- 现存 YAML 批量迁移
- `-b` 模式自动跳过 YAML body 字段（已实现）
