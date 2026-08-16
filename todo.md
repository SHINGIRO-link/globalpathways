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
- [ ] Save the final project checkpoint and deliver the project version

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
