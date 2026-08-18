export type LocalUser = {
  id: number;
  openId: string;
  name: string;
  email: string;
  loginMethod: "email";
  role: "user" | "staff" | "admin";
};

const API_BASE = import.meta.env.VITE_API_BASE_URL || "/api";

function csrfToken() {
  return document.cookie
    .split(";")
    .map((part) => part.trim())
    .find((part) => part.startsWith("csrftoken="))
    ?.slice("csrftoken=".length) || "";
}

async function ensureCsrf() {
  await fetch(`${API_BASE}/auth/csrf/`, { credentials: "include" });
}

async function request<T>(path: string, body?: Record<string, unknown>): Promise<T> {
  if (body) await ensureCsrf();
  const response = await fetch(`${API_BASE}${path}`, {
    method: body ? "POST" : "GET",
    credentials: "include",
    headers: body ? { "Content-Type": "application/json", "X-CSRFToken": csrfToken() } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "We could not complete that request.");
  return payload as T;
}

export async function getCurrentUser() {
  const payload = await request<{ user: LocalUser | null }>("/auth/me/");
  return payload.user;
}

export async function registerAccount(name: string, email: string, password: string) {
  return request<{ user: LocalUser }>("/auth/register/", { name, email, password });
}

export async function loginAccount(email: string, password: string) {
  return request<{ user: LocalUser }>("/auth/login/", { email, password });
}

export async function logoutAccount() {
  return request<{ loggedOut: boolean }>("/auth/logout/", {});
}

export async function requestPasswordReset(email: string) {
  return request<{ detail: string }>("/auth/password-reset/", { email });
}

export async function confirmPasswordReset(uid: string, token: string, password: string) {
  return request<{ user: LocalUser }>("/auth/password-reset/confirm/", { uid, token, password });
}

export function notifyAuthChanged() {
  window.dispatchEvent(new Event("globalpathways-auth-changed"));
}
