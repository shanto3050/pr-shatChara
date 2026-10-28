# M1 playable Android graybox

Working implementation · 28 October 2026. This milestone tests gameplay using simple shapes; it is not the realistic-art milestone.

## Play

- Blue is your team. The bright cyan character is the character you control. Four blue and four red players participate.
- Left stick moves. Movement is locked while holding the ball. During the initial attack, attackers stay at the throwing line; defenders can move on their side.
- Drag the right stick to aim in that direction; release to throw. Up aims toward the far end of the field. The gold line shows your aim while you hold the ball.
- Knock down the tower within three attempts. On a successful hit, collect scattered stones and return them to the center, biggest first (1 through 7).
- Pickup/placement is automatic at close range. The next required stone is gold. Teammates also collect stones and wait for their turn to stack.
- Dodge moves you quickly; Duck lowers the hit volume. They share a visible disabled-button cooldown in this first control prototype.
- On defense, retrieve the ball, aim/release at opponents, or use Pass to send it to the next teammate. A holder cannot run. An exclamation mark telegraphs an AI throw.
- You transfer to a surviving blue attacker when your current attacker is out.
- Camera switches between wide tactical and closer follow framing. Pause freezes match simulation; New match resets it. First to five wins.

Desktop checks: WASD moves, Space throws, Shift dodges, C ducks. The on-screen sticks also accept mouse input. These are development controls, not final keyboard/controller support.

## Rules used in this implementation

Three opening attempts; an opening catch or three misses changes sides without points. Rebuild deadline is 45 seconds. Successful attackers score and retain attack. All attackers out or timeout awards defense one point and switches sides. Two and a half seconds separate rounds.

Timing policy: timeout is processed first each simulation tick, then movement and stone placement, then ball contacts. Therefore a final placement takes precedence over a hit later in the same tick. Swept ball contacts resolve by the earliest intersection fraction rather than player-array order; exact tower/player contact ties favor the tower. Ground/boundary bounces remain eligible hits while the ball is sufficiently fast and within its active-flight window. These are editable prototype decisions, not a claim that all traditional variants use these rules.

## Build and automated scene checks

Open unity/SatChara in the pinned editor. **Sat Chara → Prepare Playable Graybox** authors GrayboxMatch.unity. **Sat Chara → Build Playable Android Graybox** produces Builds/Android/SatChara-Graybox.apk. Same development package ID as the foundation; installing it updates that app. Version 0.1.0, code 2.

Batch mode uses the same command pattern as android-build.md, replacing executeMethod with `SatChara.Editor.GrayboxBuild.ValidateAndBuild` and the log filename with graybox-build.log. This checks swept-contact regressions and runs the actual scene simulation to match completion before building. Validation fails if it cannot observe topples, a completed rebuild, hits, multiple rounds and a match winner. `ValidateSimulation` runs only the checks.

The .NET rules harness still checks 54 rule assertions independently. The scene simulation supplements it with movement, AI, stone interactions and ball contacts. Neither replaces real touch/camera testing or human balance feedback.

## Current implementation limits

- One open field, primitive characters, one baseline AI setting; no realistic art, character stats, roster selection, cover, hiding, audio, localization or progression yet.
- Controlled ballistic ball model with coarse spherical hit volumes; no final catching/throwing animation, full-body collision, cloth, or physically collapsing tower. Stones scatter to deterministic recoverable positions.
- Initial carrier/retriever/thrower coordination; no tactical passing or difficulty tuning. Bots can overlap. These behaviors need further playtesting.
- Camera options and control layout are experiments. The closer camera can sacrifice field coverage; choose the default based on phone tests.
- The early match result is a software integration check, not a win-rate estimate. No 20-minute frame-time or thermal benchmark has been completed.
- Core rules remain a separate package. The graybox controller intentionally centralizes scene logic for iteration; split the motor, ball and AI systems before production art/animation integration.

Full M1 approval remains pending control/camera review, rule-edge-case review, human playtests and the remaining foundation reproduction/minimum-device checks.
