# Chhuti implementation roadmap

Working revision · 30 October 2026. This reconciles the [Chhuti concept](concept/chhuti-concept.html) with the existing [Sat Chara production plan](production-plan.md). The concept is a direction and content draft; implementation evidence is tracked separately. Adjust this roadmap as playtests and art reviews change the scope.

## Delivery order

| Stage | Deliverable | Gate before expanding |
|---|---|---|
| 0 — Current match | Finish the Sat Chara interaction loop, character/environment look development, tutorial and device quality presets | Rules review; uncoached touch playtests with 5–10 people; reference/target-frame comparison; active sustained performance test |
| 1 — Day 1 vertical slice | Arrival, Nanabari courtyard, Nani and cousins, tutorial match, evening curfew and a load-shedding night | A complete saved/reloadable Day 1; Bangla text readable on the target phone; scene/settings continuity; feedback from people familiar with village life |
| 2 — Chapter 1 | Days 1–3, limited connected locations, kanamachi/marbles and swimming basics alongside Sat Chara | Content review, stability, completion playtests, measured download/memory budgets and release policy review |
| 3 — Later chapters | Remaining holiday story, village locations and games in free content updates | Each chapter passes the same content/device gates; keep extra eras/regions as measured additions |
| 4 — Online | Multiplayer Sat Chara first; later games only after their offline versions work | Networking design, authority/latency tests, accounts, operations and a separate multiplayer beta |

The current match is the foundation of Stage 0 and the Day 1 tutorial. The village props are reusable Nanabari environment assets. Integration checkpoints do not close the art or playtest gates.

## Immediate serial queue

1. Captured action runtime integration — implemented and documented in the [0.2.5 checkpoint](reports/2026-10-30-action-integration.md); final animation/clothing approval remains open.
2. Village URP prop integration, distance LODs, terrain and physical-device comparison — [0.2.6 checkpoint](reports/2026-10-30-village-props.md).
3. Regenerate/export the free Bablu v3 into Unity and review him at match and close-up distances. Correct cloth/contact problems and establish a reference-matched target frame. The MetaHuman comparison remains an optional character-source evaluation with its own hardware/account/license checks; it is not a required engine migration.
4. Finish focused touch/rule tests (pass, duck, dodge, catches, timers, interruptions) and a small uncoached playtest. Record findings before balance changes.
5. Run sustained active gameplay/memory/thermal tests on SC-03K, then on a selected lower-memory phone. Select the real minimum from evidence.
6. Build the smallest Day 1 shell: save schema, content-driven dialogue/quest state, phase transitions, then arrival-to-bed content. Add each system with a working end-to-end scene before expanding the map.

## Choices and content architecture

The concept proposes chosen character, era and region, and switches for religious village-life scenes. Store these as versioned save/settings data. Use shared locations with explicit outfit/prop/dialogue/audio variants. Begin content production with the default around-2001 era and central-region material; additional dialects require native writers/reviewers. Select launch choices when the first complete Day 1 makes their actual cost visible.

Define durable IDs for characters, dialogue lines, quests, locations and day phases; save IDs/state rather than scene object references. Test save/reload at phase boundaries and application interruption. Keep optional scene switches consistent with quest/time progression. Content and cultural sign-off needs real reviewers; no review is implied by a document entry.

The free-with-ads concept is a future release requirement. Keep the current look-development build focused on gameplay. Before adding ads/billing, resolve audience, privacy, consent, placement and current platform requirements; then verify those choices against the release build. Ad SDKs, purchases and online services are not implemented by these checkpoints.

## Device and size reconciliation

| Topic | Current implementation/evidence | Concept target / next decision |
|---|---|---|
| Low hardware | Exact low-memory phone unselected; physical checks use SC-03K (~6 GB) | Concept asks for 3 GB / Android 10; treat this as an unverified candidate, replacing the earlier 4 GB candidate in planning |
| Resolution | Low 540px, Realistic 720px, High 900px height; 30 FPS cap | Concept Low 720p / High optional 60 FPS needs measurement; keep the measured settings until justified |
| OS | Development APK minimum API 26, target API 36 | Decide oldest supported OS after selecting hardware; Android 10 in the concept is not yet an enforced minimum |
| Size | Direct development APK; size/fingerprint recorded per checkpoint | Concept base download under 150 MB and eventual full content around 1.5–2 GB are budgets, not measured store delivery sizes |
| Content delivery | Assets bundled in the prototype | Evaluate chapter/voice asset packs at Chapter 1; do not equate development APK bytes with Play download size |

Both Samsung and the mentioned Xiaomi can test aspects of the game; neither establishes the proposed 3 GB floor. A short near-30-FPS sample does not close the sustained thermal gate.

## Still open

Final title/branding, launch regions and voices, art source/budget, exact local rule variants, lowest device, approved village references/target frame, and the availability of Bangla writers, cultural reviewers and playtesters. The full 14-day concept is substantially larger than the current sports prototype; its chapter gates control expansion.
