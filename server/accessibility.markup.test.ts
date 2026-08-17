import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const homeSource = readFileSync(resolve(process.cwd(), "client/src/pages/Home.tsx"), "utf8");
const dashboardSource = readFileSync(resolve(process.cwd(), "client/src/pages/Dashboard.tsx"), "utf8");
const staffSource = readFileSync(resolve(process.cwd(), "client/src/pages/StaffNotifications.tsx"), "utf8");
const staffApplicationsSource = readFileSync(resolve(process.cwd(), "client/src/pages/StaffApplications.tsx"), "utf8");
const appSource = readFileSync(resolve(process.cwd(), "client/src/App.tsx"), "utf8");

describe("interactive card markup", () => {
  it("keeps opportunity actions outside the card navigation link", () => {
    const opportunityCard = homeSource.slice(homeSource.indexOf("function OpportunityCard"), homeSource.indexOf("function InquiryDialog"));
    const linkEnd = opportunityCard.indexOf("</Link>");
    expect(linkEnd).toBeGreaterThan(0);
    expect(opportunityCard.slice(0, linkEnd)).not.toContain("<button");
    expect(opportunityCard.slice(linkEnd)).toContain("source-link");
    expect(opportunityCard.slice(linkEnd)).toContain("save-opportunity");
  });

  it("keeps dashboard saved-route actions as sibling controls", () => {
    const savedCard = dashboardSource.slice(dashboardSource.indexOf("saved-card"), dashboardSource.indexOf("}</div>)}</div>}</section>"));
    expect(savedCard).toContain("saved-card-link");
    expect(savedCard).toContain("unsave-button");
  });

  it("gives staff notification icon actions explicit accessible labels", () => {
    expect(staffSource).toContain("aria-label={notification.is_read ? `Mark ${notification.title} unread` : `Mark ${notification.title} read`}");
    expect(staffSource).toContain("aria-label={`Archive ${notification.title}`}");
  });

  it("registers and protects the staff applications workspace", () => {
    expect(appSource).toContain('const StaffApplications = lazy(() => import("@/pages/StaffApplications"));');
    expect(appSource).toContain('<Route path="/staff/applications" component={StaffApplications} />');
    expect(staffApplicationsSource).toContain("user.role !== \"admin\"");
    expect(staffApplicationsSource).toContain("Download CSV");
    expect(staffApplicationsSource).toContain("Download all documents");
    expect(staffApplicationsSource).toContain("getStaffDocumentsExportUrl");
    expect(staffApplicationsSource).toContain("Documents");
    expect(staffSource).toContain('href="/staff/applications"');
  });

  it("routes the footer Policies links to the dedicated policies page", () => {
    expect(homeSource).toContain('<Link href="/policies" className="footer-promise-link">');
    expect(homeSource).toContain('<Link href="/policies" className="footer-read-more">');
    expect(homeSource).toContain('location === "/applicant-responsibility" || location === "/policies"');
  });

  it("resets the viewport on route changes and syncs category links", () => {
    expect(homeSource).toContain('window.scrollTo({ top: 0, left: 0, behavior: "auto" })');
    expect(homeSource).toContain('href="/opportunities?category=scholarship"');
    expect(homeSource).toContain('href="/opportunities?category=job"');
    expect(homeSource).toContain("setCategory(queryCategory)");
  });

  it("keeps the public apply form aligned with the API and success state", () => {
    const applySource = homeSource.slice(homeSource.indexOf("function Apply"), homeSource.indexOf("export default function Home"));
    expect(applySource).not.toContain("Please sign in before submitting");
    expect(applySource).toContain("const result = await submitApplication");
    expect(applySource).toContain("setApplicationId(result.id); setSent(true)");
    expect(applySource).toContain("Application received");
  });
});
