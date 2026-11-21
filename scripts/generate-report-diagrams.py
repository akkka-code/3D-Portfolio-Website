#!/usr/bin/env python3
"""
Generates high-DPI (300 DPI) technical architecture diagrams, pipeline flowcharts,
performance charts, and a crisp 2x2 project showcase collage for the Web3D Portfolio
Microsoft Word Project Report (docs/Web3D_Portfolio_Project_Report.docx).
"""

import os
from PIL import Image, ImageDraw, ImageFont
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "docs", "report_assets")
os.makedirs(OUT_DIR, exist_ok=True)

# Clean technical palette matching the Word report
NAVY = "#0B132B"
NAVY_MID = "#162447"
TEAL = "#0284C7"
CYAN = "#06B6D4"
LIME = "#84CC16"
EMERALD = "#10B981"
AMBER = "#D97706"
PURPLE = "#7C3AED"
SLATE_BG = "#F8FAFC"
CARD_BG = "#FFFFFF"
BORDER = "#CBD5E1"
TEXT_DARK = "#0F172A"
TEXT_MUTED = "#475569"

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.edgecolor"] = BORDER


def draw_box(ax, x, y, w, h, title, subtitle="", facecolor="#FFFFFF", edgecolor=TEAL,
             title_color=TEXT_DARK, sub_color=TEXT_MUTED, lw=1.6, title_size=9.5,
             sub_size=7.6, header_bar=None, radius=0.015):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0.004,rounding_size={radius}",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=lw, zorder=3
    )
    ax.add_patch(box)

    if header_bar:
        bar_h = min(0.055, h * 0.28)
        bar = FancyBboxPatch(
            (x, y + h - bar_h), w, bar_h,
            boxstyle=f"round,pad=0.004,rounding_size={radius}",
            facecolor=header_bar, edgecolor=edgecolor, linewidth=lw, zorder=4
        )
        ax.add_patch(bar)
        ax.text(x + w / 2, y + h - bar_h / 2, title,
                ha="center", va="center", fontsize=title_size, fontweight="bold",
                color="#FFFFFF", zorder=5)
        if subtitle:
            ax.text(x + w / 2, y + (h - bar_h) / 2, subtitle,
                    ha="center", va="center", fontsize=sub_size, color=sub_color,
                    linespacing=1.35, zorder=5)
    else:
        if subtitle:
            ax.text(x + w / 2, y + h * 0.66, title,
                    ha="center", va="center", fontsize=title_size, fontweight="bold",
                    color=title_color, zorder=5)
            ax.text(x + w / 2, y + h * 0.30, subtitle,
                    ha="center", va="center", fontsize=sub_size, color=sub_color,
                    linespacing=1.3, zorder=5)
        else:
            ax.text(x + w / 2, y + h / 2, title,
                    ha="center", va="center", fontsize=title_size, fontweight="bold",
                    color=title_color, zorder=5)


def draw_arrow(ax, x1, y1, x2, y2, color=NAVY_MID, label="", label_offset=(0, 0.018),
               rad=0.0, lw=1.5, ls="-"):
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        connectionstyle=f"arc3,rad={rad}",
        arrowstyle="-|>,head_length=6.5,head_width=3.8",
        color=color, linewidth=lw, linestyle=ls, zorder=6
    )
    ax.add_patch(arrow)
    if label:
        mx = (x1 + x2) / 2 + label_offset[0]
        my = (y1 + y2) / 2 + label_offset[1]
        ax.text(mx, my, label, ha="center", va="center", fontsize=7.2,
                fontweight="bold", color=color,
                bbox=dict(boxstyle="round,pad=0.18", facecolor="#FFFFFF", edgecolor="none", alpha=0.92),
                zorder=7)


# =============================================================================
# DIAGRAM 1: End-to-End Full-Stack Web3D Portfolio Architecture
# =============================================================================
def build_architecture_diagram():
    fig, ax = plt.subplots(figsize=(12.2, 6.8), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    # Title bar
    ax.text(0.5, 0.968, "END-TO-END SYSTEM ARCHITECTURE — INTERACTIVE 3D WEBGPU PORTFOLIO",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.935, "Single-Source-of-Truth Data Flow across WebGPU 3D Client, Static Media Pipeline, Hybrid RAG AI & Vercel Serverless APIs",
            ha="center", va="center", fontsize=8.4, color=TEXT_MUTED)

    # Layer 1: Left Column — Authoring & Content Pipeline
    grp1 = FancyBboxPatch((0.015, 0.13), 0.225, 0.76, boxstyle="round,pad=0.006,rounding_size=0.014",
                          facecolor="#F1F5F9", edgecolor="#94A3B8", linewidth=1.2, linestyle="--", zorder=1)
    ax.add_patch(grp1)
    ax.text(0.1275, 0.868, "1. AUTHORING & CONTENT", ha="center", va="center",
            fontsize=8.3, fontweight="bold", color=NAVY)

    draw_box(ax, 0.028, 0.685, 0.199, 0.145,
             "Single Source of Truth",
             "content/profile.json\n9 Projects · Skills · Bio\nknowledge/CV.pdf + .md",
             facecolor="#EFF6FF", edgecolor=TEAL, header_bar=NAVY, title_size=8.0, sub_size=6.9)

    draw_box(ax, 0.028, 0.505, 0.199, 0.145,
             "Blender 5.1 Avatar",
             "blender/build_avatar.py\n20-Bone Rig · 6 NLA Clips\n3 Morph Targets → avatar.glb",
             facecolor="#FFFFFF", edgecolor=PURPLE, header_bar=PURPLE, title_size=8.0, sub_size=6.9)

    draw_box(ax, 0.028, 0.325, 0.199, 0.145,
             "After Effects + FFmpeg",
             "video/build_promo.jsx\n9-Act Editorial Showreel\npromo.mp4 (10.8 MB H.264)",
             facecolor="#FFFFFF", edgecolor=AMBER, header_bar=AMBER, title_size=8.0, sub_size=6.9)

    draw_box(ax, 0.028, 0.148, 0.199, 0.145,
             "RAG Ingestion Pipeline",
             "scripts/ingest.mjs\n28 Docs → 44 Chunks (700c)\ngemini-embedding-001 (768d)",
             facecolor="#FFFFFF", edgecolor=EMERALD, header_bar=EMERALD, title_size=8.0, sub_size=6.9)

    # Layer 2: Center Column — Browser Web3D Client (Vite 6 + WebGPU)
    grp2 = FancyBboxPatch((0.278, 0.13), 0.415, 0.76, boxstyle="round,pad=0.006,rounding_size=0.014",
                          facecolor="#F8FAFC", edgecolor=TEAL, linewidth=1.6, zorder=1)
    ax.add_patch(grp2)
    ax.text(0.4855, 0.868, "2. BROWSER CLIENT (VITE 6 · THREE.JS r185 WEBGPU + TSL)",
            ha="center", va="center", fontsize=8.0, fontweight="bold", color=TEAL)

    draw_box(ax, 0.293, 0.69, 0.385, 0.140,
             "Editorial Portfolio UI (createPortfolioUI.js)",
             "Fixed Topbar · 5-Waypoint Scroll Camera · 9-Project Index\n60fps Wave-Distortion Preview · Case Modal · Dark/Light",
             facecolor="#FFFFFF", edgecolor=NAVY, header_bar=NAVY, title_size=8.0, sub_size=6.9)

    draw_box(ax, 0.293, 0.505, 0.185, 0.150,
             "WebGPU World & TSL",
             "Cyberpunk Alley + Quadra\n5,000 GPU Rain + Height RT\nPlanar Mirror Ground\n8 Neon Video Kiosks",
             facecolor="#FFFFFF", edgecolor=TEAL, header_bar=TEAL, title_size=7.6, sub_size=6.5)

    draw_box(ax, 0.493, 0.505, 0.185, 0.150,
             "3rd-Person Avatar & BVH",
             "three-mesh-bvh Walk\nWASD + Sprint + Crouch\nV: 1st/3rd POV Toggle\nLip-Sync + Gestures",
             facecolor="#FFFFFF", edgecolor=PURPLE, header_bar=PURPLE, title_size=7.6, sub_size=6.5)

    draw_box(ax, 0.293, 0.325, 0.185, 0.145,
             "TSL Post-Processing",
             "GTAO (0.5×) · Scene MRT\nHalf-Res Bloom & Flare\n6 Look Presets · SMAA",
             facecolor="#FFFFFF", edgecolor=CYAN, header_bar=CYAN, title_size=7.6, sub_size=6.5)

    draw_box(ax, 0.493, 0.325, 0.185, 0.145,
             "Audio & Adaptive Perf",
             "1:58 Cyber Groove + Rain\nAuto Video Audio Ducking\nAdaptive DPR (1.5→0.85)",
             facecolor="#FFFFFF", edgecolor=AMBER, header_bar=AMBER, title_size=7.6, sub_size=6.5)

    draw_box(ax, 0.293, 0.148, 0.385, 0.142,
             "Interactive Client Services & Immutable CDN Cache",
             "AHMAD.AI Drawer (Web Speech STT/TTS + Citations) · Contact Form\nCDN Assets: /models/*.glb · /video/*.mp4 · /textures/* · /fonts/*",
             facecolor="#EFF6FF", edgecolor=TEAL, title_color=NAVY, title_size=7.9, sub_size=6.8)

    # Layer 3: Right Column — Vercel Serverless & External APIs
    grp3 = FancyBboxPatch((0.732, 0.13), 0.252, 0.76, boxstyle="round,pad=0.006,rounding_size=0.014",
                          facecolor="#F1F5F9", edgecolor=EMERALD, linewidth=1.4, zorder=1)
    ax.add_patch(grp3)
    ax.text(0.858, 0.868, "3. VERCEL CLOUD & APIS", ha="center", va="center",
            fontsize=8.3, fontweight="bold", color=EMERALD)

    draw_box(ax, 0.746, 0.665, 0.206, 0.165,
             "POST /api/chat (30s)",
             "Dense (0.75) + BM25 (0.25)\ndata/vector-index.json\nRate Limit 20/m · 9 Langs\nAnti-Hallucination Guard",
             facecolor="#FFFFFF", edgecolor=EMERALD, header_bar=EMERALD, title_size=7.9, sub_size=6.7)

    draw_box(ax, 0.746, 0.470, 0.206, 0.160,
             "POST /api/contact (15s)",
             "shared/validation.js Sync\nHoneypot + 3s Fill Guard\nRate Limit 5/10m · Escape\nGraceful Relay Fallback",
             facecolor="#FFFFFF", edgecolor=TEAL, header_bar=TEAL, title_size=7.9, sub_size=6.7)

    draw_box(ax, 0.746, 0.295, 0.206, 0.135,
             "External Cloud APIs",
             "Google Gemini 3.7 Flash\n(+4 Model Fallback Cascade)\nResend REST Email API",
             facecolor="#FFFFFF", edgecolor=NAVY_MID, header_bar=NAVY_MID, title_size=7.9, sub_size=6.7)

    draw_box(ax, 0.746, 0.148, 0.206, 0.115,
             "CI/CD & Observability",
             "GitHub Push → Vercel Prod\nSecurity Headers · Analytics",
             facecolor="#ECFDF5", edgecolor=EMERALD, title_color=NAVY, title_size=7.9, sub_size=6.8)

    # Clean non-crossing arrows: Left -> Center
    draw_arrow(ax, 0.228, 0.758, 0.292, 0.758, color=TEAL, label="JSON", label_offset=(0, 0.022))
    draw_arrow(ax, 0.228, 0.578, 0.292, 0.578, color=PURPLE, label="GLB", label_offset=(0, 0.022))
    draw_arrow(ax, 0.228, 0.398, 0.292, 0.398, color=AMBER, label="MP4", label_offset=(0, 0.022))

    # Clean non-crossing orthogonal bus at bottom: RAG Ingestion -> /api/chat (via bottom corridor y=0.088 -> right edge x=0.715 -> /api/chat)
    bus_x = [0.1275, 0.1275, 0.712, 0.712]
    bus_y = [0.146, 0.088, 0.088, 0.748]
    ax.plot(bus_x, bus_y, color=EMERALD, linewidth=1.6, linestyle="--", zorder=5)
    draw_arrow(ax, 0.712, 0.748, 0.745, 0.748, color=EMERALD, lw=1.6, ls="--")
    ax.text(0.42, 0.088, "Pre-Built Vector Index (data/vector-index.json — 44 Chunks × 768-d Embeddings)",
            ha="center", va="center", fontsize=7.3, fontweight="bold", color=EMERALD,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor=EMERALD, lw=0.8), zorder=7)

    # Clean arrows: Client Services -> /api/chat and /api/contact (through gap x=0.696..0.728)
    ax.plot([0.679, 0.703, 0.703], [0.235, 0.235, 0.720], color=TEAL, linewidth=1.4, zorder=5)
    draw_arrow(ax, 0.703, 0.720, 0.745, 0.720, color=TEAL, lw=1.4)
    ax.plot([0.679, 0.721, 0.721], [0.195, 0.195, 0.550], color=NAVY_MID, linewidth=1.4, zorder=5)
    draw_arrow(ax, 0.721, 0.550, 0.745, 0.550, color=NAVY_MID, lw=1.4)

    ax.text(0.712, 0.630, "/api/chat", ha="center", va="center", fontsize=6.7, fontweight="bold", color=TEAL,
            rotation=90, bbox=dict(boxstyle="round,pad=0.14", facecolor="#FFFFFF", edgecolor="none"), zorder=7)
    ax.text(0.721, 0.375, "/api/contact", ha="center", va="center", fontsize=6.7, fontweight="bold", color=NAVY_MID,
            rotation=90, bbox=dict(boxstyle="round,pad=0.14", facecolor="#FFFFFF", edgecolor="none"), zorder=7)

    # Clean right-rail bypass arrow from /api/chat -> External Cloud APIs (never crosses /api/contact!)
    ax.plot([0.953, 0.972, 0.972], [0.748, 0.748, 0.362], color=NAVY_MID, linewidth=1.4, linestyle=":", zorder=5)
    draw_arrow(ax, 0.972, 0.362, 0.953, 0.362, color=NAVY_MID, lw=1.4, ls=":")
    # Direct short arrow from /api/contact -> External Cloud APIs
    draw_arrow(ax, 0.849, 0.468, 0.849, 0.432, color=NAVY_MID, lw=1.4)

    # Footer note
    ax.text(0.5, 0.032, "Live Production URL: https://syed-muhammad-ahmad-portfolio.vercel.app   |   GitHub Repository: github.com/akkka-code/3D-Portfolio-Website",
            ha="center", va="center", fontsize=8.0, style="italic", color=TEXT_MUTED)

    out_path = os.path.join(OUT_DIR, "diag_architecture.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    print("Wrote", out_path)


# =============================================================================
# DIAGRAM 2: Per-Frame WebGPU Render Loop & TSL Post-Processing Pipeline
# =============================================================================
def build_render_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(11.2, 5.8), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "PER-FRAME WEBGPU RENDER LOOP & TSL POST-PROCESSING GRAPH",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.922, "Exact Execution Sequence in createRenderLoop.js and postprocessing.js (Zero Custom GLSL — 100% Three.js TSL Node Graph)",
            ha="center", va="center", fontsize=8.4, color=TEXT_MUTED)

    # Row 1: Simulation & Pre-Render Passes (y = 0.61 .. 0.84)
    ax.text(0.025, 0.865, "STAGE A — WORLD SIMULATION & AUXILIARY RENDER TARGETS (CPU + WEBGPU COMPUTE)",
            ha="left", va="center", fontsize=8.4, fontweight="bold", color=TEAL)

    r1_boxes = [
        ("1. Camera & Input", "Orbit / Scroll Waypoints\nor BVH 3rd-Person Walk\n(createCameraDirector)", NAVY),
        ("2. Height-Map Pass", "Ortho Top-Down 100×100m\n512² HalfFloat Nearest RT\nHides Rain/Sky/Smoke/UI", TEAL),
        ("3. GPU Compute Rain", "5,000 Raindrops + Splashes\nfloorY = texture(height).y\nTSL If() Roof Respawn", CYAN),
        ("4. World & Media Sync", "Avatar 3rd-POV + Lip-Sync\n8 Kiosk Videos · Sky · Smoke\nCar UV1 Drops · Ripples", PURPLE),
        ("5. Planar Mirror RT", "Half-Res (0.5×) HalfFloat\nOblique Mirror Camera\nSkip/Frame-Budget Gate", AMBER),
    ]
    bw = 0.172
    gap = 0.022
    x0 = 0.025
    for i, (t, s, c) in enumerate(r1_boxes):
        bx = x0 + i * (bw + gap)
        draw_box(ax, bx, 0.62, bw, 0.21, t, s, facecolor="#FFFFFF", edgecolor=c,
                 header_bar=c, title_size=8.2, sub_size=6.9)
        if i < len(r1_boxes) - 1:
            draw_arrow(ax, bx + bw + 0.002, 0.725, bx + bw + gap - 0.002, 0.725, color=NAVY_MID, lw=1.4)

    # Connector from Stage A to Stage B
    draw_arrow(ax, 0.905, 0.615, 0.905, 0.525, color=NAVY, lw=1.8)
    ax.text(0.895, 0.568, "RenderPipeline.render()", ha="right", va="center",
            fontsize=7.8, fontweight="bold", color=NAVY)

    # Row 2: TSL RenderPipeline Post-Processing Graph (y = 0.25 .. 0.50)
    grp_post = FancyBboxPatch((0.02, 0.22), 0.96, 0.30, boxstyle="round,pad=0.006,rounding_size=0.014",
                              facecolor="#F8FAFC", edgecolor=NAVY_MID, linewidth=1.4, zorder=1)
    ax.add_patch(grp_post)
    ax.text(0.035, 0.495, "STAGE B — THREE.JS TSL RENDERPIPELINE (postprocessing.js + cyberpunkLook.js)",
            ha="left", va="center", fontsize=8.4, fontweight="bold", color=NAVY)

    r2_boxes = [
        ("6. GTAO Pre-Pass", "Depth + Packed ViewNormal\n0.5× Res · 6 Samples\nExcludes Rain & Smoke", NAVY_MID),
        ("7. Scene MRT Pass", "Color (output) + Emissive\nNormalBlending Emissive\nPlanar Ground + Kiosks", TEAL),
        ("8. Bloom & Lensflare", "Emissive-Driven Bloom\n0.5× Res + Ghost Flares\nGaussian Blur (r=4)", PURPLE),
        ("9. Cyberpunk Look", "Distance/Sky Fog + Tint\nGreen Suppress · Contrast\nEdge CA · Vignette · Grain", AMBER),
        ("10. SMAA & Output", "Subpixel Morphological AA\nAdaptive DPR Sample\nWebGPU Canvas Present", EMERALD),
    ]
    for i, (t, s, c) in enumerate(r2_boxes):
        bx = x0 + i * (bw + gap)
        draw_box(ax, bx, 0.25, bw, 0.215, t, s, facecolor="#FFFFFF", edgecolor=c,
                 header_bar=c, title_size=8.2, sub_size=6.9)
        if i < len(r2_boxes) - 1:
            draw_arrow(ax, bx + bw + 0.002, 0.355, bx + bw + gap - 0.002, 0.355, color=NAVY_MID, lw=1.4)

    # Bottom Performance Safeguards strip
    draw_box(ax, 0.025, 0.05, 0.95, 0.125,
             "ADAPTIVE PERFORMANCE SAFEGUARDS (performanceProfile.js & adaptiveDpr.js)",
             "Desktop Max DPR: 1.5×  |  Apple Mobile Cap: 1.25×  |  Sustained FPS < 50 (2 windows) → Drop DPR to 0.85× + Disable DoF, Lensflare & Video Billboards\nHalf-Resolution Buffers (0.5×): Ground Planar Reflection, GTAO, Bloom, Lensflare  |  Modal/Showreel Playback → Pauses Background 3D Kiosk Video Decoders",
             facecolor="#EFF6FF", edgecolor=TEAL, title_color=NAVY, title_size=8.4, sub_size=7.3, lw=1.3)

    out_path = os.path.join(OUT_DIR, "diag_render_pipeline.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    print("Wrote", out_path)


# =============================================================================
# DIAGRAM 3: Hybrid RAG AI Assistant Pipeline (AHMAD.AI)
# =============================================================================
def build_rag_pipeline_diagram():
    fig, ax = plt.subplots(figsize=(11.2, 5.5), dpi=300)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")
    fig.patch.set_facecolor("#FFFFFF")

    ax.text(0.5, 0.96, "HYBRID RAG AI ASSISTANT PIPELINE (AHMAD.AI — MODULE 4)",
            ha="center", va="center", fontsize=12.5, fontweight="bold", color=NAVY)
    ax.text(0.5, 0.922, "Offline Knowledge Ingestion (scripts/ingest.mjs) + Online Hybrid Vector/BM25 Retrieval & Grounded Generation (api/chat.js)",
            ha="center", va="center", fontsize=8.4, color=TEXT_MUTED)

    # Top row: Offline Ingestion
    grp_off = FancyBboxPatch((0.02, 0.56), 0.96, 0.32, boxstyle="round,pad=0.006,rounding_size=0.014",
                             facecolor="#F0FDF4", edgecolor=EMERALD, linewidth=1.3, zorder=1)
    ax.add_patch(grp_off)
    ax.text(0.035, 0.852, "PHASE 1 — OFFLINE INGESTION & VECTOR INDEXING (npm run ingest)",
            ha="left", va="center", fontsize=8.4, fontweight="bold", color=EMERALD)

    off_boxes = [
        ("Source Documents", "content/profile.json\nSyedMuhammadAhmad_CV.pdf\nportfolio-details.md\n(28 Structured Docs)", NAVY),
        ("Structure Chunker", "Heading & Sentence Aware\nChunk Size: 700 chars\nOverlap: 120 chars\n→ 44 Grounded Chunks", TEAL),
        ("Gemini Embeddings", "gemini-embedding-001\n768-Dim Float Vectors\nL2-Normalized for\nDot-Product Cosine Sim", PURPLE),
        ("Pre-Built Artifact", "data/vector-index.json\nBundled in Vercel Function\nZero External DB Latency\n+ Runtime BM25 Index", EMERALD),
    ]
    bw4 = 0.212
    gap4 = 0.030
    x0 = 0.035
    for i, (t, s, c) in enumerate(off_boxes):
        bx = x0 + i * (bw4 + gap4)
        draw_box(ax, bx, 0.59, bw4, 0.23, t, s, facecolor="#FFFFFF", edgecolor=c,
                 header_bar=c, title_size=8.4, sub_size=7.2)
        if i < len(off_boxes) - 1:
            draw_arrow(ax, bx + bw4 + 0.003, 0.705, bx + bw4 + gap4 - 0.003, 0.705, color=EMERALD, lw=1.5)

    # Clean orthogonal dashed corridor from Pre-Built Artifact -> Hybrid Fusion Search
    # Pre-Built Artifact center-x = 0.867, drop into Hybrid Fusion Search left-top at x=0.315 (clear of Phase 2 header)
    ax.plot([0.867, 0.867, 0.315], [0.588, 0.528, 0.528], color=EMERALD, linewidth=1.6, linestyle="--", zorder=5)
    draw_arrow(ax, 0.315, 0.528, 0.315, 0.443, color=EMERALD, lw=1.6, ls="--")
    ax.text(0.59, 0.528, "Loads Pre-Built Index (Cached in Serverless RAM)",
            ha="center", va="center", fontsize=7.4, fontweight="bold", color=EMERALD,
            bbox=dict(boxstyle="round,pad=0.22", facecolor="#FFFFFF", edgecolor=EMERALD, lw=0.8), zorder=7)

    # Bottom row: Online Query & Grounded Generation
    grp_on = FancyBboxPatch((0.02, 0.06), 0.96, 0.435, boxstyle="round,pad=0.006,rounding_size=0.014",
                            facecolor="#EFF6FF", edgecolor=TEAL, linewidth=1.4, zorder=1)
    ax.add_patch(grp_on)
    ax.text(0.34, 0.472, "PHASE 2 — ONLINE HYBRID RETRIEVAL & GROUNDED GENERATION (POST /api/chat)",
            ha="left", va="center", fontsize=8.1, fontweight="bold", color=TEAL)

    on_boxes = [
        ("Visitor Query + Voice", "Text or Web Speech STT\n9 Languages Supported\nOrigin + Rate Limit (20/m)\nFollow-Up Context Expand", NAVY),
        ("Hybrid Fusion Search", "Dense Cosine (Weight 0.75)\n+ BM25 k1=1.4, b=0.75 (0.25)\nPer-Source Diversity Cap\n(Max 2/Source → Top-6)", TEAL),
        ("Grounded LLM Prompt", "Gemini 3.7 Flash (+4 Fallbacks)\nStrict <sources> Grounding\nBracketed Citations [1][2]\nNo Invented Personal Facts", PURPLE),
        ("UI + Avatar Response", "Clickable Section Citations\nWeb Speech TTS Readout\nAvatar Talk + MouthOpen\nBM25 Extractive Fallback", AMBER),
    ]
    for i, (t, s, c) in enumerate(on_boxes):
        bx = x0 + i * (bw4 + gap4)
        draw_box(ax, bx, 0.160, bw4, 0.280, t, s, facecolor="#FFFFFF", edgecolor=c,
                 header_bar=c, title_size=8.4, sub_size=7.1)
        if i < len(on_boxes) - 1:
            draw_arrow(ax, bx + bw4 + 0.003, 0.300, bx + bw4 + gap4 - 0.003, 0.300, color=TEAL, lw=1.5)

    # Formula callout cleanly inside grp_on
    ax.text(0.5, 0.105,
            "Hybrid Score(q, d) = 0.75 · cos(e_q, e_d) + 0.25 · BM25_norm(q, d) · max(cos(e_q, e_d), 0.30)   |   Fallback Guard: hasTopicMatch(q, top3)",
            ha="center", va="center", fontsize=7.2, fontweight="bold", color=NAVY,
            bbox=dict(boxstyle="round,pad=0.32", facecolor="#FFFFFF", edgecolor=TEAL, lw=1.0))

    out_path = os.path.join(OUT_DIR, "diag_rag_pipeline.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    print("Wrote", out_path)


# =============================================================================
# DIAGRAM 4: Production Bundle & 3D Asset Footprint Chart
# =============================================================================
def build_perf_chart():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.2, 4.4), dpi=300)
    fig.patch.set_facecolor("#FFFFFF")
    fig.suptitle("PRODUCTION BUILD FOOTPRINT & 3D ASSET BUDGET ANALYSIS (VITE 6 + WEBGPU)",
                 fontsize=12, fontweight="bold", color=NAVY, y=0.98)

    # Left subplot: Vite 6 Vendor-Split Gzipped Chunks (kB)
    chunks = [
        "vendor-three (WebGPU+TSL)",
        "basis_transcoder.wasm",
        "draco_decoder.wasm (x2)",
        "index.js (App + UI Core)",
        "vendor-gsap (Motion)",
        "index.css (Editorial UI)",
        "vendor-bvh (Collision)",
    ][::-1]
    gzip_kb = [382.45, 247.62, 152.10, 62.14, 27.95, 22.79, 16.18][::-1]
    colors1 = [EMERALD, CYAN, PURPLE, TEAL, AMBER, "#64748B", NAVY]

    bars1 = ax1.barh(chunks, gzip_kb, color=colors1, height=0.62, edgecolor="none")
    ax1.set_title("A. Gzipped JS / CSS / WASM Chunks (kB)", fontsize=9.8, fontweight="bold", color=NAVY, pad=10)
    ax1.set_xlabel("Compressed Transfer Size (kB)", fontsize=8.5, color=TEXT_MUTED)
    ax1.set_xlim(0, 460)
    ax1.grid(axis="x", linestyle="--", alpha=0.45, color="#94A3B8")
    ax1.set_axisbelow(True)
    ax1.spines["top"].set_visible(False)
    ax1.spines["right"].set_visible(False)
    ax1.tick_params(axis="both", labelsize=8)
    for b, val in zip(bars1, gzip_kb):
        ax1.text(val + 7, b.get_y() + b.get_height() / 2, f"{val:.1f} kB",
                 va="center", ha="left", fontsize=7.8, fontweight="bold", color=TEXT_DARK)

    # Right subplot: Key Static 3D & Media Assets (MB) — strictly sorted descending
    assets = [
        "promo.mp4 (1080p Faststart)",
        "cyberpunk_compressed.glb",
        "wet-puddles PBR (3 Maps)",
        "light-rain.mp3 (Ambient)",
        "funky-cyber-groove.mp3",
        "quadra.glb (Car + UV1)",
        "avatar.glb (20-Bone Rig)",
        "plane.glb (Flying Craft)",
    ][::-1]
    sizes_mb = [10.81, 4.64, 3.34, 3.26, 2.79, 2.61, 2.53, 2.42][::-1]
    colors2 = ["#64748B", PURPLE, TEAL, EMERALD, CYAN, TEAL, NAVY, AMBER]

    bars2 = ax2.barh(assets, sizes_mb, color=colors2, height=0.62, edgecolor="none")
    ax2.set_title("B. Key 3D Models, Audio & Showreel Assets (MB)", fontsize=9.8, fontweight="bold", color=NAVY, pad=10)
    ax2.set_xlabel("Disk Size (MB, Cached Immutable via Vercel CDN)", fontsize=8.5, color=TEXT_MUTED)
    ax2.set_xlim(0, 12.8)
    ax2.grid(axis="x", linestyle="--", alpha=0.45, color="#94A3B8")
    ax2.set_axisbelow(True)
    ax2.spines["top"].set_visible(False)
    ax2.spines["right"].set_visible(False)
    ax2.tick_params(axis="both", labelsize=8)
    for b, val in zip(bars2, sizes_mb):
        ax2.text(val + 0.18, b.get_y() + b.get_height() / 2, f"{val:.2f} MB",
                 va="center", ha="left", fontsize=7.8, fontweight="bold", color=TEXT_DARK)

    plt.tight_layout(rect=[0, 0, 1, 0.93])
    out_path = os.path.join(OUT_DIR, "diag_perf_bundle.png")
    plt.savefig(out_path, dpi=300, bbox_inches="tight", facecolor="#FFFFFF")
    plt.close(fig)
    print("Wrote", out_path)


# =============================================================================
# FIGURE: Clean 2x2 Project Gameplay Showcase Collage
# =============================================================================
def build_projects_collage():
    items = [
        (os.path.join(OUT_DIR, "fig_chrono_action.jpg"), "001 // CHRONO REBELLION — Unity HDRP Sci-Fi Shooter"),
        (os.path.join(ROOT, "public", "video", "projects", "behind-the-smile.jpg"), "002 // BEHIND THE SMILE — Global Game Jam 2026 (Unity 3D)"),
        (os.path.join(ROOT, "public", "video", "projects", "paper-dash.jpg"), "003 // PAPER PLANE DASH — Unreal Engine 5 Procedural Runner"),
        (os.path.join(ROOT, "public", "video", "projects", "voxelcraft.jpg"), "005 // VOXELCRAFT 3D — Procedural Block Sandbox Engine"),
    ]
    cw, ch = 800, 450
    pad = 16
    cap_h = 38
    W = cw * 2 + pad * 3
    H = (ch + cap_h) * 2 + pad * 3
    canvas = Image.new("RGB", (W, H), (11, 19, 43))
    draw = ImageDraw.Draw(canvas)

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 20)
    except Exception:
        font = ImageFont.load_default()

    for idx, (path, caption) in enumerate(items):
        col = idx % 2
        row = idx // 2
        x = pad + col * (cw + pad)
        y = pad + row * (ch + cap_h + pad)
        im = Image.open(path).convert("RGB")
        # Center crop to 16:9
        sw, sh = im.size
        target = cw / ch
        if sw / sh > target:
            nw = int(sh * target)
            left = (sw - nw) // 2
            im = im.crop((left, 0, left + nw, sh))
        else:
            nh = int(sw / target)
            top = (sh - nh) // 2
            im = im.crop((0, top, sw, top + nh))
        im = im.resize((cw, ch), Image.Resampling.LANCZOS)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + ch, x + cw, y + ch + cap_h], fill=(15, 23, 42))
        draw.rectangle([x, y, x + cw, y + ch + cap_h], outline=(2, 132, 199), width=2)
        draw.text((x + 12, y + ch + 8), caption, fill=(241, 245, 249), font=font)

    out_path = os.path.join(OUT_DIR, "fig_projects_grid.jpg")
    canvas.save(out_path, quality=92)
    print("Wrote", out_path)


def build_side_by_side(left_path, left_cap, right_path, right_cap, out_name, cw=760, ch=520):
    pad = 18
    cap_h = 40
    W = cw * 2 + pad * 3
    H = ch + cap_h + pad * 2
    canvas = Image.new("RGB", (W, H), (11, 19, 43))
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 19)
    except Exception:
        font = ImageFont.load_default()

    for idx, (path, cap) in enumerate([(left_path, left_cap), (right_path, right_cap)]):
        x = pad + idx * (cw + pad)
        y = pad
        im = Image.open(path).convert("RGB")
        sw, sh = im.size
        target = cw / ch
        if sw / sh > target:
            nw = int(sh * target)
            left = (sw - nw) // 2
            im = im.crop((left, 0, left + nw, sh))
        else:
            nh = int(sw / target)
            top = max(0, int((sh - nh) * 0.25))  # Slight upper-center crop for portraits
            im = im.crop((0, top, sw, min(sh, top + nh)))
        im = im.resize((cw, ch), Image.Resampling.LANCZOS)
        canvas.paste(im, (x, y))
        draw.rectangle([x, y + ch, x + cw, y + ch + cap_h], fill=(15, 23, 42))
        draw.rectangle([x, y, x + cw, y + ch + cap_h], outline=(2, 132, 199), width=2)
        draw.text((x + 12, y + ch + 9), cap, fill=(241, 245, 249), font=font)

    out_path = os.path.join(OUT_DIR, out_name)
    canvas.save(out_path, quality=92)
    print("Wrote", out_path)


if __name__ == "__main__":
    build_architecture_diagram()
    build_render_pipeline_diagram()
    build_rag_pipeline_diagram()
    build_perf_chart()
    build_projects_collage()
    build_side_by_side(
        os.path.join(ROOT, "blender", "avatar_preview.png"),
        "A. Procedural Blender 5.1 Avatar (20-Bone Rig + Neon Rim)",
        os.path.join(ROOT, "public", "images", "ahmad-1.jpg"),
        "B. Reference Styling Photograph (Syed Muhammad Ahmad)",
        "fig_avatar_comparison.jpg",
        cw=720, ch=640,
    )
    build_side_by_side(
        os.path.join(OUT_DIR, "fig_promo_act4_dual.jpg"),
        "A. Act 4 — Dual Engine Comparison (UE5 Blueprints × C++/SFML)",
        os.path.join(OUT_DIR, "fig_promo_act6_xr.jpg"),
        "B. Act 6 — Triple XR Viewport (OpenXR VR · Vuforia AR · OpenCV)",
        "fig_showreel_scenes.jpg",
        cw=820, ch=462,
    )
