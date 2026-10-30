# Decisions and open questions

## Decision log

| ID | Date | Decision | Basis / revisit trigger |
|---|---|---|---|
| D01 | 2026-10-28 | Android is the target product | User direction |
| D02 | 2026-10-28 | Pursue realistic presentation within low-end constraints | **Superseded by D15** |
| D03 | 2026-10-28 | Xiaomi 17 Ultra is an available test phone | User report; does not establish low-end support |
| D04 | 2026-10-28 | Proposed Unity + URP, offline 4 vs 4, one field first | Working technical/scope baseline; revisit after M0/M1 |
| D05 | 2026-10-28 | Replace exaggerated low-poly character proportions with believable proportions | Align older art brief with D02; retain roster identities |
| D06 | 2026-10-28 | Store editable production documents in this repository | User request; plans may change |
| D07 | 2026-10-28 | Select Unity 6000.3.27f1 LTS, Universal 3D template, matching Android modules | Live official CLI release/template discovery; installation in progress, not verified |
| D08 | 2026-10-28 | Keep match authority in an engine-independent local C# rules package | Enables automated rule checks while editor setup proceeds; physics and presentation remain separate |
| D09 | 2026-10-28 | Preserve prototype turn/scoring behavior initially; timeout wins at the deadline | Successful attackers retain attack; opening catch/misses switch without points; revisit after human playtests |
| D10 | 2026-10-28 | Record first device checks as Samsung SC-03K / Android 10 | Actual connected/authorized hardware; does not replace the unselected 4 GB minimum tier or claim Xiaomi testing |
| D11 | 2026-10-28 | M1 prototypes dual touch sticks, automatic nearby stone interaction and two camera options | Working controls for real phone comparison; preserve foundation diagnostic scene |
| D12 | 2026-10-28 | M1 tick order: timeout, movement/placement, ball contacts; earliest swept contact wins | Removes player-array collision priority; final placement precedes a later same-tick hit; exact tower/contact ties favor tower; revisit in rules review |
| D13 | 2026-10-28 | Retain wide tactical view as current default; keep closer view experimental | Graybox only. **Superseded by D18** for the realistic game |
| D14 | 2026-10-28 | Advance independent M1 prototyping while minimum-device selection remains open | Use available authorized Samsung for real builds; do not claim all foundation/device gates complete or start full realistic asset production |
| D15 | 2026-10-29 | Realistic graphics are the primary goal on mid/high phones; lower-spec phones get a simpler Low preset | User decision after realism review. Realistic minimum: Samsung SC-03K (Snapdragon 845, ~6 GB). Supersedes D02 |
| D16 | 2026-10-29 | **Open:** source of final realistic characters: evaluate the free Bablu pipeline first, then compare paid character tools or an artist if needed | Bablu v2 is an offline free-tool experiment, not an approved in-game character. Decide after a Unity/device comparison; any purchase still requires user authorization |
| D17 | 2026-10-29 | Visual benchmark: Real Cricket 24; M2 gated on a side-by-side comparison with a target frame and user sign-off | User decision. Lighting, environment, camera and motion expected to come close; characters depend on D16 |
| D18 | 2026-10-29 | Broadcast-style sports camera by default; wide tactical view as an option; presentation cameras for key moments | User: "as good as it can be developed". Supersedes D13 for the realistic game |
| D19 | 2026-10-29 | Reference photography of a real village field, houses, objects and clothing; photogrammetry for props | User confirmed it's possible. Needed before environment production |
| D20 | 2026-10-29 | Provisional manual Low/Realistic/High presets; resolution height 540/720/900; target 30 FPS | Realistic 720p initially measured 18.3 FPS on SC-03K. Mobile geometry and shadow costs were reduced, reaching near 30 FPS in short samples; these are smoke-test settings, not certification. Low has no real-time shadows; realistic uses 1024 hard shadows; High uses 2048 soft shadows. Final Low hair/LODs/blob-shadow work remains open |
| D21 | 2026-10-29 | Use official CMU subject 02 walking/jogging recordings for provisional locomotion, with source data, hashes and reuse terms included | Free recorded motion replaces the sine-wave gait. Direction-space retargeting, stride-by-distance, flat-ground foot locking and authored action overlays remain a prototype. Throws, stacking, duck and sidestep still need game-specific animation; M2 is not approved |
| D22 | 2026-10-30 | Fixed-step captured throw/pickup/place events and shared action poses; integrated village props with preserved FBX transforms and distance LODs | Serial implementation checkpoints 0.2.5–0.2.6; separate technical checks from final clothing/contact/art approval |
| D23 | 2026-10-30 | Reconcile the Chhuti draft through match → Day 1 → Chapter 1 → later chapters → online gates | Working implementation sequence from the incoming concept; current match work is reusable. The concept's 3 GB candidate supersedes the earlier 4 GB planning candidate, without certifying hardware or changing the development APK's API floor |

## Open questions

These do not block writing the plan. Resolve them at the specified gate and record outcomes above.

| Question | When needed | Working assumption |
|---|---|---|
| Which low-end phone/chipset and oldest Android version are supported by the Low preset? | Before Low-preset certification | 3 GB / Android 10 candidate from the Chhuti concept (D23), unverified; exact device unselected; realistic reference is SC-03K (D15) |
| Character source and art budget (D16) | Start of M2 | Evaluate free Bablu on-device first; paid tools or artist remain options, with explicit purchase authorization |
| Which local rule variants should be authoritative? | M1 | Browser behavior until reviewed |
| Landscape or portrait? | M1 input test | Landscape; camera direction set by D18 |
| Can low-end physical hardware be borrowed or obtained? | M0 | Access must be arranged; no purchase authorized |
| Budget for models, animation, audio and other assets? | Before any paid sourcing | Prefer available tools; request authorization for purchases |
| Is Play Store the intended distribution route? | Before beta/release preparation | Direct APK testing first; Play Store proposed for release |
| What public title, package ID, developer identity and branding? | Before signed beta | Sat Chara working title; no final package ID |
| Who provides fluent Bangla/cultural review and tester feedback? | M3/M4 | Arrange with user; do not claim review without evidence |

## Change procedure

Add a dated decision with its reason and affected milestones. Update relevant documents and backlog in the same change. Keep past decisions visible and mark superseded entries rather than deleting rationale. Estimates, quality budgets, and scope can change when real evidence supports the change.
