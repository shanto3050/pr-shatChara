# Implementation backlog

Working baseline · 28 October 2026

Status: TODO / IN PROGRESS / BLOCKED / DONE. DONE requires the listed evidence. Foundation work has started; no Android build exists yet. See [setup status](setup-status.md).

| ID | Gate | Task | Acceptance evidence | Status |
|---|---|---|---|---|
| F01 | M0 | Audit editor, Android tools, storage and device connection | Tool/version inventory and actual blockers in setup-status.md | DONE |
| F02 | M0 | Choose minimum phone and OS baseline | Device/chipset/OS recorded; test access identified | TODO |
| F03 | M0 | Initialize pinned Unity/URP project and Git ignores | Ignores added and Hub installed; Editor/project still required | IN PROGRESS |
| F04 | M0 | Build and install empty Android scene | APK and launch on Xiaomi; exact build instructions | TODO |
| G01 | M1 | Audit prototype rules and resolve edge cases | Source rules table in rules-audit.md; edge-case decisions pending | IN PROGRESS |
| G02 | M1 | Compare touch and camera schemes | Phone recordings and selected scheme rationale | TODO |
| G03 | M1 | Implement match state machine and scoring | C# package passes 54 assertions; scene integration and full-match evidence still pending | IN PROGRESS |
| G04 | M1 | Implement movement, ball and seven stones | Full attack/rebuild/defend loop in graybox | TODO |
| G05 | M1 | Add team coordination and baseline AI | Complete 4 vs 4 match without manual intervention | TODO |
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

Next: complete Editor/URP setup for F03, connect a test phone for F04, and resolve G01 decisions. Do not begin mass character production before V04 establishes affordable quality.
