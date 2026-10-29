# Sat Chara Android production plan

Version 0.2 · 29 October 2026 · Status: working baseline, open to revision

## 1. Product goal

Build a convincing, realistic 3D Android adaptation of Bangladeshi Sat Chara. Players should recognize both the traditional game and the village setting. Natural movement, responsive controls, readable action, and reliable performance matter as much as visual detail.

The browser game is a reference prototype, not the Android implementation. Preserve it so rules and balance can be compared during development. No Unity project or Android build is delivered by this planning milestone.

## 2. Agreed direction and provisional choices

Agreed: Android; **realistic graphics are the primary goal**; retain an editable plan in GitHub.

Agreed 29 October 2026 (D15–D19):

- **Realism first on mid and high phones.** Lower-spec phones are supported through a Low preset that is allowed to look clearly simpler. Low-end support no longer limits the target look.
- **Visual benchmark: Real Cricket 24**, a realistic South Asian sports game on mid-range Android. It is the reference for character, lighting and camera quality (see "Visual target" below).
- **Camera:** a broadcast-style sports camera as the default, with a wide tactical view as an option.
- **Real reference photography** of a Bangladeshi village field, houses, objects and children's clothing is available and is used for authenticity, textures and photogrammetry.
- Test phones: Samsung SC-03K (Galaxy S9+ class: Snapdragon 845, Adreno 630, ~6 GB RAM) is the current minimum for the realistic tier. A Xiaomi 17 Ultra is mentioned as available but has not been used yet.

Baseline: Unity with Universal Render Pipeline (URP), landscape orientation, offline single-player 4 vs 4 matches, three difficulty levels, one village courtyard, and eight selectable characters. Unreal Engine 5 was considered: it is stronger at realism on PC, but its main realism features (Lumen, Nanite) don't run on mobile and its Android builds are heavy, so Unity URP stays. Record changes in decisions.md.

Realism means believable proportions, skin, cloth and hair, natural motion-captured movement, grounded lighting, and authentic village details. Avoid exaggerated heads and cartoon locomotion. Use optimized assets and simplified background geometry where the difference is hard to see.

### Visual target

Before producing final art, agree on a **look-development target**: a mood board from the reference photos and benchmark captures, plus one target frame (a mock-up still of the courtyard during play). M2 passes only when an on-device capture is compared side by side with that frame and the benchmark, and the user signs off.

What "Real Cricket 24 level" means here, and what to expect:

| Area | Expectation |
|---|---|
| Lighting and atmosphere | Achievable at a similar level: fixed golden-hour lighting, baked GI, light and reflection probes, haze, color grading |
| Environment | Achievable and potentially more authentic, using photogrammetry of real objects and photo-based textures |
| Camera presentation | Achievable: broadcast camera, close-ups, replays |
| Movement | Close, if game actions are motion-captured (phone-based mocap) and cleaned up; not with procedural posing |
| Characters (faces, skin, hair, clothing) | The hardest gap. A studio benchmark relies on dedicated character artists. Matching it needs a paid character tool or a 3D character artist; code-generated or free base meshes will look noticeably weaker |

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
| Low (supported, simpler look) | 4 GB RAM Android phone; exact chipset and OS still to be chosen | Stable 30 FPS; reduced resolution, lower LODs, opaque hair, blob shadows. Allowed to look clearly simpler |
| Realistic minimum | Samsung SC-03K / Galaxy S9+ class (Snapdragon 845, ~6 GB) | Stable 30 FPS with the realistic look: baked lighting, character shadows, hair cards |
| High | Recent flagship (e.g. Xiaomi 17 Ultra, if available for testing) | Full detail, higher resolution and shadows; optional 60 FPS |

Initial engineering budgets: 30 FPS means 33.3 ms/frame; aim for p95 frame time at or below that during warmed-up active play. Investigate spikes above 100 ms. Peak process memory below 1.5 GB on the realistic minimum and below 1 GB on Low. Download around 150 MB for the base app, with the realistic content delivered through Google Play Asset Delivery; total download up to about 1 GB. Cold start below 15 seconds, and fewer than 1% of sessions ending in crashes during beta. These are goals, not measured results. Review budgets after the first real build rather than silently weakening them.

Run at least 20 minutes of continuous matches on physical devices to expose heat and throttling. Record quality preset, render resolution, battery/thermal condition, build ID, frame timing, memory, and crashes. The Xiaomi cannot certify the minimum tier. Obtain or borrow a low-end device; emulators and editor profiling are supplementary.

## 5. Rules and gameplay specification

At M1, extract the actual browser behavior into a rules table and compare it with human understanding of Sat Chara. Existing reference: three tower throws, seven stones placed biggest first, stationary ball holders, four-player teams, first to five points. Do not assume every village uses identical rules.

Resolve explicitly: turn changes after misses; valid tower hits; direct versus bounced player hits; catch behavior; head hits; out-of-bounds ball/stone recovery; ball pickup priority; elimination while carrying; simultaneous last placement and hit; round timeout; blocked/unreachable stones; all players out; full-team versus individual scoring; pause/resume. Use deterministic event ordering for simultaneous outcomes.

Implement a match state machine: setup → tower attack → rebuild/defend → round resolution → next round → match results. Provide debug controls to enter each state and inspect ball ownership, elimination, carried stone, and next required stone. Prevent duplicate scores and invalid transitions.

## 6. Controls and camera

Prototype landscape with left virtual stick and right-side contextual actions. Tower attack uses drag/release aiming with a readable trajectory preview limited to the information we want players to have. During defense, aim and release to throw; expose passing without forcing precise taps on moving teammates. During rebuild, pick up/place through clear contextual interaction. Dodge and duck need visible cooldowns.

Default to a **broadcast-style sports camera**: lower and closer than a tactical view, so characters, movement and materials are visible, while still framing the tower, immediate threats and relevant teammates. Keep the wide tactical view as a player option. Add short presentation cameras where realism pays off: throw wind-up, tower falling, an out, the "সাতচারা!" celebration, and an optional replay. Presentation cameras never take control away during live play. Handle walls, foliage, and cover occlusion; never let scenery hide an incoming ball without a readable warning. Use subtle team markers that remain legible on low settings.

Acceptance: new testers can move, aim, pass, retrieve, rebuild, and understand being out after the tutorial, without developer coaching. Avoid invisible automation; if pickup or aiming is assisted, communicate it consistently.

## 7. Simulation and AI

Use a controlled character motor, explicit ball ownership and collision rules, and bounded stone physics. Visual realism must not make match outcomes unpredictable. During rebuilding, constrain placed stones to valid stack positions; free rigid-body tower wobble is optional presentation, not the scoring authority.

AI roles: ball retriever, thrower, passing receiver, marker, stone carrier, support runner. Assign roles centrally to avoid every agent chasing the same object. Include reaction delay, imperfect aim, line-of-sight checks, interception, cover use, and stuck recovery. Difficulty changes decisions and execution rather than hidden rule advantages. Do not let AI use unseen player inputs or throw through obstacles.

Preserve seeded match scenarios for repeatable debugging. Port balance concepts from tools/balance-sim.js, but validate the Unity game independently: browser statistics do not establish Android balance.

## 8. Art and animation pipeline

Start with one production-quality character, one tower/ball set, and one courtyard section. Verify their appearance and cost on Android before commissioning all content. Use docs/characters.md for identities, outfits, and provisional stats; this production plan supersedes its former low-poly style direction.

Create consistent reference sheets, human-proportion models, shared compatible humanoid rigs, LODs, texture atlases, collision proxies, and import presets. Generated imagery can guide art direction and textures; it is not automatically a rigged, game-ready 3D asset. Inspect every asset in engine. Track source, license, modifications, and attribution in asset-register.csv for every asset as it is added. No paid asset or service purchase without user authorization.

### Who makes what

| Asset type | Source |
|---|---|
| Village props and buildings (stones, haystacks, fences, tin-roof and mud houses, tube well, drums) | Built by script (Blender Python, procedural meshes) and/or **photogrammetry** of real objects from the reference shoot, then cleaned and optimized |
| Ground, wall, roof and cloth textures | Reference photos made tileable; CC0 libraries (Poly Haven, ambientCG) where they fit |
| Vegetation (banana, areca and coconut palms, bamboo, grass) | CC0 or licensed assets, adapted; scanned leaves where useful |
| Lighting, materials, shaders (including a mobile skin shader), post-processing, LODs, import tooling | Code and configuration |
| **Realistic characters** (faces, skin, hair, clothing) | **Open decision (D16):** a paid character tool (e.g. Reallusion Character Creator 4) or a commissioned 3D character artist. MakeHuman/MPFB output is a placeholder only: its current model is an adult in Western clothing and doesn't match the roster |
| Clothing folds (lungi, dupatta, kameez, frock) | Simulated offline (e.g. Marvelous Designer or Blender cloth) and baked into the mesh; no real-time cloth |
| Animation | Mixamo for basic movement; **phone-based motion capture** (e.g. Move.ai, Rokoko Video) for the game's own actions (overarm throw, crouch-and-stack, duck, sidestep); Unity Animation Rigging for foot locking and hand reach. Adjust adult motion for children's proportions. Procedural posing (VillageAvatar.cs) is a stopgap, not the final animation |

Animation priority: idle, locomotion with turns/stops, aim/wind-up/release, pass/catch, carry/place, dodge/duck, hit/out, celebration. Align release and contact events to gameplay. Fix sliding feet, floating hands, snapping turns, and stone clipping. Use shared rigs and retargeting but check clothing and limb proportions per character. Keep signature animations optional until core actions are polished. Faces: blinking, a few expressions, and eyes that track the ball; no facial capture.

### Lighting and look

Fix one time of day: late-afternoon golden hour. HDRI sky, baked global illumination with light probes for characters and reflection probes, one real-time directional shadow for characters, baked ambient occlusion, light humid haze for depth, ACES or neutral tonemapping with a color-grading LUT, and subtle bloom. Higher presets add screen-space ambient occlusion and longer shadow distance.

### Village authenticity

Build the village from the reference photos, not generic assets: packed earth with footpaths, banana/areca/coconut palms, bamboo clumps and fences, tin-roofed and mud houses, haystacks, dung cakes drying on a wall, a tube well, a pond edge, clothes lines, a van-rickshaw, curious villagers on the sideline. Composition and material variation carry the identity, not excessive geometry. Limit dynamic lights, simplify foliage and transparent layers. Specific budgets are in technical-plan.md. A fluent reviewer checks clothing, objects and play style for cultural accuracy, as well as the Bangla text.

## 9. Audio, language, and accessibility

Use ball/stone impacts, grounded footsteps, restrained village ambience, and short Bengali calls. No essential information should depend on audio alone. Provide separate music/effects levels, vibration toggle, clear contrast, readable control sizes, and text labels alongside key icons. Have a fluent Bangla reviewer verify spelling, shaping, clipping, and cultural details on-device. Track audio and font licenses.

## 10. Milestones and completion gates

Milestones are ordered gates, not promised dates. Estimates depend on tool availability, asset sourcing, and review turnaround. Finish each gate before expanding scope.

| Milestone | Work and tangible deliverable | Exit gate |
|---|---|---|
| M0 — Foundation | Inspect dev machine; choose supported Unity editor/URP versions and Android toolchain; pin them; choose minimum reference device; initialize Unity project; build instructions and empty-scene APK | APK installs and opens on Xiaomi; low-device test route agreed; repository builds from clean checkout |
| M1 — Rules and input | Audit browser; settle rule edge cases; touch/camera prototypes; graybox full match with debugging | Complete 4 vs 4 match on phone; all round transitions and scoring checked; controls selected from actual tests |
| M2 — Visual/performance proof | Reference photo shoot; mood board and target frame; character-source decision (D16); one finished character with mocap actions; courtyard section; lighting setup; broadcast camera; quality presets; profiling report | On-device capture matches the target frame and benchmark side by side, signed off by the user; sustained 30 FPS on the realistic minimum (SC-03K) and on Low; budgets revised explicitly if needed |
| M3 — Complete vertical slice | One finished courtyard, all match mechanics, competent AI, tutorial, pause/audio, initial localization | Installable APK gives a complete enjoyable match; low/high device QA passes; known issues recorded |
| M4 — Content and polish | Eight validated characters; complete action animations; final UI/audio/localization; balance tuning | No placeholder assets in release scope; no blocking gameplay defects; licenses complete; repeated playtests understood |
| M5 — Beta | Versioned signed candidate, device matrix, interruption/thermal testing, save recovery, external feedback | Critical/high defects resolved; target performance and size measured; remaining limits documented |
| M6 — Release | Store assets and listing, final policy/SDK review, signed bundle, privacy/data declarations, release checklist | User authorizes publication of a reviewable release candidate; store acceptance checked separately |

Unity installation, asset production, physical device testing, and store submission may require user participation. Report a blocked gate honestly; do not substitute a script, mockup, or queued generation for a running build.

## 11. Work and review method

Before implementation: pull the latest main, select a backlog item, read repository instructions, identify acceptance checks. Keep tasks small enough to review. Branches use codex/ prefix. Commit source, settings, .meta files, and documentation; keep generated caches and builds out of Git. Realistic art will add large binaries (FBX, textures, Blender files, scans): set up Git LFS for them before adding more, remove duplicated textures, and check GitHub's LFS storage and bandwidth limits (paid data packs may be needed; ask first).

After each meaningful milestone provide: build/source commit, installable artifact location, short actual-device capture, test device/preset, measured performance, completed acceptance checks, open defects, and proposed next work. Screenshots alone do not prove a playable Android game. Do not call editor-only results device verification.

Update backlog.md as work changes. Update decisions.md when direction changes. Keep plan version/date and a short change entry. A scope change should explain its effect on assets, performance, work remaining, and acceptance criteria. Plans are living documents; approved direction can change without rewriting project history.

## 12. Risks and responses

| Risk | Response |
|---|---|
| Realistic assets exceed the realistic-minimum budget | Test one finished scene early on SC-03K; reduce resolution, material variety, overdraw, and shadows before multiplying content |
| Characters fall short of the benchmark | Decide the character source (D16) at the start of M2; prove one character on-device before the other seven |
| Motion looks robotic | Motion-capture game-specific actions; never ship procedural posing as final animation |
| Village looks generic | Reference shoot and photogrammetry before environment production; cultural review |
| Repository grows too large | Git LFS for large binaries; no duplicate textures; build outputs stay out of Git |
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

- 2026-10-29: v0.2, realism review. Realistic graphics become the primary goal on mid/high phones with a simpler Low preset; Real Cricket 24 as visual benchmark; look-dev target frame and user sign-off gate M2; broadcast camera default; reference photography and photogrammetry; character source as an open budget decision; motion capture for game actions; lighting look defined; download budget moved to Play Asset Delivery; Git LFS before more art (D15–D19).
- 2026-10-28: v0.1, initial Android production baseline. Realistic art replaces the original exaggerated low-poly direction; all performance values remain unverified targets.
