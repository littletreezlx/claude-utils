---
name: 部署到 TCL TV (192.168.0.105) 必须走 OTA 升级系统
description: 192.168.0.105 是 TCL 客厅 TV，固件拦截 adb install；改完代码直接跑 publish-to-nas.sh，不要尝试 adb install
type: feedback
originSessionId: d387e5b3-6c83-48b6-a503-9ea88d41ea0f
---
在 192.168.0.105（TCL 客厅 TV）上验证代码改动时，**不要尝试 `adb install`**。直接走项目的 OTA 流程：`./scripts/publish-to-nas.sh` → 告知 Founder 冷启动 FlameTree 应用 + 在 TV 端弹窗点系统安装确认 → 装好后再 screencap 验证。

**Why:** TCL 固件内置 `OverseasAppConfig` 海外应用验证器，拦掉所有 `adb install` 路径，返回 `INSTALL_FAILED_VERIFICATION_FAILURE`。2026-04-25 实测无解：先 `pm uninstall` 后再装、`-t -r` 标志、`adb shell settings put global verifier_verify_adb_installs 0` + `package_verifier_enable 0` 全部无效（这是 TCL 私货，不是标准 Android verifier）。`logcat` 关键证据：`OverseasAppConfig: Verifying begin pkgName=com.littletree.flametree_tv`。`publish-to-nas.sh` 走的是 NAS OTA + 系统 PackageInstaller + FileProvider 路径，不被 `OverseasAppConfig` 拦。

**How to apply:**
1. 改完代码 → `./gradlew :app:assembleDebug` 编译通过 → **直接** `./scripts/publish-to-nas.sh`，不要先尝试 `adb install`（白浪费时间）。
2. 脚本会 `versionCode + 1` 写回 `app/build.gradle.kts`，是预期行为，不是脏改动。
3. 推送完成后向 Founder 发指令："重启 FlameTree 应用（冷启动）→ 等系统安装弹窗 → 点确认（首次需要授权'安装未知应用'）"。
4. 装好后 `adb -s 192.168.0.105:5555 shell screencap` 截图，对比改动前后验证。
5. 区别于 192.168.0.51 小米手机（开发调试机，能直接 adb install）—— 105 是真 TV 形态、最终目标设备，但部署门槛高。
