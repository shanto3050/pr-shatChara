# সাতচারা · Sat Chara prototype

A playable gray-box prototype of **Sat Chara** (সাতচারা, "seven stones"), the traditional Bangladeshi team game. It's used to test the rules, AI and game feel before building the full Android game in Unity.

## Play

Open `index.html` in any modern browser (desktop or phone). There's no build step and nothing to install.

- **Attack:** drag back from anywhere and release to throw at the tower. You get 3 throws.
- **Rebuild:** hold on the field (or use arrows/WASD) to run. Carry the stones to the base and stack them biggest first (1 → 7).
- **Survive:** hide behind cover, **Dodge** (Space) or **Duck** (C). Run into a loose ball to kick it away.
- **Defend:** grab the ball and throw at the rivals. You can't run with the ball, so pass it instead.
- A raised ball with **!** means a throw is coming, or a fake.

Fields: **Village** (haystacks, banana trees and drums to hide behind) or **Classic** (open field).
Rivals: Easy, Normal or Hard.

## Balance simulator

`tools/balance-sim.js` plays headless matches of `index.html` with a scripted player and reports win rates, rebuild times and hit rates per field and difficulty.

```bash
node tools/balance-sim.js 100
```

To try a tweak without editing the game:

```bash
PATCH='SK.normal.react=.8' node tools/balance-sim.js 100
```

All the balance values are in the `TUNE`, `SK` (rival skill per difficulty) and `ALLY` (your teammates) blocks at the top of the script in `index.html`.

Current results (150 matches per setting): about 87% wins on Easy, 53% on Normal and 39% on Hard, with a median rebuild of 11–15 seconds.

## Roadmap

1. Phase 0, browser prototype: rules, AI, hiding and tactics (this repo)
2. Character design sheet: roster, looks, outfits, stats
3. Unity (C#) Android game: 3D low-poly village, characters, animations, Bangla/English UI
