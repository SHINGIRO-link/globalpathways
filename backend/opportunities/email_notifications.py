import logging

from django.conf import settings
from django.core.mail import send_mail

from .models import Application
from .guest_access import create_guest_access

logger = logging.getLogger(__name__)


def _send(subject: str, message: str, recipient: str) -> bool:
    if not recipient:
        logger.warning("Email notification skipped because recipient is empty: %s", subject)
        return False
    try:
        return bool(send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=False))
    except Exception:
        logger.exception("Email notification failed: %s", subject)
        return False


def notify_new_application(application: Application) -> bool:
    subject = f"New Global Pathways application: {application.full_name}"
    message = (
        f"{application.full_name} submitted an application for {application.opportunity.title}.\n\n"
        f"Applicant email: {application.email}\n"
        f"Current status: {application.get_status_display()}\n"
        "Review the application in the Global Pathways staff workspace."
    )
    internal_sent = _send(subject, message, settings.SMTP_STAFF_RECIPIENT)
    applicant_sent = notify_application_status(application, initial=True) if application.consent_to_contact else False
    return internal_sent or applicant_sent


def notify_internal_status(application: Application, previous_status: str | None = None) -> bool:
    subject = f"Application status update: {application.full_name}"
    previous = f" from {previous_status.replace('_', ' ')}" if previous_status else ""
    message = (
        f"{application.full_name}'s application for {application.opportunity.title} moved{previous} to {application.get_status_display()}.\n\n"
        f"Applicant email: {application.email}\n"
        "Review the application in the Global Pathways staff workspace."
    )
    return _send(subject, message, settings.SMTP_STAFF_RECIPIENT)


def notify_internal_payment_status(application: Application, previous_status: str, current_status: str) -> bool:
    subject = f"Payment status update: {application.full_name}"
    message = (
        f"Payment for {application.full_name}'s application to {application.opportunity.title} "
        f"moved from {previous_status.replace('_', ' ')} to {current_status.replace('_', ' ')}.\n\n"
        f"Applicant email: {application.email}\n"
        "Review the payment record in the Global Pathways staff workspace."
    )
    return _send(subject, message, settings.SMTP_STAFF_RECIPIENT)


def notify_guest_access(application: Application, base_url: str) -> bool:
    access = create_guest_access(application)
    root = base_url.rstrip("/")
    claim_link = f"{root}/guest/claim?token={access['claim_token']}"
    status_link = f"{root}/guest/status?token={access['status_token']}"
    subject = "Secure access to your Global Pathways application"
    message = (
        f"Hello {application.full_name},\n\n"
        f"We received your application for {application.opportunity.title}.\n\n"
        "You did not need to create an account to apply. You can use the private status link below immediately to check updates:\n\n"
        f"{status_link}\n\n"
        "If you later want a personal dashboard, use this optional link to sign in and claim this application:\n\n"
        f"{claim_link}\n\n"
        "No email verification is required. These links are private access links for this application.\n\n"
        "These links expire and should not be forwarded. Global Pathways will never ask for your password by email."
    )
    return _send(subject, message, application.email)


def notify_application_status(application: Application, initial: bool = False) -> bool:
    if not application.consent_to_contact:
        return False
    subject = f"Global Pathways application update: {application.get_status_display()}"
    greeting = f"Hello {application.full_name},\n\n"
    message = (
        greeting
        + ("We received your application" if initial else "Your application status has been updated")
        + f" for {application.opportunity.title}.\n\n"
        f"Current status: {application.get_status_display()}\n\n"
        "Our team will contact you with the next clear step."
    )
    return _send(subject, message, application.email)
