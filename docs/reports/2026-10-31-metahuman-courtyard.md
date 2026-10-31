# Clothed MetaHuman courtyard checkpoint

31 October 2026. The actual MetaHuman now runs in a separate Android walking trial. This checkpoint does not replace the full match character or close the art gate.

## Current installed build: 0.3.2

The phone now has **0.3.2, code 13**. This adds a courtyard-only stop-heading fix: the character keeps his travel direction rather than turning back toward the legacy throw direction. A rightward movement logged 89.9 degrees; a paused check 2.5 seconds later logged 90.0 degrees. The stationary baked body minimum was -0.0198 m, using four-weight skinning.

Current APK size: **90,347,399 bytes**. SHA-256: `E87412D7A510F322D5FD21F0F41C0C5B3C854C525B3DE0D6AE24D2221087FBC9`. The local APK path is the same as below; successive development builds overwrite that file.

A 20.03-second sample spanning the recorded 0.3.2 control test reported 29.9 FPS, p95 33.46 ms, p99 33.94 ms and no frames over 100 ms. A post-test PSS snapshot was 405,348 KiB, about 396 MiB. The geometry budget is unchanged. These remain single-active-character smoke tests on the Samsung phone.

The verified compact 0.3.2 preview is `.verification/metahuman-unity/phone-meta-032-preview-short.mp4` (H.264, 1280 x 624). Its full decode and sampled frames were checked. The app was restarted after testing and left at the initial courtyard view, ready for manual play.

## Implemented

- Fitted the lungi and gamcha to the new skeleton. Rebuilt the vest on the MetaHuman torso with a U neckline, shoulder coverage and matching body weights. The old body's crouch correction was removed; it is not valid for this body.
- Normalized all skinned meshes into the same armature-local bind space. The initial mixed-scale export looked plausible at rest but failed in motion; the corrected export was checked with baked skinned pose captures.
- Attached captured locomotion through the shared avatar builder. Inspected four jog phases. Cloth folds, contacts and all action poses still need further work.
- Added `MetaHumanCourtyard.unity`, using the clothed MetaHuman prefab and the existing third-person controller. It starts in walking-only mode; match actions are disabled, and the HUD shows movement/look instructions and Reset.
- Enforced four skinning influences per renderer. Mobile's default two-influence quality setting differed from the four-weight grounding calculations. Skinning and the cached grounding probes now use the same influence count.

The dressed trial has **52,599 triangles, 40,784 vertices, 10 skinned renderers and 55 weighted bones**. These are the current hero trial's source counts, not an approved eight-character budget. Lower-detail NPC variants remain necessary work.

## Initial 0.3.1 Android artifact

- Version: **0.3.1, code 12**, ARM64 development build.
- APK: `unity/SatChara/Builds/Android/SatChara-MetaHumanCourtyard.apk`.
- File size: **108,026,676 bytes**.
- SHA-256: `A64F86EFF80E78FDA30279DE2CC6A691AB964CD7412261C453369457D2067D07`.
- Installed and launched on the connected Samsung SC-03K test phone. Earlier iterations used the same development version code; the size/hash identify the tested final artifact.

Orbit gestures, forward movement and lateral movement were exercised. Grounding logs reported four-weight skinning and sampled baked body minima from **-0.0249 m to -0.0193 m**, against terrain at **-0.025 m**. This verifies the sampled walking contacts, not every action or every terrain slope.

The Realistic preset rendered at **1480 x 720**. Short 20-second samples around the control test reported **29.9 FPS**, p95 about **33.45 ms**, p99 up to **34.36 ms**, and no frames over 100 ms in those samples. A post-control-test PSS snapshot was **400,763 KiB, about 391 MiB**. These are development smoke-test observations with one active character, not a sustained thermal test or proof of the 4 GB minimum.

[Actual phone view](../mockups/metahuman/bablu-courtyard-phone.png) · [Unity baked jog pose](../mockups/metahuman/bablu-clothed-jog-trial.png)

The local phone recording is `.verification/metahuman-unity/phone-meta-review.mp4`, H.264 at 1480 x 720. It was retrieved from the device, trimmed to the camera/movement portion, decoded for verification and inspected through sampled frames. The video uses the current village prototype; it is not the final environment graphics target.

## Open work, in order

1. Review cloth penetration throughout walk/run transitions and turns; finish neckline/seams, gamcha drape, hair/brows, eye shading, body tone and teenage likeness. The outfit and face are not final art.
2. Retarget and inspect pickup, placement, aim, throw, crouch and hit reactions. Generate new garment corrections for the new body where needed. Do not restore the old corrective offsets.
3. Reintroduce the approved character into a match review and benchmark eight active characters with appropriate LODs.
4. Finish courtyard lighting, contact shadows, scenery collisions, vegetation, sound and HUD against the immersive direction.
5. Perform sustained active play and test a representative 4 GB phone before setting official minimum requirements.

The 0.3.1 phone trial intentionally offers walking and camera inspection. The full-match source scene still retains the fallback character. Unity remains the runtime; Unreal remains the MetaHuman authoring tool. Runtime/source asset integration is local while these gates remain open; the published report and renders document progress.
