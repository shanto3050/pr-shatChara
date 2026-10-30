# Captured game actions (free motion capture)

Recorded human motion for the actions the game needs beyond walk/jog, converted from the free [CMU Graphics Lab Motion Capture Database](http://mocap.cs.cmu.edu/). Its FAQ grants: "The motion capture data may be copied, modified, or redistributed without permission." See `art-source/licenses/CMU-Mocap.md`.

| Clip | Source take (CMU description) | Frames @30 fps | Event | Use in the game |
|---|---|---|---|---|
| `Throw` | 124_01 "Baseball Pitch" | 49 | `release` 0.95 s | Full overarm throw at the tower |
| `ThrowCasual` | 111_33 "Throwing" | 40 | `release` 0.75 s | Quick throw at a rival, passes |
| `PickUp` | 111_17 "Pick up" | 55 | `grab` 0.95 s | Grab the ball or a stone from the ground, bending down with the feet still |
| `PickUpSquat` | 111_18 "Pick up" | 57 | `grab` 0.95 s | Squat right down to pick a stone off the ground |
| `Place` | 69_75 "walk up to object, squat, pick up object, set down in another place" | 52 | `place` 0.9 s | Deep squat to place a stone on the tower |
| `Duck` | 139_09 "Ducking" | 40 | `lowest` 0.55 s | Duck under a throw |
| `DodgeRight` | 127_14 "Run Side Step Right" | 21 | `step` 0.12 s | Side-step dodge (running cut) |
| `DodgeLeft` | mirror of `DodgeRight` | 21 | `step` 0.12 s | 127_13 "Run Side Step Left" barely moves sideways, so the right one is mirrored |

Preview videos and a still at each event are in this folder (`<Clip>.mp4`, `<Clip>-<event>.jpg`), retargeted onto the Bablu mockup in Blender.

**How the pick-up takes were chosen:** each CMU pick-up take was scored over its clip window. The first choice, 64_26, kicked its back leg out in the preview; the other "Picking up Ball" takes (64_27–30) also step or lift a foot (0.19–0.50 leg lengths). 111_17 keeps both feet planted (foot lift 0.04, travel 0.02) and 111_18 squats with the hand reaching the ground (0.07) and feet nearly still. Scoring script: `art-source/score_pickup_takes.py` (needs the 64_* and 115_* takes from the CMU site, which aren't kept in the repo).

## Files

- **Data:** `unity/SatChara/Assets/SatChara/Animation/CapturedActions.json`, the same direction-space format as `CapturedLocomotion.json` (one direction per mapped bone), plus per frame: `pelvis` (height change, in leg lengths), `root` (travel, in leg lengths), foot contacts, and per clip the `events`.
- **Loader:** `unity/SatChara/Assets/SatChara/Scripts/CapturedActions.cs` with `Load`, `Find(name)`, `EventTime(clip, name)` and `Sample(clip, time, ...)`. Type-checked and run outside Unity against the real JSON with `dotnet` and small stand-ins for the Unity types. **Not yet compiled inside Unity.**
- **Converter:** `art-source/convert_cmu_actions.py` (run with Blender's Python). It finds the key moment automatically (fastest hand for throws, lowest hand or head for pick-up/place/duck, fastest sideways step for dodges), cuts a window around it, and orients the clip: throws face along the stride, everything else faces the hips' forward direction.
- **Preview:** `art-source/preview_actions.py` retargets the clips onto the Bablu mockup and renders the videos. It adds a simple ground lock for planted feet; it does not do full foot IK.

All source takes and their SHA-256 digests are listed in `art-source/motion/cmu/manifest.json`.

## Hooking into the game (for the Unity PC)

1. Add a `TextAsset capturedActions` field next to `capturedMotion` in `VillageAvatar` and load it with `CapturedActions.Load`.
2. When gameplay starts an action (throw, pick up, place, duck, dodge), play the matching clip from time 0: each frame, call `CapturedActions.Sample` and feed the directions through the same retargeting path as the locomotion pose, instead of the authored overlay in `Arm(...)` and the duck leg override.
3. Fire the gameplay moment from the clip's event, e.g. release the ball at `EventTime(clip, "release")` and place the stone at `"place"`. That keeps hand and ball in sync.
4. Blend in and out over about 0.1–0.15 s from and to locomotion. Gameplay keeps owning the root; `root` is there if you want the body to lean into the travel.
5. Check on the phone: feet, the arm at release, and the stone in the hand at `place`.

## Fixed: left and right were mirrored in the walk/jog data

In CMU data, `np.cross([0,1,0], heading)` (the old basis in `convert_cmu_motion.py`) points to the subject's **left**. Checked on walk 02_01: dot product with the anatomical right (right hip minus left hip) = **−0.997**. In Unity, where x is right (`VillageAvatar`'s idle pose puts left limbs at −x, with no compensation elsewhere), `CapturedLocomotion.json` played **mirrored left-to-right**.

**Fixed on 30 October 2026:** the basis is now `np.cross(heading, [0,1,0])` and `CapturedLocomotion.json` was regenerated. Verified against the previous file: every direction's x component flipped sign exactly (max error 0), y/z, pelvis bob, foot contacts and the summary are identical, and the pelvis roll was already anatomical and is unchanged. **Recheck walk/jog foot contacts and the arm swing on the phone** before calling it done. `CapturedActions.json` used the anatomical right from the start.

## Limits

- These are adult recordings on a teenage body: timing and range of motion are adult.
- `Place` is a two-handed set-down from a squat. Stacking small stones one-handed would ideally be captured specifically (phone motion capture of a person acting it out).
- The dodges are running side-steps with forward momentum, not a standing hop sideways.
- Skinned clothing stretches in deep crouches (`Place`, `Duck`); the lungi needs corrective shapes or a simple cloth setup later.
