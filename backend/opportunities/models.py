import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class AccountProfile(models.Model):
    ROLE_CHOICES = [("user", "User"), ("staff", "Staff"), ("admin", "Admin")]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="account_profile")
    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    role = models.CharField(max_length=12, choices=ROLE_CHOICES, default="user")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email or self.user.username} ({self.role})"


class Opportunity(models.Model):
    CATEGORY_CHOICES = [("scholarship", "Scholarship"), ("visa", "Student Visa"), ("job", "Job")]
    STATUS_CHOICES = [("open", "Open now"), ("coming", "Coming soon")]

    title = models.CharField(max_length=180)
    slug = models.SlugField(unique=True)
    category = models.CharField(max_length=30, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    country = models.CharField(max_length=80)
    region = models.CharField(max_length=20, default="Europe")
    deadline = models.DateTimeField()
    deadline_note = models.CharField(max_length=180, blank=True)
    source_name = models.CharField(max_length=120, blank=True)
    source_url = models.URLField(blank=True)
    source_verified_at = models.DateField(null=True, blank=True)
    summary = models.TextField()
    description = models.TextField()
    eligibility = models.JSONField(default=list)
    required_documents = models.JSONField(default=list)
    featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["deadline", "title"]

    def __str__(self):
        return self.title


class Application(models.Model):
    STATUS_CHOICES = [
        ("payment_required", "Payment required"),
        ("received", "Received"),
        ("reviewing", "Reviewing"),
        ("needs_info", "Needs information"),
        ("approved", "Approved"),
        ("rejected", "Not approved"),
    ]
    opportunity = models.ForeignKey(Opportunity, on_delete=models.PROTECT, related_name="applications")
    owner_open_id = models.CharField(max_length=120, blank=True, db_index=True)
    full_name = models.CharField(max_length=160)
    email = models.EmailField(db_index=True)
    phone = models.CharField(max_length=40, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    current_location = models.CharField(max_length=120, blank=True)
    education_level = models.CharField(max_length=120, blank=True)
    statement = models.TextField(blank=True)
    document_links = models.JSONField(default=list, blank=True)
    document_metadata = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="payment_required")
    consent_to_contact = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.opportunity.title}"


class ApplicationStatusEvent(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_events")
    status = models.CharField(max_length=30, choices=Application.STATUS_CHOICES)
    note = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.application_id} — {self.status}"


class SavedOpportunity(models.Model):
    email = models.EmailField(db_index=True)
    owner_open_id = models.CharField(max_length=120, blank=True, db_index=True)
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, related_name="saved_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["email", "opportunity"], name="unique_saved_opportunity")]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} — {self.opportunity.title}"


class StaffNotification(models.Model):
    EVENT_CHOICES = [
        ("application_submitted", "Application submitted"),
        ("application_status", "Application status changed"),
        ("payment_status", "Payment status changed"),
    ]
    event_type = models.CharField(max_length=40, choices=EVENT_CHOICES)
    title = models.CharField(max_length=180)
    message = models.TextField()
    application = models.ForeignKey("Application", on_delete=models.CASCADE, null=True, blank=True, related_name="staff_notifications")
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class PaymentRecord(models.Model):
    PROVIDER_CHOICES = [("momo", "MoMo"), ("airtel", "Airtel Money")]
    STATUS_CHOICES = [("pending", "Pending"), ("integration_pending", "Integration pending"), ("paid", "Paid"), ("failed", "Failed")]

    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="payment")
    amount = models.PositiveIntegerField(default=2000)
    currency = models.CharField(max_length=8, default="RWF")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="integration_pending")
    provider_reference = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id} — {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        previous_status = None
        if self.pk:
            previous_status = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
        super().save(*args, **kwargs)
        if previous_status and previous_status != self.status:
            StaffNotification.objects.create(event_type="payment_status", title="Payment status changed", message=f"Payment for {self.application.full_name} moved from {previous_status.replace('_', ' ')} to {self.status.replace('_', ' ')}.", application=self.application)
            from .email_notifications import notify_internal_payment_status
            notify_internal_payment_status(self.application, previous_status, self.status)


class Inquiry(models.Model):
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    topic = models.CharField(max_length=120, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    resolved = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.topic or 'General inquiry'}"


class SuccessStory(models.Model):
    """Only publish stories explicitly approved by the person featured."""
    name = models.CharField(max_length=120)
    destination = models.CharField(max_length=160)
    quote = models.TextField()
    consent_confirmed = models.BooleanField(default=False)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} — {self.destination}"


class GuestAccessToken(models.Model):
    PURPOSE_CHOICES = [
        ("status", "Status tracking"),
        ("claim", "Application claim"),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="guest_access_tokens")
    email = models.EmailField(db_index=True)
    token_hash = models.CharField(max_length=64, unique=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField(db_index=True)
    used_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=["application", "purpose", "expires_at"])]
        ordering = ["-created_at"]

    @property
    def is_valid(self):
        return self.used_at is None and self.expires_at > timezone.now()

    def __str__(self):
        return f"{self.application_id} — {self.purpose}"
