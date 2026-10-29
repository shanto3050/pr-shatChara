# Village polish and mobile performance — 29 October 2026

Installed build: **0.2.3, version code 6**. This is a development proof; M2 visual approval and sustained performance certification remain open.

## What changed

Added a neutral blue sky, larger continuous ground, house verandas and gables, banana plants, a tube well and clay vessel shapes. These are scripted approximations, not photo scans or approved final village art. Added a dark scoreboard/instruction backdrop and text shadows for contrast.

The full Bablu export was **65,324 triangles**, above the planned gameplay budget. The derived gameplay mesh is **31,410 triangles**: current shape keys baked, body/clothes reduced, whole hair cards thinned while preserving their UVs and the rig. Original full source is retained. The distant tree is **15,514 triangles versus 46,936** for the near tree, with distant shadow casting disabled.

Added manual Low/Realistic/High presets and delivered-frame interval diagnostics. The first version of these presets still missed the target, prompting mesh and shadow-cost reductions rather than silently lowering the frame-rate goal.

## Actual phone measurements

Samsung SC-03K / Android 10 / Adreno 630, ARM64 GLES3 development APK. Each table entry is a 20-second window after 5 seconds of warm-up. Idle samples are a stationary tower-attack setup, not a full match. Frame rate is measured by runtime frame intervals, not inferred from encoded video.

| Build/settings | Actual render size | Mean FPS | p95 interval | Frames >100 ms |
|---|---|---|---|---|
| 0.2.2 Low, full mesh, short-range real-time shadows | 1110×540 | 21.4 | 50.13 ms | 0 |
| 0.2.2 Realistic, full mesh, 2048 soft shadows, 2x MSAA | 1480×720 | 18.3 | 66.84 ms | 0 |
| 0.2.3 Low, mobile mesh, real-time shadows off | 1110×540 | 29.9 | 33.43 ms | 0 |
| 0.2.3 Realistic, mobile mesh, 1024 hard shadows, no MSAA | 1480×720 | 29.9 | 33.44 ms | 0 |
| 0.2.3 High, mobile mesh, 2048 soft shadows, 2x MSAA | 1850×900 | 29.9 | 33.43 ms | 0 |
| 0.2.3 Realistic, active play while screen recording | 1480×720 | 29.3 | 33.44 ms | 1 |

[Baseline raw samples](assets/village-profile-before.txt) · [Optimized raw samples and gameplay events](assets/village-profile-after.txt).

This is a combined geometry/shadow/MSAA optimization, not an equal-image-quality A/B experiment. Temperature and recording conditions were not controlled: the earlier battery snapshot was 38.6°C and the final snapshot 33.5°C. A pre-optimization Adreno busy-counter snapshot was nearly 100%, suggesting GPU load, but no full CPU/GPU profiler breakdown was captured. The source logs include several further idle windows; those do not replace sustained active-match testing.

Near 30 FPS is encouraging, but p95 is slightly above the literal 33.3 ms target, and active recording included one >100 ms hitch. Its cause needs profiling. Do not mark the performance gate passed. A final memory snapshot was **323584 kB total PSS (316 MiB)**, not peak memory.

## Verification and capture

- Pinned Unity 6000.3.27f1 / URP 17.3.0 compile and APK build succeeded.
- Actual visual-scene simulation passed: **7 rounds, 7 topples, 42 placements, 14 hits, score 2–5, MatchOver**.
- APK installed and launched on the Samsung; all three preset buttons were exercised and actual render sizes logged.
- Realistic touch aiming toppled the tower, movement reached `(2.33, 0.90, -8.52)`, and the phone round ended **Rebuilt, score 1–0**.
- Editor renders and actual phone capture were inspected. Gameplay video is silent H.264, 1280×622, 23.97 seconds. It was normalized to 30 FPS for playback, fully decoded and sampled visually; that encoding rate is not a game-performance measurement.

![Actual phone, Realistic preset](assets/village-polish-phone.png)

[Actual phone gameplay clip](assets/village-polish-demo.mp4)

APK: `unity/SatChara/Builds/Android/SatChara-Village.apk`, **55,282,757 bytes** (55.28 MB), min API 26 / target API 36. SHA-256: `712D4610BA26EA2BA0834CE2C46D5A0FB4AB6636A519D6D3C432E609F8336F92`.

## What remains

All eight players still use one character; animation is procedural, not mocap. Skin/hair, silhouettes, cloth contacts, team presentation, camera direction, final terrain/building detail and lighting remain prototypes. Presets currently share one mobile character mesh; tier-specific LODs, opaque Low hair and blob/contact shadows remain open. The props and vegetation still need authentic reference review.

Next: replace temporary posing with a natural core-animation pipeline, establish the approved look target, investigate the hitch, and run at least 20 minutes of active matches with thermal/frame-time recording on representative devices. No 4 GB compatibility, Xiaomi test, final benchmark match or clean-machine visual APK reproduction is claimed here. No paid assets/services were purchased.
