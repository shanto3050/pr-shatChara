# Bablu: MetaHuman production track

31 October 2026. User selected MetaHuman after reviewing the procedural model as too puppet-like. The approved [fictional photographic concept](mockups/bablu-v4-realistic-concept.png) is the visual target. The existing MakeHuman model is a fallback and garment reference, not the approved final character.

## Current state

- Epic Games Launcher is installed and signed in.
- Unreal Engine 5.8.4 with MetaHuman Creator Core Data: **installed**, verified against the launcher manifest and installed preset/example files.
- Separate authoring project under `art-source/metahuman/BabluCreator`: **engine initialization completed** in the project log. First launch took about 454 seconds. Visual inspection is pending because Windows denied desktop input and capture was blank.
- `art-source/metahuman/create_bablu_candidate.py` is prepared using the installed Epic scripting examples. It duplicates the Bo preset into a separate Bablu asset and applies a 170 cm height target. It has passed Python syntax validation but **has not run inside Unreal**; there is no saved candidate asset yet.
- MetaHuman Bablu asset, textures, rig, portrait renders, clothing fit, Unity import, and Android tests: **pending**.
- Unity gameplay code and currently installed APK have not been replaced by this authoring setup.

## Design brief

Bablu is a fictional Bangladeshi village teenager, about 15. Match the approved concept's natural facial proportions and ordinary adolescent physique: medium brown skin, dark brown eyes, short black hair, subtle asymmetry, restrained skin shine, and a relaxed closed-mouth expression. Avoid doll-like eyes, exaggerated lips, smooth plastic skin, an adult body with a small head, or beauty makeup. MetaHuman's starting presets may need additional sculpting to achieve the teenage appearance.

Keep the blue checked lungi, off-white sleeveless cotton vest, red/off-white gamcha, and bare feet. The lungi must permit running and squatting without leg penetration. The vest must have continuous straps and sewn armholes. The gamcha must drape as thin cotton, not a rigid folded board. Cloth detail must remain convincing in neutral light as well as village light.

No real person's identity is required. The concept and the two public textile references are documented in `docs/mockups/v4-references/README.md`. They provide appearance guidance, not hidden geometry, scan data, or an automatically reconstructed 3D face.

## Serial implementation and review gates

1. **Authoring setup:** finish installing Unreal and core data; open the separate project; verify MetaHuman asset creation, required services, and editor stability on the RTX 4060 Ti 8 GB. Record actual settings and errors.
2. **Face and body:** select suitable presets, sculpt against the concept, set realistic skin/eyes/hair, and review front, profile, three-quarter, and full-body views in neutral light. A MetaHuman preset is not automatically an approved Bablu.
3. **Texture and rig generation:** retrieve skin sources and generate the rig through Epic's supported services. Keep character identity/edit state reproducible; record source asset paths and chosen settings. Confirm the material output can be baked/exported for Unity.
4. **Custom garments:** fit or rebuild the lungi, vest, and gamcha to the selected body. Preserve UVs, seams, sensible thickness, and cloth ease. Review standing, running, deep squat, pickup, placement, and overarm throw before accepting the garments.
5. **Mobile adaptation:** assemble lower-detail geometry, use hair cards, simplify materials and facial joints as appropriate, and bake required texture detail. Begin with 1K/2K textures and measure the whole character. Epic's mobile LOD guidance is a starting point, not a demonstrated budget for eight players on a lower-spec phone.
6. **Unity integration:** import into an isolated review scene; rebuild skin/eye/hair materials for URP; retarget the existing motions to the new skeleton. Verify scale, root ownership, feet, hands, contact timing, pause/resume, and clothing. Preserve gameplay rules and action transactions.
7. **On-device gate:** inspect close-up and match-distance views; test one character, then eight characters. Measure frame times, memory and APK growth; follow with sustained play on the older test phone. Only replace the main character prefab after visual/deformation and performance gates pass.

## First deliverable

A saved, editable MetaHuman Bablu candidate with neutral-light portrait and full-body renders, plus a clear comparison with the concept. This is the next art review milestone. A generated character is not considered delivered until the asset opens and the renders are inspected.

## Sources checked

- [Epic setup and core data](https://dev.epicgames.com/documentation/en-us/metahuman/getting-started-with-metahuman-creator)
- [MetaHuman Character plugin](https://dev.epicgames.com/documentation/unreal-engine/API/PluginIndex/MetaHumanCharacter?lang=en-US)
- [Creator Python scripting](https://dev.epicgames.com/documentation/metahuman/metahuman-creator-python-scripting-in-unreal-engine?lang=en-US)
- [Mobile platform and LOD guidance](https://dev.epicgames.com/documentation/en-us/metahuman/platform-support-and-lod-specifications-for-metahumans)
- [MetaHuman licensing](https://www.metahuman.com/license?lang=en-US)

Epic permits use in other engines under its license. Exporting does not automatically reproduce Unreal's materials or facial rig in Unity. Keep engine/game licensing and third-party clothing/reference attribution with the final assets.
