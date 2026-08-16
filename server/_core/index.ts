import "dotenv/config";
import express from "express";
import type { NextFunction, Request, Response } from "express";
import multer from "multer";
import crypto from "crypto";
import { storagePut } from "../storage";
import { createServer } from "http";
import net from "net";
import { createDjangoProxyHandler } from "./djangoProxy";
import { createExpressMiddleware } from "@trpc/server/adapters/express";
import { registerOAuthRoutes } from "./oauth";
import { registerStorageProxy } from "./storageProxy";
import { appRouter } from "../routers";
import { createContext } from "./context";
import { serveStatic, setupVite } from "./vite";

const proxyDjangoApi = createDjangoProxyHandler(process.env.DJANGO_API_URL || "http://127.0.0.1:8000/api");
const educationUpload = multer({
  storage: multer.memoryStorage(),
  limits: { fileSize: 10 * 1024 * 1024 },
  fileFilter: (_req, file, callback) => {
    const allowed = ["application/pdf", "image/jpeg", "image/png", "image/webp"].includes(file.mimetype);
    if (!allowed) {
      callback(new Error("Only PDF, JPG, PNG, or WebP files are accepted."));
      return;
    }
    callback(null, true);
  },
});

function isPortAvailable(port: number): Promise<boolean> {
  return new Promise(resolve => {
    const server = net.createServer();
    server.listen(port, () => {
      server.close(() => resolve(true));
    });
    server.on("error", () => resolve(false));
  });
}

async function findAvailablePort(startPort: number = 3000): Promise<number> {
  for (let port = startPort; port < startPort + 20; port++) {
    if (await isPortAvailable(port)) {
      return port;
    }
  }
  throw new Error(`No available port found starting from ${startPort}`);
}

async function startServer() {
  const app = express();
  const server = createServer(app);
  // Configure body parser with larger size limit for file uploads
  app.use(express.json({ limit: "50mb" }));
  app.use(express.urlencoded({ limit: "50mb", extended: true }));
  registerStorageProxy(app);
  registerOAuthRoutes(app);
  app.post("/api/uploads/education-document", educationUpload.single("file"), async (req, res) => {
    if (!req.file) {
      res.status(400).json({ detail: "Please attach a PDF or education-document photo." });
      return;
    }
    try {
      const safeName = req.file.originalname.replace(/[^a-zA-Z0-9._-]/g, "-").slice(-120) || "education-document";
      const stored = await storagePut(`education-documents/${crypto.randomUUID()}-${safeName}`, req.file.buffer, req.file.mimetype);
      res.status(201).json({ name: req.file.originalname, content_type: req.file.mimetype, size: req.file.size, ...stored });
    } catch (error) {
      console.error("[Education upload] Storage upload failed", error);
      res.status(503).json({ detail: "Document storage is temporarily unavailable. Please try again." });
    }
  });
  app.use("/api/uploads", (error: unknown, req: Request, res: Response, next: NextFunction) => {
    if (!error || !req.path) { next(error); return; }
    const message = error instanceof Error ? error.message : "The uploaded document could not be processed.";
    res.status(400).json({ detail: message });
  });
  // tRPC must be mounted before the broad Django proxy. Otherwise `/api/trpc/*`
  // is forwarded to Django and the client receives an HTML 404 page instead of JSON.
  app.use(
    "/api/trpc",
    createExpressMiddleware({
      router: appRouter,
      createContext,
    })
  );
  // Same-origin bridge for the Django REST API. This runs before Vite/static fallback
  // so remaining `/api/*` requests reach Django instead of the frontend HTML shell.
  app.use("/api", proxyDjangoApi);
  // development mode uses Vite, production mode uses static files
  if (process.env.NODE_ENV === "development") {
    await setupVite(app, server);
  } else {
    serveStatic(app);
  }

  const preferredPort = parseInt(process.env.PORT || "3000");
  const port = await findAvailablePort(preferredPort);

  if (port !== preferredPort) {
    console.log(`Port ${preferredPort} is busy, using port ${port} instead`);
  }

  server.listen(port, () => {
    console.log(`Server running on http://localhost:${port}/`);
  });
}

startServer().catch(console.error);
