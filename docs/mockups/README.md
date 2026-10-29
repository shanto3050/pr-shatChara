# Character mockups

## Bablu (বাবলু): free resources only

**Purpose:** see how close free tools get to the Real Cricket 24 benchmark (D17) before deciding on paid tools or an artist (D16).

### Version 2, 29 October 2026

![Bablu v2, three-quarter view](bablu-three-quarter.jpg)

| Front | Face |
|---|---|
| ![Front](bablu-front.jpg) | ![Face](bablu-face.jpg) |

What changed from version 1 (all still free):

- **Lungi:** simulated with Blender's cloth solver. The waist is pinned, spare fabric settles on the posed body and forms real folds, and the folded hem follows the settled edge.
- **Hair:** 1,600 hair cards grown from the MakeHuman hair cap, with a generated strand texture (soft roots, thin tips). The fringe is swept aside and kept above the eyes.
- **Skin:** a tiling pore normal map (also exported to the 3D model) and stronger subsurface scattering in the renders.
- **Gamcha:** wider and with more detail across, still shaped rather than simulated. A simulated version crumpled, and a thick towel keeps its drape anyway.

### Version 1 (first attempt)

| Three-quarter | Face |
|---|---|
| ![v1](v1/bablu-three-quarter.jpg) | ![v1 face](v1/bablu-face.jpg) |

### How it's made

`art-source/create_mockup_bablu.py`, run headless in Blender 4.5 LTS.

- Body, skin, eyes, brows, lashes and hair cap: MakeHuman CC0 assets through the MPFB2 v2.0.18 add-on. Age about 15, broad build, skin tinted toward #9C6440, black hair.
- Clothing generated from the body's evaluated shape and skinned to the same game rig: a lungi (blue check, waist roll, tuck knot, hem), a vest with shoulder straps, and a red-and-white checked gamcha.
- Light: Poly Haven "Evening Field" HDRI (CC0) plus a warm low sun; ground uses the project's village-earth texture.
- Renders: Cycles, 128 samples, AgX. The full build takes about 2 minutes plus rendering on a desktop CPU.

To rebuild: download the assets with `fetch_mockup_assets.py` (needs MPFB2 v2.0.18 in `art-source/vendor/mpfb/` and the HDRI in `art-source/vendor/hdri/`), then run:

```bash
blender -b --factory-startup -P art-source/create_mockup_bablu.py -- --samples 128
```

The `.blend` file and the web 3D model (`.glb`) are written to `art-source/vendor/` and aren't committed until Git LFS is set up (backlog V00).

### Assessment against the benchmark

| Area | Version 1 | Version 2 |
|---|---|---|
| Proportions, build, skin tone | Good | Good |
| Rig (Unity, mocap) | Good | Good |
| Light | Good | Good |
| Lungi | Stiff tube | Real folds (simulated) |
| Hair | Helmet-like cap | Strand cards; fine at game distance |
| Face | Smooth, generic | Slightly better skin shading; still generic. **Main remaining gap** |
| Vest, gamcha | Stiff | Still shaped, no wrinkles |

The biggest free improvement left is a **face photo-texture**: project a real reference photo onto the face (with the person's consent) and sculpt the face shape to match. After that, the free route hits its limit on facial detail. The renders are offline quality; the in-game real-time look is flatter.
