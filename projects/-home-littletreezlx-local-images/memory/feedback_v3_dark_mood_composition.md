---
name: V3 暗调质感 + 构图经验
description: V3 风格实现暗调光影的方法、构图选择(cowboy shot)、姿势描述轻重技巧
type: feedback
---

## V3 暗调光影：用环境描述绕过黑名单

V3 黑名单封杀 rim lighting / deep shadow / cinematic lighting / dark mood，但可通过**环境层描述**间接实现暗调：
- `(night:1.2), (dimly lit room:1.3), dark ornate bedroom`
- `(warm lamp light:1.2), candle, ambient glow`
- Negative 加 `white background, (bright:1.2), overexposed`

**Why:** V3 的 SSS + wet skin 在暗环境下反而产生更强高光反差，接近"黑暗中的光泽感"。

## 构图选择：cowboy shot 是肉感甜点

| 标签 | 效果 | 适用 |
|------|------|------|
| `upper body` | 只有胸以上，无腿无臀 | 脸部特写 |
| `cowboy shot` | 膝盖以上，胸→腰→臀→大腿 S 曲线 | **肉感美感最佳** |
| `full body` | 含小腿脚，画面空旷分散 | 全身站姿 |

**How to apply:** 需要展示身体曲线时优先 `cowboy shot`，避免 `full body` 稀释焦点。

## 姿势描述：轻触 > 用力抓

- `holding own legs` → 手用力抱腿，动作过重
- `hand on own thigh, spreading` → 轻轻掰开，优雅暗示

**Why:** 用户反馈"抓太多了"。姿势标签选择轻动词（hand on, touching）而非重动词（holding, grabbing）。

## Negative 管理

需要露出特定部位时，记得检查 negative_prompt 是否有矛盾标签（如想露胸但 negative 里有 `exposed breasts`）。
