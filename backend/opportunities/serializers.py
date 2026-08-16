from rest_framework import serializers
from .models import Application, ApplicationStatusEvent, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, StaffNotification, SuccessStory


class OpportunitySerializer(serializers.ModelSerializer):
    category_label = serializers.CharField(source="get_category_display", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = Opportunity
        fields = ["id", "title", "slug", "category", "category_label", "status", "status_label", "country", "region", "deadline", "deadline_note", "source_name", "source_url", "source_verified_at", "summary", "description", "eligibility", "required_documents", "featured"]


class ApplicationSerializer(serializers.ModelSerializer):
    opportunity_title = serializers.CharField(source="opportunity.title", read_only=True)
    status_label = serializers.CharField(source="get_status_display", read_only=True)
    documents = serializers.ListField(child=serializers.DictField(), write_only=True, required=False)

    class Meta:
        model = Application
        fields = ["id", "opportunity", "opportunity_title", "full_name", "email", "phone", "nationality", "current_location", "education_level", "statement", "document_links", "document_metadata", "documents", "consent_to_contact", "status", "status_label", "created_at", "updated_at"]
        read_only_fields = ["id", "document_links", "document_metadata", "status", "status_label", "created_at", "updated_at"]

    def validate_documents(self, value):
        allowed_types = {"application/pdf", "image/jpeg", "image/png", "image/webp"}
        for document in value:
            key = document.get("key", "")
            url = document.get("url", "")
            content_type = document.get("content_type", "")
            if not key.startswith("education-documents/") or not url.startswith("/manus-storage/") or content_type not in allowed_types:
                raise serializers.ValidationError("Each education document must be uploaded through the secure document uploader.")
            if not document.get("name") or not isinstance(document.get("size"), int) or document["size"] > 10 * 1024 * 1024:
                raise serializers.ValidationError("Each education document must include a valid name and size under 10 MB.")
        return value

    def create(self, validated_data):
        documents = validated_data.pop("documents", [])
        validated_data["document_links"] = [document["url"] for document in documents]
        validated_data["document_metadata"] = documents
        return super().create(validated_data)

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


class StaffNotificationSerializer(serializers.ModelSerializer):
    event_type_label = serializers.CharField(source="get_event_type_display", read_only=True)
    application_name = serializers.CharField(source="application.full_name", read_only=True)

    class Meta:
        model = StaffNotification
        fields = ["id", "event_type", "event_type_label", "title", "message", "application", "application_name", "is_read", "created_at"]
        read_only_fields = ["id", "event_type_label", "application_name", "created_at"]


class SuccessStorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SuccessStory
        fields = ["id", "name", "destination", "quote"]
