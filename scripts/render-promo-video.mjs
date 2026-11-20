#!/usr/bin/env node
/**
 * Builds the 46.8-second 1080p@30fps Editorial Creative-Technologist Showreel
 * (public/video/promo.mp4 and public/video/promo-poster.jpg) matching the
 * exact samsy.ninja design system:
 *   - Color Palette: #07070A Obsidian Void, #0D0D12 Elevated Panels, #F4F4F6 Off-White,
 *     #DDFB24 Surgical Acid-Lime Accent, and 1px Swiss Architectural Hairlines
 *   - Motion System:
 *       - Sharp Kinetic Typography Slide-Up Reveals with Cubic Ease-Out
 *       - Crisp Architectural Mask Shutter Wipes (with 2px #DDFB24 leading edge)
 *       - Smooth Eased Camera Push-In & Pan on 1080p Gameplay Footage
 *       - Rhythmic Beat-Grid Pacing synced to 116 BPM Funky Cyber Groove
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, statSync, writeFileSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const FFMPEG = join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe");
const PROJ_DIR = join(ROOT, "public", "video", "projects");
const OVR_DIR = join(ROOT, "video", "overlays");
const SEG_DIR = join(ROOT, "video", "segments");
const OUT_MP4 = join(ROOT, "public", "video", "promo.mp4");
const OUT_POSTER = join(ROOT, "public", "video", "promo-poster.jpg");
const MUSIC_WAV = join(ROOT, "video", "music", "funky-cyber-groove.wav");

mkdirSync(SEG_DIR, { recursive: true });
mkdirSync(join(ROOT, "public", "video"), { recursive: true });

// Regenerate the 9 editorial overlays
execFileSync("python", ["video/make_hud_overlays.py"], { stdio: "inherit" });

function runFfmpeg(args) {
  execFileSync(FFMPEG, ["-y", ...args], { stdio: "pipe" });
}

/**
 * Editorial Motion Overlay Expression:
 *   1. Smooth cubic ease-out vertical slide-up on the HUD typography layer:
 *      y = 'if(lt(t,0.42), 36*pow(1-t/0.42,3), 0)'
 *   2. Crisp horizontal mask wipe on scene entry (fade=t=in:st=0:d=0.24) and exit.
 */
function editorialHudOverlayAndWipe(dur) {
  const fadeOutStart = (dur - 0.22).toFixed(2);
  return `overlay=x=0:y='if(lt(t,0.44),42*pow(1-t/0.44,3),0)',fade=t=in:st=0:d=0.22,fade=t=out:st=${fadeOutStart}:d=0.22`;
}

/**
 * Helper 1: Full-screen crystal-clear 1080p gameplay + smooth eased camera pan + editorial kinetic overlay
 */
function buildFullScreenScene(segName, dur, videoFile, seekSec, overlayPng) {
  const outPath = join(SEG_DIR, segName);
  const complex = [
    `[0:v]scale=2020:1136:force_original_aspect_ratio=increase,crop=1920:1080:x='(in_w-1920)/2+36*sin(t*0.55)':y='(in_h-1080)/2',fps=30,eq=contrast=1.05:saturation=1.10,format=rgba[bg]`,
    `[1:v]scale=1920:1080,format=rgba[hud]`,
    `[bg][hud]${editorialHudOverlayAndWipe(dur)},format=yuv420p[outv]`,
  ].join(";");

  runFfmpeg([
    "-ss", String(seekSec), "-t", String(dur), "-i", join(PROJ_DIR, videoFile),
    "-loop", "1", "-t", String(dur), "-i", join(OVR_DIR, overlayPng),
    "-filter_complex", complex,
    "-map", "[outv]",
    "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
    outPath,
  ]);
  return outPath;
}

/**
 * Helper 2: 2x2 Quad-Grid Simultaneous 4-Game Architectural Matrix + Editorial Overlay
 */
function buildQuadGridScene(segName, dur, vids, seeks, overlayPng, dimBg = 0.0) {
  const outPath = join(SEG_DIR, segName);
  const eqStr = dimBg < 0 ? `,eq=brightness=${dimBg}:saturation=1.08` : `,eq=contrast=1.05:saturation=1.10`;
  const complex = [
    `[0:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v0]`,
    `[1:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v1]`,
    `[2:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v2]`,
    `[3:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v3]`,
    `[v0][v1]hstack=inputs=2[top]`,
    `[v2][v3]hstack=inputs=2[bot]`,
    `[top][bot]vstack=inputs=2,format=rgba[grid]`,
    `[4:v]scale=1920:1080,format=rgba[hud]`,
    `[grid][hud]${editorialHudOverlayAndWipe(dur)},format=yuv420p[outv]`,
  ].join(";");

  runFfmpeg([
    "-ss", String(seeks[0]), "-t", String(dur), "-i", join(PROJ_DIR, vids[0]),
    "-ss", String(seeks[1]), "-t", String(dur), "-i", join(PROJ_DIR, vids[1]),
    "-ss", String(seeks[2]), "-t", String(dur), "-i", join(PROJ_DIR, vids[2]),
    "-ss", String(seeks[3]), "-t", String(dur), "-i", join(PROJ_DIR, vids[3]),
    "-loop", "1", "-t", String(dur), "-i", join(OVR_DIR, overlayPng),
    "-filter_complex", complex,
    "-map", "[outv]",
    "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
    outPath,
  ]);
  return outPath;
}

/**
 * Helper 3: Dual Side-by-Side Split-Screen Editorial Comparison
 */
function buildDualSplitScene(segName, dur, leftVid, leftSeek, rightVid, rightSeek, overlayPng) {
  const outPath = join(SEG_DIR, segName);
  const complex = [
    `[0:v]scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,fps=30,eq=contrast=1.05:saturation=1.10[left]`,
    `[1:v]scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,fps=30,eq=contrast=1.05:saturation=1.10[right]`,
    `[left][right]hstack=inputs=2,format=rgba[split]`,
    `[2:v]scale=1920:1080,format=rgba[hud]`,
    `[split][hud]${editorialHudOverlayAndWipe(dur)},format=yuv420p[outv]`,
  ].join(";");

  runFfmpeg([
    "-ss", String(leftSeek), "-t", String(dur), "-i", join(PROJ_DIR, leftVid),
    "-ss", String(rightSeek), "-t", String(dur), "-i", join(PROJ_DIR, rightVid),
    "-loop", "1", "-t", String(dur), "-i", join(OVR_DIR, overlayPng),
    "-filter_complex", complex,
    "-map", "[outv]",
    "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
    outPath,
  ]);
  return outPath;
}

/**
 * Helper 4: 3-Panel XR Triple Viewport (1080x1080 Left + two 840x540 Right stacked)
 */
function buildTripleXrScene(segName, dur, leftVid, topRightVid, botRightVid, overlayPng) {
  const outPath = join(SEG_DIR, segName);
  const complex = [
    `[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,fps=30,eq=contrast=1.05:saturation=1.10[left]`,
    `[1:v]scale=840:540:force_original_aspect_ratio=increase,crop=840:540,fps=30,eq=contrast=1.05:saturation=1.10[tr]`,
    `[2:v]scale=840:540:force_original_aspect_ratio=increase,crop=840:540,fps=30,eq=contrast=1.05:saturation=1.10[br]`,
    `[tr][br]vstack=inputs=2[right]`,
    `[left][right]hstack=inputs=2,format=rgba[triple]`,
    `[3:v]scale=1920:1080,format=rgba[hud]`,
    `[triple][hud]${editorialHudOverlayAndWipe(dur)},format=yuv420p[outv]`,
  ].join(";");

  runFfmpeg([
    "-ss", "1", "-t", String(dur), "-i", join(PROJ_DIR, leftVid),
    "-ss", "1", "-t", String(dur), "-i", join(PROJ_DIR, topRightVid),
    "-ss", "1", "-t", String(dur), "-i", join(PROJ_DIR, botRightVid),
    "-loop", "1", "-t", String(dur), "-i", join(OVR_DIR, overlayPng),
    "-filter_complex", complex,
    "-map", "[outv]",
    "-r", "30", "-an", "-c:v", "libx264", "-preset", "veryfast", "-crf", "19", "-pix_fmt", "yuv420p",
    outPath,
  ]);
  return outPath;
}

console.log("1/9 Rendering Editorial Act 1 (0.0 - 4.8s): Hero Statement & Kinetic Typography...");
const s1 = buildQuadGridScene(
  "s1_intro.mp4",
  4.8,
  ["chrono-rebellion.mp4", "behind-the-smile.mp4", "paper-dash.mp4", "voxelcraft.mp4"],
  [0.5, 1.0, 0.5, 1.0],
  "hud_scene1_intro.png",
  -0.15,
);

console.log("2/9 Rendering Editorial Act 2 (4.8 - 10.2s): 001 // Chrono Rebellion Case Study...");
const s2 = buildFullScreenScene("s2_chrono.mp4", 5.4, "chrono-rebellion.mp4", 2.0, "hud_scene2_chrono.png");

console.log("3/9 Rendering Editorial Act 3 (10.2 - 15.6s): 002 // Behind the Smile Case Study...");
const s3 = buildFullScreenScene("s3_smile.mp4", 5.4, "behind-the-smile.mp4", 2.0, "hud_scene3_smile.png");

console.log("4/9 Rendering Editorial Act 4 (15.6 - 21.0s): 003 × 006 // Dual Split Comparison...");
const s4 = buildDualSplitScene("s4_dual.mp4", 5.4, "paper-dash.mp4", 1.5, "pac-man.mp4", 1.0, "hud_scene4_dual.png");

console.log("5/9 Rendering Editorial Act 5 (21.0 - 26.2s): 005 // Voxelcraft 3D Case Study...");
const s5 = buildFullScreenScene("s5_voxel.mp4", 5.2, "voxelcraft.mp4", 2.0, "hud_scene5_voxel.png");

console.log("6/9 Rendering Editorial Act 6 (26.2 - 31.8s): 004 × 007 × 008 // Triple XR Suite...");
const s6 = buildTripleXrScene("s6_xr.mp4", 5.6, "solar-system.mp4", "ar-memory.mp4", "ar-face-filter.mp4", "hud_scene6_xr.png");

console.log("7/9 Rendering Editorial Act 7 (31.8 - 37.0s): (02) // Custom Blender 5.1 3D Avatar & Stack...");
const s7 = buildFullScreenScene("s7_avatar.mp4", 5.2, "chrono-rebellion.mp4", 7.5, "hud_scene7_avatar.png");

console.log("8/9 Rendering Editorial Act 8 (37.0 - 41.6s): (01) // 09 Works Architectural Matrix...");
const s8 = buildQuadGridScene(
  "s8_quad.mp4",
  4.6,
  ["solar-system.mp4", "pac-man.mp4", "ar-memory.mp4", "paper-dash.mp4"],
  [3.0, 3.0, 2.5, 4.0],
  "hud_scene8_quad.png",
  0.0,
);

console.log("9/9 Rendering Editorial Act 9 (41.6 - 46.8s): (04) // Direct Transmission Outro...");
const s9 = buildQuadGridScene(
  "s9_outro.mp4",
  5.2,
  ["behind-the-smile.mp4", "chrono-rebellion.mp4", "voxelcraft.mp4", "ar-face-filter.mp4"],
  [4.0, 5.0, 4.0, 2.0],
  "hud_scene9_outro.png",
  -0.16,
);

const allSegs = [s1, s2, s3, s4, s5, s6, s7, s8, s9];
const concatListPath = join(SEG_DIR, "concat_list.txt");
writeFileSync(
  concatListPath,
  allSegs.map((p) => `file '${p.replace(/\\/g, "/")}'`).join("\n") + "\n",
  "utf8",
);

console.log("Concatenating 9 editorial scenes with 116 BPM soundtrack...");
runFfmpeg([
  "-f", "concat",
  "-safe", "0",
  "-i", concatListPath,
  "-i", MUSIC_WAV,
  "-map", "0:v:0",
  "-map", "1:a:0",
  "-c:v", "libx264",
  "-preset", "slow",
  "-crf", "25",
  "-maxrate", "1800k",
  "-bufsize", "3600k",
  "-g", "60",
  "-pix_fmt", "yuv420p",
  "-r", "30",
  "-af", "afade=t=in:st=0:d=0.6,afade=t=out:st=44.8:d=2.0",
  "-c:a", "aac",
  "-b:a", "160k",
  "-shortest",
  "-movflags", "+faststart",
  OUT_MP4,
]);

runFfmpeg([
  "-ss", "1.5",
  "-i", OUT_MP4,
  "-frames:v", "1",
  "-q:v", "2",
  OUT_POSTER,
]);

const sizeMb = (statSync(OUT_MP4).size / 1024 / 1024).toFixed(2);
console.log(`✅ Built Editorial Showreel ${OUT_MP4} (${sizeMb} MB) and ${OUT_POSTER}`);
