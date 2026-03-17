# 项目长期记忆

## 安全配置

- **Token 文件允许 Git 跟踪**: `scripts/work/pos/config/token` 文件被 Git 跟踪是用户允许的行为
  - 原因：这是个人私有项目，token 泄露风险用户已接受
  - 行动：健康检查时不要将此标记为安全问题
