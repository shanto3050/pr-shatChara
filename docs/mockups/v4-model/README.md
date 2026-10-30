# Bablu v4: 3D character refinement

31 October 2026. Work in progress against the approved [photographic concept](../bablu-v4-realistic-concept.png).

These are Blender renders of actual rigged geometry, not generated photographs. This pass changes the teenage build, face proportions, hair volume, mid-calf lungi, red-on-off-white gamcha, cotton surface variation, and portrait lighting.

The refinement replaces the disconnected vest and strap pieces with a continuous garment sampled directly from the body's rest surface, with a U neckline and armholes. The eye coat/glare is reduced, the mouth and eye shape targets are adjusted, the hair cards are shortened into a more compact silhouette, the oversized rolled lungi hem is hidden, and the gamcha gains a softer subdivided surface. Skin has restrained procedural relief and tone variation. These changes were reviewed in full-body and face renders; the result is still stylized compared with the approved concept.

![Three-quarter model render](bablu-three-quarter.jpg)

![Face model render](bablu-face.jpg)

## Rebuild

Uses the existing cached MakeHuman/MPFB assets and HDRI documented in the parent mockup README. No paid service or new character-generation subscription is used.

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --factory-startup --python-exit-code 1 --python art-source/create_mockup_bablu.py -- --design-v4 --samples 64
```

Source: `art-source/create_mockup_bablu.py` and `art-source/design_bablu_v4.py`. Outputs: ignored editable `art-source/vendor/bablu-v4-design.blend`, GLB in the same directory, and these three rendered JPGs. A portable copy is provided as [bablu-v4-design.glb](bablu-v4-design.glb). The v3 scene and existing gameplay character are preserved. This is a separate design branch of the asset, not a Unity integration. The GLB retains the skeleton and skinning but does not reproduce the offline procedural material detail exactly.

## Remaining art work

- Match the concept's face more closely: eyelids, eye appearance, lips, nose, cheek contours, and asymmetry.
- Replace the coarse hair silhouette with intentional clumps and finer hairline cards.
- Refine the lungi waist fold, knot, cotton weave, and cloth thickness.
- Refine garment fit and folds in motion, particularly squat, pickup, and throw poses.
- Bake offline skin and fabric shader detail into game textures; Blender's procedural materials and lighting do not transfer directly to Android.
- Export the selected model, tune LODs, and validate deformation and performance on-device before replacing the runtime character.

The concept remains the quality target. This first pass does not yet match its photographic realism, and no new Android performance claim is made.
