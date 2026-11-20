/**
 * Tiny helpers shared by the serverless functions. Works both on Vercel
 * (Node runtime, req.body pre-parsed) and in the local Vite dev middleware.
 * Files under api/_lib are NOT exposed as routes (underscore prefix).
 */

export function sendJson(res, status, payload) {
  res.statusCode = status;
  res.setHeader("Content-Type", "application/json; charset=utf-8");
  res.setHeader("Cache-Control", "no-store");
  res.setHeader("X-Content-Type-Options", "nosniff");
  res.end(JSON.stringify(payload));
}

export async function readJsonBody(req, maxBytes = 32 * 1024) {
  if (req.body && typeof req.body === "object") return req.body;
  if (typeof req.body === "string") return JSON.parse(req.body || "{}");

  return new Promise((resolve, reject) => {
    let size = 0;
    const chunks = [];
    req.on("data", (chunk) => {
      size += chunk.length;
      if (size > maxBytes) {
        reject(Object.assign(new Error("Payload too large"), { status: 413 }));
        req.destroy?.();
        return;
      }
      chunks.push(chunk);
    });
    req.on("end", () => {
      try {
        const text = Buffer.concat(chunks).toString("utf8");
        resolve(text ? JSON.parse(text) : {});
      } catch {
        reject(Object.assign(new Error("Invalid JSON"), { status: 400 }));
      }
    });
    req.on("error", reject);
  });
}

export function getClientIp(req) {
  const fwd = req.headers?.["x-forwarded-for"];
  if (typeof fwd === "string" && fwd.length) return fwd.split(",")[0].trim();
  return req.headers?.["x-real-ip"] || req.socket?.remoteAddress || "unknown";
}

/**
 * Best-effort sliding-window rate limiter (per warm serverless instance).
 * Good enough for basic abuse protection on a portfolio.
 */
export function createRateLimiter({ windowMs, max }) {
  const hits = new Map();
  return function isLimited(key) {
    const now = Date.now();
    const list = (hits.get(key) || []).filter((t) => now - t < windowMs);
    list.push(now);
    hits.set(key, list);
    if (hits.size > 5000) hits.clear();
    return list.length > max;
  };
}

/** Reject cross-site browser posts when ALLOWED_ORIGINS is configured. */
export function isOriginAllowed(req) {
  const allowed = (process.env.ALLOWED_ORIGINS || "")
    .split(",")
    .map((s) => s.trim())
    .filter(Boolean);
  if (!allowed.length) return true;
  const origin = req.headers?.origin;
  if (!origin) return true; // same-origin requests from some browsers / curl
  return allowed.some((a) => origin === a || (a.startsWith("*.") && origin.endsWith(a.slice(1))));
}

export function methodGuard(req, res, method = "POST") {
  if (req.method === "OPTIONS") {
    res.statusCode = 204;
    res.setHeader("Allow", `${method}, OPTIONS`);
    res.end();
    return false;
  }
  if (req.method !== method) {
    res.setHeader("Allow", `${method}, OPTIONS`);
    sendJson(res, 405, { ok: false, error: "Method not allowed" });
    return false;
  }
  return true;
}
