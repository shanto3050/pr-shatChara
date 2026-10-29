# Village visual proof — 29 October 2026

Status: early graphical integration, not M2 approval or benchmark parity.

## Changes

Bablu v2 now has an exported skinned FBX, explicit URP materials and a reusable prefab. All eight slots use this one character for the proof. The courtyard has textured earth, plastered houses, tin roofs, wooden shutters, fences, trees, drums and a small flattened seven-stone tower. VillageBuild can author, capture, validate and build the scene; its incomplete-code guard is removed.

Legacy images were importing as cubemaps rather than 2D textures. Corrected that and bypassed Blender offline material conversion through standard named slots plus explicit URP materials. The first phone check also exposed cropped foreground players and oversized labels; camera framing and label sizing were revised.

The free Bablu route is evaluated before any paid character purchase. Git LFS is configured for art binaries without rewriting history; duplicate FBX companion PNGs were hash-verified against canonical copies before removal. The asset register and reproduction notes were expanded.

## Verification

- Unity 6000.3.27f1 / URP 17.3.0; ARM64 Android development build, GLES3, minimum API 26, target API 36.
- Independent rule harness: **54 assertions passed**.
- Actual visual scene simulation: **7 rounds, 7 topples, 42 placements, 14 hits, score 2–5, MatchOver**. This checks gameplay wiring; it does not prove animation quality, touch usability or balance.
- Unity URP camera renders inspected; Blender offline renders were not used as engine evidence.
- Samsung SC-03K, Android 10: graphical APK 0.2.0 installed and launched. Textured characters/environment visibly rendered. A touch-aim throw toppled the smaller tower. Camera/HUD issues found on this device triggered the 0.2.1 update.
- Brief 0.2.0 memory snapshot: total PSS **398032 kB** (about 389 MiB). This is one snapshot, not peak memory or a low-tier performance certification.
- Final **0.2.1 (version code 4)** APK built, installed and launched successfully. Actual phone capture confirms the controlled team stays above the controls with smaller labels. A touch-aim throw again toppled the tower and entered Rebuild. Touch movement was exercised during the recording; dedicated control regression checks remain open.
- APK file size: **62,879,393 bytes** (62.88 MB). SHA-256: `E8AC66A9BC7BDDEBF9F4341955ED7A971C64365BDF7218F30B4F71C43587C67C`.

![Actual Samsung SC-03K capture, version 0.2.1](assets/village-phone.png)

[Actual-device gameplay clip (silent)](assets/village-phone-demo.mp4) — 19.17 seconds, H.264, 1280×622. Android screen recording was normalized to 30 FPS for playback and fully decoded successfully; the encoded rate is not a measurement of game FPS. A sampled frame confirms the tower-scatter/rebuild action.

## Remaining work and limitations

The character is an experiment, not an approved final asset. All players look identical, motion is procedural rather than captured, hands/feet and cloth intersections need animation work, and team markers/UI remain prototype presentation. Buildings are simple scripted approximations; authentic reference photography, terrain composition, suitable local vegetation and final prop detail are still needed. Lighting is a provisional directional/ambient setup, not completed baked GI and probe authoring.

No sustained frame-time/thermal run, quality-preset comparison, 4 GB device certification, Xiaomi test or clean-machine visual APK reproduction was completed in this checkpoint. A running textured scene is progress toward the benchmark, not evidence that the benchmark has been matched. M2 and V04 remain open.

Next: approve a look-development target from real references, improve one character and core animation, refine the court and camera/HUD, then measure quality presets on-device before expanding the roster.

## Reproduce

Install Git LFS and pull its objects after cloning. Open `unity/SatChara` in the pinned Unity editor with Android modules. Run `SatChara.Editor.VillageBuild.VerifyAndBuild` for simulation, URP captures and APK generation. The APK is written to `unity/SatChara/Builds/Android/SatChara-Village.apk`; generated builds remain out of Git. Captures under `.verification/village` are editor-only unless explicitly labelled as phone images.
