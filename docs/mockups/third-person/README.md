# First third-person camera pass

31 October 2026. `first-camera-pass.png` is an actual 1280 x 720 Unity render from the existing VillageMatch scene, with the new orbit camera and Explore presentation. It uses the fallback MakeHuman character, not the MetaHuman candidate. It is not a final graphics target or a phone screenshot.

Camera: 3.8 m trailing distance, 14 degree downward pitch, 62 degree field of view; closer shoulder framing while aiming. Empty right-side drag or right mouse drag orbits; movement and aim use camera yaw. Explore suspends match simulation and hides other players for review; return starts a fresh match. Courtyard actions and scenery collision remain unfinished.

`SatChara.Editor.ThirdPersonReview.Capture` verifies camera follow distance, yaw-relative direction, retraction before a static test wall, and shoulder framing. It also checks actual baked body geometry across 12 locomotion samples. The final run exited 0; body minima ranged from -0.01961 m to +0.01921 m against a ground height of -0.025 m. This sampling does not establish action contacts, animation quality, touch usability, sustained performance or Android compatibility.

See [the milestone plan](../../game-feel-direction.md) for the remaining character, environment and device gates.
