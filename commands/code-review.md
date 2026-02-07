---
description: 代码审查与提测单生成 ultrathink
---

# 代码审查

> 自动化执行 Feature Branch 代码审查，生成技术评审报告和 QA 提测单。

---

## Step 0: 项目类型检测

自动检测项目类型（Android/Kotlin、Flutter/Dart、Node/TypeScript 等），应用对应的审查策略。

---

## Step 1: 获取变更

- 获取 `master...HEAD` 的变更统计和核心代码 diff
- 排除 lockfile、生成代码、资源文件等噪音
- **Token 熔断**：Diff 超过 1000 行时，优先审查核心业务逻辑，跳过样式和配置

---

## Step 2: 深度审查

### 通用审查维度

| 维度 | 检查点 |
|------|--------|
| **完整性** | 新增逻辑是否闭环？怀疑未使用时**必须**全局搜索确认 |
| **健壮性** | 空指针、数组越界、异常捕获 |
| **安全性** | SQL 注入、敏感信息硬编码 |
| **规范性** | 命名风格、注释质量 |

### Android/Kotlin 专项（检测到 Android 项目时强制执行）

| 维度 | 审查红线 |
|------|---------|
| 崩溃风险 | `!!` 非空断言、未捕获异常、`lateinit` 误用 |
| 内存泄漏 | ViewModel 持有 Activity 引用、未注销 Listener、静态 Context |
| 生命周期 | `lifecycleScope` 外收集 Flow、LiveData 倒灌 |
| 线程安全 | 主线程 IO、`GlobalScope` 滥用 |
| 架构规范 | View 层含业务逻辑、ViewModel 依赖 Context |

---

## Step 3: 问题分级

- **🔴 严重 (Blocker)**：功能缺失、逻辑错误、必现 Bug、数据安全
- **🟡 中等 (Warning)**：潜在风险、可读性差、规范问题、维护成本
- **🟢 轻微 (Optional)**：命名优化、代码风格偏好

---

## Step 4: 生成双文档

### 文档 1: 技术审查报告

**路径**: `docs/reviews/review-{branch}-{date}.md`

结构：变更概览 → 🔴 严重问题（含文件:行号、修复建议）→ 🟡 改进建议 → 🟢 最佳实践 → 总体评估（1-10 分 + 是否建议合并）

### 文档 2: QA 提测单

**路径**: `docs/reviews/test-submission-{branch}-{date}.md`

结构：变更模块表 → 具体变更内容 → 测试入口 → 风险提示 → 部署注意事项

---

## 审查红线

1. **严禁臆测**：看不懂标记为 "❓ 疑问" 而非 "❌ 错误"
2. **验证引用**：标记 "Dead Code" 前必须全局搜索确认
3. **保持礼貌**：评论针对代码而非人
