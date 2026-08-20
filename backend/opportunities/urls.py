from django.urls import path

from .admin_views import AdminAccountView
from .auth_views import AuthMeView, LoginView, LogoutView, PasswordResetConfirmView, PasswordResetRequestView, RegisterView, csrf_cookie
from .documents import EducationDocumentUploadView, StaffDocumentServeView
from .views import (
    ApplicationCreateView, ApplicationStatusView, DashboardView, GuestClaimApplicationView, GuestStatusView, HealthView,
    InquiryCreateView, OpportunityDetailView, OpportunityListView,
    PaymentPrepareView, SavedOpportunityDeleteView, SavedOpportunityListCreateView,
    StaffNotificationListView, StaffNotificationMarkAllReadView, StaffNotificationReadView,
    SuccessStoryListView,
)
from .staff_views import (
    StaffAllDocumentsZipView, StaffApplicationDocumentDownloadView, StaffApplicationListView,
    StaffApplicationStatusView, StaffApplicationsExportView, StaffPaymentStatusView,
)

urlpatterns = [
    path("auth/csrf/", csrf_cookie, name="auth-csrf"),
    path("auth/me/", AuthMeView.as_view(), name="auth-me"),
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/password-reset/", PasswordResetRequestView.as_view(), name="auth-password-reset"),
    path("auth/password-reset/confirm/", PasswordResetConfirmView.as_view(), name="auth-password-reset-confirm"),
    path("uploads/education-document", EducationDocumentUploadView.as_view(), name="education-document-upload"),
    path("manus-storage/<path:key>", StaffDocumentServeView.as_view(), name="staff-document-serve"),
    path("admin/accounts/", AdminAccountView.as_view(), name="admin-accounts"),
    path("admin/accounts/<int:account_id>/", AdminAccountView.as_view(), name="admin-account-detail"),
    path("health/", HealthView.as_view(), name="health"),
    path("opportunities/", OpportunityListView.as_view(), name="opportunity-list"),
    path("opportunities/<slug:slug>/", OpportunityDetailView.as_view(), name="opportunity-detail"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
    path("guest/status/", GuestStatusView.as_view(), name="guest-status"),
    path("guest/claim/", GuestClaimApplicationView.as_view(), name="guest-claim"),
    path("applications/<int:application_id>/status/", ApplicationStatusView.as_view(), name="application-status"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("saved-opportunities/", SavedOpportunityListCreateView.as_view(), name="saved-opportunities"),
    path("saved-opportunities/<int:opportunity_id>/", SavedOpportunityDeleteView.as_view(), name="saved-opportunity-delete"),
    path("payments/prepare/", PaymentPrepareView.as_view(), name="payment-prepare"),
    path("inquiries/", InquiryCreateView.as_view(), name="inquiry-create"),
    path("success-stories/", SuccessStoryListView.as_view(), name="success-story-list"),
    path("staff/notifications/", StaffNotificationListView.as_view(), name="staff-notifications"),
    path("staff/notifications/mark-all-read/", StaffNotificationMarkAllReadView.as_view(), name="staff-notifications-mark-all-read"),
    path("staff/notifications/<int:notification_id>/", StaffNotificationReadView.as_view(), name="staff-notification-detail"),
    path("staff/applications/", StaffApplicationListView.as_view(), name="staff-applications"),
    path("staff/applications/export/", StaffApplicationsExportView.as_view(), name="staff-applications-export"),
    path("staff/applications/documents/export/", StaffAllDocumentsZipView.as_view(), name="staff-documents-export"),
    path("staff/applications/<int:application_id>/status/", StaffApplicationStatusView.as_view(), name="staff-application-status"),
    path("staff/applications/<int:application_id>/documents/<int:document_index>/download/", StaffApplicationDocumentDownloadView.as_view(), name="staff-document-download"),
    path("staff/payments/<int:payment_id>/status/", StaffPaymentStatusView.as_view(), name="staff-payment-status"),
]
