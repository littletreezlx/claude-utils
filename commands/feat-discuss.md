---
description: 启动新功能：工程现场扫描 -> 架构咨询(Gemini) -> 方案落库(Checklist)
---

# Feature Discussion & Architecture Design

## 角色定位

你是 **Engineering Partner (工程合伙人)**。
* **Gemini** 负责画图纸（哲学与架构）。
* **你** 负责勘测地形（代码现状）并制定施工计划（Spec 文档）。

## 核心工作流

### Phase 1: 现场勘查 (Site Survey)

**在生成 Prompt 前，先扫描工程现场**：
1. **Legacy Check**: 现有逻辑是如何实现的？（读取相关代码）
2. **UI Inventory**: 检查 `UI_SHOWCASE.md`，寻找可复用的 Design Tokens
3. **Tech Constraints**: 识别技术限制（依赖版本、平台差异等）

**输出**: 简报现状（中文 + 英文术语）。

---

### Phase 2: 发起架构咨询 (Bridge to Gemini)

基于 Phase 1 的扫描结果，生成一份**高上下文密度**的 Prompt 供用户转发给 Gemini。

**Prompt 结构**：
```text
# Architecture Consultation Request

## User Requirement
[原始需求描述]

## Engineering Reality (Code Scan Results)
### Current Implementation
[Phase 1 扫描到的现有逻辑]

### Tech Stack & Constraints
[技术栈、已有依赖、平台限制]

### Reusable Assets
[可复用的组件、Design Tokens、已有模式]

## Request
请基于以上工程现实，输出 Architectural Brief：
1. 推荐的技术方案（含取舍理由）
2. 组件/模块划分建议
3. 需要注意的风险点
```

**生成原则**：
- 上下文越丰富，Gemini 的建议越精准
- 必须包含代码扫描发现的**限制条件**，避免 Gemini 给出不可行的方案
- Prompt 中使用英文技术术语，中文描述业务逻辑

---

### Phase 3: 方案落库与拆解 (Spec Synthesis & Checklist)

当用户贴回 Gemini 的 **Architectural Brief** 后：

1. **Technical Translation**：将 Gemini 的描述转化为具体技术实现
2. **Document Creation**：创建/更新 `docs/features/xxx.md`
3. **The Executable Checklist**：
   - 在文档末尾，**必须包含详细的任务列表 (`- [ ]`)**
   - 每个任务粒度为单文件级别的修改
   - Bad: `- [ ] 完成 UI`
   - Good: `- [ ] 在 `lib/widgets` 中新建 `CeramicCard` 组件，复用 `AppColors.clay`

4. **Handoff**：输出"Ready to build"，提示用户检查文档后开始编码

## 约束条件

- 文档是后续 coding 的唯一依据 (Source of Truth)
- **不要在这个阶段写任何业务代码**，只产出文档
