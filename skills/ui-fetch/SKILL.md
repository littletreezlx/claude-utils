---
name: ui-fetch
description: >
  Downloads a Claude Design bundle from share URLs (pattern:
  api.anthropic.com/v1/design/h/<id>?open_file=<file>) and extracts to
  .claude-design-inbox/, then reports contents with suggested next action.
  The "bundle" is a gzipped tar archive (.tar.gz), NOT a ZIP — common mistake.
  Triggers on the URL pattern, Claude Design's standard hand-off prompt
  "Fetch this design file", or Chinese phrases like "拉这份 bundle" /
  "下载这份 claude-design" / "入库这份 bundle". Does NOT auto-execute
  /ui-vs / /ui-adopt / /ui-bootstrap or auto-overwrite docs/design/HANDOFF.md
  — those require explicit Founder action.
version: 0.2.0
---

# UI Fetch — Claude Design Bundle 下载器

## 目的

Claude Design 的 share URL(`api.anthropic.com/v1/design/h/<id>?open_file=<file>`)本质是该轮 export bundle 的**下载链接**。下载下来的是 **gzipped tar 归档**(`.tar.gz`,非 ZIP),解压后是 `<project-slug>/project/<files>` 两层嵌套结构。

本 skill 把"下载 + 解压 + 识别结构"这段机械流程标准化,避免 Founder 手动操作或 AI 凭直觉猜格式出错。

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

1. 校验 `curl` + `tar` 可用(`unzip` 作为 fallback,见 Phase 2)
2. 确保 `.claude-design-inbox/` 存在,且根 `.gitignore` 已排除(同 `/ui-bootstrap` Phase 0 逻辑,缺失则补)
3. Inbox 已有旧内容 → **暂停询问**:"上轮残留还在,清空 / 保留 / 看一下?"

### Phase 1: 解析 URL

从用户消息里抽:

- `<URL>`: 完整 URL
- `<open_file>`: `?open_file=` 参数值(若有)
- `<implement_file>`: `Implement: <file>` 字段(若有,来自 Claude Design 标准模板)

URL 格式不符(缺 `api.anthropic.com/v1/design/h/` 段) → 停,提示 Founder 贴正确格式。

### Phase 2: 下载 + 解压

**铁律**:**单条 Bash 调用里一次性完成**(绝对路径),避免踩 shell cwd 持久性陷阱(见 Gotcha)。**不要**用 `cd X && ...` 开头的多次独立 Bash 调用。

```bash
# 单条调用模板 — 用项目根的绝对路径,一步到位
INBOX="$(pwd)/.claude-design-inbox"
mkdir -p "$INBOX"

# 下载(不假设扩展名,统一存为 "bundle")
curl -fL --retry 2 --max-time 60 -o "$INBOX/bundle" "<URL>" || { echo "ERROR: curl 失败"; exit 1; }

# 识别类型
TYPE=$(file -b "$INBOX/bundle")
echo "TYPE: $TYPE"

# 按类型解压(Claude Design 2026-04 观察是 gzipped tar,留 zip fallback)
if echo "$TYPE" | grep -qi 'gzip'; then
  tar -xzf "$INBOX/bundle" -C "$INBOX"
elif echo "$TYPE" | grep -qi 'tar'; then
  tar -xf "$INBOX/bundle" -C "$INBOX"
elif echo "$TYPE" | grep -qi 'zip'; then
  unzip -o "$INBOX/bundle" -d "$INBOX"
else
  echo "ERROR: 未知 bundle 格式: $TYPE"
  echo "hint: head -c 200 $INBOX/bundle  看是不是 HTML 错误页"
  exit 1
fi

# 清理 + 报告结构(含嵌套目录)
rm "$INBOX/bundle"
echo "---"
shasum -a 256 "$INBOX"/*/project/*.html 2>/dev/null | head -1
echo "---"
find "$INBOX" -maxdepth 3 -type f | head -30
```

**错误处理**(给清晰可操作的信息):

- **404 / 410**(HTTP) → "URL 已过期。Claude Design 的 share URL 短期失效,回 Claude Design 重新拿一份。"
- **401 / 403** → "URL 需要认证。本 skill 暂未实现认证路径,等产品层确认后再补。"
- **`file` 判定为 `HTML document`** → "下载拿到的是 HTML 错误页,不是 bundle。URL 大概率过期或无权访问。"
- **解压失败但类型识别成功** → 原样报 tar / unzip exit code + stderr。
- **网络超时** → "网络问题,重试或检查代理。"

### Phase 3: 报告 + 建议

**不执行任何后续动作**。输出:

1. **Bundle 根目录结构**:识别 `<INBOX>/<project-slug>/project/` 作为 primary dir(Claude Design 的 bundle 是两层嵌套 —— `<slug>/project/{files}` + `<slug>/README.md`)
2. **文件清单**:primary dir 下的 `*.html` / `*.css` / `*.jsx` / `HANDOFF.md` / `uploads/`
3. **`<slug>/README.md` 的前 20 行**(通常含本轮 bundle 的上下文说明)
4. 按 `<open_file>` 给建议(路径给**完整绝对路径**,Founder 复制即可用):

| open_file | 建议下一步 |
|---|---|
| `HANDOFF.md` | "入库 HANDOFF:`.claude-design-inbox/<slug>/project/HANDOFF.md` → `docs/design/HANDOFF.md`(整文件覆写)。若 Pending 段空则只入库,Appendix 段不占 TASK 编号。" |
| `{Name}.html`(primary design file) | 视项目状态:<br>• 无 `docs/design/EXTERNAL_REFS.md` → `/ui-bootstrap`<br>• 有 → 问 Founder:本轮要评审 `/ui-vs` / 采纳 `/ui-adopt` / 已评审完只要落代码(pixel-perfect recreate) |
| `styles.css` / `*.jsx` | 同 HTML 路径,但通常入口是 HTML |
| 无 `open_file` 参数 | 列清单,让 Founder 手动选入口 |

5. Inbox 若含 `.gitignore` / `README.md`(inbox 模板污染,同 `/ui-bootstrap` Gotcha) → 提醒 Founder,归档时需删除

## 关键约束

- **单条 Bash 调用完成 Phase 2** — 避免多次 `cd X && ...` 导致 cwd 漂移(实战观察到的坑)
- **绝对路径优先** — `"$(pwd)/.claude-design-inbox"` 比相对路径安全
- **不假设 bundle 格式** — 用 `file` 判定,不靠 URL 扩展名或 Content-Type
- **不自动跑 `/ui-vs` / `/ui-adopt` / `/ui-bootstrap`**:这些是重动作,Founder 必须显式触发
- **不自动覆写 `docs/design/HANDOFF.md`**:即使 `open_file=HANDOFF.md` 也只建议,避免误触
- **不自动清理 inbox 旧内容**:先询问再动
- **不猜认证 header**:遇 401/403 暂停,等产品层澄清
- **URL 过期是常态,不是 bug**:错误信息里要明确说"回 Claude Design 重拿",别让 Founder 以为是自己贴错
- **只负责"下载 + 解压 + 报告"**,不承担 drift 诊断 / 设计系统抽取 / TASK 识别 —— 那是 `/ui-bootstrap` / `/ui-vs` / `/ui-adopt` 的事

## 和其他工作流的关系

```text
Founder 贴 URL  →  ui-fetch(本 skill)  →  inbox/<slug>/project/* 有内容
                                              ↓
                       Founder 根据建议选下一步:
                       ├─ /ui-bootstrap     (首次接入)
                       ├─ /ui-vs            (评审)
                       ├─ /ui-adopt         (采纳反哺)
                       └─ 直接入库 HANDOFF  → 按协议处理 TASK
```

## Gotchas

- **Bundle 是 `.tar.gz` 不是 `.zip`**(2026-04 实战观察):Claude Design 的 share URL 返回 gzipped tar。用 `unzip` 会报"End-of-central-directory signature not found" —— 那不是文件损坏,是**搞错了格式**。一律用 `file` 判定后选工具。
- **解压后是两层嵌套** `<slug>/project/<files>`:不是平铺在 inbox 根。Phase 3 报告必须识别这个结构,路径建议给精确到嵌套内的完整路径。
- **Shell cwd 持久但 shell state 不**:`cd A && do_X`(第一次 Bash)后,**第二次 Bash 的 cwd 已经是 A**,再 `cd A && do_Y` 会失败("no such file")。实战里 Claude Code 分步救错时踩过。Phase 2 要求"单条 Bash 调用完成"就是为了避开这个坑。
- **同一 URL 二次下载**:若 inbox 已有相同解压后 HTML 的 SHA256,提示"内容无变化,要跳过解压吗"(复用 `/ui-bootstrap` Phase 0.3 的去重逻辑;注意比的是解压后的 HTML,不是 bundle tar 本身的 SHA)
- **share URL 每轮变**:Founder 每次迭代 Claude Design 后在它那边拿到新 URL,旧 URL 立即失效。报错时别误导 Founder 以为是自己写错
- **两种 Claude Design URL 易混淆**:
  - `claude.ai/design/p/<id>` = project 管理页(浏览器访问,不可下载 bundle)
  - `api.anthropic.com/v1/design/h/<id>` = bundle 下载链接(本 skill 要的)
- **`open_file` 参数可能拼错**:Claude Design 偶尔给错参数,导致 inbox 解压后找不到该文件。这种情况 Phase 3 只列清单、不报错,让 Founder 自己挑
- **`<slug>/README.md` 是给 Claude Code 读的**:bundle 里通常带一份 `<slug>/README.md`(Claude Design 写的落地说明,不是仓库 README),Phase 3 要扫它作为本轮上下文,但**不入仓库**
