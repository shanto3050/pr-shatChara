# Village reference photos

Photo sites the user suggested on 30 October 2026 for making the map and environment realistic. Licenses were checked on that date on each site's own license page.

## Which sites we can use, and how

| Site | License | Use as reference (look and match) | Use inside the game (textures, decals, skies) | Credit |
|---|---|---|---|---|
| [Pexels](https://www.pexels.com/search/bangladesh%20village/) | [Pexels License](https://www.pexels.com/license/): free, may be modified | Yes | Yes, once modified (cropped, made tileable, colour-matched) | Not required; we list sources in `docs/asset-register.csv` anyway |
| [Pixabay](https://pixabay.com/images/search/village%20of%20bangladesh/) | [Pixabay Content License](https://pixabay.com/service/license-summary/): free, may be modified | Yes | Yes, once modified; avoid images with visible brands or logos | Not required; listed in the register |
| [Vecteezy](https://www.vecteezy.com/free-photos/bangladesh-village) | [Free License](https://www.vecteezy.com/licensing-agreement): **attribution required**, otherwise a paid Pro license | Yes | Only with a credit in the game's credits screen, per image; check each image's license badge (some are Pro only) | Required |
| [Shutterstock](https://www.shutterstock.com/search/beautiful-village-bangladesh) | **Paid.** The previews are watermarked and not licensed | Look only | **No.** Don't download previews or use them in any way | n/a |

Rules for the project:

- **Recognisable people:** photos showing them are for reference only, never put into the game (both Pexels and Pixabay restrict how identifiable people may be shown).
- **Photos as textures:** scene photos make poor textures directly, because the light and perspective are baked in. For surfaces (mud, straw, bark, brick) we keep using CC0 scanned materials (ambientCG, Poly Haven) or close-up, flat photos made tileable.
- **Before any image goes into the repo:** record it in `docs/asset-register.csv` with its source URL, license and the date.

## What the photos show that our village gets wrong

Compared against our renders in `docs/environment/` (pond-edge, clothes-line-rickshaw, courtyard-broadcast):

1. **It's green, not dry.** Every village photo is dense green: rice fields, grass verges, trees overhead. Our courtyard is a bare brown plain under an HDRI of a dry European field with leafless trees. This is the single biggest reason it doesn't read as Bangladesh. Fix:
   - a lush summer sky/HDRI (or a painted backdrop of tree lines)
   - green ground cover off the swept courtyard
   - many more trees
2. **Villages are enclosed by trees.** Homesteads sit inside a ring of mango, jackfruit, banana, coconut, betel-nut (supari) and bamboo, with only glimpses of open field. Paths run through green tunnels. Our scene is open in every direction.
3. **Tall slender palms in rows.** Betel-nut (areca) and date palms line paths and ponds. We have one coconut palm.
4. **Only the courtyard is swept bare.** Elsewhere the ground is grass, weeds and leaf litter. Paths are packed earth with grass verges, or raised brick paths (herringbone brick roads) on the main routes.
5. **Ponds are dark green, overhung with trees,** with a bamboo or brick ghat and water plants at the edges. Ours sits in the open.
6. **Haystacks are tall, narrow cones on a pole** standing among green. Ours matches the shape well; it needs green around it.
7. **Light is humid and hazy:** soft sun, a pale sky, distant tree lines fading into mist. Our light is clean and crisp.
8. **Common objects:**
   - aluminium/silver kolshi alongside clay ones
   - bamboo baskets and woven fish traps
   - wooden and bamboo footbridges over khals
   - cows and ducks everywhere
   - jute drying on bamboo racks

## Useful reference photos (Pexels, checked 30 October 2026)

Links only; nothing has been downloaded.

- Lush village and tree lines: [Netrokona village](https://www.pexels.com/photo/lush-village-landscape-in-netrokona-bangladesh-32766721/), [green fields](https://www.pexels.com/photo/serene-green-fields-in-rural-bangladesh-28948362/), [dirt road and tree](https://www.pexels.com/photo/a-dirt-road-leading-to-a-field-with-a-tree-in-the-middle-20432036/)
- Paths: [footpath through trees](https://www.pexels.com/photo/footpath-in-forest-in-village-26563001/), [cyclists on rural path](https://www.pexels.com/photo/cyclists-and-pedestrians-on-rural-path-in-bangladesh-36776235/), [bicycle with straw](https://www.pexels.com/photo/bicycle-with-straw-load-on-rural-path-in-bangladesh-34935537/), [boy pulling a cart](https://www.pexels.com/photo/back-view-shot-of-a-boy-pulling-brown-wooden-cart-on-a-walkway-12036749/)
- Bridges and water: [wooden bridge](https://www.pexels.com/photo/children-walking-on-wooden-bridge-in-bangladesh-village-34793481/), [fishermen on river](https://www.pexels.com/photo/fishermen-on-tranquil-river-in-bangladesh-35124585/), [Rangpur riverbank](https://www.pexels.com/photo/rural-riverbank-scene-in-rangpur-bangladesh-35111209/), [drying crops by river](https://www.pexels.com/photo/rural-workers-drying-crops-by-river-in-dhaka-37513335/)
- Houses and crafts: [hut on the countryside](https://www.pexels.com/photo/a-hut-on-the-countryside-10000475/), [bamboo basket weaver](https://www.pexels.com/photo/village-handicraftsman-weaving-bamboo-baskets-34775925/), [processing jute](https://www.pexels.com/photo/woman-processing-jute-from-a-jute-plant-9492213/)
- Fields and animals: [ploughing](https://www.pexels.com/photo/farmer-ploughing-field-in-rural-bangladesh-35633238/), [herding ducks](https://www.pexels.com/photo/farmer-herding-ducks-in-rural-bangladesh-countryside-36726783/), [farmer with cow](https://www.pexels.com/photo/bangladeshi-farmer-walking-with-cow-in-lush-field-36726788/), [farmers and cattle](https://www.pexels.com/photo/rural-lifestyle-with-farmers-and-cattle-in-bangladesh-36811391/)

## Next step

"Green the village" pass on `art-source/create_village_props.py`:

- Ground and sky:
  - lush sky/HDRI or tree-line backdrop
  - grass and weed cover outside the swept courtyard
  - leaf litter
  - humid haze
- Plants:
  - a ring of mango and jackfruit trees around the homestead
  - betel-nut palms in a row
  - a bamboo clump
- Build items:
  - pond under trees with a bamboo ghat
  - a brick path
  - a bamboo footbridge
- Re-render, then compare side by side with the photos above.
