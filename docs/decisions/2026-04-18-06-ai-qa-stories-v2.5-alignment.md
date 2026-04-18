# 2026-04-18-06 ai-qa-stories v2.5：与 ai-explore v4.0 共享基础设施对齐

## 背景

同一天早些时候完成 `ai-explore` v3.2 → v4.0 大改造（见 `2026-04-18-05`）。Founder 追问：姐妹 skill `ai-qa-stories` 是否需要同级别升级？

两个 skill 共用同一套 Debug State Server 和 Cyborg Probe 基础设施，但**业务定位本质不同**：

| 维度 | ai-explore | ai-qa-stories |
|------|-----------|---------------|
| 行动逻辑 | AI 扮演用户自由探索 | 按编译后的 qa.md 脚本执行 |
| 结果语义 | A/B/C/D 可信度梯度 | pass/skip/fail 二元+豁免 |
| 发现性质 | 未知 bug 涌现 | 已知契约回归 |
| 角色扮演 | persona × strategy 矩阵 | 无，按脚本走 |

## 讨论过程

Claude Code 按 v4.0 改动清单逐条做适用性判断（未启动 /think，因 v4.0 讨论已覆盖所有共享维度，qa-stories 特殊逻辑未引入新方法论问题，且 Founder 明确 "直接开干"）：

| v4.0 改动 | ai-qa-stories 是否适用 | 判断 |
|-----------|----------------------|------|
| Debug Server 契约（Generation ID / quiet-frame 2s / `/cyborg/reset`） | ✅ 必须对齐 | 共享基础设施，契约必须一致 |
| screenshots 路径统一 | ✅ 必须对齐 | 已有 user memory 规定 |
| State Teardown | ✅ 适用 | 故事切换时减少脏状态 |
| 工具错误预算 | ✅ 适用 | Server Bug 率 / flaky 率月度追踪 |
| Crime Scene 双快照 | ✅ 适用 | qa fail 时 Founder 30 秒判真假 |
| A/B/C/D 分级 | ❌ 不适用 | qa 本质是 pass/fail，无可信度梯度 |
| persona × strategy | ❌ 不适用 | qa 按脚本走不扮演用户 |
| Behavioral Fuzzing | ❌ 不适用 | qa 不能乱点 |
| 最小证伪单元 | ❌ 不适用 | 现有"归因四选一"已够 |
| Ignorance Hash | ❌ 不适用 | qa 同故事 fail 多次就是同故事，无"重复问题"概念 |

同时发现 v2.4 **已经做到**的 v4.0 理念（不需再加）：

- **端点对账三态判定**（MATCH / MISSING / **SERVER_BUG**）= Oracle 非神谕化的雏形，已把 Server 自己的 bug 单独红标
- **"只验证不修复"** = 边界硬卡
- **Seed / Remote Prep / 空库三档**（Step 0.5）= 测试数据治理

## 决策

**版本 v2.4 → v2.5**（不升 v3，改动量约 ai-explore v4.0 的 1/4）。5 项具体改动：

1. 新增「Debug Server 契约」章节，**引用 ai-explore v4.0 同一份契约**（DRY，两 skill 契约单一来源）
2. 新增「工具错误预算」小节 + `_scratch/ai-qa-stories/tool-errors/YYYY-MM.md` 月度聚合模板
3. Step 5 失败时触发 Crime Scene 双快照（改"失败详情"结构，附 before 红框 / after / oracle diff）
4. Step 0 加 State Teardown（故事间调 `/cyborg/reset` 如可用，替代"QA 过程中不重启"的硬约束）
5. screenshots 路径对齐 user memory：`screenshots/qa/YYYY-MM-DD/story_N_scenario_N_{before,after}.png`

## 为什么不做 v3 大重写

- 业务逻辑已清晰稳定，核心流程（Step 1-6）无需改动
- 边界本来就硬（"只验证不修复"比 ai-explore 的边界白名单更简单）
- 归因四选一（server-handler-bug / code-business-bug / prereq-missing / scenario-outdated）已是最小证伪单元的简化版
- 强行引入 A/B/C/D 分级会破坏 qa 的二元判定契约，消费方（Founder / generate-stories）都要改

## 风险与反面检验

- **Crime Scene 双快照增加 qa 执行成本**：但只在 fail 时触发，pass 路径零开销
- **State Teardown 依赖 `/cyborg/reset` 端点**：端点不存在时优雅降级为"不 reset，沿用 v2.4 的故事编号顺序依赖"
- **月度错误预算阈值未定**：与 ai-explore 保持一致（30%），首月运行后校准

## 下游影响

- ai-qa-stories 和 ai-explore 的 Debug Server 契约现在**单一来源**（都指向 v4.0 契约章节），任一 skill 升级契约，另一 skill 自动继承
- `_scratch/ai-qa-stories/tool-errors/` 与 `_scratch/ai-explore/tool-errors/` 并列但独立，各自追踪
- 姐妹 skill `android-explore` / `godot-explore` / 未来的 android-qa-stories / godot-qa-stories 应在下次触及时同步对齐（不主动推进）

## 回滚条件

3 个月内观察到：
- Crime Scene 双快照对 qa 执行时间影响 >30% → 改为可选
- State Teardown 引入新的 flaky（reset 后状态不干净）→ 回退

## 参考

- 前一决策：`2026-04-18-05-ai-explore-v4-trust-framework.md`（建立了共享设计原则）
- user memory：`user_project_screenshots.md`（screenshots 路径约定）
