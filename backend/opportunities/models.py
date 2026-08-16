from django.db import models


class Opportunity(models.Model):
    CATEGORY_CHOICES = [
        ("scholarship", "Scholarship"),
        ("visa", "Student Visa"),
        ("job", "Job"),
    ]
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
        ("received", "Received"),
        ("reviewing", "Reviewing"),
        ("needs_info", "Needs information"),
        ("submitted", "Submitted"),
    ]
    opportunity = models.ForeignKey(Opportunity, on_delete=models.PROTECT, related_name="applications")
    full_name = models.CharField(max_length=160)
    email = models.EmailField()
    phone = models.CharField(max_length=40, blank=True)
    nationality = models.CharField(max_length=80, blank=True)
    current_location = models.CharField(max_length=120, blank=True)
    education_level = models.CharField(max_length=120, blank=True)
    statement = models.TextField(blank=True)
    document_links = models.JSONField(default=list, blank=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default="received")
    consent_to_contact = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.full_name} — {self.opportunity.title}"


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
