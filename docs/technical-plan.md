# Technical implementation and verification

Working baseline · 28 October 2026 · Read with production-plan.md

## Project structure

Keep index.html, tools/, and existing reference documents. Create the future Unity project under unity/SatChara/. Suggested Assets/SatChara subfolders: Scenes, Scripts, Art, Animation, Audio, UI, Data, Tests. Commit ProjectSettings, Packages manifests/lockfiles, source assets, and all .meta files. Ignore Library, Temp, Logs, obj, local IDE files, and generated builds. Do not commit signing keys, passwords, device identifiers, or account credentials.

Current foundation: Unity 6000.3.27f1 and URP 17.3.0, with editor-matched Android SDK/NDK/OpenJDK installed. ProjectVersion.txt, manifest.json and packages-lock.json pin the source baseline. See [build instructions](android-build.md) and [setup evidence](setup-status.md). Physical-device suitability and clean-checkout reproduction still require verification.

## Systems and boundaries

| System | Responsibility |
|---|---|
| MatchController | State transitions, round ownership, scoring, victory |
| RulesService | Valid hits, catches, stack sequence, outs, boundary decisions |
| CharacterMotor/Input | Movement, touch commands, cooldowns; same command interface for AI |
| BallController | Possession, release, travel, collision, pickup arbitration |
| StoneController | Pickup/carry/place, reset/recovery, authoritative stack order |
| TeamCoordinator | Role assignment and team-level tactical choices |
| AgentBrain | Perception, reactions, movement and action selection |
| CameraController | Framing, occlusion, threat visibility |
| Presentation | Animations, effects, sound; observes gameplay events |
| Settings/Localization | Quality, audio, language, safe-area UI, persistence |

Use data assets for character stats, difficulty, rules, and quality settings. Separate simulation state from scene effects to make edge cases testable. Avoid architecture packages that add complexity before the full loop exists. Offline first; no backend dependency.

## Initial content budgets

Starting ceilings to profile and revise at M2, not guarantees: eight active characters; Low character LOD around 5–10k triangles, realistic tier around 20–35k for the near LOD; shared/atlased materials where practical; Low character textures 512–1024 px, realistic tier 1–2K for faces and hero surfaces. Hair cards (alpha-tested or dithered) on the realistic tier, opaque hair on Low. A mobile skin shader that approximates subsurface scattering (URP has none built in). Clothing folds baked into meshes; no real-time cloth. Pooled effects, baked environment lighting, a single real-time shadow for characters, limited other shadow casters. Facial rig limited to blinks, a few expressions and eye look-at.

Content beyond about 150 MB ships through Google Play Asset Delivery (install-time asset packs). Large source binaries (FBX, textures, .blend, scans) go in Git LFS.

Measure CPU main thread, render thread, GPU time, allocation spikes, draw calls, overdraw, texture memory, skinning cost, and load time. Triangle count alone is not a performance verdict. Choose texture compression and rendering features through on-device compatibility tests. Add texture streaming only if measurements justify it. Asset Delivery is the planned release route if content exceeds the base-app budget; direct APKs remain the development route.

## Quality presets

Low (simpler look, 4 GB phones): reduced internal resolution, blob shadows, sparse decorative vegetation, lower LODs/textures, opaque hair, tonemapping and color grading only. Realistic (default from SC-03K up): character shadows, hair cards, skin shader, baked GI with light/reflection probes, haze, bloom. High: higher resolution, SSAO, longer shadow distance, denser vegetation, optional 60 FPS. Preserve gameplay geometry, collision, telegraphs, and team readability across presets. Offer manual override; do not infer quality solely from RAM.

### Implemented prototype presets (0.2.3)

All presets currently use the same 31,410-triangle mobile Bablu mesh. Original 65,324-triangle source is preserved. Preset names do not imply completed skin/hair/LOD features from the target specification above.

| Preset | Landscape render height | Main-light shadows | MSAA | Target |
|---|---|---|---|---|
| Low | 540 px, capped to display | Off; blob/contact presentation still open | Off | 30 FPS |
| Realistic (default) | 720 px, capped to display | 1024 hard shadows, 35 m range | Off | 30 FPS |
| High | 900 px, capped to display | 2048 soft shadows, 55 m range | 2x | 30 FPS |

Width follows device aspect ratio. The top-left quality button cycles presets and remembers the choice; do not infer a preset solely from RAM. Resolution and shadow tradeoffs are explicit. The serialized editor pipeline is cloned at runtime so profile changes do not mutate project assets.

MobileVisualQuality logs delivered-frame intervals in 20-second windows after 5 seconds of warm-up, resetting on focus/pause/preset changes. These are wall-clock frame intervals, not CPU/GPU profiler breakdowns or video-derived FPS. Sustained active-match thermal and device-matrix certification remains separate.

### Captured locomotion prototype (0.2.4)

`CapturedLocomotion.json` contains two small CMU-derived direction cycles (34 walk frames, 24 jog frames), shared across avatars. `VillageAvatar` retargets those directions to the current rig, preserves torso bind offsets, blends by measured speed and advances stride phase from actual gameplay travel. It never applies animation root motion to the simulation.

Support contacts inferred from source toe height/velocity drive two-bone leg IK on the flat field. The pose clock freezes when the match or app pauses. Hands, fingers, full axial twist, varied terrain and game-specific action capture remain incomplete. Holding, carrying, ducking and throw follow-through currently use authored overlays. The animation validation tool checks contacts, turning, pause and root ownership; its offline editor captures do not replace actual-device playback review.

## Test strategy

Automated tests should target consequential logic: invalid state transitions, score applied once, hit/placement ordering, ownership arbitration, stack order, eliminated player actions, and reset/recovery. Add scenario tests for interrupted rounds and impossible AI tasks. Do not spend early effort testing cosmetic constants.

Physical-device checks per candidate build:

- Install/update, first launch, complete tutorial and full match.
- Attack misses/hits, all seven placements, all-outs, turn changes, match results, rematch.
- Ball/stone recovery, teammate collisions, obstructed throws, AI stuck recovery.
- Multi-touch, accidental touches, safe areas, camera occlusion, different aspect ratios.
- Background/resume, screen lock, audio focus, app process death and settings persistence.
- Bangla/English text, readable low-quality rendering, audio/vibration settings.
- Warmed-up 20-minute session; frame-time distribution, memory, heat-related slowdown, crash logs.
- Offline launch and play without network access.

Record results in a dated report with commit/build ID, device model/chipset/OS, preset/resolution, duration, measurement method, observations, and pass/fail. Use 'not tested' for absent coverage. Fix or explicitly defer defects; never replace measurements with guessed FPS.

## Build and delivery

Development APKs go to an external artifact location or deliberate release attachment, with checksums and matching commit IDs. Repository history stores source and small reports, not every binary. Before beta establish package ID, versioning, signing ownership, backup, and repeatable build steps. User owns production signing credentials; keep secrets out of source and chat.

Before release verify current official Android/Google Play requirements, target API, supported architectures, privacy/data declarations, content rating, licenses, and store graphics. Do this again near submission because requirements can change. Prepare a concrete release candidate before requesting publication approval.


### Captured action integration (30 October 2026)

`GrayboxMatch` owns fixed-step action time and pending throw/pickup/place transactions. `VillageAvatar` samples `CapturedActions.json` and blends through the same ordered bone bindings as locomotion. A throw releases at the clip's release marker, not at button-up; pickup/place recheck rules and proximity at their marker. Pending pickups reserve stones, and new rounds/deaths clear pending actions. Presentation updates do not advance the action clock. Pausing simulation therefore freezes both poses and transactions. Gameplay owns roots and dodge displacement; captured root travel is not applied. See the [checkpoint](reports/2026-10-30-action-integration.md) for evidence and limitations.


### Village runtime assets (0.2.6)

`VillageProps.cs` converts the supplied FBXs into shared-material combined mesh prefabs, with a per-level source-bounds assertion that preserves FBX root transforms. Blender's `art-source/create_village_lods.py` supplies the heavy-prop distant models. `village-unity-materials.json` maps source material slots to URP textures, tint, cutout/culling and linear metallic/smoothness masks. Generated meshes and the terrain data are Git LFS assets; prefabs, material definitions and metadata remain source-controlled.

`VillageSceneryQuality` applies prop LOD/grass visibility and terrain sampling settings when `MobileVisualQuality` changes. The latter restores its original LOD bias on destruction. The flat two-layer terrain is visual only, adds no collider and keeps the playable rectangle swept clear. See the [village checkpoint](reports/2026-10-30-village-props.md) for measured preset windows and the limits of those measurements. Chhuti's save/dialogue/chapter architecture remains staged work in the [roadmap](chhuti-roadmap.md).
