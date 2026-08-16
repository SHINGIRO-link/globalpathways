from django.urls import path
from .views import (
    ApplicationCreateView, ApplicationStatusView, DashboardView, HealthView,
    InquiryCreateView, OpportunityDetailView, OpportunityListView,
    PaymentPrepareView, SavedOpportunityDeleteView, SavedOpportunityListCreateView,
    SuccessStoryListView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("opportunities/", OpportunityListView.as_view(), name="opportunity-list"),
    path("opportunities/<slug:slug>/", OpportunityDetailView.as_view(), name="opportunity-detail"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
    path("applications/<int:application_id>/status/", ApplicationStatusView.as_view(), name="application-status"),
    path("dashboard/", DashboardView.as_view(), name="dashboard"),
    path("saved-opportunities/", SavedOpportunityListCreateView.as_view(), name="saved-opportunities"),
    path("saved-opportunities/<int:opportunity_id>/", SavedOpportunityDeleteView.as_view(), name="saved-opportunity-delete"),
    path("payments/prepare/", PaymentPrepareView.as_view(), name="payment-prepare"),
    path("inquiries/", InquiryCreateView.as_view(), name="inquiry-create"),
    path("success-stories/", SuccessStoryListView.as_view(), name="success-story-list"),
]
