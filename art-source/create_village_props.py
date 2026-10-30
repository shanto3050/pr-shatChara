"""Village props for the Sat Chara courtyard, built from free/CC0 sources only.

Props: haystack (khorer gada) on a bamboo pole, tube well (chapkol) on a concrete pad, mud house with a raised
plinth, verandah and corrugated tin roof, dung cakes (ghute) drying on the wall, split-bamboo fence, banana
plant, coconut palm, clay water pots (kolshi) and jute sacks.
Textures: ambientCG / Poly Haven CC0 sets in vendor/textures (see village-textures.json); leaf, trunk and paint
textures are generated here. Sizes are real-world metres; UVs are in metres so textures tile at true scale.

Run headless:  blender -b --factory-startup -P create_village_props.py -- [--samples N] [--no-render]
Outputs: Unity FBX + textures in unity/SatChara/Assets/SatChara/Art/Environment/Village/,
renders in docs/environment/, vendor/village-props.blend, village-props-summary.json.
"""
import bpy, bmesh, math, json, pathlib, shutil, sys
import numpy as np
from mathutils import Vector, Matrix, noise

ROOT = pathlib.Path(__file__).resolve().parent
PROJECT = ROOT.parent
TEX = ROOT / 'vendor' / 'textures'
ARGS = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []
SAMPLES = int(ARGS[ARGS.index('--samples') + 1]) if '--samples' in ARGS else 96
UNITY = PROJECT / 'unity/SatChara/Assets/SatChara/Art/Environment/Village'
RENDERS = PROJECT / 'docs' / 'environment'
for d in (UNITY / 'Textures', RENDERS): d.mkdir(parents=True, exist_ok=True)
rng = np.random.default_rng(2026)

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
props = {}                                                     # prop name -> list of objects

# ---------------------------------------------------------------- helpers
def link(ob, prop):
    bpy.context.collection.objects.link(ob); props.setdefault(prop, []).append(ob); return ob

def mesh(name, verts, faces, prop, mat=None, uvs=None, smooth=True):
    me = bpy.data.meshes.new(name); me.from_pydata([tuple(v) for v in verts], [], faces); me.update()
    if uvs is not None:
        layer = me.uv_layers.new(name='UVMap')
        for poly in me.polygons:
            for li, vi in zip(poly.loop_indices, poly.vertices): layer.data[li].uv = uvs[vi]
    for p in me.polygons: p.use_smooth = smooth
    ob = bpy.data.objects.new(name, me)
    if mat: me.materials.append(mat)
    return link(ob, prop)

def uv_box(ob, size=1.0):
    """Box projection in metres: one texture repeat per `size` metres, seen from the face's dominant axis."""
    me = ob.data
    if not me.uv_layers: me.uv_layers.new(name='UVMap')
    layer = me.uv_layers.active; mw = ob.matrix_world
    for poly in me.polygons:
        n = (mw.to_3x3() @ poly.normal); ax = max(range(3), key=lambda i: abs(n[i]))
        for li, vi in zip(poly.loop_indices, poly.vertices):
            co = mw @ me.vertices[vi].co
            u, v = [(co.y, co.z), (co.x, co.z), (co.x, co.y)][ax]
            layer.data[li].uv = (u / size, v / size)

def box(name, size, loc, prop, mat, bevel=0.0, tile=1.0, rot=(0, 0, 0)):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc, rotation=rot)
    ob = bpy.context.active_object; ob.name = name; ob.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel:
        m = ob.modifiers.new('bevel', 'BEVEL'); m.width = bevel; m.segments = 2
        bpy.ops.object.modifier_apply(modifier='bevel')
    uv_box(ob, tile); ob.data.materials.append(mat)
    for c in ob.users_collection: c.objects.unlink(ob)
    return link(ob, prop)

def revolve(name, profile, prop, mat, seg=32, loc=(0, 0, 0), u_tiles=1.0, wobble=0.0, seed=0, v_scale=1.0):
    """Lathe a (radius, height) profile around Z. UV u goes around, v up the profile (metres * v_scale)."""
    verts, uvs, faces = [], [], []
    lengths = [0.0]
    for (r0, z0), (r1, z1) in zip(profile, profile[1:]): lengths.append(lengths[-1] + math.hypot(r1 - r0, z1 - z0))
    for j, (r, z) in enumerate(profile):
        for i in range(seg + 1):
            a = 2 * math.pi * i / seg
            w = 1 + wobble * noise.noise(Vector((math.cos(a) * 2 + seed, math.sin(a) * 2, z * 3)))
            verts.append((loc[0] + r * w * math.cos(a), loc[1] + r * w * math.sin(a), loc[2] + z))
            uvs.append((i / seg * u_tiles, lengths[j] * v_scale))
    for j in range(len(profile) - 1):
        for i in range(seg):
            a = j * (seg + 1) + i; b = a + seg + 1
            faces.append((a, a + 1, b + 1, b))
    ob = mesh(name, verts, faces, prop, mat, uvs)
    bpy.ops.object.select_all(action='DESELECT'); ob.select_set(True); bpy.context.view_layer.objects.active = ob
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.remove_doubles(threshold=1e-5); bpy.ops.object.mode_set(mode='OBJECT')
    return ob

def tube(name, path, radius, prop, mat, seg=8, u_tiles=1.0, taper=None):
    """A tube along a list of points (bamboo poles, pump handle, palm trunk, banana stem, frond spines)."""
    verts, uvs, faces = [], [], []
    path = [Vector(p) for p in path]; dist = 0.0
    for j, p in enumerate(path):
        t = (path[min(j + 1, len(path) - 1)] - path[max(j - 1, 0)]).normalized()
        side = t.cross(Vector((0, 0, 1))) if abs(t.z) < .95 else t.cross(Vector((1, 0, 0)))
        side.normalize(); up = side.cross(t)
        if j: dist += (path[j] - path[j - 1]).length
        r = radius * (taper(j / (len(path) - 1)) if taper else 1)
        for i in range(seg + 1):
            a = 2 * math.pi * i / seg
            verts.append(p + (side * math.cos(a) + up * math.sin(a)) * r)
            uvs.append((i / seg * u_tiles, dist))
    for j in range(len(path) - 1):
        for i in range(seg):
            a = j * (seg + 1) + i; b = a + seg + 1
            faces.append((a, a + 1, b + 1, b))
    return mesh(name, verts, faces, prop, mat, uvs)

def image_from_array(name, arr, alpha=False):
    h, w = arr.shape[:2]
    if arr.shape[2] == 3 and alpha: arr = np.dstack([arr, np.ones((h, w))])
    if arr.shape[2] == 3: arr = np.dstack([arr, np.ones((h, w))])
    img = bpy.data.images.new(name, w, h, alpha=alpha)
    img.pixels.foreach_set(np.clip(arr, 0, 1).astype(np.float32).ravel()); img.pack()
    return img

def pbr(name, color, normal=None, rough=None, tint=None, rough_value=None, metallic=0.0, alpha=None, sat=None):
    """Principled material from image files (or generated images). tint multiplies the colour; sat scales saturation."""
    m = bpy.data.materials.new(name); m.use_nodes = True; nt = m.node_tree; b = nt.nodes['Principled BSDF']
    def tex(src, non_color=False):
        n = nt.nodes.new('ShaderNodeTexImage')
        n.image = src if isinstance(src, bpy.types.Image) else bpy.data.images.load(str(src), check_existing=True)
        if non_color: n.image.colorspace_settings.name = 'Non-Color'
        return n
    c = tex(color); col = c.outputs['Color']
    if tint:
        mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'; mix.blend_type = 'MULTIPLY'
        mix.inputs['Factor'].default_value = 1; mix.inputs[7].default_value = (*tint, 1)
        nt.links.new(col, mix.inputs[6]); col = mix.outputs[2]
    if sat is not None:
        hsv = nt.nodes.new('ShaderNodeHueSaturation'); hsv.inputs['Saturation'].default_value = sat
        nt.links.new(col, hsv.inputs['Color']); col = hsv.outputs['Color']
    nt.links.new(col, b.inputs['Base Color'])
    if alpha is not None:
        nt.links.new(c.outputs['Alpha'], b.inputs['Alpha'])
        try: m.surface_render_method = 'DITHERED'
        except AttributeError: m.blend_method = 'HASHED'
    if normal:
        nn = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(tex(normal, True).outputs['Color'], nn.inputs['Color'])
        nt.links.new(nn.outputs['Normal'], b.inputs['Normal'])
    if rough: nt.links.new(tex(rough, True).outputs['Color'], b.inputs['Roughness'])
    elif rough_value is not None: b.inputs['Roughness'].default_value = rough_value
    b.inputs['Metallic'].default_value = metallic
    return m

def ph(set_, kind): return TEX / set_ / f'{set_}_{kind}_1k.jpg'
def acg(set_, kind): return TEX / set_ / f'{set_}_1K-JPG_{kind}.jpg'

# ---------------------------------------------------------------- generated textures
def blotch(n, scales=((8, .5), (24, .3), (64, .2))):
    """Tileable-ish value noise in [0, 1] from a few blocky octaves."""
    nz = np.zeros((n, n))
    for s, a in scales:
        g = rng.random((s, s)); k = -(-n // s); nz += a * np.kron(g, np.ones((k, k)))[:n, :n]
    return nz / sum(a for _, a in scales)

def leaf_texture(n=512, green=(.16, .34, .08)):
    """Banana / palm leaf: green blade, lighter midrib down the middle (v), parallel veins, brown dry edges."""
    u = np.linspace(-1, 1, n)[None, :]; v = np.linspace(0, 1, n)[:, None]
    base = np.array(green) * (1 + .12 * np.sin(v * 9 + u * 2))[..., None]
    veins = (np.abs(np.sin((v * 1.0 + np.abs(u) * .9) * 130)) > .92) * .06
    rib = np.exp(-(u / .035) ** 2)
    col = base + veins[..., None] * np.array([.25, .3, .1]) + rib[..., None] * np.array([.18, .22, .08])
    edge = np.clip((np.abs(u) - .8) / .2, 0, 1) * (rng.random((n, n)) > .3)
    col = col * (1 - edge[..., None] * .7) + edge[..., None] * np.array([.36, .28, .12]) * .7
    col *= (1 + rng.normal(0, .04, (n, n, 1)))
    return col

def trunk_texture(n=512):
    """Coconut trunk (1 m per tile): grey-brown bark, irregular leaf-scar rings every 6-10 cm, fine fibres."""
    v = np.linspace(0, 1, n, endpoint=False)[:, None]; u = np.linspace(0, 1, n, endpoint=False)[None, :]
    ring = np.zeros((n, n)); z = 0.0
    while z < 1:
        width = rng.uniform(.006, .012); wav = rng.uniform(.003, .01)
        ring = np.maximum(ring, np.exp(-((v - z - wav * np.sin(u * 6.283 + rng.uniform(0, 6))) / width) ** 2))
        z += rng.uniform(.06, .1)
    fib = blotch(n, ((4, .5), (128, .5)))                                     # vertical fibre streaks
    fib = np.repeat(fib[:1, :], n, axis=0) * .6 + fib * .4
    col = np.array([.42, .37, .31]) * (.85 + .3 * fib)[..., None] * (1 - .45 * ring[..., None])
    return col * (1 + rng.normal(0, .03, (n, n, 1)))

def stem_texture(n=512):
    """Banana pseudo-stem: green with long vertical streaks and brown patches of dried sheath."""
    u = np.linspace(0, 1, n)[None, :]
    streak = np.repeat(blotch(n, ((16, .4), (96, .6)))[:1, :], n, axis=0)
    dry = np.clip((blotch(n, ((6, .6), (20, .4))) - .58) * 3, 0, 1)
    col = np.array([.30, .40, .15]) * (.8 + .4 * streak)[..., None]
    col = col * (1 - dry[..., None]) + np.array([.38, .28, .16]) * dry[..., None]
    return col * (1 + rng.normal(0, .03, (n, n, 1)))

def planks_texture(n=512, boards=5):
    """Weathered vertical door planks: grey-brown wood, grain, a dark gap between boards, scuffs."""
    u = np.arange(n)[None, :] / n; v = np.arange(n)[:, None] / n
    b = np.floor(u * boards).astype(int)
    tone = rng.uniform(.8, 1.15, boards)[b]
    grain = .07 * np.sin((u * boards * 9 + 2.5 * np.sin(v * 7 + b) + v * 2) * 6.283)
    gap = (np.abs(u * boards - np.round(u * boards)) < .018) * .55
    wear = blotch(n) * .25
    col = np.array([.36, .29, .22]) * (tone + grain + wear)[..., None] * (1 - gap[..., None])
    grey = blotch(n, ((5, 1.0),))[..., None]                                   # sun-greyed patches
    return col * (1 - .35 * grey) + np.array([.42, .4, .37]) * .35 * grey

def paint_rust_texture(n=512):
    """Tube-well paint: dark green enamel with rust breaking through at the edges and joints."""
    nz = blotch(n)
    rust = np.clip((nz - .62) * 4, 0, 1)
    green = np.array([.05, .16, .1]); rustc = np.array([.32, .14, .06])
    col = green * (1 - rust[..., None]) + rustc * rust[..., None]
    return col * (1 + rng.normal(0, .03, (n, n, 1)))

def strand_texture(n=512, color=(.62, .5, .26), count=320, seed_tone=.25):
    """Alpha strands for straw and grass cards: thin lines, tapered tips, varied tone. RGBA."""
    img = np.zeros((n, n, 4))
    for _ in range(count):
        x = rng.uniform(0, n); w = rng.uniform(.6, 2.2); a = rng.uniform(.6, 1)
        tone = np.array(color) * rng.uniform(1 - seed_tone, 1 + seed_tone)
        lean = rng.uniform(-.25, .25) * np.linspace(0, 1, n) ** 2 * n * .1
        xs = np.arange(n)[None, :]; centre = x + lean[:, None]
        prof = np.clip(1 - np.abs(xs - centre) / w, 0, 1) * a
        length = rng.uniform(.55, 1.0); v = np.linspace(0, 1, n)[:, None]
        alpha = prof * np.clip((length - v) / .15, 0, 1)                     # strands end at different heights
        img[..., :3] = img[..., :3] * (1 - alpha[..., None]) + tone * alpha[..., None]
        img[..., 3] = np.maximum(img[..., 3], alpha)
    im = bpy.data.images.new(f'strands_{len(bpy.data.images)}', n, n, alpha=True)
    im.pixels.foreach_set(np.clip(img, 0, 1).astype(np.float32).ravel()); im.pack()
    return im

def plaid_texture(n=256, base=(.1, .2, .45), lines=((.9, .9, .85, .1, .02), (.05, .1, .25, .55, .08))):
    """Woven check for hanging cloth: base colour with crossing bands (r, g, b, position, width)."""
    t = np.arange(n) / n; col = np.tile(np.array(base, float), (n, n, 1))
    for r, g, b, pos, wid in lines:
        band = (np.abs(((t - pos + .5) % 1) - .5) < wid).astype(float)
        mask = np.maximum(band[None, :], band[:, None]) * .85
        col = col * (1 - mask[..., None]) + np.array([r, g, b]) * mask[..., None]
    return col * (1 + rng.normal(0, .03, (n, n, 1)))

def saree_texture(n=512):
    """Cotton saree: green body with small woven gold dots (buti), a gold border with a red line along the bottom
    and one side. Used without tiling: the border must sit at the cloth's edges."""
    u = np.arange(n)[None, :] / n; v = np.arange(n)[:, None] / n
    col = np.tile(np.array([.08, .42, .28]), (n, n, 1))
    dots = ((np.abs(((u * 18) % 1) - .5) < .12) & (np.abs(((v * 24 + (np.floor(u * 18) % 2) * .5) % 1) - .5) < .12)).astype(float)
    col = col * (1 - dots[..., None] * .8) + np.array([.82, .62, .18]) * dots[..., None] * .8
    for edge, w in ((1 - v, .14), (u, .08)):                                   # bottom and side border
        band = (edge < w).astype(float); line = (np.abs(edge - w * .55) < .012).astype(float)
        col = col * (1 - band[..., None]) + np.array([.8, .6, .16]) * band[..., None]
        col = col * (1 - line[..., None]) + np.array([.6, .06, .12]) * line[..., None]
    return col * (1 + rng.normal(0, .025, (n, n, 1)))

leaf_img = image_from_array('village_leaf', leaf_texture())
straw_cards_img = strand_texture(color=(.66, .53, .28), count=110, seed_tone=.12)
grass_cards_img = strand_texture(color=(.32, .38, .14), count=380, seed_tone=.35)
dead_leaf_img = image_from_array('village_leaf_dry', leaf_texture(green=(.36, .27, .13)))
trunk_img = image_from_array('village_palm_trunk', trunk_texture())
stem_img = image_from_array('village_banana_stem', stem_texture())
planks_img = image_from_array('village_door_planks', planks_texture())
paint_img = image_from_array('village_pump_paint', paint_rust_texture())

M = {
    'straw': pbr('Straw', acg('ThatchedRoof002A', 'Color'), acg('ThatchedRoof002A', 'NormalGL'), acg('ThatchedRoof002A', 'Roughness'), tint=(1.1, .98, .78)),
    'bamboo': pbr('Bamboo', acg('Bamboo001C', 'Color'), acg('Bamboo001C', 'NormalGL'), acg('Bamboo001C', 'Roughness'), tint=(1.15, 1.05, .85)),
    # walls: smeared raw clay (the plaster texture had vertical board marks that read as planks)
    'mud': pbr('MudPlaster', acg('Clay005', 'Color'), acg('Clay005', 'NormalGL'), acg('Clay005', 'Roughness'), tint=(.74, .64, .54), sat=.62),   # earthy grey-brown, not orange
    'mud_base': pbr('MudBase', ph('dry_mud_field_001', 'diff'), ph('dry_mud_field_001', 'nor_gl'), ph('dry_mud_field_001', 'rough'), tint=(.7, .58, .46)),
    'tin': pbr('TinRoof', ph('rusty_corrugated_iron', 'diff'), ph('rusty_corrugated_iron', 'nor_gl'), ph('rusty_corrugated_iron', 'rough'), metallic=.35),
    'wood': pbr('OldWood', planks_img, rough_value=.85),
    'clay': pbr('Terracotta', acg('Clay005', 'Color'), acg('Clay005', 'NormalGL'), acg('Clay005', 'Roughness'), tint=(1.05, .6, .38)),
    'dung': pbr('DungCake', acg('Clay005', 'Color'), acg('Clay005', 'NormalGL'), acg('Clay005', 'Roughness'), tint=(.42, .32, .22)),
    'jute': pbr('Jute', ph('hessian_230', 'diff'), ph('hessian_230', 'nor_gl'), ph('hessian_230', 'rough'), tint=(.72, .56, .36)),
    'concrete': pbr('Concrete', ph('yellow_plaster_02', 'diff'), ph('yellow_plaster_02', 'nor_gl'), ph('yellow_plaster_02', 'rough'), tint=(.72, .72, .7)),
    'leaf': pbr('Leaf', leaf_img, rough_value=.55),
    'straw_cards': pbr('StrawCards', straw_cards_img, rough_value=.8, alpha=True),
    'grass_cards': pbr('GrassCards', grass_cards_img, rough_value=.7, alpha=True),
    'lungi_cloth': pbr('LungiCloth', image_from_array('village_cloth_lungi', plaid_texture(
        base=(.12, .22, .48), lines=((.85, .85, .8, .1, .015), (.05, .1, .26, .55, .09), (.45, .6, .85, .3, .01), (.45, .6, .85, .8, .01)))), rough_value=.85),
    'gamcha_cloth': pbr('GamchaCloth', image_from_array('village_cloth_gamcha', plaid_texture(
        base=(.75, .1, .1), lines=((.95, .93, .88, .25, .06), (.95, .93, .88, .75, .06), (.2, .45, .2, .5, .01)))), rough_value=.85),
    'saree_cloth': pbr('SareeCloth', image_from_array('village_cloth_saree', saree_texture()), rough_value=.6),
    'rope': pbr('Rope', ph('hessian_230', 'diff'), tint=(.6, .5, .36), rough_value=.9),
    'rickshaw_paint': pbr('RickshawPaint', paint_img, tint=(1.3, 2.2, 3.6), rough_value=.4, metallic=.4),
    'dead_leaf': pbr('DryLeaf', dead_leaf_img, rough_value=.8),
    'stem': pbr('BananaStem', stem_img, rough_value=.6),
    'frond': pbr('FrondStem', leaf_img, tint=(1.4, 1.25, .8), rough_value=.6),
    'trunk': pbr('PalmTrunk', trunk_img, rough_value=.85),
    'paint': pbr('PumpPaint', paint_img, rough_value=.45, metallic=.5),
}

def plain(name, color, rough, metallic=0.0, ior=None):
    m = bpy.data.materials.new(name); m.use_nodes = True; b = m.node_tree.nodes['Principled BSDF']
    b.inputs['Base Color'].default_value = (*color, 1); b.inputs['Roughness'].default_value = rough
    b.inputs['Metallic'].default_value = metallic
    if ior: b.inputs['IOR'].default_value = ior
    return m
M['water'] = plain('PondWater', (.035, .06, .045), .04, ior=1.33)            # dark, still, green-brown village pond
M['tyre'] = plain('Tyre', (.025, .025, .025), .7)
M['hyacinth'] = plain('HyacinthFlower', (.55, .45, .85), .5)

# ---------------------------------------------------------------- props (each built at the origin)
def haystack(prop='Haystack', H=3.0, R=1.25):
    # tall dome of straw stacked around a bamboo pole, slightly irregular, with a pointed cap
    prof = []
    for k in range(22):
        h = k / 21
        r = R * (1 - h ** 1.7) ** .75 * (1 + .1 * math.sin(h * math.pi))
        prof.append((max(r, .02), h * H))
    ob = revolve(prop + '_straw', prof, prop, M['straw'], seg=48, u_tiles=4, wobble=.07, seed=1, v_scale=.6)
    for v in ob.data.vertices:                                                # stacked layers: soft horizontal bulges
        h = v.co.z / H; rr = math.hypot(v.co.x, v.co.y)
        if rr > .05: s = 1 + .025 * math.sin(h * 2 * math.pi * 7); v.co.x *= s; v.co.y *= s
    d = ob.modifiers.new('rough', 'DISPLACE'); tx = bpy.data.textures.new('hay_noise', 'CLOUDS'); tx.noise_scale = .25
    d.texture = tx; d.strength = .08; d.mid_level = .5
    bpy.context.view_layer.objects.active = ob; bpy.ops.object.modifier_apply(modifier='rough')
    tube(prop + '_pole', [(0, 0, H - .3), (0, 0, H + .55)], .035, prop, M['bamboo'], seg=8)
    # a loose ring of straw around the base
    revolve(prop + '_skirt', [(R * 1.08, 0), (R * 1.02, .12), (R * .9, .2)], prop, M['straw'], seg=40, u_tiles=4, wobble=.12, seed=3)
    # loose straws sticking out and hanging down: alpha strand cards on the surface (breaks the smooth outline)
    ob.data.update(); verts, faces, uvs = [], [], []
    surf = [(ob.matrix_world @ v.co, (ob.matrix_world.to_3x3() @ v.normal).normalized()) for v in ob.data.vertices if v.co.z < H * .92]
    for c in range(1400):
        p, n = surf[rng.integers(len(surf))]
        down = (Vector((0, 0, -1)) - n * Vector((0, 0, -1)).dot(n)).normalized()
        L = rng.uniform(.1, .26); w = rng.uniform(.015, .03)                    # narrow, sparse strands, not patches
        side = n.cross(down).normalized(); tip = p + down * L * .8 + n * L * rng.uniform(.15, .45)
        b = len(verts); u0 = rng.uniform(0, .8)
        verts += [p - side * w / 2, p + side * w / 2, tip + side * w / 2, tip - side * w / 2]
        uvs += [(u0, 0), (u0 + .2, 0), (u0 + .2, 1), (u0, 1)]; faces.append((b, b + 1, b + 2, b + 3))
    mesh(prop + '_loose', verts, faces, prop, M['straw_cards'], uvs, smooth=False)

def tube_well(prop='TubeWell'):
    box(prop + '_pad', (1.2, 1.2, .14), (0, 0, .07), prop, M['concrete'], bevel=.02, tile=.8)
    box(prop + '_drain', (.18, .55, .1), (0, .82, .05), prop, M['concrete'], bevel=.01, tile=.8)
    revolve(prop + '_base', [(.11, .14), (.11, .2), (.07, .24)], prop, M['paint'], seg=20)
    revolve(prop + '_body', [(.065, .24), (.065, .78), (.075, .8), (.075, .86), (.04, .9)], prop, M['paint'], seg=20, u_tiles=1)
    tube(prop + '_spout', [(0, .05, .66), (0, .2, .63), (0, .26, .58)], .022, prop, M['paint'], seg=10)
    revolve(prop + '_cap', [(.075, .86), (.06, .9), (.03, .93), (.001, .94)], prop, M['paint'], seg=20)
    box(prop + '_bracket', (.03, .1, .12), (0, -.05, .9), prop, M['paint'], bevel=.005, tile=.3)
    tube(prop + '_handle', [(0, -.05, .93), (0, -.3, 1.0), (0, -.62, 1.04)], .018, prop, M['paint'], seg=8)
    tube(prop + '_grip', [(0, -.62, 1.04), (0, -.8, 1.05)], .026, prop, M['wood'], seg=10)   # worn wooden grip on the handle end

def mud_house(prop='MudHouse', W=5.2, D=3.6, Hw=2.3, plinth=.45):
    # raised earthen plinth (bhita) with a front verandah
    box(prop + '_plinth', (W + 1.4, D + 2.2, plinth), (0, -.5, plinth / 2), prop, M['mud_base'], bevel=.08, tile=2)
    z0 = plinth; t = .28
    # walls with a door and a window in the front (facing -Y)
    door_w, door_h, win_w, win_h, win_z = .95, 1.85, .7, .55, 1.0
    fx = -D / 2
    door_l = -.6 - door_w / 2; door_r = door_l + door_w; win_l = 1.0; win_r = win_l + win_w
    # one continuous front wall with the openings cut out (separate pieces showed seams like planks)
    front = box(prop + '_wall_f', (W + t, t, Hw), (0, fx, z0 + Hw / 2), prop, M['mud'], tile=1.6)
    for w, h, cxx, czz in ((door_w, door_h, (door_l + door_r) / 2, z0 + door_h / 2 - .01),
                           (win_w, win_h, (win_l + win_r) / 2, z0 + win_z + win_h / 2)):
        bpy.ops.mesh.primitive_cube_add(size=1, location=(cxx, fx, czz)); cutter = bpy.context.active_object
        cutter.scale = (w, t * 3, h)
        mod = front.modifiers.new('cut', 'BOOLEAN'); mod.object = cutter; mod.operation = 'DIFFERENCE'; mod.solver = 'EXACT'
        bpy.context.view_layer.objects.active = front; bpy.ops.object.modifier_apply(modifier='cut')
        bpy.data.objects.remove(cutter, do_unlink=True)
    bev = front.modifiers.new('bevel', 'BEVEL'); bev.width = .03; bev.segments = 2; bev.limit_method = 'ANGLE'
    bpy.context.view_layer.objects.active = front; bpy.ops.object.modifier_apply(modifier='bevel')
    uv_box(front, 1.6)
    box(prop + '_wall_b', (W + t, t, Hw), (0, D / 2, z0 + Hw / 2), prop, M['mud'], bevel=.03, tile=1.6)
    for sx in (-1, 1):
        box(prop + '_wall_s', (t, D - t, Hw), (sx * W / 2, 0, z0 + Hw / 2), prop, M['mud'], bevel=.03, tile=1.6)
    # darker mud band along the bottom of the walls (re-plastered often)
    box(prop + '_band_f', (W + .04, t + .03, .35), (0, fx, z0 + .175), prop, M['mud_base'], bevel=.03, tile=1.6)
    # wooden door (closed, slightly ajar) and shutter
    box(prop + '_door', (door_w - .06, .05, door_h - .04), ((door_l + door_r) / 2 + .02, fx - .02, z0 + door_h / 2), prop, M['wood'], bevel=.008, tile=1.2, rot=(0, 0, math.radians(-12)))
    box(prop + '_shutter', (win_w - .04, .04, win_h - .04), ((win_l + win_r) / 2, fx - .05, z0 + win_z + win_h / 2), prop, M['wood'], bevel=.006, tile=1.2)
    # corrugated tin gable roof with overhang, extended over the verandah at the front
    over, pitch = .45, math.radians(22)
    ridge_z = z0 + Hw + (D / 2 + over) * math.tan(pitch)
    for sy in (-1, 1):
        L = (D / 2 + over + (1.4 if sy < 0 else 0)) / math.cos(pitch)
        nx, ny = 160, 6; verts, faces, uvs = [], [], []
        for j in range(ny + 1):
            s = L * j / ny
            for i in range(nx + 1):
                x = -W / 2 - over + (W + 2 * over) * i / nx
                y = sy * s * math.cos(pitch); z = ridge_z - s * math.sin(pitch) + .012 * math.sin(x * 2 * math.pi / .076)
                verts.append((x, y, z)); uvs.append((x / 1.2, s / 1.2))
        faces = [(j * (nx + 1) + i, j * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i + 1, (j + 1) * (nx + 1) + i) for j in range(ny) for i in range(nx)]
        if sy > 0: faces = [tuple(reversed(f)) for f in faces]
        roof = mesh(prop + '_roof', verts, faces, prop, M['tin'], uvs)
        sol = roof.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = .006
    # bamboo posts holding the verandah roof
    for x in (-W / 2 - .1, -W / 6, W / 6, W / 2 + .1):
        tube(prop + '_post', [(x, fx - 1.3, z0), (x, fx - 1.3, z0 + Hw - .2)], .045, prop, M['bamboo'], seg=8)
    tube(prop + '_beam', [(-W / 2 - .3, fx - 1.3, z0 + Hw - .2), (W / 2 + .3, fx - 1.3, z0 + Hw - .2)], .04, prop, M['bamboo'], seg=8)
    # dung cakes (ghute) pressed onto the sunny side wall to dry
    for k in range(14):
        cy = -D / 2 + .5 + (k % 7) * .42 + rng.uniform(-.05, .05); cz = z0 + .7 + (k // 7) * .45 + rng.uniform(-.05, .05)
        prof = [(0, .03), (.06, .028), (.1, .015), (.115, 0)]
        dc = revolve(prop + '_dungcake', prof, prop, M['dung'], seg=14, wobble=.15, seed=k)
        dc.rotation_euler = (0, math.radians(90), 0); dc.location = (W / 2 + t / 2 + .005, cy, cz)
        bpy.context.view_layer.objects.active = dc; dc.select_set(True)
        bpy.ops.object.transform_apply(location=True, rotation=True, scale=True); dc.select_set(False)

def bamboo_fence(prop='BambooFence', L=4.0, H=1.6):
    for x in np.arange(-L / 2, L / 2 + .01, 1.33):
        lean = rng.uniform(-.03, .03)
        tube(prop + '_post', [(x, 0, -.2), (x + lean, 0, H + .15)], .04, prop, M['bamboo'], seg=8)
    for z in (.35, H - .25):
        tube(prop + '_rail', [(-L / 2 - .1, .05, z), (L / 2 + .1, .05, z + rng.uniform(-.02, .02))], .028, prop, M['bamboo'], seg=8)
    x = -L / 2
    while x < L / 2:                                                        # split-bamboo slats, slightly uneven
        w = rng.uniform(.04, .06); h = H + rng.uniform(-.12, .05)
        box(prop + '_slat', (w, .015, h), (x + w / 2, .08, h / 2), prop, M['bamboo'], tile=.5,
            rot=(0, math.radians(rng.uniform(-2, 2)), 0))
        x += w + rng.uniform(.0, .015)

def leaf_blade(name, prop, base, direction, length, width, rise, droop, twist=0.0, tear=.25, n=24, mat=None):
    """A banana leaf: a narrow petiole, then a long blade that rises and arches over (rise/droop in leaf
    lengths), slightly V-shaped across the midrib, with tears between the veins on the outer part."""
    verts, faces, uvs = [], [], []
    d = Vector(direction); d.z = 0; d.normalize(); side = d.cross(Vector((0, 0, 1))).normalized()
    for j in range(n + 1):
        t = j / n
        p = Vector(base) + d * length * t + Vector((0, 0, length * (rise * t - droop * t * t)))
        bt = min(1, max(0, (t - .16) / .84))                                  # blade starts after the petiole
        w = .012 if t < .16 else width * math.sin(math.pi * min(1, bt * 1.08)) ** .45
        for s in (-1, 0, 1):
            off = side * w * s * math.cos(twist * t) + Vector((0, 0, -abs(s) * w * (.22 + .25 * t)))
            verts.append(p + off); uvs.append(((s + 1) / 2, t))
    for j in range(n):
        for k in range(2):
            if tear and j > n * .35 and rng.random() < tear: continue        # torn strips toward the tip
            a = j * 3 + k; faces.append((a, a + 1, a + 4, a + 3))
    return mesh(name, verts, faces, prop, mat or M['leaf'], uvs)

def banana_clump_plant(prop, at, H, leaves, size):
    tube(prop + '_stem', [(at[0], at[1], 0), (at[0] + .01, at[1], H * .5), (at[0] + .02, at[1] + .01, H)],
         .12 * size, prop, M['stem'], seg=12, taper=lambda t: 1 - .35 * t)
    for k in range(leaves):                                                  # live leaves from the crown
        a = k * 2.4 + rng.uniform(-.25, .25)
        leaf_blade(prop + '_leaf', prop, (at[0] + .02, at[1] + .01, H - .03), (math.cos(a), math.sin(a), 0),
                   rng.uniform(2.0, 2.6) * size, rng.uniform(.3, .38) * size, rng.uniform(.9, 1.4), rng.uniform(1.1, 1.7),
                   twist=rng.uniform(-.5, .5))
    for k in range(3 if size > .8 else 1):                                   # old leaves hanging dead along the stem
        a = rng.uniform(0, 6.28)
        leaf_blade(prop + '_dead', prop, (at[0], at[1], H * rng.uniform(.6, .85)), (math.cos(a), math.sin(a), 0),
                   rng.uniform(1.1, 1.5) * size, .2 * size, -.1, 1.1, twist=1.2, tear=.4, mat=M['dead_leaf'])

def banana_plant(prop='BananaPlant', H=2.5):
    """A banana clump: a mature plant and two young suckers, as they grow beside village houses."""
    banana_clump_plant(prop, (0, 0), H, 8, 1.0)
    banana_clump_plant(prop, (.55, .3), 1.1, 4, .5)
    banana_clump_plant(prop, (-.4, .45), .8, 3, .4)

def coconut_palm(prop='CoconutPalm', H=7.5):
    pts = [(0, 0, 0)]
    for k in range(1, 15):
        t = k / 14; pts.append((.9 * t ** 1.6, .15 * t ** 2, H * t))           # gentle lean
    tube(prop + '_trunk', pts, .17, prop, M['trunk'], seg=12, taper=lambda t: 1 - .35 * t)
    top = Vector(pts[-1])
    for k in range(14):
        a = k * 2 * math.pi / 14 + rng.uniform(-.15, .15); up = rng.uniform(-.1, .5)
        d = Vector((math.cos(a), math.sin(a), up)).normalized(); L = rng.uniform(3.0, 3.8)
        spine = [top + d * L * t + Vector((0, 0, -1.4 * t * t * (1 - up))) for t in np.linspace(0, 1, 10)]
        tube(prop + '_rachis', spine, .025, prop, M['frond'], seg=5, taper=lambda t: 1 - .7 * t)
        side = d.cross(Vector((0, 0, 1))).normalized()
        verts, faces, uvs = [], [], []
        for j, p in enumerate(spine[1:], 1):                                   # pinnate leaflets on both sides
            t = j / 9; ll = .95 * math.sin(math.pi * min(1, t * 1.05)) + .12
            for s in (-1, 1):
                for q in range(4):
                    root = spine[j - 1].lerp(p, q / 4)
                    l2 = ll * rng.uniform(.85, 1.1)
                    mid = root + side * s * l2 * .55 + d * .06 + Vector((0, 0, -.12 * l2))
                    tip = root + side * s * l2 + d * .14 + Vector((0, 0, -.5 * l2))  # leaflets droop at the tips
                    w = (d * .035 + Vector((0, 0, .012))); b = len(verts)          # ~7 cm wide, folded slightly
                    verts += [root - w * .6, root + w * .6, mid + w, mid - w, tip + w * .15, tip - w * .15]
                    uvs += [(.35, 0), (.65, 0), (.65, .55), (.35, .55), (.55, 1), (.45, 1)]
                    faces += [(b, b + 1, b + 2, b + 3), (b + 3, b + 2, b + 4, b + 5)]
        mesh(prop + '_leaflets', verts, faces, prop, M['leaf'], uvs, smooth=False)
    for k in range(3):                                                         # dry old fronds hanging down the trunk
        a = rng.uniform(0, 6.28); d = Vector((math.cos(a), math.sin(a), 0))
        spine = [top + Vector((0, 0, -.15)) + d * .45 * t + Vector((0, 0, -2.2 * t)) for t in np.linspace(0, 1, 12)]
        tube(prop + '_dry_rachis', spine, .022, prop, M['dead_leaf'], seg=5, taper=lambda t: 1 - .6 * t)
        side = d.cross(Vector((0, 0, 1))).normalized(); verts, faces, uvs = [], [], []
        for j, p in enumerate(spine[1:], 1):                                   # dense, limp leaflets hanging almost straight down
            for s in (-1, 1):
                for q in range(3):
                    root = spine[j - 1].lerp(p, q / 3); b = len(verts)
                    tip = root + side * s * rng.uniform(.06, .16) + d * rng.uniform(-.05, .08) + Vector((0, 0, -rng.uniform(.45, .7)))
                    w = side * .025
                    verts += [root - w, root + w, tip + w * .3, tip - w * .3]
                    uvs += [(.4, 0), (.6, 0), (.55, 1), (.45, 1)]; faces.append((b, b + 1, b + 2, b + 3))
        mesh(prop + '_dry_leaflets', verts, faces, prop, M['dead_leaf'], uvs, smooth=False)
    for k in range(7):                                                         # coconut bunch
        bpy.ops.mesh.primitive_uv_sphere_add(segments=12, ring_count=8, radius=.11,
                                             location=top + Vector((math.cos(k) * .2, math.sin(k) * .2, -.25 - .05 * (k % 2))))
        c = bpy.context.active_object; c.name = prop + '_coconut'; c.data.materials.append(M['trunk'])
        for col in c.users_collection: col.objects.unlink(c)
        link(c, prop)

def kolshi(prop='ClayPot', loc=(0, 0, 0), s=1.0):
    prof = [(0.001, 0), (.09, .005), (.17, .07), (.19, .16), (.17, .26), (.11, .32), (.065, .35), (.06, .39), (.085, .42), (.08, .43)]
    revolve(prop, [(r * s, z * s) for r, z in prof], prop, M['clay'], seg=28, loc=loc, u_tiles=2, v_scale=2)

def jute_sack(prop='JuteSack', loc=(0, 0, 0)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=20, ring_count=14, radius=.3, location=(loc[0], loc[1], loc[2] + .32))
    ob = bpy.context.active_object; ob.name = prop; ob.scale = (1, .8, 1.15)
    for v in ob.data.vertices:
        if v.co.z < -.12: v.co.z = -.12 - (v.co.z + .12) * .15                 # flat bottom where it sits
        if v.co.z > .2: v.co.x *= .55; v.co.y *= .55                           # gathered, tied neck
        v.co += v.normal * .03 * noise.noise(v.co * 6 + Vector((loc[0], 0, 0)))  # lumpy: grain inside the sack
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    uv_box(ob, .3); ob.data.materials.append(M['jute'])
    for p in ob.data.polygons: p.use_smooth = True
    tube(prop + '_tie', [(loc[0] - .09, loc[1], loc[2] + .62), (loc[0] + .09, loc[1], loc[2] + .63)], .012, prop, M['jute'], seg=6)
    for c in ob.users_collection: c.objects.unlink(ob)
    link(ob, prop)

def cloth_panel(name, prop, top_left, top_right, drop, mat, n=10, sway=.03, repeat=(1, 1)):
    """A cloth hanging over the line: grid from the line downwards, gentle folds and sag.
    repeat tiles the woven pattern so checks are cloth-sized, not flag-sized."""
    a, b = Vector(top_left), Vector(top_right); verts, faces, uvs = [], [], []
    for j in range(n + 1):
        t = j / n
        for i in range(n + 1):
            s = i / n; p = a.lerp(b, s)
            fold = sway * math.sin(s * math.pi * 5 + t * 2) * (.3 + t)
            verts.append(p + Vector((0, fold, -drop * t - .03 * math.sin(s * math.pi) * t))); uvs.append((s * repeat[0], (1 - t) * repeat[1]))
    faces = [(j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i) for j in range(n) for i in range(n)]
    ob = mesh(name, verts, faces, prop, mat, uvs)
    sol = ob.modifiers.new('thick', 'SOLIDIFY'); sol.thickness = .004
    return ob

def clothes_line(prop='ClothesLine', L=4.0):
    """Two bamboo poles and a sagging jute rope with a lungi, a gamcha and a saree drying in the sun."""
    for x in (-L / 2, L / 2):
        tube(prop + '_pole', [(x, 0, 0), (x + rng.uniform(-.04, .04), 0, 1.95)], .035, prop, M['bamboo'], seg=8)
    rope = [(x, 0, 1.85 - .18 * (1 - (2 * x / L) ** 2)) for x in np.linspace(-L / 2, L / 2, 21)]
    tube(prop + '_rope', rope, .006, prop, M['rope'], seg=5)
    def at(x): return Vector((x, 0, 1.85 - .18 * (1 - (2 * x / L) ** 2)))
    cloth_panel(prop + '_lungi', prop, at(-1.6), at(-.65), 1.0, M['lungi_cloth'], repeat=(4, 4))
    cloth_panel(prop + '_gamcha', prop, at(-.45), at(-.05), .55, M['gamcha_cloth'], n=8, repeat=(3, 4))
    cloth_panel(prop + '_saree', prop, at(.15), at(1.7), 1.25, M['saree_cloth'], n=12, sway=.05)

def straw_drying(prop='StrawDrying', R=1.6):
    """Rice straw spread out on a woven bamboo mat (chatai) to dry in the courtyard."""
    verts, faces, uvs = [], [], []
    for j in range(9):                                                        # irregular oval mat, slightly uneven
        for i in range(25):
            a = 2 * math.pi * i / 24; r = R * j / 8 * (1 + .08 * math.sin(a * 3))
            verts.append((r * math.cos(a), r * .7 * math.sin(a), .01 + .006 * noise.noise(Vector((i, j, 0)) * .7)))
            uvs.append((r * math.cos(a) / .6, r * .7 * math.sin(a) / .6))
    faces = [(j * 25 + i, j * 25 + i + 1, (j + 1) * 25 + i + 1, (j + 1) * 25 + i) for j in range(8) for i in range(24)]
    mesh(prop + '_mat', verts, faces, prop, M['bamboo'], uvs)
    verts, faces, uvs = [], [], []                                            # straw strands lying flat in drifts
    for c in range(700):
        a = rng.uniform(0, 6.28); r = R * .95 * math.sqrt(rng.random())
        p = Vector((r * math.cos(a), r * .7 * math.sin(a), .02 + rng.uniform(0, .05)))
        d = Vector((math.cos(rng.uniform(0, 6.28)), math.sin(rng.uniform(0, 6.28)), 0)).normalized()
        L = rng.uniform(.3, .6); w = rng.uniform(.04, .08); side = d.cross(Vector((0, 0, 1))) * w / 2
        b = len(verts); u0 = rng.uniform(0, .8)
        verts += [p - side, p + side, p + d * L + side + Vector((0, 0, .02)), p + d * L - side + Vector((0, 0, .02))]
        uvs += [(u0, 0), (u0 + .2, 0), (u0 + .2, 1), (u0, 1)]; faces.append((b, b + 1, b + 2, b + 3))
    mesh(prop + '_straw', verts, faces, prop, M['straw_cards'], uvs, smooth=False)

def grass_clump(prop='GrassClump', blades=14):
    """A clump of grass cards (crossed alpha strips) for scattering along edges and fences."""
    verts, faces, uvs = [], [], []
    for k in range(blades):
        a = k / blades * math.pi + rng.uniform(-.2, .2); h = rng.uniform(.25, .5); w = rng.uniform(.18, .3)
        lean = Vector((rng.uniform(-.08, .08), rng.uniform(-.08, .08), 0))
        side = Vector((math.cos(a), math.sin(a), 0)) * w / 2; o = Vector((rng.uniform(-.08, .08), rng.uniform(-.08, .08), 0))
        b = len(verts); u0 = rng.uniform(0, .6)
        verts += [o - side, o + side, o + side * .8 + Vector((0, 0, h)) + lean, o - side * .8 + Vector((0, 0, h)) + lean]
        uvs += [(u0, 0), (u0 + .4, 0), (u0 + .4, 1), (u0, 1)]; faces.append((b, b + 1, b + 2, b + 3))
    mesh(prop, verts, faces, prop, M['grass_cards'], uvs, smooth=False)

def pond(prop='Pond', R=3.2):
    """A village pond edge: dark still water below a sloping mud bank, with water hyacinth floating."""
    verts, faces, uvs = [], [], []
    # raised earth bank (paar) around the pond, as village ponds are dug: rises above the yard, slopes down to the water
    rings = [(R * 1.5, -.02), (R * 1.3, .32), (R * 1.18, .36), (R * 1.04, .08), (R * .96, -.02)]
    for j, (r, z) in enumerate(rings):
        for i in range(48):
            a = 2 * math.pi * i / 48; w = 1 + .08 * noise.noise(Vector((math.cos(a) * 2, math.sin(a) * 2, j * .3)))
            verts.append((r * w * math.cos(a), r * .75 * w * math.sin(a), z)); uvs.append((r * w * math.cos(a) / 2, r * .75 * w * math.sin(a) / 2))
    faces = [(j * 48 + i, j * 48 + (i + 1) % 48, (j + 1) * 48 + (i + 1) % 48, (j + 1) * 48 + i) for j in range(len(rings) - 1) for i in range(48)]
    mesh(prop + '_bank', verts, faces, prop, M['mud_base'], uvs)
    bpy.ops.mesh.primitive_circle_add(vertices=48, radius=R, fill_type='NGON', location=(0, 0, .02))
    wtr = bpy.context.active_object; wtr.name = prop + '_water'; wtr.scale = (1, .75, 1)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    uv_box(wtr, 2); wtr.data.materials.append(M['water'])
    for c in wtr.users_collection: c.objects.unlink(wtr)
    link(wtr, prop)
    for k in range(9):                                                        # water hyacinth rosettes near the edge
        a = rng.uniform(0, 6.28); r = R * rng.uniform(.6, .9); c = Vector((r * math.cos(a), r * .75 * math.sin(a), .03))
        for q in range(7):
            b2 = q * 2 * math.pi / 7 + rng.uniform(-.2, .2); d = Vector((math.cos(b2), math.sin(b2), .9))
            leaf_blade(prop + '_hyacinth', prop, c, d, .18, .07, .9, .5, tear=0, n=6)
        if k % 3 == 0:
            bpy.ops.mesh.primitive_uv_sphere_add(segments=8, ring_count=6, radius=.035, location=c + Vector((0, 0, .2)))
            fl = bpy.context.active_object; fl.name = prop + '_flower'; fl.scale = (1, 1, 1.8); fl.data.materials.append(M['hyacinth'])
            for col in fl.users_collection: col.objects.unlink(fl)
            link(fl, prop)

def wheel(name, prop, centre, radius, axis='x', spokes=20):
    """Bicycle-style wheel: rubber tyre, thin rim, hub and wire spokes."""
    rot = Matrix.Rotation(math.radians(90), 4, 'Y') if axis == 'x' else Matrix.Identity(4)
    bpy.ops.mesh.primitive_torus_add(major_radius=radius, minor_radius=.022, major_segments=32, minor_segments=8, location=centre)
    t = bpy.context.active_object; t.name = name + '_tyre'; t.matrix_world = Matrix.Translation(centre) @ rot
    t.data.materials.append(M['tyre'])
    for c in t.users_collection: c.objects.unlink(t)
    link(t, prop)
    c = Vector(centre)
    tube(name + '_hub', [c + rot.to_3x3() @ Vector((0, 0, -.05)), c + rot.to_3x3() @ Vector((0, 0, .05))], .025, prop, M['rickshaw_paint'], seg=8)
    for k in range(spokes):
        a = 2 * math.pi * k / spokes
        tip = c + rot.to_3x3() @ Vector((math.cos(a) * (radius - .02), math.sin(a) * (radius - .02), .0))
        tube(name + '_spoke', [c, tip], .0025, prop, M['paint'], seg=3)

def van_rickshaw(prop='VanRickshaw'):
    """Pedal van-rickshaw: bicycle front with handlebar and saddle, flat wooden cargo deck on two rear wheels."""
    r = .33
    wheel(prop + '_front', prop, (0, -1.25, r), r, axis='x')
    for sx in (-.55, .55): wheel(prop + '_rear', prop, (sx, .45, r), r, axis='x')
    tube(prop + '_axle', [(-.6, .45, r), (.6, .45, r)], .015, prop, M['paint'], seg=6)
    P = M['rickshaw_paint']
    tube(prop + '_frame_top', [(0, -1.12, .95), (0, -.35, .9)], .022, prop, P, seg=8)       # bicycle frame
    tube(prop + '_frame_down', [(0, -1.1, .9), (0, -.45, .42)], .022, prop, P, seg=8)
    tube(prop + '_seat_tube', [(0, -.35, .92), (0, -.42, .4)], .02, prop, P, seg=8)
    tube(prop + '_fork', [(0, -1.12, 1.0), (0, -1.25, r)], .016, prop, P, seg=6)
    tube(prop + '_handlebar', [(-.3, -1.05, 1.08), (0, -1.12, 1.03), (.3, -1.05, 1.08)], .014, prop, P, seg=6)
    tube(prop + '_chain_stay', [(0, -.42, .4), (0, .45, r)], .016, prop, P, seg=6)
    box(prop + '_saddle', (.12, .24, .05), (0, -.33, .98), prop, M['tyre'], bevel=.02, tile=.3)
    box(prop + '_deck', (1.05, 1.25, .04), (0, .4, .62), prop, M['wood'], tile=.6)          # cargo deck
    for sx in (-1, 1):
        box(prop + '_rail', (.04, 1.25, .1), (sx * .5, .4, .69), prop, M['wood'], tile=.6)
        tube(prop + '_deck_strut', [(sx * .45, .45, r), (sx * .45, .45, .6)], .015, prop, P, seg=6)
    tube(prop + '_deck_bar', [(0, -.42, .4), (0, -.2, .6)], .018, prop, P, seg=6)

haystack(); tube_well(); mud_house(); bamboo_fence(); banana_plant(); coconut_palm()
kolshi('ClayPot'); jute_sack('JuteSack')
clothes_line(); straw_drying(); grass_clump(); pond(); van_rickshaw()

# ---------------------------------------------------------------- export each prop to Unity (FBX + textures)
summary = {}
for name, objs in props.items():
    bpy.ops.object.select_all(action='DESELECT')
    for o in objs: o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    tris = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs:
        me = o.evaluated_get(dg).to_mesh(); me.calc_loop_triangles(); tris += len(me.loop_triangles); o.evaluated_get(dg).to_mesh_clear()
    bpy.ops.export_scene.fbx(filepath=str(UNITY / f'{name}.fbx'), use_selection=True, apply_unit_scale=True,
                             apply_scale_options='FBX_SCALE_UNITS', axis_forward='-Z', axis_up='Y',
                             use_mesh_modifiers=True, mesh_smooth_type='FACE', path_mode='STRIP', embed_textures=False)
    summary[name] = {'triangles': tris, 'objects': len(objs)}
    print('EXPORTED', name, tris, 'tris', flush=True)
used = set()
for m in bpy.data.materials:
    if not m.use_nodes: continue
    for n in m.node_tree.nodes:
        if n.type == 'TEX_IMAGE' and n.image:
            img = n.image; dest = UNITY / 'Textures' / (pathlib.Path(img.filepath).name if img.filepath else img.name + '.png')
            if dest.name in used: continue
            used.add(dest.name)
            if img.filepath and pathlib.Path(bpy.path.abspath(img.filepath)).exists():
                shutil.copy2(bpy.path.abspath(img.filepath), dest)
            else:
                img.filepath_raw = str(dest); img.file_format = 'PNG'; img.save()
summary['_materials'] = {m.name: [n.image.name for n in m.node_tree.nodes if n.type == 'TEX_IMAGE' and n.image] for m in bpy.data.materials if m.use_nodes}
(ROOT / 'village-props-summary.json').write_text(json.dumps(summary, indent=2))
bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'vendor' / 'village-props.blend'))

# ---------------------------------------------------------------- courtyard layout + renders
if '--no-render' not in ARGS:
    placed = {}
    def place(prop, loc, rot=0.0, scale=1.0):
        placed[prop] = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ Matrix.Scale(scale, 4)
        for o in props[prop]: o.matrix_world = placed[prop] @ o.matrix_world
    place('MudHouse', Vector((0, 6.5, 0)))
    place('Haystack', Vector((-6.2, 3.2, 0)))
    place('TubeWell', Vector((4.2, 1.4, 0)), math.radians(-30))
    place('BambooFence', Vector((-3.5, 9.6, 0)))
    place('BananaPlant', Vector((3.9, 4.0, .45)))
    place('CoconutPalm', Vector((-4.6, 8.8, 0)), math.radians(20))
    place('ClayPot', Vector((4.9, 1.0, .14)))
    place('JuteSack', Vector((-1.6, 4.1, .45)))
    place('ClothesLine', Vector((-3.4, .4, 0)), math.radians(8))
    place('StrawDrying', Vector((-1.2, -2.6, 0)), math.radians(-10))
    place('Pond', Vector((9.5, 6.5, 0)))
    place('VanRickshaw', Vector((-7.6, -.6, 0)), math.radians(-115))
    place('GrassClump', Vector((-7.0, 6.0, 0)))
    # grass along the fence, the plinth edges, the pond bank and the courtyard border
    spots = [(-5 + 1.1 * i + rng.uniform(-.3, .3), 9.2 + rng.uniform(-.3, .3)) for i in range(9)] + \
            [(-3.6 + rng.uniform(-.2, .2), 3.6 + i * .7) for i in range(4)] + \
            [(9.5 + 4.2 * math.cos(a), 6.5 + 3.2 * math.sin(a)) for a in np.linspace(0, 6.28, 14, endpoint=False)] + \
            [(10 * math.cos(a) + rng.uniform(-1, 1), 10 * math.sin(a) + 2 + rng.uniform(-1, 1)) for a in np.linspace(0, 6.28, 40, endpoint=False)]
    for x, y in spots:
        m_ = Matrix.Translation((x, y, 0)) @ Matrix.Rotation(rng.uniform(0, 6.28), 4, 'Z') @ Matrix.Scale(rng.uniform(.7, 1.4), 4) @ placed['GrassClump'].inverted()
        for o in props['GrassClump']:
            c = o.copy(); c.data = o.data; bpy.context.collection.objects.link(c); c.matrix_world = m_ @ o.matrix_world
    # extra copies for a fuller courtyard
    for src, loc, rot in (('BananaPlant', (5.4, 5.6, 0), 1.2), ('ClayPot', (4.55, .6, .14), .5), ('BambooFence', (2.6, 9.7, 0), .05),
                          ('JuteSack', (-2.2, 4.3, .45), 2.0)):
        copy_m = Matrix.Translation(loc) @ Matrix.Rotation(rot, 4, 'Z') @ placed[src].inverted()
        for o in props[src]:
            c = o.copy(); c.data = o.data; bpy.context.collection.objects.link(c)
            c.matrix_world = copy_m @ o.matrix_world
    # ground: packed earth with grassy edges
    bpy.ops.mesh.primitive_plane_add(size=60, location=(0, 0, 0)); g = bpy.context.active_object; g.name = 'Ground'
    uv_box(g, 2.5)
    gm = bpy.data.materials.new('Courtyard'); gm.use_nodes = True; nt = gm.node_tree; b = nt.nodes['Principled BSDF']
    def t(path, nc=False):
        n = nt.nodes.new('ShaderNodeTexImage'); n.image = bpy.data.images.load(str(path), check_existing=True)
        if nc: n.image.colorspace_settings.name = 'Non-Color'
        return n
    dirt, grass = t(ph('dry_mud_field_001', 'diff')), t(ph('grass_ground', 'diff'))
    nzt = nt.nodes.new('ShaderNodeTexNoise'); nzt.inputs['Scale'].default_value = .08
    geo = nt.nodes.new('ShaderNodeNewGeometry'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); nt.links.new(geo.outputs['Position'], sep.inputs['Vector'])
    dist = nt.nodes.new('ShaderNodeVectorMath'); dist.operation = 'LENGTH'; nt.links.new(geo.outputs['Position'], dist.inputs[0])
    ramp = nt.nodes.new('ShaderNodeMapRange'); ramp.inputs['From Min'].default_value = 7; ramp.inputs['From Max'].default_value = 13
    add = nt.nodes.new('ShaderNodeMath'); add.operation = 'ADD'
    nt.links.new(dist.outputs['Value'], ramp.inputs['Value']); nt.links.new(ramp.outputs['Result'], add.inputs[0]); nt.links.new(nzt.outputs['Fac'], add.inputs[1])
    clamp = nt.nodes.new('ShaderNodeMath'); clamp.operation = 'SUBTRACT'; clamp.use_clamp = True; clamp.inputs[1].default_value = .55
    nt.links.new(add.outputs['Value'], clamp.inputs[0])
    mix = nt.nodes.new('ShaderNodeMix'); mix.data_type = 'RGBA'
    nt.links.new(clamp.outputs['Value'], mix.inputs['Factor']); nt.links.new(dirt.outputs['Color'], mix.inputs[6]); nt.links.new(grass.outputs['Color'], mix.inputs[7])
    tint = nt.nodes.new('ShaderNodeMix'); tint.data_type = 'RGBA'; tint.blend_type = 'MULTIPLY'; tint.inputs['Factor'].default_value = 1
    tint.inputs[7].default_value = (1.0, .86, .7, 1); nt.links.new(mix.outputs[2], tint.inputs[6]); nt.links.new(tint.outputs[2], b.inputs['Base Color'])
    nn = nt.nodes.new('ShaderNodeNormalMap'); nt.links.new(t(ph('dry_mud_field_001', 'nor_gl'), True).outputs['Color'], nn.inputs['Color']); nt.links.new(nn.outputs['Normal'], b.inputs['Normal'])
    b.inputs['Roughness'].default_value = .95
    g.data.materials.append(gm)
    # sky and sun: same evening light as the character mockups
    world = bpy.data.worlds.new('Evening'); scene.world = world; world.use_nodes = True
    wn = world.node_tree.nodes; env = wn.new('ShaderNodeTexEnvironment')
    env.image = bpy.data.images.load(str(ROOT / 'vendor' / 'hdri' / 'evening_field_2k.hdr'))
    world.node_tree.links.new(env.outputs['Color'], wn['Background'].inputs['Color']); wn['Background'].inputs['Strength'].default_value = .6
    sun = bpy.data.lights.new('Sun', 'SUN'); sun.energy = 6.5; sun.color = (1, .78, .55); sun.angle = math.radians(1.5)
    so = bpy.data.objects.new('Sun', sun); scene.collection.objects.link(so); so.rotation_euler = (math.radians(68), 0, math.radians(-50))
    # Bablu for scale, if the mockup exists
    mock = ROOT / 'vendor' / 'bablu-mockup.blend'
    if mock.exists():
        with bpy.data.libraries.load(str(mock), link=False) as (src, dst):
            dst.objects = [n for n in src.objects if n not in ('Ground', 'Sun') and not n.startswith(('three', 'front', 'face', 'Preview'))]
        for o in dst.objects:
            if o and o.type in ('MESH', 'ARMATURE'): scene.collection.objects.link(o)
        rig = next((o for o in dst.objects if o and o.type == 'ARMATURE'), None)
        if rig: rig.location = Vector((2.6, .2, 0)); rig.rotation_euler = (0, 0, math.radians(200))
    scene.render.engine = 'CYCLES'; scene.cycles.samples = SAMPLES; scene.cycles.use_denoising = True; scene.cycles.device = 'CPU'
    try: scene.view_settings.view_transform = 'AgX'; scene.view_settings.look = 'AgX - Medium High Contrast'
    except TypeError: pass
    scene.render.image_settings.file_format = 'JPEG'; scene.render.image_settings.quality = 90
    def shoot(name, loc, target, lens, res=(1600, 900)):
        cd = bpy.data.cameras.new(name); cd.lens = lens; co = bpy.data.objects.new(name, cd); scene.collection.objects.link(co)
        co.location = loc; co.rotation_euler = (Vector(target) - Vector(loc)).to_track_quat('-Z', 'Y').to_euler()
        scene.camera = co; scene.render.resolution_x, scene.render.resolution_y = res
        scene.render.filepath = str(RENDERS / f'{name}.jpg'); bpy.ops.render.render(write_still=True); print('RENDERED', name, flush=True)
    shoot('courtyard-broadcast', (6.5, -9.5, 3.6), (0, 3.2, 1.3), 30)
    shoot('courtyard-ground', (-1.2, -3.2, 1.25), (1.5, 4, 1.4), 24)
    shoot('tube-well-close', (5.6, -.4, 1.3), (4.3, 1.4, .6), 45, (1200, 1200))
    shoot('clothes-line-rickshaw', (-1.0, -6.8, 1.7), (-5.2, .2, 1.0), 30)
    shoot('pond-edge', (5.2, -.8, 2.2), (9.8, 6.6, -.1), 30)
    shoot('haystack-palm-close', (-3.2, -.6, 1.6), (-6.0, 3.6, 1.6), 35, (1200, 1200))
    bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / 'vendor' / 'village-courtyard.blend'))
print('DONE', json.dumps({k: v for k, v in summary.items() if not k.startswith('_')}), flush=True)
