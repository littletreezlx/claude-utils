---
name: AI Vision 对低对比度差异不可靠
description: 基于压缩截图做 UI 灵魂级判定前必须先读源码，防幻觉；外部 AI 叠加不等于独立证据
type: feedback
originSessionId: 53984e57-41e1-43af-80f3-8beba995d073
---
**规则**：任何基于截图做出的 Soul-breaking / P0 / P1 级 UI 判定，在写入报告或触发代码修改前，必须用 Glob/Read 读对应组件源码做字段对照。仅凭截图观察不足以支持这一级别的判定。

**Why**:
- 2026-04-13 flametree_pick 翻车事件：`/ui-vision-check` 基于 942×2048 压缩 JPEG 判定了三项 P0/P1 偏离（GroupChipBar 实色橙色胶囊、GlassGroupCard Emoji 裸贴、CeramicCard 扁平 Material）。`/think` 透传同样截图给 Gemini 3.1 Pro，Gemini 非但没纠偏，反而加码断言"CeramicCard 根本不是陶瓷双层 Stack"。Founder 据此拍板执行"Warm Ceramic 质感重建"。
- AI 即将写代码前先 Glob + Read 源码，发现三项判定全部是 AI Vision 幻觉——代码实际完全符合 Spec v3.8（`Color(0x14E06D06)` @ 8% 淡底、`32.w + Color(0xFFF2E8E0) + shape: BoxShape.circle` 暖米托盘、完整的 `_buildClayLayer + _buildGlazeLayer + 6.h 偏移` Stack 双层结构都在代码里）。
- AI Vision 编码器对三类差异特别不可靠：透明度 <20% 的色底、相近色值的双层结构（米色 vs 白）、小位移的 3D 错层（几 dp 偏移）。
- **两个 AI 看同一张压缩 JPEG 不等于独立证据**——共享感知缺陷时置信度正相关，不提供交叉验证保障。真正的独立证据必须来自不同感知通道（源代码）。

**How to apply**:
- 任何 UI 审视工作流（ui-vision-check / ui-vision-advance / game-ui-advance），只要输出物会触发代码修改，必须在"判定偏离 → 写入报告"之间插入"读源码对照"环节
- 基于截图做判定时，看到以下信号应**主动怀疑自己**：色底看起来"有颜色但不浓"（很可能是 <20% 透明度，你会幻觉成实色）、两个元素"像是融为一体"（很可能是相近色值叠层）、元素"看起来扁平"（很可能是几 dp 偏移被压缩 JPEG 抹平）
- 外部 `/think` 独立视角对"源码级判定"不是保险——对同类感知任务 Gemini 和 Claude 会共享幻觉。让 Gemini 看截图前先自己读代码，把源码事实作为 Context 的一部分传给 Gemini，而不是让 Gemini 从压缩图里自己推
- 在对话里上报 Soul-breaking 时必须带 `<file>:<line> + 实际字段值`，写不出 = 判定不成立

**相关**:
- skill: `~/.claude/skills/ui-vision-check/SKILL.md` v3.1.0 Step 2.5 源码对照护栏
- ADR: `~/.claude/docs/decisions/2026-04-13-01-ui-vision-check-code-anchor.md`
