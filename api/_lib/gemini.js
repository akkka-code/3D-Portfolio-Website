/**
 * Minimal Google Gemini REST client (no SDK dependency).
 * Docs: https://ai.google.dev/api
 */

const BASE = "https://generativelanguage.googleapis.com/v1beta";

export const GEMINI_DEFAULTS = {
  chatModel: process.env.GEMINI_CHAT_MODEL || "gemini-3.7-flash",
  embedModel: process.env.GEMINI_EMBED_MODEL || "gemini-embedding-001",
  embedDims: Number(process.env.GEMINI_EMBED_DIMS || 768),
};

function apiKey() {
  const key = process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY;
  if (!key) throw Object.assign(new Error("GEMINI_API_KEY is not set"), { code: "NO_KEY" });
  return key;
}

export function hasGeminiKey() {
  return Boolean(process.env.GEMINI_API_KEY || process.env.GOOGLE_API_KEY);
}

async function post(path, body, { timeoutMs = 25000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);
  try {
    const response = await fetch(`${BASE}/${path}`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "x-goog-api-key": apiKey() },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    const json = await response.json().catch(() => ({}));
    if (!response.ok) {
      const err = new Error(json?.error?.message || `Gemini HTTP ${response.status}`);
      err.status = response.status;
      throw err;
    }
    return json;
  } finally {
    clearTimeout(timer);
  }
}

function l2normalize(vec) {
  let sum = 0;
  for (const v of vec) sum += v * v;
  const norm = Math.sqrt(sum) || 1;
  return vec.map((v) => v / norm);
}

/**
 * Embed many texts. taskType: RETRIEVAL_DOCUMENT | RETRIEVAL_QUERY
 * Vectors are L2-normalised so cosine similarity == dot product.
 */
export async function embedTexts(texts, { taskType = "RETRIEVAL_DOCUMENT", titles = [] } = {}) {
  const { embedModel, embedDims } = GEMINI_DEFAULTS;
  const out = [];
  const BATCH = 50;
  for (let i = 0; i < texts.length; i += BATCH) {
    const slice = texts.slice(i, i + BATCH);
    const json = await post(`models/${embedModel}:batchEmbedContents`, {
      requests: slice.map((text, j) => ({
        model: `models/${embedModel}`,
        content: { parts: [{ text }] },
        taskType,
        ...(taskType === "RETRIEVAL_DOCUMENT" && titles[i + j] ? { title: titles[i + j] } : {}),
        outputDimensionality: embedDims,
      })),
    });
    for (const e of json.embeddings || []) out.push(l2normalize(e.values));
  }
  return out;
}

export async function embedQuery(text) {
  const [vec] = await embedTexts([text], { taskType: "RETRIEVAL_QUERY" });
  return vec;
}

const FALLBACK_CHAT_MODELS = [
  "gemini-3.7-flash",
  "gemini-3.6-flash",
  "gemini-3.5-flash",
  "gemini-3.8-flash",
  "gemma-4-31b-it",
];

/**
 * Generate a grounded answer, trying fallback models if a model is experiencing a demand spike.
 * @param {{system: string, contents: Array<{role:'user'|'model', parts:[{text:string}]}>}} args
 */
export async function generate({ system, contents, temperature = 0.2, maxOutputTokens = 1100 }) {
  const models = [
    GEMINI_DEFAULTS.chatModel,
    ...FALLBACK_CHAT_MODELS.filter((m) => m !== GEMINI_DEFAULTS.chatModel),
  ];

  let lastErr = null;
  for (const model of models) {
    try {
      const json = await post(
        `models/${model}:generateContent`,
        {
          systemInstruction: { parts: [{ text: system }] },
          contents,
          generationConfig: {
            temperature,
            maxOutputTokens,
            ...(/2\.5-flash/.test(model) ? { thinkingConfig: { thinkingBudget: 0 } } : {}),
          },
          safetySettings: [
            { category: "HARM_CATEGORY_HARASSMENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
            { category: "HARM_CATEGORY_HATE_SPEECH", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
            { category: "HARM_CATEGORY_SEXUALLY_EXPLICIT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
            { category: "HARM_CATEGORY_DANGEROUS_CONTENT", threshold: "BLOCK_MEDIUM_AND_ABOVE" },
          ],
        },
        { timeoutMs: 12000 },
      );
      const text = (json.candidates?.[0]?.content?.parts || [])
        .map((p) => p.text || "")
        .join("")
        .trim();
      if (text) return text;
    } catch (err) {
      lastErr = err;
    }
  }
  throw lastErr || new Error("All Gemini models failed");
}
