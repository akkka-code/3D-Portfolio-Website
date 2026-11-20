/**
 * Retrieval layer of the RAG pipeline.
 *
 * - Loads the pre-built vector index (data/vector-index.json, created by
 *   `npm run ingest`).
 * - Hybrid search: dense cosine similarity on Gemini embeddings + sparse
 *   BM25 keyword scoring (helps with names, acronyms, exact tech terms).
 * - Falls back to BM25-only when the index has no embeddings or the
 *   embedding API is unavailable.
 */
import { readFileSync, existsSync } from "node:fs";
import { join } from "node:path";

let cached = null;

const STOPWORDS = new Set(
  "a an the and or of to in on for with is are was were be been his her he she him it its this that what which who whom how when where why do does did have has had about tell me you your i my can could would should please there their them they as at by from into than then so if not no yes any all some more most much many".split(
    " ",
  ),
);

export function tokenize(text = "") {
  return text
    .toLowerCase()
    .normalize("NFKD")
    .replace(/[^\p{L}\p{N}+#.\s-]/gu, " ")
    .split(/\s+/)
    .map((t) => t.replace(/^[.-]+|[.-]+$/g, ""))
    .filter((t) => t.length > 1 && !STOPWORDS.has(t));
}

function buildBm25(chunks) {
  const docs = chunks.map((c) => tokenize(`${c.meta.title} ${c.meta.title} ${c.text}`));
  const df = new Map();
  for (const tokens of docs) {
    for (const t of new Set(tokens)) df.set(t, (df.get(t) || 0) + 1);
  }
  const avgdl = docs.reduce((s, d) => s + d.length, 0) / Math.max(docs.length, 1);
  const tfs = docs.map((tokens) => {
    const tf = new Map();
    for (const t of tokens) tf.set(t, (tf.get(t) || 0) + 1);
    return { tf, len: tokens.length };
  });
  return { df, avgdl, tfs, N: docs.length };
}

function bm25Scores(bm25, queryTokens, k1 = 1.4, b = 0.75) {
  const { df, avgdl, tfs, N } = bm25;
  return tfs.map(({ tf, len }) => {
    let score = 0;
    for (const q of queryTokens) {
      const f = tf.get(q);
      if (!f) continue;
      const n = df.get(q) || 0;
      const idf = Math.log(1 + (N - n + 0.5) / (n + 0.5));
      score += idf * ((f * (k1 + 1)) / (f + k1 * (1 - b + (b * len) / avgdl)));
    }
    return score;
  });
}

export function loadIndex() {
  if (cached) return cached;
  const file = join(process.cwd(), "data", "vector-index.json");
  if (!existsSync(file)) {
    throw new Error("Vector index not found. Run `npm run ingest` first.");
  }
  const index = JSON.parse(readFileSync(file, "utf8"));
  const hasEmbeddings = index.chunks.every((c) => Array.isArray(c.embedding) && c.embedding.length);
  cached = { ...index, hasEmbeddings, bm25: buildBm25(index.chunks) };
  return cached;
}

function dot(a, b) {
  let s = 0;
  for (let i = 0; i < a.length; i++) s += a[i] * b[i];
  return s;
}

/**
 * @param {string} query
 * @param {number[]|null} queryEmbedding
 * @returns {Array<{chunk, score, dense, sparse}>}
 */
export function search(query, queryEmbedding, { k = 6 } = {}) {
  const index = loadIndex();
  const qTokens = tokenize(query);
  const sparse = bm25Scores(index.bm25, qTokens);
  const maxSparse = Math.max(...sparse, 1e-9);

  const useDense = Boolean(queryEmbedding && index.hasEmbeddings);
  const results = index.chunks.map((chunk, i) => {
    const dense = useDense ? dot(queryEmbedding, chunk.embedding) : 0;
    const sparseNorm = sparse[i] / maxSparse;
    const score = useDense ? 0.75 * dense + 0.25 * sparseNorm * Math.max(dense, 0.3) : sparseNorm;
    return { chunk, score, dense, sparse: sparse[i] };
  });

  results.sort((a, b) => b.score - a.score);

  // Diversity: at most 2 chunks from the same source section.
  const picked = [];
  const perSource = new Map();
  for (const r of results) {
    const key = r.chunk.meta.sourceId;
    const n = perSource.get(key) || 0;
    if (n >= 2) continue;
    perSource.set(key, n + 1);
    picked.push(r);
    if (picked.length >= k) break;
  }
  return { results: picked, mode: useDense ? "hybrid" : "keyword" };
}
