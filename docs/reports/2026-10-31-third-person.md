# First immersive camera and MetaHuman Unity trial

31 October 2026. This is an initial review milestone, not the completed graphics or movement target. Unity remains the game runtime; the provisional minimum remains 4 GB RAM and needs representative-device verification.

## Playable camera pass

The village camera now follows behind the player, with empty-right-side touch orbit, camera-relative movement/aim, gradual acceleration/deceleration and closer shoulder framing while aiming. The tactical view is retained. Explore mode starts a fresh round, suspends the match and hides other players/markers so the camera and walking can be judged separately. Returning starts a fresh match.

Android development build 0.3.0, code 11, was built successfully and installed on the connected Samsung test phone. APK: `unity/SatChara/Builds/Android/SatChara-ThirdPerson.apk`, 97,430,057 bytes. Explore, orbit swipes and camera-relative forward movement were exercised on-device; movement telemetry included position `(2.30, 0.90, -6.96)` after an orbit and forward-stick gesture. The phone still uses the fallback character.

An actual device recording is retained locally at `.verification/third-person/phone-camera-movement-review.mp4` (H.264, 2960 x 1440, 17.976 seconds). Metadata and sampled frames were inspected. Short **idle** Realistic samples at 1480 x 720 reported 29.9 FPS, p95 around 33.44 ms and no frames over 100 ms in those windows. This does not verify sustained thermals, moving-match performance, MetaHuman performance or the 4 GB floor.

## Checks and grounding

- Unity camera checks passed for follow distance, yaw-relative direction, static test-wall obstruction and shoulder framing. Village scenery still needs collision geometry; the test wall does not establish village-wide collision coverage.
- The fallback sole probes now use actual skin weights and bind-pose points, including mixed-weight heel vertices and more support directions. Twelve sampled locomotion poses passed the baked-body floor tolerance check. Their minima ranged from -0.01961 m to +0.01921 m against ground at -0.025 m. Contacts throughout every action still need close-camera review.
- The full automated match and pause check passed: 8 rounds, 8 topples, 44 placements and 22 hits.

## Actual MetaHuman export and Unity import

Epic sign-in completed for the rig service. A separate copy of BabluConcept received a joints-only rig and 2K skin sources. Head/body/full-body FBXs were exported and inspected in Blender, including their skeletons and supplied LODs. Skin PNGs, source short-messy hair cards, natural eyebrow cards and eye textures were exported from the installed Epic data.

The isolated Unity trial uses head LOD2, body LOD2, source hair/brow cards, 35,149 triangles and 55 weighted bones. Facial weights are collapsed onto the body skeleton for this trial; it does not preserve the full MetaHuman facial rig. Materials are rebuilt for URP, including a simple mobile eye shader. Hair coverage is packed from the cards atlas coverage channel. The assembly is fitted to 1.7 m body height in the review scene.

The saved scene is `unity/SatChara/Assets/SatChara/Scenes/MetaHumanReview.unity`; the trial prefab is under `Art/Characters/MetaHumanBablu`. [This portrait](../mockups/metahuman/bablu-unity-mobile-trial.png) is an actual Unity render, not the earlier Unreal portrait. It shows a technical import, not approved final likeness, skin, eyes, brows, hair or outfit. These assets are MetaHuman/Epic-derived, not the CC0 fallback character.

Headless export initially crashed in RigLogic, and a rendering-enabled attempt exhausted Windows memory. Saving/closing the separate authoring editor allowed export to proceed. The first export script's JSON summary failed on an Unreal Array after FBXs were written; serialization was corrected, and artifacts were independently checked. The local canonical artifact inventory is `art-source/metahuman/exports/export-verification.json`.

## Remaining serial work

1. Fit the vest, lungi and gamcha to the new body; complete hair/brow/eye materials and inspect neutral views.
2. Retarget and inspect walk/run transitions, starts/stops, turns, pickup, aim, throw and squat on the MetaHuman. Review feet, hands and cloth penetration.
3. Put the finished trial into the courtyard review, add scenery collisions and explicit actions, then record a complete feel test.
4. Finish the village lighting/materials, vegetation, audio and HUD for the close camera.
5. Benchmark one and eight MetaHumans, including sustained play on a representative 4 GB device. Only then replace the main character.

Runtime changes and the isolated trial remain local during this integration. Published documents and renders are progress evidence, not a claim that the MetaHuman is already in the installed phone build.
