---
name: feasibility-study.md 结构约束
description: remote-control 项目 docs/远程协助/feasibility-study.md 的项目特定组织决策（飞书 URL、跨项目协同、§3 同事稿边界）
type: feedback
originSessionId: 5e480da6-b30f-44fe-904d-e600e4c96eca
---

> **通用撰写卫生**（代码视角措辞、断言优先、推荐有依据、删段重编号、竞品稿 vs 决策稿分工）参见 `~/.claude/guides/tech-report-hygiene.md` 与 `~/.claude/commands/techdoc.md`。本 memory 只保留本项目特定约束。

## 飞书映射

- `docs/远程协助/feasibility-study.md` → https://shihengtech.feishu.cn/wiki/AcYGw0fWeiRccWkAExkc4Oyinfd（本项目管辖，映射写入 `docs/.feishu-doc-map.json`）
- 友商对比稿飞书版（§2 外链）→ https://shihengtech.feishu.cn/wiki/DeBZwFf8ziy7wPkzmOhc9Donn6C（标题「友商远程协助对比分析」）
- 技术方案调研外链（§3）→ https://shihengtech.feishu.cn/wiki/Kga1wUcKViU83lk2LQQcOqMInSe（**同事写的**，不是 AI 产出物）

## 跨项目约束

- **§3 飞书链接不动**：同事写的，AI 动它会造成事实面改写 + 协作边界越线。不修改、不补全、不内嵌，哪怕格式调整（空行、标题层级）都不要碰。
- **友商对比稿源文件在 youshang 项目**：`~/AndroidStudioProjects/Work_Other_Projects/youshang/pos/android/docs/远程协助-对比.md`。源头归该项目 AI 负责，本项目**不拷贝、不独立维护**。2026-04-17 Founder 授权 remote-control 侧 AI 可直接改其中的措辞（断言化、去代码视角），后续若 youshang AI 接手时应沿用断言式措辞。
- **不跨项目维护映射**：`docs/.feishu-doc-map.json` 只管 remote-control 项目文件；友商对比稿的飞书 URL 知情即可，不写入本项目映射。

## 项目特定事实

- **§4 已删、章节已重编连续**（2026-04-17）：原「技术原型当前能力」被 §3 飞书链接涵盖，Founder 删除后跳号 §3→§5 ，用 Python 脚本把 §5~§13 整体减 1（含 §N.M 子章节与正文交叉引用）。现在序号为连续 §1~§12。
- **mt 认知**：mt 是软硬一体厂商，客户端无屏幕级远程桌面 ≠ 不提供——能力就在系统 / ROM / 厂商运维后台。**禁止**任何基于「mt 用业务管控替代远程桌面」的论点，这是错误前提。
- **MVP 阶段授权流程倾向 kry 模式（一次性配对码）**：LiveKit 原型天然适配（房间号≈配对码）、工程量比 qm 模式小 3-5 倍、对运维组织无假设。qm 模式作为未来演进方向。这条推荐经过 Founder 挑战后修正——早期错误地推了 qm 模式，前提「有自有运维后台」是未经验证的假设，见 tech-report-hygiene.md §「推荐前先反问自己」。

## 本项目自有写作基调

- feasibility-study.md 是「决策链」文档，不是「证据库」：重型论据外链飞书或放 `_scratch/`，本文档保持精炼
- §2 是 AI 产出摘要，改它有自由度；§3 是同事产出外链，碰都不要碰
- 任何修改前扫一遍 §3 是否被改动；产品类决策（新增/删除章节）需 Founder 授权，不要擅自代劳
