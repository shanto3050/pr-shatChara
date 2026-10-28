# Technical implementation and verification

Working baseline · 28 October 2026 · Read with production-plan.md

## Project structure

Keep index.html, tools/, and existing reference documents. Create the future Unity project under unity/SatChara/. Suggested Assets/SatChara subfolders: Scenes, Scripts, Art, Animation, Audio, UI, Data, Tests. Commit ProjectSettings, Packages manifests/lockfiles, source assets, and all .meta files. Ignore Library, Temp, Logs, obj, local IDE files, and generated builds. Do not commit signing keys, passwords, device identifiers, or account credentials.

Pin the editor version only after checking current support, Android requirements, and installed tooling. Pin URP and package dependencies; document exact clean-checkout build steps. This plan does not claim a particular version is currently installed or suitable.

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

Starting ceilings to profile and revise at M2, not guarantees: eight active characters; low-tier character LOD around 5–10k triangles and medium around 15–25k; shared/atlased materials where practical; low-tier character textures primarily 512–1024 px; 2K textures reserved for visible hero surfaces on higher settings. Prefer simple opaque hair, static clothing, pooled effects, baked environment lighting, and limited shadow-casting objects. Avoid per-character real-time cloth and expensive full-screen effects in the baseline.

Measure CPU main thread, render thread, GPU time, allocation spikes, draw calls, overdraw, texture memory, skinning cost, and load time. Triangle count alone is not a performance verdict. Choose texture compression and rendering features through on-device compatibility tests. Include texture streaming or asset delivery systems only if measurements justify their complexity.

## Quality presets

Low: reduced internal resolution, short shadow distance or blob shadows, sparse decorative vegetation, lower LODs/textures, minimal post-processing. Medium: improved resolution, selected real-time shadows, denser surroundings. High: highest validated resolution/detail/shadows and optional 60 FPS. Preserve gameplay geometry, collision, telegraphs, and team readability across presets. Offer manual override; do not infer quality solely from RAM.

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
