---
name: A/B test 作为项目资产管理
description: A/B test yaml 文件要保存在 ab-tests/ 目录，不要改 quick.yaml
type: feedback
---

A/B test 配置文件要作为项目资产保存，不是用完就删。

**Why:** 改 quick.yaml 跑 A/B test 需要反复修改文件，无法还原，也不利于维护和复现。

**How to apply:** 每次 A/B test 在 `ab-tests/<topic>/` 下创建独立 yaml 文件（a-xxx.yaml, b-xxx.yaml...），注释里记录结果和输出路径。结构类似 scenes/ 目录，每个实验主题一个子目录。不要修改 quick.yaml 来做测试。
