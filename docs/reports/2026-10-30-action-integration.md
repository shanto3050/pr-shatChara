# Captured action integration — 30 October 2026

Work proceeds in order: action integration, village prop integration/optimization, physical-device verification, then roadmap reconciliation for Chhuti. This checkpoint covers the first step; later steps are not complete.

## Runtime changes

- The avatar now loads the CMU action bank alongside locomotion. Throw, quick throw/pass, stone pickup, placement, duck and left/right dodge use captured direction-space poses with short transitions to locomotion. PickUpSquat is available and checked but is not the default pickup.
- Gameplay advances the action clock in fixed simulation steps. Pausing/suspending the match stops both the pose clock and its event. Opening throws release at 0.95 seconds, quick throws at 0.75 seconds, pickup commits at 0.95 seconds, and placement at 0.90 seconds. A fixed step can cross an event by up to one step; pending events are consumed once.
- The authoritative rules still decide whether a pickup/place is legal at the event. Pending pickups reserve a stone; dead players and new rounds clear their pending actions. Movement is stopped during pickup/place/throw recovery. Dodge root travel remains gameplay controlled. Ball catches still use existing gameplay contact logic rather than a new captured catching action.
- The ball releases from the sampled hand position; tower-distance aiming compensates for that hand offset. Carried stones follow the right hand. Actors face the target for pickup/place; dodge poses preserve their facing. Duck hit height is low during the middle of the captured crouch rather than the entire wind-up.
- The corrected anatomical walk/jog data is included. Action and locomotion banks must have identical ordered bone mappings; incompatible rigs fail explicitly. Both banks are shared across avatars.

## Verification

Unity's final run passed:

- All eight action clips: finite hand poses, unchanged gameplay root, pause holds, and completion. The alternate squat pickup is checked but not selected by gameplay.
- Corrected walk: 414 planted samples / 388 continued contacts. Jog: 231 / 194. Contact anchor error and horizontal slip rounded to 0.00000 m; these remain ideal flat-ground proxy checks, not final mesh-contact approval.
- Match pause while an opening throw is queued: action clocks and match deadline stayed unchanged.
- Full match: **8 rounds, 8 topples, 33 placements, 28 hits, score 5–3, MatchOver**. All 127 logged event crossings were within one 20 ms simulation step of their source event marker.
- Unity compilation and Android build succeeded. [Raw Unity validation](assets/action-integration-unity-validation.txt).

Physical Samsung SC-03K verification passed after the captured-hand aiming correction: pause mid-throw retained 45.00 seconds, release occurred only after resume at action time 0.960 seconds, the tower toppled, touch movement was logged, and captured pickup/place events committed during rebuilding. Round 1 ended AllOut (0–1) and round 2 started and toppled its tower. This physical test does not replace the full automated match or certify balance.

Two short Realistic gameplay windows measured **29.9 and 29.7 FPS at 1480×720**, p95 33.45 ms, p99 33.47 / 33.53 ms, with zero / one frame above 100 ms. [45-second phone recording](assets/action-integration-phone-demo.mp4) and [raw phone events](assets/action-integration-phone-validation.txt). The video was normalized to 30 FPS H.264, fully decoded and sampled visually; encoding rate is not measured runtime performance. No managed exception appeared in the captured Unity log. Touch duck/dodge inputs were sent, but this log does not instrument them individually; dedicated device contact/readability review remains open.

 The aimed point on the tower-distance plane now accounts for the actual hand's lateral release position. Actors retain their action-start orientation until recovery ends. These fixes were included in the final Unity run above.

Build **0.2.5, version code 8**, ARM64 GLES3, minimum API 26 / target API 36. APK: `unity/SatChara/Builds/Android/SatChara-Village.apk`, **73,349,717 bytes**. SHA-256: `A80265744E1E70007187ED3456968DC93B7BD718232AC460258613AE6C8C5D5B`. APKs are local build outputs, not committed to Git.

## Remaining limits

These are adult CMU recordings retargeted onto the prototype character. A baseball pitch is a provisional opening throw; the set-down is two-handed rather than a custom one-handed stone stack. Deep squats visibly stretch and intersect the lungi; clothing correction and target-frame approval remain open. Finger grasp, precise hand-to-stone contact, turning/start-stop transitions and varied-terrain contacts still need work. This checkpoint does not certify realistic final animation, a 3 GB device, sustained thermals or the expanded Chhuti story systems.


## Unity close-up evidence

These are offline Unity camera snapshots at action markers, not phone screenshots. Deep-crouch clothing defects are visible and remain open.

| Opening throw | Stone placement |
|---|---|
| ![Throw](assets/action-throw-unity.png) | ![Place](assets/action-place-unity.png) |
