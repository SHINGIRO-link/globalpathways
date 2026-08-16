from django.db import models


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


class PaymentRecord(models.Model):
    PROVIDER_CHOICES = [("momo", "MoMo"), ("airtel", "Airtel Money")]
    STATUS_CHOICES = [("pending", "Pending"), ("integration_pending", "Integration pending"), ("paid", "Paid"), ("failed", "Failed")]

    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="payment")
    amount = models.PositiveIntegerField(default=2000)
    currency = models.CharField(max_length=8, default="TBD")
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="integration_pending")
    provider_reference = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.application_id} — {self.amount} {self.currency}"


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
