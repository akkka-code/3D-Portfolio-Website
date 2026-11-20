#!/usr/bin/env node
/**
 * Builds the high-energy 46.5-second 1080p@30fps Cyberpunk Game Developer Trailer
 * (public/video/promo.mp4 and public/video/promo-poster.jpg) featuring:
 *   - 2x2 Simultaneous 4-Game Quad Grids
 *   - Dual Split-Screen Arcade Showdowns (Paper Plane Dash x Pac-Man)
 *   - 3-Panel XR Viewports (Solar System VR x AR Memory x AR Face Filter)
 *   - Full-Screen Crystal-Clear 1080p Gameplay Action Cuts (Chrono Rebellion, Behind the Smile, Voxelcraft 3D)
 *   - Custom 3D Blender Avatar & Real Portrait HUD Composites
 *   - Chamfered Sci-Fi HUD Overlays + RGB Chromatic Glitch Transitions + Animated Progress Telemetry
 *   - 116 BPM Electro-Funk / Cyberpunk Synth-Funk Soundtrack (video/music/funky-cyber-groove.wav)
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

// Ensure overlays are up-to-date
execFileSync("python", ["video/make_hud_overlays.py"], { stdio: "inherit" });

function runFfmpeg(args) {
  execFileSync(FFMPEG, ["-y", ...args], { stdio: "pipe" });
}

/**
 * Adds a punchy cyberpunk RGB-split glitch transition on entry (first 0.28s) and exit (last 0.24s)
 * plus a dynamic animated cyan progress bar along the bottom HUD rail.
 */
function glitchAndHudBar(dur) {
  const endStart = (dur - 0.25).toFixed(2);
  return [
    `rgbashift=rh=14:bh=-14:rv=4:enable='lt(t,0.28)+gt(t,${endStart})'`,
    `fade=t=in:st=0:d=0.18`,
  ].join(",");
}

/**
 * Helper 1: Full-screen crystal-clear 1080p gameplay + Sci-Fi HUD overlay PNG + RGB glitch cut
 */
function buildFullScreenScene(segName, dur, videoFile, seekSec, overlayPng) {
  const outPath = join(SEG_DIR, segName);
  const complex = [
    `[0:v]scale=2040:1148:force_original_aspect_ratio=increase,crop=1920:1080:x='(in_w-1920)/2+40*sin(t*0.7)':y='(in_h-1080)/2',fps=30,eq=contrast=1.06:saturation=1.18,format=rgba[bg]`,
    `[1:v]scale=1920:1080,format=rgba[hud]`,
    `[bg][hud]overlay=0:0,${glitchAndHudBar(dur)},format=yuv420p[outv]`,
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
 * Helper 2: 2x2 Quad-Grid Simultaneous 4-Game Montage + Sci-Fi HUD overlay PNG
 */
function buildQuadGridScene(segName, dur, vids, seeks, overlayPng, dimBg = 0.0) {
  const outPath = join(SEG_DIR, segName);
  const eqStr = dimBg < 0 ? `,eq=brightness=${dimBg}:saturation=1.18` : `,eq=contrast=1.05:saturation=1.16`;
  const complex = [
    `[0:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v0]`,
    `[1:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v1]`,
    `[2:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v2]`,
    `[3:v]scale=960:540:force_original_aspect_ratio=increase,crop=960:540,fps=30${eqStr}[v3]`,
    `[v0][v1]hstack=inputs=2[top]`,
    `[v2][v3]hstack=inputs=2[bot]`,
    `[top][bot]vstack=inputs=2,format=rgba[grid]`,
    `[4:v]scale=1920:1080,format=rgba[hud]`,
    `[grid][hud]overlay=0:0,${glitchAndHudBar(dur)},format=yuv420p[outv]`,
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
 * Helper 3: Dual Side-by-Side Split-Screen Gameplay Showdown + Sci-Fi HUD overlay PNG
 */
function buildDualSplitScene(segName, dur, leftVid, leftSeek, rightVid, rightSeek, overlayPng) {
  const outPath = join(SEG_DIR, segName);
  const complex = [
    `[0:v]scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,fps=30,eq=contrast=1.06:saturation=1.18[left]`,
    `[1:v]scale=960:1080:force_original_aspect_ratio=increase,crop=960:1080,fps=30,eq=contrast=1.06:saturation=1.18[right]`,
    `[left][right]hstack=inputs=2,format=rgba[split]`,
    `[2:v]scale=1920:1080,format=rgba[hud]`,
    `[split][hud]overlay=0:0,${glitchAndHudBar(dur)},format=yuv420p[outv]`,
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
    `[0:v]scale=1080:1080:force_original_aspect_ratio=increase,crop=1080:1080,fps=30,eq=contrast=1.06:saturation=1.18[left]`,
    `[1:v]scale=840:540:force_original_aspect_ratio=increase,crop=840:540,fps=30,eq=contrast=1.06:saturation=1.18[tr]`,
    `[2:v]scale=840:540:force_original_aspect_ratio=increase,crop=840:540,fps=30,eq=contrast=1.06:saturation=1.18[br]`,
    `[tr][br]vstack=inputs=2[right]`,
    `[left][right]hstack=inputs=2,format=rgba[triple]`,
    `[3:v]scale=1920:1080,format=rgba[hud]`,
    `[triple][hud]overlay=0:0,${glitchAndHudBar(dur)},format=yuv420p[outv]`,
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

console.log("1/9 Rendering Scene 1 (0.0 - 4.8s): 4-Game Quad Cold Open + Developer Profile HUD...");
const s1 = buildQuadGridScene(
  "s1_intro.mp4",
  4.8,
  ["chrono-rebellion.mp4", "behind-the-smile.mp4", "paper-dash.mp4", "voxelcraft.mp4"],
  [0.5, 1.0, 0.5, 1.0],
  "hud_scene1_intro.png",
  -0.12,
);

console.log("2/9 Rendering Scene 2 (4.8 - 10.2s): Chrono Rebellion Full-Screen HD Combat...");
const s2 = buildFullScreenScene("s2_chrono.mp4", 5.4, "chrono-rebellion.mp4", 2.0, "hud_scene2_chrono.png");

console.log("3/9 Rendering Scene 3 (10.2 - 15.6s): Behind the Smile (GGJ26) Full-Screen HD...");
const s3 = buildFullScreenScene("s3_smile.mp4", 5.4, "behind-the-smile.mp4", 2.0, "hud_scene3_smile.png");

console.log("4/9 Rendering Scene 4 (15.6 - 21.0s): Dual Split-Screen Arcade Showdown (Paper Plane Dash x Pac-Man)...");
const s4 = buildDualSplitScene("s4_dual.mp4", 5.4, "paper-dash.mp4", 1.5, "pac-man.mp4", 1.0, "hud_scene4_dual.png");

console.log("5/9 Rendering Scene 5 (21.0 - 26.2s): Voxelcraft 3D Procedural Sandbox Full-Screen HD...");
const s5 = buildFullScreenScene("s5_voxel.mp4", 5.2, "voxelcraft.mp4", 2.0, "hud_scene5_voxel.png");

console.log("6/9 Rendering Scene 6 (26.2 - 31.8s): Triple XR Viewport (Solar System VR x AR Memory x AR Face Filter)...");
const s6 = buildTripleXrScene("s6_xr.mp4", 5.6, "solar-system.mp4", "ar-memory.mp4", "ar-face-filter.mp4", "hud_scene6_xr.png");

console.log("7/9 Rendering Scene 7 (31.8 - 37.0s): Custom 3D Blender Avatar & Technical Arsenal HUD...");
const s7 = buildFullScreenScene("s7_avatar.mp4", 5.2, "chrono-rebellion.mp4", 7.5, "hud_scene7_avatar.png");

console.log("8/9 Rendering Scene 8 (37.0 - 41.6s): 4-Up Quad-Grid All-Games Rapid Action Matrix...");
const s8 = buildQuadGridScene(
  "s8_quad.mp4",
  4.6,
  ["solar-system.mp4", "pac-man.mp4", "ar-memory.mp4", "paper-dash.mp4"],
  [3.0, 3.0, 2.5, 4.0],
  "hud_scene8_quad.png",
  0.0,
);

console.log("9/9 Rendering Scene 9 (41.6 - 46.8s): Finale Command Deck & Call To Action...");
const s9 = buildQuadGridScene(
  "s9_outro.mp4",
  5.2,
  ["behind-the-smile.mp4", "chrono-rebellion.mp4", "voxelcraft.mp4", "ar-face-filter.mp4"],
  [4.0, 5.0, 4.0, 2.0],
  "hud_scene9_outro.png",
  -0.14,
);

const allSegs = [s1, s2, s3, s4, s5, s6, s7, s8, s9];
const concatListPath = join(SEG_DIR, "concat_list.txt");
writeFileSync(
  concatListPath,
  allSegs.map((p) => `file '${p.replace(/\\/g, "/")}'`).join("\n") + "\n",
  "utf8",
);

console.log("Concatenating 9 high-energy scenes with 116 BPM Funky Cyber Groove soundtrack...");
runFfmpeg([
  "-f", "concat",
  "-safe", "0",
  "-i", concatListPath,
  "-i", MUSIC_WAV,
  "-map", "0:v:0",
  "-map", "1:a:0",
  "-c:v", "libx264",
  "-preset", "fast",
  "-crf", "20",
  "-pix_fmt", "yuv420p",
  "-r", "30",
  "-c:a", "aac",
  "-b:a", "192k",
  "-shortest",
  "-movflags", "+faststart",
  OUT_MP4,
]);

// Extract a vibrant poster frame from Scene 1
runFfmpeg([
  "-ss", "1.5",
  "-i", OUT_MP4,
  "-frames:v", "1",
  "-q:v", "2",
  OUT_POSTER,
]);

const sizeMb = (statSync(OUT_MP4).size / 1024 / 1024).toFixed(2);
console.log(`✅ Built remade Sci-Fi Trailer ${OUT_MP4} (${sizeMb} MB) and ${OUT_POSTER}`);
