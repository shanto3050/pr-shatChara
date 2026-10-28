import bpy, pathlib, json
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT.parent/'unity/SatChara/Assets/SatChara/Art/Environment'
summary={}
for name in ['island_tree_01','barrel_03']:
    bpy.ops.object.select_all(action='SELECT');bpy.ops.object.delete(use_global=False)
    bpy.ops.import_scene.fbx(filepath=str(ROOT/'vendor'/(name+'.fbx')))
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    print('IMPORTED',name,[(o.name,len(o.data.polygons)) for o in meshes],flush=True)
    # Keep the lowest supplied LOD if the file contains several versions.
    lods=[o for o in meshes if 'lod' in o.name.lower()]
    if lods:
        levels=sorted(set(o.name.lower().split('lod')[-1].split('_')[0] for o in lods))
        chosen=levels[-1]
        for obj in list(meshes):
            if 'lod' in obj.name.lower() and obj.name.lower().split('lod')[-1].split('_')[0]!=chosen:
                bpy.data.objects.remove(obj,do_unlink=True)
    meshes=[o for o in bpy.context.scene.objects if o.type=='MESH']
    for obj in meshes:
        if len(obj.data.polygons)>12000:
            bpy.context.view_layer.objects.active=obj
            modifier=obj.modifiers.new('Mobile mesh reduction','DECIMATE')
            modifier.ratio=max(.03, min(.5,12000/len(obj.data.polygons)))
            bpy.ops.object.modifier_apply(modifier=modifier.name)
        for poly in obj.data.polygons:poly.use_smooth=True
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.export_scene.fbx(filepath=str(OUT/(name+'.fbx')),use_selection=True,add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',path_mode='STRIP')
    summary[name]=[(o.name,len(o.data.polygons),list(o.dimensions),[m.name if m else '' for m in o.data.materials]) for o in meshes]
(ROOT/'environment-model-summary.json').write_text(json.dumps(summary,indent=2))
print('ENVIRONMENT_MODELS_EXPORTED',summary,flush=True)
