import { afterEach, describe, expect, it, vi } from "vitest";
import { getOpportunities, getOpportunity } from "./api";

afterEach(() => vi.unstubAllGlobals());

describe("Django REST client", () => {
  it("uses the API response when the opportunity endpoint is available", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => [{ id: 10, title: "API opportunity" }] }));
    const result = await getOpportunities();
    expect(result).toEqual([{ id: 10, title: "API opportunity" }]);
    expect(fetch).toHaveBeenCalledWith("/api/opportunities/", expect.objectContaining({ headers: { "Content-Type": "application/json" } }));
  });

  it("keeps the discovery experience useful when the API is temporarily unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const result = await getOpportunity("global-excellence-scholarship");
    expect(result.category).toBe("scholarship");
    expect(result.status).toBe("open");
  });
});
