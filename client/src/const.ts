export { COOKIE_NAME, ONE_YEAR_MS } from "@shared/const";

// First-party authentication lives on the same Django host as the application.
// Keep this as an event-handler action so callers never navigate during render.
export const startLogin = () => {
  try { sessionStorage.setItem("globalpathways-post-login", "1"); } catch {}
  window.location.href = "/sign-in";
};
