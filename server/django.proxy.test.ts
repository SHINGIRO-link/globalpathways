import { afterEach, describe, expect, it, vi } from "vitest";
import { createDjangoProxyHandler } from "./_core/djangoProxy";

afterEach(() => vi.unstubAllGlobals());

describe("Django same-origin proxy", () => {
  it("forwards the REST path and relays JSON responses", async () => {
    const fetchMock = vi.fn().mockResolvedValue(new Response(JSON.stringify({ status: "ok" }), { status: 200, headers: { "content-type": "application/json" } }));
    vi.stubGlobal("fetch", fetchMock);
    const status = vi.fn().mockReturnThis();
    const setHeader = vi.fn().mockReturnThis();
    const send = vi.fn().mockReturnThis();
    const json = vi.fn().mockReturnThis();
    const handler = createDjangoProxyHandler("http://django.test/api/");

    await handler({ method: "GET", originalUrl: "/api/health/", headers: {} } as never, { status, setHeader, send, json } as never);

    expect(fetchMock).toHaveBeenCalledWith("http://django.test/api/health/", expect.objectContaining({ method: "GET" }));
    expect(status).toHaveBeenCalledWith(200);
    expect(send).toHaveBeenCalledWith(expect.any(Buffer));
    expect(json).not.toHaveBeenCalled();
  });

  it("returns a JSON 502 when Django is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const status = vi.fn().mockReturnThis();
    const setHeader = vi.fn().mockReturnThis();
    const send = vi.fn().mockReturnThis();
    const json = vi.fn().mockReturnThis();
    const handler = createDjangoProxyHandler("http://django.test/api");

    await handler({ method: "POST", originalUrl: "/api/applications/", headers: {}, body: {} } as never, { status, setHeader, send, json } as never);

    expect(status).toHaveBeenCalledWith(502);
    expect(json).toHaveBeenCalledWith({ detail: "The Django API is unavailable." });
  });
});
