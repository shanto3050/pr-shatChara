# Immersive village milestone

31 October 2026. User confirmed GTA V, Red Dead Redemption and Modern Combat as references for presence, movement, camera and graphics. Unity remains the game engine. Unreal is the MetaHuman authoring tool.

The current overhead sports prototype is not the approved experience. Pause new days, missions and content expansion until a third-person courtyard slice is reviewed.

## Serial work

1. Put the camera behind Bablu at human scale. Add right-side drag orbit, camera-relative analog movement, gradual acceleration/deceleration, and closer aiming framing. Keep the tactical camera available for comparison. Verify touch ownership, pause, player switching and camera obstruction.
2. Use the initial Explore mode to review camera-relative walking without match rules preventing movement. Complete this as a free courtyard scene with explicit actions. Add solid scenery collision, grounded locomotion, coherent starts/stops/turns and explicit pickup/throw interactions. Review foot sliding and contact timing at close camera distance; existing pose clips alone do not establish realistic movement.
3. Export a copy of the saved BabluConcept MetaHuman through Epic's rig, texture and geometry pipeline. Preserve the editable source. Import a mobile derivative into an isolated Unity scene, rebuild URP skin/eye/hair materials and retarget motion. Fit the target vest, lungi and gamcha. The portrait is approved as a direction; the current preset outfit and unfinished teenage likeness are not the final asset.
4. Dress one courtyard for the new eye-level view: village buildings, dirt, vegetation, shadows, material scale, ambient sound and restrained HUD. Review front, side, running, aiming and throwing footage before extending the village.
5. Integrate the approved character and camera into the match, then measure one and eight characters on Android. Inspect controls, silhouette, terrain contact, camera visibility, sustained frame times, memory and heat.

## Hardware and acceptance

Provisional floor: 4 GB RAM, 64-bit Android 9+, Snapdragon 720G/732G-class graphics or comparable; target 30 FPS with adaptive resolution and lower settings. This is a planning target, not a verified compatibility claim. Current APK minimum OS settings may differ until explicitly updated. The existing Samsung test device does not prove the 4 GB floor.

Accept the slice only after the user reviews actual playable footage and confirms camera, movement and visual direction. GTA/RDR guide weight and atmosphere; their full desktop rendering complexity is not the mobile budget. The MetaHuman portrait does not establish Unity appearance or Android performance.

## Initial implementation status

Third-person orbit, camera-relative move/aim, acceleration/deceleration, shoulder framing and an Explore mode are implemented in the first pass. Unity camera checks passed for yaw-relative movement, follow distance, a static obstruction, and shoulder framing. Scenery needs colliders before obstruction can be demonstrated. Captured movement and action clips remain provisional. The fallback character sole probes now use actual skinning weights and bind poses; 12 sampled locomotion poses passed the body-floor tolerance check. This does not establish final animation quality or action contact correctness. MetaHuman runtime integration, complete courtyard actions, new environment finish and on-device verification remain open.

## Verified first pass

Android 0.3.0 (code 11) was built and installed on the connected Samsung test phone. Explore, orbit gestures and camera-relative movement were tested. Short idle samples were about 29.9 FPS at 720p using the fallback character. The separate Unity MetaHuman trial imports actual exported geometry and textures; it is not yet the phone character. See [the integration report](reports/2026-10-31-third-person.md).

## Clothed MetaHuman walking checkpoint

The initial 0.3.1 walking courtyard was checked on the Samsung phone with the actual MetaHuman, fitted garments, retargeted locomotion and four-weight skinning. Short 720p samples were 29.9 FPS; one PSS snapshot was about 391 MiB. The first-pass phone build described above is historical. Full actions, art approval, environment finish and the 4 GB/eight-character/sustained gates remain open. See [the current checkpoint](reports/2026-10-31-metahuman-courtyard.md).

The installed trial is now **0.3.2, code 13**, which preserves the character's heading when stopping. Device checks confirmed a 90-degree heading after a rightward run and subsequent stop. Current short samples remain 29.9 FPS; the latest PSS snapshot was about 396 MiB.
