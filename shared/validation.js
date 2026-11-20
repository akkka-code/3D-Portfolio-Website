/**
 * Shared validation rules for the contact form.
 * Imported by BOTH the browser (src/portfolio/sections/contact.js) and the
 * serverless function (api/contact.js) so frontend + backend stay in sync.
 */

export const CONTACT_LIMITS = {
  name: { min: 2, max: 80 },
  email: { max: 254 },
  subject: { min: 3, max: 120 },
  message: { min: 10, max: 4000 },
  /** Humans need at least this long to fill the form (ms). */
  minFillTimeMs: 3000,
};

// Pragmatic RFC 5322 subset — rejects spaces, missing TLD, double dots, etc.
const EMAIL_RE =
  /^(?!.*\.\.)[A-Za-z0-9._%+-]+@[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*\.[A-Za-z]{2,24}$/;

// Basic header-injection / control character guard for single-line fields.
const CONTROL_CHARS_RE = /[\u0000-\u001F\u007F]/;

const URL_RE = /(https?:\/\/|www\.)/gi;

export function normalizeContactInput(raw = {}) {
  const str = (value) => (typeof value === "string" ? value : "");
  return {
    name: str(raw.name).trim().replace(/\s+/g, " "),
    email: str(raw.email).trim().toLowerCase(),
    subject: str(raw.subject).trim().replace(/\s+/g, " "),
    message: str(raw.message).replace(/\r\n/g, "\n").trim(),
    // Honeypot: real users never see/fill this field.
    website: str(raw.website).trim(),
    startedAt: Number(raw.startedAt) || 0,
  };
}

/**
 * @returns {{ valid: boolean, errors: Record<string,string>, data: object }}
 */
export function validateContact(raw, { now = Date.now(), checkTiming = true } = {}) {
  const data = normalizeContactInput(raw);
  const errors = {};
  const L = CONTACT_LIMITS;

  if (data.name.length < L.name.min) errors.name = `Name must be at least ${L.name.min} characters.`;
  else if (data.name.length > L.name.max) errors.name = `Name must be at most ${L.name.max} characters.`;
  else if (CONTROL_CHARS_RE.test(data.name) || /[<>]/.test(data.name)) errors.name = "Name contains invalid characters.";

  if (!data.email) errors.email = "Email is required.";
  else if (data.email.length > L.email.max || !EMAIL_RE.test(data.email)) errors.email = "Please enter a valid email address.";

  if (data.subject.length < L.subject.min) errors.subject = `Subject must be at least ${L.subject.min} characters.`;
  else if (data.subject.length > L.subject.max) errors.subject = `Subject must be at most ${L.subject.max} characters.`;
  else if (CONTROL_CHARS_RE.test(data.subject)) errors.subject = "Subject contains invalid characters.";

  if (data.message.length < L.message.min) errors.message = `Message must be at least ${L.message.min} characters.`;
  else if (data.message.length > L.message.max) errors.message = `Message must be at most ${L.message.max} characters.`;
  else if ((data.message.match(URL_RE) || []).length > 3) errors.message = "Too many links in the message.";

  const spam = {
    honeypot: data.website.length > 0,
    tooFast: checkTiming && data.startedAt > 0 && now - data.startedAt < L.minFillTimeMs,
    noTimestamp: checkTiming && data.startedAt <= 0,
  };

  return { valid: Object.keys(errors).length === 0, errors, data, spam };
}

export function escapeHtml(value = "") {
  return String(value)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
