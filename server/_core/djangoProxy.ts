import type { Request, Response } from "express";
import { sdk } from "./sdk";

export function createDjangoProxyHandler(baseUrl: string) {
  const djangoApiBase = baseUrl.replace(/\/$/, "");
  return async function proxyDjangoApi(req: Request, res: Response) {
    const targetUrl = `${djangoApiBase}${req.originalUrl.slice("/api".length)}`;
    const headers = new Headers();
    for (const [key, value] of Object.entries(req.headers)) {
      if (["host", "content-length", "connection", "x-authenticated-role", "x-authenticated-open-id"].includes(key)) continue;
      if (typeof value === "string") headers.set(key, value);
      else if (Array.isArray(value)) headers.set(key, value.join(", "));
    }
    try {
      const authenticatedUser = await sdk.authenticateRequest(req as any);
      headers.set("X-Authenticated-Role", authenticatedUser.role);
      headers.set("X-Authenticated-Open-Id", authenticatedUser.openId);
    } catch {
      // Django remains responsible for rejecting unauthenticated requests.
    }

    const body = ["GET", "HEAD"].includes(req.method) ? undefined : JSON.stringify(req.body ?? {});
    try {
      const upstream = await fetch(targetUrl, { method: req.method, headers, body, redirect: "manual" });
      res.status(upstream.status);
      upstream.headers.forEach((value, key) => {
        if (!["content-encoding", "transfer-encoding", "connection"].includes(key)) res.setHeader(key, value);
      });
      res.send(Buffer.from(await upstream.arrayBuffer()));
    } catch (error) {
      console.error(`[Django proxy] ${req.method} ${targetUrl} failed`, error);
      res.status(502).json({ detail: "The Django API is unavailable." });
    }
  };
}
