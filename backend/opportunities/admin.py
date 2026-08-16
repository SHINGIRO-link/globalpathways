from django.contrib import admin
from .models import Application, Inquiry, Opportunity, SuccessStory


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "country", "status", "deadline", "featured")
    list_filter = ("category", "status", "region", "featured")
    search_fields = ("title", "country", "summary")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("full_name", "opportunity", "email", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("full_name", "email", "opportunity__title")
    readonly_fields = ("created_at",)


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
