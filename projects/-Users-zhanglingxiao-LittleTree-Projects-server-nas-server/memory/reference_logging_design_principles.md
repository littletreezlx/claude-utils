---
name: 日志系统设计原则（多服务架构）
description: 搭建或审查多服务项目日志系统时参考的设计原则，来自 NAS Server 项目实践
type: reference
---

## 核心原则

1. **控制台给人看，文件给机器读** — 控制台保持各框架原生可读格式（colorize、pretty-print），文件输出用统一 JSON schema。这是正确的分层，不要试图统一控制台格式。

2. **每个服务必须有日志文件** — 只输出到终端的日志对 AI 不可见。新增服务时第一件事确认文件输出存在。

3. **多服务统一文件 schema** — 一个解析器读所有日志。推荐短 key 节省空间：`ts`(ISO时间), `l`(级别缩写), `s`(服务名), `m`(模块), `msg`(消息), `data`(可选结构化数据)。

4. **AI 需要一条命令看全局错误** — 类似 `log-check.sh` 的聚合脚本，支持 errors/all/grep 模式。这是 AI 排查问题的第一入口。

5. **启动日志降噪** — 抑制第三方包噪音（npm warn、dotenv tip、nodemon 模板）、健康检查探针日志、重复初始化日志。级别缩写 `[I]/[E]/[W]` 节省水平空间。

## 实践要点

- Next.js `createLogger` 的 server/client 自动选择：用 `typeof window === 'undefined'` + 动态 `require` 避免 Turbopack 打包 Winston 进客户端
- Pino 自定义 file transport 必须用 CJS 格式（worker thread 不支持 ESM）
- Python `logging.getLogger(__name__)` 不会继承自定义 Formatter — 必须用项目的 UnifiedLogger
- Fastify 内置 logger 默认只输出到控制台 — 需要显式配置 file transport
