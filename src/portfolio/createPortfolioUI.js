import "./portfolio.css";
import gsap from "gsap";
import profile from "../../content/profile.json";
import { validateContact, escapeHtml } from "../../shared/validation.js";
import { AVATAR_START } from "../world/avatar/loadAvatar.js";
import { getIsMusicPlaying } from "../audio/audioState.js";

const SCROLL_CAMERA_WAYPOINTS = [
  // 0.00 — Hero: Iconic low-angle framing over the wet Quadra car toward the 3D Avatar & neon alley
  { pos: [-137.4, -3.85, 33.6], target: [-122.0, -3.35, 31.2] },
  // 0.30 — Works Index: Gliding down the center of the 8 Holographic Game Kiosks
  { pos: [-126.5, -3.55, 31.55], target: [-108.0, -3.45, 31.55] },
  // 0.58 — Showreel & 3D Avatar Stage: Framing the custom Blender 5.1 3D Avatar & glowing arch
  { pos: [-134.55, -4.05, 33.95], target: [-133.2, -4.25, 32.1] },
  // 0.80 — Capabilities & About: Wide architectural alley perspective
  { pos: [-118.0, -3.25, 31.55], target: [-102.0, -2.85, 31.55] },
  // 1.00 — Contact & Footer: Looking up toward the cyberpunk neon skyline & flying planes
  { pos: [-112.5, -3.35, 31.55], target: [-98.0, -1.2, 31.55] },
];

function lerp(a, b, t) {
  return a + (b - a) * t;
}

function clamp(x, min, max) {
  return Math.max(min, Math.min(max, x));
}

function sampleCameraPath(scrollNorm) {
  const t = clamp(scrollNorm, 0, 1) * (SCROLL_CAMERA_WAYPOINTS.length - 1);
  const idx = Math.min(Math.floor(t), SCROLL_CAMERA_WAYPOINTS.length - 2);
  const frac = t - idx;
  const a = SCROLL_CAMERA_WAYPOINTS[idx];
  const b = SCROLL_CAMERA_WAYPOINTS[idx + 1];
  return {
    pos: [
      lerp(a.pos[0], b.pos[0], frac),
      lerp(a.pos[1], b.pos[1], frac),
      lerp(a.pos[2], b.pos[2], frac),
    ],
    target: [
      lerp(a.target[0], b.target[0], frac),
      lerp(a.target[1], b.target[1], frac),
      lerp(a.target[2], b.target[2], frac),
    ],
  };
}

export function createPortfolioUI({
  camera,
  cameraDirector,
  world,
  appShell,
}) {
  const root = document.createElement("div");
  root.className = "pf-root";
  root.setAttribute("data-ui-block-look", "true");

  // Restore theme preference
  let isLightTheme = localStorage.getItem("pf_theme") === "light";
  if (isLightTheme) {
    document.body.classList.add("pf-theme-light");
  }

  let is3dWalkMode = false;
  let activeCategory = "All";
  let projectSearch = "";
  let worksViewMode = "list"; 
  let activeCaseStudyIndex = -1;
  let hoveredProjectIndex = -1;
  let avatarFocusOverride = false;

  const projects = profile.projects || [];
  const categories = ["All", ...new Set(projects.map((p) => p.category))];

  // ---------------------------------------------------------------------------
  // 1. Atmospheric Vignette + Fixed Top Architectural Bar (.sn-topbar)
  // ---------------------------------------------------------------------------
  const vignette = document.createElement("div");
  vignette.className = "sn-backdrop-vignette";

  const topbar = document.createElement("header");
  topbar.className = "sn-topbar";
  topbar.innerHTML = `
    <div style="display:flex;align-items:center;gap:18px">
      <button type="button" class="sn-brand" data-nav-scroll="hero" data-cursor="TOP">
        <span class="sn-brand-mark">${escapeHtml(profile.name)}</span>
        <span class="sn-brand-handle">${escapeHtml(profile.handle)}®</span>
      </button>
      <span class="sn-status-pill">
        <span class="sn-status-dot"></span>
        <span>AVAILABLE FOR GAME DEV & XR</span>
      </span>
    </div>

    <nav class="sn-nav" aria-label="Primary navigation">
      <button type="button" class="sn-nav-link is-active" data-nav-scroll="works" data-cursor="INDEX">Works (${String(projects.length).padStart(2, "0")})</button>
      <button type="button" class="sn-nav-link" data-nav-scroll="lab" data-cursor="REEL">Showreel</button>
      <button type="button" class="sn-nav-link" data-nav-scroll="about" data-cursor="PROFILE">Capabilities</button>
      <button type="button" class="sn-nav-link" data-nav-scroll="contact" data-cursor="CONTACT">Contact</button>
      <button type="button" class="sn-nav-btn" data-action="toggle-chat" data-cursor="AI RAG">◈ AHMAD.AI</button>
      <button type="button" class="sn-nav-btn sn-nav-btn--accent" data-action="enter-3d-world" data-cursor="WALK 3D">Explore 3D World ↗</button>
      <button type="button" class="sn-nav-btn" data-action="toggle-audio" id="sn-audio-btn" title="Toggle Background Music">Sound: OFF</button>
      <button type="button" class="sn-nav-btn" data-action="toggle-theme" id="sn-theme-btn" title="Toggle High-Contrast Light/Dark Mode">${isLightTheme ? "Dark" : "Light"}</button>
    </nav>
  `;

  // Floating bar shown when inside Full 3D Walk Mode (unobstructed 3D Character & Gesture controls)
  const returnBar = document.createElement("div");
  returnBar.className = "sn-3d-return-bar";
  returnBar.innerHTML = `
    <button type="button" class="sn-nav-btn sn-nav-btn--accent" data-action="exit-3d-world">← Return to Portfolio</button>
    <button type="button" class="sn-nav-btn" data-action="toggle-pov" id="sn-pov-btn">View: 3RD PERSON (V)</button>
    <button type="button" class="sn-nav-btn" data-3d-gesture="Wave">Wave</button>
    <button type="button" class="sn-nav-btn" data-3d-gesture="Victory">Victory</button>
    <button type="button" class="sn-nav-btn" data-3d-gesture="Point">Point</button>
    <button type="button" class="sn-nav-btn" data-3d-gesture="Talk">Talk</button>
    <button type="button" class="sn-nav-btn" data-action="toggle-chat">◈ AHMAD.AI</button>
  `;

  // ---------------------------------------------------------------------------
  // 2. Editorial Scroll Viewport & Sections (.sn-scroll-viewport)
  // ---------------------------------------------------------------------------
  const scrollViewport = document.createElement("main");
  scrollViewport.className = "sn-scroll-viewport";

  function renderWorksItems() {
    const q = projectSearch.trim().toLowerCase();
    const filtered = projects
      .map((p, idx) => ({ ...p, originalIndex: idx }))
      .filter((p) => {
        const catOk = activeCategory === "All" || p.category === activeCategory;
        const textOk =
          !q ||
          p.title.toLowerCase().includes(q) ||
          p.summary.toLowerCase().includes(q) ||
          (p.tags || []).some((t) => t.toLowerCase().includes(q));
        return catOk && textOk;
      });

    if (filtered.length === 0) {
      return `<p style="padding:32px 0;font-family:var(--sn-font-mono);color:var(--sn-fg-muted)">No works matching filter "${escapeHtml(projectSearch)}".</p>`;
    }

    if (worksViewMode === "grid") {
      return `
        <div class="sn-work-grid">
          ${filtered
            .map(
              (p) => `
            <article class="sn-grid-card" data-open-case="${p.originalIndex}" data-hover-proj="${p.originalIndex}" data-cursor="VIEW CASE">
              <div class="sn-grid-media">
                ${
                  p.video
                    ? `<video muted loop playsinline preload="metadata" poster="${escapeHtml(p.poster || "")}">
                        <source src="${escapeHtml(p.video)}" type="video/mp4" />
                      </video>`
                    : `<img src="${escapeHtml(p.poster || "/video/promo-poster.jpg")}" alt="${escapeHtml(p.title)}" style="width:100%;height:100%;object-fit:cover" />`
                }
              </div>
              <div class="sn-grid-body">
                <div class="sn-grid-meta">
                  <span>${String(p.originalIndex + 1).padStart(3, "0")} // ${escapeHtml(p.category)}</span>
                  <span>${escapeHtml(String(p.year))}</span>
                </div>
                <h3 class="sn-grid-title">${escapeHtml(p.title)}</h3>
                <p class="sn-grid-desc">${escapeHtml(p.summary)}</p>
                <div class="sn-work-tags" style="margin-top:auto;padding-top:6px">
                  ${(p.tags || []).map((t) => `<span class="sn-tag">${escapeHtml(t)}</span>`).join("")}
                </div>
              </div>
            </article>
          `,
            )
            .join("")}
        </div>
      `;
    }

    return `
      <div class="sn-work-list" role="list">
        ${filtered
          .map(
            (p) => `
          <div
            class="sn-work-row"
            role="listitem"
            tabindex="0"
            id="sn-proj-${escapeHtml(p.id)}"
            data-open-case="${p.originalIndex}"
            data-hover-proj="${p.originalIndex}"
            data-cursor="VIEW CASE"
          >
            <span class="sn-work-num">${String(p.originalIndex + 1).padStart(3, "0")}</span>
            <div class="sn-work-title-wrap">
              ${
                p.poster
                  ? `<img class="sn-work-thumb" src="${escapeHtml(p.poster)}" alt="${escapeHtml(p.title)}" loading="lazy" />`
                  : `<img class="sn-work-thumb" src="/video/promo-poster.jpg" alt="${escapeHtml(p.title)}" loading="lazy" />`
              }
              <span class="sn-work-title">${escapeHtml(p.title)}</span>
            </div>
            <span class="sn-work-cat">${escapeHtml(p.category)}</span>
            <div class="sn-work-tags">
              ${(p.tags || []).map((t) => `<span class="sn-tag">${escapeHtml(t)}</span>`).join("")}
            </div>
            <span class="sn-work-year">${escapeHtml(String(p.year))}</span>
            <span class="sn-work-arrow" aria-hidden="true">↗</span>
          </div>
        `,
          )
          .join("")}
      </div>
    `;
  }

  scrollViewport.innerHTML = `
    <div class="sn-page" id="sn-page-content">
      <!-- =================================================================
           SECTION 00: IMMEDIATE HERO STATEMENT (SAMSY.NINJA FLOW)
           ================================================================= -->
      <section class="sn-hero" id="sn-sec-hero">
        <h1 class="sn-hero-headline" id="sn-hero-headline">
          <span class="sn-hero-line">SYED MUHAMMAD</span>
          <span class="sn-hero-line sn-hero-line--accent">AHMAD — ${escapeHtml(profile.handle)}®</span>
          <span class="sn-hero-line sn-hero-line--outline">INTERACTIVE 3D &</span>
          <span class="sn-hero-line">GAME ARCHITECT.</span>
        </h1>

        <div class="sn-hero-grid">
          <p class="sn-hero-manifesto">
            ${escapeHtml(profile.tagline)} Specializing in high-frame-rate gameplay systems, procedural 3D worlds, OpenXR/Vuforia simulations, and real-time WebGPU experiences.
          </p>

          <div class="sn-hero-metrics">
            ${(profile.stats || [])
              .map(
                (st) => `
              <div>
                <div class="sn-metric-val">${escapeHtml(st.value)}</div>
                <div class="sn-metric-lbl">${escapeHtml(st.label)}</div>
              </div>
            `,
              )
              .join("")}
          </div>

          <div class="sn-hero-actions">
            <button type="button" class="sn-btn sn-btn--primary" data-nav-scroll="works" data-cursor="WORKS">Selected Works (${String(projects.length).padStart(2, "0")}) ↓</button>
            <button type="button" class="sn-btn" data-action="enter-3d-world" data-cursor="WALK 3D">Walk 3D Alley (3rd-Person) ↗</button>
            <button type="button" class="sn-btn" data-nav-scroll="lab" data-cursor="REEL">2026 Showreel ▶</button>
            <a class="sn-btn" href="${escapeHtml(profile.cvUrl)}" target="_blank" rel="noopener" data-cursor="PDF">Curriculum Vitae ↗</a>
          </div>
        </div>
      </section>

      <!-- =================================================================
           SECTION 01: CURATED INTERACTIVE PROJECT INDEX (HOVER PREVIEW + MODAL)
           ================================================================= -->
      <section class="sn-section" id="sn-sec-works">
        <header class="sn-section-header">
          <span class="sn-section-index">(01) — SELECTED WORKS</span>
          <h2 class="sn-section-title">Curated Project Index</h2>
        </header>

        <div class="sn-works-toolbar">
          <div class="sn-filter-group" id="sn-category-filters" role="tablist">
            ${categories
              .map((cat) => {
                const count =
                  cat === "All"
                    ? projects.length
                    : projects.filter((p) => p.category === cat).length;
                return `
                  <button
                    type="button"
                    class="sn-filter-btn ${cat === activeCategory ? "is-active" : ""}"
                    data-cat="${escapeHtml(cat)}"
                  >
                    ${escapeHtml(cat)} [${String(count).padStart(2, "0")}]
                  </button>
                `;
              })
              .join("")}
          </div>

          <div class="sn-works-controls">
            <input
              type="search"
              class="sn-search-input"
              id="sn-project-search"
              placeholder="Filter engine, genre, C++, UE5..."
              aria-label="Filter projects"
            />
            <button type="button" class="sn-filter-btn is-active" data-view-mode="list">Index List</button>
            <button type="button" class="sn-filter-btn" data-view-mode="grid">Media Grid</button>
          </div>
        </div>

        <div id="sn-works-container">
          ${renderWorksItems()}
        </div>
      </section>

      <!-- =================================================================
           SECTION 02: MOTION SHOWREEL
           ================================================================= -->
      <section class="sn-section" id="sn-sec-lab">
        <header class="sn-section-header">
          <span class="sn-section-index">(02) — MOTION SHOWREEL</span>
          <h2 class="sn-section-title">2026 Developer Trailer</h2>
        </header>

        <div class="sn-showcase-grid">
          <div class="sn-panel">
            <div>
              <h3 class="sn-panel-title">2026 Game & XR Developer Trailer</h3>
              <video class="sn-reel-video" id="sn-promo-video" controls preload="none" poster="/video/promo-poster.jpg?v=20261120d" data-cursor="PLAY REEL">
                <source src="/video/promo.mp4?v=20261120d" type="video/mp4" />
              </video>
            </div>
          </div>
        </div>
      </section>

      <!-- =================================================================
           SECTION 03: CAPABILITIES, TECHNICAL ARSENAL & JOURNEY
           ================================================================= -->
      <section class="sn-section" id="sn-sec-about">
        <header class="sn-section-header">
          <span class="sn-section-index">(03) — PROFILE & CAPABILITIES</span>
          <h2 class="sn-section-title">Biography, Stack & Timeline</h2>
        </header>

        <div class="sn-about-top">
          <div class="sn-portrait-frame">
            <img class="sn-portrait-img" src="${escapeHtml(profile.photo || "/images/ahmad-2.jpg")}" alt="${escapeHtml(profile.name)}" />
            <div class="sn-portrait-caption">
              <span>${escapeHtml(profile.name)}</span>
              <span>[${escapeHtml(profile.handle)}]</span>
            </div>
          </div>

          <div>
            <p class="sn-bio-lead">
              ${escapeHtml(profile.about?.[0] || "")}
            </p>
            ${(profile.about || [])
              .slice(1)
              .map((p) => `<p class="sn-bio-p">${escapeHtml(p)}</p>`)
              .join("")}

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:20px;margin-top:28px;padding-top:24px;border-top:1px solid var(--sn-line)">
              <div>
                <div class="sn-Subheading">Spoken Languages</div>
                <div class="sn-work-tags">
                  ${(profile.languages || []).map((l) => `<span class="sn-tag">${escapeHtml(l)}</span>`).join("")}
                </div>
              </div>
              <div>
                <div class="sn-Subheading">Core Disciplines</div>
                <div class="sn-work-tags">
                  ${(profile.interests || []).map((i) => `<span class="sn-tag">${escapeHtml(i)}</span>`).join("")}
                </div>
              </div>
              <div>
                <div class="sn-Subheading">Availability</div>
                <p style="margin:0;font-family:var(--sn-font-mono);font-size:12px;color:var(--sn-fg)">${escapeHtml(profile.availability)}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- 6-Column Technical Capabilities Matrix -->
        <div class="sn-Subheading">Technical Capabilities Matrix</div>
        <div class="sn-capabilities-grid">
          ${(profile.skills || [])
            .map(
              (group, idx) => `
            <div class="sn-cap-cell">
              <div class="sn-cap-num">0${idx + 1} // DISCIPLINE</div>
              <h3 class="sn-cap-title">${escapeHtml(group.group)}</h3>
              <div class="sn-cap-list">
                ${(group.items || []).map((item) => `<span class="sn-tag">${escapeHtml(item)}</span>`).join("")}
              </div>
            </div>
          `,
            )
            .join("")}
        </div>

        <!-- Experience, Education & Achievements -->
        <div class="sn-journey-grid">
          <div>
            <h3 class="sn-Subheading">Experience & Education</h3>
            ${(profile.experience || [])
              .map(
                (exp) => `
              <div class="sn-timeline-row">
                <div class="sn-timeline-period">${escapeHtml(exp.period)}</div>
                <div>
                  <h4 class="sn-timeline-role">${escapeHtml(exp.role)}</h4>
                  <div class="sn-timeline-org">${escapeHtml(exp.company)} · Work Experience</div>
                  ${exp.details ? `<p class="sn-timeline-desc">${escapeHtml(exp.details)}</p>` : ""}
                </div>
              </div>
            `,
              )
              .join("")}

            ${(profile.education || [])
              .map(
                (edu) => `
              <div class="sn-timeline-row">
                <div class="sn-timeline-period">${escapeHtml(edu.period)}</div>
                <div>
                  <h4 class="sn-timeline-role">${escapeHtml(edu.degree)}</h4>
                  <div class="sn-timeline-org">${escapeHtml(edu.institution)}</div>
                  ${edu.details ? `<p class="sn-timeline-desc">${escapeHtml(edu.details)}</p>` : ""}
                </div>
              </div>
            `,
              )
              .join("")}
          </div>

          <div>
            <h3 class="sn-Subheading">Achievements & Certifications</h3>
            ${(profile.achievements || [])
              .map(
                (ach) => `
              <div class="sn-timeline-row">
                <div class="sn-timeline-period">${escapeHtml(String(ach.year))}</div>
                <div>
                  <h4 class="sn-timeline-role">${escapeHtml(ach.title)}</h4>
                  <p class="sn-timeline-desc">${escapeHtml(ach.description)}</p>
                </div>
              </div>
            `,
              )
              .join("")}

            <div style="margin-top:24px">
              <div class="sn-Subheading">Verified Credentials</div>
              <div class="sn-work-tags">
                ${(profile.certifications || []).map((c) => `<span class="sn-tag">${escapeHtml(c)}</span>`).join("")}
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- =================================================================
           SECTION 04: DIRECT TRANSMISSION (CONTACT) & MINIMAL FOOTER
           ================================================================= -->
      <section class="sn-section" id="sn-sec-contact">
        <header class="sn-section-header">
          <span class="sn-section-index">(04) — INITIATE CONTACT</span>
          <h2 class="sn-section-title">Direct Transmission</h2>
        </header>

        <div class="sn-contact-grid">
          <div>
            <h3 class="sn-contact-headline">
              LET’S BUILD<br />THE NEXT<br />IMMERSIVE WORLD.
            </h3>
            <p class="sn-bio-p">
              Available for game development internships, gameplay engineering roles, Unreal/Unity prototyping, and interactive 3D web collaborations.
            </p>

            <div class="sn-direct-links">
              <a class="sn-direct-link" href="mailto:${escapeHtml(profile.email)}" data-cursor="EMAIL">
                <span>EMAIL // ${escapeHtml(profile.email)}</span>
                <span>↗</span>
              </a>
              <a class="sn-direct-link" href="${escapeHtml(profile.socials?.linkedin || "#")}" target="_blank" rel="noopener" data-cursor="LINKEDIN">
                <span>LINKEDIN // SYED MUHAMMAD AHMAD</span>
                <span>↗</span>
              </a>
              <a class="sn-direct-link" href="${escapeHtml(profile.socials?.canva || "#")}" target="_blank" rel="noopener" data-cursor="CANVA">
                <span>ARCHIVE // CANVA DESIGN PORTFOLIO</span>
                <span>↗</span>
              </a>
              <a class="sn-direct-link" href="${escapeHtml(profile.cvUrl)}" target="_blank" rel="noopener" data-cursor="CV PDF">
                <span>RESUME // DOWNLOAD FULL CV (PDF)</span>
                <span>↗</span>
              </a>
            </div>
          </div>

          <form class="sn-form" id="sn-contact-form" novalidate>
            <input type="hidden" name="startedAt" value="${Date.now()}" />
            <div class="sn-honeypot" aria-hidden="true">
              <label>Website <input type="text" name="website" tabindex="-1" autocomplete="off" /></label>
            </div>

            <div class="sn-form-row">
              <div class="sn-field">
                <label for="sn-c-name">01 // Your Name *</label>
                <input id="sn-c-name" name="name" type="text" required placeholder="Ada Lovelace" />
                <div class="sn-field-error" data-err="name"></div>
              </div>
              <div class="sn-field">
                <label for="sn-c-email">02 // Your Email *</label>
                <input id="sn-c-email" name="email" type="email" required placeholder="ada@studio.com" />
                <div class="sn-field-error" data-err="email"></div>
              </div>
            </div>

            <div class="sn-field">
              <label for="sn-c-subject">03 // Subject *</label>
              <input id="sn-c-subject" name="subject" type="text" required placeholder="Game Development Role / Interactive 3D Collaboration" />
              <div class="sn-field-error" data-err="subject"></div>
            </div>

            <div class="sn-field">
              <label for="sn-c-message">04 // Message *</label>
              <textarea id="sn-c-message" name="message" rows="5" required placeholder="Hi Ahmad, we explored your Chrono Rebellion and 3D WebGPU portfolio..."></textarea>
              <div class="sn-field-error" data-err="message"></div>
            </div>

            <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap">
              <button type="submit" class="sn-btn sn-btn--primary" id="sn-contact-submit" data-cursor="SEND">Send Transmission ↗</button>
              <span style="font-family:var(--sn-font-mono);font-size:11px;color:var(--sn-fg-muted)">DIRECT RELAY TO ${escapeHtml(profile.email.toUpperCase())}</span>
            </div>
            <div class="sn-form-status" id="sn-contact-status" role="status"></div>
          </form>
        </div>
      </section>

      <!-- Minimal Creative-Technologist Footer -->
      <footer class="sn-footer">
        <span>© ${new Date().getFullYear()} ${escapeHtml(profile.name)} (${escapeHtml(profile.handle)}®). ALL RIGHTS RESERVED.</span>
        <button type="button" class="sn-nav-btn" data-nav-scroll="hero" data-cursor="TOP">Back to Top ↑</button>
      </footer>
    </div>
  `;

 
  const hoverPreview = document.createElement("div");
  hoverPreview.className = "sn-hover-preview";
  hoverPreview.innerHTML = `
    <canvas class="sn-hover-canvas" width="480" height="270"></canvas>
    <div class="sn-hover-caption">
      <span id="sn-hover-title">CHRONO REBELLION</span>
      <span id="sn-hover-meta">2026 // LIVE SHADER FEED</span>
    </div>
  `;
  const hoverCanvas = hoverPreview.querySelector(".sn-hover-canvas");
  const hoverCtx = hoverCanvas.getContext("2d");
  const hoverTitleEl = hoverPreview.querySelector("#sn-hover-title");
  const hoverMetaEl = hoverPreview.querySelector("#sn-hover-meta");

  const previewVideo = document.createElement("video");
  previewVideo.muted = true;
  previewVideo.loop = true;
  previewVideo.playsInline = true;
  previewVideo.crossOrigin = "anonymous";

  const previewPosterImg = new Image();
  previewPosterImg.crossOrigin = "anonymous";

  // ---------------------------------------------------------------------------
  // 4. Single-View Project Case Study Modal (.sn-case-modal)
  // ---------------------------------------------------------------------------
  const caseModal = document.createElement("aside");
  caseModal.className = "sn-case-modal";
  caseModal.setAttribute("role", "dialog");
  caseModal.setAttribute("aria-modal", "true");
  caseModal.setAttribute("aria-label", "Project Case Study");
  caseModal.innerHTML = `
    <div class="sn-case-topbar">
      <span id="sn-case-index">CASE STUDY // 001 OF 009</span>
      <div style="display:flex;gap:10px">
        <button type="button" class="sn-nav-btn" id="sn-case-view3d">View on 3D Alley Screen ↗</button>
        <button type="button" class="sn-nav-btn sn-nav-btn--accent" id="sn-case-close">Close [ESC] ✕</button>
      </div>
    </div>
    <div class="sn-case-body" id="sn-case-body"></div>
  `;

  const caseIndexEl = caseModal.querySelector("#sn-case-index");
  const caseBodyEl = caseModal.querySelector("#sn-case-body");

  function openCaseStudy(index) {
    const idx = ((index % projects.length) + projects.length) % projects.length;
    const proj = projects[idx];
    if (!proj) return;
    activeCaseStudyIndex = idx;
    hoveredProjectIndex = idx;

    caseIndexEl.textContent = `CASE STUDY // ${String(idx + 1).padStart(3, "0")} OF ${String(projects.length).padStart(3, "0")} — ${proj.category.toUpperCase()}`;

    caseBodyEl.innerHTML = `
      <header class="sn-case-header">
        <p class="sn-case-kicker">${String(idx + 1).padStart(3, "0")} // ${escapeHtml(proj.category)} · ${escapeHtml(String(proj.year))}</p>
        <h2 class="sn-case-title">${escapeHtml(proj.title)}</h2>
      </header>

      <div class="sn-case-video-wrap">
        ${
          proj.video
            ? `<video class="sn-case-video" controls autoplay muted loop playsinline poster="${escapeHtml(proj.poster || "")}">
                <source src="${escapeHtml(proj.video)}" type="video/mp4" />
              </video>`
            : `<img class="sn-case-video" src="${escapeHtml(proj.poster || "/video/promo-poster.jpg")}" alt="${escapeHtml(proj.title)}" />`
        }
      </div>

      <div class="sn-case-info-grid">
        <div>
          <div class="sn-Subheading">Overview & Creative Direction</div>
          <p class="sn-case-summary">${escapeHtml(proj.summary)}</p>
          <div class="sn-Subheading" style="margin-top:28px">Engineering & Implementation</div>
          <p class="sn-case-details">${escapeHtml(proj.details || proj.summary)}</p>
        </div>

        <div class="sn-case-specs">
          <div class="sn-spec-row">
            <span class="sn-spec-key">Project Index</span>
            <span class="sn-spec-val">${String(idx + 1).padStart(3, "0")} / ${String(projects.length).padStart(3, "0")}</span>
          </div>
          <div class="sn-spec-row">
            <span class="sn-spec-key">Release Year</span>
            <span class="sn-spec-val">${escapeHtml(String(proj.year))}</span>
          </div>
          <div class="sn-spec-row">
            <span class="sn-spec-key">Discipline</span>
            <span class="sn-spec-val">${escapeHtml(proj.category)}</span>
          </div>
          <div class="sn-spec-row">
            <span class="sn-spec-key">Developer</span>
            <span class="sn-spec-val">${escapeHtml(profile.name)} (${escapeHtml(profile.handle)})</span>
          </div>
          <div class="sn-spec-row">
            <span class="sn-spec-key">Technologies</span>
            <span class="sn-spec-val">${(proj.tags || []).map(escapeHtml).join(" · ")}</span>
          </div>
        </div>
      </div>

      <div class="sn-case-nav">
        <button type="button" class="sn-btn" id="sn-case-prev">← Previous Work</button>
        <span style="font-family:var(--sn-font-mono);font-size:11.5px;color:var(--sn-fg-muted)">USE ← / → ARROW KEYS TO BROWSE</span>
        <button type="button" class="sn-btn sn-btn--primary" id="sn-case-next">Next Work →</button>
      </div>
    `;

    caseModal.classList.add("is-open");
    caseBodyEl.scrollTop = 0;
    world?.projectScreens?.setPaused?.(true);

    caseBodyEl.querySelector("#sn-case-prev")?.addEventListener("click", () => {
      openCaseStudy(activeCaseStudyIndex - 1);
    });
    caseBodyEl.querySelector("#sn-case-next")?.addEventListener("click", () => {
      openCaseStudy(activeCaseStudyIndex + 1);
    });
  }

  function closeCaseStudy() {
    activeCaseStudyIndex = -1;
    caseModal.classList.remove("is-open");
    const vid = caseBodyEl.querySelector("video");
    vid?.pause?.();
    if (!promoVideoEl || promoVideoEl.paused) {
      world?.projectScreens?.setPaused?.(false);
    }
  }

  caseModal.querySelector("#sn-case-close").addEventListener("click", closeCaseStudy);
  caseModal.querySelector("#sn-case-view3d").addEventListener("click", () => {
    const targetIdx = activeCaseStudyIndex;
    closeCaseStudy();
    enter3dWalkMode();
    // Focus near the selected project screen in the 3D alley if available
    const entry = world?.projectScreens?.screenEntries?.[targetIdx];
    if (entry && camera && cameraDirector) {
      const lookPos = entry.worldPos;
      const offsetZ = lookPos.z < 31.5 ? 3.8 : -3.8;
      camera.position.set(lookPos.x, -3.95, lookPos.z + offsetZ);
      camera.lookAt(lookPos.x, lookPos.y, lookPos.z);
      cameraDirector.walkControls?.syncEulerFromCamera?.();
    }
  });

  // ---------------------------------------------------------------------------
  // 5. Minimalist Creative-Technologist RAG AI Drawer (.sn-chat)
  // ---------------------------------------------------------------------------
  const chat = document.createElement("aside");
  chat.className = "sn-chat";
  chat.setAttribute("aria-label", "AHMAD.AI RAG Assistant");
  chat.innerHTML = `
    <header class="sn-chat-header">
      <div>
        <h3 class="sn-chat-title">◈ AHMAD.AI </h3>
      </div>
      <div class="sn-chat-controls">
        <select class="sn-chat-lang" id="sn-chat-lang" aria-label="Response language">
          <option value="auto">AUTO</option>
          <option value="en">EN</option>
          <option value="ur">UR (اردو)</option>
          <option value="ar">AR</option>
          <option value="zh">ZH</option>
          <option value="es">ES</option>
          <option value="fr">FR</option>
        </select>
        <button type="button" class="sn-nav-btn" id="sn-chat-tts" title="Toggle voice read-aloud">🔊</button>
        <button type="button" class="sn-nav-btn" id="sn-chat-close" aria-label="Close AI Drawer">✕</button>
      </div>
    </header>

    <div class="sn-chat-messages" id="sn-chat-messages" role="log" aria-live="polite"></div>

    <div class="sn-chat-prompts">
      <button type="button" class="sn-prompt-chip" data-q="What games has Ahmad built in Unity and Unreal Engine 5?">Games built ↗</button>
      <button type="button" class="sn-prompt-chip" data-q="What are Ahmad's technical skills and certifications?">Skills & Certs ↗</button>
      <button type="button" class="sn-prompt-chip" data-q="Where does Ahmad study and work?">Education & Work ↗</button>
    </div>

    <form class="sn-chat-form" id="sn-chat-form">
      <input
        type="text"
        class="sn-chat-input"
        id="sn-chat-input"
        placeholder="Query games, C++, UE5, NED University, CV..."
        maxlength="550"
        autocomplete="off"
      />
      <button type="button" class="sn-nav-btn" id="sn-chat-mic" title="Voice input">🎤</button>
      <button type="submit" class="sn-nav-btn sn-nav-btn--accent">Ask</button>
    </form>
  `;

  const chatMessages = chat.querySelector("#sn-chat-messages");
  const chatForm = chat.querySelector("#sn-chat-form");
  const chatInput = chat.querySelector("#sn-chat-input");
  const chatLang = chat.querySelector("#sn-chat-lang");
  const ttsBtn = chat.querySelector("#sn-chat-tts");
  const micBtn = chat.querySelector("#sn-chat-mic");

  const chatHistory = [];
  let ttsEnabled = false;

  ttsBtn.addEventListener("click", () => {
    ttsEnabled = !ttsEnabled;
    ttsBtn.textContent = ttsEnabled ? "🔊 ON" : "🔊";
    if (!ttsEnabled && "speechSynthesis" in window) {
      window.speechSynthesis.cancel();
      world?.avatar?.setSpeaking?.(false);
    }
  });

  function speakText(text) {
    if (!ttsEnabled || !("speechSynthesis" in window)) return;
    window.speechSynthesis.cancel();
    const clean = text.replace(/\[\d+\]/g, "").trim();
    const utter = new SpeechSynthesisUtterance(clean);
    utter.rate = 1.02;
    utter.onstart = () => world?.avatar?.setSpeaking?.(true);
    utter.onend = () => world?.avatar?.setSpeaking?.(false);
    utter.onerror = () => world?.avatar?.setSpeaking?.(false);
    window.speechSynthesis.speak(utter);
  }

  function appendChatMessage(role, text, citations = []) {
    const msg = document.createElement("div");
    msg.className = `sn-msg sn-msg--${role}`;
    msg.textContent = text;

    if (citations && citations.length > 0) {
      const citWrap = document.createElement("div");
      citWrap.className = "sn-citations";
      for (const c of citations) {
        const btn = document.createElement("button");
        btn.type = "button";
        btn.className = "sn-citation-btn";
        btn.textContent = `[${c.n}] ${c.title}`;
        btn.title = c.snippet || c.title;
        btn.addEventListener("click", () => {
          if (c.itemId) {
            const pIdx = projects.findIndex((p) => p.id === c.itemId);
            if (pIdx !== -1) {
              openCaseStudy(pIdx);
              return;
            }
          }
          exit3dWalkMode();
          scrollToSection(c.section || "works");
        });
        citWrap.appendChild(btn);
      }
      msg.appendChild(citWrap);
    }

    chatMessages.appendChild(msg);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return msg;
  }

  appendChatMessage(
    "bot",
    `AHMAD.AI ready. Ask me anything about ${profile.name}'s Unity & Unreal Engine 5 games, C++/SFML algorithms, AR/VR simulations, NED University degree, or internship at Aerox ERP.`,
  );

  async function sendChatQuestion(question) {
    const q = question.trim();
    if (!q) return;
    appendChatMessage("user", q);
    chatInput.value = "";
    const thinking = appendChatMessage("bot", "Retrieving grounded portfolio chunks...");

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: q,
          history: chatHistory.slice(-6),
          lang: chatLang.value,
        }),
      });
      const data = await res.json().catch(() => ({}));
      thinking.remove();
      const answer = data.answer || data.error || "Unable to process request.";
      appendChatMessage("bot", answer, data.citations || []);
      chatHistory.push({ role: "user", text: q }, { role: "assistant", text: answer });
      speakText(answer);
    } catch {
      thinking.remove();
      appendChatMessage("bot", "Network error while querying RAG endpoint.");
    }
  }

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    sendChatQuestion(chatInput.value);
  });

  for (const chip of chat.querySelectorAll("[data-q]")) {
    chip.addEventListener("click", () => sendChatQuestion(chip.dataset.q));
  }

  chat.querySelector("#sn-chat-close").addEventListener("click", () => {
    chat.classList.remove("is-open");
  });

  const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (SpeechRecognition) {
    const recognition = new SpeechRecognition();
    recognition.lang = "en-US";
    recognition.interimResults = false;
    recognition.onresult = (ev) => {
      const transcript = ev.results?.[0]?.[0]?.transcript;
      if (transcript) {
        chatInput.value = transcript;
        sendChatQuestion(transcript);
      }
    };
    micBtn.addEventListener("click", () => {
      try {
        recognition.start();
      } catch {
        /* ignore */
      }
    });
  } else {
    micBtn.style.display = "none";
  }

  // ---------------------------------------------------------------------------
  // 6. Custom Magnetic Cursor (.sn-cursor)
  // ---------------------------------------------------------------------------
  const cursor = document.createElement("div");
  cursor.className = "sn-cursor";
  cursor.innerHTML = `<div class="sn-cursor-ring"><span id="sn-cursor-label"></span></div>`;
  const cursorLabel = cursor.querySelector("#sn-cursor-label");

  const pointer = {
    x: window.innerWidth * 0.5,
    y: window.innerHeight * 0.5,
    curX: window.innerWidth * 0.5,
    curY: window.innerHeight * 0.5,
    prevX: window.innerWidth * 0.5,
    prevY: window.innerHeight * 0.5,
    velX: 0,
    velY: 0,
    ndcX: 0,
    ndcY: 0,
    smoothNdcX: 0,
    smoothNdcY: 0,
  };

  window.addEventListener(
    "pointermove",
    (e) => {
      pointer.x = e.clientX;
      pointer.y = e.clientY;
      pointer.ndcX = (e.clientX / Math.max(1, window.innerWidth)) * 2 - 1;
      pointer.ndcY = -((e.clientY / Math.max(1, window.innerHeight)) * 2 - 1);

      const interactive = e.target?.closest?.("[data-cursor], button, a, input, textarea");
      const label = e.target?.closest?.("[data-cursor]")?.getAttribute("data-cursor") || "";
      if (interactive) {
        cursor.classList.add("is-expanded");
        cursorLabel.textContent = label;
      } else {
        cursor.classList.remove("is-expanded");
        cursorLabel.textContent = "";
      }
    },
    { passive: true },
  );

  // ---------------------------------------------------------------------------
  // 7. Mode Switching: Editorial Index Mode <-> Full 3D Walk Mode
  // ---------------------------------------------------------------------------
  function enter3dWalkMode() {
    is3dWalkMode = true;
    avatarFocusOverride = false;
    hoveredProjectIndex = -1;
    hoverPreview.classList.remove("is-visible");
    document.body.classList.add("sn-mode-3d");

    cameraDirector?.enterThirdPersonAlleyPose?.();
    appShell?.walkPrompt?.setEnabled?.(true);
    appShell?.moveHint?.setEnabled?.(true);
    appShell?.virtualJoystick?.setEnabled?.(true);
    appShell?.audioButton?.play?.()?.catch?.(() => {});
    syncAudioBtnLabel();
  }

  function exit3dWalkMode() {
    is3dWalkMode = false;
    document.exitPointerLock?.();
    document.body.classList.remove("sn-mode-3d");

    cameraDirector?.setCameraMode?.("orbit");
    if (cameraDirector?.controls) {
      cameraDirector.controls.enabled = false;
    }
    appShell?.walkPrompt?.setEnabled?.(false);
    appShell?.moveHint?.setEnabled?.(false);
    appShell?.virtualJoystick?.setEnabled?.(false);
  }

  const SECTION_ALIAS = {
    home: "hero",
    hero: "hero",
    projects: "works",
    works: "works",
    lab: "lab",
    showreel: "lab",
    avatar: "lab",
    about: "about",
    skills: "about",
    journey: "about",
    contact: "contact",
  };

  function scrollToSection(sectionKey) {
    exit3dWalkMode();
    const resolved = SECTION_ALIAS[sectionKey] || "works";
    avatarFocusOverride = false;
    const targetEl = scrollViewport.querySelector(`#sn-sec-${resolved}`);
    if (targetEl) {
      scrollViewport.scrollTo({
        top: Math.max(0, targetEl.offsetTop - 8),
        behavior: "smooth",
      });
    }
    for (const link of topbar.querySelectorAll(".sn-nav-link")) {
      link.classList.toggle("is-active", link.dataset.navScroll === resolved);
    }
  }

  function focusAvatarIn3D() {
    avatarFocusOverride = true;
    document.body.classList.add("sn-peeking-3d");
    if (!camera || !cameraDirector) return;
    const [ax, ay, az] = AVATAR_START.position;
    gsap.to(camera.position, {
      x: ax - 1.1,
      y: ay + 1.42,
      z: az + 2.25,
      duration: 1.1,
      ease: "power3.out",
    });
    gsap.to(cameraDirector.controls.target, {
      x: ax,
      y: ay + 1.15,
      z: az,
      duration: 1.1,
      ease: "power3.out",
      onUpdate: () => cameraDirector.controls.update(),
    });
    world?.avatar?.triggerGesture?.("Wave");
  }

  // ---------------------------------------------------------------------------
  // 8. Bind Works Hover, Filter, Search, Avatar & Contact Form Events
  // ---------------------------------------------------------------------------
  function bindWorksInteractions() {
    const container = scrollViewport.querySelector("#sn-works-container");
    if (!container) return;

    for (const item of container.querySelectorAll("[data-open-case]")) {
      const idx = Number(item.getAttribute("data-open-case"));

      item.addEventListener("pointerenter", () => {
        hoveredProjectIndex = idx;
        avatarFocusOverride = false;
        const proj = projects[idx];
        if (!proj) return;
        hoverTitleEl.textContent = proj.title;
        hoverMetaEl.textContent = `${proj.year} // ${(proj.tags || []).slice(0, 2).join(" · ")}`;

        previewPosterImg.src = proj.poster || "/video/promo-poster.jpg";
        if (proj.video) {
          if (!previewVideo.src.endsWith(proj.video)) {
            previewVideo.src = proj.video;
          }
          previewVideo.play().catch(() => {});
        } else {
          previewVideo.pause();
          previewVideo.removeAttribute("src");
        }
        hoverPreview.classList.add("is-visible");

        // Auto-play grid video if in grid mode
        const gridVid = item.querySelector("video");
        gridVid?.play?.().catch?.(() => {});
      });

      item.addEventListener("pointerleave", () => {
        if (hoveredProjectIndex === idx) {
          hoveredProjectIndex = -1;
          hoverPreview.classList.remove("is-visible");
          previewVideo.pause();
        }
        const gridVid = item.querySelector("video");
        gridVid?.pause?.();
      });

      item.addEventListener("click", () => {
        hoverPreview.classList.remove("is-visible");
        openCaseStudy(idx);
      });

      item.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          openCaseStudy(idx);
        }
      });
    }
  }

  function refreshWorksView() {
    const container = scrollViewport.querySelector("#sn-works-container");
    if (!container) return;
    container.innerHTML = renderWorksItems();
    bindWorksInteractions();
  }

  // Category filter buttons
  scrollViewport.querySelector("#sn-category-filters")?.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-cat]");
    if (!btn) return;
    activeCategory = btn.dataset.cat;
    for (const b of scrollViewport.querySelectorAll("[data-cat]")) {
      b.classList.toggle("is-active", b.dataset.cat === activeCategory);
    }
    refreshWorksView();
  });

  // View mode toggle (List vs Grid)
  for (const btn of scrollViewport.querySelectorAll("[data-view-mode]")) {
    btn.addEventListener("click", () => {
      worksViewMode = btn.dataset.viewMode;
      for (const b of scrollViewport.querySelectorAll("[data-view-mode]")) {
        b.classList.toggle("is-active", b.dataset.viewMode === worksViewMode);
      }
      refreshWorksView();
    });
  }

  // Search filter
  const searchInput = scrollViewport.querySelector("#sn-project-search");
  searchInput?.addEventListener("input", (e) => {
    projectSearch = e.target.value;
    refreshWorksView();
  });

  // Promo Video Auto-Duck / Pause Background Music & 3D Alley Video Decoders so video never lags or overlaps
  const promoVideoEl = scrollViewport.querySelector("#sn-promo-video");
  let wasBgMusicPlayingBeforePromo = false;

  promoVideoEl?.addEventListener("play", () => {
    world?.projectScreens?.setPaused?.(true);
    if (getIsMusicPlaying()) {
      wasBgMusicPlayingBeforePromo = true;
      appShell?.audioButton?.pause?.();
      setTimeout(syncAudioBtnLabel, 60);
    }
  });

  function onPromoStop() {
    if (activeCaseStudyIndex === -1) {
      world?.projectScreens?.setPaused?.(false);
    }
    if (wasBgMusicPlayingBeforePromo) {
      wasBgMusicPlayingBeforePromo = false;
      appShell?.audioButton?.play?.()?.catch?.(() => {});
      setTimeout(syncAudioBtnLabel, 60);
    }
  }

  promoVideoEl?.addEventListener("pause", onPromoStop);
  promoVideoEl?.addEventListener("ended", onPromoStop);

  // 3D World Mode Gesture buttons (inside .sn-3d-return-bar where the character is 100% unobstructed)
  for (const gBtn of returnBar.querySelectorAll("[data-3d-gesture]")) {
    gBtn.addEventListener("click", (e) => {
      e.stopPropagation();
      world?.avatar?.triggerGesture?.(gBtn.getAttribute("data-3d-gesture"));
    });
  }

  // Contact form submission
  const contactForm = scrollViewport.querySelector("#sn-contact-form");
  contactForm?.addEventListener("submit", async (e) => {
    e.preventDefault();
    const statusEl = contactForm.querySelector("#sn-contact-status");
    const submitBtn = contactForm.querySelector("#sn-contact-submit");
    statusEl.className = "sn-form-status";
    statusEl.textContent = "";

    const raw = Object.fromEntries(new FormData(contactForm).entries());
    const check = validateContact(raw, { checkTiming: false });

    for (const errEl of contactForm.querySelectorAll("[data-err]")) {
      const field = errEl.dataset.err;
      errEl.textContent = check.errors[field] || "";
    }

    if (!check.valid) {
      statusEl.className = "sn-form-status is-error";
      statusEl.textContent = "VALIDATION ERROR // Please verify highlighted fields.";
      return;
    }

    submitBtn.disabled = true;
    submitBtn.textContent = "Transmitting...";

    const buildMailtoHref = (targetEmail) => {
      const subject = `[Portfolio] ${check.data.subject}`;
      const bodyText = `From: ${check.data.name} <${check.data.email}>\n\n${check.data.message}`;
      return `mailto:${encodeURIComponent(targetEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(bodyText)}`;
    };

    const showFallbackError = (msg, targetEmail) => {
      statusEl.className = "sn-form-status is-error";
      statusEl.innerHTML = `${escapeHtml(msg)} <a href="${buildMailtoHref(targetEmail)}" style="color:inherit;text-decoration:underline;font-weight:700;margin-left:6px">Open in Email App ↗</a>`;
    };

    try {
      const res = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(raw),
      });
      const data = await res.json().catch(() => ({}));
      if (res.ok && data.ok) {
        statusEl.className = "sn-form-status is-success";
        statusEl.textContent = data.message || "TRANSMISSION DELIVERED // Thank you for reaching out.";
        contactForm.reset();
        contactForm.querySelector('input[name="startedAt"]').value = String(Date.now());
      } else if (data.code === "EMAIL_PROVIDER_UNCONFIGURED" && data.relay === "formsubmit") {
        // Server validated input & spam guards, but RESEND_API_KEY is not set yet.
        // Relay live from the visitor's browser via FormSubmit AJAX so real email arrives!
        const targetEmail = data.to || profile.email || "ahmedakka765@gmail.com";
        try {
          const fsRes = await fetch(`https://formsubmit.co/ajax/${encodeURIComponent(targetEmail)}`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Accept: "application/json",
            },
            body: JSON.stringify({
              name: check.data.name,
              email: check.data.email,
              _replyto: check.data.email,
              _subject: `[Portfolio] ${check.data.subject}`,
              message: check.data.message,
              _template: "table",
              _captcha: "false",
            }),
          });
          const fsData = await fsRes.json().catch(() => ({}));
          const delivered = fsRes.ok && (fsData.success === true || fsData.success === "true");
          if (delivered) {
            statusEl.className = "sn-form-status is-success";
            statusEl.textContent = `Thanks ${check.data.name.split(" ")[0]}! Your message has been delivered to ${targetEmail} — I'll reply soon.`;
            contactForm.reset();
            contactForm.querySelector('input[name="startedAt"]').value = String(Date.now());
          } else if (/activat/i.test(String(fsData.message || ""))) {
            showFallbackError(
              `ACTIVATION REQUIRED // FormSubmit sent a 1-click "Activate Form" email to ${targetEmail}. Click it once in your inbox (or add RESEND_API_KEY in Vercel) so emails deliver automatically.`,
              targetEmail,
            );
          } else {
            showFallbackError(
              `EMAIL NOT DELIVERED // ${fsData.message || "Email relay could not deliver from this origin. Configure RESEND_API_KEY in .env / Vercel, or send directly:"}`,
              targetEmail,
            );
          }
        } catch {
          showFallbackError(
            `EMAIL NOT DELIVERED // Could not reach email relay (configure RESEND_API_KEY in .env / Vercel).`,
            targetEmail,
          );
        }
      } else {
        if (data.errors) {
          for (const [k, msg] of Object.entries(data.errors)) {
            const el = contactForm.querySelector(`[data-err="${k}"]`);
            if (el) el.textContent = msg;
          }
        }
        showFallbackError(data.error || "TRANSMISSION FAILED // Please try again.", data.to || profile.email);
      }
    } catch {
      showFallbackError("NETWORK ERROR // Unable to reach transmission endpoint.", profile.email);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Send Transmission ↗";
    }
  });

  // Global click delegation for navigation & actions
  function syncAudioBtnLabel() {
    const audioBtn = topbar.querySelector("#sn-audio-btn");
    if (audioBtn) {
      audioBtn.textContent = getIsMusicPlaying() ? "Sound: ON" : "Sound: OFF";
    }
  }

  root.addEventListener("click", (e) => {
    const navBtn = e.target.closest("[data-nav-scroll]");
    if (navBtn) {
      scrollToSection(navBtn.dataset.navScroll);
      return;
    }

    const actBtn = e.target.closest("[data-action]");
    if (!actBtn) return;
    const action = actBtn.dataset.action;

    if (action === "enter-3d-world") {
      enter3dWalkMode();
    } else if (action === "exit-3d-world") {
      exit3dWalkMode();
    } else if (action === "toggle-chat") {
      chat.classList.toggle("is-open");
      if (chat.classList.contains("is-open")) {
        document.exitPointerLock?.();
        chatInput.focus();
      }
    } else if (action === "toggle-audio") {
      if (getIsMusicPlaying()) {
        wasBgMusicPlayingBeforePromo = false;
        appShell?.audioButton?.pause?.();
      } else {
        if (promoVideoEl && !promoVideoEl.paused) {
          wasBgMusicPlayingBeforePromo = false;
          promoVideoEl.pause();
        }
        appShell?.audioButton?.play?.()?.catch?.(() => {});
      }
      setTimeout(syncAudioBtnLabel, 80);
    } else if (action === "toggle-theme") {
      isLightTheme = !isLightTheme;
      document.body.classList.toggle("pf-theme-light", isLightTheme);
      localStorage.setItem("pf_theme", isLightTheme ? "light" : "dark");
      const themeBtn = topbar.querySelector("#sn-theme-btn");
      if (themeBtn) themeBtn.textContent = isLightTheme ? "Dark" : "Light";
    } else if (action === "toggle-pov") {
      const next3p = world?.avatar?.toggleThirdPerson?.() ?? true;
      const povBtn = returnBar.querySelector("#sn-pov-btn");
      if (povBtn) povBtn.textContent = `View: ${next3p ? "3RD PERSON" : "1ST PERSON"} (V)`;
    }
  });

  world?.avatar?.onPerspectiveChange?.((is3p) => {
    const povBtn = returnBar.querySelector("#sn-pov-btn");
    if (povBtn) povBtn.textContent = `View: ${is3p ? "3RD PERSON" : "1ST PERSON"} (V)`;
  });

  // Keyboard shortcuts for Case Study Modal (ESC, Left/Right arrows)
  window.addEventListener("keydown", (e) => {
    if (activeCaseStudyIndex !== -1) {
      if (e.key === "Escape") {
        closeCaseStudy();
      } else if (e.key === "ArrowRight") {
        openCaseStudy(activeCaseStudyIndex + 1);
      } else if (e.key === "ArrowLeft") {
        openCaseStudy(activeCaseStudyIndex - 1);
      }
    }
  });

  // ---------------------------------------------------------------------------
  // 9. 60fps Animation Loop (Cursor, Distortion Canvas,
  //    Scroll-Velocity Kinetic Typography, and 3D WebGPU Camera Choreography)
  // ---------------------------------------------------------------------------
  const heroHeadline = scrollViewport.querySelector("#sn-hero-headline");

  let lastScrollTop = 0;
  let scrollVelocity = 0;
  let smoothScrollNorm = 0;
  let previewX = window.innerWidth * 0.65;
  let previewY = window.innerHeight * 0.5;
  let waveTime = 0;

  scrollViewport.addEventListener(
    "scroll",
    () => {
      if (avatarFocusOverride) {
        avatarFocusOverride = false;
        document.body.classList.remove("sn-peeking-3d");
      }
      // Update active nav link based on scroll position
      const st = scrollViewport.scrollTop;
      const sections = ["hero", "works", "lab", "about", "contact"];
      let currentSec = "works";
      for (const id of sections) {
        const el = scrollViewport.querySelector(`#sn-sec-${id}`);
        if (el && st + 240 >= el.offsetTop) {
          currentSec = id;
        }
      }
      for (const link of topbar.querySelectorAll(".sn-nav-link")) {
        link.classList.toggle("is-active", link.dataset.navScroll === currentSec);
      }
    },
    { passive: true },
  );

  function tick() {
    requestAnimationFrame(tick);
    waveTime += 0.065;

    // 1. Custom Magnetic Cursor & Velocity
    pointer.curX = lerp(pointer.curX, pointer.x, 0.28);
    pointer.curY = lerp(pointer.curY, pointer.y, 0.28);
    pointer.velX = pointer.curX - pointer.prevX;
    pointer.velY = pointer.curY - pointer.prevY;
    pointer.prevX = pointer.curX;
    pointer.prevY = pointer.curY;
    pointer.smoothNdcX = lerp(pointer.smoothNdcX, pointer.ndcX, 0.06);
    pointer.smoothNdcY = lerp(pointer.smoothNdcY, pointer.ndcY, 0.06);

    cursor.style.transform = `translate3d(${pointer.curX.toFixed(1)}px, ${pointer.curY.toFixed(1)}px, 0)`;

    // 2. Scroll Progress & Scroll-Velocity Kinetic Typography Skew
    const maxScroll = Math.max(1, scrollViewport.scrollHeight - scrollViewport.clientHeight);
    const curScroll = scrollViewport.scrollTop;
    const rawVel = curScroll - lastScrollTop;
    lastScrollTop = curScroll;
    scrollVelocity = lerp(scrollVelocity, rawVel, 0.15);
    const targetScrollNorm = clamp(curScroll / maxScroll, 0, 1);
    smoothScrollNorm = lerp(smoothScrollNorm, targetScrollNorm, 0.08);

    if (heroHeadline && curScroll < window.innerHeight) {
      const skew = clamp(scrollVelocity * -0.035, -3.5, 3.5);
      heroHeadline.style.transform = `skewY(${skew.toFixed(2)}deg)`;
    }

    // 3. Floating 60fps Media Preview Canvas (anchored to the right of the title column)
    if (hoveredProjectIndex !== -1) {
      const targetPrevX = clamp(
        Math.max(pointer.x + 42, window.innerWidth * 0.56),
        320,
        Math.max(340, window.innerWidth - 420),
      );
      const targetPrevY = clamp(pointer.y - 110, 82, Math.max(90, window.innerHeight - 250));
      previewX = lerp(previewX, targetPrevX, 0.18);
      previewY = lerp(previewY, targetPrevY, 0.18);
      const rot = clamp(pointer.velX * 0.18, -5, 5);
      hoverPreview.style.transform = `translate3d(${previewX.toFixed(1)}px, ${previewY.toFixed(1)}px, 0) rotate(${rot.toFixed(2)}deg) scale(1)`;

      const sourceMedia =
        previewVideo.readyState >= 2
          ? previewVideo
          : previewPosterImg.complete && previewPosterImg.naturalWidth > 0
            ? previewPosterImg
            : null;

      if (sourceMedia && hoverCtx) {
        const cw = hoverCanvas.width;
        const ch = hoverCanvas.height;
        const speed = Math.min(18, Math.hypot(pointer.velX, pointer.velY));
        const slices = 16;
        const sliceH = ch / slices;
        const srcW = sourceMedia.videoWidth || sourceMedia.naturalWidth || cw;
        const srcH = sourceMedia.videoHeight || sourceMedia.naturalHeight || ch;
        const srcSliceH = srcH / slices;

        hoverCtx.clearRect(0, 0, cw, ch);
        for (let i = 0; i < slices; i++) {
          const wave = Math.sin(waveTime + i * 0.45) * (0.4 + speed * 0.22);
          hoverCtx.drawImage(
            sourceMedia,
            0,
            i * srcSliceH,
            srcW,
            srcSliceH,
            wave,
            i * sliceH,
            cw,
            sliceH + 0.8,
          );
        }
      }
    }

    // 4. 3D WebGPU Camera Choreography (Smooth Scroll Spline + Mouse Parallax)
    if (!is3dWalkMode && !avatarFocusOverride && camera && cameraDirector) {
      const sampled = sampleCameraPath(smoothScrollNorm);
      const desiredPos = sampled.pos;
      const desiredTarget = sampled.target;

      // Add smooth mouse-reactive parallax offset
      const px = desiredPos[0] + pointer.smoothNdcY * 0.45;
      const py = desiredPos[1] + pointer.smoothNdcY * 0.38;
      const pz = desiredPos[2] + pointer.smoothNdcX * 0.95;

      camera.position.x = lerp(camera.position.x, px, 0.055);
      camera.position.y = lerp(camera.position.y, py, 0.055);
      camera.position.z = lerp(camera.position.z, pz, 0.055);

      const ctrlTarget = cameraDirector.controls.target;
      ctrlTarget.x = lerp(ctrlTarget.x, desiredTarget[0], 0.065);
      ctrlTarget.y = lerp(ctrlTarget.y, desiredTarget[1] + pointer.smoothNdcY * 0.45, 0.065);
      ctrlTarget.z = lerp(ctrlTarget.z, desiredTarget[2] - pointer.smoothNdcX * 0.75, 0.065);

      camera.lookAt(ctrlTarget);
    }
  }

  root.appendChild(vignette);
  root.appendChild(topbar);
  root.appendChild(returnBar);
  root.appendChild(scrollViewport);
  root.appendChild(hoverPreview);
  root.appendChild(caseModal);
  root.appendChild(chat);
  root.appendChild(cursor);
  document.body.appendChild(root);

  bindWorksInteractions();

  gsap.from(scrollViewport.querySelectorAll(".sn-hero-line"), {
    yPercent: 105,
    opacity: 0,
    duration: 1.0,
    stagger: 0.09,
    ease: "power4.out",
    delay: 0.25,
  });

  if ("IntersectionObserver" in window) {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            gsap.fromTo(
              entry.target,
              { y: 28, opacity: 0 },
              { y: 0, opacity: 1, duration: 0.75, ease: "power3.out", overwrite: "auto" },
            );
            observer.unobserve(entry.target);
          }
        }
      },
      { root: scrollViewport, threshold: 0.08 },
    );

    for (const el of scrollViewport.querySelectorAll(
      ".sn-section-header, .sn-panel, .sn-cap-cell, .sn-timeline-row",
    )) {
      observer.observe(el);
    }
  }

  requestAnimationFrame(tick);

  return {
    root,
    openCaseStudy,
    closeCaseStudy,
    enter3dWalkMode,
    exit3dWalkMode,
    openChat: () => chat.classList.add("is-open"),
    flyCameraToAvatar: focusAvatarIn3D,
  };
}
