# Android foundation build

This is the M0 installation/simulation smoke build, not a playable match or finished art. The test scene contains a graybox seven-stone tower and a button which runs a successful rebuild through the shared C# rules.

## Requirements

- Unity 6000.3.27f1, pinned in unity/SatChara/ProjectSettings/ProjectVersion.txt.
- Active eligible Unity license (Personal is sufficient). Credentials and license files stay outside Git.
- Matching Android Build Support, OpenJDK, SDK/NDK modules installed through Unity Hub/CLI.
- Full repository checkout, including packages/com.satchara.rules. The Unity project references this package by relative path.

Open unity/SatChara in Unity. Let package resolution and compilation finish. Use **Sat Chara → Prepare Foundation Scene** to regenerate the installation test scene, then **Sat Chara → Build Android Development APK** to build it. The generator deliberately replaces the Foundation scene; do not use it to store future hand-edited gameplay scenes.

## Reproducible command

Close any editor using this project first. In PowerShell from the repository root:

```powershell
$editor = 'E:\Unity\Hub\Editor\6000.3.27f1\Editor\Unity.exe'
$project = (Resolve-Path 'unity/SatChara').Path
$arguments = @('-batchmode', '-nographics', '-DisableDirectoryMonitor', '-quit',
    '-projectPath', ('"' + $project + '"'), '-buildTarget', 'Android',
    '-executeMethod', 'SatChara.Editor.AndroidBuild.BuildDevelopment',
    '-logFile', ('"' + (Join-Path $project 'Logs/android-build.log') + '"'))
$process = Start-Process -FilePath $editor -ArgumentList $arguments -WindowStyle Hidden -PassThru -Wait
if ($process.ExitCode -ne 0) { throw "Unity failed; inspect Logs/android-build.log" }
```

Adjust the editor installation path on another machine. The output defaults to unity/SatChara/Builds/Android/SatChara-Foundation.apk. Optional SAT_CHARA_APK environment variable selects another output path. Builds and logs are excluded from Git. The command disables directory event monitoring for this invocation because initial setup encountered repeated monitor-buffer overflows; it does not change global preferences.

Development defaults: package identifier com.shanto3050.satchara.dev, ARM64/IL2CPP, OpenGL ES 3, landscape, 30 FPS runtime cap, Android API 26 minimum, automatic installed target SDK. These are provisional test settings, not certification that every API-26/ARM64 device is supported. Release identity, minimum hardware/OS, target SDK and signing must be reviewed before beta.

## Device check

```powershell
adb devices -l
adb install -r unity/SatChara/Builds/Android/SatChara-Foundation.apk
adb shell am start -W -n com.shanto3050.satchara.dev/com.unity3d.player.UnityPlayerGameActivity
```

The launch activity above was confirmed from the actual foundation APK using aapt. Reinspect it if application entry-point settings change. Do not guess a successful launch from install success alone.

Check the title and tower render, landscape orientation, the rebuild button changes score from 0–0 to 1–0, Reset works, and background/resume works. Capture the screen and inspect logcat for exceptions. Record phone model/OS and build ID. [The first device report](reports/2026-10-28-foundation.md) records successful installation and these checks on the connected Samsung SC-03K (Android 10).

## Recovery

If an interrupted import leaves a stale Bee compiler worker, first verify that no editor/compiler for this project is still running. Preserve or clear only generated Library/Bee state inside this project, then retry. Do not delete source assets, ProjectSettings, Packages manifests, or another project's processes. A first import takes longer than subsequent builds; check logs before restarting.
