# 配置管理和目录结构优化方案

## 目标
1. 精简 .env 文件（7个 → 4个），移回根目录
2. 删除 `deployment/environments/` 目录
3. 将 `deployment/scripts/` 整合到 `scripts/deploy/`

---

## 最终目录结构

```
nas-server/
├── .env                    # 基础配置（原 .env.base）
├── .env.dev                # 开发环境覆盖
├── .env.prod               # 生产环境覆盖
├── .env.test               # 测试环境覆盖（合并后）
├── deployment/
│   └── docker/             # 只保留 Docker 配置
│       ├── Dockerfile.*
│       └── docker-compose*.yml
└── scripts/
    ├── core/               # 现有
    ├── deploy/             # 新增：部署脚本
    │   ├── start-dev.sh
    │   ├── start-prod.sh
    │   ├── stop-prod.sh
    │   ├── deploy-all-to-nas.sh
    │   ├── deploy-on-nas.sh
    │   └── local-docker-test.sh
    └── ...                 # 其他现有目录
```

---

## 实施步骤

### 阶段 1: 迁移 .env 文件到根目录

```bash
# 1.1 删除符号链接
rm .env .env.dev .env.test

# 1.2 复制文件到根目录
cp deployment/environments/.env.base .env
cp deployment/environments/.env.dev .env.dev
cp deployment/environments/.env.prod .env.prod

# 1.3 合并测试配置
# 将 .env.test + .env.test.dev + .env.test.local 合并为 .env.test

# 1.4 删除孤立文件
rm .env.test.local

# 1.5 清理 environments 目录
rm -rf deployment/environments/
```

### 阶段 2: 整合脚本目录

```bash
# 2.1 创建目标目录
mkdir -p scripts/deploy

# 2.2 移动脚本
mv deployment/scripts/*.sh scripts/deploy/

# 2.3 删除空目录
rm -rf deployment/scripts/
```

### 阶段 3: 更新引用

| 文件 | 修改内容 |
|------|----------|
| `dev.sh` | `./deployment/scripts/start-dev.sh` → `./scripts/deploy/start-dev.sh` |
| `deploy.sh` | `./deployment/scripts/deploy-all-to-nas.sh` → `./scripts/deploy/deploy-all-to-nas.sh` |
| `docker-test.sh` | `./deployment/scripts/local-docker-test.sh` → `./scripts/deploy/local-docker-test.sh` |
| `scripts/deploy/deploy-all-to-nas.sh` | `ENV_FILE` 路径改为 `.env.prod` |
| `scripts/deploy/start-prod.sh` | `ENV_FILE` 路径更新 |

### 阶段 4: 更新文档

- `CLAUDE.md` - 如有必要
- `deployment/README.md` - 更新说明

### 阶段 5: 验证

```bash
./dev.sh                           # 开发环境启动
./scripts/test.sh e2e              # E2E 测试
./scripts/deploy/local-docker-test.sh  # Docker 测试
```

---

## 关键文件清单

**需要修改**：
- `/dev.sh` - 更新脚本路径
- `/deploy.sh` - 更新脚本路径
- `/docker-test.sh` - 更新脚本路径
- `/scripts/deploy/deploy-all-to-nas.sh` - 更新 ENV_FILE 路径
- `/scripts/deploy/start-prod.sh` - 更新 ENV_FILE 路径

**需要创建**：
- `/scripts/deploy/` - 新目录
- `/.env.test` - 合并后的测试配置

**需要删除**：
- `/deployment/environments/` - 整个目录
- `/deployment/scripts/` - 移动后删除
- `/.env.test.local` - 合并后删除

---

## 注意事项

1. **模块级 .env.example 保持不变**
   - `pythonapi/services/bili/tests/.env.example`
   - `src/rss/config/.env.example`
   - 这些是模块特定的使用示例，不需要移动

2. **startup-utils.sh 无需修改**
   - 已使用相对路径 `.env` 加载配置
   - 只要 .env 在根目录即可正常工作
