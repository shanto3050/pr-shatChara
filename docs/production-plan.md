# Sat Chara Android production plan

Version 0.1 · 28 October 2026 · Status: working baseline, open to revision

## 1. Product goal

Build a convincing, realistic 3D Android adaptation of Bangladeshi Sat Chara. Players should recognize both the traditional game and the village setting. Natural movement, responsive controls, readable action, and reliable performance matter as much as visual detail.

The browser game is a reference prototype, not the Android implementation. Preserve it so rules and balance can be compared during development. No Unity project or Android build is delivered by this planning milestone.

## 2. Agreed direction and provisional choices

Agreed: Android; realistic presentation as far as practical; support lower-spec phones; Xiaomi 17 Ultra available for testing; retain an editable plan in GitHub.

Proposed baseline: Unity with Universal Render Pipeline (URP), landscape orientation, offline single-player 4 vs 4 matches, three difficulty levels, one village courtyard, and eight selectable characters. These are planning decisions to validate, not irreversible commitments. Record changes in decisions.md.

Realism means believable proportions, materials, movement, lighting, sound, and village details. Avoid exaggerated heads and cartoon locomotion. Use optimized assets and simplified background geometry where the difference is hard to see. Do not promise photorealism across low-end phones.

## 3. First release scope

Include:

- One complete village field with safe boundaries and readable cover.
- Eight village characters, team selection, four players on each side.
- Tower attack, stone retrieval and rebuilding, defense, passing, dodging, ducking, elimination, scoring, and match results.
- AI allies and opponents; Easy, Normal, Hard.
- Touch controls, contextual tutorial, pause, settings, audio controls.
- Bangla and English UI, readable fonts and language switching.
- Low, Medium, High graphics presets, persistent settings and basic local progression only if time permits after core quality gates.
- Offline play, interruption recovery, signed Android test and release artifacts.

Exclude from first release: online multiplayer, accounts, backend, chat, ads, purchases, open-world exploration, multiple maps, weather cycles, cinematic story, facial capture, and elaborate cloth/hair simulation. Adding any requires an explicit scope revision.

## 4. Device, performance, and size targets

These are hypotheses until a representative low-end device is selected and tested. RAM alone does not define performance; record chipset, GPU, OS, screen resolution, and available storage for each device.

| Tier | Initial target | Quality approach |
|---|---|---|
| Minimum candidate | 4 GB RAM Android phone; exact chipset and OS to be chosen at M0 | Stable 30 FPS, reduced resolution, mostly baked light, simple shadows |
| Mid-range | Representative 6 GB device | 30 FPS with better image quality; optional 60 only if sustained |
| High | User's Xiaomi 17 Ultra | Highest validated detail; optional 60 FPS |

Initial engineering budgets: 30 FPS means 33.3 ms/frame; aim for p95 frame time at or below that during warmed-up active play. Investigate spikes above 100 ms. Target peak process memory below 1 GB on the minimum device, download below 300 MB, installed footprint below 700 MB, cold start below 15 seconds, and fewer than 1% sessions ending in crashes during beta. These are goals, not measured results. Review budgets after the first real build rather than silently weakening them.

Run at least 20 minutes of continuous matches on physical devices to expose heat and throttling. Record quality preset, render resolution, battery/thermal condition, build ID, frame timing, memory, and crashes. The Xiaomi cannot certify the minimum tier. Obtain or borrow a low-end device; emulators and editor profiling are supplementary.

## 5. Rules and gameplay specification

At M1, extract the actual browser behavior into a rules table and compare it with human understanding of Sat Chara. Existing reference: three tower throws, seven stones placed biggest first, stationary ball holders, four-player teams, first to five points. Do not assume every village uses identical rules.

Resolve explicitly: turn changes after misses; valid tower hits; direct versus bounced player hits; catch behavior; head hits; out-of-bounds ball/stone recovery; ball pickup priority; elimination while carrying; simultaneous last placement and hit; round timeout; blocked/unreachable stones; all players out; full-team versus individual scoring; pause/resume. Use deterministic event ordering for simultaneous outcomes.

Implement a match state machine: setup → tower attack → rebuild/defend → round resolution → next round → match results. Provide debug controls to enter each state and inspect ball ownership, elimination, carried stone, and next required stone. Prevent duplicate scores and invalid transitions.

## 6. Controls and camera

Prototype landscape with left virtual stick and right-side contextual actions. Tower attack uses drag/release aiming with a readable trajectory preview limited to the information we want players to have. During defense, aim and release to throw; expose passing without forcing precise taps on moving teammates. During rebuild, pick up/place through clear contextual interaction. Dodge and duck need visible cooldowns.

Test an elevated follow camera against a wider tactical camera before committing. The player must see the tower, immediate threats, and relevant teammates. Handle walls, foliage, and cover occlusion; never let scenery hide an incoming ball without a readable warning. Use subtle team markers that remain legible on low settings.

Acceptance: new testers can move, aim, pass, retrieve, rebuild, and understand being out after the tutorial, without developer coaching. Avoid invisible automation; if pickup or aiming is assisted, communicate it consistently.

## 7. Simulation and AI

Use a controlled character motor, explicit ball ownership and collision rules, and bounded stone physics. Visual realism must not make match outcomes unpredictable. During rebuilding, constrain placed stones to valid stack positions; free rigid-body tower wobble is optional presentation, not the scoring authority.

AI roles: ball retriever, thrower, passing receiver, marker, stone carrier, support runner. Assign roles centrally to avoid every agent chasing the same object. Include reaction delay, imperfect aim, line-of-sight checks, interception, cover use, and stuck recovery. Difficulty changes decisions and execution rather than hidden rule advantages. Do not let AI use unseen player inputs or throw through obstacles.

Preserve seeded match scenarios for repeatable debugging. Port balance concepts from tools/balance-sim.js, but validate the Unity game independently: browser statistics do not establish Android balance.

## 8. Art and animation pipeline

Start with one production-quality character, one tower/ball set, and one courtyard section. Verify their appearance and cost on Android before commissioning all content. Use docs/characters.md for identities, outfits, and provisional stats; this production plan supersedes its former low-poly style direction.

Create consistent reference sheets, human-proportion models, shared compatible humanoid rigs, LODs, texture atlases, collision proxies, and import presets. Generated imagery can guide art direction and textures; it is not automatically a rigged, game-ready 3D asset. Inspect every asset in engine. Track source, license, modifications, and attribution in asset-register.csv. No paid asset or service purchase without user authorization.

Animation priority: idle, locomotion with turns/stops, aim/wind-up/release, pass/catch, carry/place, dodge/duck, hit/out, celebration. Align release and contact events to gameplay. Fix sliding feet, floating hands, snapping turns, and stone clipping. Use shared rigs and retargeting but check clothing and limb proportions per character. Keep signature animations optional until core actions are polished.

Build convincing village identity through composition and material variation, not excessive geometry: tin roofs, packed earth, vegetation, fences, everyday objects, afternoon atmosphere. Bake most static lighting, limit dynamic lights, simplify foliage and transparent layers, and reserve higher shadow quality for stronger devices. Specific budgets are in technical-plan.md.

## 9. Audio, language, and accessibility

Use ball/stone impacts, grounded footsteps, restrained village ambience, and short Bengali calls. No essential information should depend on audio alone. Provide separate music/effects levels, vibration toggle, clear contrast, readable control sizes, and text labels alongside key icons. Have a fluent Bangla reviewer verify spelling, shaping, clipping, and cultural details on-device. Track audio and font licenses.

## 10. Milestones and completion gates

Milestones are ordered gates, not promised dates. Estimates depend on tool availability, asset sourcing, and review turnaround. Finish each gate before expanding scope.

| Milestone | Work and tangible deliverable | Exit gate |
|---|---|---|
| M0 — Foundation | Inspect dev machine; choose supported Unity editor/URP versions and Android toolchain; pin them; choose minimum reference device; initialize Unity project; build instructions and empty-scene APK | APK installs and opens on Xiaomi; low-device test route agreed; repository builds from clean checkout |
| M1 — Rules and input | Audit browser; settle rule edge cases; touch/camera prototypes; graybox full match with debugging | Complete 4 vs 4 match on phone; all round transitions and scoring checked; controls selected from actual tests |
| M2 — Visual/performance proof | One finished character, courtyard section, lighting setup, core animations, quality presets; profiling report | Real assets meet acceptable visual quality and sustained minimum-device performance; budgets revised explicitly if needed |
| M3 — Complete vertical slice | One finished courtyard, all match mechanics, competent AI, tutorial, pause/audio, initial localization | Installable APK gives a complete enjoyable match; low/high device QA passes; known issues recorded |
| M4 — Content and polish | Eight validated characters; complete action animations; final UI/audio/localization; balance tuning | No placeholder assets in release scope; no blocking gameplay defects; licenses complete; repeated playtests understood |
| M5 — Beta | Versioned signed candidate, device matrix, interruption/thermal testing, save recovery, external feedback | Critical/high defects resolved; target performance and size measured; remaining limits documented |
| M6 — Release | Store assets and listing, final policy/SDK review, signed bundle, privacy/data declarations, release checklist | User authorizes publication of a reviewable release candidate; store acceptance checked separately |

Unity installation, asset production, physical device testing, and store submission may require user participation. Report a blocked gate honestly; do not substitute a script, mockup, or queued generation for a running build.

## 11. Work and review method

Before implementation: select a backlog item, read repository instructions, identify acceptance checks. Keep tasks small enough to review. Branches use codex/ prefix. Commit source, settings, .meta files, and documentation; keep generated caches and builds out of Git. Use Git LFS only after agreeing which large binary formats need it and checking remote support.

After each meaningful milestone provide: build/source commit, installable artifact location, short actual-device capture, test device/preset, measured performance, completed acceptance checks, open defects, and proposed next work. Screenshots alone do not prove a playable Android game. Do not call editor-only results device verification.

Update backlog.md as work changes. Update decisions.md when direction changes. Keep plan version/date and a short change entry. A scope change should explain its effect on assets, performance, work remaining, and acceptance criteria. Plans are living documents; approved direction can change without rewriting project history.

## 12. Risks and responses

| Risk | Response |
|---|---|
| Realistic assets exceed low-end budget | Test one finished scene early; reduce resolution, material variety, overdraw, and shadows before multiplying content |
| Natural animation feels unresponsive | Keep gameplay timings authoritative; tune blends and anticipation; preserve readable throw telegraphs |
| AI makes rebuilding unfair or trivial | Seeded scenarios, role coordination, difficulty logs, human matches, independent Unity balance runs |
| Art generation gives inconsistent characters | Approve shared references; use a repeatable modeling/rigging pipeline; inspect all states |
| Lack of low-end physical device | Arrange access during M0; do not claim minimum support based on flagship or emulator |
| Scope grows into online game | Keep offline release gate; evaluate networking as a separate future project phase |
| Tool/account/license constraints | Audit early; document exact blocker and alternatives; seek authorization only for actual purchases or publication |

## 13. Immediate next work

1. Review this plan with the user and record any changes.
2. Audit Unity, Android SDK/JDK, available disk, build tools, and device connectivity without altering unrelated projects.
3. Select/pin supported editor and packages using current official documentation at implementation time.
4. Confirm a low-end reference device and rule variants; proceed with provisional rules while independent setup continues.
5. Complete M0 with a real empty-scene Android build, then begin M1.

## Change log

- 2026-10-28: v0.1, initial Android production baseline. Realistic art replaces the original exaggerated low-poly direction; all performance values remain unverified targets.
