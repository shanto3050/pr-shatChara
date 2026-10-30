# Bablu MetaHuman authoring

This is a separate Unreal authoring workspace. The Android game stays in `unity/SatChara`.

Status on 31 October 2026: Unreal Engine **5.8.4** installation started through Epic Games Launcher at `E:/UE_5.8`, with **MetaHuman Creator Core Data** selected. Installer showed **17.84 GB download / 37.86 GB storage**. These are installer estimates, not the final size of the character project. Epic licensing acceptance and installation were explicitly approved by the user.

The `BabluCreator.uproject` descriptor enables the documented MetaHuman Character, Python, and Editor Scripting plugins. It is prepared but **has not yet been opened or validated in Unreal**. There is no MetaHuman character asset yet. Engine/plugin compatibility and core-data detection must be checked after installation finishes.

## Launch after installation

```powershell
& 'E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' "$PWD/art-source/metahuman/BabluCreator/BabluCreator.uproject"
```

First launch will compile shaders and may need Epic sign-in for cloud texture synthesis and autorigging. Authentication is completed by the user. Do not put credentials in scripts or the repository.

Read [the character brief and acceptance gates](../../docs/metahuman-bablu.md). Use Epic's installed examples under `Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples` as the version-specific source for scripting asset creation and edits. Do not guess API names from older tutorials.

Unreal caches and saved editor state are ignored. Check licensing and track selected final character sources with Git LFS when they actually exist; do not commit the engine installation or bulk downloaded content.
