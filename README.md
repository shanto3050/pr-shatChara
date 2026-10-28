# সাতচারা · Sat Chara prototype

## Android production planning

The next product is a realistic 3D Android game designed to scale down to lower-spec phones. A **playable 4 vs 4 Android graybox** now runs on the test phone with touch aiming/movement, AI, stone rebuilding and scoring. This uses development shapes; realistic art and final balance are still ahead. See [controls and build instructions](docs/playable-graybox.md), the [verified phone report and gameplay clip](docs/reports/2026-10-28-graybox.md), and [development setup status](docs/setup-status.md). The browser prototype remains the original gameplay reference.

- [Detailed production plan and milestones](docs/production-plan.md)
- [Technical architecture, budgets, and verification](docs/technical-plan.md)
- [Implementation backlog and acceptance checks](docs/backlog.md)
- [Decisions, assumptions, and open questions](docs/decisions.md)
- [Asset provenance and license register](docs/asset-register.csv)
- [Visual-slice checkpoint and continuation notes (incomplete)](docs/visual-slice-status.md)

These documents are an editable v0.1 baseline dated 28 October 2026; performance figures are targets pending physical-device testing.

### C# rules implementation

The [local rules package](packages/com.satchara.rules/README.md) implements and checks the match state independently of Unity rendering. Run `dotnet run --project tools/rules-check/RulesCheck.csproj` with .NET 10 SDK (54 assertions). It also compiles in the Unity 6000.3.27f1 project at unity/SatChara. The foundation APK passed installation, rendering, rebuild/reset and basic resume checks on Samsung SC-03K (Android 10). [Android build instructions](docs/android-build.md) explain reproduction. Full gameplay and sustained performance remain pending.

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

**Team:** pick 4 of the 8 village kids (রানা Rana, মিতু Mitu, বাবলু Bablu, টুনি Tuni, সজীব Sajib, নুসরাত Nusrat, জয় Joy, শিউলি Shiuli). Your first pick is you, and the other four play for the rivals. Each character has Speed, Aim, Power and Agility stats. See the [character design sheet](docs/characters.md).

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

Current results with the default team (150 matches per setting): about 80% wins on Easy, 62% on Normal and 45% on Hard, with a median rebuild of 11–14 seconds. Team choice moves Normal by about ±10%.

## Roadmap

1. ✅ Browser prototype: rules, AI, hiding and tactics, balance tuning
2. ✅ Character roster: design sheet, 8 playable characters with stats, team picker
3. Unity (C#) Android game: realistic optimized 3D village, characters, animations, Bangla/English UI; see the production plan above.
