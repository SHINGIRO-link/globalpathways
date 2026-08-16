from django.utils import timezone
from rest_framework import generics
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Application, Inquiry, Opportunity, SuccessStory
from .serializers import ApplicationSerializer, InquirySerializer, OpportunitySerializer, SuccessStorySerializer


class OpportunityListView(generics.ListAPIView):
    serializer_class = OpportunitySerializer
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ["title", "summary", "country", "category", "region"]
    ordering_fields = ["deadline", "title", "created_at"]

    def get_queryset(self):
        queryset = Opportunity.objects.all()
        category = self.request.query_params.get("category")
        region = self.request.query_params.get("region")
        status = self.request.query_params.get("status")
        if category:
            queryset = queryset.filter(category=category)
        if region:
            queryset = queryset.filter(region=region)
        if status:
            queryset = queryset.filter(status=status)
        return queryset


class OpportunityDetailView(generics.RetrieveAPIView):
    queryset = Opportunity.objects.all()
    serializer_class = OpportunitySerializer
    lookup_field = "slug"


class ApplicationCreateView(generics.CreateAPIView):
    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer


class InquiryCreateView(generics.CreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer


class SuccessStoryListView(generics.ListAPIView):
    serializer_class = SuccessStorySerializer

    def get_queryset(self):
        return SuccessStory.objects.filter(published=True, consent_confirmed=True)


class HealthView(APIView):
    def get(self, request):
        return Response({"status": "ok", "service": "globalpathways-django-api", "time": timezone.now()})
