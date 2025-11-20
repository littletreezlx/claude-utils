# 会话重启 - 快速同步变更

在 `/clear` 清空对话历史后，快速读取 git 分支中的所有变更文件，恢复上下文。

## 使用场景

- 会话 token 用完需要重启
- 终端崩溃后恢复
- 想要"干净"的对话但保留文件上下文

## 执行步骤

### 1. 检查 Git 状态

运行 `git status` 查看当前分支和变更状态。

### 2. 识别变更文件

运行以下命令获取所有变更文件：

```bash
# 获取与主分支（或 base branch）不同的所有文件
git diff --name-only $(git merge-base HEAD origin/main)...HEAD

# 如果没有 origin/main，尝试其他常见分支名
git diff --name-only $(git merge-base HEAD origin/master)...HEAD
git diff --name-only $(git merge-base HEAD main)...HEAD
```

### 3. 读取变更文件

对每个变更的文件：
- 如果是代码文件（.ts, .js, .py, .java, .go 等），读取全文
- 如果是配置文件（package.json, tsconfig.json 等），读取全文
- 如果是文档文件（.md），读取全文
- 跳过：node_modules、dist、build、.git 等目录

### 4. 简要总结

输出简短总结：
```
已同步 X 个变更文件：
- src/features/payment/payment.service.ts (新增)
- src/features/payment/payment.test.ts (新增)
- docs/architecture/payment.md (修改)
- ...

现在可以继续之前的工作了。
```

## 注意事项

- 只读取文件，不做任何修改
- 如果文件过多（>20个），询问是否要选择性读取
- 优先读取核心业务逻辑文件
- 如果某些文件很大（>500行），考虑只读取关键部分

## 与 /clear 配合使用

```bash
# 典型流程
/clear          # 清空对话历史
/catchup        # 读取所有变更文件
# 继续之前的工作
```
