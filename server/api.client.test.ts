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
    const result = await getOpportunity("chevening-scholarship-2027-2028");
    expect(result.category).toBe("scholarship");
    expect(result.status).toBe("open");
  });

  it("keeps verified fallback metadata visible when the Django API is unavailable", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new Error("offline")));
    const un = await getOpportunity("un-human-rights-representative-bishkek-281339");
    const eures = await getOpportunity("eures-europe-job-search");
    expect(un.source_url).toBe("https://careers.un.org/jobSearchDescription/281339");
    expect(un.status).toBe("open");
    expect(un.deadline_note).toContain("10 September 2026");
    expect(eures.source_url).toBe("https://eures.europa.eu/index_en");
    expect(eures.deadline_note).toContain("Dynamic portal");
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
