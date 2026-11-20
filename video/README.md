# Module 3 — Short Animated Promotional Video (Adobe After Effects)

## Overview
This folder contains the promotional video pipeline for **Syed Muhammad Ahmad (AKKA)**, introducing his background, technical skills, game development projects, and achievements in a 46-second 1080p@30fps showcase synced to an original synthesized dark-synthwave soundtrack.

## Deliverables
- `video/build_promo.jsx` — ExtendScript automation script for Adobe After Effects (`PROMO_MAIN` composition, 1920×1080, 30 fps, 46.0 s) reading directly from `content/profile.json`.
- `video/promo.aep` — Adobe After Effects project file.
- `video/music/make_music.py` & `video/music/promo_music.wav` — Original 100 BPM dark-synthwave soundtrack synthesized purely from the Python standard library (`wave`, `math`, `struct`, `random`), released under CC0 1.0 (100% copyright-safe).
- `public/video/promo.mp4` — Final 1920×1080 H.264 + AAC promotional video embedded in the portfolio website.
- `public/video/promo-poster.jpg` — High-resolution poster frame for the HTML5 video player.

## Storyboard (Synced to 100 BPM Bar Grid, 1 Bar = 2.4 s)

| Time | Bars | Scene | Visuals, Typography & Transitions |
|------|------|-------|-----------------------------------|
| `0.0 – 4.8 s` | 0–1 | **00 // Cyber Boot & Identity** | Blurred gameplay backdrop, neon cyan/magenta HUD bars, kinetic fade-in of `SYED MUHAMMAD AHMAD`, role badge (`Game Developer · Game Programmer · Graphic Designer`), and NED University affiliation. |
| `4.8 – 12.0 s` | 2–4 | **01 // Technical Arsenal** | 4 glassmorphic skill cards with cyan, magenta, and yellow accent borders highlighting Game Engines (Unity, Unreal Engine 5), Programming (C#, C++, C, Python), XR (OpenXR, Vuforia, OpenCV, MediaPipe), and 3D/Design/AI (Blender, Three.js WebGPU, RAG). |
| `12.0 – 17.4 s` | 5–6 | **02A // Chrono Rebellion** | Full-HD gameplay footage of *Chrono Rebellion* (Unity, C#, HDRP) with lower-third cyber telemetry card. |
| `17.4 – 22.8 s` | 7–8 | **02B // Behind the Smile** | Gameplay showcase of *Behind the Smile* (Global Game Jam 2026, 48-hour narrative 3D game). |
| `22.8 – 28.2 s` | 9–11 | **02C // Paper Plane Dash** | Gameplay showcase of *Paper Plane Dash* (Unreal Engine 5, Blueprints procedural endless runner). |
| `28.2 – 33.6 s` | 11–13 | **02D // Solar System VR** | Gameplay showcase of *Solar System Exploration VR* (Unity, OpenXR, XR Interaction Toolkit). |
| `33.6 – 38.4 s` | 14–15 | **03 // More Demos & Honors** | Highlights of *Voxelcraft 3D*, *Pac-Man (C++/SFML)*, *AR Memory Card*, *AR Face Filter*, and CEGA / Coursera Google AI certifications. |
| `38.4 – 46.0 s` | 16–18 | **04 // Call to Action & Outro** | Invitation to walk the live 3D cyberpunk alley, interact with the 3D avatar, and query the RAG AI assistant, with contact links and fade-to-black. |

## How to Rebuild
1. **Regenerate soundtrack**:
   ```powershell
   python video/music/make_music.py
   ```
2. **Generate/Update After Effects `.aep` project**:
   Open Adobe After Effects and run `File -> Scripts -> Run Script File... -> video/build_promo.jsx` (or run via CLI with `AfterFX.exe -r`).
3. **Render final MP4 & poster**:
   ```powershell
   node scripts/render-promo-video.mjs
   ```
