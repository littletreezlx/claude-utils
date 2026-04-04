# 数据迁移项目 - DAG 执行计划

> **项目宏观目标**：
> 将旧系统数据安全迁移到新系统，确保数据完整性和一致性

## STAGE ## name="数据备份" mode="serial"
备份必须在所有迁移之前完成，且必须串行确保完整性。

## TASK ##
备份生产数据库

**目标**：完整备份生产数据库（表结构 + 数据），验证备份可恢复

**核心文件**：
- `backup/prod-YYYYMMDD.sql` - [生成] 完整备份文件

**完成标志**：
- [ ] 备份文件已生成
- [ ] 备份文件大小合理（非空）
- [ ] 恢复测试通过

验证: test -f backup/prod-*.sql && ls -lh backup/prod-*.sql

## STAGE ## name="迁移脚本开发" mode="parallel" max_workers="4"
各数据表的迁移脚本可以独立开发，无文件依赖。

## TASK ##
编写用户数据迁移脚本

**目标**：迁移用户表、角色表、权限表到新 schema

**核心文件**：
- `migrations/users/migrate.ts` - [新建] 迁移脚本
- `migrations/users/verify.ts` - [新建] 验证脚本

**完成标志**：
- [ ] 迁移脚本可执行
- [ ] 单元测试通过

文件: migrations/users/**/*.ts
验证: npm test -- migrations/users

## TASK ##
编写订单数据迁移脚本

**目标**：迁移订单表、订单明细表、物流信息表到新 schema

**核心文件**：
- `migrations/orders/migrate.ts` - [新建] 迁移脚本
- `migrations/orders/verify.ts` - [新建] 验证脚本

**完成标志**：
- [ ] 迁移脚本可执行
- [ ] 单元测试通过

文件: migrations/orders/**/*.ts
验证: npm test -- migrations/orders

## TASK ##
编写商品数据迁移脚本

**目标**：迁移商品表、库存表、分类表到新 schema

**核心文件**：
- `migrations/products/migrate.ts` - [新建] 迁移脚本

**完成标志**：
- [ ] 迁移脚本可执行
- [ ] 单元测试通过

文件: migrations/products/**/*.ts
验证: npm test -- migrations/products

## TASK ##
编写支付数据迁移脚本

**目标**：迁移支付记录表、退款记录表到新 schema

**核心文件**：
- `migrations/payments/migrate.ts` - [新建] 迁移脚本

**完成标志**：
- [ ] 迁移脚本可执行
- [ ] 单元测试通过

文件: migrations/payments/**/*.ts
验证: npm test -- migrations/payments

## STAGE ## name="测试环境迁移" mode="serial"
测试环境迁移必须串行，验证数据一致性和完整性。注意执行顺序：用户/商品先行，订单依赖两者，支付依赖订单。

## TASK ##
在测试环境执行用户数据迁移

**目标**：运行用户迁移脚本并验证数据一致性

**输入依赖**：
- ⬆️ 迁移脚本开发阶段的 migrations/users/

**完成标志**：
- [ ] 迁移执行成功
- [ ] 数据验证通过

验证: npm run migrate:test -- users && npm run verify:test -- users

## TASK ##
在测试环境执行商品数据迁移

**目标**：运行商品迁移脚本并验证数据一致性

**完成标志**：
- [ ] 迁移执行成功
- [ ] 数据验证通过

验证: npm run migrate:test -- products && npm run verify:test -- products

## TASK ##
在测试环境执行订单数据迁移

**目标**：运行订单迁移脚本并验证数据一致性（依赖用户和商品数据已迁移）

**输入依赖**：
- ⬆️ 用户数据已迁移
- ⬆️ 商品数据已迁移

**完成标志**：
- [ ] 迁移执行成功
- [ ] 数据验证通过（含外键关联）

验证: npm run migrate:test -- orders && npm run verify:test -- orders

## TASK ##
在测试环境执行支付数据迁移

**目标**：运行支付迁移脚本并验证数据一致性（依赖订单数据已迁移）

**输入依赖**：
- ⬆️ 订单数据已迁移

**完成标志**：
- [ ] 迁移执行成功
- [ ] 数据验证通过

验证: npm run migrate:test -- payments && npm run verify:test -- payments

## STAGE ## name="生产环境迁移" mode="serial"
生产环境迁移必须串行，需要人工确认每一步。

## TASK ##
在生产环境执行数据迁移

**目标**：按照测试环境验证过的顺序执行生产迁移

**完成标志**：
- [ ] 所有表迁移成功
- [ ] 全量数据验证通过

验证: npm run migrate:prod && npm run verify:prod

## STAGE ## name="review" mode="serial"

## TASK ##
全局审视与收尾

**目标**：纵观所有迁移阶段产出，整体梳理，将剩余工作记录到 TODO.md

**执行步骤**：
1. 回顾所有阶段的迁移结果和数据验证报告
2. 评估整体完成度：所有数据是否完整迁移？
3. 记录关键决策和遇到的问题
4. 自问：还有什么数据未迁移？还有什么风险需要关注？
5. **直接写入项目根目录 TODO.md**（不依赖 /todo-write），包含迁移摘要、遗留数据、下一步行动项

**⚠️ 重要**：你没有前序任务的会话历史，必须通过 `git log`、`git diff --stat` 和文件系统自行发现前序产出。

**完成标志**：
- [ ] TODO.md 已写入项目根目录且包含遗留事项和下一步行动

文件: TODO.md
验证: test -f TODO.md && grep -c "\- \[ \]" TODO.md
