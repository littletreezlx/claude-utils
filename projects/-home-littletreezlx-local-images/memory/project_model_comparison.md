---
name: model_comparison_3d_cg
description: 底模对比实验结论 — MiaoMiao vs Nova vs IlluQuaint vs Flux 在 3D CG 动漫质感上的表现
type: project
---

## 底模对比实验 (2026-03-21)

目标美学：3D CG 动漫人偶 + 物理级油光材质（参考图 input-interrogate/image-3d.png）

| 底模 | 文件名 | 美学定位 | 优势 | 劣势 | 结论 |
|------|--------|---------|------|------|------|
| **MiaoMiao Realskin** | miaomiaoRealskin_epsV14 | 树脂/硅胶人偶 | 油光最强、色气感最好、甜点区 | 极端 POV 构图不稳定 | **最佳选择** |
| Nova Anime3D XL | novaAnime3dXL_v70 | 手游 3D CG | 构图稳定、动作自然 | 偏塑料感 | 备选（构图要求高时） |
| IlluQuaint | illuquaint_v08 | 2.5D 高级插画 | 皮肤最自然柔和 | 油光不够、挤压感弱 | 备选（追求自然感时） |
| Flux Dev GGUF | (内置) | 照片级写实 | 物理光影碾压级 | 完全真人化，丢失动漫感 | 不适合此目标 |
| Nova 3DCG XL | 已删除 | PVC 手办 | 水珠颗粒好 | 塑料感最强 | 不推荐 |

**Why:** MiaoMiao 精准卡在"二次元完美比例"与"3D 光影肉感"之间的甜点区，是其他模型无法替代的。

**How to apply:** 追求 3D CG 动漫质感时，优先用 MiaoMiao + V1 风格。只在构图稳定性要求极高时考虑 Nova Anime3D。
