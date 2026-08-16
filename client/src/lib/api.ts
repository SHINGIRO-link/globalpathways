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
