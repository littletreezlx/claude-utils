# 电商系统开发 - DAG 执行计划
# 生成时间: 2025-11-10 16:30
# 总阶段数: 5
# 预计任务数: 15

## STAGE ## name="初始化数据库" mode="serial"
数据库表结构和基础数据必须按顺序创建，有严格依赖。

## TASK ##
创建数据库表结构

**🎯 目标**：创建用户、订单、支付、商品、购物车的数据库表

**📁 核心文件**：
- `migrations/001_create_tables.sql` - [新建] 数据库 schema

**✅ 完成标志**：
- [ ] 所有表创建成功
- [ ] `npm run migrate:check` 通过

文件: migrations/001_create_tables.sql
验证: npm run migrate:check

## TASK ##
初始化基础数据

**🎯 目标**：初始化角色、权限、系统配置、商品分类等基础数据

**📁 核心文件**：
- `migrations/002_seed_data.sql` - [新建] 种子数据

**✅ 完成标志**：
- [ ] 种子数据插入成功
- [ ] `npm run seed:verify` 通过

文件: migrations/002_seed_data.sql
验证: npm run seed:verify

## STAGE ## name="实现业务模块" mode="parallel" max_workers="2"
各业务模块独立，可以并行开发。注意：排除 src/common/ 避免冲突。

## TASK ##
实现用户管理 API

**🎯 目标**：实现注册、登录、权限验证、个人信息管理

**📁 核心文件**：
- `src/modules/user/user.service.ts` - [新建] 用户服务
- `src/modules/user/user.controller.ts` - [新建] 用户控制器
- `src/modules/user/user.entity.ts` - [新建] 用户实体

**✅ 完成标志**：
- [ ] API 端点可访问
- [ ] `npm test -- user.service.test.ts` 通过

文件: src/modules/user/**/*.ts
排除: src/common/
验证: npm test -- user.service.test.ts

## TASK ##
实现订单管理 API

**🎯 目标**：实现创建订单、查询订单、状态流转、取消订单

**📁 核心文件**：
- `src/modules/order/order.service.ts` - [新建] 订单服务
- `src/modules/order/order.controller.ts` - [新建] 订单控制器
- `src/modules/order/order.entity.ts` - [新建] 订单实体

**✅ 完成标志**：
- [ ] API 端点可访问
- [ ] `npm test -- order.service.test.ts` 通过

文件: src/modules/order/**/*.ts
排除: src/common/
验证: npm test -- order.service.test.ts

## TASK ##
实现支付集成

**🎯 目标**：实现支付宝、微信支付、回调处理、退款逻辑

**📁 核心文件**：
- `src/modules/payment/payment.service.ts` - [新建] 支付服务
- `src/modules/payment/alipay.provider.ts` - [新建] 支付宝对接
- `src/modules/payment/wechat.provider.ts` - [新建] 微信支付对接

**✅ 完成标志**：
- [ ] 支付流程可完成
- [ ] `npm test -- payment.service.test.ts` 通过

文件: src/modules/payment/**/*.ts
排除: src/common/
验证: npm test -- payment.service.test.ts

## TASK ##
实现商品管理 API

**🎯 目标**：实现商品列表、详情、库存管理、分类筛选

**📁 核心文件**：
- `src/modules/product/product.service.ts` - [新建] 商品服务
- `src/modules/product/product.controller.ts` - [新建] 商品控制器
- `src/modules/product/product.entity.ts` - [新建] 商品实体

**✅ 完成标志**：
- [ ] API 端点可访问
- [ ] `npm test -- product.service.test.ts` 通过

文件: src/modules/product/**/*.ts
排除: src/common/
验证: npm test -- product.service.test.ts

## STAGE ## name="前端页面开发" mode="parallel" max_workers="2"
前端页面可以使用 mock 数据，不强依赖后端完成。

## TASK ##
实现用户相关页面

**🎯 目标**：实现登录、注册、个人中心、订单列表页面

**📁 核心文件**：
- `src/pages/user/login.tsx` - [新建] 登录页
- `src/pages/user/register.tsx` - [新建] 注册页
- `src/pages/user/profile.tsx` - [新建] 个人中心

**✅ 完成标志**：
- [ ] 页面可访问
- [ ] `npm run lint:ui` 通过

文件: src/pages/user/**/*.tsx, src/components/user/**/*.tsx
排除: src/pages/**/*.test.tsx
验证: npm run lint:ui

## TASK ##
实现订单相关页面

**🎯 目标**：实现订单列表、订单详情、创建订单、订单跟踪页面

**📁 核心文件**：
- `src/pages/order/list.tsx` - [新建] 订单列表
- `src/pages/order/detail.tsx` - [新建] 订单详情
- `src/pages/order/create.tsx` - [新建] 创建订单

**✅ 完成标志**：
- [ ] 页面可访问
- [ ] `npm run lint:ui` 通过

文件: src/pages/order/**/*.tsx, src/components/order/**/*.tsx
排除: src/pages/**/*.test.tsx
验证: npm run lint:ui

## TASK ##
实现商品相关页面

**🎯 目标**：实现商品列表、商品详情、购物车、搜索筛选页面

**📁 核心文件**：
- `src/pages/product/list.tsx` - [新建] 商品列表
- `src/pages/product/detail.tsx` - [新建] 商品详情
- `src/pages/cart/index.tsx` - [新建] 购物车

**✅ 完成标志**：
- [ ] 页面可访问
- [ ] `npm run lint:ui` 通过

文件: src/pages/product/**/*.tsx, src/components/product/**/*.tsx
排除: src/pages/**/*.test.tsx
验证: npm run lint:ui

## STAGE ## name="集成测试" mode="serial"
集成测试需要等待后端 API 和前端页面都完成。

## TASK ##
编写用户-订单集成测试

**🎯 目标**：测试用户登录 → 浏览商品 → 创建订单流程

**📁 核心文件**：
- `tests/integration/user-order.test.ts` - [新建] 集成测试

**✅ 完成标志**：
- [ ] `npm run test:integration -- user-order` 通过

文件: tests/integration/user-order.test.ts
验证: npm run test:integration -- user-order

## TASK ##
编写订单-支付集成测试

**🎯 目标**：测试创建订单 → 发起支付 → 回调处理 → 订单状态更新

**📁 核心文件**：
- `tests/integration/order-payment.test.ts` - [新建] 集成测试

**✅ 完成标志**：
- [ ] `npm run test:integration -- order-payment` 通过

文件: tests/integration/order-payment.test.ts
验证: npm run test:integration -- order-payment

## TASK ##
编写商品-购物车集成测试

**🎯 目标**：测试添加商品 → 购物车管理 → 批量下单

**📁 核心文件**：
- `tests/integration/product-cart.test.ts` - [新建] 集成测试

**✅ 完成标志**：
- [ ] `npm run test:integration -- product-cart` 通过

文件: tests/integration/product-cart.test.ts
验证: npm run test:integration -- product-cart

## STAGE ## name="端到端测试" mode="parallel" max_workers="2"
E2E 测试场景相对独立，可以并行执行。

## TASK ##
E2E 测试：用户注册登录流程

**🎯 目标**：测试注册 → 邮箱验证 → 登录 → 个人信息完善

**✅ 完成标志**：
- [ ] `npm run test:e2e -- auth.spec.ts` 通过

验证: npm run test:e2e -- auth.spec.ts

## TASK ##
E2E 测试：完整购物流程

**🎯 目标**：测试浏览商品 → 加入购物车 → 下单 → 支付 → 完成

**✅ 完成标志**：
- [ ] `npm run test:e2e -- checkout.spec.ts` 通过

验证: npm run test:e2e -- checkout.spec.ts

## TASK ##
E2E 测试：订单管理流程

**🎯 目标**：测试查看订单 → 订单详情 → 取消订单 → 申请退款

**✅ 完成标志**：
- [ ] `npm run test:e2e -- order-management.spec.ts` 通过

验证: npm run test:e2e -- order-management.spec.ts

## TASK ##
E2E 测试：商品搜索流程

**🎯 目标**：测试关键词搜索 → 分类筛选 → 价格排序 → 查看详情

**✅ 完成标志**：
- [ ] `npm run test:e2e -- product-search.spec.ts` 通过

验证: npm run test:e2e -- product-search.spec.ts
