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
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

const localOpportunities: Opportunity[] = [
  {
    id: 1,
    title: "Global Excellence Scholarship",
    slug: "global-excellence-scholarship",
    category: "scholarship",
    category_label: "Scholarship",
    status: "open",
    status_label: "Open now",
    country: "Netherlands",
    region: "Europe",
    deadline: "2026-10-28T23:59:00Z",
    summary: "A merit-based award for ambitious international students building the next generation of ideas.",
    description: "The Global Excellence Scholarship supports high-potential students pursuing a full-time master's degree in an international learning environment.",
    eligibility: ["Bachelor's degree or equivalent", "Strong academic record", "Evidence of leadership or community impact"],
    required_documents: ["Passport or national ID", "Academic transcripts", "Statement of purpose", "One academic reference"],
    featured: true,
  },
  {
    id: 2,
    title: "Japan Student Visa Guidance",
    slug: "japan-student-visa-guidance",
    category: "visa",
    category_label: "Student visa",
    status: "open",
    status_label: "Open now",
    country: "Japan",
    region: "Asia",
    deadline: "2026-09-18T23:59:00Z",
    summary: "Step-by-step support for preparing a confident student visa application for Japan.",
    description: "Our advisors help you understand the required documents, timeline, financial evidence, and next steps for a Japan student visa application.",
    eligibility: ["Confirmed admission or application in progress", "Valid passport", "Proof of financial readiness"],
    required_documents: ["Passport", "Certificate of eligibility or school documents", "Financial evidence", "Accommodation plan"],
    featured: true,
  },
  {
    id: 3,
    title: "Nordic Graduate Talent Route",
    slug: "nordic-graduate-talent-route",
    category: "job",
    category_label: "Job opening",
    status: "coming",
    status_label: "Coming soon",
    country: "Sweden",
    region: "Europe",
    deadline: "2026-12-02T23:59:00Z",
    summary: "A curated route for early-career talent exploring graduate roles with global teams.",
    description: "This upcoming opportunity route will connect eligible graduates with selected employers and practical relocation guidance.",
    eligibility: ["Recent graduate or final-year student", "Relevant portfolio or experience", "Professional English"],
    required_documents: ["CV", "Portfolio or work samples", "Degree certificate or expected graduation letter"],
    featured: false,
  },
  {
    id: 4,
    title: "South Korea Study Pathway",
    slug: "south-korea-study-pathway",
    category: "visa",
    category_label: "Student visa",
    status: "coming",
    status_label: "Coming soon",
    country: "South Korea",
    region: "Asia",
    deadline: "2027-01-14T23:59:00Z",
    summary: "Prepare early for a focused study pathway in one of Asia's most dynamic education hubs.",
    description: "Join the early interest list for upcoming South Korea study and visa support, including document preparation and timeline planning.",
    eligibility: ["Planning to study in South Korea", "Academic profile aligned with the target institution", "Willingness to prepare early"],
    required_documents: ["Passport", "Academic records", "Personal statement", "Financial plan"],
    featured: false,
  },
  {
    id: 5, title: "France Campus Scholarship Route", slug: "france-campus-scholarship-route", category: "scholarship", category_label: "Scholarship", status: "open", status_label: "Open now", country: "France", region: "Europe", deadline: "2026-11-20T23:59:00Z", summary: "Editorial route preview for students preparing a competitive postgraduate application in France.", description: "A planning-led scholarship route preview focused on programme research, statement preparation, and a clear application calendar.", eligibility: ["Relevant undergraduate background", "Strong academic record", "Clear study plan"], required_documents: ["Passport", "Academic transcripts", "Statement of purpose", "Reference letter"], featured: false,
  },
  {
    id: 6, title: "Germany Study Preparation Route", slug: "germany-study-preparation-route", category: "visa", category_label: "Student visa", status: "open", status_label: "Open now", country: "Germany", region: "Europe", deadline: "2026-10-16T23:59:00Z", summary: "A practical route preview for students planning study, financial evidence, and visa preparation in Germany.", description: "Build an informed Germany study plan with a structured document checklist and timeline for the next stage of your application.", eligibility: ["Offer or active programme search", "Valid passport", "Evidence of financial planning"], required_documents: ["Passport", "Admission documents", "Financial evidence", "Accommodation plan"], featured: false,
  },
  {
    id: 7, title: "Ireland Graduate Roles Route", slug: "ireland-graduate-roles-route", category: "job", category_label: "Job opening", status: "coming", status_label: "Coming soon", country: "Ireland", region: "Europe", deadline: "2027-01-30T23:59:00Z", summary: "A future-facing route preview for graduates exploring international roles with growing teams in Ireland.", description: "Join the early list for practical guidance on CV positioning, employer research, and relocation planning.", eligibility: ["Final-year student or recent graduate", "Relevant portfolio", "Professional communication skills"], required_documents: ["CV", "Portfolio", "Degree or expected graduation letter"], featured: false,
  },
  {
    id: 8, title: "Malaysia Student Visa Route", slug: "malaysia-student-visa-route", category: "visa", category_label: "Student visa", status: "open", status_label: "Open now", country: "Malaysia", region: "Asia", deadline: "2026-11-08T23:59:00Z", summary: "A clear preparation route preview for students considering Malaysia as their next study destination.", description: "Understand the core preparation steps, documents, and timeline before moving forward with a Malaysia study application.", eligibility: ["Study plan aligned with a recognised institution", "Valid passport", "Financial readiness"], required_documents: ["Passport", "Admission or application evidence", "Academic records", "Financial plan"], featured: false,
  },
  {
    id: 9, title: "Taiwan Research Scholarship Route", slug: "taiwan-research-scholarship-route", category: "scholarship", category_label: "Scholarship", status: "coming", status_label: "Coming soon", country: "Taiwan", region: "Asia", deadline: "2027-02-12T23:59:00Z", summary: "An upcoming route preview for research-minded students preparing an international academic profile.", description: "Prepare early with guidance on research fit, academic evidence, and a compelling statement of purpose.", eligibility: ["Research or postgraduate interest", "Relevant academic preparation", "Clear academic goals"], required_documents: ["Passport", "Transcripts", "Research statement", "Academic reference"], featured: false,
  },
  {
    id: 10, title: "Singapore Early-Career Roles Route", slug: "singapore-early-career-roles-route", category: "job", category_label: "Job opening", status: "coming", status_label: "Coming soon", country: "Singapore", region: "Asia", deadline: "2027-03-05T23:59:00Z", summary: "An upcoming route preview for early-career talent building a focused international job search.", description: "Join the early list for support with role research, application positioning, and practical relocation questions.", eligibility: ["Recent graduate or early-career professional", "Relevant skills or portfolio", "Professional English"], required_documents: ["CV", "Portfolio or work samples", "Qualification evidence"], featured: false,
  },
];

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, { headers: { "Content-Type": "application/json" }, ...options });
  if (!response.ok) throw new Error("The service is temporarily unavailable.");
  return response.json() as Promise<T>;
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
