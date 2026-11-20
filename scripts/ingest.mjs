#!/usr/bin/env node
/**
 * RAG ingestion: documents → chunks → embeddings → data/vector-index.json
 *
 * Sources
 *   1. content/profile.json   (the same file that renders the website)
 *   2. knowledge/**  .md / .txt / .pdf  (CV, project write-ups, extra notes)
 *
 * Usage:  npm run ingest            (uses GEMINI_API_KEY from .env)
 *         npm run ingest -- --no-embed   (keyword-only index, no API calls)
 */
import { readFileSync, writeFileSync, readdirSync, statSync, existsSync, mkdirSync } from "node:fs";
import { join, extname, basename, relative } from "node:path";

const ROOT = process.cwd();
try {
  process.loadEnvFile?.(join(ROOT, ".env"));
} catch {
  /* no .env — fine */
}

const { embedTexts, hasGeminiKey, GEMINI_DEFAULTS } = await import("../api/_lib/gemini.js");

const args = new Set(process.argv.slice(2));
const CHUNK_SIZE = 700; // characters (~150-180 tokens)
const CHUNK_OVERLAP = 120;

/* ----------------------------------------------------------- documents -- */

function profileToDocuments(p) {
  const docs = [];
  const add = (sourceId, title, section, text, itemId = null) =>
    docs.push({ sourceId, title, section, itemId, source: "content/profile.json", text: text.trim() });

  add(
    "profile-overview",
    "Profile overview",
    "home",
    `${p.name} (${p.shortName || ""}) — ${p.role}. ${p.tagline} Location: ${p.location}. ${p.availability || ""}.
Spoken languages: ${(p.languages || []).join(", ")}. Interests: ${(p.interests || []).join(", ")}.`,
  );
  add("about", "About me", "about", (p.about || []).join("\n\n"));

  if (p.stats?.length) {
    add("stats", "Quick stats", "home", p.stats.map((s) => `${s.label}: ${s.value}`).join(". "));
  }

  for (const g of p.skills || []) {
    add(`skills-${g.group}`, `Skills — ${g.group}`, "skills", `${p.name}'s ${g.group} skills: ${g.items.join(", ")}.`);
  }
  add(
    "skills-all",
    "All skills and technologies",
    "skills",
    `Complete list of ${p.name}'s skills: ${(p.skills || []).flatMap((g) => g.items).join(", ")}.`,
  );

  for (const pr of p.projects || []) {
    const links = Object.entries(pr.links || {})
      .map(([k, v]) => `${k}: ${v}`)
      .join(", ");
    add(
      `project-${pr.id}`,
      `Project — ${pr.title}`,
      "projects",
      `Project "${pr.title}" (${pr.year}, category: ${pr.category}). Technologies: ${pr.tags.join(", ")}.
${pr.summary}
${pr.details || ""}${links ? `\nLinks: ${links}` : ""}${pr.featured ? "\nThis is a featured project." : ""}`,
      pr.id,
    );
  }
  add(
    "projects-list",
    "List of projects",
    "projects",
    `${p.name} has worked on these projects: ${(p.projects || []).map((x) => `${x.title} (${x.year}, ${x.category})`).join("; ")}.`,
  );

  if (p.achievements?.length) {
    add(
      "achievements",
      "Achievements",
      "projects",
      `${p.name}'s achievements and awards:\n${p.achievements.map((a) => `- ${a.title} (${a.year}): ${a.description}`).join("\n")}`,
      "achievements",
    );
  }

  for (const [i, e] of (p.education || []).entries()) {
    add(`edu-${i}`, `Education — ${e.degree}`, "journey", `Education: ${e.degree} at ${e.institution} (${e.period}). ${e.details || ""}`);
  }
  for (const [i, x] of (p.experience || []).entries()) {
    add(`exp-${i}`, `Experience — ${x.role}`, "journey", `Experience: ${x.role} at ${x.company} (${x.period}). ${x.details || ""}`);
  }

  const socials = Object.entries(p.socials || {})
    .map(([k, v]) => `${k}: ${v}`)
    .join(", ");
  add(
    "contact",
    "Contact information",
    "contact",
    `To contact ${p.name}, use the contact form on this website (name, email, subject, message) or email ${p.email}. ${socials ? `Profiles: ${socials}.` : ""} ${p.availability || ""}`,
  );
  return docs;
}

function walk(dir) {
  if (!existsSync(dir)) return [];
  return readdirSync(dir).flatMap((name) => {
    const full = join(dir, name);
    return statSync(full).isDirectory() ? walk(full) : [full];
  });
}

function parseFrontmatter(text) {
  const m = text.match(/^---\r?\n([\s\S]*?)\r?\n---\r?\n?/);
  if (!m) return { meta: {}, body: text };
  const meta = {};
  for (const line of m[1].split(/\r?\n/)) {
    const kv = line.match(/^(\w+):\s*(.*)$/);
    if (kv) meta[kv[1]] = kv[2].trim().replace(/^["']|["']$/g, "");
  }
  return { meta, body: text.slice(m[0].length) };
}

async function readPdf(file) {
  const { extractText, getDocumentProxy } = await import("unpdf");
  const pdf = await getDocumentProxy(new Uint8Array(readFileSync(file)));
  const { text } = await extractText(pdf, { mergePages: true });
  return Array.isArray(text) ? text.join("\n\n") : text;
}

async function knowledgeDocuments() {
  const docs = [];
  for (const file of walk(join(ROOT, "knowledge"))) {
    const ext = extname(file).toLowerCase();
    if (![".md", ".txt", ".pdf"].includes(ext) || basename(file).toLowerCase() === "readme.md") continue;
    let raw = ext === ".pdf" ? await readPdf(file) : readFileSync(file, "utf8");
    const { meta, body } = ext === ".pdf" ? { meta: {}, body: raw } : parseFrontmatter(raw);
    const rel = relative(ROOT, file).replace(/\\/g, "/");
    const name = basename(file, ext);
    docs.push({
      sourceId: `kb-${name}`,
      title: meta.title || name.replace(/[-_]/g, " "),
      section: meta.section || (/cv|resume/i.test(name) ? "about" : "about"),
      itemId: meta.itemId || null,
      source: rel,
      text: body.replace(/\u0000/g, "").trim(),
    });
  }
  return docs;
}

/* ------------------------------------------------------------- chunking -- */

function splitSentences(text) {
  return text.match(/[^.!?\n]+(?:[.!?]+|\n+|$)/g)?.map((s) => s.trim()).filter(Boolean) ?? [text];
}

/** Heading-aware, sentence-boundary chunker with character overlap. */
export function chunkDocument(doc) {
  const sections = [];
  let current = { heading: "", lines: [] };
  for (const line of doc.text.split(/\r?\n/)) {
    const h = line.match(/^#{1,4}\s+(.*)/);
    if (h) {
      if (current.lines.join("").trim()) sections.push(current);
      current = { heading: h[1].trim(), lines: [] };
    } else current.lines.push(line);
  }
  if (current.lines.join("").trim()) sections.push(current);

  const chunks = [];
  for (const sec of sections) {
    const text = sec.lines.join("\n").replace(/\n{3,}/g, "\n\n").trim();
    const prefix = sec.heading ? `${sec.heading}: ` : "";
    if (text.length + prefix.length <= CHUNK_SIZE) {
      chunks.push(prefix + text);
      continue;
    }
    let buf = "";
    for (const sentence of splitSentences(text)) {
      if ((buf + " " + sentence).length > CHUNK_SIZE && buf) {
        chunks.push(prefix + buf.trim());
        buf = buf.slice(-CHUNK_OVERLAP).replace(/^\S*\s/, "") + " " + sentence;
      } else buf += " " + sentence;
    }
    if (buf.trim()) chunks.push(prefix + buf.trim());
  }

  return chunks.map((text, i) => ({
    id: `${doc.sourceId}#${i}`,
    text,
    meta: {
      sourceId: doc.sourceId,
      title: doc.title,
      section: doc.section,
      itemId: doc.itemId,
      source: doc.source,
    },
  }));
}

/* ----------------------------------------------------------------- main -- */

const profile = JSON.parse(readFileSync(join(ROOT, "content", "profile.json"), "utf8"));
const documents = [...profileToDocuments(profile), ...(await knowledgeDocuments())];
const chunks = documents.flatMap(chunkDocument);

console.log(`📄 ${documents.length} documents → ${chunks.length} chunks`);

let embedded = false;
if (!args.has("--no-embed") && hasGeminiKey()) {
  console.log(`🧠 Embedding with ${GEMINI_DEFAULTS.embedModel} (${GEMINI_DEFAULTS.embedDims} dims)…`);
  const vectors = await embedTexts(
    chunks.map((c) => c.text),
    { taskType: "RETRIEVAL_DOCUMENT", titles: chunks.map((c) => c.meta.title) },
  );
  chunks.forEach((c, i) => (c.embedding = vectors[i].map((v) => Number(v.toFixed(6)))));
  embedded = true;
} else {
  console.warn("⚠️  No GEMINI_API_KEY (or --no-embed): building a keyword-only (BM25) index.");
}

const index = {
  version: 1,
  owner: profile.name,
  createdAt: new Date().toISOString(),
  embedModel: embedded ? GEMINI_DEFAULTS.embedModel : null,
  dims: embedded ? GEMINI_DEFAULTS.embedDims : 0,
  chunkSize: CHUNK_SIZE,
  chunkOverlap: CHUNK_OVERLAP,
  sources: [...new Set(documents.map((d) => d.source))],
  chunks,
};

mkdirSync(join(ROOT, "data"), { recursive: true });
writeFileSync(join(ROOT, "data", "vector-index.json"), JSON.stringify(index));
console.log(`✅ Wrote data/vector-index.json (${embedded ? "hybrid dense+BM25" : "BM25 only"})`);
