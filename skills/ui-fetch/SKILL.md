---
name: ui-fetch
description: >
  Downloads a Claude Design bundle ZIP from share URLs (pattern:
  api.anthropic.com/v1/design/h/<id>?open_file=<file>), unzips to
  .claude-design-inbox/, and reports contents with suggested next action.
  Triggers on the URL pattern, Claude Design's standard hand-off prompt
  "Fetch this design file", or Chinese phrases like "拉这份 bundle" /
  "下载这份 claude-design" / "入库这份 bundle". Does NOT auto-execute
  /ui-vs / /ui-adopt / /ui-bootstrap or auto-overwrite docs/design/HANDOFF.md
  — those require explicit Founder action.
version: 0.1.0
---

# UI Fetch — Claude Design Bundle 下载器

## 目的

Claude Design 的 share URL(`api.anthropic.com/v1/design/h/<id>?open_file=<file>`)本质是该轮 export bundle 的 **ZIP 下载链接**(非 HTML、非 API endpoint)。本 skill 把"下载 + 解压"这段机械流程标准化为自动入口,避免 Founder 手动操作出错。

**只做轻量路由,不做决策**:Phase 3 只给建议,Founder 确认后才走 `/ui-vs` / `/ui-adopt` / `/ui-bootstrap` 或入库 HANDOFF.md。

## 触发

**强匹配(必触发)**:
- URL 含 `api.anthropic.com/v1/design/h/`
- 消息开头是 `Fetch this design file`(Claude Design 标准 handoff 模板)

**弱匹配(建议触发)**:
- "拉这份 bundle" / "下载这份 claude-design" / "入库这份 bundle"
- 消息以 `Implement: <filename>` 结尾

**不触发**:
- URL 是 `claude.ai/design/p/<id>`(project 管理页,不是 bundle 下载)
- 用户只是讨论 URL 没让入库

## 流程

### Phase 0: 准备

1. 校验 `curl` + `unzip` 可用
2. 确保 `.claude-design-inbox/` 存在,且根 `.gitignore` 已排除(同 `/ui-bootstrap` Phase 0 逻辑,缺失则补)
3. Inbox 已有旧内容 → **暂停询问**:"上轮残留还在,清空 / 保留 / 看一下?"

### Phase 1: 解析 URL

从用户消息里抽:

- `<URL>`: 完整 URL
- `<open_file>`: `?open_file=` 参数值(若有)
- `<implement_file>`: `Implement: <file>` 字段(若有,来自 Claude Design 标准模板)

URL 格式不符(缺 `api.anthropic.com/v1/design/h/` 段) → 停,提示 Founder 贴正确格式。

### Phase 2: 下载 + 解压

```bash
curl -fL --retry 2 --max-time 60 -o .claude-design-inbox/bundle.zip "<URL>"
unzip -o .claude-design-inbox/bundle.zip -d .claude-design-inbox/
rm .claude-design-inbox/bundle.zip
```

**错误处理**(给清晰可操作的信息):

- **404 / 410** → "URL 已过期。Claude Design 的 share URL 短期失效,回 Claude Design 重新拿一份。"
- **401 / 403** → "URL 需要认证。本 skill 暂未实现认证路径,等产品层确认后再补。"
- **解压失败** → "下载的内容不是有效 ZIP。可能返回的是错误页(URL 过期或项目访问受限)。"
- **网络超时** → "网络问题,重试或检查代理。"
- **其他** → 原样报 curl / unzip exit code,不猜原因。

### Phase 3: 报告 + 建议

**不执行任何后续动作**。输出:

1. Inbox 根目录文件清单 + bundle SHA256(前 12 位) + 总大小
2. 按 `<open_file>` 给建议:

| open_file | 建议下一步 |
|---|---|
| `HANDOFF.md` | "入库 HANDOFF:`.claude-design-inbox/HANDOFF.md` → `docs/design/HANDOFF.md`(整文件覆写)。入库后按协议处理 TASK(Pending 段空则只入库)。" |
| `{Name}.html`(primary design file) | 视项目状态:<br>• 无 `docs/design/EXTERNAL_REFS.md` → `/ui-bootstrap`<br>• 有 → 问 Founder:本轮要评审 `/ui-vs` / 采纳 `/ui-adopt` / 已评审完只要落代码(pixel-perfect recreate) |
| `styles.css` / `*.jsx` | 同 HTML 路径,但通常入口是 HTML |
| 无 `open_file` 参数 | 列清单,让 Founder 手动选入口 |

3. Inbox 若含 `.gitignore` / `README.md`(inbox 模板污染,同 `/ui-bootstrap` Gotcha) → 提醒 Founder,归档时需删除

## 关键约束

- **不自动跑 `/ui-vs` / `/ui-adopt` / `/ui-bootstrap`**:这些是重动作,Founder 必须显式触发
- **不自动覆写 `docs/design/HANDOFF.md`**:即使 `open_file=HANDOFF.md` 也只建议,避免误触
- **不自动清理 inbox 旧内容**:先询问再动
- **不猜认证 header**:遇 401/403 暂停,等产品层澄清
- **URL 过期是常态,不是 bug**:错误信息里要明确说"回 Claude Design 重拿",别让 Founder 以为是自己贴错
- **只负责"下载 + 解压 + 报告"**,不承担 drift 诊断 / 设计系统抽取 / TASK 识别 —— 那是 `/ui-bootstrap` / `/ui-vs` / `/ui-adopt` 的事

## 和其他工作流的关系

```text
Founder 贴 URL  →  ui-fetch(本 skill)  →  inbox 有内容
                                              ↓
                       Founder 根据建议选下一步:
                       ├─ /ui-bootstrap     (首次接入)
                       ├─ /ui-vs            (评审)
                       ├─ /ui-adopt         (采纳反哺)
                       └─ 直接入库 HANDOFF  → 按协议处理 TASK
```

## Gotchas

- **同一 URL 二次下载**:若 inbox 已有相同 SHA256 的 bundle,提示"内容无变化,要跳过解压吗"(复用 `/ui-bootstrap` Phase 0.3 的去重逻辑)
- **share URL 每轮变**:Founder 每次迭代 Claude Design 后在它那边拿到新 URL,旧 URL 立即失效。报错时别误导 Founder 以为是自己写错
- **两种 Claude Design URL 易混淆**:
  - `claude.ai/design/p/<id>` = project 管理页(浏览器访问,不可下载 bundle)
  - `api.anthropic.com/v1/design/h/<id>` = bundle ZIP 下载链接(本 skill 要的)
- **`open_file` 参数可能拼错**:Claude Design 偶尔给错参数,导致 inbox 解压后找不到该文件。这种情况 Phase 3 只列清单、不报错,让 Founder 自己挑
- **本 skill 是新产物(2026-04 起)**:早期路由表可能不够完善,跑 3-5 轮实战后再扩展 Phase 3 的建议表
