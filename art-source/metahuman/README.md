# Bablu MetaHuman authoring

This is a separate Unreal authoring workspace. The Android game stays in `unity/SatChara`.

Status on 31 October 2026: Unreal Engine **5.8.4** installation started through Epic Games Launcher at `E:/UE_5.8`, with **MetaHuman Creator Core Data** selected. Installer showed **17.84 GB download / 37.86 GB storage**. These are installer estimates, not the final size of the character project. Epic licensing acceptance and installation were explicitly approved by the user.

Installation subsequently completed and is verified by the launcher manifest and installed preset/example files. The `BabluCreator.uproject` descriptor enables the documented MetaHuman Character, Python, and Editor Scripting plugins. Unreal completed project initialization (about 454 seconds on first launch). Desktop input/capture was denied before visual inspection. There is no MetaHuman character asset yet.

`create_bablu_candidate.py` was executed successfully through Unreal's Python script tools. The saved candidate is `Content/Characters/MetaHumans/Bablu.uasset`: a separate starting candidate from the Bo preset, with a 170 cm height target. It saves a report under `Saved` and opens the asset editor. The first preview has been inspected; it is too heavy and mature for the approved concept, so face/body refinement remains open. Re-running preserves an existing candidate instead of replacing it.

The candidate depends on Epic's installed MetaHuman Creator Core Data. Its `.uasset` is an Unreal source asset, not a portable Unity mesh or assembled gameplay character. Epic's MetaHuman/Unreal license applies to it; it is not a MakeHuman CC0 asset. No cloud texture or autorig request has been made for this candidate yet.

A second candidate, `BabluConcept.uasset`, is now saved from the Mateo preset. `create_concept_candidate.py` and `adjust_studio.py` create its preview assembly and studio capture using Unreal's native APIs. See the [inspected portrait and remaining art gates](../../docs/mockups/metahuman/README.md). The preview actor is transient, and the disposable studio map is not tracked as final scene content.

## Launch after installation

```powershell
& 'E:/UE_5.8/Engine/Binaries/Win64/UnrealEditor.exe' "$PWD/art-source/metahuman/BabluCreator/BabluCreator.uproject"
```

First launch will compile shaders and may need Epic sign-in for cloud texture synthesis and autorigging. Authentication is completed by the user. Do not put credentials in scripts or the repository.

Read [the character brief and acceptance gates](../../docs/metahuman-bablu.md). Use Epic's installed examples under `Engine/Plugins/MetaHuman/MetaHumanCharacter/Content/Python/examples` as the version-specific source for scripting asset creation and edits. Do not guess API names from older tutorials.

Unreal caches and saved editor state are ignored. Check licensing and track selected final character sources with Git LFS when they actually exist; do not commit the engine installation or bulk downloaded content.
