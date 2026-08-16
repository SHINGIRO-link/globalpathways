import type { Request, Response } from "express";

export function createDjangoProxyHandler(baseUrl: string) {
  const djangoApiBase = baseUrl.replace(/\/$/, "");
  return async function proxyDjangoApi(req: Request, res: Response) {
    const targetUrl = `${djangoApiBase}${req.originalUrl.slice("/api".length)}`;
    const headers = new Headers();
    for (const [key, value] of Object.entries(req.headers)) {
      if (["host", "content-length", "connection"].includes(key)) continue;
      if (typeof value === "string") headers.set(key, value);
      else if (Array.isArray(value)) headers.set(key, value.join(", "));
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
