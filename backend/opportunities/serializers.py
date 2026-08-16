from rest_framework import serializers
from .models import Application, Inquiry, Opportunity, SuccessStory


class OpportunitySerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            "id", "title", "slug", "category", "category_label", "status", "status_label",
            "country", "region", "deadline", "summary", "description", "eligibility",
            "required_documents", "featured",
        ]


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = [
            "id", "opportunity", "full_name", "email", "phone", "nationality",
            "current_location", "education_level", "statement", "document_links",
            "consent_to_contact", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_consent_to_contact(self, value):
        if not value:
            raise serializers.ValidationError("Please consent to contact so our team can support your application.")
        return value


class InquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inquiry
        fields = ["id", "full_name", "email", "topic", "message", "created_at", "resolved"]
        read_only_fields = ["id", "created_at", "resolved"]


class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = ["id", "name", "destination", "quote"]
