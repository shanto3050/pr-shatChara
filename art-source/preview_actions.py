"""Preview the captured CMU actions on the Bablu mockup: retarget CapturedActions.json onto the game rig
and render one short video per clip, plus a still at each clip's event (release, grab, place...).

Run headless:  blender -b --factory-startup -P preview_actions.py -- [--clips Throw,Duck] [--engine eevee|workbench]
Needs art-source/vendor/bablu-mockup.blend (built by create_mockup_bablu.py).
Retargeting matches each bone's direction to the recorded direction (same method as the Unity runtime);
it does not lock feet, so small foot sliding in the previews is expected.
"""
import bpy, json, math, pathlib, sys
from mathutils import Vector, Matrix

ROOT = pathlib.Path(__file__).resolve().parent
PROJECT = ROOT.parent
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
ONLY = set(ARGS[ARGS.index('--clips') + 1].split(',')) if '--clips' in ARGS else None
ENGINE = ARGS[ARGS.index('--engine') + 1] if '--engine' in ARGS else 'eevee'
OUT = PROJECT / 'docs' / 'animations'
OUT.mkdir(parents=True, exist_ok=True)

bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'vendor' / 'bablu-mockup.blend'))
data = json.loads((PROJECT / 'unity/SatChara/Assets/SatChara/Animation/CapturedActions.json').read_text())
scene = bpy.context.scene
rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
inv = rig.matrix_world.to_3x3().inverted()

def to_blender(d):
    """Clip space (x right, y up, z forward) to Blender: the character faces -Y with its right side at -X."""
    return Vector((-d['x'], -d['z'], d['y'])).normalized()

leg = (rig.data.bones['thigh_l'].head_local - rig.data.bones['calf_l'].head_local).length + \
      (rig.data.bones['calf_l'].head_local - rig.data.bones['foot_l'].head_local).length
rest_loc = rig.location.copy()
# ground height = lowest foot point in the rest pose
for _pb in rig.pose.bones: _pb.matrix_basis = Matrix.Identity(4)
bpy.context.view_layer.update()
GROUND = min((rig.matrix_world @ getattr(rig.pose.bones[b], e)).z for b in ('foot_l', 'foot_r', 'ball_l', 'ball_r') for e in ('head', 'tail'))

def reset():
    for pb in rig.pose.bones:
        pb.rotation_mode = 'QUATERNION'; pb.matrix_basis = Matrix.Identity(4)
    rig.location = rest_loc
    bpy.context.view_layer.update()

def pose(frame):
    reset()
    for name, d in zip(data['bones'], frame['directions']):
        pb = rig.pose.bones[name]
        bpy.context.view_layer.update()
        head = pb.head.copy(); cur = (pb.tail - pb.head).normalized()
        q = cur.rotation_difference(inv @ to_blender(d))
        pb.matrix = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
    # whole body travels and drops with the pelvis; bent legs keep the feet near the ground
    r = frame['root']
    rig.location = rest_loc + Vector((-r['x'], -r['z'], frame['pelvis'])) * leg
    bpy.context.view_layer.update()
    # simple ground lock: when the recording says a foot is planted, put the lowest foot point on the ground
    if frame['leftContact'] or frame['rightContact']:
        pts = [rig.matrix_world @ getattr(rig.pose.bones[b], e) for b in ('foot_l', 'foot_r', 'ball_l', 'ball_r') for e in ('head', 'tail')]
        rig.location.z += GROUND - min(p.z for p in pts)
        bpy.context.view_layer.update()

def keyframe(f):
    for name in ['pelvis'] + data['bones']:
        pb = rig.pose.bones[name]
        pb.keyframe_insert('rotation_quaternion', frame=f); pb.keyframe_insert('location', frame=f)
    rig.keyframe_insert('location', frame=f)

# camera: three-quarter front, low, like a broadcast replay; set per clip to frame the travel
cam_data = bpy.data.cameras.new('PreviewCam'); cam_data.lens = 40
cam = bpy.data.objects.new('PreviewCam', cam_data); scene.collection.objects.link(cam); scene.camera = cam
if ENGINE == 'eevee':
    for e in ('BLENDER_EEVEE_NEXT', 'BLENDER_EEVEE'):
        try: scene.render.engine = e; break
        except TypeError: pass
else:
    scene.render.engine = 'BLENDER_WORKBENCH'
scene.render.resolution_x, scene.render.resolution_y = 720, 720
scene.render.fps = data['fps']
height = max((o.matrix_world @ Vector(c)).z for o in bpy.data.objects if o.type == 'MESH' and o.name.startswith('Bablu') for c in o.bound_box)

results = []
for clip in data['clips']:
    if ONLY and clip['name'] not in ONLY: continue
    rig.animation_data_clear()
    for i, fr in enumerate(clip['frames']):
        pose(fr); keyframe(i + 1)
    n = len(clip['frames'])
    end = clip['frames'][-1]['root']
    mid = rest_loc + Vector((-end['x'], -end['z'], 0)) * leg * .5
    span = max(1.2, math.hypot(end['x'], end['z']) * leg + 1.0)
    cam.location = mid + Vector((span * .9, -span * 1.5, height * .55))
    cam.rotation_euler = (mid + Vector((0, 0, height * .45)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    scene.frame_start, scene.frame_end = 1, n
    # still at the event (release, grab, place, lowest, step)
    ev = clip['events'][0]; ef = min(n, int(round(ev['time'] * data['fps'])) + 1)
    scene.frame_set(ef)
    scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 88
    scene.render.filepath = str(OUT / f"{clip['name']}-{ev['name']}.jpg")
    bpy.ops.render.render(write_still=True)
    # short video of the whole clip
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'; scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    scene.render.filepath = str(OUT / f"{clip['name']}.mp4")
    bpy.ops.render.render(animation=True)
    results.append((clip['name'], n, ev['name'], ef))
    print('PREVIEW', clip['name'], n, 'frames; event', ev['name'], 'at frame', ef, flush=True)
reset()
print('DONE', results, flush=True)
