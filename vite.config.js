import { defineConfig } from "vite";
import basicSsl from "@vitejs/plugin-basic-ssl";
import { readFileSync, existsSync } from "node:fs";
import { resolve, dirname, extname } from "node:path";
import { fileURLToPath } from "node:url";

const rootDir = dirname(fileURLToPath(import.meta.url));
try {
  process.loadEnvFile?.(resolve(rootDir, ".env"));
} catch {
  /* .env optional in local dev */
}
const inspectorExtensionsDir = resolve(
  rootDir,
  "node_modules/three/examples/jsm/inspector/extensions",
);

const MIME_TYPES = {
  ".json": "application/json",
  ".js": "text/javascript",
  ".css": "text/css",
  ".html": "text/html",
  ".svg": "image/svg+xml",
};

function serveInspectorExtensions() {
  const urlPrefix = "/node_modules/.vite/extensions/";

  return (req, res, next) => {
    if (!req.url?.startsWith(urlPrefix)) {
      next();
      return;
    }

    const relativePath = req.url.slice(urlPrefix.length).split("?")[0];
    const filePath = resolve(inspectorExtensionsDir, relativePath);

    if (
      !filePath.startsWith(inspectorExtensionsDir) ||
      !existsSync(filePath)
    ) {
      next();
      return;
    }

    const ext = extname(filePath);
    res.setHeader("Content-Type", MIME_TYPES[ext] ?? "application/octet-stream");
    res.end(readFileSync(filePath));
  };
}

function serveLocalApiRoutes() {
  return async (req, res, next) => {
    const pathname = req.url?.split("?")[0];
    if (pathname === "/api/chat") {
      const { default: handler } = await import("./api/chat.js");
      await handler(req, res);
      return;
    }
    if (pathname === "/api/contact") {
      const { default: handler } = await import("./api/contact.js");
      await handler(req, res);
      return;
    }
    next();
  };
}

const useHttps = process.env.VITE_HTTPS === "1" || process.env.VITE_HTTPS === "true";

export default defineConfig({
  server: {
    host: true,
    open: true,
  },
  build: {
    target: "es2022",
    cssMinify: true,
    chunkSizeWarningLimit: 1600,
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes("node_modules/three-mesh-bvh")) {
            return "vendor-bvh";
          }
          if (id.includes("node_modules/three")) {
            return "vendor-three";
          }
          if (id.includes("node_modules/gsap")) {
            return "vendor-gsap";
          }
        },
      },
    },
  },
  plugins: [
    ...(useHttps ? [basicSsl()] : []),
    {
      name: "local-serverless-api",
      configureServer(server) {
        server.middlewares.use(serveLocalApiRoutes());
      },
      configurePreviewServer(server) {
        server.middlewares.use(serveLocalApiRoutes());
      },
    },
    {
      name: "three-inspector-extensions",
      configureServer(server) {
        server.middlewares.use(serveInspectorExtensions());
      },
      configurePreviewServer(server) {
        server.middlewares.use(serveInspectorExtensions());
      },
    },
  ],
});
