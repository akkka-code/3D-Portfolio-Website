#!/usr/bin/env node
/**
 * Generates docs/Project_Report.pdf with embedded screenshots of the 3D avatar,
 * promotional video, and game projects.
 */
import PDFDocument from "pdfkit";
import { createWriteStream, existsSync, mkdirSync, statSync } from "node:fs";
import { join } from "node:path";

const ROOT = process.cwd();
const OUT_DIR = join(ROOT, "docs");
const OUT_PDF = join(OUT_DIR, "Project_Report.pdf");
mkdirSync(OUT_DIR, { recursive: true });

const doc = new PDFDocument({
  size: "A4",
  margins: { top: 48, bottom: 48, left: 50, right: 50 },
  info: {
    Title: "Interactive 3D Web Portfolio — Project Report (Syed Muhammad Ahmad)",
    Author: "Syed Muhammad Ahmad (AKKA)",
    Subject: "3D Web Portfolio, Blender Avatar, After Effects Video, RAG AI Chatbot, Email Contact System",
  },
});

const stream = createWriteStream(OUT_PDF);
doc.pipe(stream);

function h1(text) {
  doc.moveDown(0.3);
  doc.font("Helvetica-Bold").fontSize(20).fillColor("#0b132b").text(text);
  doc.moveDown(0.3);
}

function h2(text) {
  doc.moveDown(0.6);
  doc.font("Helvetica-Bold").fontSize(13.5).fillColor("#0284c7").text(text);
  const y = doc.y + 2;
  doc.moveTo(50, y).lineTo(545, y).lineWidth(1).strokeColor("#0284c7").stroke();
  doc.moveDown(0.4);
}

function p(text) {
  doc.font("Helvetica").fontSize(10.2).fillColor("#1e293b").text(text, { lineGap: 2.5 });
  doc.moveDown(0.35);
}

function bullet(label, body) {
  doc.font("Helvetica-Bold").fontSize(10).fillColor("#0f172a").text(`• ${label}: `, { continued: true });
  doc.font("Helvetica").fontSize(10).fillColor("#334155").text(body, { lineGap: 2 });
  doc.moveDown(0.2);
}

// Header Banner
doc.rect(50, 44, 495, 78).fill("#070b16");
doc.fillColor("#00e5ff").font("Helvetica-Bold").fontSize(10).text("FINAL PROJECT REPORT // INTERACTIVE 3D WEB PORTFOLIO", 66, 56);
doc.fillColor("#ffffff").font("Helvetica-Bold").fontSize(17).text("Design & Development of an Interactive 3D Web Portfolio", 66, 72);
doc.fillColor("#cbd5e1").font("Helvetica").fontSize(9.5).text("Syed Muhammad Ahmad (AKKA)  |  BS CS & IT (Gaming & Animation), NED University  |  ahmedakka765@gmail.com", 66, 98);
doc.y = 136;

h2("1. Executive Summary & System Overview");
p(
  "This project combines real-time 3D web graphics (Three.js WebGPU + Three Shading Language), an original rigged 3D character created in Blender 5.1, a 46-second promotional video built with Adobe After Effects ExtendScript, FilmBro VFX overlays, and a synthesized CC0 dark-synthwave soundtrack, a Google Gemini Retrieval-Augmented Generation (RAG) AI chatbot with clickable source citations and voice I/O, and a Resend-powered email contact system into one cohesive cyberpunk web portfolio.",
);

h2("2. Module 1 — Interactive 3D Web-Based Portfolio");
bullet("WebGPU & TSL Alley Scene", "Built with Three.js r185 WebGPURenderer and TSL node materials featuring GPU height-map rain collision (createCollisionHeight.js + createCollisionRain.js), wet pavement ripples, half-resolution planar reflections (createGround.js), and BVH first-person walk + orbit controls.");
bullet("In-World Gameplay Billboards", "Neon city billboards stream gameplay video loops from Syed Muhammad Ahmad's 8 game projects (Chrono Rebellion, Behind the Smile, Paper Plane Dash, Solar System VR, Voxelcraft 3D, Pac-Man, AR Memory Card, and AR Face Filter).");
bullet("Responsive Glassmorphic UI & Extra Credit", "Floating navigation dock (src/portfolio/createPortfolioUI.js) with smooth slide-over panels for Home, About Me, Skills & Technologies, Projects & Achievements (with category filtering and instant search), Education & Experience, and Contact, plus Dark/Light theme switching.");

h2("3. Module 2 — Custom 3D Avatar Using Blender 5.1");
bullet("Procedural Modelling & PBR Shading", "Generated from scratch via blender/build_avatar.py and saved to blender/avatar.blend and public/models/avatar.glb (1.3 MB). Styled after reference photos of Syed Muhammad Ahmad with voluminous swept-up dark hair, glasses, neat moustache, jawline stubble, and an olive-charcoal leather biker jacket with emissive cyan (#00E5FF) and magenta (#FF2BD6) accents.");
bullet("Rigging, 5 Animations & Facial Morphs", "18-bone armature (Root, Hips, Spine, Chest, Neck, Head, Shoulder.L/R, UpperArm.L/R, LowerArm.L/R, Hand.L/R, UpperLeg.L/R, LowerLeg.L/R, Foot.L/R) with 5 NLA animation clips (Idle, Wave, Talk, Point, Victory) and 3 facial shape keys (Blink, Smile, MouthOpen).");
bullet("Interactive Web Integration", "Placed in the 3D alley (src/world/avatar/loadAvatar.js) with cursor head-tracking, proximity auto-wave, interactive animation trigger buttons, turntable controls, and real-time voice lip-sync.");

// Embed Avatar & Promo Poster side-by-side
const avatarPng = join(ROOT, "blender", "avatar_preview.png");
const promoJpg = join(ROOT, "public", "video", "promo-poster.jpg");
const figY = doc.y + 4;
if (existsSync(avatarPng)) {
  doc.image(avatarPng, 55, figY, { width: 175, height: 145, fit: [175, 145] });
}
if (existsSync(promoJpg)) {
  doc.image(promoJpg, 255, figY, { width: 280, height: 145, fit: [280, 145] });
}
doc.y = figY + 152;
doc.font("Helvetica-Oblique").fontSize(8.8).fillColor("#475569").text(
  "Left: Custom 3D Avatar rendered in Blender 5.1 Eevee. Right: Promotional video opening frame with Cyberpunk Glitch VFX.",
  50,
  doc.y,
);
doc.moveDown(0.5);

// Page 2
doc.addPage();

h2("4. Module 3 — Short Animated Video Using Adobe After Effects");
bullet("ExtendScript & Project File", "Automated via video/build_promo.jsx reading directly from content/profile.json and saved as video/promo.aep (1920x1080, 30 fps, 46.0 seconds).");
bullet("Original CC0 Synthwave Music", "Synthesized purely with the Python standard library (video/music/make_music.py -> promo_music.wav) at 100 BPM in A minor so scene transitions land on bar downbeats with risers and impacts.");
bullet("FilmBro VFX Assets Pack Compositing", "Integrates screen-blended 1080p overlays from the FilmBro VFX pack (Cyberpunk Style Glitch Elements, Hollywood HUD Custom Frame & Drone Overlays, Real Particles, and Sparks) over gameplay footage from Chrono Rebellion, Behind the Smile, Paper Plane Dash, Solar System VR, and Voxelcraft 3D.");

const chronoJpg = join(ROOT, "public", "video", "projects", "chrono-rebellion.jpg");
const smileJpg = join(ROOT, "public", "video", "projects", "behind-the-smile.jpg");
const fig2Y = doc.y + 4;
if (existsSync(chronoJpg)) {
  doc.image(chronoJpg, 50, fig2Y, { width: 238, height: 134, fit: [238, 134] });
}
if (existsSync(smileJpg)) {
  doc.image(smileJpg, 305, fig2Y, { width: 238, height: 134, fit: [238, 134] });
}
doc.y = fig2Y + 140;
doc.font("Helvetica-Oblique").fontSize(8.8).fillColor("#475569").text(
  "Gameplay frames featured in the promotional video and 3D billboards: Chrono Rebellion (left) and Behind the Smile (right).",
  50,
  doc.y,
);
doc.moveDown(0.4);

h2("5. Module 4 — RAG-Based AI Chatbot Pipeline (AHMAD.AI)");
bullet("1. Ingestion & Sentence Chunking", "scripts/ingest.mjs parses content/profile.json, knowledge/SyedMuhammadAhmad_CV.pdf (via unpdf), and knowledge/portfolio-details.md into 28 structured documents and splits them into 44 overlapping chunks (700 chars, 120-char overlap).");
bullet("2. Vector Embeddings & Hybrid Index", "Generates L2-normalized 768-dimensional embeddings via Google's gemini-embedding-001 model and stores them alongside metadata in data/vector-index.json.");
bullet("3. Hybrid Dense + BM25 Retrieval", "api/_lib/retriever.js combines cosine similarity (0.75 weight) with normalized BM25 keyword scores (0.25 weight) and per-source diversity to retrieve top-6 chunks.");
bullet("4. Grounded Generation & Citations", "api/chat.js prompts Gemini Flash with strict anti-hallucination rules and numbered <sources>. Answers include clickable [1], [2] citation chips that jump directly to the referenced portfolio section, plus multilingual support and Web Speech API voice input/output.");

h2("6. Module 5 — Email and Contact System");
bullet("Dual Frontend & Backend Validation", "shared/validation.js enforces identical field limits and RFC-5322 email validation in both the browser form and POST /api/contact.");
bullet("Spam Protection & Security", "Includes HTML entity escaping, a hidden honeypot field (website), a 3-second minimum fill-time bot check, origin verification, and a sliding-window IP rate limiter (5 messages / 10 min).");
bullet("Resend Email Delivery", "api/contact.js sends formatted HTML + plain-text emails with visitor Reply-To headers to ahmedakka765@gmail.com using environment variables (RESEND_API_KEY, CONTACT_TO_EMAIL).");

h2("7. Module 6 — Deployment & Verification Summary");
bullet("Build & API Verification", "Verified via `npm run build` (190 modules bundled cleanly by Vite 6) and `npm run test:api` (confirming hybrid RAG retrieval, grounded Gemini answers with citations, anti-hallucination refusal on unknown personal questions, and 422 validation errors on invalid contact input).");
bullet("Vercel Cloud Configuration", "vercel.json configures serverless functions (/api/chat and /api/contact), bundles data/vector-index.json, and sets security headers (X-Content-Type-Options, X-Frame-Options, Referrer-Policy).");

doc.end();

stream.on("finish", () => {
  const kb = (statSync(OUT_PDF).size / 1024).toFixed(1);
  console.log(`✅ Generated ${OUT_PDF} (${kb} KB)`);
});
