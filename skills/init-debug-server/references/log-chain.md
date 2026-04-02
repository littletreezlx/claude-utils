# Debug State Server — 日志链路

## 问题

`flutter run` 后台运行时，Dart 的 `developer.log()` / `debugPrint()` 输出**不会**被转发到文件。
`flutter logs` 抓的是设备 syslog，也抓不到 Dart VM 日志。

结论：**无法**从外部获取 App 运行时的 Dart 日志。

## 解决方案：DebugServer 自己记录操作日志

在 DebugServer 内部维护环形缓冲区，记录所有 HTTP 交互（action 请求/响应、state 读取、错误），通过 `GET /logs` 暴露。

### DebugServer 需要的代码

```dart
class DebugServer {
  // 环形日志缓冲区（最近 200 条）
  static final List<Map<String, dynamic>> _logBuffer = [];
  static const _maxLogEntries = 200;

  // 在 router 中注册
  // ..get('/logs', _handleGetLogs)

  static void _addLog(String level, String message) {
    _logBuffer.add({
      'time': DateTime.now().toIso8601String(),
      'level': level,
      'message': message,
    });
    if (_logBuffer.length > _maxLogEntries) {
      _logBuffer.removeAt(0);
    }
  }

  static Response _handleGetLogs(Request request) {
    final countStr = request.url.queryParameters['count'];
    final count = countStr != null ? int.tryParse(countStr) ?? 50 : 50;
    final logs = _logBuffer.length <= count
        ? _logBuffer
        : _logBuffer.sublist(_logBuffer.length - count);
    return _jsonOk({
      'logs': logs,
      'count': logs.length,
      'total': _logBuffer.length,
    });
  }
}
```

### 在 handler 中调用 _addLog

```dart
// Action handler 中：
_addLog('action', '$actionKey ← $payload');
// 成功后：
_addLog('result', '$actionKey → $result');
// 失败时：
_addLog('error', '$actionKey failed: $e');
// State 读取：
_addLog('state', 'read $name (${state.length} fields)');
```

### 效果

```bash
curl -s "localhost:8788/logs?count=5" | python3 -c "
import sys, json
for log in json.load(sys.stdin)['data']['logs']:
    print(f\"  [{log['time'][11:19]}] [{log['level']:6s}] {log['message']}\")
"
```

输出：
```
  [23:00:30] [action] app/toggleAnimation ← {enabled: false}
  [23:00:30] [result] app/toggleAnimation → {action: toggleAnimation, enabled: false}
  [23:00:40] [state ] read app (4 fields)
  [23:00:40] [action] app/toggleAnimation ← {enabled: true}
  [23:00:40] [result] app/toggleAnimation → {action: toggleAnimation, enabled: true}
```

## start-dev.sh --background 模板

```bash
#!/bin/bash
# start-dev.sh — 支持 AI 后台模式

LOG_FILE="/tmp/flutter_run.log"
DEBUG_PORT=8788
SESSION_START=$(date '+%Y-%m-%d %H:%M:%S')

# 追加会话标记
echo -e "\n=== 新会话: $SESSION_START ===" >> "$LOG_FILE"

if [ "${1:-}" = "--background" ]; then
  echo "🤖 AI 模式"
  flutter run -d iPhone >> "$LOG_FILE" 2>&1 &
  PID=$!
  echo "   PID: $PID"
  echo "   日志: $LOG_FILE"

  # 等待 Debug Server ready
  # ⚠️ 每次迭代必须 sleep 1s！否则 60 次瞬间完成报"超时"
  echo -n "   等待..."
  for i in $(seq 1 60); do
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$DEBUG_PORT/providers" 2>/dev/null | grep -q 200; then
      echo " ✓ Ready (http://localhost:$DEBUG_PORT)"
      exit 0
    fi
    if ! kill -0 $PID 2>/dev/null; then
      echo " ✗ 进程已退出"
      tail -20 "$LOG_FILE"
      exit 1
    fi
    sleep 1
  done
  echo " ✗ 超时（60s）"
  echo "   flutter run 可能仍在编译，检查日志: tail -f $LOG_FILE"
  exit 1
else
  # 交互模式
  flutter run 2>&1 | tee -a "$LOG_FILE"
fi
```

**关键改动 vs 旧版**：`sleep 1` 在循环内。没有 sleep 时 60 次 curl 在 1 秒内全部完成，iOS 首次编译需要 45s+，必然"超时"。脚本超时不代表启动失败——flutter run 仍在后台编译。

## AI 使用方式

```bash
# 启动
./scripts/start-dev.sh --background

# 改代码后重启（整个 QA 会话最多重启 1 次）
pkill -9 -f "<app_binary>"; pkill -f "flutter run"
./scripts/start-dev.sh --background

# 查看操作日志
curl -s "localhost:8788/logs?count=20" | python3 -m json.tool

# 查看构建日志
./scripts/view-dev-log.sh latest
```
