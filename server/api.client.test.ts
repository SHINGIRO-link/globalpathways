import { afterEach, describe, expect, it, vi } from "vitest";
import { getDashboard, getOpportunity, getOpportunities } from "../client/src/lib/api";

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

  it("surfaces strict list failures for the directory error state", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    await expect(getOpportunities()).rejects.toThrow("offline");
  });

  it("loads a personalized dashboard by signed-in email", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ email: "amina@example.com", applications: [], saved_opportunities: [] }) }));
    const result = await getDashboard("amina@example.com");
    expect(result.email).toBe("amina@example.com");
    expect(fetch).toHaveBeenCalledWith("/api/dashboard/?email=amina%40example.com", expect.objectContaining({ headers: { "Content-Type": "application/json", "X-Dashboard-Email": "amina@example.com" } }));
  });
});
