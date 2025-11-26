# 电商系统开发 - DAG 执行计划（详细版）

## STAGE ## name="数据库初始化" mode="serial"
# 🎯 阶段目标：创建数据库表结构和初始化基础数据
# 📥 输入：空白数据库
# 📤 输出：完整的数据库架构和基础数据
# 🔗 为下一阶段提供：可以开始业务开发的数据库环境

## TASK ##
创建数据库表结构

**📖 背景**：
项目需要用户、订单、支付、商品四个核心表，作为整个系统的数据基础。必须先完成数据库表结构创建，才能进行业务逻辑开发。

**🔨 要做什么**：
1. 创建 migrations/001_create_tables.sql 文件
2. 定义 users 表（id, name, email, password, role）
3. 定义 orders 表（id, user_id, total, status, created_at）
4. 定义 payments 表（id, order_id, amount, method, status）
5. 定义 products 表（id, name, price, stock, description）
6. 添加必要的索引（user_id, order_id 等）
7. 添加外键约束确保数据一致性
8. 运行迁移脚本

**✅ 完成标志**：
- SQL 文件创建成功，包含所有表定义
- 迁移命令 `npm run migrate` 执行通过
- 数据库中存在 4 个新表
- 所有索引和外键约束正确创建
- 表结构符合设计文档要求

**📤 输出状态**：
- ✅ 数据库表结构已创建完成
- ✅ 索引和约束已正确设置
- ✅ 为下一任务提供：可以插入数据的表结构
- ➡️ 下一任务可以开始初始化基础数据

文件: migrations/001_create_tables.sql
验证: npm run migrate:check && \
      psql -d ecommerce -c "\dt" | grep -E "users|orders|payments|products" | wc -l | grep -q "4" && \
      echo "✅ 4 个核心表已创建"

## TASK ##
初始化系统基础数据

**📥 输入依赖**：
- ⬆️ 前一任务已创建完整的表结构
- ⬆️ 数据库连接正常，可以插入数据

**📖 背景**：
系统需要一些基础数据才能正常运行，包括用户角色（管理员、普通用户）、系统配置（税率、运费规则）、初始管理员账号。这些数据是业务逻辑的前置条件。

**🔨 要做什么**：
1. 创建 migrations/002_seed_data.sql 文件
2. 插入用户角色数据（admin, customer, guest）
3. 插入初始管理员账号（用于系统管理）
4. 插入系统配置数据（税率 8%，免费邮费阈值 100）
5. 插入商品分类数据（电子产品、服装、食品等）
6. 运行数据初始化脚本
7. 验证数据已正确插入

**✅ 完成标志**：
- SQL 文件创建成功，包含所有初始数据
- 数据初始化命令执行通过
- 数据库中存在 3 个角色、1 个管理员账号
- 系统配置表有至少 5 条配置数据
- 商品分类表有至少 5 个分类

**📤 输出状态**：
- ✅ 所有基础数据已初始化完成
- ✅ 系统具备完整的运行环境
- ✅ 管理员账号可用（admin / admin123）
- ➡️ 下一阶段可以开始业务模块开发

文件: migrations/002_seed_data.sql
验证: npm run seed:verify && \
      psql -d ecommerce -c "SELECT COUNT(*) FROM roles" | grep -q "3" && \
      psql -d ecommerce -c "SELECT COUNT(*) FROM admins" | grep -q "1" && \
      echo "✅ 基础数据已初始化，系统环境就绪"

## STAGE ## name="业务模块开发" mode="parallel" max_workers="4"
# 🎯 阶段目标：并行开发各业务模块，提高开发效率
# 📥 输入：来自上一阶段的完整数据库环境
# 📤 输出：所有核心业务模块的完整实现
# 🔗 为下一阶段提供：可以进行集成测试的业务功能

## TASK ##
实现用户管理模块

**📖 背景**：
用户模块是系统的核心之一，提供用户注册、登录、权限验证、个人信息管理等功能。与订单、支付、商品模块相对独立，可以并行开发。

**🔨 要做什么**：
1. 创建 src/modules/user/user.model.ts（用户数据模型）
2. 创建 src/modules/user/user.service.ts（业务逻辑层）
   - 实现用户注册（邮箱验证、密码加密）
   - 实现用户登录（JWT Token 生成）
   - 实现权限验证中间件
   - 实现个人信息 CRUD 操作
3. 创建 src/api/user.controller.ts（API 路由层）
   - POST /api/users/register（注册）
   - POST /api/users/login（登录）
   - GET /api/users/profile（获取个人信息）
   - PUT /api/users/profile（更新个人信息）
4. 编写单元测试（覆盖率 > 80%）
5. 更新 API 文档

**✅ 完成标志**：
- 所有文件创建完成，代码结构清晰
- 4 个 API 端点全部实现
- 单元测试通过，覆盖率达到 85%
- 代码符合 ESLint 规范，无警告
- API 文档已更新，包含请求/响应示例
- 手动测试注册登录流程正常

文件: src/modules/user/**/*.ts
文件: src/api/user.controller.ts
排除: src/modules/user/**/*.test.ts
排除: src/common/

验证: npm test -- user.service.test.ts && \
      npm run lint -- src/modules/user/ && \
      npm run coverage -- user | grep -E "Lines.*8[5-9]|Lines.*9[0-9]" && \
      echo "✅ 用户模块开发完成，测试通过"

## TASK ##
实现订单管理模块

**📖 背景**：
订单模块处理用户的下单流程，包括创建订单、查询订单、订单状态流转、取消订单等功能。与用户模块有数据关联，但业务逻辑独立，可以并行开发。

**🔨 要做什么**：
1. 创建 src/modules/order/order.model.ts（订单数据模型）
2. 创建 src/modules/order/order.service.ts（业务逻辑层）
   - 实现创建订单（库存检查、价格计算）
   - 实现订单查询（分页、筛选）
   - 实现订单状态流转（待支付 → 已支付 → 配送中 → 已完成）
   - 实现取消订单（退库存、记录原因）
3. 创建 src/api/order.controller.ts（API 路由层）
   - POST /api/orders（创建订单）
   - GET /api/orders（查询订单列表）
   - GET /api/orders/:id（查询订单详情）
   - PUT /api/orders/:id/cancel（取消订单）
4. 编写单元测试（覆盖率 > 80%）
5. 更新 API 文档

**✅ 完成标志**：
- 所有文件创建完成，订单状态机正确实现
- 4 个 API 端点全部实现
- 订单状态流转逻辑正确（包含边界条件处理）
- 单元测试通过，覆盖率达到 82%
- 代码符合 ESLint 规范
- API 文档已更新

文件: src/modules/order/**/*.ts
文件: src/api/order.controller.ts
排除: src/modules/order/**/*.test.ts
排除: src/common/

验证: npm test -- order.service.test.ts && \
      npm run lint -- src/modules/order/ && \
      echo "✅ 订单模块开发完成，状态机测试通过"

## TASK ##
实现支付集成模块

**📖 背景**：
支付模块集成第三方支付（支付宝、微信支付），处理支付发起、回调验证、退款逻辑。与其他模块独立，可以并行开发。

**🔨 要做什么**：
1. 创建 src/modules/payment/payment.model.ts（支付记录模型）
2. 创建 src/modules/payment/payment.service.ts（业务逻辑层）
   - 实现支付宝支付集成（SDK 调用）
   - 实现微信支付集成（SDK 调用）
   - 实现支付回调验证（签名验证）
   - 实现退款逻辑（部分退款、全额退款）
3. 创建 src/api/payment.controller.ts（API 路由层）
   - POST /api/payments/alipay（发起支付宝支付）
   - POST /api/payments/wechat（发起微信支付）
   - POST /api/payments/callback（支付回调）
   - POST /api/payments/:id/refund（申请退款）
4. 编写单元测试（mock 第三方 SDK）
5. 更新 API 文档

**✅ 完成标志**：
- 支付宝和微信支付 SDK 正确集成
- 4 个 API 端点全部实现
- 支付回调验证逻辑正确（防重放攻击）
- 单元测试通过（使用 mock 数据）
- 代码符合 ESLint 规范
- API 文档已更新，包含回调处理说明

文件: src/modules/payment/**/*.ts
文件: src/api/payment.controller.ts
排除: src/modules/payment/**/*.test.ts
排除: src/common/

验证: npm test -- payment.service.test.ts && \
      npm run lint -- src/modules/payment/ && \
      echo "✅ 支付模块开发完成，回调验证测试通过"

## TASK ##
实现商品管理模块

**📖 背景**：
商品模块管理商品信息，包括商品列表、详情、库存管理、分类筛选等功能。与其他模块相对独立，可以并行开发。

**🔨 要做什么**：
1. 创建 src/modules/product/product.model.ts（商品数据模型）
2. 创建 src/modules/product/product.service.ts（业务逻辑层）
   - 实现商品 CRUD 操作
   - 实现商品列表查询（分页、排序、筛选）
   - 实现库存管理（扣减、回退）
   - 实现分类筛选
3. 创建 src/api/product.controller.ts（API 路由层）
   - GET /api/products（商品列表）
   - GET /api/products/:id（商品详情）
   - POST /api/products（创建商品，管理员）
   - PUT /api/products/:id（更新商品，管理员）
4. 编写单元测试
5. 更新 API 文档

**✅ 完成标志**：
- 所有文件创建完成
- 4 个 API 端点全部实现
- 库存管理逻辑正确（并发安全）
- 单元测试通过，覆盖率 > 80%
- 代码符合 ESLint 规范
- API 文档已更新

文件: src/modules/product/**/*.ts
文件: src/api/product.controller.ts
排除: src/modules/product/**/*.test.ts
排除: src/common/

验证: npm test -- product.service.test.ts && \
      npm run lint -- src/modules/product/ && \
      echo "✅ 商品模块开发完成，库存管理测试通过"

## STAGE ## name="集成测试" mode="serial"
# 🎯 阶段目标：验证各模块间的协作是否正常
# 📥 输入：来自上一阶段的所有业务模块实现
# 📤 输出：验证通过的集成功能，确保模块间正确协作
# 🔗 为下一阶段提供：可以进行端到端测试的稳定功能

## TASK ##
用户-订单集成测试

**📥 输入依赖**：
- ⬆️ 用户模块和订单模块已开发完成
- ⬆️ 数据库环境正常，测试数据已准备

**📖 背景**：
验证用户下单的完整流程，确保用户模块和订单模块能够正确协作。这是核心业务流程，必须严格验证。

**🔨 要做什么**：
1. 创建 tests/integration/user-order.test.ts
2. 编写集成测试场景：
   - 用户注册 → 登录 → 浏览商品 → 创建订单
   - 验证订单中的用户信息正确关联
   - 验证订单状态流转
   - 验证用户可以查询自己的订单
   - 验证用户不能查询他人订单（权限隔离）
3. 运行集成测试
4. 修复发现的问题
5. 确保测试通过率 100%

**✅ 完成标志**：
- 集成测试文件创建完成
- 所有测试场景都已编写（至少 8 个测试用例）
- 集成测试 100% 通过
- 用户-订单数据关联正确
- 权限隔离验证通过

**📤 输出状态**：
- ✅ 用户下单流程验证通过
- ✅ 数据关联正确，无权限漏洞
- ✅ 为下一任务提供：稳定的用户-订单功能
- ➡️ 下一任务可以测试订单-支付集成

文件: tests/integration/user-order.test.ts
验证: npm run test:integration -- user-order && \
      echo "✅ 用户-订单集成测试通过"

## TASK ##
订单-支付集成测试

**📥 输入依赖**：
- ⬆️ 订单模块和支付模块已开发完成
- ⬆️ 用户-订单集成已验证通过

**📖 背景**：
验证订单支付的完整流程，确保订单模块和支付模块能够正确协作。包括支付成功、支付失败、退款等场景。

**🔨 要做什么**：
1. 创建 tests/integration/order-payment.test.ts
2. 编写集成测试场景：
   - 创建订单 → 发起支付 → 支付成功 → 订单状态更新
   - 创建订单 → 发起支付 → 支付失败 → 订单状态保持
   - 已支付订单 → 申请退款 → 退款成功 → 订单状态更新
   - 验证支付金额与订单金额一致
   - 验证支付记录正确保存
3. 使用 mock 模拟第三方支付回调
4. 运行集成测试
5. 修复发现的问题

**✅ 完成标志**：
- 集成测试文件创建完成
- 所有支付场景都已测试（至少 10 个测试用例）
- 集成测试 100% 通过
- 支付-订单状态同步正确
- 退款逻辑验证通过

**📤 输出状态**：
- ✅ 订单-支付流程验证通过
- ✅ 支付回调处理正确
- ✅ 退款逻辑正常工作
- ➡️ 下一阶段可以进行端到端测试

文件: tests/integration/order-payment.test.ts
验证: npm run test:integration -- order-payment && \
      echo "✅ 订单-支付集成测试通过，支付流程稳定"

## STAGE ## name="端到端测试" mode="parallel" max_workers="2"
# 🎯 阶段目标：完整的用户场景测试，确保系统整体可用
# 📥 输入：来自上一阶段验证通过的集成功能
# 📤 输出：可以发布的稳定系统
# 🔗 为发布提供：经过完整验证的可发布版本

## TASK ##
E2E 测试：用户完整流程

**📖 背景**：
从用户视角验证完整的使用流程，模拟真实用户操作，确保整个系统端到端可用。

**🔨 要做什么**：
1. 创建 tests/e2e/user-flow.spec.ts
2. 使用 Playwright 编写 E2E 测试：
   - 打开网站首页
   - 点击注册，填写注册信息，提交
   - 邮箱验证（mock）
   - 登录系统
   - 查看个人信息
   - 更新个人信息
   - 退出登录
3. 运行 E2E 测试（headless 模式）
4. 截图保存测试证据

**✅ 完成标志**：
- E2E 测试文件创建完成
- 测试覆盖用户完整流程（7-8 个步骤）
- 测试 100% 通过
- 截图保存在 tests/e2e/screenshots/
- 测试报告生成

文件: tests/e2e/user-flow.spec.ts
验证: npm run test:e2e -- user-flow && \
      echo "✅ 用户流程 E2E 测试通过"

## TASK ##
E2E 测试：购物完整流程

**📖 背景**：
验证完整的购物流程，从浏览商品到支付完成，确保核心业务流程端到端可用。

**🔨 要做什么**：
1. 创建 tests/e2e/shopping-flow.spec.ts
2. 使用 Playwright 编写 E2E 测试：
   - 登录系统
   - 浏览商品列表
   - 点击商品查看详情
   - 加入购物车
   - 结算，创建订单
   - 选择支付方式（mock 支付）
   - 支付成功，查看订单
   - 验证订单状态为"已支付"
3. 运行 E2E 测试
4. 截图保存测试证据

**✅ 完成标志**：
- E2E 测试文件创建完成
- 测试覆盖购物完整流程（8-10 个步骤）
- 测试 100% 通过
- 截图保存
- 测试报告生成

文件: tests/e2e/shopping-flow.spec.ts
验证: npm run test:e2e -- shopping-flow && \
      echo "✅ 购物流程 E2E 测试通过，系统可以发布"
