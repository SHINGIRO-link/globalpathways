export function dashboardPath(role?: string | null) {
  if (role === "admin") return "/admin";
  if (role === "staff") return "/staff";
  return "/dashboard/end-user";
}
