import os
from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "video/overlays"
os.makedirs(OUT_DIR, exist_ok=True)

W, H = 1920, 1080

# Exact samsy.ninja Editorial Design System Palette (extracted from src/portfolio/portfolio.css)
BG_SOLID = (7, 7, 10, 246)          # --sn-bg-solid: #07070a
BG_ELEV = (13, 13, 18, 244)         # --sn-bg-elev:  rgba(13, 13, 18, 0.96)
BG_CARD = (15, 15, 22, 238)         # --sn-bg-card:  rgba(15, 15, 22, 0.93)
FG = (244, 244, 246, 255)           # --sn-fg:       #f4f4f6
FG_MUTED = (148, 148, 156, 255)     # --sn-fg-muted: rgba(244, 244, 246, 0.58)
FG_SUBTLE = (96, 96, 104, 255)      # --sn-fg-subtle
LINE = (244, 244, 246, 38)          # --sn-line:     1px architectural hairline
LINE_STRONG = (244, 244, 246, 86)   # --sn-line-strong
LINE_OPAQUE = (52, 52, 62, 255)     # Opaque 1px hairline for nested cards
ACCENT = (221, 251, 36, 255)        # --sn-accent:   #ddfb24 Surgical Acid-Lime
EMERALD = (24, 242, 160, 255)       # --sn-success:  #18f2a0 Status Dot


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


def draw_editorial_box(draw, x, y, w, h, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True, accent_color=ACCENT):
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=border, width=1)
    if accent_stub:
        # Surgical 3px acid-lime top-left index rule
        stub_w = min(96, w // 4)
        draw.rectangle([x, y, x + stub_w, y + 3], fill=accent_color)


def draw_outline_text(draw, xy, text, font, stroke_color=FG, stroke_width=2):
    # Hollow outline typography matching .sn-hero-line--outline (-webkit-text-stroke: 1.5px #f4f4f6)
    x, y = xy
    for dx in range(-stroke_width, stroke_width + 1):
        for dy in range(-stroke_width, stroke_width + 1):
            if dx * dx + dy * dy == stroke_width * stroke_width:
                draw.text((x + dx, y + dy), text, font=font, fill=stroke_color)
    draw.text((x, y), text, font=font, fill=BG_ELEV)


def draw_editorial_chrome(draw, section_tag="(01) — SELECTED WORKS", right_tag="SHOWREEL 2026 // 1080P 60FPS"):
    # Minimal Fixed Top Architectural Bar (62px height, 1px hairline bottom border)
    draw.rectangle([0, 0, W, 62], fill=BG_ELEV)
    draw.line([(0, 62), (W, 62)], fill=LINE_OPAQUE, width=1)

    f_brand = get_font(18, bold=True)
    f_mono = get_font(15, mono=True)

    # Brand mark + [AKKA®] handle box + green availability dot
    draw.text((48, 21), "SYED MUHAMMAD AHMAD", font=f_brand, fill=FG)
    draw.rectangle([282, 18, 352, 43], fill=BG_CARD, outline=LINE_OPAQUE, width=1)
    draw.text((317, 23), "AKKA®", font=f_mono, fill=FG, anchor="ma")

    # Emerald pulse dot + availability
    draw.ellipse([376, 27, 384, 35], fill=EMERALD)
    draw.text((396, 23), "AVAILABLE FOR GAME DEV & XR", font=f_mono, fill=FG_MUTED)

    # Center section index & right metadata
    draw.text((W // 2 + 80, 23), section_tag, font=f_mono, fill=ACCENT, anchor="ma")
    draw.text((W - 48, 23), right_tag, font=f_mono, fill=FG_MUTED, anchor="ra")

    # Minimal Bottom Architectural Rail (52px height, 1px hairline top border)
    draw.rectangle([0, H - 52, W, H], fill=BG_ELEV)
    draw.line([(0, H - 52), (W, H - 52)], fill=LINE_OPAQUE, width=1)
    draw.text((48, H - 33), "© 2026 SYED MUHAMMAD AHMAD (AKKA®). ALL RIGHTS RESERVED.", font=f_mono, fill=FG_MUTED)
    draw.text((W - 48, H - 33), "UNITY  ·  UNREAL ENGINE 5  ·  C++ / C# / PYTHON  ·  OPENXR  ·  BLENDER 5.1  ·  WEBGPU", font=f_mono, fill=FG_MUTED, anchor="ra")


def draw_hairline_tags(draw, x, y, tags, highlight_first=False):
    f_tag = get_font(15, mono=True)
    cur_x = x
    for idx, tag in enumerate(tags):
        label = tag.upper()
        bbox = draw.textbbox((0, 0), label, font=f_tag)
        tw = (bbox[2] - bbox[0]) + 24
        th = 32
        if highlight_first and idx == 0:
            draw.rectangle([cur_x, y, cur_x + tw, y + th], fill=ACCENT, outline=ACCENT, width=1)
            draw.text((cur_x + 12, y + 8), label, font=f_tag, fill=(7, 7, 10, 255))
        else:
            draw.rectangle([cur_x, y, cur_x + tw, y + th], fill=BG_CARD, outline=LINE_OPAQUE, width=1)
            draw.text((cur_x + 12, y + 8), label, font=f_tag, fill=FG)
        cur_x += tw + 8


def paste_editorial_image(base_img, img_path, x, y, w, h, caption_left="", caption_right=""):
    if not os.path.exists(img_path):
        return
    draw = ImageDraw.Draw(base_img)
    # Outer 1px Swiss frame with 10px matte padding
    draw.rectangle([x, y, x + w, y + h], fill=BG_CARD, outline=LINE_OPAQUE, width=1)
    ix, iy, iw, ih = x + 10, y + 10, w - 20, h - (42 if caption_left else 20)

    src = Image.open(img_path).convert("RGBA")
    sw, sh = src.size
    target_aspect = iw / ih
    src_aspect = sw / sh
    if src_aspect > target_aspect:
        new_w = int(sh * target_aspect)
        left = (sw - new_w) // 2
        src = src.crop((left, 0, left + new_w, sh))
    else:
        new_h = int(sw / target_aspect)
        top = (sh - new_h) // 2
        src = src.crop((0, top, sw, top + new_h))
    src = src.resize((iw, ih), Image.Resampling.LANCZOS)
    base_img.paste(src, (ix, iy))
    draw.rectangle([ix, iy, ix + iw, iy + ih], outline=LINE_OPAQUE, width=1)

    if caption_left:
        f_cap = get_font(13, mono=True)
        draw.text((ix, iy + ih + 10), caption_left, font=f_cap, fill=FG_MUTED)
        if caption_right:
            draw.text((ix + iw, iy + ih + 10), caption_right, font=f_cap, fill=ACCENT, anchor="ra")


def build_case_study_overlay(filename, idx_str, category, year, title, summary, tags):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw_editorial_chrome(draw, section_tag=f"(01) — SELECTED WORKS // CASE STUDY {idx_str}")

    # Crisp 1px Swiss architectural framing lines around viewport
    draw.line([(48, 62), (48, H - 52)], fill=(244, 244, 246, 35), width=1)
    draw.line([(W - 48, 62), (W - 48, H - 52)], fill=(244, 244, 246, 35), width=1)

    # Top-right minimal index pill
    draw_editorial_box(draw, W - 368, 86, 296, 68, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw.text((W - 348, 99), f"INDEX // {idx_str} OF 009", font=get_font(14, mono=True), fill=ACCENT)
    draw.text((W - 348, 122), f"{category.upper()} · {year}", font=get_font(16, bold=True), fill=FG)

    # Lower-left Minimalist Editorial Case Study Card (leaves 78% of gameplay footage crystal-clear)
    px, py, pw, ph = 72, 738, 1280, 248
    draw_editorial_box(draw, px, py, pw, ph, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)

    # Vertical hairline column divider inside card (Index col | Content col)
    draw.line([(px + 128, py), (px + 128, py + ph)], fill=LINE_OPAQUE, width=1)
    draw.text((px + 64, py + 32), idx_str, font=get_font(36, mono=True), fill=ACCENT, anchor="ma")
    draw.text((px + 64, py + 82), str(year), font=get_font(15, mono=True), fill=FG_MUTED, anchor="ma")

    # Content column
    cx = px + 156
    draw.text((cx, py + 24), f"{category.upper()}   //   DIRECT ENGINE CAPTURE", font=get_font(15, mono=True), fill=FG_MUTED)
    draw.text((cx, py + 52), title.upper(), font=get_font(48, bold=True), fill=FG)
    draw.text((cx, py + 118), summary, font=get_font(20, bold=False), fill=FG_MUTED)

    # Horizontal hairline above tags
    draw.line([(cx, py + 166), (px + pw - 28, py + 166)], fill=LINE_OPAQUE, width=1)
    draw_hairline_tags(draw, cx, py + 184, tags, highlight_first=True)

    img.save(os.path.join(OUT_DIR, filename))


def main():
    # =========================================================================
    # ACT 1: Editorial Showreel Cover & Title Lockup (Reveals 2x2 Gameplay Matrix)
    # =========================================================================
    img1 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw1 = ImageDraw.Draw(img1)
    # Architectural 2x2 grid hairlines over the 4-game live backdrop
    draw1.line([(W // 2, 62), (W // 2, H - 52)], fill=LINE_OPAQUE, width=2)
    draw1.line([(0, H // 2), (W, H // 2)], fill=LINE_OPAQUE, width=2)
    draw_editorial_chrome(draw1, section_tag="(02) — 2026 GAME & XR DEVELOPER SHOWREEL")

    # Quadrant index badges in the 4 outer corners so all 4 live game viewports are framed & visible
    quad_labels = [
        (36, 84, "001 // CHRONO REBELLION", "UNITY HDRP · SCI-FI FPS/TPS"),
        (W - 372, 84, "002 // PAPER PLANE DASH", "UNREAL ENGINE 5 · FLIGHT"),
        (36, H - 134, "003 // BEHIND THE SMILE", "GLOBAL GAME JAM 2026 · 3D"),
        (W - 372, H - 134, "004 // MINECRAFT CLONE", "PROCEDURAL VOXEL ENGINE"),
    ]
    for qx, qy, qtitle, qsub in quad_labels:
        draw_editorial_box(draw1, qx, qy, 336, 62, fill=(13, 13, 18, 220), border=LINE_OPAQUE, accent_stub=True)
        draw1.text((qx + 16, qy + 11), qtitle, font=get_font(14, bold=True), fill=FG)
        draw1.text((qx + 16, qy + 33), qsub, font=get_font(12, mono=True), fill=ACCENT)

    # Compact centered architectural title card (lets the 4 gameplay quadrants shine around it)
    cx_box, cy_box, cw_box, ch_box = 340, 290, 1240, 500
    draw_editorial_box(
        draw1,
        cx_box,
        cy_box,
        cw_box,
        ch_box,
        fill=(10, 10, 14, 232),
        border=LINE_OPAQUE,
        accent_stub=True,
    )

    # Top eyebrow bar inside center card
    draw1.rectangle([cx_box + 48, cy_box + 42, cx_box + 388, cy_box + 74], fill=ACCENT)
    draw1.text(
        (cx_box + 62, cy_box + 50),
        "SHOWREEL 2026 // 09 SELECTED WORKS",
        font=get_font(15, mono=True),
        fill=(7, 7, 10, 255),
    )
    draw1.text(
        (cx_box + cw_box - 48, cy_box + 50),
        "AKKA® // KARACHI, PK",
        font=get_font(15, mono=True),
        fill=FG_MUTED,
        anchor="ra",
    )

    f_cover_main = get_font(74, bold=True)
    f_cover_sub = get_font(56, bold=True)
    draw1.text((cx_box + 48, cy_box + 104), "SYED MUHAMMAD AHMAD", font=f_cover_main, fill=FG)
    draw_outline_text(
        draw1,
        (cx_box + 48, cy_box + 194),
        "GAME & XR DEVELOPER",
        font=f_cover_main,
        stroke_color=ACCENT,
        stroke_width=2,
    )
    draw1.text((cx_box + 48, cy_box + 286), "INTERACTIVE 3D ARCHITECT.", font=f_cover_sub, fill=FG)

    # Hairline divider + engine/tool matrix strip
    draw1.line([(cx_box + 48, cy_box + 378), (cx_box + cw_box - 48, cy_box + 378)], fill=LINE_OPAQUE, width=1)
    draw_hairline_tags(
        draw1,
        cx_box + 48,
        cy_box + 408,
        ["UNITY 3D / HDRP", "UNREAL ENGINE 5", "C++ / C# / PYTHON", "OPENXR / VUFORIA", "BLENDER 5.1", "THREE.JS WEBGPU"],
        highlight_first=True,
    )
    img1.save(os.path.join(OUT_DIR, "hud_scene1_intro.png"))

    # =========================================================================
    # ACT 2: 001 — Chrono Rebellion
    # =========================================================================
    build_case_study_overlay(
        "hud_scene2_chrono.png",
        "001",
        "Game // Sci-Fi Shooter",
        2026,
        "Chrono Rebellion",
        "Third-person and first-person sci-fi shooter featuring time-manipulation mechanics, custom HUD, and HDRP combat.",
        ["UNITY", "C#", "HDRP", "SHADER GRAPH", "TIME-MANIPULATION AI", "1ST & 3RD PERSON"],
    )

    # =========================================================================
    # ACT 3: 002 — Behind the Smile (Global Game Jam 2026)
    # =========================================================================
    build_case_study_overlay(
        "hud_scene3_smile.png",
        "002",
        "Game // Global Game Jam 2026",
        2026,
        "Behind the Smile",
        "Narrative-driven 3D exploration game built in 48 hours at Global Game Jam 2026 around the theme 'Masks'.",
        ["UNITY 3D", "C#", "GLOBAL GAME JAM 2026", "NARRATIVE SYSTEMS", "CUSTOM UI"],
    )

    # =========================================================================
    # ACT 4: Dual Split-Screen Editorial Comparison (003 Paper Plane Dash x 006 Pac-Man)
    # =========================================================================
    img4 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw4 = ImageDraw.Draw(img4)
    # Crisp 2px vertical architectural split line
    draw4.rectangle([W // 2 - 1, 62, W // 2 + 1, H - 52], fill=FG)
    draw_editorial_chrome(draw4, section_tag="(01) — SELECTED WORKS // DUAL ENGINE COMPARISON")

    # Left Card: 003 Paper Plane Dash
    draw_editorial_box(draw4, 48, 752, 864, 236, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw4.text((76, 774), "003   //   GAME · 2025 · UNREAL ENGINE 5", font=get_font(15, mono=True), fill=ACCENT)
    draw4.text((76, 804), "PAPER PLANE DASH", font=get_font(42, bold=True), fill=FG)
    draw4.text((76, 862), "Procedural 3D endless runner with Blueprint lane physics & obstacle generation.", font=get_font(18, bold=False), fill=FG_MUTED)
    draw_hairline_tags(draw4, 76, 918, ["UNREAL ENGINE 5", "BLUEPRINTS", "PROCEDURAL GENERATION"], highlight_first=True)

    # Right Card: 006 Pac-Man
    draw_editorial_box(draw4, W // 2 + 48, 752, 864, 236, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw4.text((W // 2 + 76, 774), "006   //   GAME · 2024 · CUSTOM C++ ENGINE", font=get_font(15, mono=True), fill=ACCENT)
    draw4.text((W // 2 + 76, 804), "PAC-MAN (C++ / SFML)", font=get_font(42, bold=True), fill=FG)
    draw4.text((W // 2 + 76, 862), "2D arcade engine using QuadTrees for spatial collision and Graph AI pathfinding.", font=get_font(18, bold=False), fill=FG_MUTED)
    draw_hairline_tags(draw4, W // 2 + 76, 918, ["C++", "SFML", "QUADTREES", "GRAPH PATHFINDING"], highlight_first=True)
    img4.save(os.path.join(OUT_DIR, "hud_scene4_dual.png"))

    # =========================================================================
    # ACT 5: 005 — Voxelcraft 3D
    # =========================================================================
    build_case_study_overlay(
        "hud_scene5_voxel.png",
        "005",
        "Game // Procedural Sandbox",
        2025,
        "Voxelcraft 3D",
        "Voxel-based 3D sandbox engine featuring procedural terrain chunks, block placement, and raycast destruction.",
        ["UNITY 3D", "C#", "PROCEDURAL VOXEL ENGINE", "CHUNK MESHING", "SANDBOX"],
    )

    # =========================================================================
    # ACT 6: Triple XR Viewport (004 Solar System VR + 007 AR Memory + 008 AR Face Filter)
    # =========================================================================
    img6 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw6 = ImageDraw.Draw(img6)
    draw6.rectangle([1079, 62, 1081, H - 52], fill=FG)
    draw6.rectangle([1080, 539, W, 541], fill=FG)
    draw_editorial_chrome(draw6, section_tag="(01) — SELECTED WORKS // EXTENDED REALITY (VR · AR · CV)")

    # Left: 004 Solar System VR
    draw_editorial_box(draw6, 48, 768, 984, 220, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw6.text((76, 790), "004   //   XR · 2025 · VIRTUAL REALITY", font=get_font(15, mono=True), fill=ACCENT)
    draw6.text((76, 818), "SOLAR SYSTEM EXPLORATION (VR)", font=get_font(38, bold=True), fill=FG)
    draw6.text((76, 872), "Immersive VR planetary simulation with teleportation locomotion and world-space UI.", font=get_font(18, bold=False), fill=FG_MUTED)
    draw_hairline_tags(draw6, 76, 922, ["UNITY", "OPENXR", "XR INTERACTION TOOLKIT", "VR"], highlight_first=True)

    # Top-Right: 007 AR Memory Card Game
    draw_editorial_box(draw6, 1112, 392, 760, 122, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw6.text((1136, 412), "007   //   XR · 2025 · VUFORIA AUGMENTED REALITY", font=get_font(14, mono=True), fill=ACCENT)
    draw6.text((1136, 440), "AR MEMORY CARD GAME  [UNITY · VUFORIA]", font=get_font(26, bold=True), fill=FG)

    # Bottom-Right: 008 AR Face Filter App
    draw_editorial_box(draw6, 1112, 882, 760, 122, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    draw6.text((1136, 902), "008   //   XR · 2025 · REAL-TIME COMPUTER VISION", font=get_font(14, mono=True), fill=ACCENT)
    draw6.text((1136, 930), "AR FACE FILTER  [PYTHON · OPENCV · MEDIAPIPE]", font=get_font(25, bold=True), fill=FG)
    img6.save(os.path.join(OUT_DIR, "hud_scene6_xr.png"))

    # =========================================================================
    # ACT 7: Section (02) & (03) — Custom Blender 5.1 3D Avatar & Capabilities Matrix
    # =========================================================================
    img7 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw7 = ImageDraw.Draw(img7)
    draw_editorial_chrome(draw7, section_tag="(02) — 3D CHARACTER LAB & TECHNICAL CAPABILITIES")

    draw_editorial_box(draw7, 650, 108, 1210, 864, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    paste_editorial_image(
        img7,
        "blender/avatar_preview.png",
        686,
        146,
        420,
        788,
        caption_left="MODEL // AVATAR.GLB",
        caption_right="BLENDER 5.1",
    )

    cx = 1140
    draw7.text((cx, 148), "(02B) — CUSTOM RIGGED 3D AVATAR & CAPABILITIES", font=get_font(15, mono=True), fill=ACCENT)
    draw7.text((cx, 180), "BLENDER 5.1 3D AVATAR", font=get_font(42, bold=True), fill=FG)
    draw7.text((cx, 238), "21-Bone Skeleton · 6 NLA Clips (Walk, Idle, Wave, Talk, Point, Victory)", font=get_font(18, bold=False), fill=FG_MUTED)
    draw7.text((cx, 268), "3rd-Person Avatar Walk Mode + AI Voice Lip-Sync Shape Keys", font=get_font(18, bold=False), fill=FG_MUTED)

    cap_cells = [
        ("01 // GAME ENGINES", ["UNITY", "UNREAL ENGINE 5", "BLUEPRINTS", "HDRP", "SFML"], 326),
        ("02 // PROGRAMMING", ["C#", "C++", "C", "PYTHON", "DATA STRUCTURES & ALGORITHMS"], 468),
        ("03 // XR & 3D DESIGN", ["OPENXR", "VUFORIA", "BLENDER 5.1", "AFTER EFFECTS", "PHOTOSHOP"], 610),
        ("04 // WEB, AI & CERTS", ["THREE.JS WEBGPU", "GEMINI RAG", "CEGA UE5", "COURSERA GOOGLE AI"], 752),
    ]
    for ctitle, ctags, cy in cap_cells:
        draw7.line([(cx, cy), (1824, cy)], fill=LINE_OPAQUE, width=1)
        draw7.text((cx, cy + 16), ctitle, font=get_font(15, mono=True), fill=ACCENT)
        draw_hairline_tags(draw7, cx, cy + 52, ctags, highlight_first=False)

    img7.save(os.path.join(OUT_DIR, "hud_scene7_avatar.png"))

    # =========================================================================
    # ACT 8: 2x2 Architectural Index Matrix (09 Interactive Works)
    # =========================================================================
    img8 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw8 = ImageDraw.Draw(img8)
    draw8.rectangle([W // 2 - 1, 62, W // 2 + 1, H - 52], fill=FG)
    draw8.rectangle([0, H // 2 - 1, W, H // 2 + 1], fill=FG)
    draw_editorial_chrome(draw8, section_tag="(01) — CURATED PROJECT INDEX // 09 WORKS")

    # Center Swiss Architectural Plaque
    bx, by, bw, bh = W // 2 - 460, H // 2 - 115, 920, 230
    draw_editorial_box(draw8, bx, by, bw, bh, fill=BG_SOLID, border=FG, accent_stub=True)
    draw8.text((W // 2, by + 34), "(01) — CURATED INTERACTIVE PORTFOLIO INDEX", font=get_font(15, mono=True), fill=ACCENT, anchor="ma")
    draw8.text((W // 2, by + 72), "09 SELECTED WORKS (2024–2026)", font=get_font(46, bold=True), fill=FG, anchor="ma")
    draw8.text((W // 2, by + 144), "HOVER FOR 60FPS WAVE-DISTORTION PREVIEW  ·  WALK IN 3RD-PERSON 3D ALLEY", font=get_font(16, mono=True), fill=FG_MUTED, anchor="ma")
    img8.save(os.path.join(OUT_DIR, "hud_scene8_quad.png"))

    # =========================================================================
    # ACT 9: Section (04) — Editorial Outro & Direct Transmission
    # =========================================================================
    img9 = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    draw9 = ImageDraw.Draw(img9)
    draw9.line([(W // 2, 62), (W // 2, H - 52)], fill=LINE_OPAQUE, width=1)
    draw9.line([(0, H // 2), (W, H // 2)], fill=LINE_OPAQUE, width=1)
    draw_editorial_chrome(draw9, section_tag="(04) — INITIATE DIRECT TRANSMISSION")

    draw_editorial_box(draw9, 100, 140, 1720, 800, fill=BG_ELEV, border=LINE_OPAQUE, accent_stub=True)
    paste_editorial_image(
        img9,
        "public/images/ahmad-1.jpg",
        144,
        192,
        360,
        696,
        caption_left="KARACHI, PK",
        caption_right="NED ’27",
    )
    paste_editorial_image(
        img9,
        "blender/avatar_preview.png",
        1416,
        192,
        360,
        696,
        caption_left="3D AVATAR",
        caption_right="3RD-POV",
    )

    draw9.text((W // 2, 210), "(04) — DIRECT TRANSMISSION // AVAILABLE FOR ROLES", font=get_font(16, mono=True), fill=ACCENT, anchor="ma")
    draw9.text((W // 2, 265), "SYED MUHAMMAD AHMAD", font=get_font(56, bold=True), fill=FG, anchor="ma")
    draw_outline_text(draw9, (W // 2 - 335, 340), "LET'S BUILD THE NEXT WORLD.", font=get_font(44, bold=True), stroke_color=FG, stroke_width=2)

    # Swiss table of direct links in center
    rows = [
        ("LIVE DEPLOYMENT", "syed-muhammad-ahmad-portfolio.vercel.app"),
        ("DIRECT EMAIL", "ahmedakka765@gmail.com"),
        ("LINKEDIN", "linkedin.com/in/syed-muhammad-ahmad-55b240284"),
        ("EDUCATION", "BS CS & IT (Gaming & Animation) · NED University"),
    ]
    ry = 445
    for rkey, rval in rows:
        draw9.line([(545, ry), (1375, ry)], fill=LINE_OPAQUE, width=1)
        draw9.text((555, ry + 16), rkey, font=get_font(15, mono=True), fill=FG_MUTED)
        draw9.text((1365, ry + 16), rval, font=get_font(16, mono=True), fill=ACCENT if "vercel" in rval else FG, anchor="ra")
        ry += 56
    draw9.line([(545, ry), (1375, ry)], fill=LINE_OPAQUE, width=1)

    draw_hairline_tags(
        draw9,
        565,
        785,
        ["EXPLORE 3D WORLD", "ASK AHMAD.AI", "DOWNLOAD CV (PDF)", "09 CASE STUDIES"],
        highlight_first=True,
    )
    img9.save(os.path.join(OUT_DIR, "hud_scene9_outro.png"))
    print(f"[overlays] Generated 9 Editorial samsy.ninja overlays in {OUT_DIR}")


if __name__ == "__main__":
    main()
