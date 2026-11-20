"""
build_avatar.py — Procedural Blender 5.1 script to model, texture, rig, and animate
the stylized 3D avatar of Syed Muhammad Ahmad (AKKA).

Run headless:
  "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python blender\build_avatar.py

Outputs:
  - blender/avatar.blend
  - public/models/avatar.glb
  - blender/avatar_preview.png
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Euler

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BLEND_PATH = os.path.join(ROOT_DIR, "blender", "avatar.blend")
GLB_PATH = os.path.join(ROOT_DIR, "public", "models", "avatar.glb")
PREVIEW_PATH = os.path.join(ROOT_DIR, "blender", "avatar_preview.png")

os.makedirs(os.path.dirname(BLEND_PATH), exist_ok=True)
os.makedirs(os.path.dirname(GLB_PATH), exist_ok=True)

# ---------------------------------------------------------------------------
# 1. Clear scene
# ---------------------------------------------------------------------------
bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.render.fps = 30

# ---------------------------------------------------------------------------
# 2. Materials (Principled BSDF — glTF compatible)
# ---------------------------------------------------------------------------
def make_mat(name, base_color, roughness=0.5, metallic=0.0, emission=None, emission_strength=0.0):
    mat = bpy.data.materials.new(name=name)
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if not bsdf:
        bsdf = mat.node_tree.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (*base_color, 1.0)
    bsdf.inputs["Roughness"].default_value = roughness
    bsdf.inputs["Metallic"].default_value = metallic
    if emission is not None and "Emission Color" in bsdf.inputs:
        bsdf.inputs["Emission Color"].default_value = (*emission, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission_strength
    return mat

MAT_SKIN = make_mat("Skin", (0.58, 0.37, 0.25), roughness=0.48)
MAT_STUBBLE = make_mat("Stubble", (0.11, 0.08, 0.07), roughness=0.72)
MAT_HAIR = make_mat("Hair", (0.025, 0.025, 0.032), roughness=0.38)
MAT_EYE_WHITE = make_mat("EyeWhite", (0.96, 0.96, 0.98), roughness=0.12)
MAT_IRIS = make_mat("Iris", (0.14, 0.07, 0.03), roughness=0.10)
MAT_PUPIL = make_mat("Pupil", (0.01, 0.01, 0.01), roughness=0.05)
MAT_HIGHLIGHT = make_mat("EyeHighlight", (1.0, 1.0, 1.0), roughness=0.05, emission=(1.0, 1.0, 1.0), emission_strength=1.5)
MAT_LIPS = make_mat("Lips", (0.44, 0.24, 0.22), roughness=0.45)

# Olive-charcoal leather biker jacket + black inner shirt + dark jeans
MAT_JACKET = make_mat("BikerJacket", (0.12, 0.14, 0.13), roughness=0.34, metallic=0.22)
MAT_SHIRT = make_mat("BlackShirt", (0.03, 0.03, 0.04), roughness=0.68)
MAT_PANTS = make_mat("DarkJeans", (0.05, 0.06, 0.09), roughness=0.68)
MAT_SHOE = make_mat("Sneakers", (0.08, 0.08, 0.10), roughness=0.42)
MAT_SOLE = make_mat("SneakerSole", (0.90, 0.92, 0.95), roughness=0.48)
MAT_GLASSES = make_mat("GlassesFrame", (0.04, 0.04, 0.05), roughness=0.18, metallic=0.85)
MAT_CYAN = make_mat("NeonCyan", (0.0, 0.90, 1.0), roughness=0.2, emission=(0.0, 0.90, 1.0), emission_strength=3.5)
MAT_MAGENTA = make_mat("NeonMagenta", (1.0, 0.17, 0.84), roughness=0.2, emission=(1.0, 0.17, 0.84), emission_strength=3.0)

# ---------------------------------------------------------------------------
# 3. Helper geometry builders (character faces -Y in Blender => +Z in glTF)
#    All limb cylinders have capped ends rounded into smooth capsules!
# ---------------------------------------------------------------------------
def add_uv_sphere(name, radius, loc, scale=(1, 1, 1), rot=(0, 0, 0), segments=28, rings=18, mat=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=radius, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_capsule_limb(name, r_bottom, r_top, length, loc, rot=(0, 0, 0), scale=(1, 1, 1), mat=None):
    """Smooth tapered limb using a subdivided cylinder with rounded bevelled caps."""
    bpy.ops.mesh.primitive_cone_add(
        vertices=24,
        radius1=r_bottom,
        radius2=r_top,
        depth=length,
        location=loc,
        rotation=rot,
    )
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = scale
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = min(r_bottom, r_top) * 0.45
    bev.segments = 4
    bpy.ops.object.modifier_apply(modifier=bev.name)
    sub = obj.modifiers.new("Subsurf", "SUBSURF")
    sub.levels = 1
    sub.render_levels = 1
    bpy.ops.object.modifier_apply(modifier=sub.name)
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

def add_round_box(name, size, loc, rot=(0, 0, 0), bevel=0.025, subsurf=1, mat=None):
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    obj = bpy.context.active_object
    obj.name = name
    obj.scale = size
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True)
    bev = obj.modifiers.new("Bevel", "BEVEL")
    bev.width = bevel
    bev.segments = 3
    bpy.ops.object.modifier_apply(modifier=bev.name)
    if subsurf > 0:
        sub = obj.modifiers.new("Subsurf", "SUBSURF")
        sub.levels = subsurf
        sub.render_levels = subsurf
        bpy.ops.object.modifier_apply(modifier=sub.name)
    bpy.ops.object.shade_smooth()
    if mat:
        obj.data.materials.append(mat)
    return obj

parts = []

# ---------------------------------------------------------------------------
# 4. Legs & Sneakers (0.00 m -> 0.86 m)
# ---------------------------------------------------------------------------
for side, sx in [("L", 1), ("R", -1)]:
    x = sx * 0.105
    sole = add_round_box(f"Sole.{side}", (0.105, 0.25, 0.032), (x, -0.035, 0.016), bevel=0.01, mat=MAT_SOLE)
    parts.append((sole, f"Foot.{side}"))
    heel = add_round_box(f"HeelGlow.{side}", (0.108, 0.075, 0.012), (x, 0.048, 0.026), bevel=0.003, subsurf=0, mat=MAT_MAGENTA)
    parts.append((heel, f"Foot.{side}"))
    shoe = add_round_box(f"Shoe.{side}", (0.10, 0.23, 0.082), (x, -0.03, 0.068), bevel=0.028, mat=MAT_SHOE)
    parts.append((shoe, f"Foot.{side}"))
    tongue_glow = add_round_box(f"ShoeCyan.{side}", (0.045, 0.02, 0.035), (x, -0.095, 0.095), rot=(0.35, 0, 0), bevel=0.004, subsurf=0, mat=MAT_CYAN)
    parts.append((tongue_glow, f"Foot.{side}"))

    # Smooth overlapping capsule limbs (no sharp seam between shin & thigh)
    shin = add_capsule_limb(f"LowerLegMesh.{side}", 0.056, 0.068, 0.42, (x, 0.0, 0.27), scale=(1.0, 1.05, 1.0), mat=MAT_PANTS)
    parts.append((shin, f"LowerLeg.{side}"))

    thigh = add_capsule_limb(f"UpperLegMesh.{side}", 0.068, 0.086, 0.42, (x, 0.0, 0.64), scale=(1.04, 1.06, 1.0), mat=MAT_PANTS)
    parts.append((thigh, f"UpperLeg.{side}"))

# Pelvis / Hips
pelvis = add_round_box("Pelvis", (0.31, 0.20, 0.17), (0.0, 0.0, 0.84), bevel=0.055, mat=MAT_PANTS)
parts.append((pelvis, "Hips"))

belt = add_round_box("Belt", (0.315, 0.205, 0.032), (0.0, 0.0, 0.905), bevel=0.008, subsurf=0, mat=MAT_SHOE)
parts.append((belt, "Hips"))
buckle = add_round_box("BeltBuckle", (0.058, 0.022, 0.036), (0.0, -0.102, 0.905), bevel=0.004, subsurf=0, mat=MAT_CYAN)
parts.append((buckle, "Hips"))

# ---------------------------------------------------------------------------
# 5. Torso: Black Shirt + Olive Biker Leather Jacket (0.88 m -> 1.38 m)
# ---------------------------------------------------------------------------
# Inner black shirt visible down the center V-opening
shirt_torso = add_capsule_limb("ShirtTorso", 0.125, 0.148, 0.45, (0.0, -0.012, 1.13), scale=(1.12, 0.78, 1.0), mat=MAT_SHIRT)
parts.append((shirt_torso, "Chest"))

# Outer Biker Jacket with open front channel so the black shirt shows clearly
jacket_shell = add_capsule_limb("JacketShell", 0.142, 0.172, 0.47, (0.0, 0.004, 1.14), scale=(1.18, 0.84, 1.0), mat=MAT_JACKET)
# Carve front V-opening on JacketShell
bm = bmesh.new()
bm.from_mesh(jacket_shell.data)
for v in bm.verts:
    if v.co.y < -0.06 and abs(v.co.x) < 0.052:
        # Push center-front vertices inward so the black inner shirt is visible
        v.co.y += 0.035
bm.to_mesh(jacket_shell.data)
bm.free()
parts.append((jacket_shell, "Chest"))

# Left & right biker jacket lapels + glowing cyan zipper trim + shoulder pads
for side, sx in [("L", 1), ("R", -1)]:
    lapel = add_round_box(
        f"JacketLapel.{side}",
        (0.088, 0.045, 0.42),
        (sx * 0.092, -0.104, 1.14),
        rot=(0.0, sx * 0.03, -sx * 0.08),
        bevel=0.016,
        mat=MAT_JACKET,
    )
    parts.append((lapel, "Chest"))

    pipe = add_round_box(
        f"JacketCyanPipe.{side}",
        (0.009, 0.012, 0.40),
        (sx * 0.048, -0.124, 1.14),
        bevel=0.003,
        subsurf=0,
        mat=MAT_CYAN,
    )
    parts.append((pipe, "Chest"))

    sh_pad = add_uv_sphere(
        f"ShoulderPad.{side}",
        0.076,
        (sx * 0.20, 0.0, 1.32),
        scale=(1.08, 0.96, 0.78),
        mat=MAT_JACKET,
    )
    parts.append((sh_pad, f"Shoulder.{side}"))

# Stand-up biker jacket collar with cyan neon rim
collar = add_capsule_limb("JacketCollar", 0.082, 0.088, 0.075, (0.0, 0.004, 1.375), scale=(1.08, 0.95, 1.0), mat=MAT_JACKET)
parts.append((collar, "Neck"))
collar_glow = add_round_box("CollarCyanTrim", (0.175, 0.16, 0.010), (0.0, 0.004, 1.404), bevel=0.004, subsurf=0, mat=MAT_CYAN)
parts.append((collar_glow, "Neck"))

# ---------------------------------------------------------------------------
# 6. Arms & Hands (Smooth Capsule Sleeves, Natural Relaxed Pose)
# ---------------------------------------------------------------------------
for side, sx in [("L", 1), ("R", -1)]:
    u_arm = add_capsule_limb(
        f"UpperArmMesh.{side}",
        0.052,
        0.064,
        0.29,
        (sx * 0.228, 0.0, 1.195),
        rot=(0.0, sx * 0.14, 0.0),
        mat=MAT_JACKET,
    )
    parts.append((u_arm, f"UpperArm.{side}"))

    # Smooth elbow sphere bridging upper and lower arm
    elbow = add_uv_sphere(f"Elbow.{side}", 0.052, (sx * 0.248, -0.004, 1.072), mat=MAT_JACKET)
    parts.append((elbow, f"LowerArm.{side}"))

    l_arm = add_capsule_limb(
        f"LowerArmMesh.{side}",
        0.043,
        0.052,
        0.25,
        (sx * 0.258, -0.015, 0.960),
        rot=(0.08, sx * 0.06, 0.0),
        mat=MAT_JACKET,
    )
    parts.append((l_arm, f"LowerArm.{side}"))

    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.045,
        minor_radius=0.006,
        location=(sx * 0.265, -0.024, 0.842),
        rotation=(0.08, sx * 0.06, 0.0),
    )
    cuff = bpy.context.active_object
    cuff.name = f"CuffGlow.{side}"
    bpy.ops.object.shade_smooth()
    cuff.data.materials.append(MAT_CYAN if side == "L" else MAT_MAGENTA)
    parts.append((cuff, f"LowerArm.{side}"))

    hand = add_round_box(
        f"HandMesh.{side}",
        (0.044, 0.064, 0.085),
        (sx * 0.270, -0.032, 0.790),
        rot=(0.08, sx * 0.05, 0.0),
        bevel=0.016,
        mat=MAT_SKIN,
    )
    parts.append((hand, f"Hand.{side}"))

    thumb = add_round_box(
        f"Thumb.{side}",
        (0.020, 0.024, 0.044),
        (sx * 0.248, -0.060, 0.795),
        rot=(0.3, -sx * 0.25, 0.0),
        bevel=0.008,
        mat=MAT_SKIN,
    )
    parts.append((thumb, f"Hand.{side}"))

# ---------------------------------------------------------------------------
# 7. Neck, Multi-Material Head (Clean Stubble!), Facial Features & Hair
# ---------------------------------------------------------------------------
neck = add_capsule_limb("NeckMesh", 0.056, 0.062, 0.11, (0.0, -0.005, 1.41), mat=MAT_SKIN)
parts.append((neck, "Neck"))

# Stylized head with two material slots on the SAME mesh:
#   Slot 0 = MAT_SKIN
#   Slot 1 = MAT_STUBBLE (assigned cleanly to lower-jaw / chin / cheek-line faces -> zero Z-fighting!)
bpy.ops.mesh.primitive_uv_sphere_add(segments=48, ring_count=32, radius=0.125, location=(0.0, -0.01, 1.548))
head = bpy.context.active_object
head.name = "HeadMesh"
head.scale = (0.93, 1.02, 1.13)
bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

head.data.materials.append(MAT_SKIN)
head.data.materials.append(MAT_STUBBLE)

bm = bmesh.new()
bm.from_mesh(head.data)
for v in bm.verts:
    dz = v.co.z - 1.548
    if dz < 0:
        taper = 1.0 + 0.22 * (dz / 0.14)
        v.co.x *= max(0.72, taper)
    if dz < -0.08 and v.co.y < 0:
        v.co.y -= 0.008

# Assign clean symmetrical jawline beard / stubble to polygons on lower jaw & sideburns
for f in bm.faces:
    c = f.calc_center_median()
    if c.y < 0.010:
        is_sideburn = abs(c.x) > 0.084 and 1.490 < c.z < 1.552 and c.y < -0.015
        is_jaw_chin = 1.410 < c.z < 1.482 and c.y < -0.020
        is_cheek_low = 1.480 <= c.z < 1.500 and abs(c.x) > 0.052 and c.y < -0.030
        if is_sideburn or is_jaw_chin or is_cheek_low:
            f.material_index = 1
        else:
            f.material_index = 0

bm.to_mesh(head.data)
bm.free()
bpy.ops.object.shade_smooth()

# Shape keys on HeadMesh (Blink, Smile, MouthOpen)
sk_basis = head.shape_key_add(name="Basis")
sk_blink = head.shape_key_add(name="Blink")
sk_smile = head.shape_key_add(name="Smile")
sk_mouth = head.shape_key_add(name="MouthOpen")

for i, v in enumerate(head.data.vertices):
    co = v.co
    if abs(abs(co.x) - 0.043) < 0.032 and abs(co.z - 1.558) < 0.028 and co.y < -0.07:
        sk_blink.data[i].co.z = 1.552
        sk_blink.data[i].co.y -= 0.006
    if abs(co.x) < 0.055 and abs(co.z - 1.485) < 0.035 and co.y < -0.07:
        corner = min(1.0, abs(co.x) / 0.045)
        sk_smile.data[i].co.z += 0.012 * corner
        sk_smile.data[i].co.x *= 1.0 + 0.10 * corner
        if co.z < 1.486:
            sk_mouth.data[i].co.z -= 0.018 * (1.0 - corner * 0.5)

parts.append((head, "Head"))

# Ears
for side, sx in [("L", 1), ("R", -1)]:
    ear = add_uv_sphere(f"Ear.{side}", 0.025, (sx * 0.114, 0.005, 1.542), scale=(0.45, 0.65, 1.15), mat=MAT_SKIN)
    parts.append((ear, "Head"))

# Well-proportioned nose bridge & tip (protruding clearly at y = -0.136)
nose = add_uv_sphere("Nose", 0.017, (0.0, -0.128, 1.534), scale=(0.82, 1.05, 1.38), rot=(0.18, 0.0, 0.0), mat=MAT_SKIN)
parts.append((nose, "Head"))

# Expressive Eyes (sclera, dark brown iris, black pupil, crisp white catchlight, eyebrows)
for side, sx in [("L", 1), ("R", -1)]:
    ex = sx * 0.042
    ey = -0.121
    ez = 1.558
    sclera = add_uv_sphere(f"Eye.{side}", 0.018, (ex, ey, ez), scale=(1.08, 0.55, 0.92), mat=MAT_EYE_WHITE)
    parts.append((sclera, "Head"))
    iris = add_uv_sphere(f"Iris.{side}", 0.0105, (ex, ey - 0.008, ez), scale=(1.0, 0.35, 1.0), mat=MAT_IRIS)
    parts.append((iris, "Head"))
    pupil = add_uv_sphere(f"Pupil.{side}", 0.0055, (ex, ey - 0.0105, ez), scale=(1.0, 0.30, 1.0), mat=MAT_PUPIL)
    parts.append((pupil, "Head"))
    catchlight = add_uv_sphere(f"EyeHighlight.{side}", 0.0024, (ex + 0.0035, ey - 0.012, ez + 0.0035), mat=MAT_HIGHLIGHT)
    parts.append((catchlight, "Head"))

    # Upper eyelid crease
    lid = add_uv_sphere(
        f"UpperLid.{side}",
        0.019,
        (ex, ey - 0.004, ez + 0.010),
        scale=(1.05, 0.50, 0.25),
        rot=(0.0, -sx * 0.04, 0.0),
        mat=MAT_HAIR,
    )
    parts.append((lid, "Head"))

    # Thick dark eyebrows
    brow = add_uv_sphere(
        f"Eyebrow.{side}",
        0.022,
        (ex, ey - 0.010, ez + 0.026),
        scale=(1.05, 0.45, 0.26),
        rot=(0.0, -sx * 0.08, sx * 0.05),
        mat=MAT_HAIR,
    )
    parts.append((brow, "Head"))

# Distinct Moustache & Lips + Soul-patch (protruding clearly in front of head surface)
for side, sx in [("L", 1), ("R", -1)]:
    stache_half = add_uv_sphere(
        f"Moustache.{side}",
        0.022,
        (sx * 0.015, -0.123, 1.503),
        scale=(1.25, 0.65, 0.38),
        rot=(0.0, sx * 0.16, -sx * 0.08),
        mat=MAT_STUBBLE,
    )
    parts.append((stache_half, "Head"))

lips = add_uv_sphere(
    "Lips",
    0.024,
    (0.0, -0.122, 1.488),
    scale=(1.15, 0.60, 0.36),
    mat=MAT_LIPS,
)
parts.append((lips, "Head"))

soul_patch = add_uv_sphere(
    "SoulPatch",
    0.011,
    (0.0, -0.119, 1.472),
    scale=(0.95, 0.65, 1.0),
    mat=MAT_STUBBLE,
)
parts.append((soul_patch, "Head"))

# Sleek dark glasses frames (with temples going back to ears)
for side, sx in [("L", 1), ("R", -1)]:
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.024,
        minor_radius=0.0026,
        location=(sx * 0.042, -0.132, 1.558),
        rotation=(math.pi / 2, 0.0, 0.0),
    )
    rim = bpy.context.active_object
    rim.name = f"GlassesRim.{side}"
    rim.scale = (1.12, 1.0, 0.92)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    bpy.ops.object.shade_smooth()
    rim.data.materials.append(MAT_GLASSES)
    parts.append((rim, "Head"))

    temple = add_round_box(
        f"GlassesTemple.{side}",
        (0.004, 0.115, 0.004),
        (sx * 0.072, -0.070, 1.560),
        rot=(0.0, 0.0, -sx * 0.32),
        bevel=0.001,
        subsurf=0,
        mat=MAT_GLASSES,
    )
    parts.append((temple, "Head"))

bridge = add_round_box("GlassesBridge", (0.020, 0.004, 0.004), (0.0, -0.133, 1.562), bevel=0.001, subsurf=0, mat=MAT_GLASSES)
parts.append((bridge, "Head"))

# Signature Swept-Up Voluminous Dark Hair (smooth organic sculpted locks)
hair_cap = add_uv_sphere("HairCap", 0.133, (0.0, 0.008, 1.580), scale=(0.98, 1.05, 1.04), mat=MAT_HAIR)
bm = bmesh.new()
bm.from_mesh(hair_cap.data)
to_del = [v for v in bm.verts if v.co.z < 1.540 and v.co.y < -0.015]
bmesh.ops.delete(bm, geom=to_del, context="VERTS")
bm.to_mesh(hair_cap.data)
bm.free()
parts.append((hair_cap, "Head"))

lock_specs = [
    ("HairSweepCenter", (0.00, -0.070, 1.676), (0.082, 0.105, 0.046), (0.22, -0.14, 0.08)),
    ("HairSweepLeft1", (0.048, -0.062, 1.668), (0.074, 0.098, 0.044), (0.18, 0.22, -0.18)),
    ("HairSweepLeft2", (0.084, -0.038, 1.645), (0.058, 0.090, 0.042), (0.12, 0.38, -0.22)),
    ("HairSweepRight1", (-0.048, -0.060, 1.664), (0.072, 0.096, 0.042), (0.16, -0.24, 0.18)),
    ("HairSweepRight2", (-0.084, -0.036, 1.642), (0.056, 0.088, 0.040), (0.12, -0.40, 0.22)),
    ("HairCrownTop", (0.00, 0.005, 1.688), (0.102, 0.112, 0.046), (-0.06, 0.05, 0.0)),
    ("HairSideTemple.L", (0.106, -0.022, 1.602), (0.036, 0.078, 0.055), (0.08, 0.30, -0.10)),
    ("HairSideTemple.R", (-0.106, -0.022, 1.600), (0.036, 0.078, 0.055), (0.08, -0.30, 0.10)),
]
for hname, hloc, hscale, hrot in lock_specs:
    lock = add_uv_sphere(hname, 1.0, hloc, scale=hscale, rot=hrot, segments=32, rings=20, mat=MAT_HAIR)
    parts.append((lock, "Head"))

# ---------------------------------------------------------------------------
# 8. Build Armature & Skin Meshes by Bone Vertex Groups
# ---------------------------------------------------------------------------
arm_data = bpy.data.armatures.new("AvatarArmature")
arm_obj = bpy.data.objects.new("AvatarRig", arm_data)
scene.collection.objects.link(arm_obj)
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="EDIT")

eb = arm_data.edit_bones

def make_bone(name, head_pos, tail_pos, parent=None):
    b = eb.new(name)
    b.head = Vector(head_pos)
    b.tail = Vector(tail_pos)
    if parent:
        b.parent = parent
    return b

b_root = make_bone("Root", (0, 0, 0.0), (0, 0, 0.25))
b_hips = make_bone("Hips", (0, 0, 0.84), (0, 0, 0.96), b_root)
b_spine = make_bone("Spine", (0, 0, 0.96), (0, 0, 1.12), b_hips)
b_chest = make_bone("Chest", (0, 0, 1.12), (0, 0, 1.35), b_spine)
b_neck = make_bone("Neck", (0, 0, 1.35), (0, 0, 1.45), b_chest)
b_head = make_bone("Head", (0, 0, 1.45), (0, 0, 1.72), b_neck)

for side, sx in [("L", 1), ("R", -1)]:
    b_sh = make_bone(f"Shoulder.{side}", (sx * 0.08, 0, 1.32), (sx * 0.20, 0, 1.32), b_chest)
    b_ua = make_bone(f"UpperArm.{side}", (sx * 0.20, 0, 1.32), (sx * 0.258, 0, 1.07), b_sh)
    b_la = make_bone(f"LowerArm.{side}", (sx * 0.258, 0, 1.07), (sx * 0.288, -0.025, 0.84), b_ua)
    make_bone(f"Hand.{side}", (sx * 0.288, -0.025, 0.84), (sx * 0.305, -0.04, 0.74), b_la)

    b_ul = make_bone(f"UpperLeg.{side}", (sx * 0.105, 0, 0.84), (sx * 0.105, 0, 0.46), b_hips)
    b_ll = make_bone(f"LowerLeg.{side}", (sx * 0.105, 0, 0.46), (sx * 0.105, 0, 0.08), b_ul)
    make_bone(f"Foot.{side}", (sx * 0.105, 0, 0.08), (sx * 0.105, -0.16, 0.02), b_ll)

bpy.ops.object.mode_set(mode="OBJECT")

for mesh_obj, bone_name in parts:
    vg = mesh_obj.vertex_groups.new(name=bone_name)
    all_verts = [v.index for v in mesh_obj.data.vertices]
    vg.add(all_verts, 1.0, "REPLACE")
    mesh_obj.parent = arm_obj
    mod = mesh_obj.modifiers.new(name="Armature", type="ARMATURE")
    mod.object = arm_obj

# ---------------------------------------------------------------------------
# 9. Animations (Idle, Wave, Talk, Point, Victory) pushed to NLA tracks
# ---------------------------------------------------------------------------
bpy.context.view_layer.objects.active = arm_obj
bpy.ops.object.mode_set(mode="POSE")

for pb in arm_obj.pose.bones:
    pb.rotation_mode = "XYZ"

def reset_pose():
    for pb in arm_obj.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)

def key_bones(action_name, keyframes, total_frames):
    action = bpy.data.actions.new(name=action_name)
    action.use_fake_user = True
    if not arm_obj.animation_data:
        arm_obj.animation_data_create()
    arm_obj.animation_data.action = action
    reset_pose()

    touched = set(["Hips", "Chest", "Head", "UpperArm.L", "LowerArm.L", "UpperArm.R", "LowerArm.R"])
    for _, pose_dict in keyframes:
        touched.update(pose_dict.keys())

    for frame, pose_dict in keyframes:
        scene.frame_set(frame)
        reset_pose()
        for bname, transforms in pose_dict.items():
            pb = arm_obj.pose.bones[bname]
            if "rot" in transforms:
                pb.rotation_euler = Euler(transforms["rot"], "XYZ")
            if "loc" in transforms:
                pb.location = Vector(transforms["loc"])
        for bname in touched:
            pb = arm_obj.pose.bones[bname]
            pb.keyframe_insert(data_path="rotation_euler", frame=frame)
            pb.keyframe_insert(data_path="location", frame=frame)

    track = arm_obj.animation_data.nla_tracks.new()
    track.name = action_name
    strip = track.strips.new(action_name, 1, action)
    strip.frame_end = total_frames
    track.mute = False
    arm_obj.animation_data.action = None

key_bones("Idle", [
    (1, {
        "Hips": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
        "Chest": {"rot": (0.02, 0, 0)},
        "Head": {"rot": (0.0, 0.0, 0.0)},
        "UpperArm.L": {"rot": (0.04, 0, -0.05)},
        "UpperArm.R": {"rot": (0.04, 0, 0.05)},
    }),
    (60, {
        "Hips": {"loc": (0, 0, 0.012), "rot": (0, 0.015, 0.02)},
        "Chest": {"rot": (-0.03, 0, -0.015)},
        "Head": {"rot": (-0.03, 0.02, 0.05)},
        "UpperArm.L": {"rot": (-0.02, 0, -0.08)},
        "UpperArm.R": {"rot": (-0.02, 0, 0.08)},
    }),
    (120, {
        "Hips": {"loc": (0, 0, 0), "rot": (0, 0, 0)},
        "Chest": {"rot": (0.02, 0, 0)},
        "Head": {"rot": (0.0, 0.0, 0.0)},
        "UpperArm.L": {"rot": (0.04, 0, -0.05)},
        "UpperArm.R": {"rot": (0.04, 0, 0.05)},
    }),
], 120)

key_bones("Wave", [
    (1, {"UpperArm.R": {"rot": (0, 0, 0)}, "LowerArm.R": {"rot": (0, 0, 0)}, "Head": {"rot": (0, 0, 0)}}),
    (18, {"UpperArm.R": {"rot": (0.9, -1.1, 0.4)}, "LowerArm.R": {"rot": (0.8, 0, 0.35)}, "Head": {"rot": (-0.05, -0.08, -0.06)}}),
    (30, {"UpperArm.R": {"rot": (0.9, -1.1, 0.4)}, "LowerArm.R": {"rot": (0.8, 0, -0.35)}, "Head": {"rot": (-0.05, -0.08, 0.04)}}),
    (42, {"UpperArm.R": {"rot": (0.9, -1.1, 0.4)}, "LowerArm.R": {"rot": (0.8, 0, 0.35)}, "Head": {"rot": (-0.05, -0.08, -0.06)}}),
    (55, {"UpperArm.R": {"rot": (0.9, -1.1, 0.4)}, "LowerArm.R": {"rot": (0.8, 0, -0.30)}, "Head": {"rot": (-0.05, -0.08, 0.02)}}),
    (75, {"UpperArm.R": {"rot": (0, 0, 0)}, "LowerArm.R": {"rot": (0, 0, 0)}, "Head": {"rot": (0, 0, 0)}}),
], 75)

key_bones("Talk", [
    (1, {"Head": {"rot": (0, 0, 0)}, "UpperArm.L": {"rot": (0.25, 0.1, -0.1)}, "LowerArm.L": {"rot": (0.6, 0, 0)}, "UpperArm.R": {"rot": (0.2, -0.1, 0.1)}, "LowerArm.R": {"rot": (0.5, 0, 0)}}),
    (25, {"Head": {"rot": (0.08, 0.04, 0.05)}, "UpperArm.L": {"rot": (0.45, 0.2, -0.15)}, "LowerArm.L": {"rot": (0.9, 0, -0.2)}, "UpperArm.R": {"rot": (0.3, -0.1, 0.1)}, "LowerArm.R": {"rot": (0.65, 0, 0.15)}}),
    (55, {"Head": {"rot": (-0.05, -0.04, -0.06)}, "UpperArm.L": {"rot": (0.3, 0.1, -0.1)}, "LowerArm.L": {"rot": (0.65, 0, 0.1)}, "UpperArm.R": {"rot": (0.5, -0.2, 0.15)}, "LowerArm.R": {"rot": (0.95, 0, 0.25)}}),
    (90, {"Head": {"rot": (0, 0, 0)}, "UpperArm.L": {"rot": (0.25, 0.1, -0.1)}, "LowerArm.L": {"rot": (0.6, 0, 0)}, "UpperArm.R": {"rot": (0.2, -0.1, 0.1)}, "LowerArm.R": {"rot": (0.5, 0, 0)}}),
], 90)

key_bones("Point", [
    (1, {"UpperArm.L": {"rot": (0, 0, 0)}, "LowerArm.L": {"rot": (0, 0, 0)}, "Head": {"rot": (0, 0, 0)}, "Chest": {"rot": (0, 0, 0)}}),
    (20, {"UpperArm.L": {"rot": (0.65, 0.85, -0.2)}, "LowerArm.L": {"rot": (0.35, 0, -0.25)}, "Head": {"rot": (-0.04, 0.05, 0.18)}, "Chest": {"rot": (0, 0, 0.10)}}),
    (42, {"UpperArm.L": {"rot": (0.68, 0.88, -0.2)}, "LowerArm.L": {"rot": (0.38, 0, -0.25)}, "Head": {"rot": (-0.02, 0.05, 0.20)}, "Chest": {"rot": (0, 0, 0.10)}}),
    (60, {"UpperArm.L": {"rot": (0, 0, 0)}, "LowerArm.L": {"rot": (0, 0, 0)}, "Head": {"rot": (0, 0, 0)}, "Chest": {"rot": (0, 0, 0)}}),
], 60)

key_bones("Victory", [
    (1, {"UpperArm.L": {"rot": (0, 0, 0)}, "UpperArm.R": {"rot": (0, 0, 0)}, "LowerArm.L": {"rot": (0, 0, 0)}, "LowerArm.R": {"rot": (0, 0, 0)}, "Hips": {"loc": (0, 0, 0)}}),
    (18, {"UpperArm.L": {"rot": (1.1, 1.15, 0)}, "UpperArm.R": {"rot": (1.1, -1.15, 0)}, "LowerArm.L": {"rot": (0.85, 0, 0)}, "LowerArm.R": {"rot": (0.85, 0, 0)}, "Hips": {"loc": (0, 0, 0.04)}, "Head": {"rot": (-0.10, 0, 0)}}),
    (36, {"UpperArm.L": {"rot": (1.25, 1.25, 0)}, "UpperArm.R": {"rot": (1.25, -1.25, 0)}, "LowerArm.L": {"rot": (0.65, 0, 0)}, "LowerArm.R": {"rot": (0.65, 0, 0)}, "Hips": {"loc": (0, 0, 0.06)}, "Head": {"rot": (-0.14, 0, 0)}}),
    (60, {"UpperArm.L": {"rot": (0, 0, 0)}, "UpperArm.R": {"rot": (0, 0, 0)}, "LowerArm.L": {"rot": (0, 0, 0)}, "LowerArm.R": {"rot": (0, 0, 0)}, "Hips": {"loc": (0, 0, 0)}, "Head": {"rot": (0, 0, 0)}}),
], 60)

key_bones("Walk", [
    (1, {
        "Hips": {"loc": (0, 0, -0.015), "rot": (0.04, 0, 0.04)},
        "Chest": {"rot": (0.05, 0, -0.06)},
        "Head": {"rot": (-0.02, 0, 0.03)},
        "UpperLeg.L": {"rot": (0.48, 0, 0)},
        "LowerLeg.L": {"rot": (-0.12, 0, 0)},
        "UpperLeg.R": {"rot": (-0.44, 0, 0)},
        "LowerLeg.R": {"rot": (-0.42, 0, 0)},
        "UpperArm.L": {"rot": (-0.36, 0, -0.06)},
        "LowerArm.L": {"rot": (0.32, 0, 0)},
        "UpperArm.R": {"rot": (0.38, 0, 0.06)},
        "LowerArm.R": {"rot": (0.45, 0, 0)},
    }),
    (9, {
        "Hips": {"loc": (0, 0, 0.022), "rot": (0.02, 0, 0.0)},
        "Chest": {"rot": (0.03, 0, 0.0)},
        "Head": {"rot": (0.0, 0, 0.0)},
        "UpperLeg.L": {"rot": (0.05, 0, 0)},
        "LowerLeg.L": {"rot": (-0.05, 0, 0)},
        "UpperLeg.R": {"rot": (0.12, 0, 0)},
        "LowerLeg.R": {"rot": (-0.62, 0, 0)},
        "UpperArm.L": {"rot": (0.0, 0, -0.06)},
        "LowerArm.L": {"rot": (0.28, 0, 0)},
        "UpperArm.R": {"rot": (0.0, 0, 0.06)},
        "LowerArm.R": {"rot": (0.28, 0, 0)},
    }),
    (17, {
        "Hips": {"loc": (0, 0, -0.015), "rot": (0.04, 0, -0.04)},
        "Chest": {"rot": (0.05, 0, 0.06)},
        "Head": {"rot": (-0.02, 0, -0.03)},
        "UpperLeg.L": {"rot": (-0.44, 0, 0)},
        "LowerLeg.L": {"rot": (-0.42, 0, 0)},
        "UpperLeg.R": {"rot": (0.48, 0, 0)},
        "LowerLeg.R": {"rot": (-0.12, 0, 0)},
        "UpperArm.L": {"rot": (0.38, 0, -0.06)},
        "LowerArm.L": {"rot": (0.45, 0, 0)},
        "UpperArm.R": {"rot": (-0.36, 0, 0.06)},
        "LowerArm.R": {"rot": (0.32, 0, 0)},
    }),
    (25, {
        "Hips": {"loc": (0, 0, 0.022), "rot": (0.02, 0, 0.0)},
        "Chest": {"rot": (0.03, 0, 0.0)},
        "Head": {"rot": (0.0, 0, 0.0)},
        "UpperLeg.L": {"rot": (0.12, 0, 0)},
        "LowerLeg.L": {"rot": (-0.62, 0, 0)},
        "UpperLeg.R": {"rot": (0.05, 0, 0)},
        "LowerLeg.R": {"rot": (-0.05, 0, 0)},
        "UpperArm.L": {"rot": (0.0, 0, -0.06)},
        "LowerArm.L": {"rot": (0.28, 0, 0)},
        "UpperArm.R": {"rot": (0.0, 0, 0.06)},
        "LowerArm.R": {"rot": (0.28, 0, 0)},
    }),
    (33, {
        "Hips": {"loc": (0, 0, -0.015), "rot": (0.04, 0, 0.04)},
        "Chest": {"rot": (0.05, 0, -0.06)},
        "Head": {"rot": (-0.02, 0, 0.03)},
        "UpperLeg.L": {"rot": (0.48, 0, 0)},
        "LowerLeg.L": {"rot": (-0.12, 0, 0)},
        "UpperLeg.R": {"rot": (-0.44, 0, 0)},
        "LowerLeg.R": {"rot": (-0.42, 0, 0)},
        "UpperArm.L": {"rot": (-0.36, 0, -0.06)},
        "LowerArm.L": {"rot": (0.32, 0, 0)},
        "UpperArm.R": {"rot": (0.38, 0, 0.06)},
        "LowerArm.R": {"rot": (0.45, 0, 0)},
    }),
], 33)

reset_pose()
scene.frame_set(1)
bpy.ops.object.mode_set(mode="OBJECT")

# ---------------------------------------------------------------------------
# 10. Save .blend and Export GLB
# ---------------------------------------------------------------------------
bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
print(f"Saved Blender file: {BLEND_PATH}")

bpy.ops.export_scene.gltf(
    filepath=GLB_PATH,
    export_format="GLB",
    export_yup=True,
    export_apply=False,
    export_animations=True,
    export_animation_mode="NLA_TRACKS",
    export_morph=True,
    export_skins=True,
    export_cameras=False,
    export_lights=False,
)
print(f"Exported GLB: {GLB_PATH}")

# ---------------------------------------------------------------------------
# 11. Render Preview PNG
# ---------------------------------------------------------------------------
world = bpy.data.worlds.new("PreviewWorld")
scene.world = world
bg_node = world.node_tree.nodes.get("Background")
if bg_node:
    bg_node.inputs[0].default_value = (0.025, 0.03, 0.055, 1.0)
    bg_node.inputs[1].default_value = 1.0

bpy.ops.object.camera_add(location=(0.45, -2.05, 1.26), rotation=(math.radians(84), 0.0, math.radians(12)))
cam = bpy.context.active_object
cam.data.lens = 52
scene.camera = cam

def add_light(name, ltype, energy, color, loc, rot=(0, 0, 0)):
    bpy.ops.object.light_add(type=ltype, location=loc, rotation=rot)
    lt = bpy.context.active_object
    lt.name = name
    lt.data.energy = energy
    lt.data.color = color
    return lt

add_light("KeyLight", "AREA", 135.0, (0.96, 0.97, 1.0), (1.1, -1.8, 2.1), (math.radians(55), 0, math.radians(30)))
add_light("CyanRim", "POINT", 95.0, (0.0, 0.9, 1.0), (-1.1, 0.9, 1.6))
add_light("MagentaRim", "POINT", 85.0, (1.0, 0.18, 0.85), (1.1, 0.8, 1.4))

for eng in ["BLENDER_EEVEE_NEXT", "BLENDER_EEVEE", "CYCLES"]:
    try:
        scene.render.engine = eng
        break
    except Exception:
        pass

scene.render.resolution_x = 1024
scene.render.resolution_y = 1024
scene.render.filepath = PREVIEW_PATH
bpy.ops.render.render(write_still=True)
print(f"Rendered preview: {PREVIEW_PATH}")
