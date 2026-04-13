---
description: 项目文档质量审查（Map-Reduce：全局诊断 + 机械执行）ultrathink
---

# 项目文档质量审查

## 目标

审查 `docs/` 下所有文档**本身的写作质量**，判断每份文档是否履行了它在文档体系中的职责。

**与 `/doc-update-context` 的区别**：

| 命令 | 参照物 | 回答的问题 |
|------|--------|----------|
| `/doc-update-context` | 文档 vs 代码 | 写的内容和代码一致吗？ |
| `/doc-quality-review`（本命令） | 文档 vs 文档标准 | 文档体系整体健康吗？ |

**本命令基本不读代码**。参照物是 `~/.claude/guides/doc-structure.md` 定义的文档职责和边界。

> **前置建议**：先跑 `/doc-update-context` 保证"说的是真的"，再跑本命令保证"说得好"。

---

## 架构原则：Map-Reduce（集中诊断 + 分散治疗）

**核心信念**：文档质量问题里最值钱的那类是**关系型约束**——跨文档冗余、边界越界、全局结构失衡。这类问题无法从单文档视角发现。

因此本命令拒绝"per-doc 独立审查"模式，采用：

1. **Phase 2 诊断节点**：一次性读入 `doc-structure.md` + 所有待审文档骨架 → 产出全局 `review-action-plan.md`
2. **Phase 3 执行节点**：每个文档一个 TASK，**只执行 action plan 中属于自己的处方**，禁止延伸判断

---

## 审查维度（三条硬指标，无软指标）

删除人类中心的"文笔优雅/结构清晰/表达精确"等软概念，代之以 AI 消费视角的可验证指标：

| 维度 | 操作定义 |
|------|---------|
| **唯一性 (Uniqueness)** | 任何一条信息是否只在一个文档中定义？违反例：BEHAVIOR 和 features/X 都描述同一个状态机 |
| **可预测性 (Predictability)** | 按 `doc-structure.md` 的职责定义，AI 闭着眼睛能否猜到某类信息在哪个文档里？违反例：产品愿景一半在 SOUL 一半在 BEHAVIOR |
| **信噪比 (Signal-to-Noise)** | 文档中是否存在不属于本文档职责的长篇内容，稀释核心信息？违反例：ARCHITECTURE 里写了 5 段用户流程叙事 |

**不再检查**：章节是否漂亮、段落是否流畅、表格是否好看。这些是人类读者关心的,AI 不关心。

---

## 状态记忆：JSON state 文件

放弃"文档末尾埋 HTML 注释"的方案（在 AI 高频改写的项目里会被意外清洗，且无法捕捉"审查标准升级"）。

改用集中式 state 文件：`.claude/quality-review-state.json`

```json
{
  "standard_hash": "<doc-structure.md 的 sha256>",
  "docs": {
    "docs/PRODUCT_BEHAVIOR.md": {
      "doc_hash": "<文档当前 sha256>",
      "reviewed_at": "2026-04-13",
      "reviewed_commit": "abc123"
    }
  }
}
```

**重审触发规则**（满足任一即需重审）：
- 文档 `doc_hash` 变化 → 内容改了
- 全局 `standard_hash` 变化 → 审查标准升级，所有文档需重审
- 文档未出现在 state 中 → 新增文档

**豁免**：`--force` 参数全量重审。state 文件丢失只会触发一次全量，无破坏性。

---

## 执行流程

### Phase 1: 扫描与筛选

1. 扫描 `docs/` 完整目录树，收集所有 `.md` 文件
2. 计算每个文档的 `doc_hash` 和 `doc-structure.md` 的 `standard_hash`
3. 对比 `.claude/quality-review-state.json`，按重审触发规则筛选出待审清单
4. 输出「待审清单」：待审文档数、跳过数（近期已审且标准未变）

### Phase 2: 全局诊断节点（Map 阶段）

**这是本命令的核心节点。** 单个 TASK，横向视角。

**输入**：
- `~/.claude/guides/doc-structure.md` 全文
- 所有待审文档的完整内容（本命令不读代码，Context 额度充足）

**产出**：`./review-action-plan.md`，结构化的处方清单：

```markdown
# 文档质量修复清单

## 按文档组织的处方

### docs/PRODUCT_BEHAVIOR.md
- [越界] 第 X-Y 行「随机选择算法实现」属于 features/random.md 职责，删除并在 features/random.md 中确认有对应内容
- [冗余] 第 A-B 行与 docs/ARCHITECTURE.md 第 C-D 行重复描述路由表，保留 ARCHITECTURE 版本，此处改为引用
- [缺失] 按 doc-structure.md，本文档应包含「全局状态策略」章节，当前缺失

### docs/ARCHITECTURE.md
- [信噪比] 第 M-N 行用户流程叙事稀释技术架构主题，迁移到 PRODUCT_BEHAVIOR.md

### docs/features/random.md
- （无修改，职责清晰）

## 全局观察
- 整体健康度评分：🟢/🟡/🔴
- 系统性问题（如存在）：例如「发现 3 处 BEHAVIOR→features 的越界，可能说明 BEHAVIOR 职责定义过宽」
```

**TASK 完成标志**：`review-action-plan.md` 生成，包含每份待审文档的处方（即使是"无修改"）。

### Phase 3: 执行节点（Reduce 阶段）

生成 DAG 任务文件 `./task-doc-quality-review`，每个有处方的文档一个 TASK：

```markdown
## STAGE ## name="执行 action plan" mode="serial"

## TASK ##
执行 docs/PRODUCT_BEHAVIOR.md 的修复处方

**🎯 目标**：按 review-action-plan.md 中针对本文档的处方机械执行，禁止延伸判断

**📁 核心文件**：
- `docs/PRODUCT_BEHAVIOR.md` - [修改]
- `./review-action-plan.md` - [只读]

**🔨 执行步骤**：
1. 读取 action plan 中 `### docs/PRODUCT_BEHAVIOR.md` 段落
2. 对每条处方执行对应操作（删除/迁移/引用化/补充缺失章节）
3. **禁止超出处方的额外改动**——发现新问题只记录到 TODO.md，不在本 TASK 中处理
4. 更新 `.claude/quality-review-state.json` 中本文档的 doc_hash / reviewed_at / reviewed_commit

**✅ 完成标志**：
- [ ] 处方条目全部执行或标注为"需用户决策"
- [ ] state 文件已更新

验证: jq '.docs["docs/PRODUCT_BEHAVIOR.md"].reviewed_commit' .claude/quality-review-state.json

---

## STAGE ## name="review" mode="serial"

## TASK ##
全局收尾
- 更新 state 文件的 standard_hash
- 输出本轮修改统计（按文档/按处方类型）
- 检查是否有跨文档迁移导致的新冲突
```

执行方式：

```bash
batchcc task-doc-quality-review
```

---

## 关键约束

1. **Phase 2 必须先于 Phase 3**：不允许跳过诊断直接逐文档审查
2. **Phase 3 TASK 只执行处方**：禁止 AI 在单文档 TASK 中"顺手优化"——新问题一律进 TODO
3. **跨文档迁移在处方中成对出现**：处方 A 删除的内容,必须在处方 B 中对应补充，避免信息丢失
4. **本命令不读源码**：发现疑似代码不一致时只记录到 TODO，由 `/doc-update-context` 处理
5. **state 文件是单一事实源**：不再用 HTML 注释、git log、文档 frontmatter 等其他信号

---

## 质量底线

- 不生成"一切 OK"的走过场报告，也不为凑数制造伪问题
- action plan 中每条处方必须**可机械执行**（指定行号、操作类型、目标位置）
- 发现系统性问题（如 doc-structure.md 本身职责定义有缺陷）→ 写入 TODO.md 供下次讨论，本命令不尝试修订标准
