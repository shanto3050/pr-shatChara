# Visual slice status — 29 October 2026

The earlier disabled authoring checkpoint has been advanced into a compiling Unity scene. See [the captured-locomotion checkpoint](reports/2026-10-29-captured-locomotion.md), [the polish/performance report](reports/2026-10-29-village-polish.md) and [the earlier integration report](reports/2026-10-29-village-visual-proof.md) for verified build/device evidence and remaining limitations.

## Implemented

- Bablu v2 exported as a skinned FBX with lungi, vest, gamcha, hair cards and explicit URP material metadata. Source scripts: `art-source/create_mockup_bablu.py` and `art-source/export_bablu_unity.py`.
- Completed `VillageScenery.cs`: textured earth, simple houses with pitched tin roofs, fences, trees, drums and a flattened stone mesh. `VillageBuild` and `VillageModels` now compile normally; the temporary WIP guard is removed.
- Fixed legacy texture import shape (2D rather than cubemap) and Blender material import loop. URP materials are assigned explicitly.
- Perspective follow camera defaults on the visual scene; tactical option remains. Temporary skeletal posing includes ground-height correction.
- Local Git LFS rules cover art binaries without rewriting history. Removed duplicate FBX companion textures only after hash-checking all images against preserved canonical copies.
- Plan/backlog now evaluate the free Bablu proof before deciding whether paid character tools or an artist are needed. No purchase is authorized or made.

## Latest continuation (0.2.3)

Added neutral sky, verandas, gables, banana plants, a tube well, clay vessel shapes and cheaper distant trees. Added a score backdrop and provisional manual quality presets with actual-device frame samples. Bablu gameplay geometry is reduced from 65,324 to 31,410 triangles; the full source remains available. See the latest report for measurements, tradeoffs and the installed build fingerprint.

## Captured locomotion continuation (0.2.4)

Recorded CMU walk/jog now drives basic movement, with flat-ground foot locking and authored action overlays. Torso clothing weights and retargeted neck offsets were corrected. Editor contact/turn/pause and full match checks pass; the APK passes phone touch aiming/toppling, movement, rebuilding and pause/resume. A short gameplay-capture window measured 29.7 FPS at 1480×720 with one frame above 100 ms. The report includes phone footage, a clearly labelled offline editor preview and source/licensing evidence. Sustained performance and final visual approval remain open.

## Still open

This is an early proof, not the approved M2 visual target. All eight players share one model; motion remains procedural, with no completed mocap/animation pipeline. The courtyard is a scripted approximation, not a reconstruction of supplied reference photos. Lighting, skin, hair, silhouettes, terrain edges, vegetation, HUD and camera need further work. No sustained 30 FPS, 4 GB compatibility or final benchmark match is established.

The earlier graybox reports remain historical evidence for that build. Use the new report for the graphical build; a Blender still or editor render is never a device capture.

## Reproduce

Open `unity/SatChara` in Unity 6000.3.27f1 with matching Android modules. Run `SatChara.Editor.VillageBuild.Capture` for URP camera images, `Validate` for the visual scene's match simulation, or `Build` for the development APK. Builds go under `unity/SatChara/Builds/Android/` and are ignored.

To regenerate Bablu, fetch the documented free dependencies and HDRI, run the mockup generator with `--no-render`, then load its vendor Blend file in Blender and run `export_bablu_unity.py`. Run `create_bablu_lod.py` after `export_bablu_unity.py` to regenerate the current mobile gameplay mesh; run `create_tree_lod.py` after the base environment conversion to regenerate the distant tree. The exported FBX, textures, metadata and prefab are included, so regeneration is not required for building the game.

## Provenance

MakeHuman meshes, skin, eyes, brows, lashes, hair and old casual outfit use CC0 system assets; MPFB generator code is GPLv3 and is not shipped in the Android runtime. Poly Haven environment assets are CC0. See `asset-register.csv`, `art-source/licenses/`, and recorded download manifests.

Ground albedo uses built-in image generation. Original prompt: "Perfectly overhead close photograph of dry compacted warm brown alluvial earth in a rural Bangladeshi village courtyard, subtle worn footpaths, fine sand grains and occasional tiny pale stones embedded flush with the earth, very sparse flattened straw fragments. Flat diffuse overcast illumination, no directional shadows, no perspective, no horizon, no objects, no lettering, no plants, no large rocks. Natural irregular fine detail and modest color variation. Seamless repeating edges, no obvious central feature or borders."
