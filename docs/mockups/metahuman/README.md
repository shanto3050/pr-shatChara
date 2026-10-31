# MetaHuman Bablu: first saved candidates

31 October 2026. This portrait is rendered from the actual Unreal MetaHuman preview actor. It is not an imagegen picture or an Android screenshot.

![Mateo-derived candidate portrait](bablu-concept-portrait.png)

## Saved assets

- `/Game/Characters/MetaHumans/Bablu.Bablu`: first candidate derived from Epic's Bo preset, with a 170 cm height target. The face preview was inspected and rejected as too heavy/mature for Bablu's direction; retained for comparison.
- `/Game/Characters/MetaHumans/BabluConcept.BabluConcept`: second candidate derived from Epic's Mateo preset, with beard/mustache slot selections cleared, short messy hair selected, and a 170 cm height target. Its assembled preview was captured and inspected above.

The source `.uasset` files are in `art-source/metahuman/BabluCreator/Content/Characters/MetaHumans` and tracked with Git LFS. They require Unreal Engine 5.8 and installed MetaHuman Creator Core Data. The height is a parametric constraint target, not a verified final runtime height. Groom culling bounds are larger than visible geometry, so camera framing uses a reviewed fixed face target.

## What this checkpoint proves

The project opens, MetaHuman assets can be created/saved/reopened, the native preview assembly works, and the model can produce a correctly framed 1200 x 1200 studio portrait. The first captures had incorrect camera direction/exposure and were replaced after visual inspection. No failed capture is presented as approved art.

## Remaining work

The second candidate is a starting point, not the approved final Bablu. It still needs the concept's facial likeness, younger appearance, complexion, dark eyes, black hair, and natural asymmetry. The hair melanin override attempted on the persistent collection did not apply because the assembled preview uses different instance state; hair tint remains open. Clothing is currently a stock white T-shirt, not the required vest, lungi, and gamcha.

There is no generated final face rig, cloud high-resolution texture request, Unity export, retargeted gameplay animation, or Android performance validation for either candidate. Desktop preview hair is not the proposed low-spec runtime setup.

## Reproduce the second candidate review

Open `art-source/metahuman/BabluCreator/BabluCreator.uproject`. In Unreal's Python tools, run `art-source/metahuman/create_concept_candidate.py`. It creates/preserves the second candidate, assembles its preview, and invokes `adjust_studio.py` after the editor ticks. Keep the editor visible while capturing; background/minimized viewports can delay screenshots. If shader compilation changes the first frame, run `adjust_studio.py` once the viewport settles. The disposable review map uses a transient actor; it is not the final character scene or a shipping asset.

The saved candidates depend on Epic's MetaHuman assets and license, not the CC0 license of the previous MakeHuman model. See [the MetaHuman production brief](../../metahuman-bablu.md) and [Epic licensing](https://www.metahuman.com/license?lang=en-US).
