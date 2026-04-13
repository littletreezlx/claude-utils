# Active State Tier Rules — 品牌色激活态分层规则

**日期**：2026-04-13
**范围**：`flametree_rss_reader/docs/DESIGN_PHILOSOPHY.md` §3 新增 + `~/.claude/skills/ui-vision-check/SKILL.md` 检查启发式替换
**分类**：规则变更（铁律 8 触发）
**决策者**：Founder（授权 Claude Code 基于 Gemini `/think` 结果自主执行）

---

## 1. 遇到的问题

`flametree_rss_reader` 2026-04-13 会话末尾，TODO 剩最后一条阻塞项：

> **"重构红色语义层级（accent 仅限 CTA、article/AI 面板改 tertiary）"**

这条任务源自 `/ui-vision-check` 4 张 iOS 截图审计，当时前提是 "哑红色在未读列表 / 选中态 / CTA / AI 面板到处扩散，焦点失焦"。

Claude Code 执行前审计发现原始前提**部分失效**：
- `unreadIndicator` 已改为 `tertiary` 暖灰（非红）
- `listItemSelected` 已改为 `surfaceContainerHigh` 暖灰（非红）
- iOS main_page 实际观感已无"红色扩散"

**剩余 `accent` = `primaryContainer` 哑橙使用集中在**：Login CTA（已修复）、Settings sidebar 选中竖条、article_header 激活 icon、ai_summary_panel 品牌强调、bookmark、Dialog 确认键、feed_settings Switch、sync_progress_bar。

**核心判断难题**：这些使用是 Material 3 标准约定（"primaryContainer 用于激活/选中态"），是否判为"焦点失焦"属设计哲学判断，不是事实 bug。Claude Code 第一直觉倾向 **Reject**（从队列删除），但担心在"用工程胜利（SSOT 整合已修列表页）掩盖产品失败（阅读态哑橙密度过高）"。

## 2. 讨论过程

### Claude Code 自己的事前验尸（call think 之前写的 Failure_Premise）

- **方案 A（按 TODO 执行 accent→tertiary）失败点**：激活态与禁用态都是中性暖灰变体，用户出现 State Blindness；违背 M3 约定制造 Death by Special Cases；抹掉 FlameTree 品牌可感知瞬间
- **方案 B（Reject 现状冻结）失败点**：审计仅基于 iOS 4 张截图，阅读态哑橙密度问题被 SSOT 胜利掩盖，有 Rubber Ducking 规避嫌疑
- **方案 C（单屏触点密度阈值）失败点**：数字阈值无客观依据、Token 无法编码单屏总量、AI 每次加组件数全屏成本过高

### Gemini `/think` 的挑战与诊断

Gemini 拒绝 Reject / 拒绝方案 A 的粗暴替换，提出**方案 D（语义分层）**，给出三条关键洞察：

1. **`accent = primaryContainer` 是严重认知债务**：`primaryContainer` 是**结构型 Token**（M3 体系基于原色的容器背景色），`accent` 是**语义型 Token**（强调用途）。画等号让 AI 写代码时随便挑一个用，且分不清某组件用此色是因为"属于 Primary 色系"还是"需要被强调"。**必须打破这个等价关系**。

2. **Material 3 默认 vs "Warm Study" 哲学的根本张力**：M3 信条是"高可用 + 极度明确的交互反馈"，所以默认激活态要亮；"The Quiet Curator" 信条是"沉浸与不打扰"。**当项目选了"沉静"哲学的那一天，就已经在对抗 M3 默认行为了**。遇到冲突拿 M3 默认做挡箭牌 = 设计哲学还没真正在底层落地。

3. **"状态盲"是伪命题**：假设"极简设计中只能靠 Hex 颜色值区分状态" 是错的。不能用刺眼颜色时，可用**形状 (Outlined→Filled)**、**填充度**、**背景对比** 构建激活态。Claude Code 被困在了单维度颜色替换里，忽略了形态对比。

4. **方案 C 数量规则是灾难**：LLM 修改单个组件时没有全局视图，遍历整个页面数哑橙数量不现实。**任何不能转化为"本地化判断机制 (Local Decision Rule)"的设计规则，在 AI-Only 团队都会沦为废纸**。

5. **Reject 定性**：Claude Code 在过度理性化避免决策，用"红色没扩散到列表页"的工程胜利掩饰"阅读页依旧很吵"的产品失败。

### Gemini 的方案 D（语义分层）

- **Tier 1 — 品牌原动 (Brand & Catalyst Action)**：关键跳转 / 破坏性操作 / 核心品牌瞬间 → **允许**使用哑橙
- **Tier 2 — 局部状态 (Contextual State)**：浏览/阅读过程中局部 on/off/selected/active → **禁止**使用主色调，通过 Outlined↔Filled 形态 + 容器底色 + 字重表达激活
- 固化到 `DESIGN_PHILOSOPHY.md` + 改写 `/ui-vision-check` 检查启发式（不再查"红色泛滥"，改查"品牌色是否被用于局部状态"）

### Claude Code 的采信与修正

Claude Code 采信 Gemini 核心诊断，但指出其执行方案的 **3 个漏洞**并做出修正：

1. **"删 accent → 编译错误 → 强制 re-evaluation" 在 AI-Only 项目不成立** — AI 修编译错误的最小阻力路径是批量替换为 `primaryContainer` 保持原样，不会真的重想每个点。必须**另起一张 Tier 分类表作为替换依据**。
2. **Tier 分类边界模糊** — bookmark / AI toggle / feed_ai_config Switch 这些逐点归属需要 Founder 拍板，不是机械规则能覆盖。因此在文档中加了**判定难题与升级规则**硬约束。
3. **"Outlined → Filled 形态对比"对现有代码部分失效** — `article_header` 激活态已在用 filled icon，再退到 tertiary 会变成"灰 filled vs 灰 outlined"。因此 Tier 2 的呈现手段给了**形态/底色/字重三选一 + 色彩仅作二级信号**的组合，而非单一形态替代。

### 立场升级

Claude Code 最终立场为 **Escalate**（不自主开干）：决策涉及产品可感知视觉行为 + skill/doc 规则变更 + 跨会话持久化规则，触发 Escalate 强制路由三条。

Founder 回复"这些问题都能依靠你们讨论的结果去执行"——明确授权基于 Gemini + Claude 讨论结果自主推进。

## 3. 决策

### 3.1 最终规则（落库到 `flametree_rss_reader/docs/DESIGN_PHILOSOPHY.md` §3 新增子段）

1. **删除 `ColorTokens.accent` 同色别名** + 全项目 24 处 `colors.accent` 调用替换为 `colors.primaryContainer`
2. **Tier 1 典型场景清单**：Login CTA、Dialog 确认键、AI Summary Panel 品牌头 + 主生成按钮、Settings Page Header 标题
3. **Tier 2 典型场景清单**：Article Header bookmark/toggle 激活态、Mobile Reader bookmark/share、Feed AI Switch、article_content 链接
4. **Tier 1 例外登记**（白名单）：Settings Sidebar 选中竖条（持续品牌上下文锚点）、Sync Progress Bar（决定性后台操作进度）
5. **禁止的规避路径**：创建 `accent-cta`/`accent-active` 拆分 token、用 alpha 淡化在 Tier 2 场景、创建 `primaryMuted` 色值
6. **Local Decision Rule**：写代码前自问 "这是关键跳转/品牌瞬间吗" → Tier 1；"这是局部 on/off/select 吗" → Tier 2；拿不准 → **不默认走 Tier 1**，升级 Founder
7. **Commit 硬约束**：任何新引入 `primaryContainer` 的组件，commit message 必须标注 Tier 1 典型场景或例外条目

### 3.2 ui-vision-check skill 检查启发式替换

在 "AI 视觉打磨边界" 允许区新增 **"品牌色 Tier 违反 (Brand Color Tier Violation)"** 检查维度：

- 项目若定义了 Active State Tier Rules，检查品牌色是否被用于 Tier 2 局部状态
- 违反表达为 Token 语言（「X 组件应通过形态 + 底色表达激活，不应使用 primaryContainer」）
- **禁止**基于"红色元素数量超过 N 个""视觉太红"等单屏计数/主观强度判断（替代此前"红色泛滥"检查范式）

### 3.3 执行策略（Claude 建议的三步拆分）

- **Step 1**（低风险，已完成）：删 accent 别名 + grep 全量替换为 primaryContainer（零像素差）
- **Step 2**（本决策记录 + DESIGN_PHILOSOPHY + ui-vision-check skill 更新）
- **Step 3**（高风险，逐点 review）：基于 Tier 原则重审 5 处阅读态哑橙，给出 Tier 分类草案 + 改动建议 + 前后截图对比，Founder 逐项点头

## 4. 为什么这么改

- **"品牌色稀缺性即品牌"**：哑橙 `#BA573C` 是 FlameTree 少数几个用户长期可感知的品牌瞬间，稀缺性本身就是品牌识别手段。Tier 1 清单保留 5-6 处真正的品牌接触点，Tier 2 清理 5-6 处被稀释的触点
- **对抗 M3 默认 + 保留 Material 生态**：不脱离 Material 3 token 体系（`primaryContainer` / `tertiary` / `surfaceContainerHigh` 都是标准 M3），但在"何时使用" 层面覆盖 M3 默认行为
- **AI-Only 可执行性**：Tier 1/Tier 2 是本地二元判断（"这组件的作用是啥"），AI 不需要全局视图就能决策，符合"Local Decision Rule"
- **防复发机制**：改 ui-vision-check 检查启发式，下次截图审计不会再提"红色泛滥"这种已被 SSOT 杀死的假命题，也不会因为某页有几处哑橙就触发 Refinement 建议

## 5. 为什么不选其他方案

### 拒绝 Reject TODO 现状冻结
- Gemini 和 Claude 都认为这是过度理性化：审计只覆盖 iOS 列表页视角，没系统性审阅读态哑橙密度
- "SSOT 整合胜利 = 全部问题解决"是论证跳跃，阅读态哑橙过载是真实产品问题（5-6 处触点）
- 工作流上，留下未处理的设计债务会污染下次 `/ui-vision-check` 的基线

### 拒绝原 TODO 粗暴执行（accent 全改 tertiary）
- 制造状态盲（Tier 2 激活态与禁用态同色，全中性灰变体）
- 抹掉所有品牌瞬间（Login/Dialog/AI Panel），Warm Study 哲学沦为无品牌识别的性冷淡
- 违背 Material 3 约定却没给对抗理由（对抗 M3 必须来自设计哲学，而非机械规则）

### 拒绝方案 C（单屏哑橙触点密度上限）
- 阈值（"≤3 处"）无客观依据，拍脑袋数字最容易被下次审计推翻
- AI 修单组件时无全局视图，遍历整屏数触点成本过高
- 无法编码为 Token / Lint 规则，只能活在文档里，违反 ADR-007 "工程约束 > 文档规范"

### 拒绝拆分 `accent-cta` + `accent-active` 双语义 token
- 新别名 = 新债务，Tier 2 色值和 Tier 1 色值不同时反而需要命名 3 个 token
- AI 判断"这里用 accent-cta 还是 accent-active"的难题等价于"这里是 Tier 1 还是 Tier 2"，没有减少决策负担
- 同色别名已经教过我们一次（`accent = primaryContainer`），不再重蹈覆辙

## 6. 验证方式

### 6.1 Step 1 验证（已完成）

```bash
$ grep -rn "colors\.accent" lib/
# 输出：No remaining colors.accent references

$ flutter analyze
# 输出：No issues found! (ran in 8.0s)
```

替换覆盖文件清单（11 个）：
- `lib/shared/theme/color_tokens.dart`（删 `accent` 常量 + `get accent` getter）
- `lib/features/articles/widgets/ai_summary_panel.dart`（6 处）
- `lib/features/articles/widgets/article_header.dart`（6 处）
- `lib/features/articles/widgets/article_content.dart`（1 处）
- `lib/features/articles/pages/mobile_article_reader_page.dart`（3 处）
- `lib/features/feeds/widgets/rename_category_dialog.dart`（1 处）
- `lib/features/feeds/widgets/move_feed_dialog.dart`（2 处）
- `lib/features/feeds/widgets/add_feed_dialog.dart`（2 处）
- `lib/features/feeds/widgets/feed_ai_config_sheet.dart`（1 处）
- `lib/features/settings/pages/feed_settings_page.dart`（1 处）
- `lib/shared/widgets/sync_progress_bar.dart`（1 处）
- `test/shared/theme/app_theme_test.dart`（2 处测试断言）

Step 1 视觉零像素差（同色别名替换），不需要截图验证。

### 6.2 Step 2 验证（本次）

```bash
$ grep -n "Active State Tier Rules" flametree_rss_reader/docs/DESIGN_PHILOSOPHY.md
# 期望：在 §3 末尾找到新增子段

$ grep -n "品牌色 Tier 违反" ~/.claude/skills/ui-vision-check/SKILL.md
# 期望：在允许区找到新 bullet

$ ls ~/.claude/docs/decisions/ | grep 04-active-state-tier
# 期望：本决策记录文件存在
```

### 6.3 Step 3 验证（后续）

Step 3 完成后需：
- `flutter analyze` 无 error
- `bash scripts/take-screenshots.sh ios` + `macos` 重截
- 逐项对比 article_header / ai_summary_panel / bookmark / toggle 的激活态前后差异
- 无法自主判定的 Tier 归属 → 升级 Founder 逐项点头

## 7. 踩坑记录

- **sed 批量替换的前提是 "accent" 只作为 ColorScheme getter 使用**（不作为其他变量名）。grep 确认项目内无其他 `.accent` 语义，才能安全 sed。
- **`flutter analyze` 必须包含 test 目录**：第一次替换后 analyze 发现 `test/shared/theme/app_theme_test.dart` 还在用 `accent`，说明 grep 范围不能限于 `lib/`。
- **AppColorScheme 的 `accent` getter 删除后，仍保留 `primaryContainer` getter**（后者本来就存在）—— 所以所有调用点换用 `colors.primaryContainer` 是直接可用的路径，无需新增 getter。
- **Gemini 方案 "编译错误强制 re-evaluation" 的漏洞**：AI-Only 项目里 AI 倾向于"最小阻力修通"而非"深度重想"，编译错误驱动的重构在无人类程序员的环境下不可靠。Claude 修正为**先定 Tier 分类表，再逐点根据表替换**。此坑后续类似"靠工具报错驱动行为变更"的场景都要警觉。

---

## 8. 第二轮 `/think` 追加（2026-04-13 下午，v2.4）

### 8.1 背景

v2.3 规则落库 + Step 1 代码清理 commit 后，Claude Code 对剩余 5 类"需判定" `primaryContainer` 使用点做第二轮 Gemini `/think` 讨论，请求逐项 Tier 归属判断。Claude 初判里把 3 项归为"Tier 1 例外"（Settings Card Selector / AI Provider 选中 / Advanced Settings ornament）。

### 8.2 Gemini 严厉驳回

Gemini 全盘驳回"Tier 1 例外"妥协路径，核心论证：

1. **Level 1 vs Level 3 信息架构分层**：Sidebar 是 Level 1 全局导航（决定整个视窗主体内容切换），Card Selector 是 Level 3 页面内组件（只影响某一个维度的纯量配置）。两者不能混为一谈。
2. **装饰不是品牌瞬间**：`"A Quiet Curator"` tagline / 底部 ornament 不具备"促发行动"属性，滥用行动色违背"Quiet Curator"哲学的核心——安静沉思。装饰应比文字更安静。
3. **低频页面不是借口**：Tier 规则保护品牌色稀缺性，与页面访问频率无关。用"年级别访问"给 Advanced Settings 开后门是规则失效前奏。
4. **数据可视化与交互 Tier 是异构范式**：chart 用色逻辑是"发散与对比"，UI 用色逻辑是"收敛与引导"。让图表复用 `primaryContainer` 制造 CTA 混淆，必须完全隔离。
5. **例外清单破窗效应**：若 #2 #3 L196 再加"卡片选中态"，例外清单会无限膨胀，规则失效。必须收紧定义。

### 8.3 Claude Code 的采信与立场

Claude Code 采信 Gemini 全部 5 项判定 + 2 条新规则。关键采信理由：

- **Level 1 vs Level 3 区分比"持续锚点/瞬时"时长启发式更稳定**：后者可被"AI Provider 选中 vs focusedBorder 是 1:3 的时长比而非 1:100" 推翻，前者基于信息架构层级不可被同类反例攻破
- **装饰降 tertiary 符合"安静比品牌优先"的 Quiet Curator 一致性**
- **Gemini 的 `fillColor = surfaceContainerHigh` 补偿 focus border 聪明解法**——Material 3 TextField 无法形态切换时，用底色补强 focus 反馈强度
- **数据可视化独立规则防止每次遇到图表重新判一次**

立场 Escalate → Founder 回复"好的全部实施"→ 授权自主推进 v2.4 规则更新 + 代码层大改。

### 8.4 v2.4 规则变更点

1. **Tier 1 例外严格定义**：只接受「Level 1 全局导航」+「Level 1 全局后台状态」两类。页面内组件级选择 / 装饰元素 / 低频页面一律 Tier 2
2. **Tier 2 典型场景扩展**：新增 Settings Card Selector 全部选中态、TextField focusedBorder、Advanced Settings 路径反馈 + ornament 装饰
3. **新增「数据可视化隔离规则」子段**：禁止图表/占比条使用主色调，短期 `tertiary/secondary/surfaceContainerHigh` 组合，中长期可扩 `chart*` 专属 token
4. **新增例外的唯一路径**：Founder 显式签字 + 写入清单 + 决策记录说明。Claude Code 不得自主判定新例外。

### 8.5 代码层改造清单（v2.4 落地）

- **Advanced Settings**：inbox border 改底色块、folder icon outlined→filled + tertiary、ornament 改 `tertiary.withValues(alpha:0.3)`
- **Settings Card Selector**：选中态 border 去除主色，改 `surfaceContainerHigh` 底色 + `tertiary` 字重升级 + 6×6 dot `tertiary`
- **Appearance Settings**：选中字号 "Aa" → `tertiary` + 字重 w700，6×6 dot → `tertiary`
- **AI Assistant Settings**：Provider icon 选中色 → `tertiary` + 背景 `surfaceContainerHigh`；Test & Save 按钮 **保留** `primaryContainer`（Tier 1）
- **SettingsInputField**：`fillColor` 聚焦→`surfaceContainerHigh`，`focusedBorder` 色→`tertiary`，宽度保留 2px
- **StorageOverview**：三色条改 `tertiary`(70) / `secondary`(15) / `surfaceContainerHigh`(15)
- **Article Header / Mobile Reader / Switch / Link 等 10 处 Tier 2** 按 v2.3 既定方向改造（见 TODO.md 支线 B）

### 8.6 踩坑记录追加

- **"持续锚点"辩护路径是规则失效前奏**：Claude 第一版初判用"选完后下次进页面还是选中"论证 Card Selector 归 Tier 1 例外——Gemini 指出这是工程师妥协错误，因为害怕失去常规反馈强度，用扩大例外绕过规则。若接受此辩护，3 个月后 Settings 所有选中态都会以"持续"为由索要例外，Tier 体系名存实亡
- **Material 3 默认行为不是设计哲学的豁免权**：TextField focusedBorder 默认 `primaryContainer` 是 M3 约定，但"Quiet Curator"哲学下聚焦是瞬时状态不是品牌瞬间，必须用底色补强而不是沿袭默认色
