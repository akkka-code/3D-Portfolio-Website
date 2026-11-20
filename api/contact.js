/**
 * POST /api/contact
 * Validates the contact form server-side, applies spam protection and sends
 * the message to the portfolio owner via the Resend email API.
 *
 * Env (never commit real values — see .env.example):
 *   RESEND_API_KEY      Resend API key (re_...)
 *   CONTACT_TO_EMAIL    Where messages are delivered (your inbox)
 *   CONTACT_FROM_EMAIL  Verified sender, e.g. "Portfolio <onboarding@resend.dev>"
 */
import { validateContact, escapeHtml } from "../shared/validation.js";
import {
  sendJson,
  readJsonBody,
  getClientIp,
  createRateLimiter,
  isOriginAllowed,
  methodGuard,
} from "./_lib/http.js";

const isLimited = createRateLimiter({ windowMs: 10 * 60 * 1000, max: 5 });

function buildEmail({ name, email, subject, message }, meta) {
  const safe = {
    name: escapeHtml(name),
    email: escapeHtml(email),
    subject: escapeHtml(subject),
    message: escapeHtml(message).replace(/\n/g, "<br>"),
  };

  const html = `
  <div style="font-family:Segoe UI,Arial,sans-serif;background:#0b0f1a;color:#e6f7ff;padding:24px">
    <div style="max-width:640px;margin:auto;background:#111827;border:1px solid #00e5ff55;border-radius:12px;overflow:hidden">
      <div style="padding:16px 20px;background:linear-gradient(90deg,#00e5ff33,#ff2bd633)">
        <h2 style="margin:0;font-size:18px;color:#00e5ff">New portfolio message</h2>
      </div>
      <div style="padding:20px">
        <p style="margin:0 0 6px"><b>From:</b> ${safe.name} &lt;${safe.email}&gt;</p>
        <p style="margin:0 0 16px"><b>Subject:</b> ${safe.subject}</p>
        <div style="padding:14px;background:#0b0f1a;border-radius:8px;line-height:1.6">${safe.message}</div>
        <p style="margin:16px 0 0;font-size:12px;color:#94a3b8">Sent ${escapeHtml(meta.time)} · IP ${escapeHtml(meta.ip)} · Reply directly to this email to answer ${safe.name}.</p>
      </div>
    </div>
  </div>`;

  const text = `New portfolio message\n\nFrom: ${name} <${email}>\nSubject: ${subject}\n\n${message}\n\n— Sent ${meta.time} (IP ${meta.ip})`;
  return { html, text };
}

export async function sendWithResend({ to, from, replyTo, subject, html, text }) {
  const response = await fetch("https://api.resend.com/emails", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${process.env.RESEND_API_KEY}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ from, to: [to], reply_to: replyTo, subject, html, text }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) {
    const err = new Error(body?.message || `Resend error ${response.status}`);
    err.status = response.status;
    throw err;
  }
  return body; // { id }
}

export default async function handler(req, res) {
  if (!methodGuard(req, res, "POST")) return;

  if (!isOriginAllowed(req)) {
    return sendJson(res, 403, { ok: false, error: "Origin not allowed." });
  }

  const ip = getClientIp(req);
  if (isLimited(ip)) {
    return sendJson(res, 429, {
      ok: false,
      error: "Too many messages. Please try again in a few minutes.",
    });
  }

  let body;
  try {
    body = await readJsonBody(req);
  } catch (error) {
    return sendJson(res, error.status || 400, { ok: false, error: error.message });
  }

  const { valid, errors, data, spam } = validateContact(body);

  // Silently "succeed" for bots so they don't learn what triggered the filter.
  if (spam.honeypot || spam.tooFast || spam.noTimestamp) {
    console.warn("[contact] spam blocked", { ip, ...spam });
    return sendJson(res, 200, { ok: true, message: "Thanks! Your message has been sent." });
  }

  if (!valid) {
    return sendJson(res, 422, { ok: false, error: "Please fix the highlighted fields.", errors });
  }

  const to = process.env.CONTACT_TO_EMAIL;
  const from = process.env.CONTACT_FROM_EMAIL || "Portfolio Contact <onboarding@resend.dev>";
  if (!process.env.RESEND_API_KEY || !to) {
    console.error("[contact] RESEND_API_KEY or CONTACT_TO_EMAIL is not configured");
    return sendJson(res, 503, {
      ok: false,
      error: "The contact service is not configured yet. Please email me directly.",
    });
  }

  const { html, text } = buildEmail(data, { ip, time: new Date().toISOString() });

  try {
    const result = await sendWithResend({
      to,
      from,
      replyTo: data.email,
      subject: `[Portfolio] ${data.subject}`.slice(0, 150),
      html,
      text,
    });
    return sendJson(res, 200, {
      ok: true,
      id: result.id,
      message: `Thanks ${data.name.split(" ")[0]}! Your message has been delivered — I'll reply soon.`,
    });
  } catch (error) {
    console.error("[contact] send failed:", error.message);
    return sendJson(res, 502, {
      ok: false,
      error: "Sorry, the message could not be sent right now. Please try again later.",
    });
  }
}
