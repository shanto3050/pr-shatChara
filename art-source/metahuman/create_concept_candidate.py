"""Unreal 5.8: save a second candidate and render a reproducible studio portrait.

Uses the installed Epic examples for wardrobe, body sculpting, and preview actors.
Preserves the initial Bablu/Bo candidate. No cloud rig or texture request is made.
"""
import json
import time
from pathlib import Path
import unreal

asset_path = '/Game/Characters/MetaHumans/BabluConcept'
character = unreal.load_asset(asset_path)
if character is None:
    source = unreal.load_asset('/MetaHumanCharacter/Optional/Presets/Mateo.Mateo')
    if source is None: raise RuntimeError('Mateo preset is missing')
    character = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset('BabluConcept', '/Game/Characters/MetaHumans', source)
if character is None: raise RuntimeError('Candidate creation failed')
instance = character.internal_collection.default_instance
for slot in ('Beard', 'Mustache'):
    instance.set_single_slot_selection(slot_name=slot, item_key=unreal.MetaHumanPaletteItemKey())
hair_path = '/MetaHumanCharacter/Optional/Grooms/Bindings/Hair/WI_Hair_S_Messy'
hair = unreal.load_asset(hair_path)
if hair is None: raise RuntimeError('Short messy hair wardrobe item missing')
key = character.internal_collection.try_add_item_from_wardrobe_item(slot_name='Hair', wardrobe_item=hair)
instance.set_single_slot_selection(slot_name='Hair', item_key=key)
subsystem = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
if not subsystem.is_object_added_for_editing(character) and not subsystem.try_add_object_to_edit(character):
    raise RuntimeError('Cannot register candidate for editing')
constraints = subsystem.get_body_constraints(character)
for constraint in constraints:
    if str(constraint.name).lower() == 'height':
        constraint.is_active = True; constraint.target_measurement = 170.0
subsystem.set_body_constraints(character, constraints)
subsystem.commit_body_state(character)
if not unreal.EditorAssetLibrary.save_loaded_asset(character): raise RuntimeError('Candidate save failed')

# A disposable review map; the preview character is transient and is never shipped.
level = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if not level.new_level('/Game/Review/BabluStudio'): raise RuntimeError('Review map creation failed')
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
actor = subsystem.spawn_meta_human_actor(character=character, keep_transient=True)
if actor is None: raise RuntimeError('Preview actor creation failed')
actor.set_actor_location(unreal.Vector(0, 0, 0), False, False)
target = unreal.Vector(0, 0, 153)
for location, intensity, color in (
    (unreal.Vector(140, -100, 205), 2200, unreal.LinearColor(1, .94, .87)),
    (unreal.Vector(100, 110, 175), 1100, unreal.LinearColor(.85, .91, 1)),
):
    lamp = actors.spawn_actor_from_class(unreal.RectLight, location)
    lamp.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(location, target), False)
    component = lamp.get_component_by_class(unreal.RectLightComponent)
    component.set_intensity(intensity)
    component.set_light_color(color)
    component.set_editor_property('source_width', 100)
    component.set_editor_property('source_height', 100)
camera_location = unreal.Vector(125, 0, 153)
camera = actors.spawn_actor_from_class(unreal.CameraActor, camera_location)
camera.set_actor_rotation(unreal.MathLibrary.find_look_at_rotation(camera_location, target), False)
camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(32)
level.pilot_level_actor(camera)
output = Path(unreal.Paths.project_dir()).resolve().parents[2] / 'docs' / 'mockups' / 'metahuman'
output.mkdir(parents=True, exist_ok=True)
report = {'asset': character.get_path_name(), 'preset': 'Mateo', 'heightTargetCm': 170,
          'hair': hair_path, 'removedWardrobeSlots': ['Beard', 'Mustache'],
          'stage': 'Second starting candidate; likeness, teenage age, clothing and mobile adaptation unapproved'}
(output / 'candidate.json').write_text(json.dumps(report, indent=2) + '\n')
started = time.monotonic()
def capture_when_ready(delta):
    if time.monotonic() - started < 45: return
    unreal.unregister_slate_post_tick_callback(callback)
    subsystem.assemble_for_preview(character=character)
    correction = Path(__file__).with_name('adjust_studio.py')
    exec(compile(correction.read_text(encoding='utf-8'), str(correction), 'exec'), globals())
    unreal.log('SAT_CHARA_METAHUMAN_PORTRAIT_REQUESTED ' + str(output))
callback = unreal.register_slate_post_tick_callback(capture_when_ready)
unreal.log('SAT_CHARA_METAHUMAN_CONCEPT_SAVED ' + character.get_path_name())
