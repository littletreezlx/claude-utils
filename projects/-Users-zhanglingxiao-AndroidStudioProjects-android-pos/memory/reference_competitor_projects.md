---
name: 竞品项目路径与文档策略
description: POS 竞品反编译项目的本地路径、文档完善度和调研工作流
type: reference
---

竞品项目统一放在 `~/AndroidStudioProjects/Work_Other_Projects/youshang/pos/android/`

| 竞品 | 路径 | 文档完善度 | 说明 |
|------|------|-----------|------|
| 趣买 | `Qmai/` | ✅ 标杆 | 有 FEATURE_CODE_MAP、print/ 模块深度文档、钱箱等专题 |
| 美团 | `Meituan/` | 🟡 有专题缺索引 | 蓝牙打印/购物车/打印流控/标签，缺 FEATURE_CODE_MAP |
| 客如云 | `Keruyun/` | 🔴 很薄 | 仅蓝牙打印+标签，缺整体索引和模块文档 |

每个竞品目录结构：`apktool/`（反编译原始资源）、`src/`（提取的源码）、`docs/`（分析文档）、`架构分析.md`（根目录总览）

**竞品文档补全策略：** 阅读竞品代码时，应顺手补全该竞品的 docs/，参考 Qmai 的组织方式：
1. 根目录 `架构分析.md` — 整体架构总览
2. `docs/FEATURE_CODE_MAP.md` — 功能→代码路径索引
3. `docs/<module>/` — 按模块组织深度分析文档

**How to apply:** 需要对比竞品实现时，直接读取对应目录代码。看到 Keruyun/Meituan 缺少的文档，主动提议补全。发布竞品分析文档前须遵守 `COMPETITOR_DOC_POLICY.md` 脱敏规范。
