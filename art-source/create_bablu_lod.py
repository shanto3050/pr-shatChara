"""Derive the gameplay mesh from the preserved full Bablu FBX; keep rig/UVs."""
import bpy, bmesh, pathlib, random, json
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT.parent/'unity/SatChara/Assets/SatChara/Art/Characters/Bablu'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
for material in list(bpy.data.materials):bpy.data.materials.remove(material)
bpy.ops.import_scene.fbx(filepath=str(OUT/'Bablu.fbx'))
for ob in bpy.data.objects:
    if ob.type=='ARMATURE':ob.data.pose_position='REST'
def triangles(ob):return sum(len(p.vertices)-2 for p in ob.data.polygons)
summary=[]
for ob in [o for o in bpy.data.objects if o.type=='MESH']:
    before=triangles(ob);bpy.context.view_layer.objects.active=ob
    if ob.data.shape_keys:bpy.ops.object.shape_key_remove(all=True,apply_mix=True)
    if ob.name=='HairCards':
        bm=bmesh.new();bm.from_mesh(ob.data);visited=set();drop=[];rng=random.Random(53)
        for vertex in bm.verts:
            if vertex in visited:continue
            queue=[vertex];visited.add(vertex);group=[]
            while queue:
                n=queue.pop();group.append(n)
                for edge in n.link_edges:
                    other=edge.other_vert(n)
                    if other not in visited:visited.add(other);queue.append(other)
            if rng.random()>.25:drop.extend(group)
        bmesh.ops.delete(bm,geom=drop,context='VERTS');bm.to_mesh(ob.data);bm.free()
    elif before>1000:
        ratio=.6 if ob.name=='Bablu' or ob.name.startswith('Vest') else .35 if 'Lungi' in ob.name else .5
        mod=ob.modifiers.new('Mobile reduction','DECIMATE');mod.ratio=ratio
        bpy.ops.object.modifier_apply(modifier=mod.name)
    summary.append({'mesh':ob.name,'source_triangles':before,'mobile_triangles':triangles(ob)})
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(OUT/'BabluMobile.fbx'),use_selection=True,object_types={'MESH','ARMATURE'},
    add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',path_mode='STRIP',use_mesh_modifiers=True)
report={'meshes':summary,'source_triangles':sum(r['source_triangles'] for r in summary),'mobile_triangles':sum(r['mobile_triangles'] for r in summary)}
(ROOT/'bablu-lod-summary.json').write_text(json.dumps(report,indent=2))
print('BABLU_MOBILE_EXPORTED',report['source_triangles'],report['mobile_triangles'])
