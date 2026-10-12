export type AccountRole = "user" | "staff" | "admin";

export const ROLE_LABELS: Record<AccountRole, string> = { user: "Applicant", staff: "Staff", admin: "Admin" };

export function roleLabel(role?: string | null) {
  return ROLE_LABELS[(role as AccountRole) || "user"] || "Applicant";
}

export function dashboardPath(role?: string | null) {
  if (role === "admin") return "/admin";
  if (role === "staff") return "/staff";
  return "/dashboard/end-user";
}

export function dashboardLabel(role?: string | null) {
  if (role === "admin") return "Admin dashboard";
  if (role === "staff") return "Staff dashboard";
  return "My dashboard";
}
