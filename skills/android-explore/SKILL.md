---
name: android-explore
description: >
  This skill should be used when AI should autonomously explore a running
  native Android app as a user, discovering bugs and UX issues through
  role-play. AI picks a user persona, uses the app freely via embedded
  Debug Server, and reports experience + technical issues. Use when the
  user says "探索应用", "自由探索", "用一下", "explore", "find bugs",
  or after qa-stories passed and deeper exploration is needed. Requires
  Debug Server embedded in the app.
version: 1.0.0
---

# Android Explore — 角色扮演式自主探索

AI 扮演用户自由使用应用，通过第一人称体验发现 bug 和设计问题。不是机械测试，而是真正在"用"。

## 核心原则

- **我是用户，不是测试工程师** — 用用户思维做决策，不穷举边界
- **不做故事验证** — 那是 qa-stories 的职责。explore 假定基线 OK，专注第一人称体验
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码
- **主观感受和客观 bug 都记** — 体验报告 + 技术问题清单
- **每步看截图** — 操作后截图观察 UI 反馈

---

## 前置条件

1. Debug Server 运行中（App 已启动，端口已转发）
2. 基线数据就绪（有可用业务数据供探索）

**基线不足时，只做最小 seed**（创建 1-2 组数据就开始），不要跑完整 stories。想验证 stories 的用户应显式调用 `/android-qa-stories`。

---

## 执行流程

### Step 1: 建立用户认知

读取项目文档，理解"我是谁、我为什么用这个应用"：

```
读 docs/PRODUCT_SOUL.md    → 产品愿景、情感目标
读 docs/PRODUCT_BEHAVIOR.md → 我能做什么、系统规则
读 /providers              → 我能执行哪些操作
```

**选择本轮用户人设**（从预设池选一个，或根据项目特点自拟）：

| 人设 | 行为倾向 | 自然覆盖的系统 |
|------|---------|--------------|
| 🐣 新手小白 | 不看引导，随手点，不理解专业术语 | 引导缺失、容错性、术语可达性 |
| ⚡ 效率达人 | 最快完成目标，跳过一切非必要步骤 | 流程流畅度、快捷操作、冗余步骤 |
| 🐒 混乱操作者 | 逆序调用、密集请求、操作中途切目标 | 状态一致性、竞态条件、错误恢复 |
| 🔄 回归用户 | 之前用过，隔了很久回来，期望数据还在 | 数据持久化、状态恢复、迁移兼容 |
| 🧹 洁癖用户 | 频繁整理、删除、归类，追求"干净" | 批量操作、删除级联、空状态 |

### Step 2: 自由使用

**每轮 = 一次完整使用循环**（打开 → 完成核心任务 → 浏览 → 退出）。建议 1-2 轮，每轮换人设。轮数不是目标，发现高质量问题才是。

#### 使用规则

1. **第一人称内心独白**：每步操作前，用用户视角写一句决策理由：
   > "刚打开 App，看到一堆列表但不知道从哪开始…先点第一个试试"

2. **每步操作后截图**：
   ```bash
   adb exec-out screencap -p > /tmp/android_screen.png
   ```
   然后用 Read 查看截图，观察 UI 反馈

3. **做符合人设的决策**：
   - 新手会乱点、不看说明
   - 效率达人会直奔目标、忽略装饰性内容
   - 洁癖用户会先整理再使用

4. **破坏性操作放到每轮末尾**：delete/logout/clear 等不可逆操作，确认只读探索完成后再执行，避免早期破坏导致后续全部误报

5. **遇到异常时**：
   - 技术异常（curl 报错/状态不一致）→ 记录到技术问题清单，继续用
   - 体验困惑（不知道该干嘛/UI 看不懂）→ 记录到体验报告，继续用
   - Server 完全无响应 → 停止，输出已收集的报告

6. **人设受阻时**：某条路径无法通过 debug server 验证（如纯客户端导航），记录为"debug 盲区"，换角度继续，不要硬卡

### Step 3: 输出报告

**同时做两件事**：

1. **写入本地文件**：`_scratch/explore-YYYY-MM-DD.md`（项目根目录下）
   - 目录不存在则创建
   - 同日多次追加到同一文件（新增 `## 第 N 次探索` 节）
   - 文件头部加 `# Purpose:` 和 `# Created:` 标注

2. **打印到对话**：便于用户直接阅读

报告格式：

```markdown
## 探索报告

### 环境
- 项目: xxx | 包名: com.xxx | 端口: xxxx | 时间: xxx
- 设备: [adb devices 输出]
- 基线: [qa-stories 已通过 / 仅做最小 seed / 用户提供数据]
- 本轮人设: 🐣 新手小白

### 🎮 用户体验

#### 第一轮: [人设名]
> [2-3 段第一人称体验描述]
> "打开应用，首页有三个 Tab 但图标含义不明确…"
> "想找设置页，翻了半天找不到入口，最后发现在头像里…"

**体感问题**:
1. [描述] — 感受：[困惑/沮丧/无聊/...]
2. ...

#### 第二轮: [人设名]
> ...

### 🐛 技术问题清单
| # | 描述 | 复现 curl | 实际返回 | 严重程度 |
|---|------|----------|---------|---------|
| 1 | xxx | `curl ...` | `{...}` | 高/中/低 |

### 💡 设计建议（可选）
- [建议] — 基于 [哪个人设的体验]

### 建议补充的 User Stories
- [如果发现了重要但未被故事覆盖的路径]
```

### Step 4: 分流归档（严禁混流）

按性质分两路：**事实 → 行动队列，观点 → 决策队列**

#### 4a. 事实型 bug → TODO.md
客观可验证的技术问题 → 调用 `todo-write` 写入 `TODO.md`，带 `_scratch/explore-YYYY-MM-DD.md § 章节` 引用。

#### 4b. 观点/判断型 → to-discuss.md
体验优化、产品方向、stories 补齐等**需要人工判断**的事项 → 追加到项目根 `to-discuss.md`，严格模板：

```markdown
## [UX|Product|Arch|Workflow] 简短标题 (Ref: _scratch/explore-YYYY-MM-DD.md § 章节)
- **事实前提**: [基于什么客观现象，禁止加主观修饰]
- **AI 观点**: [我认为应该...]
- **反面检验**: [这个建议可能错在哪 / 维持现状的理由]
- **决策选项**:
  - [ ] Approve → 转 TODO.md
  - [ ] Discuss → /think 或 /feat-discuss-local-gemini
  - [ ] Reject → 直接删
```

**绝对禁止**：观点塞进 TODO.md / 跳过反面检验 / 两文件之间设指针

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮使用循环，总共不超过 2 轮
2. **不穷举边界、不跑故事** — 那是 qa-stories 的事。explore 只靠自然使用发现问题
3. **截图是关键输入** — 每步操作后必须截图，UI 反馈是体验的核心
4. **保持人设一致** — 新手不会精确计算，效率达人不会慢慢浏览
5. **Logcat 辅助** — 遇到异常时 `adb logcat -d -t 30 *:E` 查看错误日志
6. **报告落盘** — 完整报告写入 `_scratch/explore-YYYY-MM-DD.md`；bug → `TODO.md`；观点建议 → `to-discuss.md`
