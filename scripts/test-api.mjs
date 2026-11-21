#!/usr/bin/env node
/**
 * Automated verification of Module 4 (RAG Chatbot) and Module 5 (Email Contact System).
 */
import { join } from "node:path";

try {
  process.loadEnvFile?.(join(process.cwd(), ".env"));
} catch {}

import chatHandler from "../api/chat.js";
import contactHandler from "../api/contact.js";

function callHandler(handler, body) {
  return new Promise((resolve) => {
    const req = {
      method: "POST",
      headers: { "x-forwarded-for": "127.0.0.1" },
      body,
    };
    const res = {
      statusCode: 200,
      headers: {},
      setHeader(k, v) {
        this.headers[k] = v;
      },
      end(payload) {
        resolve({ status: this.statusCode, data: JSON.parse(payload || "{}") });
      },
    };
    handler(req, res);
  });
}

console.log("=== 1. Testing RAG Chatbot (Grounded Question) ===");
const q1 = await callHandler(chatHandler, {
  message: "What games has Syed Muhammad Ahmad built in Unity and Unreal Engine, and where does he study?",
});
console.log("Status:", q1.status);
console.log("Retrieval mode:", q1.data.retrieval, "| Model:", q1.data.model);
console.log("Answer:\n", q1.data.answer);
console.log("Citations:", q1.data.citations?.map((c) => `[${c.n}] ${c.title}`));

console.log("\n=== 2. Testing RAG Chatbot (Anti-Hallucination Guard) ===");
const q2 = await callHandler(chatHandler, {
  message: "What is Syed Muhammad Ahmad's favorite pizza topping and passport number?",
});
console.log("Answer:\n", q2.data.answer);

console.log("\n=== 3. Testing Contact Endpoint Validation ===");
const cBad = await callHandler(contactHandler, {
  name: "A",
  email: "not-an-email",
  subject: "Hi",
  message: "Short",
  startedAt: Date.now() - 10000,
});
console.log("Invalid payload status (expected 422):", cBad.status, cBad.data.errors);

console.log("\n=== 4. Testing Contact Endpoint Unconfigured Guard & Dry-Run ===");
const cUnconf = await callHandler(contactHandler, {
  name: "Ada Lovelace",
  email: "ada@analytical-engine.org",
  subject: "Game Development Collaboration",
  message: "Hi Ahmad, I explored your 3D WebGPU portfolio and loved Chrono Rebellion!",
  startedAt: Date.now() - 12000,
  website: "",
});
console.log("Unconfigured status (expected 503 when no API key, or 200 with key):", cUnconf.status, cUnconf.data);

process.env.CONTACT_DRY_RUN = "1";
const cGood = await callHandler(contactHandler, {
  name: "Ada Lovelace",
  email: "ada@analytical-engine.org",
  subject: "Game Development Collaboration",
  message: "Hi Ahmad, I explored your 3D WebGPU portfolio and loved Chrono Rebellion!",
  startedAt: Date.now() - 12000,
  website: "",
});
console.log("Dry-run valid payload status (expected 200):", cGood.status, cGood.data);
if (cBad.status !== 422 || cGood.status !== 200 || !q1.data.ok) {
  process.exit(1);
}
console.log("\n✅ All RAG & Contact API tests passed!");
