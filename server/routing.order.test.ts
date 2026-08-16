import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

describe("API route ordering", () => {
  it("mounts tRPC before the broad Django API proxy", () => {
    const source = readFileSync(resolve(process.cwd(), "server/_core/index.ts"), "utf8");
    const trpcMount = source.indexOf('app.use(\n    "/api/trpc"');
    const djangoProxy = source.indexOf('app.use("/api", proxyDjangoApi)');
    expect(trpcMount).toBeGreaterThan(-1);
    expect(djangoProxy).toBeGreaterThan(-1);
    expect(trpcMount).toBeLessThan(djangoProxy);
  });
});
