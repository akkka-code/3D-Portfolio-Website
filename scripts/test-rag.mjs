#!/usr/bin/env node
/**
 * Automated verification of the RAG Vector Index (data/vector-index.json),
 * BM25 & Hybrid Retrieval (api/_lib/retriever.js), and Asset Integrity.
 */
import { existsSync, readFileSync } from "node:fs";
import { join } from "node:path";
import { loadIndex, search } from "../api/_lib/retriever.js";

const ROOT = process.cwd();
const profile = JSON.parse(readFileSync(join(ROOT, "content", "profile.json"), "utf8"));

console.log("=== 1. Verifying RAG Vector Index ===");
const index = loadIndex();
console.log(`Owner: ${index.owner} | Chunks: ${index.chunks.length} | Has Embeddings: ${index.hasEmbeddings}`);
if (index.chunks.length < 20) {
  throw new Error(`Expected at least 20 chunks in vector-index.json, found ${index.chunks.length}`);
}

const queries = [
  "Chrono Rebellion Unity HDRP",
  "Behind the Smile Global Game Jam 2026",
  "Paper Plane Dash Unreal Engine 5",
  "Pac-Man C++ SFML QuadTrees",
  "NED University Gaming and Animation",
  "Aerox ERP Game Development Intern",
];

for (const q of queries) {
  const { results, mode } = search(q, null, { k: 3 });
  if (!results.length || results[0].score <= 0) {
    throw new Error(`Retrieval returned no match for query: "${q}"`);
  }
  console.log(`✓ Query "${q}" (${mode}) -> Top match: [${results[0].chunk.meta.title}] (score: ${results[0].score.toFixed(3)})`);
}

console.log("\n=== 2. Verifying Public Media Assets Referenced in profile.json ===");
const requiredAssets = [
  profile.cvUrl,
  profile.photo,
  "/models/avatar.glb",
  "/models/cyberpunk_compressed.glb",
  "/models/colider.glb",
  "/models/quadra.glb",
  "/models/billboards.glb",
  "/video/promo.mp4",
  "/video/promo-poster.jpg",
  "/funky-cyber-groove.mp3",
  "/light-rain.mp3",
  ...profile.projects.flatMap((p) => [p.video, p.poster].filter(Boolean)),
];

for (const relUrl of requiredAssets) {
  const diskPath = join(ROOT, "public", relUrl.replace(/^\//, ""));
  if (!existsSync(diskPath)) {
    throw new Error(`Missing required public asset: ${relUrl} (expected at ${diskPath})`);
  }
}
console.log(`✓ Verified all ${requiredAssets.length} public 3D models, videos, posters, audio tracks, and CV assets exist on disk.`);
