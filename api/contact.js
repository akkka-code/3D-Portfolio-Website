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

export async function sendWithWeb3Forms({ accessKey, name, email, subject, message }) {
  const response = await fetch("https://api.web3forms.com/submit", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
    body: JSON.stringify({
      access_key: accessKey,
      name,
      email,
      subject: `[Portfolio] ${subject}`.slice(0, 150),
      message,
    }),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok || !body?.success) {
    const err = new Error(body?.message || `Web3Forms error ${response.status}`);
    err.status = response.status;
    throw err;
  }
  return body;
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

  if (spam.honeypot || spam.tooFast || spam.noTimestamp) {
    console.warn("[contact] spam blocked", { ip, ...spam });
    return sendJson(res, 200, { ok: true, message: "Thanks! Your message has been sent." });
  }

  if (!valid) {
    return sendJson(res, 422, { ok: false, error: "Please fix the highlighted fields.", errors });
  }

  const to = process.env.CONTACT_TO_EMAIL || "ahmedakka765@gmail.com";
  const from = process.env.CONTACT_FROM_EMAIL || "Portfolio Contact <onboarding@resend.dev>";
  const resendKey = (process.env.RESEND_API_KEY || "").trim();
  const hasRealResendKey = Boolean(resendKey && !resendKey.startsWith("re_your_"));
  const web3FormsKey = (process.env.WEB3FORMS_ACCESS_KEY || "").trim();
  const hasRealWeb3FormsKey = Boolean(web3FormsKey && !web3FormsKey.startsWith("your_"));

  const { html, text } = buildEmail(data, { ip, time: new Date().toISOString() });

  if (hasRealResendKey) {
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
        provider: "resend",
        message: `Thanks ${data.name.split(" ")[0]}! Your message has been delivered — I'll reply soon.`,
      });
    } catch (error) {
      console.error("[contact] Resend send failed:", error.message);
      return sendJson(res, 502, {
        ok: false,
        code: "PROVIDER_ERROR",
        to,
        error: `Email delivery failed (${error.message}). Please try again or email ${to} directly.`,
      });
    }
  }

  if (hasRealWeb3FormsKey) {
    try {
      await sendWithWeb3Forms({
        accessKey: web3FormsKey,
        name: data.name,
        email: data.email,
        subject: data.subject,
        message: data.message,
      });
      return sendJson(res, 200, {
        ok: true,
        provider: "web3forms",
        message: `Thanks ${data.name.split(" ")[0]}! Your message has been delivered — I'll reply soon.`,
      });
    } catch (error) {
      console.error("[contact] Web3Forms send failed:", error.message);
      return sendJson(res, 502, {
        ok: false,
        code: "PROVIDER_ERROR",
        to,
        error: `Email delivery failed (${error.message}). Please try again or email ${to} directly.`,
      });
    }
  }

  // Only allow dry-run success during automated test runs (scripts/test-api.mjs)
  if (process.env.CONTACT_DRY_RUN === "1") {
    console.info("[contact] Dry-run validated (CONTACT_DRY_RUN=1):", {
      to,
      from: `${data.name} <${data.email}>`,
      subject: data.subject,
    });
    return sendJson(res, 200, {
      ok: true,
      id: `dryrun_${Date.now()}`,
      mode: "dry_run",
      message: `Dry-run validated for ${to}.`,
    });
  }

  // Never falsely report success when no server email provider key is configured!
  console.warn("[contact] No email API key configured (set RESEND_API_KEY or WEB3FORMS_ACCESS_KEY).");
  return sendJson(res, 503, {
    ok: false,
    code: "EMAIL_PROVIDER_UNCONFIGURED",
    relay: "formsubmit",
    to,
    error: "Server email API key is not configured yet — attempting direct email relay.",
  });
}
