# ui-vision-check skill 加源码对照护栏：防 AI Vision 幻觉

- **Date**: 2026-04-13
- **Status**: Accepted
- **Scope**: skill:ui-vision-check (v3.0.0 → v3.1.0)

## 1. 问题 (What went wrong)

在 `flametree_pick` 项目一次会话中，Founder 触发 `/ui-vision-check` 做全局 UI 审计。AI 读取了 4 张已有截图（iOS 主页 idle、主页 winner、分组管理、设置）+ `docs/ui/UI_SHOWCASE.md` v3.8，基于「截图观察 vs Spec 文字描述」输出了一份全局审计报告，判定了三项偏离：

1. **P0 Soul-breaking**: GroupChipBar 选中态是"实色橙色胶囊 + 白字"，与 Spec 约定的"品牌色淡底 #E06D06 @ 8% + 25% 边框 + 琥珀色文字 #D06000"严重偏离，跨主页/管理页系统性偏差
2. **P1**: Management GlassGroupCard 的 Emoji 是"裸贴"，没有 Spec 描述的"32×32px 圆形 + 暖米色 #F2E8E0 托盘"，破坏"施釉陶艺"隐喻
3. **Evolution Dialogue**: Settings SuperDock 中间按钮是 ✓ 勾选而非 Spec 描述的 home icon

随后按 skill 约束走 `/think` 让 Gemini 3.1 Pro（透传 4 张截图）做独立第二视角。Gemini 的 challenge 不仅没有纠偏，反而**加码放大了幻觉**，进一步断言："真正的 P0 是 CeramicCard 本身是扁平 Material 卡片，没有素胎层/暖米底盘/边缘高光，这 8 个卡片根本不是陶瓷餐具。"

基于 Gemini 的翻转判断，Founder 拍板"按建议执行 Warm Ceramic 质感重建，不妥协当前进度"。

在 AI 即将开始写代码前，出于审慎（「不在脏工作区开始新任务」+ 查找关键文件位置），先用 Glob 定位到四个源文件，再 Read 读取实际代码：

- `lib/presentation/shared/widgets/group_chip_bar.dart:344-363` — **实际代码是 `Color(0x14E06D06)` = 8% 淡底 + `Color(0x40E06D06)` = 25% 边框 + `Color(0xFFD06000)` 琥珀深色文字 + 极轻贴地阴影**。完全符合 Spec v3.8
- `lib/presentation/features/management/widgets/glass_group_card.dart:469-483` — **实际代码就有 `width: 32.w + color: Color(0xFFF2E8E0) + shape: BoxShape.circle` 的暖米色圆形托盘**。完全符合 Spec
- `lib/presentation/features/random_selection/widgets/ceramic_card.dart:292-336` — **实际代码是完整的 Stack 双层结构**：`_buildClayLayer()` 用 `#E6DFD5` 素胎色 + 双层暖焦糖阴影；`_buildGlazeLayer()` 用 `#FFFFFF` 白釉；白釉层向上 `6.h` 偏移。完全符合 Spec

三项 Soul-breaking / P0 / P1 **全部是 AI Vision 幻觉**。代码和 Spec 严格一致。幸运的是 AI 在写代码前先读了源码，才避免了对一个已经符合设计语言的代码库做"重塑"——那会造成灾难性的破坏性改动。

## 2. 讨论过程 (How we thought about it)

### Round 1: AI Vision 判定偏离

AI 基于 docs/ui/screenshots 下 4 张压缩 JPEG（942×2048）+ UI_SHOWCASE.md 文字描述，判定 3 项 Spec 偏离并按 skill 约束给出 P0/P1/Evolution 分级。

### Round 2: /think 交叉验证（外部 AI 也幻觉）

按 skill 要求「Refinement → 必须透传截图走 Gemini」，AI 调用 `think.mjs` 把 4 张截图 + Context + Failure_Premise 传给 Gemini 3.1 Pro。Gemini 不仅认可了 AI 的偏离判定，还**加码升级**：

- 断言"卡片就是纯白扁平 Material Design 卡片，根本没有陶瓷双层 Stack 结构"
- 建议"用物理形态（内发光凹槽 / Outlined Pill）重建整套 CeramicCard"
- 模拟 Founder 视角指责"AI 用显微镜找不同但丧失了产品味道的嗅觉"

**关键观察**：外部 AI 的独立视角这次非但没起到防幻觉作用，反而**放大了幻觉**。原因：Gemini 也只有压缩 JPEG，没有代码访问权，推理同样建立在低对比度视觉感知之上。两个 AI 叠加不等于两份独立证据——共享相同类型的感知缺陷时，它们的置信度是正相关的，不是独立的。

### Round 3: Founder 拍板执行

Founder 看完 Gemini 的 challenge 回复，决定"按建议执行 Warm Ceramic 质感重建，不妥协当前进度"。

### Round 4: 代码验证发现幻觉

AI 按「Git 洁癖」+「先定位文件再改动」的前置动作，用 Glob 找到 4 个关键源文件，Read 实际代码——**三项判定全部被源码推翻**。AI 立即停止执行，向 Founder 上报翻车。

### Round 5: Founder 选择 A + D

- **A**: 撤回 UI Vision Check 报告
- **D**: 给 skill 加源码对照护栏

### Round 6: 设计护栏

讨论要不要像铁律 5 的「验证凭证」那样做强制输出锚。结论：

- **只在 Soul-breaking / P0 / P1 层级触发**：Refinement / P2 级的主观审美判断本来就允许"只靠眼睛"，不能要求每条 Refinement 都读源码——那会把 skill 变成代码审计工具
- **在报告模板里开显式逃生门**：加 `🪞 Vision Hallucination Reversals` section 记录被源码推翻的疑似偏离——让"撤回"变成可审计的正向产出，而不是偷偷删掉
- **在 AI 能力边界段加显式告警**：把"低对比度差异不可靠"写成一条**预判规则**（看到 <20% 透明度、相近色值、小位移结构时**预期会幻觉**），而不是事后纠偏

## 3. 决策 (What we decided)

### 修改 1：在 Step 2（加载设计基准）之后插入 Step 2.5「源码对照护栏」

触发条件：任何 Soul-breaking / P0 / P1 判定之前，强制走此步骤。Refinement / P2 / Blind Spots 不触发。

执行步骤：
1. Glob/Grep 定位涉嫌偏离组件的实现文件
2. Read 源码提取实际字段（color/width/offset/shadow/Stack 结构）带行号
3. 与 Spec 字段逐项对照
4. 三分支判定：
   - **✅ 源码 ≡ Spec** → 判定为 AI Vision 幻觉，不得标记为 Soul-breaking / P0 / P1，降级为 Blind Spots 或撤回
   - **❌ 源码 ≠ Spec** → 维持 Soul-breaking 判定，报告必须附源码行号 + 实际字段值作为证据
   - **❓ 源码引用的 token 值与 Spec 不一致** → Soul-breaking + Evolution Dialogue（Bug 还是 Spec 过时）

硬约束：
- 本步骤不可跳过，缺失源码引用 = 违反 skill
- 本步骤不可伪造，必须真实调用 Read/Grep 工具

### 修改 2：AI 能力边界段新增「低对比度差异不可靠」条款

明确列出三类易幻觉场景作为预判规则：
- 透明度 <20% 的色底（例：#E06D06 @ 8% 淡底在暖米背景上可能被判成实色填充）
- 相近色值的双层结构（例：#F2E8E0 米色托盘 vs #FFFFFF 白卡片）
- 小位移的 3D 错层（例：6.h 素胎层偏移）

这三类差异出现在截图中时，AI 应**预期自己会幻觉**，必须走 Step 2.5。

### 修改 3：报告模板新增 🪞 Vision Hallucination Reversals section

被 Step 2.5 源码证据推翻的"疑似偏离"**显式写入**该 section（附源码行号），不得静默删除。例：

```
🪞 Vision Hallucination Reversals (幻觉撤回)
- 疑似: Chip 实色橙色胶囊 → 源码 group_chip_bar.dart:344-350 实际为 Color(0x14E06D06) @ 8% 淡底，符合 Spec，判定撤回
```

### 修改 4：约束段新增「Soul-breaking 必须附源码证据」

在 skill 末尾的约束列表中加一条强约束，与 Step 2.5 互为表里。

### 修改 5：version 3.0.0 → 3.1.0

minor 版本号 bump（加 feature 不破坏既有行为）。

## 4. 放弃的替代方案 (What we rejected and why)

### 方案 A：对所有级别（含 Refinement）都要求源码对照

**拒绝理由**：Refinement 是主观审美（呼吸感、焦点层级），本来就允许"只靠眼睛"。强制读源码会把 ui-vision-check 退化成"代码审计工具"，失去"AI 视觉灵魂验证"的定位。护栏只针对高成本的 Soul-breaking / P0 / P1——因为这些级别会直接触发代码修改，误判代价高。

### 方案 B：靠 /think 做二次独立验证，不加代码护栏

**拒绝理由**：本次事件就是反例——Gemini 看同样的压缩 JPEG，同样产生了幻觉，还加码升级。两个 AI 叠加不等于独立证据，**共享感知缺陷时置信度是正相关的**。必须引入来自**不同感知通道**的证据（源代码），才是真正的独立交叉验证。

### 方案 C：要求提高截图分辨率 / 多次截图

**拒绝理由**：治标不治本。即使 4K 截图，AI Vision 对 8% 透明度 vs 实色填充的判断依然不可靠——问题不在像素数量，而在 AI 视觉编码器对"低对比度 + 暖色叠暖色"的 feature 抽取能力。源码是最底层、最不可伪造的 ground truth，必须直接消费。

### 方案 D：完全废弃 ui-vision-check skill，改为"代码审计 + 手动截图对照"

**拒绝理由**：过度矫正。截图审视对**纯审美层面**（留白、呼吸感、焦点）仍然有效——那些是代码里看不出来的。skill 本身有价值，只是需要在"灵魂级判定"这条边界上设置护栏。保留主流程，加 Step 2.5 是最小手术。

## 5. 预期影响 & 监控 (How we will know it works)

### 期望改变的行为

1. AI 在把某项观察标记为 Soul-breaking 之前，**被迫**先去 Glob/Read 对应源码。写不出 `<file>:<line>` 引用 → 无法完成 Soul-breaking 判定
2. 被推翻的幻觉会以 `🪞 Vision Hallucination Reversals` 的形式**显式**出现在报告里，而不是被 AI 偷偷删掉——让 Founder 能看到"AI 以为有问题但其实没有"，同时 AI 得到负反馈训练自己的预判
3. 外部 /think 调用不再是 Soul-breaking 的最终仲裁者——即使 Gemini 加码放大幻觉，Step 2.5 会在落到代码修改之前兜底

### 有效性信号（应当观察到）

- ui-vision-check 报告中 Soul-breaking 条目数量**下降**，但每条都带准确的源码行号
- 🪞 Vision Hallucination Reversals section **出现**（证明 AI 在做预判 → 对照 → 撤回的完整闭环，而不是跳过 Step 2.5）
- 触发后续 TODO.md / 代码修改的 UI 任务**返工率下降**（不再出现"修了个根本不存在的问题 → Founder rollback"）

### 失效信号（警戒）

- 报告里出现大量 `🔗 Code Anchor: <file>:<line> (未实际读取)` 或只有文件路径没有行号 → Step 2.5 被伪造，需要在 Digest 阶段强制工具调用检查
- 🪞 Reversals section 永远为空 → AI 在跳过 Step 2.5 直接走 Soul-breaking（或者 AI 的初始判定已经被护栏反过来抑制得太保守，不敢再提 Soul-breaking）
- Founder 反馈"AI 现在连明显的设计偏离都不敢提了" → 护栏过严，需要重新校准触发阈值

### 回访计划

- **首轮体检**：2026-05-13（1 个月后），抽查过去 30 天所有 /ui-vision-check 输出，统计：
  - Soul-breaking 数量 vs Reversal 数量的比例（健康区间：1:1 到 3:1）
  - Code Anchor 引用准确率（抽查源码行号是否真实存在）
  - 触发代码修改的 UI 任务返工事件数
- **如果有效**：把「源码对照护栏」作为模式写入 `~/.claude/guides/` 供其他涉及 AI Vision + 代码判定的 skill 借鉴（如 ui-vision-advance、game-ui-advance）
- **如果失效**：重新 /think 评估是否升级为 hook 拦截（在 Soul-breaking 输出前强制检查 `<file>:<line>` 引用存在）

## 附录：本次决策本身的验证凭证

```
[验证凭证:
  Read ~/.claude/skills/ui-vision-check/SKILL.md 确认:
    - line 15: version: 3.1.0 (was 3.0.0)
    - line 32-33: AI 能力边界新增 "低对比度差异不可靠" 条款，列出三类易幻觉场景
    - line 84-108: 新增 "Step 2.5: 源码对照护栏" section，含触发条件、执行步骤、三分支判定、硬约束
    - line 156-159: 报告模板新增 🔴 Soul-breaking 必须附 🔗 Code Anchor 要求
    - line 161-164: 新增 🪞 Vision Hallucination Reversals section 模板
    - line 229: 约束列表新增 "Soul-breaking 必须附源码证据" 条款
  Read lib/presentation/shared/widgets/group_chip_bar.dart:344-363 确认当前代码就是 Color(0x14E06D06) @ 8% 淡底 + Color(0x40E06D06) @ 25% 边框 + Color(0xFFD06000) 琥珀深色文字]
```
