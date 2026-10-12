// Forwards backend paths to the Django service on Render so the browser only
// ever talks to one origin (keeps session/CSRF cookies first-party).
// Static assets and SPA routes are served by Cloudflare assets (see wrangler.jsonc run_worker_first).
interface Env {
  BACKEND_ORIGIN: string;
}

const HOP_BY_HOP = ["host", "cf-connecting-ip", "cf-ray", "cf-visitor", "x-forwarded-host"];

export default {
  async fetch(request: Request, env: Env): Promise<Response> {
    const incoming = new URL(request.url);
    const target = new URL(incoming.pathname + incoming.search, env.BACKEND_ORIGIN);

    const headers = new Headers(request.headers);
    for (const name of HOP_BY_HOP) headers.delete(name);
    headers.set("X-Forwarded-Host", incoming.host);
    headers.set("X-Forwarded-Proto", "https");

    const upstream = await fetch(target, {
      method: request.method,
      headers,
      body: ["GET", "HEAD"].includes(request.method) ? undefined : request.body,
      redirect: "manual",
    });

    // Redirects from Django must stay on this origin.
    const response = new Response(upstream.body, upstream);
    const location = response.headers.get("Location");
    if (location?.startsWith(env.BACKEND_ORIGIN)) {
      response.headers.set("Location", location.replace(env.BACKEND_ORIGIN, incoming.origin));
    }
    return response;
  },
};
