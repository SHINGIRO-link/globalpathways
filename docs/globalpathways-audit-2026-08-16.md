# Global Pathways Product and Engineering Audit

**Audit date:** 16 August 2026  
**Scope:** Django REST backend, React frontend, application workflow, document uploads, dashboard, staff operations, accessibility, security, reliability, performance, and product readiness.

## Executive assessment

Global Pathways has a strong premium public-facing foundation. The project already includes a verified opportunity catalog, public application intake, authenticated dashboard ownership, deferred 2,000 RWF payment records, staff notifications, storage-backed document uploads, service-unavailable states, retry controls, loading skeletons, responsive layouts, and route-level performance improvements. The core experience is credible as a high-quality prototype and early operational MVP.

The most important remaining work is not visual polish. It is operational safety and conversion reliability: real payment processing, staff review and status management, applicant notifications, abuse protection on public endpoints, stronger authorization around saved opportunities, document security and lifecycle management, and production observability. These should be implemented before scaling traffic or advertising the platform broadly.

## Current capability map

| Area | Current state | Assessment |
|---|---|---|
| Opportunity discovery | Search, category filtering, deadlines, official source attribution, detail pages | Strong MVP; add freshness workflows and pagination |
| Public application | Multi-step form, public submission, consent, deferred fee record | Works after the latest metadata fix; add idempotency and abuse controls |
| Documents | PDF/image upload, 10 MB limit, categories, storage-backed metadata | Good foundation; add malware scanning, access policy, deletion and retention |
| Applicant dashboard | Authenticated applications, status timeline, saved routes, payment-ready state | Useful MVP; applicant self-service and status actions are limited |
| Payments | MoMo/Airtel provider selection and 2,000 RWF records | Not production-ready until live payment, webhook, reconciliation, and receipt flows exist |
| Staff operations | Notification center plus Django admin | Incomplete; staff cannot efficiently review applications, documents, or change statuses in the main UI |
| Notifications | In-app staff alerts for application/payment/status events | Applicant email/SMS/WhatsApp notifications are missing |
| Authentication | Shared Manus session validation and owner-based staff permission | Functional but staff authorization is too narrow and some ownership paths need hardening |
| Resilience | JSON proxy, service-unavailable UI, retries, loading skeletons | Good baseline; add request correlation, rate limits, monitoring, and offline-safe retry policy |
| Accessibility | Valid interactive markup, labels, focus feedback, responsive checks | Good baseline; add automated browser accessibility checks and full keyboard-flow coverage |
| Performance | Lazy private routes and vendor chunking; entry chunk reduced materially | Good improvement; add image/font strategy, caching, and performance budgets |

## Critical findings: address before public growth

### 1. Payment collection is still deferred

The application records a 2,000 RWF payment requirement and allows MoMo or Airtel Money selection, but it does not initiate a real payment, receive provider callbacks, verify transaction signatures, reconcile duplicate callbacks, issue receipts, or handle refunds. This is the largest business-critical gap because the service promise depends on a paid application process.

**Required functionality:** provider adapter abstraction, payment initiation, hosted or USSD flow, signed webhook endpoint, idempotent transaction state machine, payment receipt, failed-payment recovery, reconciliation view, and a clear policy for refunds and charge disputes.

### 2. Public application endpoints need abuse protection

The application and inquiry endpoints are intentionally public, which is appropriate for conversion, but the current design needs throttling, spam detection, request-size limits at the Django layer, duplicate-submission protection, and an operational review queue. Without these controls, bots can create applications, staff notifications, storage costs, and fake demand.

**Required functionality:** IP and email rate limits, CAPTCHA or risk scoring after a threshold, idempotency keys, duplicate detection, honeypot fields, structured audit logging, and a moderation state for suspicious submissions.

### 3. Saved-opportunity ownership should be tightened

The dashboard application and status paths are tied to the authenticated session, but the saved-opportunity list path queries by client-supplied email after checking only that the header matches the query parameter. The server should derive the owner identity from the authenticated session for every saved-opportunity read, create, and delete operation, then use email only as display metadata. This should be treated as a privacy-hardening item before handling real user data.

**Required functionality:** session-derived owner filtering on every saved-opportunity endpoint, regression tests proving cross-account reads and deletes fail, and a migration strategy for existing rows with incomplete owner identifiers.

### 4. Staff access is effectively single-owner access

Staff authorization compares the authenticated user to one configured `OWNER_OPEN_ID`. That is adequate for a single administrator but not for a real service team. There is no staff-user table, role assignment workflow, least-privilege permission model, or staff audit trail.

**Required functionality:** staff membership and role model, roles such as reviewer, finance, content editor, and super-admin, invitation or admin-managed assignment, permission checks per action, and audit records for status, payment, and document access.

### 5. Application review is not a first-class staff workflow

The notification center tells staff that activity occurred, but the primary UI does not provide a complete review queue with applicant profile, opportunity, uploaded documents, payment state, status transition controls, internal notes, assignment, and follow-up actions. Staff currently depend heavily on Django admin.

**Required functionality:** staff application inbox, filters by status/payment/deadline/date, application detail view, secure document preview/download, internal notes, reviewer assignment, controlled status transitions, and an audit timeline.

## High-priority product gaps

### Applicant communication

Applicants currently receive a success state and can inspect dashboard status when authenticated, but there is no reliable email, SMS, or WhatsApp communication for submission receipt, payment confirmation, missing information, status changes, approval, or rejection. Communication should be event-driven and retryable, with delivery status visible to staff.

### Applicant self-service

The dashboard should allow applicants to update contact details, add missing documents when an application enters `needs_info`, view submitted document names and upload times, download receipts, withdraw an application where policy permits, and request support. The current dashboard is primarily a read-only tracker.

### Opportunity freshness and editorial workflow

The catalog has official links and verification dates, but there is no scheduled freshness check, stale-record warning, editor review queue, source availability monitoring, or history of changes to deadlines and eligibility. The platform should distinguish a portal whose deadline varies from a route with a verified fixed deadline and display the last checked date consistently.

### Conversion and trust features

The public experience would benefit from a transparent fee explanation, privacy policy, terms of service, refund policy, service-level expectations, support contact details, and a concise “what happens after you submit” sequence. These are important for trust because the product handles identity information, education documents, and payments.

## Security and privacy gaps

| Risk | Current concern | Recommended control |
|---|---|---|
| Document access | Storage references are persisted, but an explicit applicant/staff authorization layer for viewing documents is not evident | Serve documents through an authorization endpoint or short-lived signed URLs after ownership checks |
| Malware | MIME and size validation are present, but content scanning is not evident | Add antivirus or managed document scanning before marking a document accepted |
| Orphaned files | Uploads can exist if application submission fails afterward | Track upload session/status and run a controlled orphan-retention cleanup process |
| Sensitive data | Names, email, phone, nationality, location, statements, and education files are stored | Define retention, deletion, export, privacy notice, and access logging policies |
| CSRF and cookies | Shared session authentication is present; public API and deployment cookie behavior need production validation | Set secure cookie policy, trusted origins, CSRF posture, and production HTTPS checks |
| Configuration | Development defaults include `DEBUG=true`, permissive CORS in debug, and a fallback development secret | Fail fast in production when secure secret, allowed hosts, HTTPS, and database settings are missing |
| Authorization | Staff is owner-based and saved-opportunity reads need session-derived filtering | Add role-based permissions and cross-account regression tests |
| Input abuse | Public text fields and upload endpoints need rate and content controls | Add throttles, length limits, spam controls, structured validation, and audit logs |

## Reliability and operations gaps

The project has useful controlled error states, but production readiness requires stronger visibility into what failed and whether users recovered. Add structured logs with request IDs, API latency and error metrics, upload failure metrics, payment reconciliation alerts, uptime checks, and an error-tracking integration. Add a health endpoint that checks the Django API, database, and storage dependency separately rather than reporting only process availability.

The database and file-storage recovery plan also needs to be explicit. Define automated backups, restore tests, migration procedures, document retention, and incident response contacts. SQLite is appropriate for local development but should not be the production persistence strategy for a growing application and notification workload.

## Frontend and accessibility opportunities

The current frontend has a polished visual system and has already addressed nested anchors, focus feedback, loading skeletons, retries, and responsive layouts. The next quality layer is end-to-end browser coverage for the actual public application flow, document category selection, rejected upload, successful upload, failed submission, retry recovery, dashboard ownership, and staff permission denial.

Add automated accessibility checks for landmark structure, heading order, color contrast, form labels, error announcement, focus restoration after dialogs, keyboard navigation through the application steps, and reduced-motion behavior. Add explicit upload progress and cancellation feedback for larger files, plus a visible list of uploaded documents with category, size, and removal/replacement actions.

## Performance opportunities

The entry bundle has been reduced substantially through route and vendor splitting. Continue with an explicit performance budget, compressed and cacheable assets, font-display strategy, image dimension declarations, preconnect only where useful, and measurement of first contentful paint, largest contentful paint, interaction to next paint, and cumulative layout shift on mobile. Avoid loading dashboard, staff, chart, and admin dependencies on the public landing route.

## Recommended functionality roadmap

### Phase A: production safety and revenue foundation

Implement payment initiation and signed webhooks for MoMo and Airtel Money; add idempotency and reconciliation; harden saved-opportunity ownership; add public endpoint throttling and duplicate submission protection; introduce production configuration checks; and define privacy, retention, refund, and document-access policies.

### Phase B: staff operations

Build the staff application inbox and detail view, secure document preview/download, reviewer assignment, internal notes, controlled status transitions, payment reconciliation, and staff audit logging. Replace the single-owner permission check with role-based staff membership.

### Phase C: applicant experience

Add applicant email/SMS/WhatsApp events, a dashboard document center, missing-information requests, receipts, profile editing, support tickets or inquiry threads, and a clear application activity timeline.

### Phase D: catalog quality and growth

Add opportunity editorial workflows, source freshness checks, deadline alerts, saved-search notifications, related opportunities, referral/partner attribution, analytics funnels, and content pages for visa preparation, scholarship readiness, CV review, and interview preparation.

### Phase E: scale and governance

Move production persistence to a managed relational database, add automated backups and restore drills, formalize observability, add privacy export/deletion workflows, establish incident response, and introduce a test environment with migration and payment-webhook replay checks.

## Prioritized implementation backlog

| Priority | Functionality | Why it matters | Dependency |
|---|---|---|---|
| P0 | Live MoMo/Airtel payment and signed webhooks | Converts the deferred fee into a real business flow | Provider credentials and policy decisions |
| P0 | Saved-opportunity session ownership hardening | Prevents privacy leakage across accounts | Existing auth session |
| P0 | Public endpoint throttling and idempotency | Prevents spam, duplicate records, and storage abuse | API middleware and persistence |
| P0 | Staff application review inbox | Makes operations possible without relying on raw admin | Role model and document access |
| P0 | Secure document viewing and malware scanning | Protects highly sensitive applicant files | Storage and scanning provider |
| P1 | Applicant email/SMS/WhatsApp notifications | Reduces uncertainty and support burden | Notification provider and templates |
| P1 | Staff roles, assignments, audit logs | Enables team operations and accountability | Staff membership model |
| P1 | Production configuration and database hardening | Prevents unsafe deployment defaults | Hosting and database choice |
| P1 | Applicant self-service for missing information | Shortens review cycles and improves completion | Status workflow and document center |
| P1 | Automated browser accessibility and critical-flow tests | Protects the conversion path from regressions | Browser test runner |
| P2 | Opportunity freshness/editorial workflow | Keeps discovery trustworthy over time | Staff content tooling |
| P2 | Analytics funnel and attribution | Measures acquisition and application conversion | Privacy-compliant analytics |
| P2 | Support and partner/referral workflows | Expands service capacity and acquisition | CRM or internal support model |

## Recommended next build sequence

The next implementation should be a single vertical slice: **staff review inbox plus secure document access**, backed by the saved-opportunity authorization fix and public submission throttling. That slice creates immediate operational value and exposes the permission, storage, and status-transition contracts needed for later payment and notification work. After that, implement payment initiation and webhooks, then applicant communications and self-service.

## Definition of production readiness

Global Pathways should not be considered production-ready until a new applicant can submit once without duplication, upload and later access only their own documents, receive a receipt and status notification, pay and receive a verified payment result, and obtain support when a provider or API is unavailable. Staff should be able to review the complete application, see payment and document state, change status with an audit trail, and recover from failed integrations. The platform should have tested backups, secure production configuration, monitoring, and documented privacy and retention behavior.

## Audit conclusion

The project has a differentiated, trustworthy visual foundation and a broad early-MVP feature set. The highest-return work now is operational completion rather than adding more decorative frontend sections. Prioritize authorization, payments, staff review, document security, abuse protection, and applicant communication in that order; then invest in catalog freshness, analytics, and growth features once the core service can safely handle real applications.
