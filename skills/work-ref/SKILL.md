---
name: work-ref
description: >
  Competitive analysis workflow for Android POS project. Launches 3 parallel subagents
  to explore decompiled source code across Qmai/Keruyun/Meituan, writes per-project
  analysis docs, then consolidates a cross-project comparison document.
  Trigger when: user says "分析 [功能] 三家怎么实现的", "对比 [功能]", "竞品分析 [功能]",
  "三家的 [功能]", "work-ref [功能]", or similar requests to compare how competitors
  implement a feature.
version: 0.1.0
---

# 竞品功能对比工作流 (work-ref)

## 目的

在 Android POS 竞品分析项目中，高效分析三家竞品（企迈 Qmai、客如云 Keruyun、美团 Meituan）对某功能的实现方式，产出结构化对比文档。

## 适用项目

仅限 `pos/android` 竞品分析项目（含三家反编译源码）。

---

## 执行流程

### Step 0: 解析用户意图

从用户请求中提取：
- **功能名称**（中文，如"会员卡系统"）
- **功能英文标识**（用于文件命名，如 `membership`）
- **搜索关键词**（中文 UI 文本、API 路径、类名等线索）

如果用户没有给出足够线索，主动询问：
- "这个功能在用户界面上叫什么？"
- "你知道相关的 API 路径或页面名称吗？"

### Step 1: 检索已有知识

```
1. 检查 docs/ 下是否已有相关对比文档
2. 检查各项目 docs/ 是否有相关分析
3. 如果 Qmai 有 FEATURE_CODE_MAP，查找相关条目作为线索
```

### Step 2: 启动 3 个并行 Explore Subagent

使用 Agent 工具，**在同一条消息中**发出 3 个并行调用。

每个 subagent 的 prompt 使用以下模板（替换 `{变量}`）：

```
你正在分析 Android POS 竞品的反编译源码。

## 任务
分析 {项目名}（{中文名}）中「{功能名称}」的实现方式。

## 项目信息
- 项目路径: {项目根目录}/src/
- 业务包名: {业务包名前缀}
- 资源目录: {项目根目录}/src/app/src/main/res/
- AndroidManifest: {项目根目录}/src/app/src/main/AndroidManifest.xml
{如果有已知线索，列出}

## 搜索协议（严格按顺序执行，每步无果则降级）

### 第一优先：UI/字符串锚点
1. Grep `res/values/strings.xml` 和 `res/values-zh*/strings.xml` 搜索中文关键词
2. 找到 string_name 后，Grep 布局 XML 和 Java 代码中对该资源的引用
3. 也搜索硬编码的中文字符串（直接 Grep Java/Kotlin 文件）

### 第二优先：网络/数据锚点
1. Grep API endpoint 路径字符串（如 "/api/", "/v1/", 相关业务路径）
2. 搜索 @SerializedName、JSON key 等数据契约
3. 搜索 Retrofit/OkHttp 相关的接口定义

### 第三优先：组件锚点
1. 查 AndroidManifest.xml 找相关 Activity/Service/BroadcastReceiver
2. 跟进这些组件的反编译类

### 第四优先：包名/类名正则
1. 在业务包名下 Grep 功能相关关键词
2. 仅在前三步不足时使用

## 搜索边界（铁律）

**必须排除的目录**（第三方库，Grep 时用 glob 过滤）：
- `androidx/`, `kotlin/`, `kotlinx/`
- `com/google/`, `com/alibaba/`, `com/alipay/` (除非功能本身就是支付宝相关)
- `com/tencent/`, `okhttp3/`, `retrofit2/`
- `com/squareup/`, `io/reactivex/`, `com/jakewharton/`
- `org/apache/`, `com/bumptech/`, `com/airbnb/`
- `coil/`, `rxhttp/`, `okio/`

**搜索深度熔断**：
- 跟踪调用链不超过 3 层
- 进入混淆代码区（类名如 a.java, b.java）时，记录发现但不深入穷举
- 未找到时大方承认，不要编造

## 输出格式

请按以下结构输出你的发现（纯文本，我会整理成文档）：

### 1. 功能概述
- 这个功能在 {项目名} 中是否存在？
- 功能定位（面向谁、解决什么问题）

### 2. 核心技术栈
- 使用的关键技术/框架/SDK

### 3. 架构组件
列出关键类及其职责：
| 组件 | 路径（从 src/app/src/main/java/ 起） | 说明 |

### 4. 核心流程
- 数据流 / 调用链 / 状态机（能看出多少写多少）

### 5. 关键代码片段
- 引用关键方法签名或核心逻辑（不要大段复制，点到为止）

### 6. 特殊发现
- 独特的设计选择、有趣的实现细节、踩过的坑
```

**三家业务包名速查**：

| 项目 | 业务包名前缀 | 备注 |
|------|------------|------|
| Qmai | `com/qmai/android/` | 模块化：pos_module/, pos_export/ 等 |
| Keruyun | `com/keruyun/` | 阿里系：含 alipay/iot 相关 |
| Meituan | `com/sankuai/sjst/rms/` | 最大（8万文件），混淆严重 |

### Step 3: 整合结果，写入各项目文档

Subagent 返回后，为每个**有实质发现**的项目写入分析文档：

- `Qmai/docs/{功能英文}.md`
- `Keruyun/docs/{功能英文}.md`
- `Meituan/docs/{功能英文}.md`

**命名统一**：三家使用相同的文件名。

### Step 4: 生成对比文档

在 `docs/{功能中文}-对比.md` 写入横向对比文档，使用以下模板：

```markdown
# {功能中文名}对比分析

> 分析时间：{YYYY-MM-DD}

---

## 一、方案对比总览

| 维度 | Qmai (企迈) | Keruyun (客如云) | Meituan (美团) |
|------|-------------|-----------------|----------------|
| **方案名称** | | | |
| **功能定位** | | | |
| **核心技术栈** | | | |
| **核心差异点** | | | |

---

## 二、详细分析

### 2.1 Qmai (企迈)

#### 核心技术栈
#### 架构组件
| 组件 | 路径 | 说明 |
|------|------|------|
#### 核心流程
#### 特殊发现

### 2.2 Keruyun (客如云)
（同上结构）

### 2.3 Meituan (美团)
（同上结构）

---

## 三、本质差异总结

{一段话 + 对比表格，突出三家在这个功能上的根本差异}

---

## 四、相关文档

- 企迈详细分析: [Qmai/docs/{功能英文}.md](../Qmai/docs/{功能英文}.md)
- 客如云详细分析: [Keruyun/docs/{功能英文}.md](../Keruyun/docs/{功能英文}.md)
- 美团详细分析: [Meituan/docs/{功能英文}.md](../Meituan/docs/{功能英文}.md)
- 源码路径:
  - Qmai: `Qmai/src/app/src/main/java/{路径}/`
  - Keruyun: `Keruyun/src/app/src/main/java/{路径}/`
  - Meituan: `Meituan/src/app/src/main/java/{路径}/`
```

### Step 5: 更新项目索引

更新 `CLAUDE.md` 中的文档索引表格，添加新分析的条目。

---

## 约束

- **不复制源码**：文档只记录分析结论和代码路径索引，不复制大段源码
- **承认空白**：某家没有该功能就写"未发现"，不要编造
- **引用路径必须真实**：所有代码路径必须在 subagent 搜索中实际找到
- **临时分析文件**：过程中的原始探索放 `_scratch/`，不纳入版本控制
