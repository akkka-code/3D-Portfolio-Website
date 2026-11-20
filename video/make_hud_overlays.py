import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT_DIR = "video/overlays"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1920, 1080

CYAN = (0, 229, 255, 255)
MAGENTA = (255, 43, 214, 255)
YELLOW = (252, 238, 10, 255)
GREEN = (0, 255, 157, 255)
WHITE = (245, 250, 255, 255)
MUTED = (165, 188, 214, 255)
DARK_BG = (6, 10, 22, 228)
DARK_CARD = (10, 17, 36, 235)


def get_font(size, bold=True, mono=False):
    candidates = (
        ["C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/consola.ttf"]
        if mono
        else [
            "C:/Windows/Fonts/bahnschrift.ttf",
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ]
    )
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def chamfer_poly(x, y, w, h, cut=22):
    return [
        (x + cut, y),
        (x + w - cut, y),
        (x + w, y + cut),
        (x + w, y + h - cut),
        (x + w - cut, y + h),
        (x + cut, y + h),
        (x, y + h - cut),
        (x, y + cut),
    ]


def draw_chamfer_panel(draw, x, y, w, h, cut=22, fill=DARK_BG, outline=CYAN, width=3, accent=MAGENTA):
    pts = chamfer_poly(x, y, w, h, cut)
    draw.polygon(pts, fill=fill, outline=outline, width=width)
    # Corner accent brackets
    b = cut + 24
    # Top-left & bottom-right glowing accent lines
    draw.line([(x, y + cut + b), (x, y + cut), (x + cut, y), (x + cut + b, y)], fill=accent, width=width + 2)
    draw.line(
        [(x + w, y + h - cut - b), (x + w, y + h - cut), (x + w - cut, y + h), (x + w - cut - b, y + h)],
        fill=accent,
        width=width + 2,
    )


def draw_outer_hud_chrome(draw, top_label="PORTFOLIO SHOWREEL // SYED MUHAMMAD AHMAD [AKKA]", right_label="NED UNIVERSITY · GAMING & ANIMATION"):
    # Sleek angled top HUD bar
    top_pts = [(0, 0), (W, 0), (W, 46), (W - 360, 46), (W - 380, 62), (380, 62), (360, 46), (0, 46)]
    draw.polygon(top_pts, fill=(5, 9, 20, 220))
    draw.line([(0, 46), (360, 46), (380, 62), (W - 380, 62), (W - 360, 46), (W, 46)], fill=CYAN, width=3)

    # Sleek angled bottom HUD bar
    bot_pts = [(0, H), (W, H), (W, H - 44), (W - 420, H - 44), (W - 440, H - 58), (440, H - 58), (420, H - 44), (0, H - 44)]
    draw.polygon(bot_pts, fill=(5, 9, 20, 220))
    draw.line([(0, H - 44), (420, H - 44), (440, H - 58), (W - 440, H - 58), (W - 420, H - 44), (W, H - 44)], fill=MAGENTA, width=3)

    # Corner targeting reticles
    for cx, cy, sx, sy in [(28, 78, 1, 1), (W - 28, 78, -1, 1), (28, H - 74, 1, -1), (W - 28, H - 74, -1, -1)]:
        draw.line([(cx, cy + sy * 34), (cx, cy), (cx + sx * 34, cy)], fill=CYAN, width=3)

    f_mono = get_font(18, mono=True)
    f_center = get_font(19, bold=True)
    draw.text((34, 13), top_label, font=f_mono, fill=CYAN)
    draw.text((W - 34, 13), right_label, font=f_mono, fill=YELLOW, anchor="ra")
    draw.text((W // 2, 18), "[LIVE 1080P] // 60FPS WEBGPU + GAME ENGINE REEL", font=f_center, fill=WHITE, anchor="ma")
    draw.text(
        (W // 2, H - 38),
        "UNITY 3D  ·  UNREAL ENGINE 5  ·  C# / C++ / PYTHON  ·  OPENXR / VUFORIA  ·  BLENDER 5.1  ·  THREE.JS WEBGPU",
        font=f_mono,
        fill=MUTED,
        anchor="ma",
    )


def draw_pills(draw, x, y, tags, border_color=CYAN):
    f_tag = get_font(19, bold=True)
    cur_x = x
    for tag in tags:
        bbox = draw.textbbox((0, 0), tag, font=f_tag)
        tw = bbox[2] - bbox[0] + 30
        th = 40
        pts = chamfer_poly(cur_x, y, tw, th, cut=8)
        draw.polygon(pts, fill=(10, 26, 52, 250), outline=border_color, width=2)
        draw.text((cur_x + 15, y + 9), tag, font=f_tag, fill=WHITE)
        cur_x += tw + 12


def paste_chamfer_image(base_img, img_path, x, y, w, h, cut=24, border_color=CYAN):
    if not os.path.exists(img_path):
        return
    src = Image.open(img_path).convert("RGBA")
    # Crop center aspect
    sw, sh = src.size
    target_aspect = w / h
    src_aspect = sw / sh
    if src_aspect > target_aspect:
        new_w = int(sh * target_aspect)
        left = (sw - new_w) // 2
        src = src.crop((left, 0, left + new_w, sh))
    else:
        new_h = int(sw / target_aspect)
        top = (sh - new_h) // 2
        src = src.crop((0, top, sw, top + new_h))
    src = src.resize((w, h), Image.Resampling.LANCZOS)

    mask = Image.new("L", (w, h), 0)
    mdraw = ImageDraw.Draw(mask)
    mdraw.polygon(chamfer_poly(0, 0, w, h, cut), fill=255)
    base_img.paste(src, (x, y), mask)

    draw = ImageDraw.Draw(base_img)
    draw.polygon(chamfer_poly(x, y, w, h, cut), outline=border_color, width=4)


def build_project_lower_third(filename, num_str, category, title, subtitle, tags, primary=CYAN, accent=MAGENTA):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_outer_hud_chrome(draw)

    # Sleek lower-left angled HUD card (leaves 78% of the 1080p gameplay screen completely clear!)
    px, py, pw, ph = 56, 725, 1360, 265
    draw_chamfer_panel(draw, px, py, pw, ph, cut=22, fill=(6, 11, 24, 236), outline=primary, width=3, accent=accent)

    # Number badge on left
    draw_chamfer_panel(draw, px + 24, py + 24, 96, 86, cut=12, fill=(10, 28, 56, 250), outline=primary, width=2, accent=primary)
    draw.text((px + 72, py + 44), num_str, font=get_font(42, bold=True), fill=primary, anchor="ma")

    # Category + Title + Subtitle
    draw.text((px + 142, py + 24), category, font=get_font(21, mono=True), fill=accent)
    draw.text((px + 142, py + 54), title, font=get_font(52, bold=True), fill=WHITE)
    draw.text((px + 142, py + 122), subtitle, font=get_font(22), fill=MUTED)

    draw_pills(draw, px + 24, py + 196, tags, border_color=primary)

    # Top-right live telemetry crosshair widget
    draw_chamfer_panel(draw, W - 390, 88, 334, 86, cut=14, fill=(6, 11, 24, 228), outline=primary, width=2, accent=accent)
    draw.text((W - 368, 102), "GAMEPLAY FEED // DIRECT CAPTURE", font=get_font(16, mono=True), fill=primary)
    draw.text((W - 368, 130), f"TARGET: {title[:18]}", font=get_font(20, bold=True), fill=WHITE)

    img.save(os.path.join(OUT_DIR, filename))


def main():
    # 1. Scene 1: Cold Open Overlay (over 2x2 live gameplay grid)
    img1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(img1)
    # Grid crosshair lines for the 2x2 background
    draw1.line([(W // 2, 0), (W // 2, H)], fill=(0, 229, 255, 210), width=4)
    draw1.line([(0, H // 2), (W, H // 2)], fill=(255, 43, 214, 210), width=4)
    draw_outer_hud_chrome(draw1)

    # Center-left hero HUD command panel + right portrait
    draw_chamfer_panel(draw1, 88, 185, 1744, 710, cut=34, fill=(6, 10, 24, 236), outline=CYAN, width=4, accent=MAGENTA)
    paste_chamfer_image(img1, "public/images/ahmad-2.jpg", 1320, 235, 455, 610, cut=28, border_color=CYAN)

    draw1.text((145, 235), "// SYSTEM ONLINE · INTERACTIVE 3D PORTFOLIO & SHOWREEL", font=get_font(23, mono=True), fill=CYAN)
    draw1.text((145, 285), "SYED MUHAMMAD", font=get_font(82, bold=True), fill=WHITE)
    draw1.text((145, 380), "AHMAD  [AKKA]", font=get_font(78, bold=True), fill=CYAN)

    draw_chamfer_panel(draw1, 145, 490, 1110, 66, cut=12, fill=(32, 12, 48, 250), outline=MAGENTA, width=2, accent=YELLOW)
    draw1.text((170, 508), "GAME DEVELOPER  ·  GAME PROGRAMMER  ·  XR & 3D ARTIST", font=get_font(28, bold=True), fill=YELLOW)

    draw1.text((145, 588), "BS CS & IT (Gaming & Animation) · NED University (2023–2027)", font=get_font(28), fill=WHITE)
    draw1.text((145, 634), "Game Development Intern @ Aerox ERP  ·  Global Game Jam 2026 Developer", font=get_font(26), fill=MUTED)

    draw_pills(
        draw1,
        145,
        715,
        ["8+ SHIPPED GAMES", "UNITY 3D", "UNREAL ENGINE 5", "C# / C++ / PYTHON", "AR / VR", "BLENDER 5.1"],
        border_color=CYAN,
    )
    img1.save(os.path.join(OUT_DIR, "hud_scene1_intro.png"))

    # 2. Scene 2: Chrono Rebellion (Full-screen HD)
    build_project_lower_third(
        "hud_scene2_chrono.png",
        "01",
        "FLAGSHIP 3D SCI-FI ACTION SHOOTER // 1ST & 3RD PERSON",
        "CHRONO REBELLION",
        "Time-manipulation combat mechanics, enemy AI state machines, custom weapon HUD & HDRP lighting.",
        ["UNITY 3D", "C#", "HDRP", "SHADER GRAPH", "CINEMACHINE", "COMBAT AI"],
        primary=CYAN,
        accent=MAGENTA,
    )

    # 3. Scene 3: Behind the Smile (Full-screen HD)
    build_project_lower_third(
        "hud_scene3_smile.png",
        "02",
        "GLOBAL GAME JAM 2026 SHOWCASE // BUILT IN 48 HOURS",
        "BEHIND THE SMILE",
        "Atmospheric first-person narrative exploration game built around the GGJ26 theme 'Masks'.",
        ["UNITY 3D", "C#", "NARRATIVE DESIGN", "3D ENVIRONMENT", "CUSTOM UI"],
        primary=MAGENTA,
        accent=YELLOW,
    )

    # 4. Scene 4: Dual Split-Screen Arcade Showdown (Paper Plane Dash x Pac-Man)
    img4 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw4 = ImageDraw.Draw(img4)
    # Glowing vertical divider spine
    draw4.rectangle([W // 2 - 4, 46, W // 2 + 4, H - 44], fill=CYAN)
    draw_outer_hud_chrome(draw4, top_label="DUAL ARCADE SHOWCASE // UNREAL ENGINE 5  ×  C++ / SFML")

    # Left card (Paper Plane Dash)
    draw_chamfer_panel(draw4, 42, 740, 860, 250, cut=18, fill=(6, 11, 24, 224), outline=CYAN, width=3, accent=MAGENTA)
    draw4.text((72, 762), "03 // PROCEDURAL ENDLESS RUNNER", font=get_font(20, mono=True), fill=CYAN)
    draw4.text((72, 792), "PAPER PLANE DASH", font=get_font(44, bold=True), fill=WHITE)
    draw4.text((72, 852), "Dynamic flight physics & procedural obstacle spawning.", font=get_font(21), fill=MUTED)
    draw_pills(draw4, 72, 908, ["UNREAL ENGINE 5", "BLUEPRINTS", "PROCEDURAL GEN"], border_color=CYAN)

    # Right card (Pac-Man)
    draw_chamfer_panel(draw4, W // 2 + 58, 740, 860, 250, cut=18, fill=(6, 11, 24, 224), outline=YELLOW, width=3, accent=MAGENTA)
    draw4.text((W // 2 + 88, 762), "04 // CUSTOM C++ ENGINE & AI ALGORITHMS", font=get_font(20, mono=True), fill=YELLOW)
    draw4.text((W // 2 + 88, 792), "PAC-MAN ARCADE", font=get_font(44, bold=True), fill=WHITE)
    draw4.text((W // 2 + 88, 852), "QuadTree spatial collision & Graph-based Ghost pathfinding.", font=get_font(21), fill=MUTED)
    draw_pills(draw4, W // 2 + 88, 908, ["C++", "SFML", "QUADTREES", "GRAPH PATHFINDING"], border_color=YELLOW)
    img4.save(os.path.join(OUT_DIR, "hud_scene4_dual.png"))

    # 5. Scene 5: Voxelcraft 3D (Full-screen HD)
    build_project_lower_third(
        "hud_scene5_voxel.png",
        "05",
        "PROCEDURAL 3D VOXEL SANDBOX // CUSTOM CHUNK ENGINE",
        "VOXELCRAFT 3D",
        "Procedural terrain generation, greedy chunk mesh optimization, raycast block placement & destruction.",
        ["UNITY 3D", "C#", "PROCEDURAL TERRAIN", "VOXEL MESHING", "SANDBOX PHYSICS"],
        primary=YELLOW,
        accent=CYAN,
    )

    # 6. Scene 6: XR Triple Showcase (VR Solar System + AR Memory + AR Face Filter)
    img6 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw6 = ImageDraw.Draw(img6)
    # Split lines: X = 1080 vertical, Y = 540 horizontal on right side
    draw6.rectangle([1077, 46, 1083, H - 44], fill=CYAN)
    draw6.rectangle([1080, 537, W, 543], fill=MAGENTA)
    draw_outer_hud_chrome(draw6, top_label="EXTENDED REALITY (XR) & COMPUTER VISION // VR · AR · MEDIAPIPE")

    # Left panel card (Solar System VR)
    draw_chamfer_panel(draw6, 40, 760, 995, 230, cut=18, fill=(6, 11, 24, 224), outline=CYAN, width=3, accent=MAGENTA)
    draw6.text((68, 780), "06 // IMMERSIVE VIRTUAL REALITY SIMULATION", font=get_font(19, mono=True), fill=CYAN)
    draw6.text((68, 810), "SOLAR SYSTEM VR", font=get_font(44, bold=True), fill=WHITE)
    draw_pills(draw6, 68, 885, ["UNITY VR", "OPENXR", "XR INTERACTION TOOLKIT", "3D SPATIAL UI"], border_color=CYAN)

    # Top-right card (AR Memory)
    draw_chamfer_panel(draw6, 1110, 395, 775, 125, cut=14, fill=(6, 11, 24, 224), outline=MAGENTA, width=2, accent=YELLOW)
    draw6.text((1134, 412), "07 // AUGMENTED REALITY CARD GAME", font=get_font(17, mono=True), fill=MAGENTA)
    draw6.text((1134, 440), "AR MEMORY  [UNITY · VUFORIA SDK]", font=get_font(28, bold=True), fill=WHITE)

    # Bottom-right card (AR Face Filter)
    draw_chamfer_panel(draw6, 1110, 885, 775, 125, cut=14, fill=(6, 11, 24, 224), outline=GREEN, width=2, accent=CYAN)
    draw6.text((1134, 902), "08 // REAL-TIME 468-POINT FACE TRACKING", font=get_font(17, mono=True), fill=GREEN)
    draw6.text((1134, 930), "AR FACE FILTER  [PYTHON · OPENCV · MEDIAPIPE]", font=get_font(26, bold=True), fill=WHITE)
    img6.save(os.path.join(OUT_DIR, "hud_scene6_xr.png"))

    # 7. Scene 7: Custom 3D Blender Avatar & Technical Arsenal
    img7 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw7 = ImageDraw.Draw(img7)
    draw_outer_hud_chrome(draw7, top_label="CUSTOM 3D BLENDER AVATAR & FULL-STACK TECHNICAL ARSENAL")

    # Right side: large chamfered card with Blender Avatar render + skills
    draw_chamfer_panel(draw7, 680, 110, 1180, 860, cut=28, fill=(6, 11, 24, 232), outline=CYAN, width=3, accent=MAGENTA)
    paste_chamfer_image(img7, "blender/avatar_preview.png", 715, 145, 430, 790, cut=22, border_color=CYAN)

    draw7.text((1180, 155), "CUSTOM 3D AVATAR & SKILLS", font=get_font(22, mono=True), fill=MAGENTA)
    draw7.text((1180, 190), "BLENDER 5.1 RIGGED AVATAR", font=get_font(38, bold=True), fill=WHITE)
    draw7.text((1180, 245), "· 21-Bone Skeleton + 6 NLA Animations (Walk, Idle, Wave...)", font=get_font(21), fill=MUTED)
    draw7.text((1180, 280), "· 3rd-Person Walk Mode + AI Voice Lip-Sync Morphs", font=get_font(21), fill=MUTED)

    skill_boxes = [
        ("GAME ENGINES & 3D WEB", "Unity (HDRP/URP) · Unreal Engine 5 · Three.js WebGPU (TSL)", CYAN, 335),
        ("LANGUAGES & SYSTEMS", "C# · C++ · C · Python · JavaScript · SFML · QuadTrees", MAGENTA, 470),
        ("3D ART, VFX & AI RAG", "Blender 5.1 · After Effects · Photoshop · Gemini RAG AI", YELLOW, 605),
        ("CERTIFICATIONS & HONORS", "CEGA Unreal Engine · CEGA Pre/Post-Prod · Coursera Google AI", GREEN, 740),
    ]
    for stitle, sdesc, scol, sy in skill_boxes:
        draw_chamfer_panel(draw7, 1180, sy, 645, 115, cut=14, fill=(12, 22, 46, 230), outline=scol, width=2, accent=WHITE)
        draw7.text((1205, sy + 18), stitle, font=get_font(21, bold=True), fill=scol)
        draw7.text((1205, sy + 56), sdesc, font=get_font(20), fill=WHITE)

    img7.save(os.path.join(OUT_DIR, "hud_scene7_avatar.png"))

    # 8. Scene 8: 2x2 Quad-Grid All-Games Rapid Montage
    img8 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw8 = ImageDraw.Draw(img8)
    draw8.rectangle([W // 2 - 3, 46, W // 2 + 3, H - 44], fill=CYAN)
    draw8.rectangle([0, H // 2 - 3, W, H // 2 + 3], fill=MAGENTA)
    draw_outer_hud_chrome(draw8, top_label="MULTI-ENGINE GAMEPLAY MATRIX // 8+ INTERACTIVE PROJECTS")

    # Center diamond/chamfered badge over intersection
    draw_chamfer_panel(draw8, W // 2 - 430, H // 2 - 95, 860, 190, cut=24, fill=(6, 10, 24, 238), outline=YELLOW, width=4, accent=CYAN)
    draw8.text((W // 2, H // 2 - 58), "8+ SHIPPED GAMES & XR SIMULATIONS", font=get_font(38, bold=True), fill=WHITE, anchor="ma")
    draw8.text((W // 2, H // 2 + 2), "3D ACTION · ENDLESS RUNNER · VR · AR · VOXEL SANDBOX · ARCADE", font=get_font(21, mono=True), fill=CYAN, anchor="ma")
    draw8.text((W // 2, H // 2 + 44), "PLAYABLE VIDEOS STREAMING LIVE IN THE 3D WEBGPU ALLEY", font=get_font(20, bold=True), fill=YELLOW, anchor="ma")
    img8.save(os.path.join(OUT_DIR, "hud_scene8_quad.png"))

    # 9. Scene 9: Finale Command Deck & Call To Action
    img9 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw9 = ImageDraw.Draw(img9)
    draw_outer_hud_chrome(draw9)

    draw_chamfer_panel(draw9, 110, 165, 1700, 750, cut=36, fill=(6, 10, 24, 226), outline=CYAN, width=4, accent=MAGENTA)
    paste_chamfer_image(img9, "public/images/ahmad-1.jpg", 155, 220, 360, 640, cut=24, border_color=CYAN)
    paste_chamfer_image(img9, "blender/avatar_preview.png", 1405, 220, 360, 640, cut=24, border_color=MAGENTA)

    draw9.text((W // 2, 235), "// TRANSMISSION COMPLETE · READY FOR DEPLOYMENT", font=get_font(22, mono=True), fill=CYAN, anchor="ma")
    draw9.text((W // 2, 295), "SYED MUHAMMAD AHMAD", font=get_font(62, bold=True), fill=WHITE, anchor="ma")
    draw9.text((W // 2, 378), "GAME DEVELOPER · GAME PROGRAMMER · XR ENGINEER", font=get_font(26, bold=True), fill=YELLOW, anchor="ma")

    draw_chamfer_panel(draw9, 555, 445, 810, 175, cut=18, fill=(12, 22, 48, 235), outline=MAGENTA, width=2, accent=CYAN)
    draw9.text((W // 2, 475), "EXPLORE THE LIVE 3D CYBERPUNK PORTFOLIO:", font=get_font(22, bold=True), fill=CYAN, anchor="ma")
    draw9.text((W // 2, 518), "· Walk in 3rd-Person with Custom Rigged Blender Avatar", font=get_font(21), fill=WHITE, anchor="ma")
    draw9.text((W // 2, 554), "· Watch All 8 Game Screens in the 3D Alley & Chat with AHMAD.AI", font=get_font(21), fill=WHITE, anchor="ma")

    draw9.text((W // 2, 665), "ahmedakka765@gmail.com   |   +92 332 2669028", font=get_font(30, bold=True), fill=WHITE, anchor="ma")
    draw9.text((W // 2, 718), "linkedin.com/in/syed-muhammad-ahmad-55b240284", font=get_font(23, mono=True), fill=CYAN, anchor="ma")
    draw9.text((W // 2, 775), "NED University of Engineering & Technology · Karachi, Pakistan", font=get_font(22), fill=MUTED, anchor="ma")

    img9.save(os.path.join(OUT_DIR, "hud_scene9_outro.png"))
    print(f"[overlays] Generated 9 Sci-Fi HUD overlays in {OUT_DIR}")


if __name__ == "__main__":
    main()
