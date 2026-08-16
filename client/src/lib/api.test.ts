import { afterEach, describe, expect, it, vi } from "vitest";
import { getOpportunities, getOpportunity, submitApplication, uploadEducationDocument } from "./api";

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

  it("submits applications through the same-origin Django API", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ id: 42 }) }));
    const payload = { opportunity: 10, full_name: "Amina Test", email: "amina@example.com", statement: "Ready to move.", consent_to_contact: true, document_links: [] };
    await expect(submitApplication(payload)).resolves.toEqual({ id: 42 });
    expect(fetch).toHaveBeenCalledWith("/api/applications/", expect.objectContaining({ method: "POST", body: JSON.stringify(payload) }));
  });

  it("surfaces a controlled error when application submission is rejected", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: false, json: async () => ({ detail: "Invalid application" }) }));
    await expect(submitApplication({ opportunity: 10 })).rejects.toThrow("temporarily unavailable");
  });

  it("uploads an education certificate through the storage-backed endpoint", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({ ok: true, json: async () => ({ name: "diploma.pdf", content_type: "application/pdf", size: 12, key: "education-documents/diploma.pdf", url: "/manus-storage/education-documents/diploma.pdf" }) }));
    const result = await uploadEducationDocument(new File(["certificate"], "diploma.pdf", { type: "application/pdf" }));
    expect(result.url).toContain("/manus-storage/");
    expect(fetch).toHaveBeenCalledWith("/api/uploads/education-document", expect.objectContaining({ method: "POST", body: expect.any(FormData) }));
  });
});
