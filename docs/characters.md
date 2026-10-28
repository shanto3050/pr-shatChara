# Character design sheet

Eight playable kids and teenagers from one Bangladeshi village. Each match is 4 vs 4: you pick four, and the other four play for the rivals.

This sheet is the brief for the 3D characters in the Unity game. The browser prototype already uses the same names, colors and stats.

## Art direction

- **Style:** stylized low-poly (about 3–5k triangles per character), a slightly big head (about 1:5 head-to-body), flat colors with soft gradients. It has to read clearly on a small phone screen.
- **Setting:** afternoon in a village field. Characters wear everyday clothes, not sports kits (except Sajib's jersey). Most are barefoot or in rubber sandals.
- **Variety:** different skin tones, heights and body types. Nobody is a recolor of someone else.
- **Rig:** standard humanoid (Mixamo-compatible), so free animations work on every character.
- **Team marking:** a colored outline or wristband shows the team in play. Your team is blue (#3D6FC4), the rivals are red (#C0472E). Outfits stay the same on both teams.

## Stats

Every character has 13 points across four stats (1–5 each), so no one is strictly better than anyone else.

| Stat | What it changes in the game |
|---|---|
| **Speed** | Running speed: ±8% per point from 3 |
| **Aim** | Throw accuracy: ±15% spread per point from 3. Low aim adds a small wobble to your own throws. |
| **Power** | Throw speed: ±7% per point from 3. Faster balls are harder to dodge. |
| **Agility** | Dodge chance, dodge distance and duck cooldown |

## Roster

### 1. রানা · Rana · *Fast runner*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 5 | 2 | 3 | 3 |

- **Who:** 13, plays cricket on the school team and is always the first to arrive.
- **Look:** white school shirt with rolled sleeves (#F2EFE6), navy shorts (#24345C), short side-parted hair, plastic sandals he kicks off before playing. Skin #B97A4F.
- **Body:** lean and long-legged.
- **Signature animation:** a sprint start like a sprinter's.
- **Voice line:** "দৌড়া!" (Run!)

### 2. মিতু · Mitu · *Sharp shooter*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 3 | 5 | 2 | 3 |

- **Who:** 14, the eldest sister. Quiet, but she never misses.
- **Look:** green salwar kameez (#2F8F5B), orange dupatta tied across her body for play (#F08A24), hair in a low bun. Skin #C48A5C.
- **Body:** medium height, steady stance.
- **Signature animation:** closes one eye to aim before throwing.
- **Voice line:** "এবার দেখ।" (Watch this.)

### 3. বাবলু · Bablu · *Power thrower*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 2 | 3 | 5 | 3 |

- **Who:** 15, a fisherman's son. Strong from pulling nets, slow to start running.
- **Look:** blue checked lungi (#3C5AA8) folded up to the knees, sleeveless vest, red-and-white gamcha on his shoulder (#C8372D), short cropped hair. Skin #9C6440.
- **Body:** broad and heavy.
- **Signature animation:** a big wind-up overarm throw.
- **Voice line:** "ধর!" (Catch this!)

### 4. টুনি · Tuni · *Little dodger*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 4 | 2 | 2 | 5 |

- **Who:** 9, the youngest and everyone's little sister. Impossible to hit.
- **Look:** red frock (#D6453D) with a yellow hem (#F6D34A), two braids with red ribbons, barefoot. Skin #C9915F.
- **Body:** small, which makes her the smallest target in the game.
- **Signature animation:** a cartwheel dodge.
- **Voice line:** "পারলি না!" (Missed me!)

### 5. সজীব · Sajib · *Captain*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 3 | 4 | 3 | 3 |

- **Who:** 16, the natural leader who calls the plays.
- **Look:** green Bangladesh cricket jersey (#0F7A4A) with a red circle (#E0312B), track pants, football boots that are too big for him. Skin #B07148.
- **Body:** athletic, average height.
- **Signature animation:** points and shouts directions to teammates.
- **Voice line:** "দে দে, পাস দে!" (Pass it, pass it!)

### 6. নুসরাত · Nusrat · *Strategist*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 3 | 4 | 2 | 4 |

- **Who:** 14, top of the class. She reads the defenders and always finds the gap.
- **Look:** maroon school uniform (#7A2638), white hijab (#F4F1EA), white canvas shoes. Skin #C9915F.
- **Body:** slim, quick on her feet.
- **Signature animation:** a shoulder feint before dashing.
- **Voice line:** "ডান দিকে ফাঁকা!" (Right side's open!)

### 7. জয় · Joy · *Joker*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 4 | 3 | 4 | 2 |

- **Who:** 12, a rickshaw puller's son. Loud, funny, and fearless, sometimes too fearless.
- **Look:** yellow vest (#E8B828), brown shorts (#5A3B1E), curly hair, barefoot, a cheap whistle around his neck. Skin #A86B43.
- **Body:** wiry.
- **Signature animation:** a victory dance when he hits someone.
- **Voice line:** "হা হা, আউট!" (Ha ha, you're out!)

### 8. শিউলি · Shiuli · *All-rounder*
| Speed | Aim | Power | Agility |
|---|---|---|---|
| 3 | 3 | 4 | 3 |

- **Who:** 13, helps at her family's tea stall. Named after the night-jasmine flower, and steady at everything.
- **Look:** pale lavender kameez (#E7E0F2) with orange trim (#E46A1F) like a shiuli flower, high ponytail, rubber sandals. Skin #B57850.
- **Body:** medium build.
- **Signature animation:** wipes her forehead with her dupatta after a rebuild.
- **Voice line:** "সাতচারা!" (Seven stones!)

## Shared animation list (Mixamo or custom)

Idle, run, sprint, carry stone (walk and run), place stone (crouch), overarm throw, sidearm throw, pass, catch, fake throw, dodge left/right, duck, hit reaction then a fall to sitting (no injury look, just "out"), celebrate, disappointed, cheer from the sideline.

## Later

- Unlockable outfits: Eid clothes, monsoon raincoat, school sports day kit
- More characters: twins, a grandfather who referees, a kid with a pet goat that wanders onto the field
