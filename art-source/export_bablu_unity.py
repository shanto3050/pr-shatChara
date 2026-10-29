"""Export the regenerated Bablu scene to Unity, with explicit URP material metadata.
Run Blender -b art-source/vendor/bablu-mockup.blend -P this-script.
"""
import bpy, pathlib, json

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'unity/SatChara/Assets/SatChara/Art/Characters/Bablu'
OUT.mkdir(parents=True, exist_ok=True)
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
rig.data.pose_position = 'REST'
def image_for(socket, seen=None):
    seen = seen or set()
    for link in socket.links:
        n = link.from_node
        if n in seen: continue
        seen.add(n)
        if n.type == 'TEX_IMAGE' and n.image: return n.image
        for inp in n.inputs:
            result = image_for(inp, seen)
            if result: return result
    return None

materials=[]
for mat in bpy.data.materials:
    if not mat.use_nodes: continue
    bsdf=next((n for n in mat.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
    if not bsdf: continue
    def save_image(image):
        if not image: return ''
        name=''.join(c if c.isalnum() or c in '-_' else '_' for c in image.name)+'.png'
        if image.size[0]>1024: image.scale(1024,max(1,int(image.size[1]*1024/image.size[0])))
        image.filepath_raw=str(OUT/name); image.file_format='PNG';image.save()
        return name
    color=list(bsdf.inputs['Base Color'].default_value)
    if mat.name in [m.name for m in bpy.data.objects['Bablu'].data.materials]: color=[.62,.39,.25,1]
    base=save_image(image_for(bsdf.inputs['Base Color']))
    normal=save_image(image_for(bsdf.inputs['Normal']))
    materials.append(dict(name=mat.name,texture=base,normal=normal,color=color,
        smoothness=1-bsdf.inputs['Roughness'].default_value,cutout=bsdf.inputs['Alpha'].is_linked))
bpy.ops.object.select_all(action='DESELECT')
for ob in bpy.data.objects:
    if ob==rig or (ob.type=='MESH' and any(m.type=='ARMATURE' and m.object==rig for m in ob.modifiers)):
        ob.select_set(True)
        if ob.type=='MESH':
            for mod in list(ob.modifiers):
                if mod.type=='SUBSURF': ob.modifiers.remove(mod)
bpy.context.view_layer.objects.active=rig
bpy.ops.export_scene.fbx(filepath=str(OUT/'Bablu.fbx'),use_selection=True,object_types={'ARMATURE','MESH'},
    add_leaf_bones=False,bake_anim=False,axis_forward='-Z',axis_up='Y',apply_unit_scale=True,
    apply_scale_options='FBX_SCALE_UNITS',path_mode='STRIP',use_mesh_modifiers=True)
(OUT/'materials.json').write_text(json.dumps({'materials':materials},indent=2),encoding='utf-8')
print('BABLU_UNITY_EXPORT',len(materials),[o.name for o in bpy.context.selected_objects])
