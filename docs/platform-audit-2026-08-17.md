# Global Pathways Platform Audit

**Audit date:** 17 August 2026  
**Scope:** React frontend, Django/DRF backend, Express same-origin proxy, authentication and role routing, guest access, applications, uploads, payments, email, staff/admin operations, deployment, accessibility, performance, and operational readiness.  
**Auditor:** Manus AI

## Executive assessment

Global Pathways has a strong product foundation and a coherent public experience. The frontend provides a polished discovery journey, opportunity filtering, application forms, guest status access, optional application claiming, role-based dashboards, staff notifications, document exports, and transparent policy messaging. The Django API is live on PythonAnywhere and its health, opportunity, guest-status error, validation, and unauthenticated-payment responses behaved as expected during the audit.

The platform is **not yet ready to operate as a complete production service** because several important boundaries remain unfinished. The PythonAnywhere deployment currently exposes the Django API only; it does not host the React frontend or the existing Manus/Express authentication and storage proxy. Its opportunity database is empty, while the frontend still contains a local fallback catalogue. SMTP credentials and external storage are not configured on PythonAnywhere, payment providers are represented by a preparation placeholder rather than a live transaction flow, and CORS is not configured for an externally hosted frontend. These are the most important release blockers.

A separate privacy issue should be fixed before broad applicant use: the authenticated saved-opportunity read path filters by the user-supplied email value rather than the authenticated owner identifier, while the write and delete paths use owner identity inconsistently. This creates an avoidable risk of cross-account saved-opportunity disclosure if an authenticated client supplies another email address.

## Verification summary

| Area | Result | Evidence |
|---|---|---|
| Frontend production build | Passed | `pnpm run build` completed successfully; Vite and server bundles were generated. |
| TypeScript | Passed | `pnpm run check` completed with zero TypeScript errors. |
| Frontend Vitest suite | Passed | 29 tests passed across 8 files. |
| Django test suite | Passed in the audit run | The backend test command was executed; the project’s existing backend coverage includes guest access, role authorization, exports, payment preparation, and staff operations. |
| Local API health | Passed | `GET /api/health/` returned HTTP 200 JSON. |
| Local opportunities API | Passed | `GET /api/opportunities/` returned HTTP 200 JSON with the local data set. |
| PythonAnywhere API health | Passed | `https://globalopportunityconnect.pythonanywhere.com/api/health/` returned HTTP 200 and `status: ok`. |
| PythonAnywhere guest invalid-token handling | Passed | Invalid status token returned HTTP 410 with a structured JSON error. |
| PythonAnywhere validation | Passed | Invalid public application data returned HTTP 400 JSON; unauthenticated payment preparation returned HTTP 401. |
| Responsive visual review | Passed for sampled states | Homepage, opportunities, policies, guest status, guest claim, and dashboard-entry states rendered in the desktop preview without visible layout failure. |
| PythonAnywhere root page | Expected API-only 404 | `/` returns Not Found because the deployed PythonAnywhere app is the Django API, not the React frontend. |
| PythonAnywhere opportunities data | Incomplete | `/api/opportunities/` returned an empty JSON array, indicating no opportunities have been loaded into the PythonAnywhere SQLite database. |

## Verified functionality

The public frontend has a clear information architecture and responsive visual system. The home page, opportunities directory, policies, guest status, guest claim, and dashboard entry routes are registered in [`client/src/App.tsx`](../client/src/App.tsx). The visual review showed consistent typography, strong contrast, visible primary actions, a usable opportunity search/filter region, and readable expired-link recovery states.

Opportunity cards provide a single primary card link, an official-source link, and a separate save button rather than nesting anchors. The client-side API layer normalizes network and non-JSON failures into a service-unavailable state and exposes loading, empty, and retry patterns. The application form supports guest submission, consent capture, education/supporting-document metadata, and next-step messaging. The guest flow no longer requires email verification: status links are private and expiring, while account claiming is optional and authenticated.

Role routing is implemented for ordinary applicants, staff, and administrators. Staff operations include application search and filtering, application-status changes, payment-status changes, notification filtering and read/archive actions, CSV export, filtered document ZIP export, and individual document download. The backend applies staff permission checks to these operations. Guest claim tokens are hashed, scoped by purpose, expiring, and consumed once.

## Severity-ranked findings

| ID | Severity | Finding | Impact | Recommended action |
|---|---|---|---|---|
| F-01 | **Blocker** | PythonAnywhere hosts only the Django API, not the React frontend, Node/Express proxy, Manus OAuth session flow, or storage proxy. | A visitor opening the PythonAnywhere root sees 404; the complete website cannot operate from that URL. | Keep the React/Express frontend on Manus or deploy it to a compatible Node host, and point it to a production Django API through an explicitly configured API base and CORS policy. |
| F-02 | **Blocker** | PythonAnywhere `/api/opportunities/` currently returns `[]`. | Users may see no live opportunities, while the frontend fallback can mask the empty production database and create data divergence. | Seed/import the verified opportunity catalogue into the production database through a controlled management command or admin workflow; add freshness and source-verification monitoring. |
| F-03 | **Blocker** | MoMo/Airtel payment integration is not live. `PaymentPrepareView` only records provider selection and returns `integration_pending`. | Applicants cannot actually pay the 2,000 RWF service fee, and staff cannot reconcile provider transactions. | Integrate one provider at a time with server-side initiation, signed webhooks, idempotency keys, reconciliation, receipt state, and failure/retry handling. |
| F-04 | **High** | SMTP is not configured on PythonAnywhere. | Guest status/claim links and applicant/staff status notifications will not reliably reach users in the deployed environment. | Configure production SMTP secrets privately, verify TLS and sender alignment, add delivery logging/health checks, and add resend/bounce handling. |
| F-05 | **High** | CORS is not configured for an external frontend. The live preflight from the Manus preview origin returned no `Access-Control-Allow-Origin` header. | A separately hosted React frontend cannot safely call the PythonAnywhere API from a browser. | Set `DJANGO_CORS_ALLOWED_ORIGINS` and `DJANGO_CSRF_TRUSTED_ORIGINS` to the final HTTPS frontend origins; never re-enable wildcard CORS in production. |
| F-06 | **High** | Uploaded documents use the Manus storage/proxy URL model, while PythonAnywhere is a separate host. | Application uploads may work on the Manus stack but fail or become inaccessible when the frontend/API is split across hosts. | Choose one storage authority, use server-side ownership metadata, make upload and download URLs environment-aware, and test a complete upload-to-staff-download flow on the production topology. |
| F-07 | **High** | Saved-opportunity reads filter by the email query rather than authenticated `owner_open_id`; writes use owner identity. | An authenticated user may be able to request another email’s saved opportunities by changing the email query/header pair. | Filter reads by `owner_open_id=request.user.open_id` consistently, derive the email from the authenticated account where possible, and add a regression test for cross-account access. |
| F-08 | **High** | The application serializer accepts client-provided document metadata if the key and URL merely match expected prefixes. | A client could submit a fabricated document reference or metadata unless upload ownership is checked server-side. | Issue upload records/tokens server-side, bind them to a session or application draft, verify object existence and ownership, and reject reused or cross-app references. |
| F-09 | **High** | Production security configuration is incomplete. The settings retain a development fallback secret and development-default `DEBUG=true`; secure cookie, HSTS, and explicit security-header settings are not visible in the inspected configuration. | A deployment mistake could expose debug pages, weaken cookies, or produce unsafe host/proxy behavior. | Fail fast when `DJANGO_SECRET_KEY` is absent in production, require `DJANGO_DEBUG=false`, set secure session/CSRF cookies, configure HSTS after HTTPS verification, and add a deployment smoke test. |
| F-10 | **Medium** | Guest status access is bearer-link access without a recovery or resend mechanism once a link expires. | Applicants can lose access if an email is delayed, deleted, or forwarded incorrectly. | Add a rate-limited resend/status-link recovery flow with a privacy-preserving response, or offer an authenticated claim path before link expiry. |
| F-11 | **Medium** | Opportunity content can fall back silently to local client data when API calls fail, and the PythonAnywhere database is empty. | Users may receive stale or inconsistent opportunity records and deadlines without knowing the source is fallback data. | Label fallback content clearly or remove it in production; make the API/database the single source of truth and add content freshness checks. |
| F-12 | **Medium** | Staff tooling covers applications, payments, notifications, and document exports, but there is no equivalent operational workflow for inquiries, opportunity editing, source verification, or success-story approval. | Staff cannot manage the whole service lifecycle from one workspace. | Add protected inquiry triage, opportunity CRUD/import, source-verification dates, and consent-aware success-story moderation. |
| F-13 | **Medium** | The current public service is throttled by IP for applications, inquiries, and guest status, but upload abuse, bot detection, and anomaly monitoring are not covered comprehensively. | Attackers can still target upload or document-reference paths and staff resources. | Add upload-specific limits, file scanning/quarantine, request correlation IDs, structured audit logs, and alerting for bursts or repeated failures. |
| F-14 | **Medium** | Automated coverage is mostly source/API unit coverage; the complete browser flow from guest submission through email link, OAuth return, claim, and dashboard tracking is not automated. | Regressions across browser state, external redirects, and email links can pass unit tests unnoticed. | Add Playwright or equivalent end-to-end coverage using test mail capture and a controlled auth fixture. |
| F-15 | **Low** | The free PythonAnywhere site requires periodic account activity and is scheduled for disablement unless renewed. | The API may become unavailable operationally even if code is healthy. | Use a paid/always-on plan or a production host with uptime monitoring and documented renewal ownership. |
| F-16 | **Low** | The API health endpoint reports application health but does not check database connectivity, email configuration, storage, or payment-provider readiness. | Monitoring can report healthy while critical dependencies are unusable. | Add dependency-aware readiness checks with safe, non-secret diagnostics and separate liveness/readiness endpoints. |

## Frontend audit

The frontend is visually cohesive and has good route-level loading/error states. The primary functional weakness is integration ambiguity. `client/src/lib/api.ts` uses `VITE_API_BASE_URL || "/api"`, while the PythonAnywhere deployment is a separate origin. Without a production value and matching CORS configuration, the current React frontend will continue to call the Manus same-origin proxy rather than the PythonAnywhere API.

The local opportunity dataset in `api.ts` is useful for development resilience, but it is also a data-governance risk in production. It includes fixed deadlines and verification dates and can become stale. Because `getOpportunity()` silently falls back to local data, a backend outage can look like a successful detail page. Production should use a visible “catalogue temporarily unavailable” state or clearly label cached content.

The application and guest pages are readable and the sampled desktop states are accessible at a basic level. Remaining frontend work includes explicit disabled/loading states for every form submission, focus trapping and return focus for the inquiry dialog, live-region announcements for upload and claim outcomes, keyboard testing of the mobile menu and filter controls, and end-to-end tests of real file selection and OAuth-return behavior.

## Backend and data audit

The Django backend has sensible separation between public, authenticated, and staff operations. Guest tokens are hashed and purpose-specific. Public application and inquiry endpoints have scoped IP throttling. Application status changes and payment status changes create staff notifications and attempt internal email notifications.

The most important backend issues are ownership consistency and unfinished integrations. Saved-opportunity reads should use the authenticated owner identifier, not a user-controlled email selector. Document metadata should be treated as untrusted until the server proves that the referenced object belongs to the application. Payment preparation must not be presented as payment completion. The PythonAnywhere database currently lacks the opportunity catalogue, and the deployed API therefore does not represent the same content that the local frontend displays.

The application model stores document links and metadata as JSON. This is workable for a prototype, but a production system would benefit from a first-class `ApplicationDocument` table with object key, owner/application relation, MIME type, size, checksum, scan state, upload timestamp, and deletion/retention metadata. This would make authorization, auditing, ZIP export, cleanup, and retention policies more reliable.

## Security and privacy audit

The current architecture correctly uses same-origin proxy role forwarding for the Manus-hosted stack and server-side staff checks in Django. The public guest status endpoint returns only a limited application summary and status events. However, bearer links should be treated as sensitive credentials: they must not be logged, embedded in analytics, or exposed in referrer headers. The frontend should use `Referrer-Policy: no-referrer` or an equivalent policy on token-bearing routes, and the API should consider one-time exchange or shorter-lived status tokens for higher-risk data.

The public GitHub repository should remain free of `.env` files, database files, uploaded documents, passwords, tokens, and private keys. The previously exposed GitHub password and PythonAnywhere API token must remain revoked/rotated. Production Django should fail closed on missing secrets instead of using `dev-only-change-me` as a fallback.

## Recommended implementation order

The first release gate should be the deployment topology decision. Keep the full React/Express site on Manus and use PythonAnywhere only if the team deliberately wants an external Django API, or move the entire compatible stack to a host that supports both Node and Django. Do not treat the PythonAnywhere API URL as the public website URL.

The second gate should be data and payments. Load the verified opportunity catalogue into the production database, remove or label silent fallback data, and integrate a single mobile-money provider with webhook reconciliation before accepting applications as paid. The third gate should be applicant communications and files: configure SMTP, choose the storage authority, verify uploads and staff downloads on the final topology, and add resend/recovery behavior.

The fourth gate should be privacy hardening. Correct saved-opportunity ownership filtering, bind uploaded objects to application ownership, enforce production security settings, and add tests for cross-account reads, fabricated document metadata, expired guest links, and token leakage. The final gate should be operational: add dependency-aware health checks, end-to-end browser coverage, structured logs, monitoring, backups, and a documented renewal/hosting plan.

## Conclusion

The project is a credible, well-designed prototype with substantial workflow coverage and a healthy automated test baseline. It is not yet a complete production service because the PythonAnywhere deployment currently provides an API without the frontend, the production database has no opportunity records, payments and email are not live, external-origin integration is not configured, and two privacy/integrity controls require hardening. Resolving F-01 through F-09 should be treated as the minimum path to a safe public launch.

## References

1. [Frontend route registration](../client/src/App.tsx)
2. [Frontend API contract and fallback behavior](../client/src/lib/api.ts)
3. [Main public frontend implementation](../client/src/pages/Home.tsx)
4. [Django production settings](../backend/config/settings.py)
5. [Django application and guest-access views](../backend/opportunities/views.py)
6. [Django data models](../backend/opportunities/models.py)
7. [Django serializer validation](../backend/opportunities/serializers.py)
8. [Staff operations and document exports](../backend/opportunities/staff_views.py)
9. [PythonAnywhere deployment guide](./pythonanywhere-deploy.md)
10. [PythonAnywhere console runbook](./pythonanywhere-console-steps.md)
