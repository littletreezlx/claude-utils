# 2026-04-24-05: `/ui-bootstrap` 后续打磨（.bak 审阅 / 文档一致性 / 结构去重 / 幂等性简化）

## 遇到什么问题

`/ui-bootstrap` skill 在 `2026-04-24-03` 决策后升级了三大能力（inbox 标准化 + 去重 + 漂移自动分类）。Founder 在 `flametree_rss_reader` 上实战跑一遍（手动版），然后让我诊断 skill 还有什么要改的。

我列了 10 条诊断清单（🔴 4 / 🟡 3 / 🟢 3），Founder 选"按你建议执行"—— 即先做 🔴 四条。四条都是**文档一致性 + 避免下次遗漏**，改动小、价值大，且其中第 1 条（`.bak` 审阅）是 AI-Only 协作模式下必须机械化的 gap。

### 痛点 1：`.bak` 备份沉默遗留

Phase 4.2 写着"UI_SHOWCASE 旧版备份为 .bak，提示用户手动合并" — 但 AI-Only 项目里"手动合并"不会自动发生。实战跑完 rss-reader bootstrap 后，我手动对比 UI_SHOWCASE.bak 和 DESIGN_BRIEF.bak 的哲学段落是否沉淀进新 PRODUCT_SOUL / DESIGN_PHILOSOPHY §1.4，确认全沉淀后删 .bak —— 这个动作下代 AI 不会记得做，除非写进 skill。

### 痛点 2：Phase 4.2.1 引用了不存在的章节

原文："这些 TODO 条目都引用 `docs/design/DRIFT_REPORT.md §旧 UI 子文档` 章节(下面 5.3 补一段)作为定位锚"

但 Phase 5.3 的 DRIFT_REPORT 模板里没有这个章节 —— 引用断裂。DRIFT_REPORT 定义上是**代码漂移**报告，不应承载**文档漂移**。"旧 UI 子文档审计"属于文档漂移，不该塞进 DRIFT_REPORT。

### 痛点 3：Phase 0 和 Phase 2 结构检查重复

Phase 0.2 已经检查了 `{Name}.html + styles.css` 是否存在，Phase 2 还有一段"结构检查"重复说"找不到 primary HTML → Phase 0 已拦截,此处不应再出现"。这是开发过程中的保留防御性代码，执行时是噪音。

### 痛点 4："一次性 vs 可重复跑" 段与 Phase 0.3 去重逻辑重叠

`2026-04-24-03` 决策加入了 Phase 0.3 SHA256 去重（保证内容不变时不产生新归档），但 skill 末尾还留着旧的"一次性 vs 可重复跑"段，描述了一个不同的分支（"检测到 EXTERNAL_REFS.md 已存在 → 提示'是否 re-onboard'"）。两套分支并存，语义冲突。

## 讨论过程

Claude 列诊断清单 10 条（🔴/🟡/🟢 三级）。Founder 选 🔴 四条。

Claude 进一步确认每条改动的语义边界：

- 关于 `.bak` 自动审阅：应**默认保守**（不确定就保留 .bak + 入 TODO）。自动删除仅在"章节标题完整短语在目标文件中直接出现"的高置信度命中时发生。序号类/通用类标题（"## 一、"、"## 色彩"）直接不自动删。
- 关于 DRIFT_REPORT 引用修正：不回头补 Phase 5.3 §旧 UI 子文档章节，而是**明确划清边界** —— DRIFT_REPORT 只承载代码漂移，文档漂移独立用 `[UI Bootstrap]` 标签。
- 关于幂等性：不用"一次性 vs 可重复跑"这种二元分支描述。直接说"幂等，Phase 0.3 保证"，要强制重来就删 EXTERNAL_REFS.md —— 单一机制比两套分支容易理解。

## 为什么这么改

### 改动 A：Phase 0.2 同时检 HTML + styles.css，删 Phase 2 结构检查

- Phase 0 是"进 skill 前的守门员"，应该把所有结构前置条件在这一步拦截
- Phase 2 不应该留"理论上不会到达的分支"作为文档注释 —— 读者（下代 AI）会混淆真实流程
- 成本：删 6 行冗余 + 在 Phase 0.2 错误消息里明确列"缺 HTML" / "缺 styles.css"两种情况

### 改动 B：新增 Phase 4.2.1 `.bak` 自动审阅

**为什么是高置信度 + 保守默认**：

| 策略 | 优点 | 缺点 |
|------|------|------|
| **激进（关键词任一命中即删）** | 减少手动清理负担 | 容易误判（章节名很通用时假阳性严重） → 哲学段落被静默丢失 |
| **保守（完整短语命中才删）** ✅ | 不会丢失哲学内容 | 部分已沉淀的章节会进 TODO（下代 AI 会做 noop 合并） |

选保守。AI-Only 下丢失哲学内容是不可逆伤害（哲学一旦丢了，下代 AI 不知道有这段，也不会去找）；TODO noop 是可恢复成本（合并时一眼看出"内容一致，直接删 TODO"）。

**为什么放 Phase 4.2.1**（紧跟 4.2 备份之后）：

- 4.2 刚生成 .bak，趁热审阅最合理
- 4.2.2 "审计 docs/ui/ 旧子文档" 扫的是 `docs/ui/*.md`（不含 .bak），两件事独立
- 逻辑顺序：备份 (4.2) → 审阅刚备份的 (4.2.1) → 扫 docs/ui/ 其他 (4.2.2)

### 改动 C：Phase 4.2.1 → 4.2.2 的引用修正

- DRIFT_REPORT 的职责是"代码 vs 设计 export 的视觉 token 对账"，**不包含文档漂移**
- 文档漂移的定位锚：每个 TODO 条目自身的路径引用（如 `docs/ui/theme.md`）已足够，不需要聚合章节
- 删除虚构引用 + 明确说明"[UI Bootstrap] 文档漂移 / [UI Drift] 代码漂移"的标签分工

### 改动 D：删 "一次性 vs 可重复跑"，替换为"幂等性"

**为什么单一机制好于两套分支**：

- 两套分支（Phase 0.3 去重 + 末尾 "是否 re-onboard" 提示）让 AI 无法在 Phase 0 时就决定走向 —— 要等读到末尾才发现还有另一条路径
- 幂等 + "删 EXTERNAL_REFS 即重来" 是单一机制：Phase 0.3 保证幂等，重来靠删文件触发
- 不需要交互式确认分支（AI-Only 项目对话轮次越少越好）

## 为什么不选其他方案

**为什么不做 Common Drift Patterns 沉淀机制**（🟡 清单第 5 条）：

- 这是**跨会话的知识沉淀机制**，需要：
  - 新目录 `~/.claude/docs/decisions/ui-bootstrap-patterns/`
  - 每个 pattern 一个 decision file（template 需要设计）
  - Phase 5.4 在产品判断分流前 grep 匹配逻辑
- 本轮先把 🔴 稳住，pattern 库先靠 decision record（如 `2026-04-24-02` 本身就是 AI accent 决策记录，可以手动引用）。等 2-3 个项目都跑完 bootstrap 出现明显重复模式再正式做目录。

**为什么不加"验证凭证"命令**（🟡 清单第 7 条）：

- Bootstrap 产出是文档 + TODO 条目，不是代码行为。所有产出都能用 Phase 6 完成提示里的列表直接验证
- 强加命令会让 skill 尾部臃肿，真正需要的验证凭证应在"测试 / 代码变更"这类产出类型上，不是文档 skill
- 留给下次真实需要时再加（触发条件：有用户抱怨 skill 说"完成"实际没做事）

**为什么不改 `[UI Bootstrap]` 标签名**（如改为 `[UI Docs]`）：

- Founder 在 2026-04-24 rss-reader TODO 落地时已经把两种标签并行使用 `[UI Drift]` + `[UI Bootstrap]`
- 要改必须全局 retag，对 memory / TODO 格式校验有连锁成本
- `[UI Bootstrap]` 的语义"bootstrap 后需要做的文档收尾"也能成立

## 验证凭证

```
$ wc -l ~/.claude/commands/ui-bootstrap.md
     391 /Users/zhanglingxiao/.claude/commands/ui-bootstrap.md
$ grep -nE '^### Phase|^#### 4\.[0-9]+' ~/.claude/commands/ui-bootstrap.md
31:### Phase 0: 准备 inbox（仅首次）
46:### Phase 1: 采集绑定信息（对话式,2 问）
59:### Phase 2: 读 Claude Design Export
71:### Phase 3: 逆向抽取设计系统
99:### Phase 4: 生成 / 更新源文档
101:#### 4.1 写 `docs/design/EXTERNAL_REFS.md`
126:#### 4.2 写 / 重写 `docs/ui/UI_SHOWCASE.md`(三段式)
182:#### 4.2.1 `.bak` 自动审阅（AI-Only 必须机械执行，不能留给下次人审）
211:#### 4.2.2 审计 docs/ui/ 下的旧子文档（新 UI_SHOWCASE 的关系）
230:#### 4.3 归档当前 export 为首份 bundle
244:#### 4.4 生成 `docs/design/DESIGN_BRIEF.md`(初始 Δ Brief)
264:### Phase 5: 代码漂移检测 + 自动分类
346:### Phase 6: 完成提示
$ grep -n "幂等性\|一次性 vs 可重复跑" ~/.claude/commands/ui-bootstrap.md
380:## 幂等性
```

编号顺序正确（4.2.1 先于 4.2.2），"一次性 vs 可重复跑"已被"幂等性"替换。

## 关联决策

- 前置：`2026-04-24-03-ui-bootstrap-automation.md`（inbox + 去重 + 漂移自动分类三大升级）
- 平行：`2026-04-24-01-ui-design-router-and-feat-done-to-skills.md`（闭环中其他 skill 的升级）
- 引用：`flametree_rss_reader/to-discuss.md` §[Design System] AI accent 游离 Hex 处置（rss-reader 实战中发现的 Phase 5.4 产品判断分流真实案例）
