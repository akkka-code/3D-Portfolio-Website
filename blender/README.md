# Module 2 — Custom 3D Avatar in Blender 5.1

## Overview
This folder contains the procedural Blender 5.1 pipeline that models, shades, rigs, animates, and exports the stylized 3D avatar of **Syed Muhammad Ahmad (AKKA)**.

## Deliverables
- `blender/build_avatar.py` — Re-runnable Python script that generates the entire avatar from scratch.
- `blender/avatar.blend` — Saved Blender 5.1 native project file containing all meshes, materials, armature, shape keys, and NLA animation tracks.
- `public/models/avatar.glb` — Web-ready glTF 2.0 binary (~1.3 MB) loaded into the Three.js WebGPU scene.
- `blender/avatar_preview.png` — 1024×1024 studio preview render with cyberpunk 3-point neon rim lighting.

## Character Design & Materials
- **Likeness**: Styled after reference photographs of Syed Muhammad Ahmad — voluminous dark swept-up hair quiff, dark brown eyes with catchlights, sleek dark-rimmed glasses, neat moustache, jawline stubble, and olive-charcoal leather biker jacket over a black inner shirt.
- **Cyberpunk Accents**: Emissive cyan (`#00E5FF`) jacket zipper piping, belt buckle, and left wrist cuff; emissive magenta (`#FF2BD6`) right wrist cuff and sneaker heel accents that bloom in the WebGPU post-processing pipeline.
- **Materials**: Principled BSDF materials (`Skin`, `Stubble`, `Hair`, `BikerJacket`, `BlackShirt`, `DarkJeans`, `Sneakers`, `GlassesFrame`, `NeonCyan`, `NeonMagenta`) for 100% glTF PBR compatibility.

## Rigging, Animations & Facial Expressions
- **Skeleton (`AvatarRig`)**: 18 bones (`Root`, `Hips`, `Spine`, `Chest`, `Neck`, `Head`, `Shoulder.L/R`, `UpperArm.L/R`, `LowerArm.L/R`, `Hand.L/R`, `UpperLeg.L/R`, `LowerLeg.L/R`, `Foot.L/R`).
- **Animation Clips (NLA Tracks)**:
  1. `Idle` (4.0 s loop) — Subtle breathing, weight shift, and natural head movement.
  2. `Wave` (2.5 s) — Friendly right-hand wave greeting visitors.
  3. `Talk` (3.0 s loop) — Conversational hand gestures and head nods triggered when the RAG AI Chatbot speaks.
  4. `Point` (2.0 s) — Presenting gesture toward portfolio cards.
  5. `Victory` (2.0 s) — Celebratory gamer double fist-pump.
- **Morph Targets (`HeadMesh` Shape Keys)**:
  - `Blink` — Automatic periodic eye blink in the render loop.
  - `Smile` — Friendly expression triggered on hover/wave.
  - `MouthOpen` — Driven dynamically while the AI voice assistant speaks.

## Re-building from Scratch
```powershell
& "C:\Program Files\Blender Foundation\Blender 5.1\blender.exe" -b --factory-startup --python blender\build_avatar.py
```
