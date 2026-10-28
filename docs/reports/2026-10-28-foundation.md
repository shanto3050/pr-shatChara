# First Android foundation build — verified device report

Test date: 28 October 2026 (desktop/client date). The phone's logcat clock showed a different date; do not use its timestamps as the production date.

## Artifact

- Source baseline: 633633c, Unity 6000.3.27f1, URP 17.3.0.
- Build: development APK, version 0.0.1 (code 1), com.shanto3050.satchara.dev.
- Local output: unity/SatChara/Builds/Android/SatChara-Foundation.apk. Binary is excluded from Git; source, instructions, report and screenshots are versioned.
- File size: 42,043,675 bytes (42.04 MB decimal, 40.10 MiB). Unity's report totalSize includes additional outputs and must not be substituted for the APK's file size.
- SHA-256: C77FEF38FDF50ED57D9C338A25516ACB7829D9C05F63D4F19F32096BC5DE3E32.
- aapt: minimum SDK 26, target/compile SDK 36, arm64-v8a, launch activity com.unity3d.player.UnityPlayerGameActivity.
- apksigner verification passed, APK Signature Scheme v2, one signer. This is a development/debug-signed artifact, not a production store release.
- Unity build process exited 0; log contains SAT_CHARA_APK_BUILT.

## Actual test device

ADB/system properties identified Samsung SC-03K, Android 10, Adreno 630 GPU (OpenGL ES 3.2). Reported MemTotal was 5,713,048 kB. This is the connected test device; the earlier user-mentioned Xiaomi was not the device used for these checks. It has not been designated our final minimum supported hardware.

## Results

| Check | Result / evidence |
|---|---|
| APK install | PASS — streamed install returned Success |
| Cold launch | PASS — am start -W Status ok, COLD, TotalTime 1608 ms |
| Visible scene | PASS — screenshot inspected: landscape UI, ground and seven-stone tower, no pink/missing materials |
| Rebuild button | PASS — actual touch changed score 0–0 → 1–0; app log SAT_CHARA_RULE_SMOKE: score=1, result=Rebuilt |
| Reset button | PASS — actual touch returned score to 0–0; screenshot inspected |
| Background/resume | PASS — Home then relaunch returned HOT/Status ok, preserved scene and score 1–0 |
| App errors in inspected log window | No exception/FATAL matches in the scoped app log sample; this is a short smoke check, not crash-rate certification |
| Automated rules checks | 54 .NET assertions passed; same source also compiled by Unity |
| Full match / AI / movement | NOT IMPLEMENTED in this foundation build |
| 20-minute thermal / frame-time test | NOT TESTED |
| Xiaomi / 4 GB minimum device / broad compatibility | NOT TESTED |
| Clean-checkout second-machine build | NOT TESTED |

## Captures

Only the Sat Chara app was captured. No launcher or unrelated app screen was saved.

- [Initial screen](assets/foundation-initial.png)
- [Successful rebuild](assets/foundation-rebuilt.png)
- [Reset](assets/foundation-reset.png)
- [After resume](assets/foundation-resumed.png)

## Limits and next work

This is a running installation and rules-integration test, not realistic production art or a playable match. The tower is intentionally small in the installation scene; gameplay camera framing will be designed in M1. Full movement, throwing, hit geometry, stone interaction, AI, controls, balance and realistic assets remain to be built. The 42 MB foundation size does not predict the final game's content size or performance.

Next: clean-checkout reproduction for F03, then graybox touch/camera and full 4 vs 4 loop. Keep minimum-device selection and performance certification open.
