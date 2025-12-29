# 项目结构优化实施计划

> **目标**：统一配置文件、精简根目录、清理遗留代码
> **风险等级**：低-中
> **预计时间**：30-45 分钟

---

## 执行摘要

基于深度分析，建议执行以下优化（按风险从低到高排序）：

| 阶段 | 任务 | 风险 | 时间 |
|------|------|------|------|
| 1 | 清理遗留测试文件 | 极低 | 2min |
| 2 | 删除未使用的 src/wechat-auth/ | 极低 | 1min |
| 3 | 合并 transcription/ 到 ai/ | 低 | 5min |
| 4 | 统一配置文件位置 | 中 | 20min |
| 5 | ~~精简根目录脚本~~ | ~~高~~ | **跳过** |

**注意**：根目录脚本（dev.sh, stop.sh 等）建议**保留原位**，原因：
- 文档中有 123 处引用
- 当前已是包装器模式，逻辑已分离
- 用户习惯已形成

---

## Phase 1: 清理遗留测试文件

### 操作
```bash
# 创建归档目录
mkdir -p tests/.archive/2025-01-legacy
mkdir -p tests/.archive/2025-01-archive

# 移动遗留文件
mv tests/legacy/* tests/.archive/2025-01-legacy/ 2>/dev/null || true
mv tests/archive/* tests/.archive/2025-01-archive/ 2>/dev/null || true

# 删除空目录
rmdir tests/legacy 2>/dev/null || true
rmdir tests/archive 2>/dev/null || true
```

### 影响文件
- `tests/legacy/` → `tests/.archive/2025-01-legacy/`
- `tests/archive/` → `tests/.archive/2025-01-archive/`

### 验证
```bash
./scripts/test.sh e2e  # 确保测试仍然通过
```

---

## Phase 2: 删除未使用的 src/wechat-auth/

### 前置检查
```bash
grep -r "wechat-auth" src/ app/  # 应该无结果
```

### 操作
```bash
rm -rf src/wechat-auth/
```

### 影响文件
- 删除 `src/wechat-auth/types.ts`（经确认无任何引用）

### 验证
```bash
pnpm build  # TypeScript 编译通过
```

---

## Phase 3: 合并 transcription/ 到 ai/

### 操作
```bash
# 移动服务文件
mv nodejs-service/src/transcription/transcription-service.ts \
   nodejs-service/src/ai/transcription-service.ts

# 删除空目录
rmdir nodejs-service/src/transcription/
```

### 需要更新的导入
**文件**: `nodejs-service/src/routes/transcription.ts`
```typescript
// 从
import { TranscriptionService } from '../transcription/transcription-service.js'
// 改为
import { TranscriptionService } from '../ai/transcription-service.js'
```

### 验证
```bash
cd nodejs-service && pnpm build  # 编译通过
```

---

## Phase 4: 统一配置文件位置

### 目标结构
```
deployment/environments/
├── .env.base      # 基础配置（新建，内容来自根目录 .env）
├── .env.dev       # 开发环境（已存在，合并根目录 .env.dev）
├── .env.test      # 测试环境（已存在）
├── .env.prod      # 生产环境（已存在）
└── .env.template  # 配置模板（已存在）

根目录/
├── .env           # 符号链接 → deployment/environments/.env.base
├── .env.dev       # 符号链接 → deployment/environments/.env.dev
└── .env.test      # 符号链接 → deployment/environments/.env.test
```

### 步骤 4.1: 备份现有配置
```bash
cp .env .env.backup
cp .env.dev .env.dev.backup
cp .env.test .env.test.backup
```

### 步骤 4.2: 合并配置到统一位置
```bash
# 将根目录 .env 移动为 .env.base
mv .env deployment/environments/.env.base

# 合并 .env.dev 内容
cat .env.dev >> deployment/environments/.env.dev.new
# 手动检查去重后替换

# 合并 pythonapi/.env.prod 到主配置
cat pythonapi/.env.prod >> deployment/environments/.env.prod
# 手动检查去重
```

### 步骤 4.3: 创建符号链接
```bash
ln -sf deployment/environments/.env.base .env
ln -sf deployment/environments/.env.dev .env.dev
ln -sf deployment/environments/.env.test .env.test
```

### 步骤 4.4: 更新配置加载代码

**文件 1**: `src/config/environment.ts`
- 无需修改（符号链接保持向后兼容）

**文件 2**: `pythonapi/run.py` (如有直接路径引用)
- 检查是否硬编码了 `.env.prod` 路径
- 如有，更新为 `deployment/environments/.env.prod`

**文件 3**: `deployment/scripts/start-dev.sh`
- 检查环境变量加载逻辑
- 确保使用 `$PROJECT_ROOT/.env` （符号链接会自动解析）

### 步骤 4.5: 删除冗余配置
```bash
rm pythonapi/.env.prod  # 已合并到 deployment/environments/.env.prod
rm .env.test.local      # 如不再需要
```

### 验证
```bash
# 1. 检查符号链接
ls -la .env*

# 2. 启动开发环境
./dev.sh

# 3. 检查配置加载
curl http://localhost:61001/api/health  # 后端健康检查

# 4. 运行测试
./scripts/test.sh e2e --auto
```

---

## Phase 5: 根目录脚本处理（跳过）

### 原因
- `dev.sh`, `stop.sh`, `deploy.sh`, `docker-test.sh` 已是包装器模式
- 文档中有 123 处引用，移动成本过高
- 当前结构清晰，无需改动

### 替代建议
- 保持根目录 4 个脚本不变
- 实际逻辑已在 `deployment/scripts/` 和 `scripts/core/`

---

## 回滚方案

### 配置文件回滚
```bash
# 删除符号链接
rm .env .env.dev .env.test

# 恢复备份
mv .env.backup .env
mv .env.dev.backup .env.dev
mv .env.test.backup .env.test
```

### 代码文件回滚
```bash
git checkout -- src/
git checkout -- nodejs-service/src/
```

---

## 关键文件清单

### 需要修改的文件
| 文件 | 变更类型 |
|------|---------|
| `nodejs-service/src/routes/transcription.ts` | 更新 import 路径 |
| `deployment/environments/.env.base` | 新建（从根目录移动） |
| `deployment/environments/.env.dev` | 合并内容 |
| `deployment/environments/.env.prod` | 合并 pythonapi 配置 |

### 需要删除的文件/目录
| 路径 | 原因 |
|------|------|
| `src/wechat-auth/` | 未使用的类型定义 |
| `tests/legacy/` | 遗留测试（归档） |
| `tests/archive/` | 过时测试（归档） |
| `nodejs-service/src/transcription/` | 合并到 ai/ |
| `pythonapi/.env.prod` | 合并到统一位置 |

### 需要创建的符号链接
| 链接 | 目标 |
|------|------|
| `.env` | `deployment/environments/.env.base` |
| `.env.dev` | `deployment/environments/.env.dev` |
| `.env.test` | `deployment/environments/.env.test` |

---

## 执行顺序检查清单

- [ ] Phase 1: 归档遗留测试文件
- [ ] Phase 2: 删除 src/wechat-auth/
- [ ] Phase 3: 合并 transcription/ 到 ai/
- [ ] Phase 4.1: 备份配置文件
- [ ] Phase 4.2: 合并配置内容
- [ ] Phase 4.3: 创建符号链接
- [ ] Phase 4.4: 更新代码引用（如需要）
- [ ] Phase 4.5: 删除冗余配置
- [ ] 最终验证: ./dev.sh + ./scripts/test.sh e2e
