---
name: ui-doctor
description: >
  This skill should be used to check UI documentation health, detect stale specs,
  and find pages missing spec coverage. Use PROACTIVELY when starting UI work,
  after a batch of UI changes, or when the user says "check UI docs", "UI 健康",
  "spec 状态". Also use when another workflow (like health-check or consistency-check)
  needs UI documentation status. Lightweight — no LLM reasoning, only file scanning.
version: 1.0.0
---

# UI Doctor — 文档健康探针

## 角色定位
你是一个轻量级诊断工具，类似 `flutter doctor`。只做文件扫描和时间对比，**不做深度内容分析**，保持快速。

## 执行流程

### Step 1: 扫描页面文件
使用 Glob 扫描项目中的页面文件：
- `lib/**/pages/*.dart` 或 `lib/**/pages/**/*.dart`
- 提取页面文件名列表

### Step 2: 扫描 Spec 文件
扫描 `docs/ui/specs/*.md`，提取已有 Spec 列表。

### Step 3: 交叉对比
对每个页面文件：
1. **覆盖率检查**：是否有对应的 `docs/ui/specs/{page_name}_spec.md`？
2. **腐烂检测**：通过 `git log -1 --format="%ci" -- <file>` 对比代码文件和 Spec 文件的最后修改时间。如果代码比 Spec 新超过 7 天，标记为"潜在腐烂"。

### Step 4: 输出诊断报告

```markdown
## UI Doctor 诊断报告

### 覆盖率: X/Y 页面有 Spec (XX%)

### 缺失 Spec (需要跑 /ui-spec)
- ❌ `xxx_page.dart` — 无对应 Spec

### 潜在腐烂 (代码比 Spec 新)
- ⚠️ `yyy_page.dart` (代码: 3-08, Spec: 2-20) — 相差 16 天

### 健康 Spec
- ✅ `zzz_page.dart` (代码: 3-06, Spec: 3-06)
```

## 约束
- **不读取文件内容**，只做文件名匹配和 git 时间对比
- **不修改任何文件**，纯诊断
- 执行时间应在 5 秒以内
