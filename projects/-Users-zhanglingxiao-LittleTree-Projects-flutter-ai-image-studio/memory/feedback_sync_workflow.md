---
name: Backend Sync Workflow
description: 后端项目同步到 windows 的方式：git push 而非 SSH/SCP，用户在 windows 上 pull
type: feedback
---

修改 ai-image-engine 等需要同步到 windows 的项目时，不要尝试 SSH/SCP 直接同步文件。

**Why:** SSH/SCP 到 windows 不稳定（shell 输出干扰、rsync 协议错误），且用户更希望走 git 流程。

**How to apply:** 修改后 git commit → git push，然后通知用户去 windows 上 git pull。
