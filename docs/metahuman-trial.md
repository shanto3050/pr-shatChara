# MetaHuman trial: Bablu (backlog V01b, decision D16)

Goal: make Bablu as a MetaHuman, bring him into the Unity village scene, and compare him on the phone with the free Bablu (`docs/mockups/`, v3). The result decides where the final characters come from.

**Run this on the Unity PC.** The laptop used for the free mockups has integrated graphics and 16 GB RAM, which is below Unreal Engine's recommendation. Nothing here costs money unless a step says so; ask before any purchase.

## 0. Before you start

| Check | Needed | How to check |
|---|---|---|
| Graphics card | DirectX 12, **8 GB+ video memory** (e.g. NVIDIA RTX 2000+, AMD RX 6000+, Intel Arc) | Task Manager → Performance → GPU |
| RAM | 32 GB recommended | Task Manager → Performance → Memory |
| Disk | About 100 GB free for Unreal Engine, MetaHuman and the project. E: is fine | File Explorer |
| Windows | Windows 10 22H2 or Windows 11 | Settings → System → About |
| Account | An Epic Games account. You sign in yourself; never put the password in chat or in the repo | epicgames.com |

Source for the hardware figures: [Unreal Engine hardware and software specifications](https://dev.epicgames.com/documentation/en-us/unreal-engine/hardware-and-software-specifications-for-unreal-engine).

### Confirm the license first

Open [metahuman.com/license](https://www.metahuman.com/en-US/license) while signed in to Epic (the page needs a sign-in) and confirm:

- [ ] MetaHuman characters may be **shipped in a Unity game** (reports from June 2025 say yes: free under US$1M/year revenue, an Unreal seat license above that, no royalties)
- [ ] There's no requirement to render them only in Unreal, and no attribution requirement (or note what's required)
- [ ] Any other conditions (for example the ban on using them to train AI models)

Record the result as a new decision in `docs/decisions.md`. **If shipping in Unity isn't allowed, stop here.**

## 1. Install

1. Install the **Epic Games Launcher** from epicgames.com and sign in.
2. Launcher → Unreal Engine → Library → install **Unreal Engine 5.6 or newer** (MetaHuman Creator is built into the editor from 5.6). Install on E: if C: is short of space.
3. Create a blank project (no starter content), for example `E:\Unreal\SatCharaMetaHuman`.
4. In Edit → Plugins, enable the **MetaHuman** plugins (Creator and the character plugins) and restart.

Menu names change between versions. If a step doesn't match, follow Epic's current MetaHuman documentation for your engine version and write down what you did.

## 2. Make Bablu

Use `docs/characters.md` (Bablu: 15, fisherman's son, broad and heavy, skin #9C6440, short black hair) and the v3 free mockup as the reference.

1. Create a new MetaHuman. Start from a South Asian preset close to Bablu if one exists.
2. **Face:** blend toward the v3 traits: broader nose with fuller nostrils, fuller cheeks, a heavier lower brow, a rounder and wider jaw, slightly deep-set dark brown eyes. Keep him looking 15: soft jaw, no beard or stubble.
3. **Skin:** medium-dark warm brown, matching #9C6440 in daylight. Little or no makeup. A little periorbital darkening is natural.
4. **Hair:** short black hair; no facial hair.
5. **Body: the known limitation.** MetaHuman Creator only has adult body types. Pick the **smallest and shortest male body** with a heavier build. If he reads as an adult, note it in the report. Child/teen body packs exist on Fab (paid): **don't buy one without approval.**
6. **Clothes:** MetaHuman has no lungi or gamcha. For the trial, use the plainest outfit (or none) and fit our own clothing in step 4.

Save the MetaHuman and take screenshots in Unreal: front, three-quarter and a face close-up, with neutral, evenly lit framing similar to `docs/mockups/`.

## 3. Export for Unity

Export Bablu's skeletal mesh as **FBX**, with the skeleton, skin weights, textures and the **mobile-size LODs** (the lower LODs, roughly 5–30k triangles). Use the export option Epic documents for your version (in-editor export or the DCC/Maya route). Include:

- Body and head meshes with skin weights and the skeleton
- Albedo, normal and roughness textures for face and body, at 1–2K (larger textures can be resized in Unity)
- Hair as **cards** (not strands), the lowest LODs that still look like hair
- Eyes and teeth

Put the exported files in `unity/SatChara/Assets/SatChara/Art/Characters/MetaHuman/` (Git LFS stores FBX and PNG). **Don't commit any Epic login data.** Also record the exact MetaHuman, export settings and LOD in `docs/asset-register.csv` (license: MetaHuman, per the confirmed terms).

## 4. Bring it into the village scene

1. Import the FBX into Unity 6000.3.27f1 and set **Rig → Humanoid** so the existing CMU walk/jog (D21) retargets onto him.
2. Make URP materials for skin, eyes and hair cards (alpha-clip for the hair).
3. **Clothing:** refit our generated lungi, vest and gamcha in Blender. Change `art-source/create_mockup_bablu.py` to read the MetaHuman body instead of the MakeHuman body (the clothing is built from whatever body it measures), or drape it with Blender's cloth simulation, then export the clothing skinned to the MetaHuman skeleton.
4. Add a **second prefab** (`Bablu_MetaHuman`) next to the free one, and a debug toggle in the village scene to switch all players between the two.

## 5. Compare on the phone (Samsung SC-03K, the realistic minimum)

Build an APK with both versions and record the same things for each:

| Measure | Free Bablu (v3) | MetaHuman Bablu |
|---|---|---|
| Looks at play distance (screenshot, same camera) | | |
| Looks in a close-up (celebration/replay camera) | | |
| Reads as a 15-year-old Bangladeshi village boy? | | |
| Frame time, 8 players on screen, Realistic preset (p50 / p95 ms) | | |
| Memory (total PSS) | | |
| Triangles and texture memory per character | | |
| APK / asset size increase | | |
| Walk/jog retarget quality (feet, hands) | | |
| Work to make all 8 kids this way | | |

Save the report as `docs/reports/<date>-metahuman-trial.md` with screenshots and a short phone clip (LFS), and update D16 and V01b.

## How to decide

- **MetaHuman wins** if it clearly looks better in close-ups, still holds about 30 FPS on the SC-03K with 8 players (lower LODs at play distance), the license allows shipping in Unity, and the kids can be made to look their age (possibly with an approved teen body pack).
- **Free Bablu stays** if MetaHuman only wins up close but costs too much performance, can't look 15, or needs paid packs for every child.
- **Mixed approach:** free characters in play, MetaHuman-quality heads only for close-up and celebration cameras.
