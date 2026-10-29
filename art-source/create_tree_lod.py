"""Create a distant-tree mesh from the existing CC0 mobile tree, preserving UVs."""
import bpy, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT.parent/'unity/SatChara/Assets/SatChara/Art/Environment'
bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
bpy.ops.import_scene.fbx(filepath=str(OUT/'island_tree_01.fbx'))
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
before=sum(len(o.data.polygons) for o in meshes)
# Separate material islands so leaf cards can be thinned as complete cards,
# rather than collapsing triangles and destroying their alpha-texture UVs.
import bmesh, random
for ob in list(meshes):
    bpy.ops.object.select_all(action='DESELECT');ob.select_set(True);bpy.context.view_layer.objects.active=ob
    bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.mesh.separate(type='MATERIAL');bpy.ops.object.mode_set(mode='OBJECT')
meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
for ob in meshes:
    labels=' '.join(m.name.lower() for m in ob.data.materials if m)
    bpy.context.view_layer.objects.active=ob
    if 'leaves' in labels:
        bm=bmesh.new();bm.from_mesh(ob.data);bm.verts.ensure_lookup_table()
        visited=set();drop=[];rng=random.Random(71)
        for v in bm.verts:
            if v in visited:continue
            group=[];queue=[v];visited.add(v)
            while queue:
                n=queue.pop();group.append(n)
                for edge in n.link_edges:
                    other=edge.other_vert(n)
                    if other not in visited:visited.add(other);queue.append(other)
            if len(group)<=12:
                if rng.random()>.25:drop.extend(group)
                else:
                    center=sum((n.co for n in group),group[0].co*0)/len(group)
                    for n in group:n.co=center+(n.co-center)*1.5
        bmesh.ops.delete(bm,geom=drop,context='VERTS');bm.to_mesh(ob.data);bm.free()
    else:
        mod=ob.modifiers.new('Distant woody reduction','DECIMATE');mod.ratio=.12
        bpy.ops.object.modifier_apply(modifier=mod.name)
bpy.ops.object.select_all(action='SELECT')
bpy.ops.export_scene.fbx(filepath=str(OUT/'island_tree_01_distant.fbx'),use_selection=True,
    add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',path_mode='STRIP')
summary={'source_faces':before,'distant_faces':sum(len(o.data.polygons) for o in meshes),
    'triangles':sum(sum(len(p.vertices)-2 for p in o.data.polygons) for o in meshes)}
(ROOT/'tree-lod-summary.json').write_text(json.dumps(summary,indent=2))
print('DISTANT_TREE_EXPORTED',summary)
