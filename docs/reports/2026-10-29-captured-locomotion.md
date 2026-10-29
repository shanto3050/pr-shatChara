# Captured locomotion checkpoint — 29 October 2026

Build **0.2.4, version code 7**, installs and renders on Samsung SC-03K. Editor animation/match checks passed. **Active phone movement, changed throwing pose and pause/resume verification remain pending because the phone locked before the input/recording test.** The failed 5304-byte phone recording is excluded from delivery. The previous 0.2.3 report remains the last completed touch-gameplay verification.

## Implemented

Replaced the sine-wave walk/run leg posing with recorded CMU walking and jogging, direction-space retargeting to the existing MPFB rig, distance-driven stride phase, smooth walk/jog blending, captured pelvis/torso movement, and two-bone support-foot locking on the flat field. Animation does not move the authoritative player root. The presentation clock freezes with in-game/application pause. Holding/wind-up, carrying, ducking and release follow-through are authored overlays, not new motion-capture recordings.

The torso/neck preserves the target rig's bind offsets instead of copying a different skeleton's spinal curvature. Ground offset carries through the jog flight phase rather than snapping back to standing height. Gamcha weights attach to the torso so arm movement does not pull it upward; cloth is still rigid/skinned and needs further cleanup.

## Source and reproducibility

Official sources: [CMU subject 02](http://mocap.cs.cmu.edu/search.php?subjectnumber=02) and [reuse terms](http://mocap.cs.cmu.edu/faqs.php). The permission grant, credit and numerical source provenance are recorded in `art-source/licenses/CMU-Mocap.md` and `art-source/motion/cmu/manifest.json`. This data is not labeled CC0. No paid asset/service was used.

| Motion | Source | Source rate | Selected source frames | Converted cycle |
|---|---|---|---|---|
| Walk | 02_01.amc | 120 Hz | 134–266 | 34 samples, 1.1 seconds |
| Jog | 02_03.amc | 120 Hz | 49–141 | 24 samples, 0.766667 seconds |

The original ASF/AMC files are included, hashed and preserved byte-for-byte through Git attributes. Run `convert_cmu_motion.py` with Blender Python to verify those hashes and regenerate the compact `CapturedLocomotion.json` (40,156 bytes). The converter removes heading/root travel, chooses a complete stride and blends the loop seam. Runtime stride timing follows gameplay travel rather than moving the player from animation.

## Checks

`SatChara.Editor.VillageBuild.VerifyAnimationAndBuild` passed:

- Walking at 1.3 m/s and jogging at 3.5 m/s, each for 360 deterministic 20 ms steps with a 90-degree turn halfway through.
- Walk: 414 planted-foot samples, 389 continued-contact samples. Jog: 227 planted-foot samples, 190 continued-contact samples.
- Logged anchor error and horizontal slip stayed below the **2.5 cm test tolerance** (rounded log values 0.00000 m). Foot-joint floor proxies stayed above ground. These are ideal flat-ground checks, not a guarantee of perfect mesh contacts or artistic quality.
- Gameplay roots stayed unchanged by animation; a paused step held the foot pose; no non-finite foot positions occurred.
- Full visual-scene match: **7 rounds, 7 topples, 42 placements, 14 hits, score 2–5, MatchOver**.
- Unity compilation and Android build succeeded. The phone confirmed version 0.2.4, and pre-lock idle Realistic windows remained around **29.9 FPS at 1480×720**, p95 about 33.45 ms. This does not establish active-motion performance or the 20-minute thermal gate.

## Editor preview — not a phone recording

[Close-up walk then jog preview](assets/captured-motion-editor-preview.mp4): four seconds, silent H.264, 1280×720, 30 FPS encoding. It was rendered offline from deterministic controller steps, using temporarily baked pose meshes for URP capture, then fully decoded and sampled visually. The encoded frame rate is not measured runtime performance.

| Walk | Jog |
|---|---|
| ![Editor walk](assets/captured-walk-editor.png) | ![Editor jog](assets/captured-jog-editor.png) |

Run `CaptureMotionPreview` for the two 60-frame editor sequences. `ValidateAnimation` produces stride snapshots and contact/turn/pause assertions. Those tools do not certify on-device animation.

APK: `unity/SatChara/Builds/Android/SatChara-Village.apk`, **55,297,825 bytes**. SHA-256: `F9E0DBF1EC6D3EDA5986B16D8428DD5E6B3EA019A174436A76E98453F110C9F3`. Minimum API 26, target API 36, ARM64 GLES3 development build.

## Open work

Unlock the phone and verify actual movement, touch aiming/toppling with the changed hand pose, pause/resume and frame intervals. Game-specific throw/place/duck/sidestep recordings, directional starts/stops/turning cleanup, child-specific movement, clothing contacts, full axial twist, hand/finger poses and varied-terrain foot placement remain open. Contact labels here are inferred from source toe height/velocity, not manually annotated ground truth. All eight players share the same prototype body and locomotion bank. M2 visual approval, natural-animation approval and sustained device testing are not complete.
