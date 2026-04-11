# Xcode Build — Xcode 自动化构建 Skill

> **适用场景**: macOS Flutter 项目遇到代码签名问题，需要通过 Xcode 自动化构建

## 核心问题

`flutter build macos` 遇到代码签名证书无效时（如 `Signing certificate is invalid. It may have been revoked or expired.`），需要改用 Xcode 构建。

## 职责边界

**本 Skill 负责**：
1. 打开 Xcode workspace
2. 等待 Xcode 初始化（约 30 秒）
3. 通过 xcodebuild 自动化构建（禁用签名）
4. 启动构建成功的 App

**本 Skill 不负责**：
- 修复证书问题（需要用户在 Xcode/Apple Developer Portal 操作）
- Debug Server 代码生成（那是 `init-debug-server` 的职责）

## 执行流程

### Step 1: 发现 workspace

```bash
# 在项目根目录查找 xcworkspace
WS=$(find . -name "*.xcworkspace" -type d | head -1)
if [ -z "$WS" ]; then
  echo "ERROR: No .xcworkspace found"
  exit 1
fi
echo "Found: $WS"
```

### Step 2: 用 Xcode 打开 workspace

```bash
open -a Xcode "$WS"
echo "Xcode launched, waiting 30s for initialization..."
sleep 30
```

### Step 3: 列出可用 scheme

```bash
xcodebuild -list -workspace "$WS" 2>&1 | grep -E "^\s+[A-Za-z]" | head -10
```

### Step 4: 自动化构建（禁用签名）

```bash
xcodebuild -workspace "$WS" \
  -scheme FlutterMacOS \
  -configuration Debug \
  build \
  CODE_SIGN_IDENTITY="-" \
  CODE_SIGNING_REQUIRED=NO \
  2>&1 | tail -20
```

**注意**: 如果 Mac 有隐私保护（需要输入密码授权 App 管理电脑），会在此步骤阻塞。等待用户完成授权后，构建会自动继续。

### Step 5: 验证构建结果

```bash
if [ $? -eq 0 ]; then
  echo "✅ BUILD SUCCEEDED"
else
  echo "❌ BUILD FAILED"
  exit 1
fi
```

### Step 6: 启动 App

```bash
# 查找最新构建的 app
APP=$(find ~/Library/Developer/Xcode/DerivedData/Runner-*/Build/Products/Debug -name "*.app" -type d 2>/dev/null | head -1)

# Flutter 项目通常直接 build 到项目目录
if [ -z "$APP" ]; then
  APP="./build/macos/Build/Products/Debug/FlameTree AI.app"  # 替换为实际 App 名称
fi

open "$APP"
```

### Step 7: 验证 Debug Server

```bash
sleep 5
PORT=$(grep 'static const int port' app/lib/dev_tools/debug_server.dart | grep -oE '[0-9]+$' | tail -1)
curl -s --connect-timeout 5 localhost:$PORT/providers | grep -q '"ok":true' && echo "✅ Debug Server OK" || echo "❌ Debug Server DOWN"
```

## 快速命令

```bash
# 一键构建并启动
./scripts/xcode-build.sh

# 或手动组合
open -a Xcode app/macos/Runner.xcworkspace && sleep 30 && xcodebuild -workspace app/macos/Runner.xcworkspace -scheme FlutterMacOS -configuration Debug build CODE_SIGN_IDENTITY="-" CODE_SIGNING_REQUIRED=NO
```

## 常见问题

| 问题 | 解决 |
|------|------|
| `open -a Xcode` 无反应 | Xcode 已在运行，直接使用现有实例 |
| 构建阻塞在隐私授权 | 等待用户输入密码，完成后自动继续 |
| `CODE_SIGN_IDENTITY` 不支持 | 改用 `CODE_SIGNING_ALLOWED=NO` |
| 找不到 .app | 检查 `build/macos/Build/Products/Debug/` 或 DerivedData |

## 项目级脚本模板

在项目 `scripts/` 目录创建 `xcode-build.sh`:

```bash
#!/bin/bash
set -e
cd "$(dirname "$0")/.."

PORT=$(grep 'static const int port' app/lib/dev_tools/debug_server.dart | grep -oE '[0-9]+$' | tail -1)
WS="app/macos/Runner.xcworkspace"
APP_NAME="FlameTree AI"  # 替换为实际名称

echo "=== Xcode Build ==="

# 打开 workspace
open -a Xcode "$WS"
echo "Waiting 30s for Xcode initialization..."
sleep 30

# 构建
xcodebuild -workspace "$WS" \
  -scheme FlutterMacOS \
  -configuration Debug \
  build \
  CODE_SIGN_IDENTITY="-" \
  CODE_SIGNING_REQUIRED=NO

# 启动
open build/macos/Build/Products/Debug/"$APP_NAME".app

# 验证
sleep 5
curl -s --connect-timeout 5 localhost:$PORT/providers | grep -q '"ok":true' && echo "✅ Debug Server OK" || echo "❌ Debug Server DOWN"
```

## 注意事项

1. **Xcode 初始化需要时间** — `open -a Xcode` 后必须等待 30 秒再执行 `xcodebuild`
2. **隐私授权可能阻塞** — macOS 首次运行 App 时会请求"App Management"权限，需用户手动授权
3. **签名禁用仅适用调试** — 生产构建必须使用有效签名
