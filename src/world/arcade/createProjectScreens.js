import * as THREE from "three/webgpu";
import { texture, uv, float, vec3 } from "three/tsl";
import profile from "../../../content/profile.json";

const NEON_PALETTE = [
  { hex: 0x00e5ff, css: "#00e5ff", accent: "#ff2bd6" },
  { hex: 0xff2bd6, css: "#ff2bd6", accent: "#00e5ff" },
  { hex: 0xfcee0a, css: "#fcee0a", accent: "#00e5ff" },
  { hex: 0x00ff9d, css: "#00ff9d", accent: "#00e5ff" },
];

/**
 * Renders a crisp sci-fi header banner texture (CanvasTexture) for a project kiosk.
 */
function createHeaderBannerTexture({ index, title, category, year, tags, palette }) {
  const canvas = document.createElement("canvas");
  canvas.width = 1024;
  canvas.height = 220;
  const ctx = canvas.getContext("2d");

  // Deep sci-fi HUD background
  const grad = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
  grad.addColorStop(0, "rgba(6, 11, 24, 0.96)");
  grad.addColorStop(0.6, "rgba(12, 20, 42, 0.96)");
  grad.addColorStop(1, "rgba(18, 12, 38, 0.96)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Subtle tech grid lines
  ctx.strokeStyle = "rgba(0, 229, 255, 0.08)";
  ctx.lineWidth = 1;
  for (let x = 0; x < canvas.width; x += 32) {
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, canvas.height);
    ctx.stroke();
  }

  // Outer glowing border + corner brackets
  ctx.strokeStyle = palette.css;
  ctx.lineWidth = 5;
  ctx.strokeRect(4, 4, canvas.width - 8, canvas.height - 8);

  // Top-left accent slash bar
  ctx.fillStyle = palette.css;
  ctx.fillRect(18, 18, 12, 184);

  // Kicker: index + category + year
  ctx.fillStyle = palette.accent;
  ctx.font = "bold 24px Orbitron, Segoe UI, sans-serif";
  const numStr = String(index + 1).padStart(2, "0");
  ctx.fillText(
    `PROJECT ${numStr} // ${String(category || "GAME").toUpperCase()} · ${year || 2025}`,
    48,
    52,
  );

  // Main Project Title
  ctx.fillStyle = "#ffffff";
  ctx.font = "900 50px Orbitron, Segoe UI, sans-serif";
  ctx.fillText(String(title).toUpperCase().slice(0, 26), 48, 118);

  // Tech stack badges row
  const badgeTags = (tags || []).slice(0, 4);
  let bx = 48;
  ctx.font = "bold 22px Orbitron, Segoe UI, sans-serif";
  for (const tag of badgeTags) {
    const label = String(tag).toUpperCase();
    const tw = ctx.measureText(label).width + 28;
    ctx.fillStyle = "rgba(0, 229, 255, 0.16)";
    ctx.fillRect(bx, 144, tw, 44);
    ctx.strokeStyle = palette.css;
    ctx.lineWidth = 2;
    ctx.strokeRect(bx, 144, tw, 44);
    ctx.fillStyle = "#e6f7ff";
    ctx.fillText(label, bx + 14, 174);
    bx += tw + 14;
  }

  // Right-side "HD LIVE FEED" badge
  ctx.fillStyle = palette.css;
  ctx.font = "bold 22px Orbitron, Segoe UI, sans-serif";
  ctx.textAlign = "right";
  ctx.fillText("● HD GAMEPLAY", canvas.width - 30, 52);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.needsUpdate = true;
  return tex;
}

/**
 * Renders a large overhead neon archway sign texture for the alley.
 */
function createArchwaySignTexture({ title, subtitle, primaryColor = "#00e5ff", accentColor = "#ff2bd6" }) {
  const canvas = document.createElement("canvas");
  canvas.width = 1600;
  canvas.height = 320;
  const ctx = canvas.getContext("2d");

  const grad = ctx.createLinearGradient(0, 0, canvas.width, 0);
  grad.addColorStop(0, "rgba(5, 9, 20, 0.95)");
  grad.addColorStop(0.5, "rgba(14, 24, 52, 0.95)");
  grad.addColorStop(1, "rgba(5, 9, 20, 0.95)");
  ctx.fillStyle = grad;
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  // Neon double border
  ctx.strokeStyle = primaryColor;
  ctx.lineWidth = 8;
  ctx.strokeRect(8, 8, canvas.width - 16, canvas.height - 16);

  ctx.strokeStyle = accentColor;
  ctx.lineWidth = 3;
  ctx.strokeRect(22, 22, canvas.width - 44, canvas.height - 44);

  // Corner tech chevrons
  ctx.fillStyle = primaryColor;
  ctx.fillRect(36, 36, 90, 10);
  ctx.fillRect(canvas.width - 126, 36, 90, 10);
  ctx.fillRect(36, canvas.height - 46, 90, 10);
  ctx.fillRect(canvas.width - 126, canvas.height - 46, 90, 10);

  ctx.textAlign = "center";
  ctx.fillStyle = "#ffffff";
  ctx.font = "900 68px Orbitron, Segoe UI, sans-serif";
  ctx.fillText(title, canvas.width / 2, 152);

  ctx.fillStyle = primaryColor;
  ctx.font = "bold 32px Orbitron, Segoe UI, sans-serif";
  ctx.fillText(subtitle, canvas.width / 2, 236);

  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  tex.needsUpdate = true;
  return tex;
}

/**
 * Builds a crystal-clear video material with zero vignette darkening so the
 * gameplay video looks sharp, bright, and vivid in the WebGPU alley.
 */
function createClearVideoMaterial(videoUrl, posterUrl, shouldAutoplay = false) {
  const video = document.createElement("video");
  video.src = videoUrl;
  video.crossOrigin = "anonymous";
  video.loop = true;
  video.muted = true;
  video.playsInline = true;
  video.preload = shouldAutoplay ? "auto" : "metadata";
  video.setAttribute("muted", "");
  video.setAttribute("playsinline", "");

  const videoTexture = new THREE.VideoTexture(video);
  videoTexture.colorSpace = THREE.SRGBColorSpace;
  videoTexture.minFilter = THREE.LinearFilter;
  videoTexture.magFilter = THREE.LinearFilter;
  videoTexture.generateMipmaps = false;

  // Crisp unlit node material so scene shadows or vignette never muddy the gameplay footage
  const sampleUv = uv();
  const videoSample = texture(videoTexture, sampleUv);

  const material = new THREE.MeshBasicNodeMaterial();
  // Slight 1.06 boost keeps colors vibrant under the cyberpunk tonemapper without triggering excessive bloom
  material.colorNode = videoSample.rgb.mul(float(1.06));
  material.toneMapped = false;

  if (shouldAutoplay) {
    video.play().catch(() => {});
  } else {
    // Prime first frame via currentTime seek once metadata arrives
    video.addEventListener(
      "loadedmetadata",
      () => {
        video.currentTime = 0.5;
      },
      { once: true },
    );
  }

  return { material, video, videoTexture };
}

/**
 * Creates 8 Holographic Project Showcase Screens along the walkable alley +
 * custom Overhead Cyber Archways & Floating Holo Pylons.
 */
export function createProjectScreens({ scene }) {
  const group = new THREE.Group();
  group.name = "AlleyProjectShowcase";

  const projects = (profile.projects || []).filter((p) => p.video).slice(0, 8);
  const groundY = -5.5;

  // ---------------------------------------------------------------------------
  // 1. Place 8 Eye-Level Holographic Kiosks along both sides of the alley
  // Alley runs along X from -134 to -102, Z center around 31.6.
  // Left row at Z = 27.6 (angled toward +Z), Right row at Z = 35.6 (angled toward -Z).
  // ---------------------------------------------------------------------------
  const slots = [
    { x: -130.0, z: 27.5, rotY: 0.22 },
    { x: -127.0, z: 35.6, rotY: Math.PI - 0.22 },
    { x: -123.5, z: 27.5, rotY: 0.18 },
    { x: -120.5, z: 35.6, rotY: Math.PI - 0.18 },
    { x: -117.0, z: 27.5, rotY: 0.18 },
    { x: -114.0, z: 35.6, rotY: Math.PI - 0.18 },
    { x: -110.5, z: 27.5, rotY: 0.22 },
    { x: -107.5, z: 35.6, rotY: Math.PI - 0.22 },
  ];

  const screenEntries = [];
  const floatingDecos = [];

  const screenW = 3.55;
  const screenH = 2.0;
  const screenCenterY = 1.95; // Relative to groundY (-5.5 + 1.95 = -3.55m eye-level)

  const screenGeo = new THREE.PlaneGeometry(screenW, screenH);
  const backingGeo = new THREE.BoxGeometry(screenW + 0.22, screenH + 0.22, 0.12);
  const headerGeo = new THREE.PlaneGeometry(screenW + 0.18, 0.72);
  const pillarGeo = new THREE.BoxGeometry(0.14, screenH + 1.65, 0.18);
  const basePadGeo = new THREE.RingGeometry(1.15, 1.32, 6);
  basePadGeo.rotateX(-Math.PI / 2);

  const darkMetalMat = new THREE.MeshStandardNodeMaterial({
    color: new THREE.Color(0x0b1020),
    roughness: 0.35,
    metalness: 0.85,
  });

  projects.forEach((proj, idx) => {
    const slot = slots[idx] || { x: -130 + idx * 3.5, z: 27.6, rotY: 0 };
    const palette = NEON_PALETTE[idx % NEON_PALETTE.length];

    const kiosk = new THREE.Group();
    kiosk.name = `ProjectKiosk_${proj.id}`;
    kiosk.position.set(slot.x, groundY, slot.z);
    kiosk.rotation.y = slot.rotY;

    const neonMat = new THREE.MeshStandardNodeMaterial({
      color: new THREE.Color(palette.hex),
      emissive: new THREE.Color(palette.hex),
      emissiveIntensity: 2.6,
      roughness: 0.2,
    });

    // Dark armored backing frame
    const backing = new THREE.Mesh(backingGeo, darkMetalMat);
    backing.position.set(0, screenCenterY, -0.07);
    kiosk.add(backing);

    // Crystal-clear 16:9 HD Gameplay Video Screen (autoplay closest 3 on startup, proximity-stream rest)
    const { material: vidMat, video } = createClearVideoMaterial(proj.video, proj.poster, idx < 3);
    const screenMesh = new THREE.Mesh(screenGeo, vidMat);
    screenMesh.position.set(0, screenCenterY, 0.01);
    screenMesh.userData.projectId = proj.id;
    kiosk.add(screenMesh);

    // Left & Right Glowing Cyber Pillars
    const leftPillar = new THREE.Mesh(pillarGeo, neonMat);
    leftPillar.position.set(-(screenW * 0.5 + 0.14), screenCenterY + 0.15, 0);
    kiosk.add(leftPillar);

    const rightPillar = new THREE.Mesh(pillarGeo, neonMat);
    rightPillar.position.set(screenW * 0.5 + 0.14, screenCenterY + 0.15, 0);
    kiosk.add(rightPillar);

    // Top Header Banner (Project Title + Category + Tech Stack)
    const headerTex = createHeaderBannerTexture({
      index: idx,
      title: proj.title,
      category: proj.category,
      year: proj.year,
      tags: proj.tags,
      palette,
    });
    const headerMat = new THREE.MeshBasicNodeMaterial();
    headerMat.colorNode = texture(headerTex, uv()).rgb;
    headerMat.toneMapped = false;

    const headerMesh = new THREE.Mesh(headerGeo, headerMat);
    headerMesh.position.set(0, screenCenterY + screenH * 0.5 + 0.46, 0.02);
    kiosk.add(headerMesh);

    // Hexagonal neon ground projection ring beneath the kiosk
    const padMesh = new THREE.Mesh(basePadGeo, neonMat);
    padMesh.position.set(0, 0.02, 0.45);
    kiosk.add(padMesh);

    group.add(kiosk);
    screenEntries.push({
      kiosk,
      video,
      worldPos: new THREE.Vector3(slot.x, groundY + screenCenterY, slot.z),
    });
  });

  // ---------------------------------------------------------------------------
  // 2. Custom Overhead Cyber Archways & Floating Holographic Pylons in Alley
  // ---------------------------------------------------------------------------
  const archSpecs = [
    {
      x: -131.5,
      z: 31.55,
      title: "SYED MUHAMMAD AHMAD",
      subtitle: "GAME DEVELOPER · UNITY · UNREAL ENGINE 5 · AR/VR · BLENDER",
      primary: "#00e5ff",
      accent: "#ff2bd6",
      hex: 0x00e5ff,
    },
    {
      x: -105.5,
      z: 31.55,
      title: "INTERACTIVE 3D GAME GALLERY",
      subtitle: "NED UNIVERSITY · GAMING & ANIMATION · 8 PLAYABLE SHOWCASES",
      primary: "#ff2bd6",
      accent: "#fcee0a",
      hex: 0xff2bd6,
    },
  ];

  const archBeamGeo = new THREE.BoxGeometry(0.28, 5.2, 0.28);
  const archSignGeo = new THREE.PlaneGeometry(7.8, 1.56);

  for (const spec of archSpecs) {
    const arch = new THREE.Group();
    arch.position.set(spec.x, groundY, spec.z);
    // Face along the X-axis alley (rotated 90 deg around Y)
    arch.rotation.y = Math.PI / 2;

    const archNeonMat = new THREE.MeshStandardNodeMaterial({
      color: new THREE.Color(spec.hex),
      emissive: new THREE.Color(spec.hex),
      emissiveIntensity: 3.0,
      roughness: 0.2,
    });

    const leftCol = new THREE.Mesh(archBeamGeo, archNeonMat);
    leftCol.position.set(-4.1, 2.6, 0);
    arch.add(leftCol);

    const rightCol = new THREE.Mesh(archBeamGeo, archNeonMat);
    rightCol.position.set(4.1, 2.6, 0);
    arch.add(rightCol);

    const signTex = createArchwaySignTexture({
      title: spec.title,
      subtitle: spec.subtitle,
      primaryColor: spec.primary,
      accentColor: spec.accent,
    });
    const signMat = new THREE.MeshBasicNodeMaterial({ side: THREE.DoubleSide });
    signMat.colorNode = texture(signTex, uv()).rgb.mul(vec3(1.08, 1.08, 1.08));
    signMat.toneMapped = false;

    const signFront = new THREE.Mesh(archSignGeo, signMat);
    signFront.position.set(0, 4.55, 0.08);
    arch.add(signFront);

    const signBack = new THREE.Mesh(archSignGeo, signMat);
    signBack.position.set(0, 4.55, -0.08);
    signBack.rotation.y = Math.PI;
    arch.add(signBack);

    group.add(arch);
  }

  // Floating holographic octahedrons along the alley ceiling for extra sci-fi atmosphere
  const holoGeo = new THREE.OctahedronGeometry(0.32, 0);
  for (let i = 0; i < 6; i++) {
    const palette = NEON_PALETTE[i % NEON_PALETTE.length];
    const holoMat = new THREE.MeshStandardNodeMaterial({
      color: new THREE.Color(palette.hex),
      emissive: new THREE.Color(palette.hex),
      emissiveIntensity: 3.2,
      wireframe: true,
    });
    const mesh = new THREE.Mesh(holoGeo, holoMat);
    const x = -129 + i * 4.2;
    const z = i % 2 === 0 ? 29.2 : 33.9;
    const baseY = groundY + 3.65;
    mesh.position.set(x, baseY, z);
    group.add(mesh);
    floatingDecos.push({ mesh, baseY, phase: i * 1.1 });
  }

  if (scene) {
    scene.add(group);
  }

  let accumTime = 0;

  function update(delta, camera) {
    accumTime += delta;

    // Animate floating holographic crystals
    for (const d of floatingDecos) {
      d.mesh.rotation.y += delta * 1.2;
      d.mesh.rotation.x += delta * 0.6;
      d.mesh.position.y = d.baseY + Math.sin(accumTime * 2.2 + d.phase) * 0.18;
    }

    // Ensure nearby project videos stay playing smoothly while distant ones pause to save GPU decode
    if (!camera) return;
    for (const entry of screenEntries) {
      const dist = camera.position.distanceTo(entry.worldPos);
      if (dist < 26) {
        if (entry.video.paused) {
          entry.video.play().catch(() => {});
        }
      } else if (dist > 32 && !entry.video.paused) {
        entry.video.pause();
      }
    }
  }

  return {
    group,
    screenEntries,
    update,
  };
}
