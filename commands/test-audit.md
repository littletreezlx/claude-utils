---
description: 测试基础设施审计与修复 ultrathink

---

# 测试基础设施审计与修复

> 审计当前项目的测试方案，直接修复缺失的配置和脚本

## 使用方式

```bash
/test-audit                    # 审计并修复当前项目
/test-audit $ARGUMENTS         # 指定关注点（unit/integration/e2e）
```

---

## 核心原则

1. **审计即修复** - 发现问题直接解决，不询问
2. **全类型覆盖** - 单元/集成/E2E 测试都要检查
3. **技术栈适配** - 根据项目类型选择方案
4. **借鉴成熟项目** - 参考 nas-server 等已有方案

---

## 执行流程

### 第一步：识别项目类型

| 标识文件 | 项目类型 |
|----------|----------|
| `pubspec.yaml` | Flutter |
| `package.json` + `src/` | Node.js |
| `pyproject.toml` | Python |
| `server/` + `app/` | 全栈（分别处理）|

### 第二步：检查测试脚本

#### 必须检查的项目

**package.json scripts 或等效配置：**

```json
{
  "test": "...",                    // 基础测试命令
  "test:unit": "...",               // 单元测试
  "test:integration": "...",        // 集成测试
  "test:e2e": "...",                // E2E 测试
  "test:watch": "...",              // 监听模式
  "test:coverage": "..."            // 覆盖率
}
```

**E2E 测试脚本核心功能：**
- [ ] 进程清理（残留进程导致测试失败）
- [ ] 依赖服务管理（后端/数据库启动）
- [ ] 智能输出（成功静默，失败显示详情）
- [ ] 测试报告生成

#### 缺失时的处理

**不使用模板** - 直接根据项目实际情况生成：
1. 读取项目结构
2. 识别测试框架
3. 生成适配的脚本
4. 更新 package.json

### 第三步：验证测试可运行

```bash
# 快速验证测试能否运行（不需要全部通过）
npm test -- --passWithNoTests --forceExit 2>&1 | head -20
flutter test --reporter=compact 2>&1 | head -20
pytest --collect-only 2>&1 | head -20
```

### 第四步：更新项目文档

在 `CLAUDE.md` 添加/更新测试命令部分。

---

## 技术栈方案参考

### Node.js 后端（参考 nas-server）

**package.json scripts：**
```json
{
  "test": "jest --forceExit",
  "test:unit": "jest --selectProjects backend --forceExit",
  "test:integration": "jest tests/integration/ --forceExit",
  "test:e2e": "bash scripts/test-helpers/run-e2e-smart.sh",
  "test:watch": "jest --watch"
}
```

**E2E 脚本核心逻辑：**
```bash
#!/bin/bash
set -e

# 1. 清理残留进程
pkill -f "playwright|chromium" 2>/dev/null || true

# 2. 运行测试，输出到临时文件
npx playwright test 2>&1 | tee /tmp/e2e.log
EXIT_CODE=${PIPESTATUS[0]}

# 3. 智能输出
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 测试通过"
else
    echo "❌ 失败的测试："
    grep -E "(✗|FAIL)" /tmp/e2e.log | head -10
    echo "💥 错误信息："
    grep -A 3 "Error:" /tmp/e2e.log | head -20
fi
```

### Flutter 项目

**关键点：**
- macOS 需要逐个文件运行 E2E（避免 log reader 错误）
- 需要清理 flutter_tester 进程
- 需要清理 build.db 锁文件
- 可选：后台运行支持（修改 MainFlutterWindow.swift）

**E2E 脚本核心功能：**
```bash
# 进程清理
pkill -f "flutter_tester" 2>/dev/null || true
rm -f build/macos/.../build.db* 2>/dev/null || true

# 逐个运行测试文件
for test_file in integration_test/*_test.dart; do
    flutter test "$test_file" -d macos
done

# 生成报告
echo "| 测试 | 状态 | 耗时 |" >> report.md
```

### Python 项目

**pytest 配置：**
```ini
# pytest.ini 或 pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = "test_*.py"
addopts = "-v --tb=short"
```

### 全栈项目

分别审计各子项目，可选创建全量测试脚本：
```bash
# scripts/test-all.sh
cd server && npm test
cd ../app && flutter test
```

---

## 输出格式

```markdown
## 测试基础设施审计结果

### 项目: xxx
- **类型**: Flutter + Node.js
- **路径**: /path/to/project

### 单元测试 ✅
- 测试目录存在
- 测试命令正常

### 集成测试 ⚠️ 已修复
- [创建] test:integration 命令
- [更新] jest.config.js

### E2E 测试 ⚠️ 已修复
- [创建] scripts/run-e2e.sh
- [更新] package.json
- [更新] .gitignore

### 已更新文档
- CLAUDE.md 测试命令部分
```

---

## 禁止事项

1. **不使用模板文件** - 根据项目实际情况生成
2. **不询问是否修复** - 直接修复
3. **不生成报告文件** - 只在对话中输出
4. **不修改业务代码** - 只处理测试基础设施

---

## 关联命令

- `/test-plan` - 规划测试任务（DAG 编排）
- `/test-run` - 运行测试并修复失败
- `/create-e2e-test` - 创建新测试用例
