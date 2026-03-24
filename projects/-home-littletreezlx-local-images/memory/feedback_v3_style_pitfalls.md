---
name: V3 风格演进与设计原则
description: V3 从 MiaoMiao 补偿型重写为 Perfect Doll 引导型，底模选择与标签策略
type: feedback
---

V3 风格已从"补偿型"重写为"引导型"（2026-03-22）。

**核心教训**：风格标签不应"补偿"底模缺陷，而应"引导"底模优势。底模自带的质感是基底，风格层只做微调。

**Why:** 旧 V3 为 MiaoMiao（偏哑光）设计，堆了大量 wet skin/baby oil/specular highlight 来补偿。换到自带光泽的 Perfect Doll 后这些标签全部过载，产生油腻塑料感。

**How to apply:**
- V3 现绑定 Perfect Doll 底模（force_model: perfect_doll），不再用 MiaoMiao
- 新 V3 三层引导：光影拓扑（rim lighting + deep shadow）→ SSS 通透（subsurface scattering + translucent skin）→ 3D 引擎锚定（octane render）
- 测试新底模时，先用 style: minimal 看底力，再逐层叠加标签定位甜点区
- 禁止在自带光泽的底模上堆 wet skin / shiny skin / baby oil 等液态标签
- V3 适合极简提示词，风格系统已注入 3D/光影词，用户侧不要再堆
