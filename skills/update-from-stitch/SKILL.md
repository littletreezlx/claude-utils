---
name: update-from-stitch
description: >
  This skill should be used when the user wants to pull or sync designs from
  Google Stitch to local code, when the user says "update from stitch",
  "sync from stitch", "从 stitch 更新", "拉取 stitch", "stitch 同步",
  or provides a stitch.withgoogle.com URL. Downloads Stitch project screens
  (HTML + screenshots) to a local folder, uses git diff to detect changes,
  and guides updating implementation for changed screens only.
version: 0.2.0
---

# Update from Stitch — 从 Stitch 拉取设计稿到本地

## 目的

将 Google Stitch 远程项目的设计成果同步到本地 `stitch/` 目录，通过 git diff 智能识别变更的 screen，只对变更部分提取 design token 差异并引导更新代码和文档。扮演 **Design-to-Code Bridge** 角色。

## 触发条件

当以下**任一**条件满足时启动：

1. 用户说"update from stitch"、"从 stitch 更新"、"拉取 stitch"、"stitch 同步"
2. 用户提供 `stitch.withgoogle.com/projects/` URL
3. 用户明确要求将 Stitch 设计稿同步到本地

## 执行流程

### Step 1: 解析项目关联

检查项目根目录下 `.stitch.json`：

```json
{
  "projectId": "2202007460455968270",
  "projectUrl": "https://stitch.withgoogle.com/projects/2202007460455968270",
  "lastSync": "2026-03-23T10:00:00Z"
}
```

| 情况 | 处理 |
|------|------|
| `.stitch.json` 存在且有 projectId | 直接使用 |
| 用户提供了 Stitch URL | 从 URL 提取 projectId，创建 `.stitch.json` |
| 都没有 | 引导用户提供 URL 或 ID，创建配置 |

### Step 2: 全量拉取 + Git Diff 智能过滤

**拉取阶段**：

1. `mcp__stitch__get_project` 获取项目信息
2. `mcp__stitch__list_screens` 获取所有 screen
3. **并行** `mcp__stitch__get_screen` 获取每个 screen 的 HTML + 截图 URL
4. 如果 `htmlCode` 非空，将 HTML 写入 `stitch/screens/{screen_name}.html`（覆盖）
5. 通过 `curl -sL` 下载截图到临时文件，然后**必须验证并转换格式**：
   ```bash
   # Google CDN 返回 JPEG 但无扩展名，下载后可能是 JPEG 伪装 PNG
   curl -sL -o /tmp/screen.tmp "https://lh3.googleusercontent.com/..."
   # 用 sips 转为真正的 PNG（macOS）
   sips -s format png /tmp/screen.tmp --out stitch/screens/{screen_name}.png
   ```
   或者批量处理：先全部 curl 下载为 `.png`，再统一 `sips -s format png` 转换
6. 更新 `.stitch.json` 的 `lastSync`

**变更检测**：

```bash
git diff --name-only stitch/screens/
```

- **有变更的 screen** → 进入 Step 3 详细分析
- **无变更** → 告知用户"Stitch 设计与本地一致，无需更新"，流程结束
- **首次同步**（全部是新文件）→ 全部进入 Step 3

**screen 文件命名**：`{deviceType}_{screen_title}.html`，如 `desktop_main_view.html`、`mobile_feed_list.html`。title 取自 screen 的 displayName，空格转下划线，全小写。

### Step 3: 提取差异 + 确认更新

仅针对 Step 2 识别出的**变更 screen**：

1. 用 Read 查看变更 screen 的截图（`.png` 文件），获取视觉直觉
2. 读取变更 screen 的 HTML，提取 design token（颜色、字体、圆角、间距、阴影等）
3. 读取本地代码中对应的 theme/token 文件
4. 生成**差异对比表**：

```
| 维度     | 当前实现          | Stitch 设计稿        |
|----------|-------------------|----------------------|
| 主背景色 | #E8E4DE           | #FBF2E8              |
| 主文字色 | #2A2724           | #1F1B15              |
| ...      | ...               | ...                  |
```

5. 展示差异表，**等待用户确认更新范围**后执行修改
6. 按确认范围更新 design tokens、组件样式、设计文档

### 收尾：交接提示

更新完成后，输出标准化交接：

> 同步与代码更新已完成。受影响的文件：[列表]
>
> 建议：热重载后运行 `/ui-vision-check` 对变更页面做视觉验证，确认实现效果与 Stitch 设计稿一致。

不在本 skill 内自动触发 ui-vision-check（需要先热重载/编译，环境 ready 由用户判断）。

## 踩坑点

- **get_screen 需要三个参数**：`name`（完整资源路径 `projects/{pid}/screens/{sid}`）、`projectId`、`screenId`，三个都要传
- **HTML 可能很大**：单个 screen 的 HTML 可能超过 1000 行，写入文件时不要在上下文中全量打印，用 Write 工具直接写
- **htmlCode 可能为空**：Stitch 不一定为每个 screen 生成 HTML（`htmlCode: {}` 为空对象）。此时只有截图可用，跳过 HTML 写入，仅保存截图作为视觉参考
- **并行拉取**：screens 之间无依赖，务必并行 get_screen 提高效率
- **设计稿 ≠ 代码**：Stitch 产出的是 web HTML/CSS，如果本地项目是 Flutter/Native/Godot，需要翻译设计意图（色值、字重、间距比例）而非照搬 CSS 属性
- **伪 diff 风险**：如果实践中发现 AI 生成的 HTML 结构不稳定（同样视觉效果但 HTML 不同，导致 git diff 误报），后续可引入 HTML 规范化预处理步骤
- **⚠️ 截图是 JPEG 伪装成 PNG**：Google CDN（`lh3.googleusercontent.com`）返回的截图 URL 虽然没有扩展名，但实际内容是 **JPEG 格式**。用 curl 下载并保存为 `.png` 后，文件头是 JFIF 而非 PNG signature。Godot 等引擎按扩展名判断格式，会导入失败（`.import` 文件出现 `valid=false`）。**修复方法**：下载后必须用 `sips -s format png input.jpg --out output.png`（macOS）或 `convert`（ImageMagick）转为真正的 PNG，或者直接保存为 `.jpg` 扩展名
- **截图分辨率较低**：Stitch 截图默认约 512×286（非全分辨率），作为视觉参考足够，但不适合直接用作游戏/应用的高清背景素材。如需高清版本，需用 AI 图片生成管线重新生成

## 约束

- Step 3 展示差异后**必须**等用户确认才修改代码
- `stitch/` 目录应纳入 git（作为 diff 锚点）
- `.stitch.json` 建议加入 `.gitignore`（项目关联是个人配置）
- 不在本 skill 内触发 ui-vision-check，仅输出交接提示
