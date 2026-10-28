# Browser rules audit — Android reference

28 October 2026. Source inspection of index.html, not a human playtest. Proposed Android behavior must resolve the open issues below before claiming parity.

| Area | Observed implementation | Source function |
|---|---|---|
| Team / opening | Four per side; user team attacks first; first selected character is initially controlled | setupRound, startMatch |
| Match win | First to five points | TARGET, update |
| Attack attempts | Three throws; a miss consumes one; exhausted attempts switch sides with no point | missThrow |
| Opening catch | Defender catch ends attack immediately, switches sides, no point | updateBall |
| Tower hit | Flying ball within 24 canvas units of tower scatters all seven stones | updateBall, topple |
| Rebuild clock | 45 seconds from toppling; expiration awards defenders a point and switches sides | topple, update |
| Successful rebuild | Seventh placement awards attackers one point; attackers retain attack next round | placeStone, endRound |
| Elimination | Flying opponent ball contacting attacker eliminates them unless ducking; last attacker out awards defense a point and switches sides | updateBall, hitOut |
| Controlled player out | Control transfers to nearest surviving attacker; carried stone drops | hitOut, dropStone |
| Ball possession | Held ball follows holder; defenders can catch friendly passes; loose ball is collected by defense or kicked by attackers | catchBall, updateBall, kickBall |
| Field boundary | Ball bounces from screen bounds; players clamp inside field | updateBall, update |
| Duplicate outcomes | endRound ignores calls after round already ended | endRound |
| Between rounds | 2.4-second transition; players and tower reset | endRound, setupRound, update |

## Port decisions still needed

1. Keep successful attackers on attack or alternate every round? Current prototype explicitly retains attack.
2. Keep 45 seconds? Carry distances and 3D animations will change rebuilding time.
3. Ball has no vertical height or head/body distinction in the 2D code. Define 3D legal hit volumes and duck clearance. Do not implement blanket invulnerability just because duck is active.
4. Boundary bounces currently remain eligible to hit; decide whether bounced throws can eliminate in the Android rules.
5. A ball/tower collision is processed before player contacts. Timeout is processed before movement/ball simulation. Define simultaneous last placement/hit/timeout precedence explicitly for the 3D simulation.
6. Hits and catches use point-distance checks each frame. Android needs swept collision checks for fast balls and explicit ordering to avoid tunneling and array-order outcomes.
7. Place/carry/pickup limits and physical obstruction need separate validation. A bounded recovery rule is required for unreachable stones and balls.
8. Preserve auto-transfer of player control after elimination, but make the transition and selected character clear on screen.

Default port policy: preserve observed scoring and turns until a recorded decision changes them; improve physical validity and fairness deliberately rather than relying on accidental 2D collision behavior.
