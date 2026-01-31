---
description: 测试运行与修复 ultrathink

---

# 测试运行与修复

> 运行项目测试，识别并修复失败用例

## 输入方式

```bash
/test-run              # 运行所有测试
/test-run unit         # 仅单元测试
/test-run integration  # 仅集成测试
/test-run e2e          # 仅 E2E 测试
/test-run $ARGUMENTS
```

---

## 执行流程

### 1. 识别测试环境
- 定位测试命令（package.json / pytest.ini / Makefile / pubspec.yaml）
- 确认测试框架（Jest / Vitest / Pytest / Go test / Playwright / Flutter Test）
- 检查测试环境就绪（数据库、服务、依赖）
- **Flutter 检查**: `flutter pub get`, `flutter packages pub run build_runner build`

### 2. 运行测试

**⭐ Flutter 项目特殊处理**：

**检测条件**：
- 存在 `pubspec.yaml`
- 项目路径包含 `flutter/` 目录

**优先使用统一测试脚本**：
```bash
# 检查上层统一脚本是否存在
if [ -f ../../scripts/test.sh ]; then
    # 单元测试：使用统一脚本（AI 友好）
    ../../scripts/test.sh                           # 全量
    ../../scripts/test.sh test/unit/xxx_test.dart   # 单文件

    # E2E 测试：使用统一 E2E 脚本
    ../../scripts/run-e2e.sh                        # 全量
    ../../scripts/run-e2e.sh integration_test/xxx.dart  # 单文件
else
    # 回退到标准命令
    flutter test --reporter=compact
fi
```

**其他项目**：
- **使用紧凑模式避免日志爆炸**: `--reporter=compact` 或 `--reporter=json`
- 执行测试命令，收集结果
- 记录失败用例和错误信息
- E2E 测试需收集截图/日志

**⚠️ 必须将输出重定向到文件**：
```bash
# ✅ 正确：输出到文件，避免 BashOutput 轮询卡死
npm test > /tmp/test-result.txt 2>&1
flutter test > /tmp/test-result.txt 2>&1

# ❌ 错误：直接在终端输出，会导致反复轮询 BashOutput
npm test 2>&1 | tail -30
```

测试完成后读取文件分析：
```bash
# 查看摘要
tail -50 /tmp/test-result.txt

# 筛选失败信息
grep -E "(FAIL|Error|✕)" /tmp/test-result.txt
```

**⚠️ 大量失败时的处理策略**：
当测试失败数量超过 10 个时，输出会非常庞大（每个失败都有完整堆栈），导致：
- Claude Code 处理输出耗时远超测试执行时间
- Token 消耗激增，可能被截断丢失关键信息

**应对策略**：
1. **先跑一次快速扫描**：`../../scripts/test.sh` 或 `flutter test --reporter=compact 2>&1 | head -100` 获取失败概览
2. **聚焦单个失败**：`flutter test path/to/failing_test.dart` 只看一个失败的完整日志
3. **按目录分批**：`flutter test test/unit/` 而非全量运行
4. **识别共同原因**：大量失败通常有共同根因，修一个可能修复多个

### 3. 诊断失败原因

**代码问题**（修复源代码）：
- 业务逻辑错误、边界条件处理不当
- 依赖注入或 mock 配置错误
- 异步处理问题（Promise/async-await）
- 模块间接口不匹配、数据传递错误
- 事务和状态管理问题

**测试问题**（更新测试用例）：
- 断言不符合当前需求
- 测试数据过时或不正确
- 测试与实际需求不符

**环境问题**（调整配置）：
- 数据库连接、API 调用失败
- 环境变量或配置缺失
- 测试服务未正确启动
- **Flutter 特定**: Hive未初始化、Riverpod Provider未配置、SharedPreferences未mock

**稳定性问题**（优化等待策略）：
- 时序问题（元素未加载完成）
- 选择器失效或不稳定
- 异步操作等待不当
- 测试数据冲突或状态污染

### 4. 修复并验证
- 修复后重新运行测试
- 确保没有引入新问题
- 多次运行验证稳定性（E2E）
- **Token 优化**: 使用紧凑模式，避免完整日志输出，只报告关键失败信息

**⚠️ 死循环熔断机制**：
同一测试修复 **3 次仍失败**时，必须：
1. **停止修复** - 不再继续尝试
2. **标记状态** - 在输出中标记为"需要人工介入"
3. **跳过继续** - 处理下一个失败测试
4. **记录尝试** - 简要说明已尝试的修复方向

> 避免在复杂依赖问题上死磕耗尽 Token

---

## 输出格式

```markdown
## 测试执行结果

**类型**: [unit/integration/e2e/all]
**通过**: X | **失败**: Y | **跳过**: Z

### 已修复
1. [测试名] - [问题类型] - [修复说明]

### 遗留问题（如有）
1. [测试名] - [原因] - [建议]
```

---

## 代码优化信号

修复测试时如发现以下问题，说明代码需要优化：

| 信号 | 暴露的设计问题 | 处理方式 |
|------|---------------|---------|
| 难以 mock | 依赖太多、耦合太紧 | 记录，建议拆分 |
| setup 复杂 | 单个测试需大量前置条件 | 记录，建议简化接口 |
| 无法隔离 | 测试一个功能必须牵扯多模块 | 记录，建议解耦 |
| 断言困难 | 内部状态不可观测 | 记录，建议暴露关键状态 |

**处理流程**：
- 局部问题 → 立即小重构 → 继续修复测试
- 架构问题 → 完成当前任务 → 在输出中列出优化建议

---

## 约束条件

- 优先修复代码 bug，谨慎修改测试用例
- 修改测试前理解原始设计意图
- 保持测试独立性和确定性
- E2E 使用稳定选择器（data-testid 优先）
- 避免过度 mock 导致测试失去价值

---

## 常见问题速查

### Flutter 测试常见问题

#### 1. Mockito MissingDummyValueError
```
MissingDummyValueError: Result<void>
```

**原因**: Mockito 需要为泛型返回类型提供 dummy value

**解决**:
```dart
// 在 setUpAll 或 setUp 中调用
setUpAll(() {
  provideDummy<Result<void>>(Result.success(null));
  provideDummy<Result<Session>>(Result.success(dummySession));
  provideDummy<Result<List<Session>>>(Result.success(<Session>[]));
});
```

**最佳实践**: 创建 `test/test_helpers.dart` 统一管理:
```dart
void setupMockitoDummies() {
  provideDummy<Result<void>>(Result.success(null));
  provideDummy<Result<Session>>(Result.success(_createDummySession()));
  // ... 其他类型
}
```

#### 2. SharedPreferences/Hive 初始化错误
```
sharedPreferencesProvider 必须在 ProviderScope 中 override
HiveError: You need to initialize Hive
```

**原因**: Widget 测试使用了真实 provider，但平台服务未初始化

**解决**:
```dart
setUpAll(() async {
  TestWidgetsFlutterBinding.ensureInitialized();
  SharedPreferences.setMockInitialValues({});
  Hive.init('./test_hive_data');
});

// 在测试中 override provider
await tester.pumpWidget(
  ProviderScope(
    overrides: [
      sharedPreferencesProvider.overrideWithValue(prefs),
      storageServiceProvider.overrideWithValue(mockStorage),
    ],
    child: const MaterialApp(home: MyWidget()),
  ),
);
```

#### 3. MissingStubError
```
MissingStubError: 'updateSessionModel'
No stub was found which matches the arguments
```

**原因**: Mock 对象缺少特定参数组合的 stub

**解决**:
```dart
// 方法 1: 添加具体 stub
when(mockService.updateSessionModel('1', 'invalid-model'))
  .thenAnswer((_) async => Result.failure(AppError.validation('不支持')));

// 方法 2: 使用 anyNamed 匹配任意参数
when(mockService.updateSessionModel(any, anyNamed('model')))
  .thenAnswer((_) async => Result.success(null));

// 方法 3: 使用 @GenerateNiceMocks 生成宽松 mock
@GenerateNiceMocks([MockSpec<MyService>()])
```

#### 4. 测试超时（Widget 测试等待真实服务）
```
compact_model_selector_update_test.dart 一直卡着不动
```

**原因**: Widget 测试使用了未 mock 的 provider，等待真实网络请求

**解决**:
- 检查测试是否 override 了所有依赖的 service provider
- 避免在 Widget 测试中使用 `ProviderContainer()` 不带 overrides
- 对复杂 Widget，考虑只测试纯展示逻辑，业务逻辑在 provider 测试中验证

#### 5. 正则表达式全局标志问题 (JavaScript/TypeScript)
```
hasTemplateVariables 返回不一致结果
```

**原因**: 使用 `/g` 标志的正则会保存 `lastIndex` 状态

**解决**:
```typescript
// ❌ 错误：重用带 /g 的正则
const regex = /\{(\w+)\}/g;
regex.test(str1); // 可能返回错误结果

// ✅ 正确：每次创建新实例
function hasMatch(str: string): boolean {
  const regex = new RegExp(PATTERN.source); // 不带 /g
  return regex.test(str);
}
```

### Node.js (Jest) 测试常见问题

#### 1. Snapshot 不匹配
```
Snapshot name: `MyComponent renders correctly 1`
- Snapshot  - 1
+ Received  + 1
```

**判断逻辑**：
- **逻辑变更导致** → 修复代码，不更新快照
- **非逻辑变更导致**（格式调整、依赖升级等） → 允许更新快照

**更新快照**：
```bash
# 更新单个测试的快照
npx jest path/to/test.ts -u

# 更新所有快照
npx jest -u
```

**⚠️ 必须遵守**：
- 更新前确认变更是**预期的**
- 在输出中注明"已更新快照: xxx"
- 如果无法判断是否应该更新，标记为"需要人工确认"

#### 2. ESM 模块问题
```
SyntaxError: Cannot use import statement outside a module
```

**解决**:
```bash
NODE_OPTIONS="--experimental-vm-modules" npx jest
```

#### 3. 测试断言与实际输出不匹配
```
Expected: "<files_info>"
Actual: "<files_info count=\"1\">"
```

**处理**:
- 运行单个测试查看完整输出
- 更新断言以匹配实际（正确的）输出
- 使用 `toContain()` 或正则匹配而非完全相等

#### 4. Jest watchman 卡住问题
```
watchman warning: Recrawled this watch 5 times
RUNS  test/xxx.test.ts  # 卡住不动
```

**原因**: watchman 文件监控在某些项目配置下不稳定，导致 Jest 挂起

**解决**:
```bash
# 方法 1: 清理 watchman
watchman watch-del '/path/to/project'
watchman watch-project '/path/to/project'

# 方法 2: 禁用 watchman 并强制退出
npx jest --no-watchman --forceExit test/xxx.test.ts

# 方法 3: 串行执行避免并发问题
npx jest --runInBand --forceExit
```

#### 5. beforeAll 创建的测试数据被 beforeEach 清理
```
Foreign key constraint failed / Record not found
```

**原因**: 全局 `setup.ts` 的 `beforeEach` 会清理所有表数据，但测试在 `beforeAll` 中创建数据

**执行顺序**:
1. `beforeAll` → 创建 testRole
2. `beforeEach` (全局) → 删除所有数据（testRole 被删除！）
3. 测试运行 → testRole 不存在 → 失败

**解决方案**:
```typescript
// ❌ 错误：在 beforeAll 创建数据
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

beforeAll(async () => {
  const role = await prisma.role.create({ ... }); // 会被清理
  testRoleId = role.id;
});

// ✅ 正确：使用 setup.ts 的 prisma + beforeEach 创建数据
import { prisma } from './setup';

beforeEach(async () => {
  const role = await prisma.role.create({ ... }); // 每次测试前新建
  testRoleId = role.id;
});
```

**关键原则**:
- 使用 `import { prisma } from './setup'` 统一数据库实例
- 将数据创建从 `beforeAll` 改为 `beforeEach`（与全局清理配合）
- 使每个测试独立，不依赖前一个测试创建的数据
- 如果测试间有数据依赖，在测试内部直接创建所需数据

#### 6. Content-Type 断言过于严格
```
Expected: "text/event-stream; charset=utf-8"
Received: "text/event-stream"
```

**解决**: 使用正则匹配而非完全相等
```typescript
// ❌ 过于严格
expect(response.headers['content-type']).toBe('text/event-stream; charset=utf-8');

// ✅ 更灵活
expect(response.headers['content-type']).toMatch(/^text\/event-stream/);
```

---

## 相关文档
- `/test-plan` - 测试规划（生成 DAG 任务）
