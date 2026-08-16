import { describe, expect, it } from "vitest";

describe("SMTP configuration", () => {
  it("loads the configured Gmail sender without exposing the password", () => {
    expect(process.env.SMTP_HOST).toBe("smtp.gmail.com");
    expect(process.env.SMTP_PORT).toBe("587");
    expect(process.env.SMTP_USER).toBe("globalopportunityconnect@gmail.com");
    expect(process.env.SMTP_FROM).toBe("globalopportunityconnect@gmail.com");
    expect(process.env.SMTP_STAFF_RECIPIENT).toBe("globalopportunityconnect@gmail.com");
    expect(process.env.SMTP_PASSWORD).toBeTruthy();
  });
});
