---
name: 信任 LLM 改革（已完成）
description: 去除 Python 层对 LLM 创意输出的强制干预。Tier/黑名单/auto-strip/三轴注入/随机roll 全部移除或可选化。
type: project
---

**2026-03-26 "信任 LLM" 改革（已完成，commit 8224913）：**

### 已移除的 Python 干预

| 机制 | 原行为 | 改动 |
|------|--------|------|
| Tier 1/2/3 分级 | LLM 偏好"安全"姿势 | 改为 POSITION FREEDOM |
| POSE_BLACKLIST_CORRECTIONS | 强制替换 standing+legs wrapped | 清空 |
| auto-strip | beat N 强制全裸 | 禁用，LLM 自主控制 |
| Standing sex 墙注入 | 自动加 (against wall:1.3) | 移除 |
| Missionary 镜头注入 | 自动加 from above | 移除 |
| 感官三轴注入 | 自动加 blush/sweat/skindentation | 禁用 |
| 早期阶段脱衣封锁 | Solo/Escalation 禁止 LLM 脱衣 | 移除 |
| 随机 roll 角色/服装 | Python 骰子决定外貌 | 标准模式 LLM 自由设计 |

### 保留的机制（物理/逻辑正确性）
- Mutex 互斥规则（物理不可能的组合）
- 男性属性过滤（防止 beard 写到女角色上）
- Aftercare solo 强制（结构需求）
- Pose-Camera 矩阵（改为"擦除悖论"而非"强制替换"）
- 审查标签注入（合规需求）

### 新增功能
- `--dice` 参数：骰子模式（随机 roll），默认为标准模式（LLM 自由设计）
- `WORLDBUILD_STANDARD_PROMPT`：角色+服装+环境三合一
- 实验脚本：`scripts/test_pose_freedom.py`, `scripts/test_pose_rendering.py`

**How to apply:**
- 标准模式：`python create_story.py "theme" --body voluptuous --beats 12 --style v3`
- 骰子模式：加 `--dice`
- 遇到渲染问题时，先检查是否是 LLM 输出的物理悖论（Pose-Camera 矩阵会日志警告）
