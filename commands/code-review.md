---
description: 代码审查与提测单生成 ultrathink

---

# 代码审查

> 自动化执行 Feature Branch 代码审查，生成技术评审报告和 QA 提测单。

---

## Step 0: 项目类型检测

**自动检测项目类型**，应用对应的审查策略：

| 检测文件 | 项目类型 | 专项策略 |
|----------|----------|----------|
| `build.gradle(.kts)` + `*.kt` | Android/Kotlin | → 启用 Android 专项审查 |
| `pubspec.yaml` | Flutter/Dart | → 启用 Flutter 专项审查 |
| `package.json` + `*.ts` | Node/TypeScript | → 通用审查 |
| 其他 | 通用 | → 通用审查 |

---

## Step 1: 智能获取变更

### 通用过滤规则

```bash
# 1. 获取变更统计
git diff master...HEAD --stat

# 2. 获取核心代码变更 (排除通用噪音)
git diff master...HEAD -- . \
  ':(exclude)package-lock.json' \
  ':(exclude)yarn.lock' \
  ':(exclude)*.lock' \
  ':(exclude)*.svg' \
  ':(exclude)*.min.js' \
  ':(exclude)Podfile.lock'
```

### Android/Kotlin 专项过滤

```bash
# 仅关注 Kotlin、布局、构建脚本（排除生成代码）
git diff master...HEAD -- \
  "*.kt" "*.xml" "*.gradle" "*.gradle.kts" \
  ":(exclude)**/build/**" \
  ":(exclude)**/generated/**" \
  ":(exclude)**/databinding/**"
```

**Token 熔断策略**：Diff 超过 1000 行时，优先审查核心业务逻辑（*.kt, *.ts, *.py），跳过样式和配置文件。

---

## Step 2: 深度审查

### 通用审查维度

| 维度 | 检查点 | 验证手段 |
| --- | --- | --- |
| **完整性** | 新增逻辑是否闭环？ | 🕵️ 怀疑未使用时，**必须**用 `grep` 全局搜索确认 |
| **健壮性** | 空指针、数组越界、异常捕获 | 检查代码逻辑分支 |
| **安全性** | SQL注入、敏感信息硬编码 | 关键词扫描 |
| **规范性** | 命名风格、注释质量 | 静态分析 |

### 🤖 Android/Kotlin 专项审查（检测到 Android 项目时强制执行）

| 维度 | 审查红线 |
| --- | --- |
| **☠️ 崩溃风险** | `!!` 非空断言（除非有极强理由）、未捕获异常、`lateinit` 误用 |
| **💧 内存泄漏** | ViewModel/Object 持有 Activity/View 引用、未注销 Listener、静态 Context |
| **🔄 生命周期** | 在 `lifecycleScope`/`viewLifecycleOwner` 之外收集 Flow、LiveData 倒灌 |
| **⚡ 线程安全** | 主线程执行 IO/数据库操作、`GlobalScope` 滥用 |
| **🎨 资源规范** | XML 硬编码文本/颜色、尺寸未使用 dimen |
| **🏗️ 架构规范** | View 层包含业务逻辑、ViewModel 直接依赖 Context |

---

## Step 3: 问题分级

### 通用分级标准

#### 🔴 严重（Blocker - 阻塞合并）

符合**任一条件**即为严重：

- **功能缺失**：定义了但未使用，导致功能不完整
- **逻辑错误**：条件判断、数据处理、状态管理错误
- **必现 Bug**：每次执行都会触发
- **数据安全**：可能导致数据丢失/泄露

#### 🟡 中等（Warning - 建议修复）

- **潜在风险**：特定条件下可能出问题
- **可读性差**：魔法数字、命名不清、逻辑绕
- **规范问题**：代码格式、注释缺失
- **维护成本**：重复代码、过度耦合

#### 🟢 轻微（可选优化）

- 命名可以更好、可以更简洁、代码风格偏好

### 🤖 Android/Kotlin 专项分级示例

#### 🔴 严重（Android）

- **NPE 风险**：无保护的 `!!`，链式调用未判空
- **ANR 风险**：主线程读写文件/网络请求
- **内存泄漏**：Handler/Thread 内部类持有外部引用，Context 泄露
- **复用错误**：RecyclerView Adapter 复用逻辑错误

#### 🟡 中等（Android）

- **硬编码**：String/Color 没有提取到资源文件
- **性能**：`onDraw` 中创建对象、过度绘制风险
- **Kotlin 风格**：可用 `apply/also/let` 简化、可用扩展函数
- **废弃 API**：使用了 `@Deprecated` 的 Android API

---

## Step 4: 生成双文档

生成两份文档到 `docs/` 目录。

---

## 输出文档格式

### 📄 文档 1：技术审查报告

**路径**: `docs/reviews/review-{branch}-{date}.md`
**侧重**: 代码质量、Bug 风险

```markdown
# 代码审查报告

**分支**: xxx | **日期**: xxx | **审查人**: Claude Code

## 1. 变更概览
- 文件数/行数统计
- 主要功能变更点

## 2. 问题清单

### 🔴 严重问题 (Blocker)
> 导致崩溃、逻辑错误、数据丢失的问题

#### 2.x [问题标题]
**文件**: `文件路径:行号`
**问题**: 具体描述
**为什么严重**: 解释影响
**修复建议**: 具体方案或代码示例

### 🟡 改进建议 (Warning)
> 可读性、规范性、潜在风险

### 🟢 最佳实践 (Praise)
> 值得鼓励的写法

## 3. 总体评估
- 代码质量评分（1-10）
- 是否建议合并
- 合并前必须处理的清单
```

### 📄 文档 2：QA 提测单

**路径**: `docs/reviews/test-submission-{branch}-{date}.md`
**侧重**: 功能影响、测试范围

```markdown
# 提测单

**分支**: xxx | **日期**: xxx

## 1. 变更模块

| 模块 | 类型 | 影响描述 |
|------|------|----------|
| 订单 | 修复 | 修复了金额计算精度的 bug |
| 用户 | 新增 | 增加了微信登录入口 |

## 2. 具体变更内容

### [模块名]
- 新增：xxx
- 修改：xxx
- 修复：xxx

## 3. 测试入口

说明如何进入测试该功能

## 4. 风险提示

- 需要特别关注的场景
- 已知限制

## 5. 部署注意事项 (Ops) ⚠️

- [ ] SQL 变更: `migrations/001_xxx.sql`
- [ ] 环境变量: 新增 `WECHAT_APP_ID`
- [ ] 第三方服务: 需要确认 xxx 服务可用
```

---

## 审查红线

1. **严禁臆测**：如果看不懂代码意图，标记为 "❓ 疑问" 而不是 "❌ 错误"。
2. **验证引用**：标记 "Dead Code" 前必须全局搜索确认。
3. **保持礼貌**：评论针对代码而非人。
