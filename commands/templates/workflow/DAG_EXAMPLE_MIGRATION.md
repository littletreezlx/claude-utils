# 数据迁移项目 - DAG 执行计划
# 生成时间: 2025-11-10 16:35
# 总阶段数: 4
# 预计任务数: 10

## STAGE ## name="数据备份" mode="serial"
# 阶段说明：备份必须在所有迁移之前完成，且必须串行确保完整性

## TASK ## id="backup-prod" on_failure="stop"
备份生产数据库（完整备份，包含表结构和数据）

验证: test -f backup/prod-$(date +%Y%m%d).sql && ls -lh backup/prod-*.sql

## TASK ## id="backup-verify" depends_on="backup-prod" on_failure="stop"
验证备份文件完整性（校验文件大小和可恢复性）

验证: mysql -u root -p < backup/prod-$(date +%Y%m%d).sql --dry-run

## STAGE ## name="迁移脚本开发" mode="parallel" max_workers="4" depends_on="stage:1"
# 阶段说明：各个数据表的迁移脚本可以独立开发

## TASK ## id="user-migration" on_failure="continue"
编写用户数据迁移脚本（用户表、角色表、权限表）

文件: migrations/users/**/*.ts
验证: npm test -- migrations/users

## TASK ## id="order-migration" on_failure="continue"
编写订单数据迁移脚本（订单表、订单明细表、物流信息表）

文件: migrations/orders/**/*.ts
验证: npm test -- migrations/orders

## TASK ## id="product-migration" on_failure="continue"
编写商品数据迁移脚本（商品表、库存表、分类表）

文件: migrations/products/**/*.ts
验证: npm test -- migrations/products

## TASK ## id="payment-migration" on_failure="continue"
编写支付数据迁移脚本（支付记录表、退款记录表）

文件: migrations/payments/**/*.ts
验证: npm test -- migrations/payments

## STAGE ## name="测试环境迁移" mode="serial" depends_on="stage:2"
# 阶段说明：测试环境迁移必须串行，验证数据一致性和完整性

## TASK ## id="test-migrate-users" depends_on="user-migration" on_failure="stop"
在测试环境执行用户数据迁移

验证: npm run migrate:test -- users && npm run verify:test -- users

## TASK ## id="test-migrate-products" depends_on="product-migration" on_failure="stop"
在测试环境执行商品数据迁移

验证: npm run migrate:test -- products && npm run verify:test -- products

## TASK ## id="test-migrate-orders" depends_on="order-migration,test-migrate-users,test-migrate-products" on_failure="stop"
在测试环境执行订单数据迁移（依赖用户和商品数据）

验证: npm run migrate:test -- orders && npm run verify:test -- orders

## TASK ## id="test-migrate-payments" depends_on="payment-migration,test-migrate-orders" on_failure="stop"
在测试环境执行支付数据迁移（依赖订单数据）

验证: npm run migrate:test -- payments && npm run verify:test -- payments

## STAGE ## name="生产环境迁移" mode="serial" depends_on="stage:3"
# 阶段说明：生产环境迁移必须串行，需要人工确认每一步

## TASK ## id="prod-migration" on_failure="stop"
在生产环境执行数据迁移（需人工确认每个步骤）

验证: npm run migrate:prod && npm run verify:prod
