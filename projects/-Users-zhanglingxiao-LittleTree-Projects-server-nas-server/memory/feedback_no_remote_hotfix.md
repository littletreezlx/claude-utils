---
name: 禁止远程热修改
description: 不要直接 docker cp/sed 修改 NAS 容器中的文件，走正常部署流程
type: feedback
---

不要直接修改 NAS 上运行容器中的编译产物（docker cp/sed 等热修方式）。

**Why:** 太麻烦且不可靠——尤其是 Node.js 服务需要 TS 编译，直接改 JS 不现实。

**How to apply:** 在本地修复代码、跑测试、提交，让用户走 `deploy.sh` 正常部署。只有 `.env` 等配置文件可以远程直接改。
