---
name: ai-explore
description: >
  This skill should be used when AI should autonomously explore a running
  Flutter app beyond scripted user stories, using heuristic perspectives to
  discover unknown bugs and UX issues. A true AI-autonomous loop: explores
  freely with structured heuristics, finds and fixes issues, optionally
  reviews product experience. Use when the user says "explore the app",
  "深度测试", "探索一下", "find bugs", "QA explore", or after ai-qa-stories
  has passed and deeper verification is needed. Requires Debug State Server
  running. Automatically runs ai-qa-stories first as baseline.
version: 0.1.0
---

# AI Explore — 启发式自主探索

## 目的

在 user stories 全部通过的基础上，AI 带着特定"破坏视角"自由探索 App，发现剧本之外的问题。这是 AI 自主测试的发现层——不验证已知，而是发现未知。

## 前置条件

1. Debug State Server 正在运行
2. `ai-qa-stories` 已通过（如未执行，本 skill 自动先调用）

## 执行流程

### Step 0: 确认基线

检查 `ai-qa-stories` 是否已在本会话通过。如果没有，先执行它。所有故事必须通过后才进入探索——在错误基础上探索毫无意义。

### Step 1: 建立认知地图

```bash
curl -s localhost:$PORT/providers  # 获取完整端点清单
```

读 PRODUCT_BEHAVIOR.md + PRODUCT_SOUL.md（如有），理解：
- 核心业务是什么
- 用户画像是谁
- 系统有哪些状态规则

### Step 2: 启发式探索（按视角逐个执行）

#### 视角 1: 跨端点一致性
对比语义相关的数据源，寻找矛盾：
- `/data/A` 的统计数据 vs `/data/B` 的明细数据
- `/state/X` 的 UI 状态 vs `/data/X` 的数据库真相
- 关联实体之间的引用完整性（如 option.groupId 是否指向存在的 group）

#### 视角 2: 边界突变
找到状态树中可写的地方，注入边界值：
- 空字符串、超长字符串（100+ 字符）、特殊字符（emoji、换行）
- 不存在的 ID、负数、零
- 快速连续执行同一操作（3 次以上）

#### 视角 3: 非快乐路径
基于 user stories 的步骤，在中间注入意外：
- 执行删除后立即执行依赖该数据的操作
- 在"选择"操作时传入刚被删除的 ID
- 清空所有数据后执行核心功能

#### 视角 4: 状态持久化
- 修改设置 → 验证即时生效 → 检查重启后是否保持
- 创建数据 → 验证持久化 → 删除 → 验证清理干净

### Step 3: 产品体验审查（可选，用户指定"深度"时执行）

截图（`/screen` skill）+ 视觉分析：

| 审查维度 | 关注点 |
|---------|--------|
| 空状态 | 无数据时界面是否友好？有引导吗？ |
| 数据丰富态 | 大量数据时布局是否溢出？ |
| 操作反馈 | 操作后有 loading/成功/失败提示吗？ |
| 一致性 | 同类操作的交互模式是否统一？ |

如项目启用了 UI 文档系统，可调用 `/ui-vision-check` 做更深层审查。

### Step 4: 处理发现

- **代码 bug**：直接修复 → 重启 → 验证修复 → 记录
- **设计问题**：记录到报告，不自行"优化"
- **故事缺失**：发现了重要路径但 user-stories 没覆盖 → 建议补充

### Step 5: 输出报告

```markdown
## 探索报告

### 环境
- 项目: xxx | 端口: xxxx | 时间: xxx
- 基线: ai-qa-stories 全部通过

### 发现的问题
1. [Bug/已修复] 描述 — file:line — 修复方式
2. [Bug/待修复] 描述 — 复现步骤
3. [设计] 描述 — 建议

### 探索覆盖
- 一致性检查: 对比了 N 对端点
- 边界测试: 测试了 N 个边界场景
- 非快乐路径: 注入了 N 个意外

### 建议补充的 User Stories
- {如果发现了重要但未被故事覆盖的路径}
```

## Gotchas / 踩坑点

1. **Phase A 未过不探索** — 在错误基础上自由探索只会产生噪音
2. **探索后清理状态** — 边界测试会留下脏数据，探索完执行 `seed-test-data.sh clean` + `seed-test-data.sh`
3. **区分 bug 和 design** — 数据不一致是 bug；空状态没引导是 design。前者修，后者报告
4. **不要过度探索** — 每个视角 5-10 分钟，总共不超过 30 分钟。发现问题就修，不要穷举
5. **截图需要 App 在前台** — 探索前确保模拟器可见
