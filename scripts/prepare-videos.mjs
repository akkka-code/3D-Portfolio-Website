#!/usr/bin/env node
/**
 * Compress gameplay videos and extract poster thumbnails into public/video/projects/
 * and billboard loops into public/video/billboards/.
 */
import { execFileSync } from "node:child_process";
import { mkdirSync, existsSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const SRC_DIR = "d:\\NED UNIVERSITY [All Data]\\Gameplay Videos";
const OUT_DIR = join(ROOT, "public", "video", "projects");
const BILLBOARD_DIR = join(ROOT, "public", "video", "billboards");
const FFMPEG = join(ROOT, "node_modules", "ffmpeg-static", "ffmpeg.exe");
const FFPROBE = join(ROOT, "node_modules", "ffprobe-static", "bin", "win32", "x64", "ffprobe.exe");

mkdirSync(OUT_DIR, { recursive: true });
mkdirSync(BILLBOARD_DIR, { recursive: true });

const VIDEOS = [
  { src: "Chrono Rebellion Gameplay 2.0.mp4", slug: "chrono-rebellion", start: 6, dur: 22 },
  { src: "Behind the Smile Gameplay.mp4", slug: "behind-the-smile", start: 5, dur: 22 },
  { src: "Paper Dash Gameplay.mp4", slug: "paper-dash", start: 4, dur: 22 },
  { src: "Solar System Exploration Gameplay.mp4", slug: "solar-system", start: 5, dur: 22 },
  { src: "Voxelcraft 3D Gameplay.mp4", slug: "voxelcraft", start: 5, dur: 22 },
  { src: "Pac-Man Gameplay.mp4", slug: "pac-man", start: 2, dur: 20 },
  { src: "AR Memory Card Game.mp4", slug: "ar-memory", start: 3, dur: 20 },
  { src: "AR Face Filter Demo.mp4", slug: "ar-face-filter", start: 1, dur: 18 },
];

function getDuration(filePath) {
  try {
    const out = execFileSync(FFPROBE, [
      "-v", "error",
      "-show_entries", "format=duration",
      "-of", "default=noprint_wrappers=1:nokey=1",
      filePath,
    ], { encoding: "utf8" }).trim();
    return parseFloat(out) || 30;
  } catch {
    return 30;
  }
}

for (const item of VIDEOS) {
  const inFile = join(SRC_DIR, item.src);
  if (!existsSync(inFile)) {
    console.warn(`Missing source: ${inFile}`);
    continue;
  }
  const totalDur = getDuration(inFile);
  const start = Math.min(item.start, Math.max(0, totalDur - 5));
  const dur = Math.min(item.dur, Math.max(5, totalDur - start));

  const outMp4 = join(OUT_DIR, `${item.slug}.mp4`);
  const outJpg = join(OUT_DIR, `${item.slug}.jpg`);
  const outBillboard = join(BILLBOARD_DIR, `${item.slug}.mp4`);

  console.log(`Processing ${item.slug} (from ${start}s for ${dur.toFixed(1)}s)...`);

  // 1. Project preview MP4 (720p, 30fps, H.264 + AAC, faststart)
  execFileSync(FFMPEG, [
    "-y",
    "-ss", String(start),
    "-i", inFile,
    "-t", String(dur),
    "-vf", "scale='min(1280,iw)':-2,fps=30,format=yuv420p",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "26",
    "-maxrate", "2200k",
    "-bufsize", "4400k",
    "-c:a", "aac",
    "-b:a", "96k",
    "-movflags", "+faststart",
    outMp4,
  ], { stdio: "ignore" });

  // 2. Poster frame JPG
  execFileSync(FFMPEG, [
    "-y",
    "-ss", String(start + Math.min(3, dur / 2)),
    "-i", inFile,
    "-frames:v", "1",
    "-vf", "scale='min(1280,iw)':-2",
    "-q:v", "3",
    outJpg,
  ], { stdio: "ignore" });

  // 3. Short muted 10s loop for 3D city billboards (640w, lightweight)
  execFileSync(FFMPEG, [
    "-y",
    "-ss", String(start + 1),
    "-i", inFile,
    "-t", "10",
    "-an",
    "-vf", "scale=640:-2,fps=24,format=yuv420p",
    "-c:v", "libx264",
    "-preset", "veryfast",
    "-crf", "28",
    "-movflags", "+faststart",
    outBillboard,
  ], { stdio: "ignore" });

  const sz = (statSync(outMp4).size / 1024 / 1024).toFixed(2);
  console.log(`  -> ${item.slug}.mp4 (${sz} MB)`);
}

console.log("Done processing gameplay videos.");
