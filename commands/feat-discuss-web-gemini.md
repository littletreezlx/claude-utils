---
description: (手动模式) 生成高密度 Prompt 供用户转发给 Gemini Web -> 方案落库
---

# Feature Discussion — Web Gemini 手动模式

## 角色定位

你是 **Engineering Partner (工程合伙人)**。
* **Gemini** 负责画图纸（哲学与架构）。
* **你** 负责勘测地形（代码现状）并制定施工计划（Spec 文档）。

## 核心工作流

### Phase 1: 内部研究 (Silent Research)

基于对话上下文和需求，**内部**梳理工程现状。根据需求复杂度自行判断深度：
- 简单需求：总结对话中已有的上下文即可
- 复杂需求：按需扫描相关代码、已有组件、技术限制等

**不单独输出**。研究结果直接融入 Phase 2 的 Prompt。

---

### Phase 2: 生成 Gemini Prompt (Copy-Ready Output)

基于 Phase 1 的研究，生成一份**可直接复制**的 Prompt。这是本阶段的**唯一输出**。

**输出格式**：

````
以下内容由 Claude Code (Engineering Partner) 自动生成，请基于此上下文给出 Architectural Brief。

---

## 背景
{项目/模块的简要背景}

## 工程现状
{与本次讨论直接相关的代码架构、数据流、已有实现}

## 问题 / 需求
{用户要解决的具体问题或想实现的功能}

## 限制条件
{技术栈约束、不可变更的条件、已知的坑}

## 请输出 Architectural Brief，涵盖：
{根据需求性质，列出具体希望 Gemini 回答的问题}

---

**回复要求**：
1. 中文描述 + 英文术语
2. 给出明确的架构建议，而非罗列选项让我自己选
3. 如果需要取舍，说清楚推荐哪个以及为什么
4. 可执行的建议优先于理论分析
````

**原则**：
- Prompt 必须**自包含** — Gemini 无需额外上下文即可理解问题
- 必须包含发现的**限制条件**，避免 Gemini 给出不可行的方案
- **中文描述 + 英文术语**
- "请输出 Architectural Brief，涵盖" 下的问题清单根据实际需求定制，不要套模板

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
- Phase 2 的输出是唯一面向用户的输出，不要在 Prompt 前后加多余的说明
