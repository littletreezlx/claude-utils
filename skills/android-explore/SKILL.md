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
- **只记录，不修复** — 发现问题记到报告，不在探索中改代码
- **主观感受和客观 bug 都记** — 体验报告 + 技术问题清单
- **每步看截图** — 操作后截图观察 UI 反馈

---

## 前置条件

1. Debug Server 运行中（App 已启动，端口已转发）
2. `android-qa-stories` 已在本会话通过

如果 qa-stories 未执行，**先调用它**。在故障基线上探索只会产生噪音。

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

**每轮 = 一次完整使用循环**（打开 → 完成核心任务 → 浏览 → 退出）。建议 1-3 轮，每轮换人设。

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

### Step 3: 输出报告

```markdown
## 探索报告

### 环境
- 项目: xxx | 包名: com.xxx | 端口: xxxx | 时间: xxx
- 设备: [adb devices 输出]
- 基线: qa-stories 全部通过
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

---

## 注意事项

1. **不过度探索** — 每个人设 1 轮使用循环，总共不超过 3 轮
2. **不穷举边界** — 那是 qa-stories 的事。这里靠自然使用发现问题
3. **截图是关键输入** — 每步操作后必须截图，UI 反馈是体验的核心
4. **保持人设一致** — 新手不会精确计算，效率达人不会慢慢浏览
5. **Logcat 辅助** — 遇到异常时 `adb logcat -d -t 30 *:E` 查看错误日志
