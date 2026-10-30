"""Offline design refinements for Bablu's approved photographic concept.

Run through create_mockup_bablu.py -- --design-v4 --samples 48.
Procedural shader detail is an offline design aid and requires texture baking for Unity.
"""
import bpy
import math


def refine(body, rig, vest, gamcha, height, context):
    import numpy as np
    from mathutils import Vector
    # Replace the disconnected body cutout/straps with one continuous sewn garment.
    material = vest.data.materials[0]
    for obj in list(bpy.data.objects):
        if obj.name == 'Vest' or obj.name.startswith('Vest_strap'):
            bpy.data.objects.remove(obj, do_unlink=True)
    cx, cy, zneck, ztop = (context[k] for k in ('cx', 'cy', 'z_neck', 'z_top'))
    V, warm = context['V'], context['w_arm']
    import bmesh
    # Sample the rest body directly so shoulder straps follow the real clavicle surface.
    rig.data.pose_position = 'REST'; bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    mesh = bpy.data.meshes.new_from_object(body.evaluated_get(dg), depsgraph=dg)
    vest = bpy.data.objects.new('Vest', mesh); bpy.context.collection.objects.link(vest)
    vest.matrix_world = body.matrix_world.copy()
    dx = np.abs(V[:, 0] - cx)
    keep = context['is_body'] & (V[:, 2] > ztop - .02) & (V[:, 2] < zneck + .035) & (dx < .205)
    # Smooth U neckline and deep armholes, rather than deleting every neck-weighted vertex.
    neckline = zneck - .155 + .18 * np.minimum(dx / .075, 1) ** 2
    keep &= V[:, 2] < neckline
    armpit = ((dx - .205) / .075) ** 2 + ((V[:, 2] - (zneck - .075)) / .17) ** 2
    keep &= ~((dx > .12) & (armpit < 1))
    bm = bmesh.new(); bm.from_mesh(mesh); bm.verts.ensure_lookup_table()
    bmesh.ops.delete(bm, geom=[f for f in bm.faces if not all(keep[v.index] for v in f.verts)], context='FACES')
    bmesh.ops.delete(bm, geom=[v for v in bm.verts if not v.link_faces], context='VERTS')
    bm.normal_update()
    for v in bm.verts: v.co += v.normal * .009
    boundary = [v for v in bm.verts if v.is_boundary]
    for _ in range(14): bmesh.ops.smooth_vert(bm, verts=boundary, factor=.4, use_axis_x=True, use_axis_y=True, use_axis_z=True)
    bm.to_mesh(mesh); bm.free()
    mesh.materials.clear(); mesh.materials.append(material)
    for polygon in mesh.polygons: polygon.use_smooth = True
    uv = mesh.uv_layers.active or mesh.uv_layers.new()
    for polygon in mesh.polygons:
        for li, vi in zip(polygon.loop_indices, polygon.vertices):
            co = mesh.vertices[vi].co; uv.data[li].uv = (co.x * 4 + co.y * 2, co.z * 4)
    context['skin_to_body'](vest)
    solid = vest.modifiers.new('Cotton thickness', 'SOLIDIFY'); solid.thickness = .0015
    sub = vest.modifiers.new('Soft garment edges', 'SUBSURF'); sub.levels = 1; sub.render_levels = 1
    rig.data.pose_position = 'POSE'; bpy.context.view_layer.update()
    soft = gamcha.modifiers.new('Soft cotton drape', 'SUBSURF'); soft.levels = 1; soft.render_levels = 2
    # Remove the oversized rolled hem: a sewn cloth edge is thin.
    hem = bpy.data.objects.get('Lungi_hem')
    if hem:
        hem.hide_render = True; hem.hide_viewport = True
    # Short compact hair clumps; avoid long spiky silhouette and a shiny hair cap.
    haircards = bpy.data.objects.get('HairCards')
    if haircards:
        for offset in range(0, len(haircards.data.vertices), 8):
            root = (haircards.data.vertices[offset].co + haircards.data.vertices[offset + 1].co) * .5
            for k in range(8):
                v = haircards.data.vertices[offset + k]
                v.co = root + (v.co - root) * .63
    for obj in bpy.data.objects:
        if obj.type != 'MESH': continue
        for mat in obj.data.materials:
            if not mat or not mat.use_nodes: continue
            bs = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
            if not bs: continue
            if 'low-poly' in obj.name:
                bs.inputs['Roughness'].default_value = .24
                if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = .12
                if 'Specular IOR Level' in bs.inputs: bs.inputs['Specular IOR Level'].default_value = .22
            if 'short02' in obj.name or obj.name == 'HairCards':
                bs.inputs['Roughness'].default_value = .68
                if 'Coat Weight' in bs.inputs: bs.inputs['Coat Weight'].default_value = 0
    # Small rest-space cloth wrinkles preserve the existing rig and garment silhouette.
    for obj, strength in ((vest, .0035), (gamcha, .003)):
        edges = {}
        for poly in obj.data.polygons:
            for edge in poly.edge_keys: edges[edge] = edges.get(edge, 0) + 1
        border = {i for edge, count in edges.items() if count == 1 for i in edge}
        for v in obj.data.vertices:
            p = v.co
            wave = math.sin(p.z * 84 + p.x * 15) * math.sin(p.x * 37 + p.y * 23)
            if v.index not in border: p += v.normal * (strength * wave)
        obj.data.update()
    for mat in body.data.materials:
        if not mat or not mat.use_nodes: continue
        nt = mat.node_tree
        bs = next((n for n in nt.nodes if n.type == 'BSDF_PRINCIPLED'), None)
        if not bs: continue
        tex = nt.nodes.new('ShaderNodeTexCoord')
        noise = nt.nodes.new('ShaderNodeTexNoise'); noise.name = 'V4 fine skin relief'
        noise.inputs['Scale'].default_value = 720 / height
        noise.inputs['Detail'].default_value = 2
        nt.links.new(tex.outputs['Object'], noise.inputs['Vector'])
        variation = nt.nodes.new('ShaderNodeTexNoise'); variation.name = 'V4 subtle skin tone variation'
        variation.inputs['Scale'].default_value = 95 / height
        variation.inputs['Detail'].default_value = 3
        nt.links.new(tex.outputs['Object'], variation.inputs['Vector'])
        ramp = nt.nodes.new('ShaderNodeValToRGB')
        ramp.color_ramp.elements[0].color = (.76, .72, .68, 1)
        ramp.color_ramp.elements[1].color = (1, 1, 1, 1)
        nt.links.new(variation.outputs['Fac'], ramp.inputs['Fac'])
        if bs.inputs['Base Color'].is_linked:
            previous = bs.inputs['Base Color'].links[0].from_socket
            mix = nt.nodes.new('ShaderNodeMixRGB'); mix.blend_type = 'MULTIPLY'; mix.inputs[0].default_value = .65
            nt.links.new(previous, mix.inputs[1]); nt.links.new(ramp.outputs['Color'], mix.inputs[2])
            nt.links.new(mix.outputs['Color'], bs.inputs['Base Color'])
        bump = nt.nodes.new('ShaderNodeBump'); bump.name = 'V4 restrained pores'
        bump.inputs['Strength'].default_value = .18
        bump.inputs['Distance'].default_value = .00018
        nt.links.new(noise.outputs['Fac'], bump.inputs['Height'])
        if bs.inputs['Normal'].is_linked:
            nt.links.new(bs.inputs['Normal'].links[0].from_socket, bump.inputs['Normal'])
        nt.links.new(bump.outputs['Normal'], bs.inputs['Normal'])
        if 'Subsurface Weight' in bs.inputs: bs.inputs['Subsurface Weight'].default_value = .055
    # Off-white ground and red checks match the concept instead of a solid red towel.
    mat = gamcha.data.materials[0]
    image = next(n.image for n in mat.node_tree.nodes if n.type == 'TEX_IMAGE')
    n = 512
    y, x = np.mgrid[:n, :n] / n
    line = ((x % .25) < .027) | ((y % .25) < .027)
    pixels = np.ones((n, n, 4), dtype=np.float32)
    pixels[..., :3] = np.where(line[..., None], [.52, .055, .065], [.79, .76, .68])
    weave = (np.sin(x * n * math.pi) * np.sin(y * n * math.pi) * .015)[..., None]
    pixels[..., :3] = np.clip(pixels[..., :3] + weave, 0, 1)
    image.scale(n, n); image.pixels.foreach_set(pixels.ravel()); image.pack()
    print('BABLU_V4_DESIGN: leaner teenage build; refined face; longer lungi; textured cotton; fuller hair; restrained skin relief', flush=True)
