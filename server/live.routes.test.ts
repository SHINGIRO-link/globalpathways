import { describe, expect, it } from "vitest";

describe("live API route separation", () => {
  it("returns JSON from tRPC and Django REST routes", async () => {
    const trpcResponse = await fetch("http://127.0.0.1:3000/api/trpc/auth.me?batch=1&input=%7B%7D");
    expect(trpcResponse.headers.get("content-type")).toContain("application/json");
    const trpcBody = await trpcResponse.json();
    expect(trpcBody[0]?.result?.data?.json).toBeNull();

    const djangoResponse = await fetch("http://127.0.0.1:3000/api/health/");
    expect(djangoResponse.headers.get("content-type")).toContain("application/json");
    const djangoBody = await djangoResponse.json();
    expect(djangoBody.service).toBe("globalpathways-django-api");
  }, 15_000);
});
