"""Create a CC0 MakeHuman-based clothed character and editable Blender source.
Requires the official MPFB source and selected system assets downloaded in vendor/.
"""
import bpy, pathlib, sys, json, os, shutil

ROOT = pathlib.Path(__file__).resolve().parent
PROJECT = ROOT.parent
MPFB = next((ROOT / 'vendor' / 'mpfb').glob('*/src'))
sys.path.insert(0, str(MPFB))
# Keep the add-on's transient configuration in the task workspace. This does not
# change Blender's saved preferences or patch installed/vendor source files.
extension_path = bpy.utils.extension_path_user
bpy.utils.extension_path_user = lambda package, *a, **kw: str(ROOT / 'vendor' / 'mpfb-user') if package == 'mpfb' else extension_path(package, *a, **kw)
(ROOT / 'vendor' / 'mpfb-user').mkdir(parents=True, exist_ok=True)
import mpfb
mpfb.bl_info = mpfb.fake_bl_info
bpy.context.preferences.addons.new().module = 'mpfb'
mpfb.register()
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
from mpfb.services.assetservice import AssetService
from mpfb.services.exportservice import ExportService
from mpfb.services.objectservice import ObjectService

prefs = bpy.context.preferences.addons['mpfb'].preferences
prefs.mpfb_second_root = str(ROOT / 'vendor' / 'selected-assets')
bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)
macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, age=.28, muscle=.45, weight=.4, height=.48)
macro['race'] = {'asian': .55, 'african': .20, 'caucasian': .25}
human = HumanService.create_human(macro_detail_dict=macro)
human.name = 'Village_Player'
print('BASE_CREATED', len(human.data.vertices), list(human.dimensions), flush=True)

assets_root = ROOT / 'vendor' / 'selected-assets'
skin = next(assets_root.glob('skins/young_asian_male/*.mhmat'), None)
if skin:
    HumanService.set_character_skin(str(skin), human, skin_type='GAMEENGINE')
rig = HumanService.add_builtin_rig(human, 'game_engine')
print('RIG_RETURN', repr(rig), flush=True)
print('BONES', [(o.name, [b.name for b in o.data.bones]) for o in bpy.data.objects if o.type == 'ARMATURE'], flush=True)

if '--base-only' in sys.argv:
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'vendor' / 'character-base.blend'))
    raise SystemExit(0)

items = [('eyes','low-poly.mhclo','Eyes'), ('eyebrows','eyebrow001.mhclo','Eyebrows'),
         ('hair','short01.mhclo','Hair'), ('clothes','male_casualsuit03.mhclo','Clothes')]
for folder, filename, kind in items:
    matches = list((assets_root / folder).rglob(filename))
    if not matches: raise RuntimeError('Missing required character asset: ' + filename)
    HumanService.add_mhclo_asset(str(matches[0]), human, asset_type=kind, material_type='GAMEENGINE', subdiv_levels=0)
    print('ASSET_ADDED', filename, flush=True)

ExportService.bake_modifiers_remove_helpers(human, bake_masks=True, bake_subdiv=False, remove_helpers=True)
for obj in bpy.data.objects:
    if obj.type == 'MESH':
        for poly in obj.data.polygons: poly.use_smooth = True
        for modifier in list(obj.modifiers):
            if modifier.type == 'SUBSURF': obj.modifiers.remove(modifier)

out = PROJECT / 'unity/SatChara/Assets/SatChara/Art/Characters'
out.mkdir(parents=True, exist_ok=True)
textures = out / 'Textures'
textures.mkdir(exist_ok=True)
for image in bpy.data.images:
    if image.source == 'FILE' and image.filepath:
        path = pathlib.Path(bpy.path.abspath(image.filepath))
        if path.exists():
            dest = textures / path.name
            if not dest.exists(): shutil.copy2(path, dest)
            image.filepath = str(dest)

bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'village-player.blend'))
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(out / 'VillagePlayer.fbx'), use_selection=True,
    add_leaf_bones=False, bake_anim=False, axis_forward='-Z', axis_up='Y',
    apply_unit_scale=True, apply_scale_options='FBX_SCALE_UNITS', path_mode='COPY', embed_textures=False)
summary = {'vertices': sum(len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH'),
           'objects': [(o.name, o.type) for o in bpy.data.objects],
           'materials': [(m.name, [n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image]) for m in bpy.data.materials if m.use_nodes]}
(ROOT / 'character-summary.json').write_text(json.dumps(summary, indent=2))
print('CHARACTER_EXPORTED', summary, flush=True)
