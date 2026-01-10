# DeepSeek 直连翻译器重构计划

## 目标

重构翻译模块，**移除对 NAS Node.js 服务的依赖**，直接调用 DeepSeek API，实现脚本独立运行。

## 用户决策

- **引擎选择**: 只保留 DeepSeek，移除 http/openai 引擎
- **批次大小**: 20 条/批
- **翻译模式**: 简单模式（直接翻译 + 滑动窗口上下文）

## 核心变更

### 1. 创建 `DeepSeekTranslator` 类

**文件**: `src/translators/deepseek_translator.py`

**设计要点**:
- 直接使用 `openai` Python 库，`base_url` 指向 `https://api.deepseek.com`
- 使用 DeepSeek 原生的 JSON Output 功能 (`response_format: { type: "json_object" }`)
- 实现滑动窗口上下文传递（翻译时附带前一批的原文+译文）
- 继承 `BaseTranslator` 基类，复用公共方法
- 批次大小固定为 **20 条**
- 复用 `OptimizedTranslator` 的好实现：
  - 字幕特殊字符转义/还原 (`_escape_subtitle_text`, `_unescape_subtitle_text`)
  - JSON 修复机制 (`_fix_invalid_json`)
  - 调试数据保存 (`_save_debug_data`)
- 支持并行批处理（复用 `ParallelBatchCoordinator`）

**API 调用策略**:
```python
# DeepSeek JSON Output 使用方式
response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": system_prompt},  # 必须包含 "json" 关键词
        {"role": "user", "content": user_prompt}
    ],
    response_format={"type": "json_object"},
    temperature=0.3
)
```

**分块 + 上下文 Prompt 设计**:
```
System Prompt:
你是一位专业的视频字幕翻译专家。你的任务是将提供的字幕片段翻译成中文。
1. 保留原意：结合上下文，通过意译使表达自然流畅。
2. 结构严格：必须返回符合定义的 JSON 格式。
3. 一一对应：不要合并或拆分字幕行，保持 ID 对应。
4. 术语一致：遇到专业术语请保留英文或使用标准译名。

返回格式（JSON）：
{
  "translations": [
    {"id": 1, "text": "译文1"},
    {"id": 2, "text": "译文2"}
  ]
}

User Prompt:
[上下文（前一批翻译）]
原文: "So we need to..."
译文: "所以我们需要..."

[当前待翻译]
[
  {"id": 10, "text": "Let's continue with..."},
  {"id": 11, "text": "Using Node.js here."}
]
```

### 2. 简化配置管理

**文件**: `src/config.py`

**变更**:
- 移除 `SUPPORTED_ENGINES` 列表（不再需要多引擎支持）
- 移除 `http_api_url` 配置
- 添加 DeepSeek API 配置项：
  ```python
  deepseek_api_key: str = ""  # 通过环境变量 DEEPSEEK_API_KEY 设置
  deepseek_base_url: str = "https://api.deepseek.com"
  deepseek_model: str = "deepseek-chat"
  translation_batch_size: int = 20  # 固定为 20
  ```
- 移除 `default_translator_engine` 配置（只有一个引擎）

### 3. 简化翻译器入口

**文件**: `src/translator.py`

**变更**:
- 移除引擎选择逻辑，直接使用 `DeepSeekTranslator`
- 简化 `SubtitleTranslator` 类，移除 `engine` 参数
- 移除对 `HTTPTranslator` 和 `OpenAITranslator` 的导入

### 4. 清理翻译器模块

**文件**: `src/translators/`

**变更**:
- 删除 `http_translator.py`（不再需要）
- 删除 `openai_translator.py`（不再需要）
- 删除 `optimized_translator.py`（功能合并到 DeepSeekTranslator）
- 删除 `sdk_parallel_translator.py`（不再需要）
- 保留 `base.py`、`parallel_batch_coordinator.py`
- 更新 `__init__.py`，只导出 `DeepSeekTranslator`

## 实现细节

### 滑动窗口上下文

```python
class DeepSeekTranslator(BaseTranslator):
    def __init__(self, ...):
        # 上下文缓存：存储上一批的原文和译文
        self._context_window: List[Dict[str, str]] = []
        self._context_size = 5  # 保留最后 5 条作为上下文

    def _translate_batch_with_context(self, texts, target_lang, batch_id):
        # 构建上下文字符串
        context_str = self._build_context_string()

        # 调用 API
        result = self._call_deepseek_api(texts, target_lang, context_str)

        # 更新上下文窗口
        self._update_context_window(texts, result)

        return result
```

### 配置优先级

1. 环境变量 `DEEPSEEK_API_KEY` (最高优先级)
2. 配置文件中的 `deepseek_api_key`
3. 抛出错误（必须配置）

## 文件变更清单

| 文件 | 操作 | 说明 |
|------|------|------|
| `src/translators/deepseek_translator.py` | **新建** | DeepSeek 翻译器实现（核心） |
| `src/config.py` | 修改 | 简化配置，添加 DeepSeek 配置 |
| `src/translator.py` | 修改 | 移除引擎选择，直接使用 DeepSeek |
| `src/translators/__init__.py` | 修改 | 只导出 DeepSeekTranslator |
| `src/translators/http_translator.py` | **删除** | 不再需要 |
| `src/translators/openai_translator.py` | **删除** | 不再需要 |
| `src/translators/optimized_translator.py` | **删除** | 功能合并 |
| `src/translators/sdk_parallel_translator.py` | **删除** | 不再需要 |
| `src/translators/translation_schema.py` | **删除** | 不再需要 |

## 验证方案

1. **环境准备**:
   ```bash
   # 设置环境变量
   export DEEPSEEK_API_KEY="sk-5b3b359cdf3343e5a1fd81e93ff5ba2c"
   ```

2. **翻译器单元测试**:
   ```bash
   python -c "
   from projects.auto_sub.src.translators.deepseek_translator import DeepSeekTranslator
   t = DeepSeekTranslator()
   result = t.translate(['Hello world', 'How are you?'], 'zh')
   print(result)
   assert len(result) == 2, '翻译结果数量不匹配'
   print('✓ 单元测试通过')
   "
   ```

3. **集成测试**（用实际视频文件）:
   ```bash
   # 处理视频（无需 --engine 参数，因为只有一个引擎）
   python projects/auto_sub/main.py -i test_video.mkv
   ```

4. **验证清单**:
   - [ ] API 连接正常（无网络错误）
   - [ ] JSON Output 格式正确（无解析错误）
   - [ ] 翻译结果数量与输入一致
   - [ ] 上下文传递生效（检查日志中的 context 信息）
   - [ ] 特殊字符（`\N`）处理正确
   - [ ] 并行批处理正常工作

## 预期效果

- **独立运行**: 无需 NAS Node.js 服务，脚本可完全独立执行
- **成本更低**: 直接调用 DeepSeek API（约 $0.14/M tokens，比 GPT-4 便宜 ~100 倍）
- **格式稳定**: 利用原生 JSON Output，避免正则解析问题
- **连贯翻译**: 滑动窗口上下文提升前后句的语义连贯性
- **代码简化**: 移除多引擎支持后，代码量减少约 50%
