"""Generate distance meshes from the included source FBXs; keep originals intact.

Run with Blender --background --factory-startup --python this-file.py.
Only dense meshes are decimated; small leaves, cloth panels and prop silhouettes
remain intact. Straw cards are omitted from the distant haystack.
"""
import bpy
import json
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ART = ROOT.parent / 'unity/SatChara/Assets/SatChara/Art/Environment/Village'
OUT = ART / 'LODs'
OUT.mkdir(exist_ok=True)
summary = {}
for name in ['MudHouse', 'CoconutPalm', 'Haystack']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.fbx(filepath=str(ART / (name + '.fbx')))
    original = reduced = 0
    for obj in list(bpy.context.scene.objects):
        if obj.type != 'MESH':
            continue
        obj.data.calc_loop_triangles()
        count = len(obj.data.loop_triangles)
        original += count
        if name == 'Haystack' and any(m and m.name == 'StrawCards' for m in obj.data.materials):
            bpy.data.objects.remove(obj, do_unlink=True)
            continue
        if count > 160:
            mod = obj.modifiers.new('Mobile distance reduction', 'DECIMATE')
            mod.ratio = .42
            mod.use_collapse_triangulate = True
        evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        reduced += len(mesh.loop_triangles)
        evaluated.to_mesh_clear()
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT / (name + 'LOD1.fbx')),
                             use_selection=True, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
                             use_mesh_modifiers=True, mesh_smooth_type='FACE',
                             path_mode='STRIP', embed_textures=False, bake_anim=False)
    summary[name] = dict(source_triangles=original, distant_triangles=reduced, blender=bpy.app.version_string, source_sha256=hashlib.sha256((ART / (name + ".fbx")).read_bytes()).hexdigest(), lod_sha256=hashlib.sha256((OUT / (name + "LOD1.fbx")).read_bytes()).hexdigest())
    print('VILLAGE_LOD', name, original, reduced, flush=True)
(ROOT / 'village-lod-summary.json').write_text(json.dumps(summary, indent=2) + '\n')
