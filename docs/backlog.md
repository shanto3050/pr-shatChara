# Implementation backlog

Working baseline · 28 October 2026

Status: TODO / IN PROGRESS / BLOCKED / DONE. DONE requires the listed evidence. Foundation APK is physically verified; the M1 playable graybox is in development. See [setup status](setup-status.md).

| ID | Gate | Task | Acceptance evidence | Status |
|---|---|---|---|---|
| F01 | M0 | Audit editor, Android tools, storage and device connection | Tool/version inventory and actual blockers in setup-status.md | DONE |
| F02 | M0 | Choose minimum phone and OS baseline | Device/chipset/OS recorded; test access identified | TODO |
| F03 | M0 | Initialize pinned Unity/URP project and Git ignores | Pinned project imports/compiles and scene test passes from clean source archive 12eeada without original Library; see graybox report | DONE |
| F04 | M0 | Build and install foundation Android scene | APK verified; install/launch/buttons/resume passed on connected Samsung SC-03K, Android 10; see reports/2026-10-28-foundation.md | DONE |
| G01 | M1 | Audit prototype rules and resolve edge cases | Source rules table in rules-audit.md; edge-case decisions pending | IN PROGRESS |
| G02 | M1 | Compare touch and camera schemes | Phone clip verifies aim/movement/pause; two cameras captured, wide retained; uncoached feedback/multitouch/readability work pending | IN PROGRESS |
| G03 | M1 | Implement match state machine and scoring | 54 rule assertions, full scene match, real-device Rebuilt/AllOut scoring and New match reset verified; see graybox report | DONE |
| G04 | M1 | Implement movement, ball and seven stones | Playable APK and scene tests pass; touch aim/movement/rounds verified; dedicated pass/dodge/duck and rule review pending | IN PROGRESS |
| G05 | M1 | Add team coordination and baseline AI | Carrier/retriever/thrower coordination and complete automated match pass; physical rounds observed; human playtests/tactical/balance review pending | IN PROGRESS |
| V00 | M2 | Set up Git LFS for large art binaries; remove duplicated textures; fill asset-register.csv for all assets already added | LFS tracking committed; register lists every current asset with source and license | DONE |
| V01 | M2 | Reference photo shoot (village field, houses, objects, children's clothing); mood board with Real Cricket 24 captures; target frame | Photos in repo (LFS) or linked; mood board and target frame approved by user | TODO |
| V01b | M2 | Decide character source (D16): free Bablu proof, paid tool or 3D artist | Unity/device comparison and decision recorded; any purchase authorized by user | TODO |
| V02 | M2 | Integrate one realistic rigged character with motion-captured throw, carry/place, duck and sidestep | Android capture; feet, contacts and release timing checked; side-by-side with target frame | IN PROGRESS |
| V03 | M2 | Build finished courtyard section (photogrammetry/photo textures) and golden-hour lighting; broadcast camera | On-device capture matches target frame; user sign-off | IN PROGRESS |
| V04 | M2 | Implement quality presets and profile devices | Provisional resolution/shadow/MSAA presets and short-window frame diagnostics implemented; device/thermal certification remains open | IN PROGRESS |
| S01 | M3 | Finish courtyard and all core interactions | Complete playable match in real scene | TODO |
| S02 | M3 | Add tutorial, pause, settings and initial languages | Uncoached player completes basics; UI inspection | TODO |
| S03 | M3 | Tune AI and gameplay feedback | Seeded scenarios and human playtest findings | TODO |
| C01 | M4 | Complete eight distinct characters and team selection | All rigs/actions/LODs inspected; stats reviewed | TODO |
| C02 | M4 | Complete audio, UI and localization | Fluent Bangla review; asset register complete | TODO |
| C03 | M4 | Balance all difficulties and remove placeholders | Match data and release-scope asset audit | TODO |
| B01 | M5 | Device, interruption and endurance QA | Completed matrix, defects and regression results | TODO |
| B02 | M5 | Establish signing, versioning and distribution | Reproducible signed beta; keys kept private | TODO |
| B03 | M5 | External playtest and fixes | Feedback summary; critical/high issues resolved | TODO |
| R01 | M6 | Store compliance and listing preparation | Current requirement review and reviewable listing | TODO |
| R02 | M6 | Approve and publish candidate | Explicit user publication approval; release verification | TODO |

Plan v0.2 (29 October 2026) makes realistic graphics the primary goal; see D15–D19. Start V00 and V01 now, since they don't depend on M1.

Next: V00 asset organization and V01 visual reference work, followed by one character/courtyard Unity proof and Android comparison (V02/V03). Dedicated pass/dodge/duck/multitouch checks, rules review and AI balance remain open M1 work. Full roster production stays gated by V04. See reports/2026-10-28-graybox.md.
