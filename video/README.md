# Module 3 — Editorial Promotional Showreel (Adobe After Effects)

## Design System & Visual Architecture
Rebuilt to match the exact **samsy.ninja** minimalist creative-technologist editorial design system extracted from [`src/portfolio/portfolio.css`](../src/portfolio/portfolio.css) and [`src/portfolio/createPortfolioUI.js`](../src/portfolio/createPortfolioUI.js):

### 1. Color Palette
- **Obsidian Void (`--sn-bg-solid`)**: `#07070A` (`RGB [7, 7, 10]`)
- **Elevated Surface (`--sn-bg-elev`)**: `#0D0D12` (`RGB [13, 13, 18]`)
- **Card Surface (`--sn-bg-card`)**: `#0F0F16` (`RGB [15, 15, 22]`)
- **Primary Off-White (`--sn-fg`)**: `#F4F4F6` (`RGB [244, 244, 246]`)
- **Muted Silver (`--sn-fg-muted`)**: `#8E8E96` (`rgba(244, 244, 246, 0.56)`)
- **Swiss Architectural Hairline (`--sn-line`)**: `1px solid rgba(244, 244, 246, 0.16)`
- **Surgical Acid-Lime Accent (`--sn-accent`)**: `#DDFB24` (`RGB [221, 251, 36]`)
- **Availability Status Dot (`--sn-success`)**: `#18F2A0` (`RGB [24, 242, 160]`)

### 2. Typography & Motion Language
- **Display Headlines**: Bold uppercase kinetic typography (`Syne` / `Space Grotesk` / `Bahnschrift Bold`, tight `-0.04em` tracking) paired with hollow outline stroke display lines (`-webkit-text-stroke: 1.5px #F4F4F6`).
- **Technical Metadata & Tags**: Monospace indices (`001`–`009`, `(01) — SELECTED WORKS`) and rectangular `1px` hairline tech tags (`JetBrains Mono` / `Consolas`).
- **Motion System**:
  - High-influence cubic-bezier easing (`KeyframeEase(0, 85)` incoming / `KeyframeEase(0, 35)` outgoing in After Effects; `42*pow(1-t/0.44,3)` cubic ease-out in FFmpeg).
  - Crisp rectangular mask shutter wipes and animated `1px` Swiss hairline rules.
  - Rhythmic pacing synced to the **116 BPM Electro-Funk / Synth-Funk** beat grid (`video/music/funky-cyber-groove.wav`).

---

## 9-Act Editorial Storyboard (46.8s · 1920×1080 @ 30fps)

| Time | Act | Title & Visual Architecture |
|------|-----|-----------------------------|
| `0.0 – 4.8s` | **Act 1** | **`(00)` Hero Statement**: 2×2 architectural grid backdrop, kinetic display typography (`SYED MUHAMMAD / AHMAD — AKKA® / INTERACTIVE 3D & / GAME ARCHITECT.`), metrics (`08+`, `UNITY · UE5`, `GGJ 2026`), and framed portrait. |
| `4.8 – 10.2s` | **Act 2** | **`001` Chrono Rebellion**: Full-screen 1080p Unity HDRP combat footage with smooth eased camera pan and minimalist lower-left Swiss case study card. |
| `10.2 – 15.6s` | **Act 3** | **`002` Behind the Smile**: Full-screen 1080p Global Game Jam 2026 narrative exploration showcase with cubic-eased kinetic lower-third reveal. |
| `15.6 – 21.0s` | **Act 4** | **`003 × 006` Dual Engine Comparison**: Side-by-side split-screen comparison of *Paper Plane Dash* (Unreal Engine 5 Blueprints) and *Pac-Man* (C++ / SFML / QuadTrees & Graph AI). |
| `21.0 – 26.2s` | **Act 5** | **`005` Voxelcraft 3D**: Full-screen 1080p procedural voxel sandbox engine showcase with `1px` hairline metadata tags. |
| `26.2 – 31.8s` | **Act 6** | **`004 × 007 × 008` Extended Reality Suite**: 3-viewport architectural split showcasing *Solar System Exploration (VR)*, *AR Memory Card Game (Vuforia)*, and *AR Face Filter (Python / OpenCV / MediaPipe)*. |
| `31.8 – 37.0s` | **Act 7** | **`(02)` 3D Character Lab & Capabilities**: Custom rigged Blender 5.1 3D Avatar (`21 bones · 6 NLA tracks · 3rd-person walk`) alongside the 4-row technical capabilities matrix. |
| `37.0 – 41.6s` | **Act 8** | **`(01)` Curated Project Index Matrix**: 4-up simultaneous gameplay quad grid with central Swiss architectural index plaque (`09 SELECTED WORKS`). |
| `41.6 – 46.8s` | **Act 9** | **`(04)` Direct Transmission Outro**: Editorial contact table (`syed-muhammad-ahmad-portfolio.vercel.app`, `ahmedakka765@gmail.com`, `+92 332 2669028`, LinkedIn, NED University) flanked by portrait and 3D avatar frames. |

---

## Rebuild Commands
1. **Regenerate After Effects project (`video/promo.aep`)**:
   ```powershell
   & "C:\Program Files\Adobe\Adobe After Effects 2027\Support Files\AfterFX.exe" -noui -r "d:\Projects v1\Portfolio Website\video\build_promo.jsx"
   ```
2. **Render 1080p MP4 & Poster (`public/video/promo.mp4`, `public/video/promo-poster.jpg`)**:
   ```powershell
   node scripts/render-promo-video.mjs
   ```
