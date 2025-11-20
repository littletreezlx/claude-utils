# 电商系统开发 - DAG 执行计划
# 生成时间: 2025-11-10 16:30
# 总阶段数: 5
# 预计任务数: 15

## STAGE ## name="初始化数据库" mode="serial"
# 阶段说明：数据库表结构和基础数据必须按顺序创建，有严格依赖

## TASK ## id="schema" on_failure="stop"
创建数据库表结构（用户、订单、支付、商品、购物车）

文件: migrations/001_create_tables.sql
验证: npm run migrate:check

## TASK ## id="seed" depends_on="schema" on_failure="stop"
初始化基础数据（角色、权限、系统配置、商品分类）

文件: migrations/002_seed_data.sql
验证: npm run seed:verify

## STAGE ## name="实现业务模块" mode="parallel" max_workers="4" depends_on="stage:1"
# 阶段说明：各业务模块独立，可以并行开发

## TASK ## id="user-api" on_failure="continue"
实现用户管理 API（注册、登录、权限验证、个人信息管理）

文件: src/modules/user/**/*.ts
排除: src/modules/user/**/*.test.ts
排除: src/common/
验证: npm test -- user.service.test.ts

## TASK ## id="order-api" on_failure="continue"
实现订单管理 API（创建订单、查询订单、状态流转、取消订单）

文件: src/modules/order/**/*.ts
排除: src/modules/order/**/*.test.ts
排除: src/common/
验证: npm test -- order.service.test.ts

## TASK ## id="payment-api" on_failure="continue"
实现支付集成（支付宝、微信支付、回调处理、退款逻辑）

文件: src/modules/payment/**/*.ts
排除: src/modules/payment/**/*.test.ts
排除: src/common/
验证: npm test -- payment.service.test.ts

## TASK ## id="product-api" on_failure="continue"
实现商品管理 API（商品列表、详情、库存管理、分类筛选）

文件: src/modules/product/**/*.ts
排除: src/modules/product/**/*.test.ts
排除: src/common/
验证: npm test -- product.service.test.ts

## STAGE ## name="前端页面开发" mode="parallel" max_workers="3" depends_on="stage:2"
# 阶段说明：前端页面可以使用 mock 数据，不强依赖后端完成

## TASK ## id="user-ui" on_failure="continue"
实现用户相关页面（登录、注册、个人中心、订单列表）

文件: src/pages/user/**/*.tsx
文件: src/components/user/**/*.tsx
排除: src/pages/**/*.test.tsx
排除: src/components/**/*.test.tsx
验证: npm run lint:ui

## TASK ## id="order-ui" on_failure="continue"
实现订单相关页面（订单列表、订单详情、创建订单、订单跟踪）

文件: src/pages/order/**/*.tsx
文件: src/components/order/**/*.tsx
排除: src/pages/**/*.test.tsx
排除: src/components/**/*.test.tsx
验证: npm run lint:ui

## TASK ## id="product-ui" on_failure="continue"
实现商品相关页面（商品列表、商品详情、购物车、搜索筛选）

文件: src/pages/product/**/*.tsx
文件: src/components/product/**/*.tsx
排除: src/pages/**/*.test.tsx
排除: src/components/**/*.test.tsx
验证: npm run lint:ui

## STAGE ## name="集成测试" mode="serial" depends_on="stage:2,stage:3"
# 阶段说明：集成测试需要等待后端 API 和前端页面都完成

## TASK ## id="integration-user-order" depends_on="user-api,order-api" on_failure="retry" retry="2"
编写用户-订单集成测试（用户登录 → 浏览商品 → 创建订单流程）

文件: tests/integration/user-order.test.ts
验证: npm run test:integration -- user-order

## TASK ## id="integration-order-payment" depends_on="order-api,payment-api" on_failure="retry" retry="2"
编写订单-支付集成测试（创建订单 → 发起支付 → 回调处理 → 订单状态更新）

文件: tests/integration/order-payment.test.ts
验证: npm run test:integration -- order-payment

## TASK ## id="integration-product-cart" depends_on="product-api,order-api" on_failure="retry" retry="2"
编写商品-购物车集成测试（添加商品 → 购物车管理 → 批量下单）

文件: tests/integration/product-cart.test.ts
验证: npm run test:integration -- product-cart

## STAGE ## name="端到端测试" mode="parallel" max_workers="3" depends_on="stage:4"
# 阶段说明：E2E 测试场景相对独立，可以并行执行

## TASK ## id="e2e-auth" on_failure="retry" retry="3"
E2E 测试：用户注册登录流程（注册 → 邮箱验证 → 登录 → 个人信息完善）

验证: npm run test:e2e -- auth.spec.ts

## TASK ## id="e2e-checkout" on_failure="retry" retry="3"
E2E 测试：完整购物流程（浏览商品 → 加入购物车 → 下单 → 支付 → 完成）

验证: npm run test:e2e -- checkout.spec.ts

## TASK ## id="e2e-order-mgmt" on_failure="retry" retry="3"
E2E 测试：订单管理流程（查看订单 → 订单详情 → 取消订单 → 申请退款）

验证: npm run test:e2e -- order-management.spec.ts

## TASK ## id="e2e-product-search" on_failure="retry" retry="3"
E2E 测试：商品搜索流程（关键词搜索 → 分类筛选 → 价格排序 → 查看详情）

验证: npm run test:e2e -- product-search.spec.ts
