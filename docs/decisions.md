# Decisions and open questions

## Decision log

| ID | Date | Decision | Basis / revisit trigger |
|---|---|---|---|
| D01 | 2026-10-28 | Android is the target product | User direction |
| D02 | 2026-10-28 | Pursue realistic presentation within low-end constraints | User direction; validate at M2 |
| D03 | 2026-10-28 | Xiaomi 17 Ultra is an available test phone | User report; does not establish low-end support |
| D04 | 2026-10-28 | Proposed Unity + URP, offline 4 vs 4, one field first | Working technical/scope baseline; revisit after M0/M1 |
| D05 | 2026-10-28 | Replace exaggerated low-poly character proportions with believable proportions | Align older art brief with D02; retain roster identities |
| D06 | 2026-10-28 | Store editable production documents in this repository | User request; plans may change |

## Open questions

These do not block writing the plan. Resolve them at the specified gate and record outcomes above.

| Question | When needed | Working assumption |
|---|---|---|
| Which low-end phone/chipset and oldest Android version are supported? | M0, before performance certification | 4 GB candidate, exact device/OS unselected |
| Which local rule variants should be authoritative? | M1 | Browser behavior until reviewed |
| Landscape or portrait; camera choice? | M1 input test | Landscape, compare elevated follow and tactical cameras |
| Can low-end physical hardware be borrowed or obtained? | M0 | Access must be arranged; no purchase authorized |
| Budget for models, animation, audio and other assets? | Before any paid sourcing | Prefer available tools; request authorization for purchases |
| Is Play Store the intended distribution route? | Before beta/release preparation | Direct APK testing first; Play Store proposed for release |
| What public title, package ID, developer identity and branding? | Before signed beta | Sat Chara working title; no final package ID |
| Who provides fluent Bangla/cultural review and tester feedback? | M3/M4 | Arrange with user; do not claim review without evidence |

## Change procedure

Add a dated decision with its reason and affected milestones. Update relevant documents and backlog in the same change. Keep past decisions visible and mark superseded entries rather than deleting rationale. Estimates, quality budgets, and scope can change when real evidence supports the change.
