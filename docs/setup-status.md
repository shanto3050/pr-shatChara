# Development setup status

28 October 2026 · Initial foundation work

## Verified

- Unity Editor/Hub absent from standard installation directories and desktop uninstall entries at audit start.
- Installed Unity Hub 3.22.4.65535 through winget's Unity.UnityHub package. Windows registered the MSIX package successfully. Installed package is UnityTechnologies.UnityHub.
- Packaged Hub executable did not return editor-release information through the legacy headless invocation. Its bundled standalone unity.exe returned access denied when invoked directly. No Editor installation is verified. Do not assume Hub installation completes editor setup.
- Android Studio installed. Existing SDK has platforms android-34, android-35, android-36 and build-tools 34.0.0, 35.0.0, 36.0.0. Compatibility with a selected Unity editor is not yet established; use editor-matched Android modules.
- ADB at C:\adb\adb.exe starts successfully outside the restricted shell. Device list is empty: no connected authorized phone.
- Approximately 93 GiB free on C: and 750 GiB on E: at audit time. Prefer E: for editor/project caches where practical.
- Node.js v24.11.1 available. Added repository-local CommonJS configuration because the parent workspace's ES-module setting prevented the existing balance simulator from starting.
- Simulator smoke check: `node tools/balance-sim.js 3` completed all six field/difficulty combinations (18 simulated matches). This small, unseeded sample proves execution only; it is not a balance study or human playtest.
- Added Unity build/cache/signing exclusions. No Android binary, Unity scene, or generated Unity project exists yet.

## Next actions

1. Open Unity Hub from the Windows Start menu. Complete first-run account/license setup if required; the account owner handles credentials and eligibility declarations.
2. Select a currently supported Unity 6 LTS editor from official releases, with Android Build Support, SDK/NDK tools, and OpenJDK. Prefer E: for the editor installation. Exact patch is not pinned until editor availability is verified.
3. Create a URP project at unity/SatChara, then commit its actual ProjectVersion, package lock and source settings. Avoid handwritten template files that pretend the editor has initialized the project.
4. Connect Xiaomi with a data-capable USB cable, enable developer options and USB debugging, authorize the computer, then verify `adb devices -l` reports an authorized device.
5. Build an empty-scene development APK, install and launch on the phone, and record evidence before marking F03/F04 done.

## Official setup references

- [Editor installation and Android modules](https://docs.unity.com/en-us/hub/add-editor)
- [Unity 6 support policy](https://unity.com/releases/unity-6/support)
- [Unity CLI / legacy Hub CLI overview](https://docs.unity.com/en-us/hub/cli-overview)

## Rules work available while setup completes

See rules-audit.md for observed scoring, turns, timing and unresolved 3D collision semantics. This is source-derived evidence; gameplay and on-phone controls remain untested.
