# 2026-04-24-02: `/ui-bootstrap` 自动化改造（inbox + 去重 + 漂移自动分类）

## 遇到什么问题

Founder 在 `flametree_rss_reader` 上跑完一次 `/ui-bootstrap`，产出都对（6 份文档齐全，还发现了"反向闭环"异常），但流程层面有三个明显的保守派默认：

### 痛点 1：DRIFT_REPORT 识别出问题但不进 TODO

skill 里写着 `DRIFT_REPORT 是诊断,不是 TODO — 只输出事实,决策权在项目 session`。实际那次报告的 4 类：

- 🔴 A4 纯黑阴影违反 `shadow_tokens.dart` 已登记铁律 → **事实 bug**
- 🟢 LoginColors 5 处 Hex 与 token 完全一致 → **事实 refactor**
- 🟡 A3 Snackbar 用 Bootstrap 5 色码与 Warm Study 冲突 → **事实 bug**（违反已登记的色板）
- 🟡 A1 AI accent（`#E8A838` / `#95D5B2`）游离 → **产品判断**（反哺 or 清理）

前三条全部是可以直接落 TODO 的事实项，skill 却把它们和产品判断一起留给"下次 session 决策"。这违反全局 CLAUDE.md：

> 事实型 bug → TODO.md；观点/产品/设计判断 → 先借助 /think 获取外部视角，Claude Code 自己综合判断做最终决策，能拍板则转 TODO 或丢弃

### 痛点 2：Export 路径每次都现问，归档后脏工作区

当前流程：

1. Founder 自己从 Claude Design 下载 ZIP
2. 自己解压到某处（这次是 `rss-reader/`，项目根 untracked）
3. Phase 1 skill 问"你放哪了" → 回答 `rss-reader/`
4. skill 复制到 `docs/design/generated/{ts}/project/`
5. 源 `rss-reader/` 留在项目根，git 状态脏，Founder 手动 `rm -rf`

每次 re-adopt 都重来一遍，且没有任何去重——同样的 bundle 重复下载也会重复归档。

### 痛点 3：Phase 1 问 5 个问题里有 1 个永远填 unknown

Q2 "Onboarded commit" Claude Design 产品没暴露这个字段。100% 的场景下 Founder 只能填 `unknown`。问这条纯粹是噪音。

## 讨论过程

Founder 跑完 bootstrap 后指出：
1. 识别出的问题为什么没自动进 TODO，"我感觉不用我拍板"
2. 后续拉取 design 项目更新是否还放同一位置
3. 没有增量下载能力的话，能不能固定一个 inbox 目录，diff 后再归档

Claude 核对 skill 文件 + 全局 CLAUDE.md + memory（`reference_claude_design_loop_design.md`），确认：

- 归档结构（`docs/design/generated/{ts}-{slug}/project/`）本身是对的，历史要留着做 diff，不能覆盖
- skill 里的"诊断不是 TODO"约束和全局决策政策冲突，是设计保守
- Phase 1 确实可以瘦身：Q2 始终 unknown、Q3 可以固定 inbox、Q4 可以自动生成默认 slug

Founder 批准三条改动。

## 为什么这么改

### 改动 1：标准化 inbox 为 `<project>/.claude-design-inbox/`

**为什么选项目内 inbox 而不是全局目录（如 `~/Downloads/claude-design/`）**：

| 维度 | 项目内 `.claude-design-inbox/` | 全局 `~/Downloads/claude-design/` |
|------|---------------------------------|----------------------------------|
| 配置 | 加一行 `.gitignore` 即可 | 要维护"项目 → 子目录"注册表 |
| 预测性 | skill 知道去哪找 | 要先问 Founder 是哪个项目 |
| 隔离 | 每个项目独立，不会串 | 可能误把 A 项目的解压到 B |
| 清理 | 每个项目自己清 | 全局清理需要遍历所有项目 |

选项目内。

**何时添加 `.gitignore`**：skill 首次运行检测 `.claude-design-inbox/` 不存在 → 创建 + 往项目根 `.gitignore` 追加 `.claude-design-inbox/` 一行（已存在则跳过）。

### 改动 2：hash 对比去重 + 自动归档

skill 在 Phase 2 读 export 前先做一次：

1. 扫 inbox 下的 `{Name}.html + styles.css + *.jsx`（去掉 uploads/ 减小计算量）
2. 对所有归档下最新那份的 `project/` 做相同的哈希
3. 对比：
   - **完全相同**：跳过归档，只更新 `EXTERNAL_REFS.md` 里的"最后同步时间"，报告"内容无变化"后退出
   - **有变化**：继续 Phase 2-5，归档到 `{date}-{slug}-iter-{N}`（N 自增）或首次 bootstrap 用 `-bootstrap` 后缀
   - **无历史归档**：首次 bootstrap

归档完成后自动 `rm -rf .claude-design-inbox/*`（只清内容不删目录），保持 inbox 可复用。

### 改动 3：Phase 1 从 5 问降到 2 问

保留：
- Q1 Claude Design project URL
- Q2 Organization scope（`private` / `org-view` / `org-edit`）

删除：
- ~~Q3 Onboarded commit~~ → 永远填 `unknown`，对应字段加标红提示"下次 adopt 前 re-onboard 一次"
- ~~Q4 Export 本地路径~~ → 固定 `.claude-design-inbox/`，提示 Founder 把 ZIP 解压到这里
- ~~Q5 Slug~~ → 自动生成（取项目名 + PRODUCT_SOUL 关键词，如 `quiet-curator-v1`），除非 Founder 明确换一个

### 改动 4：Phase 5 尾部加漂移自动分类

读完 DRIFT_REPORT 后 skill 按以下规则分流：

| 情况 | 动作 |
|------|------|
| 违反已登记铁律（shadow tokens / color tokens / 阴影禁用纯黑等） | 直接写 TODO.md 条目，reference 指向 DRIFT_REPORT.md 章节 |
| 明确 refactor（代码 Hex 与 token 值一致但未引用） | 直接写 TODO.md 条目 |
| 产品判断（新增 accent 反哺 or 清理 / 设计方向分歧） | 调 `/think` 获取外部视角 → 能拍板转 TODO，拿不准进 `to-discuss.md` |
| 信息不足（不知道这是什么色） | 留在 DRIFT_REPORT 作为"待议"段落 |

**TODO 条目格式**（引用 DRIFT_REPORT 定位）：

```markdown
- [ ] [UI Drift] 修正 `settings_card_selector.dart:133` 纯黑阴影违反 shadow_tokens 铁律
      Ref: docs/design/DRIFT_REPORT.md §A4
```

## 为什么不选其他方案

**为什么不在 DRIFT_REPORT 里自己维护 checkbox**（而不是写进 TODO.md）：
- `/todo-doit` skill 只消费 `TODO.md`，不会扫 DRIFT_REPORT
- DRIFT_REPORT 是诊断快照，写进 TODO 之后它就可以被当作归档资料
- 分散在两个队列里，Founder 查看时会漏

**为什么不让 `/ui-bootstrap` 直接改代码修复 A4 级铁律违反**：
- skill 当前边界是"只读代码，只写文档"
- 代码修复需要测试运行闭环，超出 bootstrap 职责
- TODO 条目生成后，下一轮 `/todo-doit` 会把它当作常规修复任务走完整流程（含测试）

**为什么保留 `-bootstrap` 后缀做首版归档**（而不是用 `iter-0`）：
- "bootstrap" 明确表示这是首次接入的快照，不是正常迭代产出（README 里会写）
- 之后 `/ui-adopt` 产生的是 `{date}-iter-{N}` 或 `{date}-{topic}`
- 语义分离方便回溯
