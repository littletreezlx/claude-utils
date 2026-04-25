# 2026-04-24-07 — 全局 Warm Ceramic 硬绑定解耦,改走"默认母语 + 反例驱动"

## 问题

Founder 发现全局 `~/.claude/` 下 4 个 skill/command 硬编码 "Warm Ceramic / 暖陶 / 施釉陶 / terracotta" 作为默认美学基调,导致:

1. 全局评审工作流(`/ui-vs`、`ui-vision-advance`、`ui-vision-check`)对任何项目都以"暖陶瓷"为标尺审,非暖调项目会系统性跑偏
2. 各项目 `docs/ui/UI_SHOWCASE.md` 在 AI 影响下"照抄":music/pick/rss_reader 深度扎根 Warm Ceramic(pick 类名 `WarmCeramicTokens`),coffee/image-studio 没接入,littletree_x 薄,只有 flametree_ai 通过独立 PRODUCT_SOUL(「Amber Terminal」)成功跳出
3. `ui-design-router` 派生 Brief 默认 accent 列表锁死 `terracotta/amber/peach/rust/sand/clay`,新项目被限制在暖色家族

Founder 品牌 flametree,确实偏温暖感——所以"完全去温暖"不是目标,目标是把"温暖感"从**全局隐式硬编码**翻转为**项目显式声明**,避免 AI 把 Founder 的合法偏好误当成所有项目的强制标尺。

## 讨论过程

`/think` 双模型对抗(Gemini + GPT,2026-04-24):

### Gemini 的方案(被否决):Material Metaphor DI

- PRODUCT_SOUL 强制 YAML 结构化字段(`core_material` + `tactile_feel` + `edge_treatment`)
- 缺失/空泛熔断
- 因果论证锁(AI 写 50 字"产品价值→材质"推演)
- 现有三项目零代码后置补齐

**核心论点**:LLM 对抽象方法论投射宽泛油滑,抽离具体 prior 会退化到万金油;一人 Lab 场景 Founder 品味就是基础设施。

### GPT 的对抗攻击(完胜)

Gemini 方案的 4 个致命漏洞:

1. **"显式声明改变生成分布"假设很脆**:YAML 字段不天然是最高优先级信号,LLM 采样分布受训练语料 prior + repo 局部模式 + 全局 skill 稳定描述主导,新加的 `core_material: newspaper` 压不过这些更强 prior,结果是**"语言上服从 schema,实现上复用熟悉模式 = 被新标签包装的旧风格"**
2. **因果锁是自证循环**:AI 先给自己找理由,再由自己判定理由成立——不是 guardrail,是 rhetoric layer。LLM 最擅长局部自洽叙述,要求它解释只会更流畅地解释,不会诚实暴露"其实我只是沿用了 Warm Ceramic"
3. **熔断依赖 AI 自我否定能力**:AI 倾向于认为自己写的已足够好、倾向于把模糊词包装成具体词、倾向于选择能继续任务的解释。"让报销申请人自己判断这笔开销是否必要"——熔断会迅速演化成"暂定 Warm Ceramic"、"现代简约但温润"等绕过
4. **把"材质隐喻"误当差异化主轴(最狠)**:7 个项目长得像不是因为缺材质声明,而是因为差异真正来自上游变量——任务节奏(scan/choose/immerse/monitor)、信息密度、交互风险、品牌姿态、时间感。**材质是末端表达,不是上游决定因子**。Gemini 把控制点设在末端 = 战略误判"把风格命名当风格生成的原因"

GPT 还列出 3 个月后 4 种失败形态,最危险是 **C:Founder 误以为问题已解决**——问题从"显性同质化"变成"被制度合法化的同质化",仪式化约束降低发现坏结果的敏感度。

### GPT 的方案(采纳):反例驱动 + 默认母语

核心原则:**允许同质,不允许无意识同质**。Founder 想继续用 Warm Ceramic 允许,但必须经过一句论证"为什么这次继续 Warm Ceramic 是项目本质,而不是偷懒默认"。

机制:LLM 最怕空白最爱抄默认,给它一个明确反例比给它十个字段更有效——**反例比 schema 更能改变 LLM 采样重心**。

## 为什么这么改

选 GPT 方案,因为:

1. **机制真正可行**:反例驱动(强迫项目先声明"本项目最不该像 Warm Ceramic 的地方")比 schema 更贴近 LLM 实际采样行为——LLM 最怕空白,明确反例直接改变采样重心,不依赖"AI 自我批评"这个 AI 不擅长的能力
2. **改动轻**:只改 3 处文本(全局原则段 + UI_SHOWCASE 必备段 + ui-design-router 前置自检),不建 schema 不加熔断,符合 AI-Only 铁律"务实主义 > 完美架构"
3. **尊重 Founder 品味事实**:Warm Ceramic 保留为"FlameTree 默认母语"——承认它是合法偏好,不假装中立。继承需论证,但允许继承
4. **失败更易被发现**:无重型制度外壳,Founder 对"审美失守"的警觉保留。vs Gemini 方案"被制度合法化的同质化"——后者是最危险的

## 为什么不选其他方案

### 为什么不选 Gemini 的 Material Metaphor DI

- 4 层机制(schema / 熔断 / 因果锁 / backfill)每层都被 GPT 精准命中:schema 不改变生成分布、因果锁是 rhetoric、熔断依赖 AI 自检、材质是末端不是上游
- 工作量中等(改 4 skill + 建 YAML schema + 加熔断步骤 + 现有三项目 backfill),回报可疑
- 最致命:即使机制全对,"让 Founder 误以为问题已解决"的副作用远超收益

### 为什么不维持现状

两个模型都隐含同意"当下该重新评估"。GPT Phase 6 直球"yes,过度约束——全局硬编码不是锚,是预判胜利后的偷懒"。推迟 refactor 到未来出现第一个冷调/严肃调项目时,触发一次混乱的全局重构。现在改是"无遗憾一步"。

### 为什么不完全抽离(我最初的方向 1)

双模型一致论证会导致万金油退化:抽象方法论 prior 让 LLM 退到广阔隐空间抓最大公约数,即泛大厂 UI。Founder 品味是合法客观事实,假装中立只增加 AI 猜测成本。

## 实施清单

### 改动点 1 — 全局评审 skill/command 把 Warm Ceramic 降为"默认母语"

- `~/.claude/commands/ui-vs.md`:四根支柱的"Warm Ceramic"降级为"FlameTree 默认母语(可被项目 UI_SHOWCASE §Vibe + Anti-default note 覆盖)";软性引导段的感官隐喻改为"从项目 Vibe 段派生,而非全局硬编码"
- `~/.claude/skills/ui-vision-advance/SKILL.md`:Tone 步骤"从暖陶瓷基底出发"改为"从项目 UI_SHOWCASE §Vibe + §Anti-default note 派生基底"
- `~/.claude/skills/ui-vision-advance/references/design-philosophy.md`:整个文件从"全局设计哲学"降为"FlameTree 默认母语示例库",文件头声明项目可通过 Anti-default 覆盖
- `~/.claude/skills/ui-vision-check/SKILL.md`:"Warm Ceramic 专属维度"改为"项目 Vibe 专属维度",评估指标从项目 UI_SHOWCASE §Vibe 段动态加载;Vibe Check 的"目标"从硬编码"早晨阳光洒在早餐桌上的陶瓷餐具"改为从项目 Vibe 段读取
- `~/.claude/skills/ui-design-router/references/brief-template.md`:默认 accent 列表 `terracotta/amber/peach/rust/sand/clay` 改为"本项目 UI_SHOWCASE §Invariants 中登记的 accent"(完全去 FlameTree 默认值污染)

### 改动点 2 — UI_SHOWCASE.md 新增第 4 段必须:Anti-default note

`~/.claude/guides/doc-structure.md`:UI_SHOWCASE.md 强制段落从 3 段改 4 段,新增:

> #### 4. Anti-default note(强制,反照抄锚)
> 一句话声明**本项目最不该像 FlameTree 默认母语(Warm Ceramic / 暖陶 / 施釉陶)的地方**。
> 若本项目就是 Warm Ceramic 合理继承者,本段写**为什么继承是项目本质而非偷懒默认**(不允许空白或"本项目采用 Warm Ceramic"这种空洞声明)。
> 目的:LLM 最怕空白最爱抄默认——明确反例改变 AI 采样重心,比声明"我用什么"更有效。

### 改动点 3 — ui-design-router 派生 Brief 前置自检

在 `~/.claude/skills/ui-design-router/` 派生 Brief 流程中加入 2-3 个固定自检问题(在读 UI_SHOWCASE 之后、写 DESIGN_BRIEF 之前):

1. 本项目 UI_SHOWCASE §Anti-default note 有没有写?若无 → 阻塞,先让 Founder 补
2. 本轮改动是不是在**重复 FlameTree 默认母语(Warm Ceramic)**?如果是,§Anti-default 是否允许?不允许就不能写 Warm Ceramic 变体进 Brief
3. 本轮 Brief 里有没有**违反 §Anti-default 声明的反例**?(例:Anti-default 说"不该有陶土感",Brief 却写"希望卡片呈现施釉陶感" = 冲突,停)

## 现有项目 backfill 策略(按需,不紧急)

- music / pick / rss_reader:深度 Warm Ceramic 合理,只需在 UI_SHOWCASE 加一句"为什么 Warm Ceramic 是本项目本质"——推荐 Founder 按需补,不强制此次一并做
- ai:已有独立 PRODUCT_SOUL「Amber Terminal」,UI_SHOWCASE 补 Anti-default 声明(如"不该有陶土感和生活方式气息")
- coffee / image-studio:没 UI_SHOWCASE,下次做 UI 时跑 `/ui-bootstrap` 时会生成新模板(含 Anti-default)
- littletree_x:UI_SHOWCASE 薄,下次 UI 改动时补 Anti-default

## Think 讨论上下文

- 模型:Gemini 3.1 Pro Preview + GPT-5.4,Solo 两轮对抗
- 核心 reframe 路径:Founder 原问题"过度约束 vs 必要锚" → Gemini reframe 为"隐式 vs 显式" → GPT 再 reframe 为"末端词汇 vs 上游变量"
- 两次 reframe 后的最终结论:问题不在"约束强度",也不在"声明是否存在",而在"LLM 怎样才能不回归 default 采样分布"——反例(负向约束)是 LLM 能识别的最强锚
