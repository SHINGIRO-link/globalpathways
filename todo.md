# Project TODO

- [x] Reconcile the requested Django + Python REST API architecture with the existing managed Node/React project and document the runtime approach
- [x] Add a Django project and REST API application structure
- [x] Add opportunity, application, inquiry, and testimonial domain models
- [x] Add Django REST API endpoints for opportunity listing, detail, application submission, and inquiries
- [x] Configure Django admin for opportunities, applications, inquiries, and testimonials
- [x] Create curated open and coming-soon opportunity content without fabricating reviews or testimonials
- [x] Implement premium responsive landing page with trust-building hero and clear calls to action
- [x] Implement searchable/filterable opportunities listing with country, category, deadline, status, and countdown behavior
- [x] Implement opportunity detail page with eligibility, documents, description, and Apply Now flow
- [x] Implement multi-step application form with progress indicator, validation, review, and submission state
- [x] Implement testimonials/success-stories section using clearly labeled editorial or verified content only
- [x] Implement Why Choose Us trust-signal section
- [x] Implement contact/inquiry form connected to the backend API
- [x] Add responsive navigation, accessibility states, empty/loading/error states, and polished motion
- [x] Add Vitest coverage for frontend behavior and backend/API verification coverage where compatible
- [x] Run type checks, tests, and visual verification at desktop and mobile widths
- [x] Document local setup, Django admin setup, API routes, and deployment considerations
- [x] Save the final project checkpoint and deliver the project version

## Change history

- User requested a Django + Python backend with React frontend consuming REST API endpoints, replacing the original tRPC/full-stack template direction.

## Follow-up quality fixes

- [x] Add real loading and not-found/error UI for opportunity detail and apply routes instead of falling back to the landing page when data is unavailable
- [x] Add document input/collection to the application flow and only show submission success after a confirmed API response
- [x] Show inquiry submission errors and keep the dialog actionable when the backend request fails
- [x] Add explicit loading/error states for opportunity list/detail/application interactions and verify failed-route behavior

## Final interaction-state fixes

- [x] Add explicit loading and error UI for the opportunities list page instead of silently masking list-fetch failures with fallback data
- [x] Add a pending/submitting state to the application form submit action and verify failed list-fetch scenarios in the UI

## Verification follow-up

- [x] Add automated coverage or an explicit UI verification path for the `/opportunities` error state when the Django REST request fails

## UI verification follow-up

- [x] Add a development-only forced-error query path for `/opportunities` and capture the rendered recovery UI to verify the page-level error state

## Dashboard and deferred payment extension

- [x] Add authenticated dashboard route and personalized application overview
- [x] Add saved opportunities data model, API endpoints, and save/remove UI
- [x] Add application status history/timeline with review-state labels and timestamps
- [x] Add payment-ready record and post-submission fee step for a 2,000 service fee without connecting live providers yet
- [x] Add dashboard navigation, empty states, and clear payment integration-pending messaging
- [x] Add tests for saved opportunities, application status, payment-ready state, and dashboard data loading
- [x] Verify dashboard and payment-ready flow at desktop and mobile widths
- [x] Document the later MoMo/Airtel integration requirements and required provider configuration

## Dashboard hardening follow-up

- [x] Secure dashboard, saved-opportunity, status, and payment endpoints with authenticated ownership rather than arbitrary email lookup
- [x] Add remove/unsave controls to the dashboard and verify delete behavior
- [x] Render the complete application status lifecycle, including terminal states like approved/not-approved terminal states
- [x] Add automated coverage for the application status endpoint and dashboard data-loading states
- [x] Capture or exercise the payment-ready step at mobile width

## Final hardening follow-up

- [x] Enforce server-side authenticated ownership for dashboard, saved-opportunity, status, and payment endpoints using the existing authenticated session rather than client-supplied identity values
- [x] Add endpoint and manual UI verification for saved-opportunity removal
- [x] Add UI-level automated coverage for dashboard loading, data, and error states

## Last verification gap follow-up

- [x] Bind dashboard ownership to the authenticated session on the server using a session-linked identity rather than trusting client-supplied email/header values
- [x] Capture or automate the dashboard unsave interaction and confirm the card disappears after deletion
- [x] Add React-level tests for dashboard loading, populated data, and error rendering

## RWF fee, staff notifications, and opportunity expansion

- [x] Change the deferred application fee from 2,000 TBD to 2,000 RWF across Django records, API responses, admin, and React messaging
- [x] Add staff notification events when applications are submitted or status changes
- [x] Add staff notification events when payment provider selection or payment status changes
- [x] Expose staff notification records in Django admin with read/unread state
- [x] Expand the opportunity library with additional Europe and Asia scholarship, visa, and job routes using clearly labeled editorial/sample content
- [x] Add coverage for the RWF amount, notification creation, and expanded opportunity records
- [x] Verify expanded opportunity discovery and notification/status messaging on desktop and mobile

## Final RWF verification follow-up

- [x] Add staff notification handling for later paid or failed payment-status transitions
- [x] Add automated coverage for the expanded seed catalog by region, category, and route count
- [x] Capture mobile verification for the expanded opportunities page and updated RWF payment messaging

## Notification center and verified opportunity library

- [x] Add staff notification-center API with unread count, filters, mark-read, mark-all-read, and archive/delete management actions
- [x] Add staff notification center route with unread badge, filters, bulk actions, and empty/loading/error states
- [x] Add official source URL and source verification metadata to opportunity records and API responses
- [x] Replace preview-only scholarship and job records with verified listings tied to official source pages and checked deadlines
- [x] Keep source attribution and deadline freshness visible in opportunity cards and detail pages
- [x] Add tests for notification filtering/read actions and verified opportunity source/deadline data
- [x] Verify notification center and verified opportunity library at desktop and mobile widths

## Verified catalog correction follow-up

- [x] Replace all remaining preview-only backend seed records with official-source-backed opportunity entries and honest deadline or application-window notes
- [x] Correct carried-over eligibility, status, and description fields for the verified UN Careers and EURES records
- [x] Add automated assertions for source URL, verification date, deadline note, and exact checked deadline values in seeded records

## Final verified-content correction

- [x] Replace reused preview summaries, descriptions, eligibility, and document requirements in every seeded verified route with source-aligned guidance or clearly labeled portal guidance
- [x] Correct the frontend fallback UN Careers and EURES records to match their verified backend status, eligibility, and descriptions
- [x] Expand per-record test assertions for Chevening, MEXT, UN Careers, and EURES source and deadline metadata

## Bug fix: nested anchor warning

- [x] Trace the homepage nested `<a>` composition and identify the ancestor/descendant link pair
- [x] Replace the nested anchor with valid accessible markup while preserving navigation and source-link behavior
- [x] Run tests, type checks, and homepage visual verification after the fix
- [x] Save the bug-fix checkpoint

## Nested interactive-content follow-up

- [x] Refactor opportunity cards so the save button is not nested inside the card anchor
- [x] Re-run homepage verification after removing all interactive-content nesting warnings
- [x] Save a new checkpoint for the corrected markup

## Accessibility and interaction audit

- [x] Audit dashboard cards for nested links, buttons, and ambiguous interactive regions
- [x] Audit staff notification cards and management actions for valid interactive markup and accessible labels
- [x] Verify opportunity-card keyboard focus order across card navigation, source link, and save button
- [x] Add visible hover and keyboard-focus feedback or tooltips to opportunity-card save and official-source actions
- [x] Add or update automated coverage for accessible labels and interaction structure where practical
- [x] Run checks and responsive visual verification, then save the accessibility checkpoint

## Accessibility verification follow-up

- [x] Capture mobile-width screenshots for opportunities, dashboard, and staff notifications after the accessibility changes
- [x] Save a new checkpoint after the accessibility audit changes are validated

## Checkpoint confirmation

- [x] Save the successful accessibility-audit checkpoint after desktop and mobile validation

## Application submission failure

- [x] Diagnose and fix the error shown when submitting an application from the live preview
- [x] Add regression coverage for the corrected application-submission request and response handling
- [x] Verify the application flow at desktop and mobile widths and save a bug-fix checkpoint

## Application submission verification follow-up

- [x] Make the documented application submission access model explicit and support signed-out submissions safely
- [x] Add and execute regression coverage for public submission success, proxy routing, and controlled failures
- [x] Capture the actual application form at desktop and mobile widths, including a successful submission state, and save a new checkpoint

## Public application form alignment

- [x] Remove the frontend sign-in requirement from the public application form so it matches the Django access model and can reach the success state
- [x] Verify the public form success state after a real 201 response and save the final checkpoint

## Homepage tRPC parsing error

- [x] Diagnose and fix the tRPC query receiving HTML instead of JSON on the homepage
- [x] Add regression coverage for the corrected tRPC response path and preserve Django REST `/api` forwarding
- [x] Verify homepage rendering and save a bug-fix checkpoint

## tRPC end-to-end regression follow-up

- [x] Add and execute an end-to-end route test proving `/api/trpc/auth.me` returns JSON while non-tRPC `/api/*` remains Django-backed

## Education documents and resilience improvements

- [x] Add secure education certificate and diploma photo/PDF uploads using server-side storage and application metadata
- [x] Add upload validation, progress/error feedback, and safe document references in the application flow
- [x] Show a friendly Service Unavailable state when API requests fail
- [x] Add homepage loading skeletons while opportunity data is fetched
- [x] Add retry actions to the error boundary and relevant API error states
- [x] Improve initial loading performance without weakening accessibility or API behavior
- [x] Add regression tests, run Django/Vitest/build checks, verify responsive UI, and save a checkpoint

## Resilience hardening follow-up

- [x] Persist and validate server-issued education-document metadata with each application
- [x] Restrict application document references to safe upload-issued records rather than arbitrary external links
- [x] Add retry controls to Dashboard and Staff Notifications API error states
- [x] Reduce the initial homepage bundle further and re-check production chunk output
- [x] Add Django regression tests for document upload/application handling and save a new checkpoint after all validations

## Final resilience checkpoint confirmation

- [x] Save the completed document-upload and resilience-hardening checkpoint

## Application submission and additional documents

- [x] Diagnose and fix the current application submission failure from the live form
- [x] Support additional uploaded documents with document categories and secure server-issued metadata
- [x] Validate the complete submission payload, add regression tests, and verify responsive upload UI
- [x] Save a checkpoint after the submission and additional-document fix

## Final verification gaps for submission fix

- [x] Capture desktop-width verification for the categorized multi-document upload form
- [x] Save a new checkpoint after the live submission repair and additional-document changes

## Product and engineering audit

- [x] Complete and save the comprehensive product, security, operations, accessibility, performance, and functionality-gap audit
- [x] Prioritize the next implementation phase: payments, authorization hardening, abuse protection, staff review, and secure document access

## Opportunity catalog expansion

- [x] Research and verify 20 additional Europe and Asia opportunities from official source pages
- [x] Add the 20 verified opportunities to Django seed/catalog data and frontend fallback coverage
- [x] Add regression coverage for the expanded catalog and verify discovery/filtering at desktop and mobile widths
- [x] Save the expanded opportunity catalog checkpoint

## Catalog verification follow-up

- [x] Open or directly inspect all 20 new official source URLs and record source-backed timing or portal notes
- [x] Add frontend regression coverage or manual verification for category and search filtering at desktop and mobile widths

## SMTP email notifications

- [x] Revoke the previously exposed Gmail app password in Google and confirm the replacement app password is active
- [x] Send an internal notification after each new application submission
- [x] Send applicant notifications when application status changes, using consent and a safe failure path
- [x] Add email regression tests and verify notification behavior without exposing credentials
- [x] Save a post-rotation validated email-notification checkpoint

## Homepage footer guidance and navigation

- [x] Add transparent application-support disclaimer explaining that Global Pathways helps applicants prepare and submit applications but cannot guarantee acceptance
- [x] Explain that incomplete, inaccurate, or unmatched requirements can lead to rejection and encourage applicants to review requirements carefully
- [x] Add bottom-of-page links for How it works, Why us, Scholarships, and Jobs
- [x] Verify footer accessibility, responsive layout, tests, and visual rendering, then save a checkpoint


## Dedicated navigation pages and direct opportunity links

- [x] Replace header How it works and Why us links with Scholarships and Jobs links that open filtered opportunities
- [x] Add dedicated How it works page and route, linked from the footer
- [x] Add dedicated Why us page and route, linked from the footer
- [x] Add separate Applicant Responsibility page for the A clear promise content and link to it from the footer
- [x] Verify all navigation targets, accessibility, responsive layouts, tests, and save a checkpoint


## Navigation scroll reset fix

- [x] Reset scroll position to the top after navigating through the Global Pathways brand, footer pages, Scholarships, Jobs, How it works, and Why us links
- [x] Verify filtered category navigation preserves the filter while resetting scroll position
- [x] Run tests and responsive navigation verification, then save a checkpoint


## Footer policy label wording

- [x] Rename the footer “A clear promise” label to “Policies” and update related link wording consistently
- [x] Verify the wording change and save a checkpoint


## Policies footer destination fix

- [x] Ensure the entire Policies label and supporting link open the dedicated policies page directly
- [x] Verify the destination, tests, and save a checkpoint


## Policies route 404 fix

- [x] Diagnose why the dedicated `/policies` route returns the 404 page
- [x] Repair route registration or fallback behavior so Policies opens correctly
- [x] Verify the direct route, footer destination, tests, and save a checkpoint


## Staff admin dashboard and downloads

- [x] Audit current staff notification, application, payment, document, auth, and storage structures
- [x] Add staff-only APIs for submission and payment review with filters and summaries
- [x] Add secure application data and document download flows with authorization checks
- [x] Build responsive staff admin dashboard for submissions, payments, status actions, and downloads
- [x] Add regression coverage for staff authorization, filtering, status updates, and secure downloads
- [x] Verify desktop/mobile dashboard behavior and save a checkpoint


## Staff all-documents ZIP export

- [x] Add a staff-only endpoint that packages all uploaded application documents into one ZIP archive
- [x] Add a dashboard action and clear empty/loading/error behavior for the ZIP export
- [x] Add regression coverage for staff authorization, archive contents, and safe filenames
- [x] Verify desktop/mobile presentation and save a checkpoint


## Filtered staff document ZIP export

- [x] Add application-status and created-date range filters to the protected document ZIP endpoint
- [x] Add matching status/date controls to the staff dashboard and preserve selected filters in the download URL
- [x] Add regression coverage for filter combinations, archive contents, invalid dates, and authorization
- [x] Verify desktop/mobile filter presentation and save a checkpoint


## Staff applicant search

- [x] Add a protected staff search query for applicant name or email
- [x] Wire the dashboard search bar to the API with clear loading, empty, and retry behavior
- [x] Add regression coverage for name/email matching and verify responsive presentation
- [x] Save a checkpoint after validation


## Visible authentication entry point

- [x] Add a clear Sign in or Continue with Google action to the public header and dashboard entry flow
- [x] Show the signed-in account state and appropriate staff-dashboard link after authentication
- [x] Verify login navigation, accessibility, and protected staff routing, then save a checkpoint


## Role-aware authentication separation

- [x] Audit current authenticated user fields, role checks, and dashboard routes
- [x] Route approved staff/admin accounts to the staff dashboard and applicants to the student dashboard after sign-in
- [x] Show clear account-status guidance when a signed-in user is not authorized for staff tools
- [x] Verify access control, role-aware navigation, responsive states, and save a checkpoint


## Automatic end-user, staff, and admin dashboards

- [x] Define and audit the three account roles and their authoritative credential sources
- [x] Add separate end-user, staff, and admin dashboard destinations
- [x] Automatically route authenticated users to the correct dashboard without manual dashboard choices
- [x] Enforce role boundaries and clear unauthorized states for every dashboard
- [x] Add role-flow regression coverage and responsive verification, then save a checkpoint


## Dashboard account profile and sign-out controls

- [x] Audit existing logout helper and dashboard header patterns
- [x] Add shared account-profile display with name, email, and role to end-user, staff, and admin dashboards
- [x] Add accessible sign-out controls that clear the session and return users to the public homepage
- [x] Add regression coverage and responsive verification, then save a checkpoint

