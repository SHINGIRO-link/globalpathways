export type OpportunityCategory = "scholarship" | "visa" | "job";
export type OpportunityStatus = "open" | "coming";

export type Opportunity = {
  id: number;
  title: string;
  slug: string;
  category: OpportunityCategory;
  category_label: string;
  status: OpportunityStatus;
  status_label: string;
  country: string;
  region: string;
  deadline: string;
  summary: string;
  description: string;
  eligibility: string[];
  required_documents: string[];
  featured: boolean;
  deadline_note?: string;
  source_name?: string;
  source_url?: string;
  source_verified_at?: string;
};

import { additionalLocalOpportunities } from "./additionalOpportunities";

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

export function filterOpportunities(opportunities: Opportunity[], category: string, search: string): Opportunity[] {
  const query = search.trim().toLowerCase();
  return opportunities.filter(item => (category === "all" || item.category === category) && `${item.title} ${item.country} ${item.summary}`.toLowerCase().includes(query));
}

export class ServiceUnavailableError extends Error {
  readonly code = "SERVICE_UNAVAILABLE";
  constructor(message = "Service Unavailable: the service is temporarily unavailable. Please try again in a moment.") {
    super(message);
    this.name = "ServiceUnavailableError";
  }
}

const localOpportunities: Opportunity[] = [
  {
    id: 1,
    title: "Chevening Scholarship — 2027–2028",
    slug: "chevening-scholarship-2027-2028",
    category: "scholarship",
    category_label: "Scholarship",
    status: "open",
    status_label: "Open now",
    country: "United Kingdom",
    region: "Europe",
    deadline: "2026-10-06T11:00:00Z",
    summary: "Official UK government-backed scholarship route for future leaders applying for postgraduate study.",
    description: "Chevening supports one-year master's study in the UK and asks applicants to apply through their country or territory page.",
    eligibility: ["Bachelor's degree or equivalent", "Strong academic record", "Evidence of leadership or community impact"],
    required_documents: ["Passport or national ID", "Academic transcripts", "Statement of purpose", "One academic reference"],
    featured: true,
    deadline_note: "Official deadline: 6 October 2026 at 11:00 UTC.",
    source_name: "Chevening",
    source_url: "https://www.chevening.org/scholarships/application-timeline/",
    source_verified_at: "2026-08-16",
  },
  {
    id: 2,
    title: "MEXT Japanese Government Scholarship",
    slug: "mext-japanese-government-scholarship",
    category: "scholarship",
    category_label: "Scholarship",
    status: "open",
    status_label: "Open now",
    country: "Japan",
    region: "Asia",
    deadline: "2026-09-18T23:59:00Z",
    summary: "Official Japan scholarship route with embassy and university recommendation paths.",
    description: "Our advisors help you understand the required documents, timeline, financial evidence, and next steps for a Japan student visa application.",
    eligibility: ["Confirmed admission or application in progress", "Valid passport", "Proof of financial readiness"],
    required_documents: ["Passport", "Certificate of eligibility or school documents", "Financial evidence", "Accommodation plan"],
    featured: true,
    deadline_note: "Deadline varies by country embassy or university; check the official source.",
    source_name: "Study in Japan",
    source_url: "https://www.studyinjapan.go.jp/en/planning/scholarships/mext-scholarships/",
    source_verified_at: "2026-08-16",
  },
  {
    id: 3,
    title: "UN Human Rights Representative — P-5",
    slug: "un-human-rights-representative-bishkek-281339",
    category: "job",
    category_label: "Job opening",
    status: "open",
    status_label: "Open now",
    country: "Kyrgyzstan",
    region: "Asia",
    deadline: "2026-09-10T23:59:00Z",
    summary: "Official UN Careers vacancy with OHCHR in Bishkek, covering the Central Asia multi-country office.",
    description: "This P-5 role is listed on the official UN Careers portal and includes responsibilities for the OHCHR Central Asia multi-country office.",
    eligibility: ["P-5 level experience", "Human rights affairs expertise", "Required UN languages and qualifications"],
    required_documents: ["UN Careers profile", "CV", "Qualification evidence", "Role-specific documents"],
    featured: false,
    deadline_note: "Official UN Careers deadline: 10 September 2026.",
    source_name: "UN Careers",
    source_url: "https://careers.un.org/jobSearchDescription/281339",
    source_verified_at: "2026-08-16",
  },
  {
    id: 4,
    title: "EURES Europe Job Search",
    slug: "eures-europe-job-search",
    category: "job",
    category_label: "Job opening",
    status: "open",
    status_label: "Open now",
    country: "European Union",
    region: "Europe",
    deadline: "2026-12-31T23:59:00Z",
    summary: "Official European employment portal with live country and region job searches.",
    description: "EURES publishes changing vacancy listings and directs jobseekers to country and regional searches; always confirm the individual vacancy deadline on the official portal.",
    eligibility: ["Jobseeker eligible for the target vacancy", "Role-specific qualifications", "Work authorization or mobility readiness"],
    required_documents: ["CV", "Qualifications", "Work authorization details", "Role-specific documents"],
    featured: false,
    deadline_note: "Dynamic portal: individual vacancy deadlines vary; check the official source.",
    source_name: "EURES",
    source_url: "https://eures.europa.eu/index_en",
    source_verified_at: "2026-08-16",
  },
  {
    id: 5, title: "Erasmus Mundus Joint Masters", slug: "erasmus-mundus-joint-masters", category: "scholarship", category_label: "Scholarship", status: "open", status_label: "Open now", country: "European Union", region: "Europe", deadline: "2027-01-31T23:59:00Z", summary: "Official Erasmus+ scholarship catalogue for joint master's programmes across Europe and partner countries.", description: "Most Erasmus Mundus applications are submitted between October and January for programmes starting the following academic year; each programme publishes its own deadline.", eligibility: ["Relevant bachelor's degree", "Programme-specific eligibility", "International study readiness"], required_documents: ["Passport", "Academic transcripts", "Motivation statement", "Programme-specific documents"], featured: false, deadline_note: "Programme deadlines vary; official guidance says most applications fall between October and January.", source_name: "Erasmus+", source_url: "https://erasmus-plus.ec.europa.eu/opportunities/individuals/students/erasmus-mundus-joint-masters", source_verified_at: "2026-08-16",
  },
  {
    id: 6, title: "DAAD Scholarship Database", slug: "daad-scholarship-database", category: "scholarship", category_label: "Scholarship", status: "open", status_label: "Open now", country: "Germany", region: "Europe", deadline: "2027-03-31T23:59:00Z", summary: "Official DAAD database for scholarship opportunities and funding guidance for international students.", description: "DAAD programmes publish their own eligibility rules and deadlines. Use the official database to identify the exact programme before preparing an application.", eligibility: ["International student or graduate", "Programme-specific eligibility", "Academic preparation"], required_documents: ["Passport", "Academic records", "Programme-specific documents", "Motivation statement"], featured: false, deadline_note: "Deadlines vary by programme; check each official DAAD listing.", source_name: "DAAD", source_url: "https://www.daad.de/en/studying-in-germany/scholarships/", source_verified_at: "2026-08-16",
  },
  {
    id: 7, title: "EURAXESS Research Jobs", slug: "euraxess-research-jobs", category: "job", category_label: "Job opening", status: "open", status_label: "Open now", country: "Europe", region: "Europe", deadline: "2026-12-31T23:59:00Z", summary: "Official European research job and funding portal for international researchers and early-career talent.", description: "EURAXESS vacancies and funding calls are dynamic. Open the official portal to confirm each individual closing date and eligibility requirements.", eligibility: ["Research or technical profile", "Role-specific qualifications", "International mobility interest"], required_documents: ["CV", "Research profile", "Qualifications", "Role-specific documents"], featured: false, deadline_note: "Dynamic portal: individual vacancy deadlines vary; check the official source.", source_name: "EURAXESS", source_url: "https://euraxess.ec.europa.eu/jobs", source_verified_at: "2026-08-16",
  },
  {
    id: 8, title: "JET Programme — Japan Exchange and Teaching", slug: "jet-programme-japan", category: "job", category_label: "Job opening", status: "open", status_label: "Open now", country: "Japan", region: "Asia", deadline: "2026-12-01T23:59:00Z", summary: "Official Japan exchange and teaching route with country-specific application windows.", description: "The JET Programme states that application deadlines vary by country, with applications generally accepted from October to late November or early December.", eligibility: ["Country-specific JET eligibility", "Bachelor's degree or equivalent", "Strong communication skills"], required_documents: ["Application form", "Degree evidence", "Statement of purpose", "Country-specific documents"], featured: false, deadline_note: "Deadline varies by country; official guidance indicates October to late November or early December windows.", source_name: "JET Programme", source_url: "https://jetprogramme.org/en/aspiring/howto/", source_verified_at: "2026-08-16",
  },
  {
    id: 9, title: "JASSO Scholarships for International Students", slug: "jasso-scholarships-japan", category: "scholarship", category_label: "Scholarship", status: "open", status_label: "Open now", country: "Japan", region: "Asia", deadline: "2027-03-31T23:59:00Z", summary: "Official Japan Student Services Organization scholarship information for privately financed international students.", description: "JASSO scholarship arrangements and timing depend on the programme and institution. Check the official page for the current route and requirements.", eligibility: ["Privately financed international student", "Institution and programme-specific eligibility", "Academic preparation"], required_documents: ["Passport", "Academic records", "Admission documents", "Programme-specific forms"], featured: false, deadline_note: "Deadline varies by programme or institution; check the official source.", source_name: "Study in Japan / JASSO", source_url: "https://www.studyinjapan.go.jp/en/planning/scholarships/jasso-scholarships/", source_verified_at: "2026-08-16",
  },
  {
    id: 10, title: "Singapore Careers Portal", slug: "singapore-careers-portal", category: "job", category_label: "Job opening", status: "open", status_label: "Open now", country: "Singapore", region: "Asia", deadline: "2026-12-31T23:59:00Z", summary: "Official Singapore public-service careers portal for current roles and application guidance.", description: "Vacancies are published with role-specific closing dates. Open the official portal to confirm the current listing and deadline before applying.", eligibility: ["Role-specific eligibility", "Relevant qualifications", "Professional communication"], required_documents: ["CV", "Qualifications", "Role-specific documents"], featured: false, deadline_note: "Dynamic portal: individual vacancy deadlines vary; check the official source.", source_name: "Careers@Gov", source_url: "https://www.careers.gov.sg/", source_verified_at: "2026-08-16",
  },
  ...additionalLocalOpportunities,
];

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  } catch (error) {
    const detail = error instanceof Error ? ` (${error.message})` : "";
    throw new ServiceUnavailableError(`Service Unavailable: the service is temporarily unavailable${detail}.`);
  }
  const contentType = response.headers?.get?.("content-type") || "application/json";
  const payload = contentType.includes("application/json") ? await response.json().catch(() => ({})) : {};
  if (!response.ok || !contentType.includes("application/json")) {
    if (response.status >= 500 || !contentType.includes("application/json")) throw new ServiceUnavailableError();
    const detail = typeof payload?.detail === "string" ? payload.detail : "Please review the highlighted information and try again.";
    throw new Error(detail);
  }
  return payload as T;
}

export type EducationDocumentCategory = "certificate" | "passport" | "transcript" | "cv" | "supporting";
export type UploadedEducationDocument = { name: string; content_type: string; size: number; key: string; url: string; category: EducationDocumentCategory };

export async function uploadEducationDocument(file: File, category: EducationDocumentCategory = "certificate"): Promise<UploadedEducationDocument> {
  const body = new FormData();
  body.append("file", file);
  body.append("category", category);
  let response: Response;
  try {
    response = await fetch(`${API_BASE}/uploads/education-document`, { method: "POST", body });
  } catch {
    throw new ServiceUnavailableError("Document upload is unavailable right now. Please try again.");
  }
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    if (response.status >= 500) throw new ServiceUnavailableError(payload.detail || "Document storage is temporarily unavailable. Please try again.");
    throw new Error(payload.detail || "We could not upload that document. Please try again.");
  }
  return payload as UploadedEducationDocument;
}

export async function getOpportunities(options: { fallback?: boolean } = {}): Promise<Opportunity[]> {
  try {
    return await request<Opportunity[]>("/opportunities/");
  } catch (error) {
    if (options.fallback) return localOpportunities;
    throw error;
  }
}

export async function getOpportunity(slug: string): Promise<Opportunity> {
  try {
    return await request<Opportunity>(`/opportunities/${slug}/`);
  } catch {
    const match = localOpportunities.find((item) => item.slug === slug);
    if (!match) throw new Error("Opportunity not found.");
    return match;
  }
}

export async function submitApplication(payload: Record<string, unknown>) {
  return request<{ id: number }>("/applications/", { method: "POST", body: JSON.stringify(payload) });
}

export async function submitInquiry(payload: Record<string, unknown>) {
  return request<{ id: number }>("/inquiries/", { method: "POST", body: JSON.stringify(payload) });
}

export async function getSuccessStories() {
  try {
    return await request<Array<{ id: number; name: string; destination: string; quote: string }>>("/success-stories/");
  } catch {
    return [];
  }
}


export type ApplicationStatus = "payment_required" | "received" | "reviewing" | "needs_info" | "approved" | "rejected";
export type DashboardApplication = {
  id: number;
  opportunity: number;
  opportunity_title: string;
  status: ApplicationStatus;
  status_label: string;
  created_at: string;
  updated_at: string;
};
export type DashboardData = {
  email: string;
  applications: DashboardApplication[];
  saved_opportunities: Array<{ id: number; opportunity: number; opportunity_detail: Opportunity; created_at: string }>;
};

const dashboardHeaders = (email: string) => ({ "X-Dashboard-Email": email });

export async function getDashboard(email: string): Promise<DashboardData> {
  return request<DashboardData>(`/dashboard/?email=${encodeURIComponent(email)}`, { headers: { "Content-Type": "application/json", ...dashboardHeaders(email) } });
}

export async function saveOpportunity(email: string, opportunity: number) {
  return request(`/saved-opportunities/`, { method: "POST", headers: { "Content-Type": "application/json", ...dashboardHeaders(email) }, body: JSON.stringify({ email, opportunity }) });
}

export async function removeSavedOpportunity(email: string, opportunity: number) {
  return request(`/saved-opportunities/${opportunity}/?email=${encodeURIComponent(email)}`, { method: "DELETE", headers: { "Content-Type": "application/json", ...dashboardHeaders(email) } });
}

export async function getApplicationStatus(email: string, applicationId: number) {
  return request<{ application: DashboardApplication; events: Array<{ id: number; status: ApplicationStatus; status_label: string; note: string; created_at: string }>; payment: { amount: number; currency: string; provider: string; status: string; status_label: string } | null }>(`/applications/${applicationId}/status/?email=${encodeURIComponent(email)}`, { headers: { "Content-Type": "application/json", ...dashboardHeaders(email) } });
}

export async function preparePayment(email: string, application: number, provider: "momo" | "airtel") {
  return request<{ payment: { amount: number; currency: string; provider: string; status: string }; message: string }>("/payments/prepare/", { method: "POST", headers: { "Content-Type": "application/json", ...dashboardHeaders(email) }, body: JSON.stringify({ email, application, provider }) });
}


export type StaffNotification = {
  id: number;
  event_type: string;
  event_type_label: string;
  title: string;
  message: string;
  application: number | null;
  application_name?: string;
  is_read: boolean;
  created_at: string;
};

export async function getStaffNotifications(filters: { read?: "all" | "unread" | "read"; event_type?: string } = {}) {
  const params = new URLSearchParams();
  if (filters.read && filters.read !== "all") params.set("read", filters.read);
  if (filters.event_type && filters.event_type !== "all") params.set("event_type", filters.event_type);
  return request<{ unread_count: number; notifications: StaffNotification[] }>(`/staff/notifications/${params.toString() ? `?${params.toString()}` : ""}`);
}

export async function markStaffNotificationRead(id: number, is_read = true) {
  return request<StaffNotification>(`/staff/notifications/${id}/`, { method: "PATCH", body: JSON.stringify({ is_read }) });
}

export async function markAllStaffNotificationsRead() {
  return request<{ updated: number; unread_count: number }>("/staff/notifications/mark-all-read/", { method: "POST" });
}

export async function archiveStaffNotification(id: number) {
  return request<{ deleted: boolean }>(`/staff/notifications/${id}/`, { method: "DELETE" });
}


export type StaffPayment = {
  id: number;
  application: number;
  amount: number;
  currency: string;
  provider: string;
  provider_label: string;
  status: string;
  status_label: string;
  provider_reference: string;
  created_at: string;
  updated_at: string;
};

export type StaffDocument = {
  index: number;
  name: string;
  category: string;
  content_type: string;
  size: number;
  download_url: string;
};

export type StaffApplication = {
  id: number;
  full_name: string;
  email: string;
  phone: string;
  nationality: string;
  current_location: string;
  education_level: string;
  statement: string;
  opportunity: number;
  opportunity_title: string;
  status: ApplicationStatus;
  status_label: string;
  consent_to_contact: boolean;
  created_at: string;
  updated_at: string;
  documents: StaffDocument[];
  payment: StaffPayment | null;
};

export type StaffApplicationFilters = { q?: string; status?: string; payment_status?: string };
export type StaffApplicationsResponse = {
  summary: { applications: number; payments: number; pending_payments: number; unread_notifications: number };
  applications: StaffApplication[];
  statuses: Array<{ value: string; label: string }>;
  payment_statuses: Array<{ value: string; label: string }>;
};

export async function getStaffApplications(filters: StaffApplicationFilters = {}) {
  const params = new URLSearchParams();
  if (filters.q) params.set("q", filters.q);
  if (filters.status) params.set("status", filters.status);
  if (filters.payment_status) params.set("payment_status", filters.payment_status);
  return request<StaffApplicationsResponse>(`/staff/applications/${params.toString() ? `?${params.toString()}` : ""}`);
}

export async function updateStaffApplicationStatus(applicationId: number, nextStatus: string, note = "") {
  return request<StaffApplication>(`/staff/applications/${applicationId}/status/`, { method: "PATCH", body: JSON.stringify({ status: nextStatus, note }) });
}

export async function updateStaffPaymentStatus(paymentId: number, nextStatus: string, providerReference = "") {
  return request<StaffApplication>(`/staff/payments/${paymentId}/status/`, { method: "PATCH", body: JSON.stringify({ status: nextStatus, provider_reference: providerReference }) });
}

export function getStaffApplicationsExportUrl() { return `${API_BASE}/staff/applications/export/`; }
