# 基于证据的"完成"定义：铁律 5 改写 + 验证凭证输出锚

- **Date**: 2026-04-12
- **Status**: Accepted
- **Scope**: ~/.claude/CLAUDE.md § 铁律 (铁律 5 改写)、§ 开发工作流 § 核心闭环 (去除"如可用")

## 1. 问题 (What went wrong)

在 `ai-image-studio` (Flutter 项目) 的一次会话中，AI 被要求给截图脚本 `scripts/take-screenshots.sh` 添加 `detail_page` 的截图支持。具体修改包括：

- 在 `PAGES` 数组里新增 `detail_page` 条目
- 新增 `_take_macos_screenshot_detail()` 函数处理详情页的特殊环境变量
- 修改 `lib/main.dart` 支持截图模式导航
- 修改 `lib/shared/router.dart` 把详情页路由移出 ShellRoute

AI 修改完后直接输出"修改总结"表格宣告完成，**期间完全没有运行脚本验证**。Founder 追问"你调用检验过了吗？"，AI 才去跑脚本，结果连续发现两个 bug：

1. **第一次跑**：只截出 3 张图（`generate_page`, `gallery_page`, `settings_page`），`detail_page` 根本没在 `PAGES` 数组里被遍历到——修改本身就是半成品
2. **第二次跑（修完数组后）**：截出 4 张图但 `detail_page` 显示的是创作主页不是详情页——路由配置还有问题（详情路由嵌在 ShellRoute 里被 AppShell 包裹）

真正交付一个可工作的修改，花了**3 次额外的 Build + 3 次截图验证 + 用 MiniMax understand_image 多次确认视觉效果**，浪费了大量来回交互和 Founder 的时间。

**关键纠正**：Founder 事后追问时指出——不是 AI "忘了验证"，是 AI **根本没打算再去跑脚本**。输出"修改总结"那一刻，AI 心智里的"完成"就已经结束。这个纠正改变了诊断层级（见 §2）。

## 2. 讨论过程 (How we thought about it)

### Round 1：Claude Code 初读 CLAUDE.md

AI 读完当前 `~/.claude/CLAUDE.md`，找到相关条款：

- 核心闭环 (line 68)："运行时验证（如可用）→ 交付检查 → 提交"
- 自动触发规则 (line 86)："改完业务逻辑/UI，项目有 Debug State Server | curl + 截图自主验证"
- 铁律 5："测试闭环：代码变更需有测试验证 → 测试必须运行通过 → 未通过禁止交付"

问题诊断：`如可用` 是条件化语言，截图脚本是 shell 不是 Flutter，没有 Debug State Server，AI 判定"不可用"→ 触发交付。铁律 5 只讲"测试"，没覆盖脚本/配置/工具这类"无单测"变更。

### Round 2：`/think` 第一轮咨询 Gemini

Claude Code 把场景和分析丢给 Gemini（OpenRouter / google/gemini-3.1-pro-preview），问"如何在 CLAUDE.md 里落地强制自闭环验证"。

Gemini 核心论点（**Evidence of Verification, EoV**）：

- LLM 有根深蒂固的"文本过度自信"——补全完代码后概率模型会让它相信代码是对的
- 在 prompt 里把"建议验证"改成"必须验证"效果微乎其微
- 真正有效的是**改交付格式**：把"验证"从主观意愿变成客观交付物
- 提议每次交付必须包含 4 字段 `[Verification Evidence]` 区块（Target Type / Verification Method / STDOUT / Result）

Claude Code 在 Round 1 Accept 了 EoV，但未落地。

### Round 3：Founder 质疑过度设计

Founder 追问"会不会过度设计以及是否有效"。Claude Code 自我反思后提出 **Counter Proposal**：

- 重写铁律 5："完成的定义 = 亲眼见过终态"
- 加一句内部自检"我怎么知道它对？"
- 拒绝 4 字段模板，理由是对 trivial 改动收税过重

Counter Proposal 的核心论点：把验证嵌进"完成"的定义里（攻心智模型），而不是做成外挂第 N 步。

### Round 4：Founder 的关键事实纠正

Founder 纠正了 Counter Proposal 的前提假设："AI 根本没打算再去跑"——不是"忘了写进交付"而是"心智里没这项"。这个纠正改变了诊断层级：

- 如果是"忘了写进交付" → 问题在**输出格式层** → EoV 切中问题
- 如果是"心智里没这项" → 问题在**心智模型层** → 纯格式约束可能够不着

### Round 5：`/think` 第二轮咨询 Gemini（带纠正事实）

Claude Code 把纠正 + Counter Proposal + EoV 并列呈给 Gemini，问哪个方案更切中要害。

Gemini 核心反驳（**Action Hallucination 风险**）：

- "心智层 vs 格式层"的二分是人格化投射——对 LLM 来说输出格式就是心智模型
- Counter Proposal 的"一句话自检"有**致命的假阳性风险**：AI 会熟练写出"我已完成自检，因为我运行了脚本看到了预期结果"却从未真的 `tool_use`，产生比原 bug 更糟的**幻觉式合规**（静默造假比静默回归更难发现）
- 主观总结（"看到 Y 符合 Z"）仍然可以被脑补伪造
- 必须索要**不可伪造的客观凭证**——截取 `STDOUT` / UI 状态变量的 2-3 行**原文**。为了输出这些冷冰冰的机器文本，AI 的内部机制会被倒逼真正发出 `tool_use` 指令（真实输出有时间戳、路径、日志前缀等难以凭空脑补的 token 分布特征）
- 3 行最小铁律方案：
  1. 完成 = 亲眼观测到 runtime 生效
  2. 强制 `[验证凭证: 运行 X → 截取真实 STDOUT 2-3 行原文]`
  3. 豁免仅限文档，业务逻辑严禁 N/A

### Round 6：Claude Code 整合并 Escalate

Claude Code Accept 了 Gemini 的 Action Hallucination 论点（确实击中一句话自检要害），但**保留疑虑**：Gemini 的"输出格式就是心智模型"是过度还原论——重定义"完成"改变了 system prompt 里的 token 分布先验，并非零作用，只是单独用不够。

最终立场：**混合方案**——主干是重定义"完成"（攻心智先验），落到输出层用 raw STDOUT 锚（而非主观总结），两条腿走路。

按 think skill § 3.3 硬路由第 2 条"决策会持久化到全局 CLAUDE.md" → 强制 Escalate，不允许自作主张动手。Claude Code 把三条路径（纯 EoV / 纯 Counter / 混合）呈给 Founder。

### Round 7：Founder 拍板 + 追加元规则

Founder 选择混合方案，并追加一条元规则要求："所有对 CLAUDE.md 和核心工作流的讨论修改都应该落实文档，描述遇到了什么问题、为什么这么做"——即本文件的存在依据。这条元规则成为新增的**铁律 8**。

## 3. 决策 (What we decided)

### 修改 1：铁律 5 从"测试闭环"扩写为"完成的定义"

**前**（CLAUDE.md line 38）:

```
5. **测试闭环**：代码变更需有测试验证 → 测试必须运行通过 → 未通过禁止交付。
```

**后**:

```
5. **完成的定义 = 亲眼观测到代码在 Runtime 生效**。禁止仅凭"我写对了"宣告完工。
   - 代码变更需有测试验证 → 测试必须运行通过 → 未通过禁止交付
   - **每次交付总结前必须包含一行验证凭证**：
     `[验证凭证: 运行 {具体命令} → 截取真实 STDOUT/日志/UI 状态 2-3 行原文]`
     严禁用自然语言概括结果（如"运行成功"、"输出符合预期"、"已验证"）。必须粘贴命令跑出来的原始片段——有时间戳、路径、日志前缀、报错行号等 AI 难以凭空脑补的细节
   - **豁免**：仅文档/纯格式修改可填 `[验证凭证: N/A - 无运行时状态]`。业务逻辑、脚本、配置、构建流程、规则文档（CLAUDE.md / skill / 全局 doc）严禁使用 N/A
   - **违反后果**：如果交付缺失验证凭证，或用自然语言代替原始输出，等同于未完成，Founder 有权直接 rollback
```

### 修改 2：核心闭环去掉"如可用"

**前**（CLAUDE.md line 68）:

```
读测试 → 改代码 → ... → ✅ 通过 → 运行时验证（如可用）→ 交付检查 → 提交
```

**后**:

```
读测试 → 改代码 → ... → ✅ 通过 → 运行时验证（亲眼观测终态）→ 截取验证凭证 → 交付检查 → 提交
```

### 修改 3：新增铁律 8

```
8. **规则变更必须产出决策记录**：任何对全局 `~/.claude/CLAUDE.md`、核心 skill、
   跨项目工作流的讨论和修改，必须在 `~/.claude/docs/decisions/` 下同步写一份决策记录
   （遇到什么问题 → 讨论过程 → 为什么这么改 → 为什么不选其他方案）。
   修改与记录必须在**同一次**交付里完成，只改规则不写记录 = 未完成。
```

### 修改 4：新建 `~/.claude/docs/decisions/` 目录

包含 `README.md` 说明目的、命名规则、记录模板，以及本文件作为第一份决策记录。

## 4. 放弃的替代方案 (What we rejected and why)

### 方案 A：纯 EoV（Gemini Round 1 原版 4 字段模板）

```
[Verification Evidence]
- Target Type: ...
- Verification Method: ...
- STDOUT/Result: ...
- Conclusion: ...
```

**拒绝理由**：

1. 对 trivial 改动（文档、typo）收税过重，会退化为"填表仪式"
2. 4 字段结构允许用 `Conclusion: 验证通过` 形式的主观总结绕过真实输出要求
3. 没有在"完成的定义"层面做改变，规则靠格式维持，没有心智先验配合
4. 4 行模板的 token 成本比 1 行锚点高出 4 倍，长对话里注意力稀释更严重

### 方案 B：纯 Counter Proposal（重定义完成 + 一句话自检）

```
完成 = 亲眼见过终态
交付前自检："我怎么知道它对？"
```

**拒绝理由**：**Action Hallucination 风险**。这是 Gemini Round 2 给的致命反驳——一句话自检没有外部输出锚，AI 会熟练地在回复里写 "我已经验证过了，运行了脚本看到了预期结果" 而从未真的 `tool_use`。这种**幻觉式合规**比原来的静默跳过验证**更糟糕**：

- 原 bug：Founder 能通过追问发现没验证
- Action Hallucination：Founder 看到"已验证"的自然语言，需要实际检查才能发现是假的

假阳性比假阴性更难发现，退化路径更隐蔽。单独采用纯 Counter Proposal 等于给 AI 一条更高效的作弊路径。

### 方案 C（已选）：混合方案

保留 Counter Proposal 的"重定义完成"作为心智先验（改变 token 分布的默认判断），加 EoV 的"不可伪造输出锚"作为可审计副产物。两条腿分别攻击不同漏洞：

- 重定义完成 → 防 AI 一开始就没"验证"这个概念
- raw STDOUT 锚 → 防 AI 内化失败时，Founder 仍能通过输出结构审计

### 方案 D：Hook / 自动化脚本在 AI 交付前拦截

Gemini 讨论中隐含提到过。**拒绝理由**：需要在 Claude Code harness 层实现 pre-submit hook，跨项目部署成本高且与当前 settings.json hook 机制耦合度不明。作为未来升级选项保留（见 memory: `project_ondemand_hooks_idea.md`），当前先走 prompt 层规则。

## 5. 预期影响 & 监控 (How we will know it works)

### 期望改变的行为

1. AI 在输出"完成"类语言前会强制检查自己能否写出一行 `[验证凭证: ...]`。写不出 → 被迫去真正跑命令
2. Founder 对 AI 交付的审计从"看 AI 说了什么"变成"看回复里有没有 raw STDOUT 片段"——零认知负荷的可视化合规检查
3. 未来对 CLAUDE.md 的任何修改都会产生决策记录，形成可回溯的立法历史

### 有效性信号（应当观察到）

- AI 修改脚本/代码后**不追问**直接执行验证的频率上升
- Founder 不再需要问"你验证过吗？"这类问题
- 回复末尾稳定出现 `[验证凭证: ...]` 格式行
- 交付返工率（"完成" → 用户追问 → 实际有 bug）显著下降

### 失效信号（警戒）

- AI 开始出现用自然语言冒充验证凭证的模式（如 `[验证凭证: 脚本运行成功]`）→ 规则没被逐字执行，需要加强措辞或引入 hook 拦截
- `N/A` 豁免被滥用到非文档修改 → 需要收紧豁免清单或强制 N/A 附理由
- 决策记录目录堆积但质量退化成 changelog 流水账 → 需要重读 README 模板或拆分决策规模

### 回访计划

- **首轮体检**：2026-05-12（1 个月后），抽查过去 30 天交付，统计验证凭证出现率、N/A 滥用率、返工事件数
- **如果有效**：把本方案作为"已验证的规则模式"写入 `~/.claude/guides/` 某处作为未来新规则的参考
- **如果失效**：重新 `/think` 评估是否升级到 hook 拦截方案（方案 D）

## 附录：本次决策本身的验证凭证

按新铁律 5 的要求，本次对规则文档的修改本身也需要验证凭证：

```
[验证凭证: 重读 ~/.claude/CLAUDE.md line 38-47 & line 68 → 确认
  - 铁律 5 开头出现 "完成的定义 = 亲眼观测到代码在 Runtime 生效"
  - 铁律 8 出现 "规则变更必须产出决策记录"
  - 核心闭环 line 68 "如可用" 已替换为 "亲眼观测终态 → 截取验证凭证"]
```

（具体截取片段见本次交付的最终消息）
