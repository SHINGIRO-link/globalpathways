from django.contrib import admin
from .models import Application, ApplicationStatusEvent, Inquiry, Opportunity, PaymentRecord, SavedOpportunity, SuccessStory


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


@admin.register(SuccessStory)
class SuccessStoryAdmin(admin.ModelAdmin):
    list_display = ("name", "destination", "consent_confirmed", "published", "created_at")
    list_filter = ("consent_confirmed", "published")
    search_fields = ("name", "destination", "quote")
