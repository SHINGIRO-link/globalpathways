from django.urls import path
from .views import (
    ApplicationCreateView,
    HealthView,
    InquiryCreateView,
    OpportunityDetailView,
    OpportunityListView,
    SuccessStoryListView,
)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("opportunities/", OpportunityListView.as_view(), name="opportunity-list"),
    path("opportunities/<slug:slug>/", OpportunityDetailView.as_view(), name="opportunity-detail"),
    path("applications/", ApplicationCreateView.as_view(), name="application-create"),
    path("inquiries/", InquiryCreateView.as_view(), name="inquiry-create"),
    path("success-stories/", SuccessStoryListView.as_view(), name="success-story-list"),
]
