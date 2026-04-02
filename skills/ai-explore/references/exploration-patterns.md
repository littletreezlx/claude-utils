# 启发式探索模式库

## 模式 1: 跨端点一致性验证

```bash
# 1. 读取关联数据
groups=$(curl -s localhost:$PORT/data/groups)
options=$(curl -s localhost:$PORT/data/options?groupId=<id>)

# 2. 交叉验证
# - group.optionCount 是否等于 options 数组长度？
# - option.groupId 是否都指向同一个 group？
# - 删除 group 后，orphan options 是否被清理？
```

## 模式 2: CRUD 完整性

对每种实体，按顺序测试：
```
Create → Read(验证已创建) → Update(如有) → Read(验证已更新) → Delete → Read(验证已删除)
```

**关键检查点**：
- Create 后返回值是否包含新 ID？
- Delete 后关联数据是否级联清理？
- 边界：名称为空、超长（100字符）、特殊字符（emoji、换行符）

## 模式 3: 状态机验证

适用于有状态流转的功能：
```
初始状态 → 操作A → 验证中间状态 → 操作B → 验证最终状态
                                    ↓ 
                              异常操作（在中间状态执行非法操作）
                                    ↓
                              验证错误处理是否正确
```

## 模式 4: 并发/快速操作

```bash
# 快速连续执行同一操作
for i in 1 2 3; do
  curl -X POST localhost:$PORT/action/xxx -d '...' &
done
wait

# 检查最终状态是否一致
curl -s localhost:$PORT/data/xxx
```

## 模式 5: 非快乐路径重放

基于 user-stories 的步骤，在中间注入意外：
- 执行完 Step 2 后删除 Step 1 创建的数据，继续 Step 3
- 在操作前清空所有数据
- 重复执行同一 Step 3 次

## 异常信号识别

| 信号 | 含义 | 行动 |
|------|------|------|
| 空数组 `[]` 但期望有数据 | 数据未加载/未持久化 | 检查 Repository 和 DAO |
| `null` 字段但应有值 | 数据映射遗漏 | 检查 Entity → JSON 转换 |
| count 不匹配 | 缓存/数据库不同步 | 对比 /state/ 和 /data/ |
| action 成功但数据未变 | 事务未提交/Stream 未刷新 | 检查 Repository.save() |
| 重复 ID | 主键冲突或 upsert 逻辑问题 | 检查 DAO insert 方法 |
