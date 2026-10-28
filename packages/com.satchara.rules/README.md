# Sat Chara rules package

Engine-independent C# authority for turns, score, elimination and ordered rebuilding. Unity integration is pending; this package has been compiled and exercised with .NET, not yet imported by Unity.

Run from the repository root with .NET 10 SDK:

```powershell
dotnet run --project tools/rules-check/RulesCheck.csproj
```

Expected: 54 assertions pass. The harness compiles the exact Runtime/MatchState.cs file, not a separate copy. No third-party test dependencies are required.

After the official Unity project is created at unity/SatChara, add this dependency to its Packages/manifest.json:

```json
"com.satchara.rules": "file:../../../packages/com.satchara.rules"
```

Local paths resolve from the project's Packages directory; keep the repository layout intact. See [Unity local package documentation](https://docs.unity3d.com/6000.3/Documentation/Manual/upm-localpath.html).

Scene integration contract:

- Call AdvanceTime with unpaused fixed simulation delta before that tick's interaction commands. Timeout takes precedence at the deadline.
- Send physical hit/placement events in a stable, documented order. The first resolving event locks the outcome. The scene's simultaneous hit/placement tie rule still needs implementation and tests.
- Call PickUpStone only after proximity and reach checks. Call PlaceStone only at the base after its placement animation/contact requirement. Rules enforce ownership/order; they do not validate distance.
- Read CarriedStone before HitAttacker to position the dropped physical stone. Refresh UI and selected attacker after accepted commands.
- RoundOver permits StartNextRound after the presentation transition. MatchOver requires a fresh MatchState for a rematch.
- Ball ownership, movement, legal hit geometry, dodge and duck collision are separate scene/simulation responsibilities. This package does not make them implemented.
