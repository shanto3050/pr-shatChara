"""Bablu (বাবলু) character mockup built only from free/CC0 resources.

Body, skin, eyes, brows and hair: MakeHuman CC0 assets through MPFB2 (run fetch_mockup_assets.py first).
Clothing (lungi, vest, gamcha): generated here from the body's own shape, skinned to the same rig.
Lighting: Poly Haven "Evening Field" HDRI (CC0) plus a low warm sun.

Run headless:  blender -b --factory-startup -P create_mockup_bablu.py -- [--no-render] [--samples N]
Outputs: docs/mockups/bablu-*.jpg, vendor/bablu-mockup.blend, vendor/bablu-mockup.glb (web viewer copy).
"""
import bpy, bmesh, pathlib, sys, math, json
import numpy as np
from mathutils import Vector, Matrix, Quaternion

ROOT = pathlib.Path(__file__).resolve().parent
PROJECT = ROOT.parent
VENDOR = ROOT / 'vendor'
import tempfile
(VENDOR / 'tmp').mkdir(parents=True, exist_ok=True)
tempfile.tempdir = str(VENDOR / 'tmp')
ASSETS = VENDOR / 'selected-assets'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAMPLES = int(ARGS[ARGS.index('--samples') + 1]) if '--samples' in ARGS else 128
OUT_IMG = PROJECT / 'docs' / 'mockups'
OUT_IMG.mkdir(parents=True, exist_ok=True)

# ---------- MPFB setup (same approach as create_character.py) ----------
MPFB = next((VENDOR / 'mpfb').glob('*/src'))
sys.path.insert(0, str(MPFB))
extension_path = bpy.utils.extension_path_user
bpy.utils.extension_path_user = lambda package, *a, **kw: str(VENDOR / 'mpfb-user') if package == 'mpfb' else extension_path(package, *a, **kw)
(VENDOR / 'mpfb-user').mkdir(parents=True, exist_ok=True)
resource_path = bpy.utils.resource_path
bpy.utils.resource_path = lambda kind: str(VENDOR / "blender-user") if kind == "USER" else resource_path(kind)
import mpfb
mpfb.bl_info = mpfb.fake_bl_info
bpy.context.preferences.addons.new().module = 'mpfb'
mpfb.register()
from mpfb.services.humanservice import HumanService
from mpfb.services.targetservice import TargetService
from mpfb.services.exportservice import ExportService
bpy.context.preferences.addons['mpfb'].preferences.mpfb_second_root = str(ASSETS)

bpy.ops.object.select_all(action='SELECT')
bpy.ops.object.delete(use_global=False)

# ---------- body: Bablu, 15, broad and heavy (docs/characters.md) ----------
macro = TargetService.get_default_macro_info_dict()
macro.update(gender=1.0, age=.272, muscle=.62, weight=.64, height=.58)
macro['race'] = {'asian': .50, 'african': .30, 'caucasian': .20}
human = HumanService.create_human(macro_detail_dict=macro)
human.name = 'Bablu'

# Face: a distinct Bengali teenage boy, not MakeHuman's default. Uses MakeHuman's CC0 shape targets
# (shipped in the packaged MPFB 2.0.18 release). '*' means the left and right versions.
FACE = {
    'nose-scale-horiz-incr': .45, 'nose-flaring-incr': .5, 'nose-nostrils-width-incr': .4, 'nose-point-width-incr': .35,
    'nose-volume-incr': .25, 'nose-hump-decr': .2, 'nose-scale-vert-decr': .1,
    'mouth-upperlip-volume-incr': .1, 'mouth-lowerlip-height-decr': .25, 'mouth-scale-depth-decr': .3, 'mouth-scale-horiz-incr': .12, 'mouth-lowerlip-middle-up': .25,
    'mouth-cupidsbow-incr': .3, 'mouth-angles-up': .15,
    '*eye-scale-incr': .04, '*eye-push1-in': .2, '*eye-bag-incr': .22, '*eye-height2-incr': .1,
    'eyebrows-trans-down': .25, 'eyebrows-angle-down': .1,
    '*cheek-bones-incr': .3, '*cheek-volume-incr': .25,
    'chin-width-incr': .3, 'chin-prominent-incr': .15, 'chin-bones-incr': .2,
    'head-round': .3, 'head-fat-incr': .2, 'head-scale-horiz-incr': .1, 'forehead-scale-vert-decr': .15,
}
for name, value in FACE.items():
    for n in (['l-' + name[1:], 'r-' + name[1:]] if name.startswith('*') else [name]):
        path = TargetService.target_full_path(n)
        if path: TargetService.load_target(human, path, weight=value, name=n)
        else: print('NO_TARGET', n, flush=True)
print('FACE_TARGETS', len(FACE), flush=True)
skin = next(ASSETS.glob('skins/young_asian_male/*.mhmat'), None) or next(ASSETS.glob('skins/**/*.mhmat'))
HumanService.set_character_skin(str(skin), human, skin_type='GAMEENGINE')
HumanService.add_builtin_rig(human, 'game_engine')
for folder, name, kind in [('eyes', 'low-poly.mhclo', 'Eyes'), ('eyebrows', 'eyebrow001.mhclo', 'Eyebrows'),
                           ('eyelashes', 'eyelashes01.mhclo', 'Eyelashes'), ('hair', 'short02.mhclo', 'Hair')]:
    found = list((ASSETS / folder).rglob(name))
    if found:
        HumanService.add_mhclo_asset(str(found[0]), human, asset_type=kind, material_type='GAMEENGINE', subdiv_levels=0)
        print('ASSET', name, flush=True)
    else:
        print('MISSING', name, flush=True)
ExportService.bake_modifiers_remove_helpers(human, bake_masks=True, bake_subdiv=False, remove_helpers=True)

rig = next(o for o in bpy.data.objects if o.type == 'ARMATURE')
body = human
for o in bpy.data.objects:
    if o.type == 'MESH':
        for p in o.data.polygons: p.use_smooth = True
print('BONES', [b.name for b in rig.data.bones][:40], flush=True)

def bone(*keys):
    for k in keys:
        for b in rig.data.bones:
            if b.name.lower() == k: return b
    for k in keys:
        for b in rig.data.bones:
            if k in b.name.lower(): return b
    raise KeyError(keys)
def head_w(b): return rig.matrix_world @ b.head_local
def tail_w(b): return rig.matrix_world @ b.tail_local

# body vertices (world) and per-vertex group weights. The age/build lives in shape keys, so read the
# evaluated mesh: the raw vertex data is MakeHuman's default adult base mesh.
dg = bpy.context.evaluated_depsgraph_get()
body_eval = body.evaluated_get(dg); me_eval = body_eval.to_mesh()
V = np.array([body_eval.matrix_world @ v.co for v in me_eval.vertices])
Nrm = np.array([(body_eval.matrix_world.to_3x3() @ v.normal).normalized() for v in me_eval.vertices])
body_eval.to_mesh_clear()
gidx = {g.name.lower(): g.index for g in body.vertex_groups}
# MakeHuman keeps hidden helper geometry (skirt/tights cages, hair helper, joint cubes) in the
# body mesh. Only vertices in the 'body' group are real skin; everything below uses those.
is_body = np.zeros(len(V), bool)
for v in body.data.vertices:
    is_body[v.index] = any(g.group == gidx['body'] and g.weight > 0 for g in v.groups)
print('SKIN_VERTS', int(is_body.sum()), 'of', len(V), flush=True)
V = np.where(is_body[:, None], V, np.nan)
def weights(*names):
    w = np.zeros(len(V))
    ids = {gidx[n] for n in gidx if any(k in n for k in names)}
    for v in body.data.vertices:
        for g in v.groups:
            if g.group in ids: w[v.index] += g.weight
    return w
w_arm = weights('upperarm', 'lowerarm', 'hand', 'arm', 'thumb', 'index', 'middle', 'ring', 'pinky')
w_spine = weights('spine')
w_neck = weights('neck', 'head')

z_knee = head_w(bone('calf_l', 'calf.l', 'lowerleg')).z
z_hip = head_w(bone('thigh_l', 'thigh.l', 'upperleg')).z
z_navel = head_w(bone('spine_02', 'spine02', 'spine')).z
z_neck = head_w(bone('neck_01', 'neck')).z
z_head_top = float(np.nanmax(V[:, 2]))
z_floor = float(np.nanmin(V[:, 2]))
height = z_head_top - z_floor
cx, cy = float(np.nanmean(V[:, 0])), float(np.nanmean(V[:, 1]))
print('LANDMARKS', dict(knee=z_knee, hip=z_hip, navel=z_navel, neck=z_neck, height=height), flush=True)

def hull_radius(P, angles):
    """Distance from the origin to the convex hull of 2D points P along each angle."""
    pts = sorted(map(tuple, P))
    if len(pts) < 3: return np.full(len(angles), .15)
    def half(seq):
        h = []
        for p in seq:
            while len(h) >= 2 and (h[-1][0] - h[-2][0]) * (p[1] - h[-2][1]) - (h[-1][1] - h[-2][1]) * (p[0] - h[-2][0]) <= 0: h.pop()
            h.append(p)
        return h
    hull = np.array(half(pts)[:-1] + half(pts[::-1])[:-1])
    out = []
    for a in angles:
        d = np.array([math.cos(a), math.sin(a)]); best = 0.
        for k in range(len(hull)):
            p, q = hull[k], hull[(k + 1) % len(hull)]; e = q - p
            den = d[0] * e[1] - d[1] * e[0]
            if abs(den) < 1e-9: continue
            t = (p[0] * e[1] - p[1] * e[0]) / den; s = (p[0] * d[1] - p[1] * d[0]) / den
            if t > 0 and -1e-6 <= s <= 1 + 1e-6: best = max(best, t)
        out.append(best)
    return np.array(out)

# ---------- texture helpers (image textures so the GLB export keeps them) ----------
def make_image(name, arr):
    h, w = arr.shape[:2]
    img = bpy.data.images.new(name, w, h, alpha=False)
    rgba = np.concatenate([arr, np.ones((h, w, 1))], axis=2).astype(np.float32)
    img.pixels.foreach_set(rgba.ravel())
    img.pack()
    return img

def plaid(n, base, stripes, seed):
    """Woven check: sum of horizontal and vertical stripe bands, slight yarn noise."""
    rng = np.random.default_rng(seed)
    t = np.arange(n) / n
    col = np.tile(np.array(base, float), (n, n, 1))
    for (c, pos, width, strength) in stripes:
        band = (np.abs(((t - pos + .5) % 1) - .5) < width).astype(float)
        mask = np.maximum(band[None, :], band[:, None]) * strength
        both = band[None, :] * band[:, None]
        col = col * (1 - mask[..., None]) + np.array(c) * mask[..., None]
        col = col * (1 - .25 * both[..., None])
    weave = ((np.arange(n)[None, :] + np.arange(n)[:, None]) % 4 < 2) * .05
    col *= (1 - weave[..., None]) * (1 + rng.normal(0, .025, (n, n, 1)))
    return np.clip(col, 0, 1)

def cloth_material(name, img, rough=.85, sheen=.4):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; bsdf = nt.nodes['Principled BSDF']
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = img
    nt.links.new(tex.outputs['Color'], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = rough
    if 'Sheen Weight' in bsdf.inputs: bsdf.inputs['Sheen Weight'].default_value = sheen
    return m

lungi_img = make_image('lungi_check', plaid(512, (.10, .17, .42), [
    ((.55, .62, .78), .10, .018, 1), ((.55, .62, .78), .14, .006, 1), ((.06, .08, .22), .55, .09, .8),
    ((.80, .78, .70), .35, .004, 1), ((.80, .78, .70), .85, .004, 1)], 1))
gamcha_img = make_image('gamcha_check', plaid(256, (.78, .10, .10), [
    ((.95, .93, .88), .25, .08, 1), ((.95, .93, .88), .75, .08, 1), ((.20, .45, .20), .5, .012, 1)], 2))
rng = np.random.default_rng(3)
vest_arr = np.clip(np.array([.88, .86, .80]) * (1 + rng.normal(0, .03, (256, 256, 1))) - (np.arange(256)[:, None, None] % 3 == 0) * .03, 0, 1)
vest_img = make_image('vest_cotton', vest_arr)

ARM_BONES = ('upperarm', 'lowerarm', 'hand', 'thumb', 'index', 'middle', 'ring', 'pinky')
def skin_to_body(obj, drop=ARM_BONES):
    """Copy bone weights from the nearest body surface and bind to the rig.
    Clothing that shouldn't follow the arms (lungi, gamcha) drops arm/hand weights."""
    dt = obj.modifiers.new('weights', 'DATA_TRANSFER')
    dt.object = body; dt.use_vert_data = True; dt.data_types_verts = {'VGROUP_WEIGHTS'}
    dt.vert_mapping = 'POLYINTERP_NEAREST'; dt.layers_vgroup_select_src = 'ALL'; dt.layers_vgroup_select_dst = 'NAME'
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.datalayout_transfer(modifier=dt.name)
    bpy.ops.object.modifier_apply(modifier=dt.name)
    for g in list(obj.vertex_groups):
        if any(k in g.name.lower() for k in drop): obj.vertex_groups.remove(g)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    arm = obj.modifiers.new('rig', 'ARMATURE'); arm.object = rig
    obj.parent = rig

def mesh_object(name, verts, faces, uvs=None, mat=None):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    if uvs is not None:
        uvl = me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices): uvl.data[li].uv = uvs[vi]
    for p in me.polygons: p.use_smooth = True
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    if mat: ob.data.materials.append(mat)
    return ob

# ---------- lungi: a tube that wraps both legs (support function of the body section) ----------
# Built for cloth simulation (run after posing): the top rows are pinned tight at the waist, the rest
# starts wider than the legs so gravity and body collision form real folds. The seam is welded.
NA, NR = 96, 34
z_top, z_bot = z_navel - .05, z_knee + .035
legs = (w_arm < .05)
rng_l = np.random.default_rng(7)
rings, uvs = [], []
prev = None
for j in range(NR + 1):
    t = j / NR; z = z_top + (z_bot - z_top) * t
    band = legs & (np.abs(V[:, 2] - z) < .05)                             # wide band: thighs slope forward
    P = V[band][:, :2] - [cx, cy]
    ring = hull_radius(P, [2 * math.pi * i / NA for i in range(NA)])
    ring = (np.roll(ring, 1) + 2 * ring + np.roll(ring, -1)) / 4            # smooth around
    if prev is not None: ring = np.maximum(ring, prev * .97)               # no pinching between the legs
    prev = ring
    for i in range(NA):
        a = 2 * math.pi * i / NA
        slack = .009 if j <= 1 else .02 + .045 * t ** .7 + rng_l.normal(0, .002)   # spare fabric lower down
        r = ring[i] + slack
        rings.append((cx + r * math.cos(a), cy + r * math.sin(a), z))
        uvs.append((i / NA * 3, (z_top - z) * 3))
faces = [(j * NA + i, j * NA + (i + 1) % NA, (j + 1) * NA + (i + 1) % NA, (j + 1) * NA + i) for j in range(NR) for i in range(NA)]
lungi = mesh_object('Lungi', rings, faces, uvs, cloth_material('Lungi', lungi_img))
uvl = lungi.data.uv_layers.active                                         # wrap faces: continue the texture past u=3
for poly in lungi.data.polygons:
    ids = [vi % NA for vi in poly.vertices]
    if 0 in ids and NA - 1 in ids:
        for li, vi in zip(poly.loop_indices, poly.vertices):
            if vi % NA == 0: uvl.data[li].uv = (3.0, uvl.data[li].uv[1])
pin = lungi.vertex_groups.new(name='pin'); pin.add(list(range(2 * NA)), 1.0, 'REPLACE')

def roll(name, ring_pts, radius, mat, uv_scale=6):
    """A rolled fabric tube following a closed ring of points (waist knot roll, folded hem)."""
    n = len(ring_pts); m = 10; verts = []; uv = []
    ring_pts = [Vector(p) for p in ring_pts]
    c = sum(ring_pts, Vector()) / n
    for i, p in enumerate(ring_pts):
        out = (p - c); out.z = 0; out.normalize()
        for k in range(m):
            a = 2 * math.pi * k / m
            verts.append(p + out * radius * (1 + math.cos(a)) + Vector((0, 0, radius * math.sin(a))))
            uv.append((i / n * uv_scale, k / m * .2))
    f = [(i * m + k, i * m + (k + 1) % m, ((i + 1) % n) * m + (k + 1) % m, ((i + 1) % n) * m + k) for i in range(n) for k in range(m)]
    return mesh_object(name, verts, f, uv, mat)

top_ring = [rings[i] for i in range(NA)]
waist = roll('Lungi_waist', top_ring, .011, lungi.data.materials[0])
# the tuck knot at the front of the waist
knot_c = Vector(top_ring[NA * 3 // 4]) + Vector((0, -.012, -.01))
bpy.ops.mesh.primitive_uv_sphere_add(segments=16, ring_count=10, radius=.02, location=knot_c)
knot = bpy.context.active_object; knot.name = 'Lungi_knot'; knot.scale = (1.6, .5, .7)
knot.data.materials.append(lungi.data.materials[0])
for o in (lungi, waist, knot): skin_to_body(o)
lungi.vertex_groups.remove(lungi.vertex_groups['pin'])                  # weight normalising touched it; re-add
lungi.vertex_groups.new(name='pin').add(list(range(2 * NA)), 1.0, 'REPLACE')
# the folded hem is added after the simulation, along the settled bottom edge

# ---------- vest: offset copy of the torso surface, scooped neck and arm holes ----------
bpy.ops.object.select_all(action='DESELECT')
dg = bpy.context.evaluated_depsgraph_get()
vest_me = bpy.data.meshes.new_from_object(body.evaluated_get(dg), preserve_all_data_layers=True, depsgraph=dg)
vest = bpy.data.objects.new('Vest', vest_me); bpy.context.collection.objects.link(vest)
for g in body.vertex_groups: vest.vertex_groups.new(name=g.name)
vest.modifiers.new('rig', 'ARMATURE').object = rig
vest.parent = rig
z_chest = z_neck - .15
dx = np.abs(V[:, 0] - cx)
keep = (V[:, 2] > z_top - .03) & (V[:, 2] < z_chest) & (w_arm < .12) & (w_neck < .35)   # straps are added below
front_scoop = (V[:, 1] < cy) & (dx < .05) & (V[:, 2] > z_chest - .05)
back_scoop = (V[:, 1] >= cy) & (dx < .05) & (V[:, 2] > z_chest - .01)
keep &= ~front_scoop & ~back_scoop & is_body
bm = bmesh.new(); bm.from_mesh(vest.data)
bm.verts.ensure_lookup_table()
bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(keep[v.index] for v in f.verts)], context='FACES')
bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
bm.normal_update()
for v in bm.verts: v.co += v.normal * .007
edge = [v for v in bm.verts if v.is_boundary]                              # soften the cut edges
for _ in range(6): bmesh.ops.smooth_vert(bm, verts=edge, factor=.5, use_axis_x=True, use_axis_y=True, use_axis_z=True)
bm.to_mesh(vest.data); bm.free()
vest.data.materials.clear(); vest.data.materials.append(cloth_material('Vest', vest_img, .9, .6))
# planar UVs for the cotton weave
uvl = vest.data.uv_layers.active or vest.data.uv_layers.new()
for poly in vest.data.polygons:
    for li, vi in zip(poly.loop_indices, poly.vertices):
        co = vest.data.vertices[vi].co; uvl.data[li].uv = (co.x * 4 + co.y * 2, co.z * 4)
sol = vest.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = .003
bpy.context.view_layer.objects.active = vest; bpy.ops.object.modifier_apply(modifier='thick')
vest.modifiers.move(len(vest.modifiers) - 1, 0) if len(vest.modifiers) > 1 else None

# ---------- gamcha: a checked cotton towel over the left shoulder ----------
clav = bone('clavicle_l', 'clavicle.l', 'shoulder')
side = 1 if tail_w(clav).x > cx else -1
def shoulder_top(frac):
    """Top of the shoulder at a fraction of the way from the neck to the shoulder joint, on either side."""
    xt = cx + (tail_w(clav).x - cx) * frac
    m = (np.abs(V[:, 0] - xt) < .02) & (V[:, 2] < z_neck + .06) & (V[:, 2] > z_neck - .12) & (w_neck < .5) & (w_arm < .3)
    y_mid = float(np.nanmedian(V[m][:, 1]))
    m &= np.abs(V[:, 1] - y_mid) < .03                                    # the top of the shoulder, not the collarbone
    return V[m][np.argmax(V[m][:, 2])]
def surface(x, z, front, off=.016):
    m = (np.abs(V[:, 0] - x) < .03) & (np.abs(V[:, 2] - z) < .03) & (w_arm < .2)
    ys = V[m][:, 1]
    return Vector((x, (ys.min() - off) if front else (ys.max() + off), z))
def catmull(pts, n):
    out = []
    P = [pts[0]] + pts + [pts[-1]]
    for i in range(1, len(P) - 2):
        for k in range(n):
            t = k / n; p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
            out.append(.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(pts[-1]); return out
def strip(name, path, width, top_z, mat, ripple=.004, uv_len=5, across=3, steps=10, solid=True):
    """A cloth strip of the given width following a path over the shoulder.
    solid=False leaves a single layer for cloth simulation (thickness is added afterwards)."""
    spine = catmull(path, steps); verts, uv = [], []
    for i, p in enumerate(spine):
        tng = (spine[min(i + 1, len(spine) - 1)] - spine[max(i - 1, 0)]).normalized()
        outward = Vector((p.x - cx, p.y - cy, 0)); outward = outward.normalized() if outward.length > 1e-4 else Vector((0, 0, 1))
        if abs(p.z - top_z) < .05: outward = Vector((0, 0, 1))
        wdir = tng.cross(outward).normalized()
        for k in range(across):
            s = 2 * k / (across - 1) - 1
            verts.append(p + wdir * (width / 2) * s + outward * ripple * math.sin(i * .9) * (k not in (0, across - 1)))
            uv.append((i / len(spine) * uv_len, k / (across - 1)))
    f = [(i * across + k, i * across + k + 1, (i + 1) * across + k + 1, (i + 1) * across + k)
         for i in range(len(spine) - 1) for k in range(across - 1)]
    ob = mesh_object(name, verts, f, uv, mat)
    if solid:
        sol = ob.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = .003
        bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier='thick')
    skin_to_body(ob)
    return ob

# gamcha over the left shoulder, hanging to the waist in front and behind
top = shoulder_top(.62); xs = top[0]
print('GAMCHA_TOP', top, flush=True)
gamcha = strip('Gamcha', [surface(xs - side * .05, top[2] - .42, True, .032), surface(xs - side * .02, top[2] - .22, True, .03),
                          surface(xs, top[2] - .06, True, .024), Vector((xs, top[1], top[2] + .022)),
                          surface(xs, top[2] - .06, False, .024), surface(xs - side * .03, top[2] - .25, False, .03),
                          surface(xs - side * .06, top[2] - .45, False, .032)], .14, top[2], cloth_material('Gamcha', gamcha_img, .9, .5),
                ripple=.004, across=9, steps=14, solid=True)    # shaped, not simulated: a thick towel keeps its drape

# vest straps on both shoulders, from the front of the vest to the back
for s_name, frac in (('Vest_strap_l', .5), ('Vest_strap_r', -.5)):
    xt = cx + (tail_w(clav).x - cx) * frac
    m = (np.abs(V[:, 0] - xt) < .02) & (V[:, 2] < z_neck + .06) & (V[:, 2] > z_neck - .12) & (w_neck < .6) & (w_arm < .3)
    y_mid = float(np.nanmedian(V[m][:, 1])); m &= np.abs(V[:, 1] - y_mid) < .03
    st = V[m][np.argmax(V[m][:, 2])]
    strip(s_name, [surface(st[0], z_chest - .03, True, .009), surface(st[0], top[2] - .06, True, .009),
                   Vector((st[0], st[1], st[2] + .01)), surface(st[0], top[2] - .06, False, .009),
                   surface(st[0], z_chest - .03, False, .009)], .035, st[2], vest.data.materials[0], ripple=0, uv_len=2)

# ---------- skin tone: warm brown per the character sheet (#9C6440), with soft subsurface for renders ----------
for mat in body.data.materials:
    if not mat.use_nodes: continue
    nt = mat.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf or not bsdf.inputs['Base Color'].is_linked: continue
    src = bsdf.inputs['Base Color'].links[0].from_socket
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
    mix.inputs['Factor'].default_value = 1.0; mix.inputs[7].default_value = (.50, .33, .22, 1)
    nt.links.new(src, mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])
    bsdf.inputs['Roughness'].default_value = .55
    if 'Subsurface Weight' in bsdf.inputs:
        bsdf.inputs['Subsurface Weight'].default_value = .12
        bsdf.inputs['Subsurface Radius'].default_value = (1.0, .35, .15)
        bsdf.inputs['Subsurface Scale'].default_value = .012

# black hair, as in the character sheet
hair = next((o for o in bpy.data.objects if 'short02' in o.name), None)
for mat in (hair.data.materials if hair else []):
    if not (mat and mat.use_nodes): continue
    nt = mat.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if bsdf and bsdf.inputs['Base Color'].is_linked:
        src = bsdf.inputs['Base Color'].links[0].from_socket
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1.0; mix.inputs[7].default_value = (.16, .13, .12, 1)
        nt.links.new(src, mix.inputs[6]); nt.links.new(mix.outputs[2], bsdf.inputs['Base Color'])

# ---------- pose: relaxed standing, arms down, slight elbow bend ----------
bpy.context.view_layer.objects.active = rig; bpy.ops.object.mode_set(mode='POSE')
def swing(name_keys, target_dir, amount):
    pb = rig.pose.bones[bone(*name_keys).name]
    bpy.context.view_layer.update()
    head = pb.head.copy(); cur = (pb.tail - pb.head).normalized()
    want = cur.lerp(Vector(target_dir).normalized(), amount).normalized()
    q = cur.rotation_difference(want)
    pb.matrix = Matrix.Translation(head) @ q.to_matrix().to_4x4() @ Matrix.Translation(-head) @ pb.matrix
    bpy.context.view_layer.update()
for s in ('l', 'r'):
    sx = 1 if s == 'l' else -1
    try:
        swing((f'upperarm_{s}', f'upperarm.{s}'), (sx * .02, .05, -1), 1.0)
        swing((f'lowerarm_{s}', f'lowerarm.{s}'), (sx * .05, -.35, -1), .25)
    except KeyError as e:
        print('POSE_SKIP', e, flush=True)
try:
    pb = rig.pose.bones[bone('head').name]; pb.rotation_mode = 'XYZ'; pb.rotation_euler.rotate_axis('Z', math.radians(-6))
except KeyError: pass
bpy.ops.object.mode_set(mode='OBJECT')

# ---------- cloth simulation: lungi and gamcha settle on the posed body (Blender's built-in solver) ----------
scene = bpy.context.scene
for o, th in ((body, .006), (vest, .003)):
    col = o.modifiers.new('collision', 'COLLISION')
    o.collision.thickness_outer = th; o.collision.cloth_friction = 8
def simulate(obj, frames, mass, bend, shrink=0.):
    mod = obj.modifiers.new('cloth', 'CLOTH'); s = mod.settings
    s.quality = 8; s.mass = mass; s.air_damping = 2
    s.tension_stiffness = s.compression_stiffness = 18; s.shear_stiffness = 6; s.bending_stiffness = bend
    s.vertex_group_mass = 'pin'; s.pin_stiffness = 1; s.shrink_min = shrink
    cs = mod.collision_settings; cs.distance_min = .004; cs.collision_quality = 4; cs.use_self_collision = False
    mod.point_cache.frame_start = 1; mod.point_cache.frame_end = frames
    scene.frame_start, scene.frame_end = 1, frames
    for f in range(1, frames + 1): scene.frame_set(f)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier='cloth')
    scene.frame_set(1)
    print('SIMULATED', obj.name, frames, 'frames', flush=True)
simulate(lungi, 50, .25, .6)
for o in (body, vest): o.modifiers.remove(o.modifiers['collision'])

# folded hem along the settled bottom edge, then cloth thickness
lw = lungi.matrix_world
hem_ring = [lw @ lungi.data.vertices[NR * NA + i].co for i in range(NA)]
hem = roll('Lungi_hem', hem_ring, .008, lungi.data.materials[0]); skin_to_body(hem)
for o, th in ((lungi, .003),):
    sol = o.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = th; sol.offset = 1
    sub = o.modifiers.new('smooth', 'SUBSURF'); sub.levels = 0; sub.render_levels = 1

# ---------- hair cards: short strands grown from the scalp, combed forward and down ----------
rng_h = np.random.default_rng(11)
def strand_texture(n=512, count=260):
    img = np.zeros((n, n, 4))
    for _ in range(count):
        x = rng_h.uniform(0, n); w = rng_h.uniform(.6, 1.8); a = rng_h.uniform(.55, 1)
        tone = np.array([.045, .035, .03]) * rng_h.uniform(.7, 1.5) + rng_h.uniform(0, .02)
        xs_ = np.arange(n)
        prof = np.clip(1 - np.abs(xs_ - x) / w, 0, 1) * a
        v_ = np.linspace(0, 1, n)
        taper = np.clip(1 - v_ ** 3 * rng_h.uniform(.8, 1.2), 0, 1) * np.clip(v_ / .12, 0, 1)   # soft root, thin tips
        alpha = taper[:, None] * prof[None, :]
        img[..., :3] = img[..., :3] * (1 - alpha[..., None]) + tone * alpha[..., None]
        img[..., 3] = np.maximum(img[..., 3], alpha)
    im = bpy.data.images.new('hair_strands', n, n, alpha=True)
    im.pixels.foreach_set(img.astype(np.float32).ravel()); im.pack()
    return im
hair_img = strand_texture()
hm = bpy.data.materials.new('HairCards'); hm.use_nodes = True
nt = hm.node_tree; hb = nt.nodes['Principled BSDF']
ht = nt.nodes.new('ShaderNodeTexImage'); ht.image = hair_img
nt.links.new(ht.outputs['Color'], hb.inputs['Base Color']); nt.links.new(ht.outputs['Alpha'], hb.inputs['Alpha'])
hb.inputs['Roughness'].default_value = .45
if 'Coat Weight' in hb.inputs: hb.inputs['Coat Weight'].default_value = .2
try: hm.surface_render_method = 'DITHERED'
except AttributeError: hm.blend_method = 'HASHED'
# Roots sit on the MakeHuman hair cap (read in the rest pose, since the cards are skinned to the head bone).
rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
dg = bpy.context.evaluated_depsgraph_get(); cap_e = hair.evaluated_get(dg); cap_m = cap_e.to_mesh()
CP = np.array([cap_e.matrix_world @ v.co for v in cap_m.vertices])
CN = np.array([(cap_e.matrix_world.to_3x3() @ v.normal).normalized() for v in cap_m.vertices])
cap_e.to_mesh_clear(); rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
eyes = next(o for o in bpy.data.objects if 'low-poly' in o.name)
eye_top = max((eyes.matrix_world @ v.co).z for v in eyes.data.vertices)
head_c = Vector(CP.mean(axis=0))
outer = CN[:, 2] > -.35                                                                   # skip the cap's inner/underside
outer &= ~((CP[:, 1] < head_c.y - .02) & (CP[:, 2] < eye_top + .045))                     # keep the forehead and eyes clear
CP, CN = CP[outer], CN[outer]
crown = Vector(CP[np.argmax(CP[:, 2] + .6 * CP[:, 1])])                                  # top-back whorl
verts, faces_h, uv_h = [], [], []
for c in range(1600):
    vi = rng_h.integers(len(CP))
    p = Vector(CP[vi]); n = Vector(CN[vi])
    d = p - crown; d -= n * d.dot(n)
    d = d.normalized() if d.length > 1e-4 else n.orthogonal().normalized()
    front = p.y < head_c.y - .03
    if front: d = (d + Vector((math.copysign(.6, p.x - head_c.x), 0, .15))).normalized()   # fringe swept to the side
    else: d = (d + Vector((0, 0, -.35))).normalized()                                    # hair falls a little
    L = rng_h.uniform(.02, .032) if front else rng_h.uniform(.02, .038)
    side = d.cross(n).normalized(); W = .009
    u0 = rng_h.uniform(0, .8); base = len(verts)
    for k in range(4):
        t = k / 3
        q = p + n * (-.001 + .004 * t) + d * L * t + Vector((0, 0, -.006 * t * t))
        verts += [q - side * W / 2, q + side * W / 2]
        uv_h += [(u0, t), (u0 + .2, t)]
    for k in range(3):
        faces_h.append((base + 2 * k, base + 2 * k + 1, base + 2 * k + 3, base + 2 * k + 2))
hairc = mesh_object('HairCards', verts, faces_h, uv_h, hm)
hairc.vertex_groups.new(name='head').add(list(range(len(verts))), 1.0, 'REPLACE')
hairc.modifiers.new('rig', 'ARMATURE').object = rig; hairc.parent = rig
print('HAIR_CARDS', len(faces_h), flush=True)

# ---------- skin micro-detail: tiling pore normal map (also exported to the GLB) ----------
def pore_normal(n=512, seed=5):
    r = np.random.default_rng(seed)
    f = np.fft.fft2(r.normal(size=(n, n)))
    k = np.fft.fftfreq(n)[:, None] ** 2 + np.fft.fftfreq(n)[None, :] ** 2
    h = np.real(np.fft.ifft2(f * np.exp(-k * 2200) * (k > 1e-6)))                       # small soft bumps (tileable)
    h = (h - h.mean()) / h.std()
    dx = (np.roll(h, -1, 1) - np.roll(h, 1, 1)) * .5; dy = (np.roll(h, -1, 0) - np.roll(h, 1, 0)) * .5
    nrm = np.dstack([-dx * .35, -dy * .35, np.ones_like(h)]); nrm /= np.linalg.norm(nrm, axis=2, keepdims=True)
    return (nrm * .5 + .5)
pore_img = make_image('skin_pores', pore_normal()); pore_img.colorspace_settings.name = 'Non-Color'
for mat in body.data.materials:
    if not mat.use_nodes: continue
    nt = mat.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf or bsdf.inputs['Normal'].is_linked: continue
    tex = nt.nodes.new('ShaderNodeTexImage'); tex.image = pore_img
    mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (55, 55, 1)
    uvn = nt.nodes.new('ShaderNodeUVMap')
    nm = nt.nodes.new('ShaderNodeNormalMap'); nm.inputs['Strength'].default_value = .35
    nt.links.new(uvn.outputs['UV'], mp.inputs['Vector']); nt.links.new(mp.outputs['Vector'], tex.inputs['Vector'])
    nt.links.new(tex.outputs['Color'], nm.inputs['Color']); nt.links.new(nm.outputs['Normal'], bsdf.inputs['Normal'])
    if 'Subsurface Weight' in bsdf.inputs: bsdf.inputs['Subsurface Weight'].default_value = .2
    if 'Specular IOR Level' in bsdf.inputs: bsdf.inputs['Specular IOR Level'].default_value = .45

# ---------- skin colour detail: generated per vertex, so it needs no photo of a real person ----------
# Darker skin around the eyes and on the lips (common in South Asian faces), a warmer nose and cheeks,
# darker knees/elbows/knuckles, a faint upper-lip shadow, lighter nails, and low-frequency tone variation.
eyes_ob = next(o for o in bpy.data.objects if 'low-poly' in o.name)
EP = np.array([eyes_ob.matrix_world @ v.co for v in eyes_ob.data.vertices])
eye_l = EP[EP[:, 0] > np.mean(EP[:, 0])].mean(axis=0); eye_r = EP[EP[:, 0] <= np.mean(EP[:, 0])].mean(axis=0)
w_lips = weights('lips'); w_nails = weights('fingernails', 'toenails'); w_scalp2 = weights('scalp')
def near(points, radius):
    d = np.min([np.linalg.norm(V - p, axis=1) for p in points], axis=0)
    return np.clip(1 - np.nan_to_num(d, nan=9) / radius, 0, 1)
joints = [head_w(bone(k)) for k in ('calf_l', 'calf_r', 'lowerarm_l', 'lowerarm_r')]
mouth_c = V[w_lips > .5].mean(axis=0) if (w_lips > .5).any() else eye_l
nose_tip = V[np.nanargmin(np.where(np.abs(V[:, 0] - cx) < .02, V[:, 1], 9))]
def vnoise(P, freq, seed):
    r = np.random.default_rng(seed); out = np.zeros(len(P))
    for k in range(4):
        d = r.normal(size=3); d /= np.linalg.norm(d)
        out += np.sin(np.nan_to_num(P) @ d * freq * (1.7 ** k) + r.uniform(0, 6.3)) / (1.6 ** k)
    return out / 2
tint = np.ones((len(V), 3))
def apply(mask, rgb):
    global tint
    tint = tint * (1 - mask[:, None]) + tint * np.array(rgb) * mask[:, None]
apply(near([eye_l, eye_r], .038) * .95, (.74, .66, .64))                                    # periorbital darkening
apply(np.clip(w_lips, 0, 1), (.70, .54, .52))                                               # lips
upper_lip = near([mouth_c + np.array([0, -.004, .018])], .022) * (1 - np.clip(w_lips, 0, 1))
apply(upper_lip * .7, (.88, .84, .82))                                                      # faint upper-lip shadow
apply(near([nose_tip], .03) * .6, (1.05, .93, .88))                                         # warmer nose
apply(near([eye_l + np.array([0, -.02, -.035]), eye_r + np.array([0, -.02, -.035])], .035) * .5, (1.04, .94, .9))
apply(near([np.array(j) for j in joints], .05) * .7, (.84, .78, .75))                       # knees and elbows
apply(np.clip(w_nails, 0, 1), (1.25, 1.15, 1.08))                                           # nails
apply(np.clip(w_scalp2, 0, 1) * .8, (.45, .42, .4))                                         # scalp under the hair
tone = vnoise(V, 9, 21) * .035 + vnoise(V, 40, 22) * .015
tint *= (1 + tone)[:, None]
tint = np.clip(np.nan_to_num(tint, nan=1), 0, 1.4)
attr = body.data.color_attributes.new('skin_detail', 'FLOAT_COLOR', 'POINT')
attr.data.foreach_set('color', np.hstack([np.clip(tint, 0, 1), np.ones((len(V), 1))]).astype(np.float32).ravel())
rough = .58 - .12 * near([nose_tip, eye_l + np.array([.0, -.01, .05]), eye_r + np.array([.0, -.01, .05])], .045)
rattr = body.data.color_attributes.new('skin_rough', 'FLOAT_COLOR', 'POINT')
rattr.data.foreach_set('color', np.repeat(rough[:, None], 4, axis=1).astype(np.float32).ravel())
body.data.color_attributes.active_color = attr
for mat in body.data.materials:
    if not (mat and mat.use_nodes): continue
    nt = mat.node_tree; bsdf = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not bsdf or not bsdf.inputs['Base Color'].is_linked: continue
    ca = nt.nodes.new('ShaderNodeVertexColor'); ca.layer_name = 'skin_detail'
    mul = nt.nodes.new('ShaderNodeMix'); mul.data_type = 'RGBA'; mul.blend_type = 'MULTIPLY'; mul.inputs['Factor'].default_value = 1
    nt.links.new(bsdf.inputs['Base Color'].links[0].from_socket, mul.inputs[6]); nt.links.new(ca.outputs['Color'], mul.inputs[7])
    nt.links.new(mul.outputs[2], bsdf.inputs['Base Color'])
    cr = nt.nodes.new('ShaderNodeVertexColor'); cr.layer_name = 'skin_rough'
    sep = nt.nodes.new('ShaderNodeSeparateColor'); nt.links.new(cr.outputs['Color'], sep.inputs['Color'])
    nt.links.new(sep.outputs[0], bsdf.inputs['Roughness'])
print('SKIN_DETAIL', 'eyes', eye_l.round(3), eye_r.round(3), flush=True)

# brows darker and fuller-looking, eyes wet
for o in bpy.data.objects:
    if o.type != 'MESH': continue
    for mat in o.data.materials:
        if not (mat and mat.use_nodes): continue
        b = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not b: continue
        if 'eyebrow' in o.name and b.inputs['Base Color'].is_linked:
            nt = mat.node_tree; m = nt.nodes.new('ShaderNodeMix'); m.data_type = 'RGBA'; m.blend_type = 'MULTIPLY'
            m.inputs['Factor'].default_value = 1; m.inputs[7].default_value = (.25, .22, .2, 1)
            nt.links.new(b.inputs['Base Color'].links[0].from_socket, m.inputs[6]); nt.links.new(m.outputs[2], b.inputs['Base Color'])
        if 'low-poly' in o.name:
            b.inputs['Roughness'].default_value = .08
            if 'Coat Weight' in b.inputs: b.inputs['Coat Weight'].default_value = 1; b.inputs['Coat Roughness'].default_value = .02

# ---------- stage: packed earth ground, evening sky, warm low sun ----------
scene = bpy.context.scene
world = bpy.data.worlds.new('Evening'); scene.world = world; world.use_nodes = True
wn = world.node_tree.nodes; env = wn.new('ShaderNodeTexEnvironment')
env.image = bpy.data.images.load(str(VENDOR / 'hdri' / 'evening_field_2k.hdr'))
mapping = wn.new('ShaderNodeMapping'); coord = wn.new('ShaderNodeTexCoord')
mapping.inputs['Rotation'].default_value = (0, 0, math.radians(140))
world.node_tree.links.new(coord.outputs['Generated'], mapping.inputs['Vector'])
world.node_tree.links.new(mapping.outputs['Vector'], env.inputs['Vector'])
world.node_tree.links.new(env.outputs['Color'], wn['Background'].inputs['Color'])
wn['Background'].inputs['Strength'].default_value = .55

bpy.ops.mesh.primitive_plane_add(size=30, location=(0, 0, z_floor))
ground = bpy.context.active_object; ground.name = 'Ground'
gm = bpy.data.materials.new('Earth'); gm.use_nodes = True
earth = PROJECT / 'unity/SatChara/Assets/SatChara/Art/Textures/village-earth.png'
if earth.exists():
    gt = gm.node_tree.nodes.new('ShaderNodeTexImage'); gt.image = bpy.data.images.load(str(earth))
    gmap = gm.node_tree.nodes.new('ShaderNodeMapping'); gmap.inputs['Scale'].default_value = (12, 12, 1)
    gco = gm.node_tree.nodes.new('ShaderNodeTexCoord')
    gm.node_tree.links.new(gco.outputs['UV'], gmap.inputs['Vector']); gm.node_tree.links.new(gmap.outputs['Vector'], gt.inputs['Vector'])
    gm.node_tree.links.new(gt.outputs['Color'], gm.node_tree.nodes['Principled BSDF'].inputs['Base Color'])
    bump = gm.node_tree.nodes.new('ShaderNodeBump'); bump.inputs['Strength'].default_value = .4
    gm.node_tree.links.new(gt.outputs['Color'], bump.inputs['Height'])
    gm.node_tree.links.new(bump.outputs['Normal'], gm.node_tree.nodes['Principled BSDF'].inputs['Normal'])
gm.node_tree.nodes['Principled BSDF'].inputs['Roughness'].default_value = .95
ground.data.materials.append(gm)

sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 6.5; sun.color = (1.0, .76, .52); sun.angle = math.radians(1.5)
sun_ob = bpy.data.objects.new('Sun', sun); scene.collection.objects.link(sun_ob)
sun_ob.rotation_euler = (math.radians(72), 0, math.radians(-38))

scene.render.engine = 'CYCLES'; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True
scene.cycles.device = 'CPU'
try: scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
except TypeError:
    try: scene.view_settings.look = 'Medium High Contrast'
    except TypeError: pass
scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 90

zmin, zmax = z_floor, z_head_top
def shoot(name, cam_pos, look_at, lens, res):
    cam = bpy.data.cameras.new(name); cam.lens = lens
    ob = bpy.data.objects.new(name, cam); scene.collection.objects.link(ob)
    ob.location = cam_pos
    ob.rotation_euler = (Vector(look_at) - Vector(cam_pos)).to_track_quat('-Z', 'Y').to_euler()
    scene.camera = ob; scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.filepath = str(OUT_IMG / f'bablu-{name}.jpg')
    bpy.ops.render.render(write_still=True); print('RENDERED', name, flush=True)

bpy.ops.wm.save_as_mainfile(filepath=str(VENDOR / 'bablu-mockup.blend'))
if '--no-render' not in ARGS:
    mid = (cx, cy, zmin + height * .52)
    shoot('three-quarter', (cx + 1.7, cy - 3.0, zmin + height * .6), mid, 55, (1080, 1440))
    shoot('front', (cx, cy - 3.4, zmin + height * .55), mid, 55, (1080, 1440))
    face = (cx, cy - .02, zmax - height * .075)
    shoot('face', (cx + .25, cy - .85, face[2] + .02), face, 85, (1080, 1080))

# ---------- web viewer copy: smaller textures, GLB ----------
for img in bpy.data.images:
    if img.size[0] > 1024 and img.source in ('FILE', 'GENERATED'):
        img.scale(1024, int(1024 * img.size[1] / img.size[0]))
for o in (ground,): o.hide_set(True)
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.data.objects:
    if o.type in ('MESH', 'ARMATURE') and o is not ground: o.select_set(True)
bpy.ops.export_scene.gltf(filepath=str(VENDOR / 'bablu-mockup.glb'), export_format='GLB', use_selection=True,
                          export_apply=True, export_animations=False, export_image_format='AUTO')  # PNG keeps lash/brow transparency
summary = {o.name: len(o.data.vertices) for o in bpy.data.objects if o.type == 'MESH'}
print('DONE', json.dumps(summary), flush=True)
