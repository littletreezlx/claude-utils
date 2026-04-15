# Memory Index

## Feedback (工作方式指导)
- [feedback_prompt_engineering.md](feedback_prompt_engineering.md) — 提示词过载教训：少即是多，控制在 20 词以内
- [feedback_lora_stacking.md](feedback_lora_stacking.md) — LoRA 堆叠经验：总权重 ≤ 1.4，注意风格系统自带 LoRA
- [feedback_v3_style_pitfalls.md](feedback_v3_style_pitfalls.md) — V3 从 MiaoMiao 补偿型重写为 Perfect Doll 引导型，底模选择与标签策略
- [feedback_quick_py_features.md](feedback_quick_py_features.md) — quick.py 新增 resolution 和 basemodel 字段
- [feedback_ai_maintenance_strategy.md](feedback_ai_maintenance_strategy.md) — AI 维护策略：ROI 评估框架 + 过度工程化警告 (Gemini 共识)
- [feedback_v3_dark_mood_composition.md](feedback_v3_dark_mood_composition.md) — V3 暗调质感方法 + cowboy shot 构图 + 姿势轻重技巧
- [feedback_data_before_opinion.md](feedback_data_before_opinion.md) — 先跑数据再下结论，不要主观臆测。A/B 实验优先于推理
- [feedback_ab_test_as_asset.md](feedback_ab_test_as_asset.md) — A/B test yaml 存 ab-tests/ 目录作为项目资产，不改 quick.yaml
- [feedback_ancient_chinese_tags.md](feedback_ancient_chinese_tags.md) — 古装质感配方：hanfu + traditional_media + v3，不用现代服装词汇
- [feedback_example_pollution.md](feedback_example_pollution.md) — Prompt 示例会被 LLM 当模板复制，必须加反例+多样性声明
- [feedback_signature_traits_rarity.md](feedback_signature_traits_rarity.md) — 签名级特征 (heterochromia 等) 在 prompt 示例里必须显式标稀有度，否则集体撞特征

## Project (项目状态)
- [project_model_comparison.md](project_model_comparison.md) — 底模对比实验：MiaoMiao > Nova Anime3D > IlluQuaint > Flux
- [project_pose_experiment.md](project_pose_experiment.md) — 信任 LLM 改革（已完成）：去除 Tier/黑名单/auto-strip/三轴注入等干预，--dice 保留骰子模式
- [project_body_lora_split.md](project_body_lora_split.md) — 脸/身材 LoRA 拆分架构：已完成训练端+生成端，Scene YAML V9 body 字段拆分待做
