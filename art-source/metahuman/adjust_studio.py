"""Reframe the live review camera and lock exposure before recapturing."""
import json
import time
from pathlib import Path
import unreal

subsystem = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
character = unreal.load_asset('/Game/Characters/MetaHumans/BabluConcept')
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
actors = unreal.GameplayStatics.get_all_actors_of_class(world, unreal.Actor)
camera = next(a for a in actors if isinstance(a, unreal.CameraActor))
human = next(a for a in actors if 'PreviewActor' in a.get_class().get_name() or a.get_actor_label().startswith('BabluConcept'))
origin, extent = human.get_actor_bounds(False)
# Groom culling bounds extend above the actual crown; use the reviewed face framing.
target = unreal.Vector(0, 0, 174)
location = unreal.Vector(0, 110, target.z)
camera.set_actor_location(location, False, False)
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, target), False)
component = camera.get_component_by_class(unreal.CameraComponent)
component.set_field_of_view(25)
component.set_editor_property('constrain_aspect_ratio', True)
component.set_editor_property('aspect_ratio', 1.0)
settings = component.get_editor_property('post_process_settings')
settings.set_editor_property('override_auto_exposure_min_brightness', True)
settings.set_editor_property('override_auto_exposure_max_brightness', True)
settings.set_editor_property('auto_exposure_min_brightness', 7.0)
settings.set_editor_property('auto_exposure_max_brightness', 7.0)
component.set_editor_property('post_process_settings', settings)
for a, position, intensity in zip([a for a in actors if isinstance(a, unreal.RectLight)],
                                  [(-90, 130, 205), (100, 80, 175)], [60, 30]):
    new = unreal.Vector(*position)
    a.set_actor_location(new, False, False)
    a.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(new, target), False)
    a.get_component_by_class(unreal.RectLightComponent).set_intensity(intensity)
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
level.pilot_level_actor(camera)
output = Path(unreal.Paths.project_dir()).resolve().parents[2] / 'docs/mockups/metahuman'
(output / 'studio-bounds.json').write_text(json.dumps({'origin': [origin.x, origin.y, origin.z], 'extent': [extent.x, extent.y, extent.z], 'targetZ': target.z}, indent=2) + '\n')
unreal.AutomationLibrary.take_high_res_screenshot(1200, 1200, str(output / 'bablu-concept-portrait.png'), camera=camera, delay=5)
unreal.log('SAT_CHARA_METAHUMAN_STUDIO_ADJUSTED')
