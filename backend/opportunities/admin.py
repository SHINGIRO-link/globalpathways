from django.contrib import admin
from .email_notifications import notify_application_status, notify_internal_status
from .models import AccountProfile, Application, ApplicationStatusEvent, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, StaffNotification, SuccessStory


@admin.register(AccountProfile)
class AccountProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "role", "created_at", "updated_at")
    list_filter = ("role",)
    search_fields = ("user__email", "user__first_name", "user__last_name")
    readonly_fields = ("public_id", "created_at", "updated_at")


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "country", "region", "status", "deadline", "featured")
    list_filter = ("category", "status", "region", "featured")
    search_fields = ("title", "country", "summary")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "opportunity", "email", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("full_name", "email", "opportunity__title")
    readonly_fields = ("created_at", "updated_at")

    def save_model(self, request, obj, form, change):
        previous_status = None
        if change and obj.pk:
            previous_status = Application.objects.get(pk=obj.pk).status
        super().save_model(request, obj, form, change)
        if change and previous_status and previous_status != obj.status:
            StaffNotification.objects.create(
                event_type="application_status",
                title="Application status changed",
                message=f"{obj.full_name}'s application moved from {previous_status.replace('_', ' ')} to {obj.status.replace('_', ' ')}.",
                application=obj,
            )
            notify_internal_status(obj, previous_status)
            notify_application_status(obj)


@admin.register(ApplicationStatusEvent)
class ApplicationStatusEventAdmin(admin.ModelAdmin):
    list_display = ("application", "status", "note", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("application__full_name", "application__email", "note")


@admin.register(SavedOpportunity)
class SavedOpportunityAdmin(admin.ModelAdmin):
    list_display = ("email", "opportunity", "created_at")
    search_fields = ("email", "opportunity__title")


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):
    list_display = ("application", "amount", "currency", "provider", "status", "updated_at")
    list_filter = ("provider", "status", "currency")
    search_fields = ("application__full_name", "application__email", "provider_reference")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ("full_name", "email", "topic", "resolved", "created_at")
    list_filter = ("resolved", "created_at")
    search_fields = ("full_name", "email", "message")


@admin.register(StaffNotification)
class StaffNotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "event_type", "is_read", "created_at", "application")
    list_filter = ("event_type", "is_read")
    search_fields = ("title", "message")


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "consent_confirmed", "published", "created_at")
    list_filter = ("consent_confirmed", "published")
    search_fields = ("name", "destination", "quote")
