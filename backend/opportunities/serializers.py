from rest_framework import serializers
from .models import Application, ApplicationStatusEvent, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, SuccessStory


class OpportunitySerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Opportunity
        fields = ["id", "title", "slug", "category", "category_label", "status", "status_label", "country", "region", "deadline", "summary", "description", "eligibility", "required_documents", "featured"]


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity_title = serializers.CharField(source="opportunity.title", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Application
        fields = ["id", "opportunity", "opportunity_title", "full_name", "email", "phone", "nationality", "current_location", "education_level", "statement", "document_links", "consent_to_contact", "status", "status_label", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "status_label", "created_at", "updated_at"]

    def validate_consent_to_contact(self, value):
        if not value:
            raise serializers.ValidationError("Please consent to contact so our team can support your application.")
        return value


class ApplicationStatusEventSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = ApplicationStatusEvent
        fields = ["id", "status", "status_label", "note", "created_at"]


class SavedOpportunitySerializer(serializers.ModelSerializer):
    opportunity_detail = OpportunitySerializer(source="opportunity", read_only=True)

    class Meta:
        model = SavedOpportunity
        fields = ["id", "email", "opportunity", "opportunity_detail", "created_at"]
        read_only_fields = ["id", "opportunity_detail", "created_at"]


class PaymentRecordSerializer(serializers.ModelSerializer):
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    provider_label = serializers.CharField(source="get_provider_display", read_only=True)

    class Meta:
        model = PaymentRecord
        fields = ["id", "application", "amount", "currency", "provider", "provider_label", "status", "status_label", "provider_reference", "created_at", "updated_at"]
        read_only_fields = ["id", "status", "status_label", "provider_label", "provider_reference", "created_at", "updated_at"]


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "full_name", "email", "topic", "message", "created_at", "resolved"]
        read_only_fields = ["id", "created_at", "resolved"]


class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = ["id", "name", "destination", "quote"]
