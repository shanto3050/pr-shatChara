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
| V01 | M2 | Establish realistic art references and source register | Consistent character/environment direction and licenses | TODO |
| V02 | M2 | Integrate one rigged character and core motion | Android capture; feet, contacts and release timing checked | TODO |
| V03 | M2 | Build finished courtyard section and lighting | Approved visual proof rendered in game | TODO |
| V04 | M2 | Implement quality presets and profile devices | Dated physical-device performance report | TODO |
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

Next: dedicated pass/dodge/duck/multitouch checks, human feedback, camera/HUD iteration and AI balance; finish G01 rules review and select minimum hardware for F02. Full realistic content production stays gated by V04. See reports/2026-10-28-graybox.md.
