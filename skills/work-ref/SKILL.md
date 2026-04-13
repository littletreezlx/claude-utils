---
name: work-ref
description: >
  Competitive analysis workflow for Android POS project. Launches 4 parallel subagents:
  1 for our own Shiheng (real source, as baseline) + 3 for decompiled competitors
  (Qmai/Keruyun/Meituan). Writes per-project analysis docs, then consolidates a
  cross-project comparison document with Shiheng as the first column baseline.
  Trigger when: user says "分析 [功能] 四家怎么实现的", "对比 [功能]", "竞品分析 [功能]",
  "work-ref [功能]", or similar requests to compare how we and competitors implement a feature.
version: 0.2.0
---

# 竞品功能对比工作流 (work-ref)

## 目的

以**食亨自研基线**为参照，对比三家 Android POS 竞品（企迈 Qmai、客如云 Keruyun、美团 Meituan）对某功能的实现方式，产出结构化四方对比文档。

## 适用项目

仅限 `pos/android` 竞品分析项目（含三家反编译源码）。

---

## 执行流程

### Step 0: 解析用户意图

从用户请求中提取：
- **功能名称**（中文，如"会员卡系统"，同时用于文件命名）
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

### Step 2: 启动 4 个并行 Explore Subagent

使用 Agent 工具，**在同一条消息中**发出 4 个并行调用：
- **1 个食亨 subagent**（真实源码，用「模板 A」）
- **3 个竞品 subagent**（Qmai/Keruyun/Meituan，用「模板 B」共享反编译搜索协议）

---

#### 模板 A：食亨（真实源码，无反编译启发式）

```
你正在分析食亨（Shiheng）自研 Android POS 的真实源码，作为竞品对比的我方基线。

## 任务
分析食亨中「{功能名称}」的实现方式。

## 项目信息
- 项目根：~/AndroidStudioProjects/Work_Projects/android-pos/packages/pos/android
- 业务包名：com/shiheng/
- 主模块：app/src/main/java/com/shiheng/
- 多模块目录：packages/（可能有拆分子模块）
- 资源目录：app/src/main/res/
- AndroidManifest：app/src/main/AndroidManifest.xml
{如果有已知线索，列出}

## 搜索协议

这是**真实源码**（未混淆、未反编译），按正常 Android 项目的方式探索：

1. **UI/字符串锚点**：Grep strings.xml 找中文关键词 → 反查布局和代码引用
2. **网络/数据锚点**：Grep API endpoint、@SerializedName、Retrofit 接口
3. **组件锚点**：AndroidManifest.xml 找 Activity/Service
4. **包名搜索**：直接在 com/shiheng/ 下 Grep 功能关键词（类名清晰，无需正则兜底）
5. **模块结构**：检查 packages/ 下是否有相关独立模块
6. **Git 信息**：可用 git log/blame 了解实现演进与决策时间线

## 搜索边界
- 不需要排除三方库（源码结构清晰，直接搜业务包即可）
- 不需要熔断（无混淆代码）
- 未找到时大方承认，不要编造

## 输出格式

### 1. 功能概述
- 食亨中是否实现了该功能？
- 功能定位、面向什么业务场景

### 2. 核心技术栈
- 关键技术/框架/SDK/自研组件

### 3. 架构组件
| 组件 | 路径（从 app/src/main/java/ 起或相对模块根） | 说明 |

### 4. 核心流程
- 数据流 / 调用链 / 状态机

### 5. 关键代码片段
- 关键方法签名或核心逻辑（点到为止）

### 6. 设计决策与权衡
- 自研 vs 三方选型、踩过的坑、遗留问题
- 对比竞品时值得突出的亮点或短板
```

---

#### 模板 B：竞品（反编译源码）

每个竞品 subagent 的 prompt 使用以下模板（替换 `{变量}`）：

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

**四家项目速查**：

| 项目 | 源码类型 | 根目录 | 业务包名前缀 | 备注 |
|------|---------|--------|------------|------|
| Shiheng | 真实源码 | `~/AndroidStudioProjects/Work_Projects/android-pos/packages/pos/android` | `com/shiheng/` | 自研基线，未混淆 |
| Qmai | 反编译 | `{pos项目}/Qmai` | `com/qmai/android/` | 模块化：pos_module/, pos_export/ |
| Keruyun | 反编译 | `{pos项目}/Keruyun` | `com/keruyun/` | 阿里系：含 alipay/iot |
| Meituan | 反编译 | `{pos项目}/Meituan` | `com/sankuai/sjst/rms/` | 最大（8万文件），混淆严重 |

### Step 3: 整合结果，写入两层文档

#### 层 1: 项目文档（AI 消费）

为每个**有实质发现**的项目写入分析文档：

- `Shiheng/docs/{功能中文}.md`（食亨基线 —— 写入本竞品项目镜像目录，**不**写入食亨外部仓库）
- `Qmai/docs/{功能中文}.md`
- `Keruyun/docs/{功能中文}.md`
- `Meituan/docs/{功能中文}.md`

**命名统一**：四家使用相同的文件名。

**内容定位**：面向 AI 跨会话检索，包含：
- 完整组件清单（类名 + 代码路径 + 职责）
- 搜索锚点（string name、API endpoint、Manifest 组件）
- 调用链伪代码
- 关键代码片段引用

#### 层 2: 对比文档（产品负责人消费）

在 `docs/{功能中文}-对比.md` 写入横向对比文档。

**内容定位**：面向产品负责人，聚焦技术方案差异和设计决策，**不含代码路径**。

**模板**：

```markdown
# {功能中文名}对比分析

> 分析时间：{YYYY-MM-DD}
> 详细代码分析：[Shiheng（我方）](../Shiheng/docs/{功能中文}.md) | [Qmai](../Qmai/docs/{功能中文}.md) | [Keruyun](../Keruyun/docs/{功能中文}.md) | [Meituan](../Meituan/docs/{功能中文}.md)

---

## 一、方案对比总览

| 维度 | **Shiheng（我方基线）** | Qmai (企迈) | Keruyun (客如云) | Meituan (美团) |
|------|-------------------------|-------------|-----------------|----------------|
| **方案类型** | | | | |
| **核心技术** | | | | |
| **功能定位** | | | | |
| **自研程度** | | | | |

---

## 二、技术架构

### 2.1 Shiheng（我方基线） — {方案概括}

（mermaid 架构图）

**技术要点**：
- ...

### 2.2 Qmai — {方案概括}

（mermaid 架构图）

**技术要点**：
- ...

### 2.3 Keruyun — {方案概括}

（mermaid 架构图）

**技术要点**：
- ...

### 2.4 Meituan — {方案概括}

（mermaid 架构图）

**技术要点**：
- ...

---

## 三、能力矩阵

| 能力 | Shiheng | Qmai | Keruyun | Meituan |
|------|:-------:|:----:|:-------:|:-------:|
| ... | ✅/❌/⚠️ | | | |

---

## 四、本质差异与我方定位

- **对比三家，我方强在哪**：...
- **对比三家，我方弱在哪**：...
- **可借鉴的竞品设计**：...

---

## 四、本质差异

{对比表格 + 一句话总结，突出技术哲学差异}
```

**对比文档规范**：
- 图表用 **mermaid**（禁止 ASCII 图）
- 聚焦**技术方案和设计决策**，不写代码路径
- 用 ✅❌⚠️ 矩阵快速传达能力差异
- 头部链接到各项目详细分析（给想深入的读者一个入口）

### Step 5: 更新项目索引

更新 `CLAUDE.md` 中的文档索引表格，添加新分析的条目。

---

## 约束

- **不复制源码**：文档只记录分析结论和代码路径索引，不复制大段源码
- **承认空白**：某家没有该功能就写"未发现"，不要编造
- **引用路径必须真实**：所有代码路径必须在 subagent 搜索中实际找到
- **临时分析文件**：过程中的原始探索放 `_scratch/`，不纳入版本控制
