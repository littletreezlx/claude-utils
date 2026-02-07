# 项目级 CLAUDE.md 模板

> 将此模板复制到项目的 `.claude/CLAUDE.md` 或项目根目录 `CLAUDE.md`，按需裁剪。
> 全局通用规则已在 `~/.claude/CLAUDE.md` 中定义，此处只写项目特定的内容。

---

## 项目文档体系

### 核心文档（必须维护）
```
README.md            → 项目概述（人类阅读）
integration_test/    → 功能规范（唯一真相）
FEATURE_CODE_MAP.md  → 功能-代码映射（AI 导航）
```

**FEATURE_CODE_MAP 维护规则**：
- 新增功能/文件时，**必须**立即注册到此文件
- 重构导致文件移动/重命名时，**必须**同步更新
- **严禁**靠猜测定位代码，必须先查此地图

### 可选文档（按需维护）
- ABOUT.md - 项目初衷与愿景
- PROJECT_STATUS.md - 项目状态快照
- docs/decisions/ - ADR（重要架构决策）

---

## 项目特定工作流

### E2E 驱动闭环

```
改代码 → 写测试 → 启动服务 → 运行测试 → 看日志 → 失败？修复重测 → ✅ 通过交付
```

**执行要点**：
- 服务：后台启动 + 日志重定向（`./start.sh > logs/dev.log 2>&1 &`）
- 运行：headless 模式，不弹窗干扰用户
- 日志：测试前清空，优先 `grep -i "error\|exception"` 抓关键报错，无明显报错时 `tail -n 100`
- 检查：测试前确认服务已启动（`lsof -i :PORT`）

### 重构代码前（最易出问题）

1. 读 ADR 索引 - 理解设计意图
2. 读相关测试 - 理解预期行为
3. 运行测试 - 确保起点通过
4. 执行重构
5. 验证：测试通过 + 文档更新

---

## 测试策略（项目特定）

### 冰山策略 (Iceberg Strategy)

对于**重交互、重状态**的应用，采用测试分层：

```
🧊 水下 80% - Unit Tests (逻辑验证)
├── 业务逻辑层
├── 状态流转、算法决策
└── 毫秒级反馈，稳定可靠

🏔️ 水上 20% - E2E Tests (流程验证)
├── 核心用户路径（Happy Path）
├── 避免通过 UI 进行繁琐的前置数据准备
└── 使用 Test Facade 注入测试状态
```

**核心理念**：把逻辑验证交给 Unit Test（快、稳），把流程验证留给 E2E（慢、脆）。

### Test Facade 模式

当 E2E 测试因 UI 状态复杂（动画、自动选择、异步加载）而变得脆弱时：

**问题**：测试脚本需要通过 UI 模拟用户操作来创建测试数据，速度慢且易失败。

**方案**：为测试提供"后门"，绕过 UI 直接操作业务逻辑层来注入状态。

**红线**：
- ❌ 禁止在生产代码中写 `if (isTestMode)` 等测试判断
- ❌ 禁止为了测试而牺牲用户体验
- ✅ Test Facade 应独立放在 `test_utils/` 或 `debug/` 目录

### 应用类型决策树

| 应用类型 | 特征 | 测试重心 |
|---------|------|---------|
| **重逻辑** | 复杂状态、算法、数据库 | Unit Test + Test Facade |
| **重表现** | 静态展示、简单 CRUD | Golden Test / 视觉对比 |
| **重交互** | 动画、物理引擎、手势 | Unit Test 逻辑 + 最少 E2E |

**快速判断**：
> **如果我把 UI 全删了，这代码还能跑吗？**
> - 能 → 用 Unit Test 覆盖逻辑层
> - 不能 → 简单页面就算了，复杂页面请重构

---

## AI 协作生态 (按需启用)

### 角色指引

| Workflow/Command | 角色 | 职责 | 输入 | 输出 |
|----------|-----|------|------|------|
| **`/ui-spec`** | **Technical PM** | 逆向分析代码，提取逻辑 | 代码文件 / 截图 | `docs/ui/specs/xxx_spec.md` |
| **`/feat-discuss`** | **Tech Lead** | 澄清需求，同步文档 | 用户讨论 | 更新 `xxx_spec.md` |
| **`/ui-redesign`** | **Lead Designer** | 基于逻辑文档进行视觉重塑 | Spec 文档 + 截图 | 设计图 + `implementation_plan.md` |

### 最佳实践循环
1. **理解现状**: 使用 `/ui-spec` 扫描现有代码，生成基础 Spec。
2. **讨论需求**: 使用 `/feat-discuss` 讨论新想法，AI 会自动更新 Spec。
3. **视觉落地**: 使用 `/ui-redesign` 读取最新的 Spec，生成既美观又符合逻辑的设计。

### 命名规范 (Naming Convention)
- 截图: `{base_name}.png` (例如: `ios_main_page.png`)
- Spec: `{base_name}_spec.md` (例如: `main_page_spec.md`)
- 映射关系维护在 `docs/ui/UI_SHOWCASE.md`。

---

## Gemini Context 工作流 (按需启用)

### 核心理念：文档分层

| 文档类型 | 目标读者 | 内容重点 | 示例 |
|---------|---------|---------|------|
| **技术实现文档** | Claude Code | 代码路径、行号、技术方案 | `docs/features/xxx.md` |
| **产品逻辑文档** | Gemini | 用户体验、设计哲学、产品权衡 | `${项目名}-context-for-gemini.md` |

### Gemini Context 原则

1. **用产品语言，不写代码路径**
   - ✅ Good: "右滑标记已读，1:1 跟手，触觉反馈增强物理质感"
   - ❌ Bad: "使用 Dismissible Widget (article_list.dart:411)"

2. **聚焦用户体验和产品决策**
   - ✅ "地铁上仍可离线阅读"
   - ❌ "使用 Drift 本地数据库"

3. **必须包含"快速状态总览"**（完成度、核心能力、已知缺口）

4. **优先级明确，工时透明**（P0/P1/P2/P3 + 预估工时）

### 相关 Commands
- **`/init-context-for-gemini`**: 生成/更新 Gemini context 文档
- **`/feat-discuss`**: 与 Gemini 讨论新功能
- **`/feat-done`**: 功能完成后，生成验收报告
