# Village prop integration — 30–31 October 2026

This is the second serial implementation checkpoint after captured actions. The 13 source prop types now have Unity URP materials and combined runtime prefabs. It is an integration checkpoint, not final M2 visual approval.

## Scene and materials

The courtyard now uses the supplied mud houses, split-bamboo fence, haystack, tube well, clay pots, jute sack, clothes line, drying straw, banana plants, coconut palms, pond and van-rickshaw. Decoration remains outside the gameplay area and adds no colliders. Houses face the field, and pond vegetation is positioned on the bank rather than in the water.

A flat, two-layer URP terrain blends swept dirt into irregular grass verges and a path to the house. An assertion keeps the playable rectangle clear. The grass maps were fetched from the exact existing Poly Haven provenance entries; all 27 included source maps that match `village-textures.json` pass their recorded SHA-256 hashes. No new paid asset was used. Tinting is an art approximation, not a match to a surveyed village or to Blender's full node graphs.

`village-unity-materials.json` describes the Unity material conversion. OpenGL normal maps are imported as normal maps; roughness is converted to linear metallic/smoothness masks (metallic in red, inverse roughness in alpha). Straw/grass cards use alpha clipping; leaves and hanging cloth are double-sided. Terrain layers explicitly use constant low smoothness, so opaque diffuse alpha does not make the field reflective. These settings were inspected in actual Unity renders.

## Mobile preparation

| Heavy prop | Source triangles | Distant triangles |
|---|---:|---:|
| Mud house | 11,160 | 5,736 |
| Coconut palm | 7,530 | 4,297 |
| Haystack | 4,992 | 1,021 |

`create_village_lods.py` runs in Blender against the included source FBXs, preserves small meshes and removes distant straw cards. Source and output hashes plus Blender version are in `village-lod-summary.json`. Original prop FBXs are unchanged.

Meshes sharing a material are combined per prop and LOD. Source root transforms are baked into the combined vertices, preserving the up axis and ground placement of single-mesh FBXs. A fence goes from 76 source parts to one renderer; a van-rickshaw from 80 to four. A house uses six renderers at each LOD; a palm uses four. This is structural renderer reduction, not a measured GPU draw-call count. Static batching is enabled and material instances are shared.

The scene uses the already reduced broadleaf tree asset rather than duplicating the full source tree. The latest validation counts **358,375 mesh triangles / 290 mesh renderers across all scenery LOD levels**, including 100 grass clumps. That count includes inactive LOD geometry, excludes players and Unity's terrain tessellation, and is not the number submitted per frame.

Low forces the three heavy prop types to their distant LOD and hides grass clumps. Realistic/High use distance LOD selection with different LOD bias; terrain pixel-error and basemap distances also follow the preset. Gameplay geometry and action timing remain shared. Switching Low/Realistic is asserted to hide/restore the grass detail.

## Verification

The final Unity run passed all 16 source-vs-combined prop/LOD bounds checks, material validation, clear-field terrain assertions, zero-decoration-collider checks, Low/Realistic grass switching, eight action checks and corrected walk/jog contact checks. The full match completed **8 rounds, 8 topples, 33 placements, 28 hits, score 5–3, MatchOver**. [Unity validation](assets/village-props-unity-validation.txt).

Samsung SC-03K (Android 10) passed touch throw/topple/movement, captured pickup/place, pause/resume at the same 40.20-second timer, and progression through two rounds. Managed exceptions were absent from the captured Unity log. [Phone events](assets/village-props-phone-validation.txt).

| Gameplay window | Render resolution | FPS | p95 ms | p99 ms | Frames >100 ms |
|---|---|---:|---:|---:|---:|
| Low | 1110×540 | 29.9 | 33.44 | 33.72 | 0 |
| Realistic, recording window 1 | 1480×720 | 29.9 | 33.45 | 33.95 | 0 |
| Realistic, recording window 2 | 1480×720 | 29.7 | 33.45 | 34.04 | 1 |
| High | 1850×900 | 29.9 | 33.44 | 33.52 | 0 |

Each window is about 20 seconds; High/Low include active rebuilding and the round transition. These are delivered-frame smoke tests at the 30 FPS cap, not GPU timings or sustained performance certification. Screenshots confirm Low removes shadows/grass detail and High restores them. The setting was returned to Realistic.

One `dumpsys meminfo` snapshot after returning to Realistic reported **389,009 kB total PSS (about 380 MiB)**. It is a point-in-time sample, not peak usage or a leak test. [Raw memory snapshot](assets/village-props-memory.txt).

Build **0.2.6, version code 9**, ARM64 GLES3, minimum API 26 / target API 36. Local APK: `unity/SatChara/Builds/Android/SatChara-Village.apk`, **79,655,842 bytes**. SHA-256: `6ED4457A82113D6C1B1C93E64C85B0F81892E1BC83EC8CA188B76E130CB3733F`. Development APK size is separate from Play download size.

## Visual evidence

[45-second Android gameplay recording](assets/village-props-phone-demo.mp4), normalized to 30 FPS H.264 for playback, fully decoded and sampled visually. The encoded rate is separate from measured runtime performance. The phone screenshots and offline Unity camera renders were inspected; they show the current prototype rather than an approved target look.

![Android Realistic](assets/village-props-phone.png)

| Offline Unity courtyard | Offline Unity tube well |
|---|---|
| ![Courtyard](assets/village-props-courtyard-unity.png) | ![Tube well](assets/village-props-tube-well-unity.png) |

| Offline Unity clothes line | Offline Unity pond |
|---|---|
| ![Clothes](assets/village-props-clothes-unity.png) | ![Pond](assets/village-props-pond-unity.png) |

[Low phone screenshot](assets/village-props-low-phone.png) · [High phone screenshot](assets/village-props-high-phone.png)

## Remaining work

The broadleaf tree is a reused sparse-canopy asset; it is not a finished local mango/jackfruit/bamboo canopy. The scene still needs richer reference-matched vegetation, ground litter, bank/ghat detail, local house proportions and baked lighting. Props have no gameplay interactions yet. Pond flowers remain simplified; clothing and deep crouches are unchanged by this environment pass. The target frame and user sign-off remain open, as do 3 GB device testing and the sustained thermal gate.
