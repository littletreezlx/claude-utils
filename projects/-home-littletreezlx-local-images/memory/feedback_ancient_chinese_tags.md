---
name: 古装质感 tag 配方
description: 用 Danbooru 原生标签 + 画风引导实现古装质感，v3/Perfect Doll 最佳
type: feedback
---

古装主题不能用现代服装词汇（silk blouse, camisole 等），会出 cosplay 感。

**Why:** 底模训练数据中"silk blouse"对应的是现代服装，不是古装面料。Danbooru 原生标签（hanfu, chinese_clothes）才能触发正确的视觉特征。

**How to apply:**
- 服装: `hanfu, chinese_clothes, wide_sleeves, layered_clothes, sash, floral_print`
- 发饰: `hair_stick, hair_ornament, hairpin, tassel`
- 画风（以下均验证有效，差异不大，任选）:
  - `(traditional_media:0.6)` — 单独就够用
  - `(traditional_media:0.6), (ink_painting:0.4)` — 默认组合
  - `(traditional_media:0.5), (gongbi:0.5), (sumi-e:0.4)` — Euryale 推荐
  - `(sumi-e:0.5), (ink_wash:0.4)` — 水墨感更强
- 负面: `modern_clothes, western_clothes, cosplay, 3d, cg`
- 底模: v3/Perfect Doll 最佳，Janku scene 风格不行
- A/B test 记录: `ab-tests/ancient-chinese-style/`, `ab-tests/art-style-tags/`
