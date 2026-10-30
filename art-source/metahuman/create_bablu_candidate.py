"""Run inside Unreal 5.8 after opening BabluCreator.

Creates a separate editable starting candidate from an installed Epic preset.
No cloud requests, rig generation, asset replacement, or paid services.
"""
import json
from pathlib import Path
import unreal

destination = '/Game/Characters/MetaHumans/Bablu'
character = unreal.load_asset(destination)
if character is None:
    source = unreal.load_asset('/MetaHumanCharacter/Optional/Presets/Bo.Bo')
    if source is None:
        raise RuntimeError('Installed Bo preset missing; verify MetaHuman Creator Core Data')
    character = unreal.AssetToolsHelpers.get_asset_tools().duplicate_asset(
        'Bablu', '/Game/Characters/MetaHumans', source)
if not isinstance(character, unreal.MetaHumanCharacter):
    raise RuntimeError('Bablu candidate is not a MetaHuman Character asset')
subsystem = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
added = not subsystem.is_object_added_for_editing(character)
if added and not subsystem.try_add_object_to_edit(character):
    raise RuntimeError('Unable to open MetaHuman editing state')
try:
    constraints = subsystem.get_body_constraints(character)
    height = next((c for c in constraints if str(c.name).lower() == 'height'), None)
    if height is None:
        raise RuntimeError('Height constraint missing; inspect installed API')
    height.is_active = True
    height.target_measurement = 170.0
    subsystem.set_body_constraints(character, constraints)
    subsystem.commit_body_state(character)
    if not unreal.EditorAssetLibrary.save_loaded_asset(character):
        raise RuntimeError('Failed to save Bablu candidate')
    report = {
        'asset': character.get_path_name(),
        'startingPreset': '/MetaHumanCharacter/Optional/Presets/Bo.Bo',
        'heightTargetCm': 170,
        'stage': 'Editable starting candidate; face, skin, hair, clothing and art approval pending',
        'bodyConstraints': [str(c.name) for c in constraints],
        'rigAndCloudTexturesRequested': False,
    }
    output = Path(unreal.Paths.project_saved_dir()) / 'bablu-candidate.json'
    output.write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    unreal.log('SAT_CHARA_METAHUMAN_CANDIDATE_SAVED ' + str(output))
finally:
    if added: subsystem.remove_object_to_edit(character)
unreal.get_editor_subsystem(unreal.AssetEditorSubsystem).open_editor_for_assets([character])
