# Visual slice checkpoint — 29 October 2026

This checkpoint preserves the graphical work so it can be continued on another machine. It is **not a completed village build**. The last phone-verified APK remains the graybox described in the earlier reports.

## Saved work

- Textured, clothed, skinned human exported to Assets/SatChara/Art/Characters/VillagePlayer.fbx; editable Blender source and generation scripts under art-source/. Character preview was rendered and inspected in Blender.
- Mobile-reduced tree and barrel FBX assets under Art/Environment, plus photographed plaster, wood and corrugated-tin textures.
- Native image-generation ground texture at Art/Textures/village-earth.png.
- First-pass skeletal pose controller VillageAvatar.cs and optional visual-asset hooks in GrayboxMatch.cs.
- Partial editor import/material/prefab/pipeline code in VillageBuild.cs and VillageModels.cs.

## Important unfinished work

The courtyard geometry authoring patch was **not applied**: automatic approval review failed because its usage limit was reached. The error explicitly said this was a review failure, not a determination that the action was unsafe. Consequently BuildCourtyard() and StoneMesh() are missing. The partial editor tools are guarded by SAT_CHARA_VISUAL_SLICE_WIP so these unresolved authoring calls do not enter normal editor compilation. Do not enable that define until the missing code exists.

No Unity compilation, Unity visual inspection, Android build or phone test has verified this visual slice. Blender's character preview does not prove Unity appearance or animation quality. The skeleton controller is an unverified first pass, not motion capture or finished natural animation. Full roster identity, final skin/material tuning and character differentiation remain open.

## Continue elsewhere

1. Clone the full repository; open unity/SatChara in Unity 6000.3.27f1 with its matching Android modules and an eligible active license.
2. Keep the existing graybox scene available while finishing the visual slice.
3. Implement and inspect the village geometry/stone mesh, then enable the editor authoring code deliberately.
4. Verify FBX scale, material remapping, skeleton pose and camera in an actual Unity render before building Android.
5. Build/install and inspect on the actual connected device, recording frame-time and memory evidence before claiming lower-end compatibility.

The vendor downloads are intentionally ignored. To regenerate assets, download the official MPFB v2.0.18 source into art-source/vendor/mpfb/, run fetch_character_assets.py, then run create_character.py using Blender. The script uses workspace-local transient add-on data. Poly Haven model preparation also needs the original vendor FBX downloads referenced in environment-downloads.json. Existing exported FBX/textures and Blender source are included in this checkpoint, so regeneration is not required just to inspect them.

## Asset provenance

MakeHuman/MPFB meshes, skin, hair, eyes and male_casualsuit03 clothing are CC0 assets; the generator itself is GPLv3 and is not shipped as part of the Android runtime. See art-source/licenses/ and the [official system-asset listing](https://static.makehumancommunity.org/assets/assetpacks/makehuman_system_assets.html).

The island_tree_01, barrel_03, clay_plaster, worn_corrugated_iron and wooden_rough_planks source assets are from Poly Haven under [CC0](https://polyhaven.com/license). Download references and hashes are saved in art-source/. Some source-resolution character images are duplicated in the FBX companion folder and canonical Textures folder to preserve the current FBX dependencies; optimization can follow after a verified import.

The ground texture was generated with the built-in image_gen tool and copied into the Unity project. Prompt: "Perfectly overhead close photograph of dry compacted warm brown alluvial earth in a rural Bangladeshi village courtyard, subtle worn footpaths, fine sand grains and occasional tiny pale stones embedded flush with the earth, very sparse flattened straw fragments. Flat diffuse overcast illumination, no directional shadows, no perspective, no horizon, no objects, no lettering, no plants, no large rocks. Natural irregular fine detail and modest color variation. Seamless repeating edges, no obvious central feature or borders." It has not yet been inspected tiled inside Unity.
