import bpy, math, pathlib
from mathutils import Vector, Quaternion
ROOT=pathlib.Path(__file__).resolve().parent
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'village-player.blend'))
rig=next(o for o in bpy.data.objects if o.type=='ARMATURE')
for name, angle in [('upperarm_l',35),('upperarm_r',-35)]:
    bone=rig.pose.bones[name]
    axis=bone.bone.matrix_local.inverted().to_3x3() @ Vector((0,1,0))
    bone.rotation_mode='QUATERNION'; bone.rotation_quaternion=Quaternion(axis, math.radians(angle))
for material in bpy.data.materials:
    if material.use_nodes:
        node=next((n for n in material.node_tree.nodes if n.type=='BSDF_PRINCIPLED'),None)
        if node: node.inputs['Roughness'].default_value=.7
world=bpy.context.scene.world
world.use_nodes=True
world.node_tree.nodes['Background'].inputs[0].default_value=(.36,.4,.45,1)
world.node_tree.nodes['Background'].inputs[1].default_value=.4
def area(name,position,power,size):
    bpy.ops.object.light_add(type='AREA', location=position)
    obj=bpy.context.object; obj.name=name; obj.data.energy=power;obj.data.shape='DISK';obj.data.size=size
    obj.rotation_euler=(Vector((0,0,.8))-obj.location).to_track_quat('-Z','Y').to_euler()
area('Key',(-3,-4,4),350,4);area('Fill',(3,-1,2),200,3)
bpy.ops.object.camera_add(location=(2,-4,1.9))
camera=bpy.context.object;camera.rotation_euler=(Vector((0,0,.75))-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.lens=68
scene=bpy.context.scene;scene.camera=camera;scene.render.engine='CYCLES';scene.cycles.samples=24
scene.render.resolution_x=768;scene.render.resolution_y=1024;scene.render.resolution_percentage=100
scene.render.image_settings.file_format='PNG';scene.render.filepath=str(ROOT/'character-preview.png')
bpy.ops.render.render(write_still=True)
