---
name: quick_py_custom_features
description: quick.py 新增的自定义功能 — resolution 和 basemodel 字段支持
type: feedback
---

## quick.py 新增功能 (2026-03-21)

本次会话中为 quick.py 添加了两个 YAML 字段支持：

1. **`resolution: WxH`** — 覆盖底模默认分辨率
   - 格式：`resolution: 1536x1024`（横图）或 `resolution: 1024x1536`（竖图）
   - 不写则使用 model_registry 中底模的 default_resolution

2. **`basemodel: filename.safetensors`** — 直接指定底模文件
   - 绕过 model_registry，直接加载 checkpoints 目录下的指定文件
   - 用于快速 A/B 测试不同底模

**How to apply:** 在 quick.yaml 中直接使用这两个字段即可，quick.py 会自动读取。
