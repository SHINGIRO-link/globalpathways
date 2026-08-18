import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const authClient = readFileSync("client/src/lib/auth.ts", "utf8");
const authRoutes = readFileSync("client/src/App.tsx", "utf8");
const loginEntry = readFileSync("client/src/const.ts", "utf8");
const djangoUrls = readFileSync("backend/opportunities/urls.py", "utf8");


describe("first-party authentication wiring", () => {
  it("uses same-origin Django session endpoints instead of Manus redirect login", () => {
    expect(loginEntry).toContain('window.location.href = "/sign-in"');
    expect(loginEntry).not.toContain("manus.im/app-auth");
    expect(authClient).toContain("/auth/login/");
    expect(authClient).toContain("credentials: \"include\"");
    expect(authClient).toContain("X-CSRFToken");
  });

  it("registers sign-in, account creation, recovery, and reset routes", () => {
    expect(authRoutes).toContain('path="/sign-in"');
    expect(authRoutes).toContain('path="/create-account"');
    expect(authRoutes).toContain('path="/forgot-password"');
    expect(authRoutes).toContain('path="/reset-password"');
  });

  it("exposes Django endpoints for session and password recovery", () => {
    expect(djangoUrls).toContain('path("auth/me/"');
    expect(djangoUrls).toContain('path("auth/register/"');
    expect(djangoUrls).toContain('path("auth/login/"');
    expect(djangoUrls).toContain('path("auth/logout/"');
    expect(djangoUrls).toContain('path("auth/password-reset/"');
    expect(djangoUrls).toContain('path("auth/password-reset/confirm/"');
  });
});
