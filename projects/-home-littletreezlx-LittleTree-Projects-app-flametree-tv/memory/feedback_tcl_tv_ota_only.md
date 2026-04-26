---
name: 部署到 TCL TV (192.168.0.105) 必须走 OTA 升级系统
description: 192.168.0.105 是 TCL 客厅 TV，固件拦截 adb install；改完代码直接跑 publish-to-nas.sh，不要尝试 adb install
type: feedback
originSessionId: d387e5b3-6c83-48b6-a503-9ea88d41ea0f
---
在 192.168.0.105（TCL 客厅 TV）上验证代码改动时，**不要尝试 `adb install`**。完整自闭环流程见 `docs/workflows/ota-self-loop.md`（编译 → 推 NAS → 触发 OTA → `adb input tap 1140 870` 模拟点击系统安装器 → poll versionCode 确认升级落地，AI 不需要 Founder 介入）。

**Why:** TCL 固件内置 `OverseasAppConfig` 海外应用验证器，拦掉所有 `adb install` 路径，返回 `INSTALL_FAILED_VERIFICATION_FAILURE`。2026-04-25 实测无解：先 `pm uninstall` 后再装、`-t -r` 标志、`adb shell settings put global verifier_verify_adb_installs 0` + `package_verifier_enable 0` 全部无效（这是 TCL 私货，不是标准 Android verifier）。`logcat` 关键证据：`OverseasAppConfig: Verifying begin pkgName=com.littletree.flametree_tv`。`publish-to-nas.sh` 走的是 NAS OTA + 系统 PackageInstaller + FileProvider 路径，不被 `OverseasAppConfig` 拦。

**How to apply:**
1. 改完代码 → `./gradlew :app:assembleDebug` 编译通过 → **直接** `./scripts/publish-to-nas.sh`，不要先尝试 `adb install`（白浪费时间）。
2. 脚本会 `versionCode + 1` 写回 `app/build.gradle.kts`，是预期行为，不是脏改动。
3. 后续步骤（等 PackageInstaller 弹窗 → tap 安装 → poll versionCode）按 `docs/workflows/ota-self-loop.md` 的命令序列执行，AI 全自动跑通。
4. **仅以下两种情况仍需 Founder 介入**：(a) 跨签名升级（debug ↔ release），(b) 该设备首次安装且未 toggle "install unknown apps"。文档 §9 边界明示。
5. 区别于 192.168.0.51 小米手机（开发调试机，能直接 adb install）—— 105 是真 TV 形态、最终目标设备，但部署门槛高（已可 AI 自闭环）。
