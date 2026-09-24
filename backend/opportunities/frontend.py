from django.utils.decorators import method_decorator
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.generic import TemplateView


@method_decorator(xframe_options_exempt, name="dispatch")
class FrontendView(TemplateView):
    """Public shell used by Namecheap masked forwarding.

    The exemption is deliberately scoped to this public page. API, admin, and
    authenticated application responses retain Django's clickjacking defense.
    """

    template_name = "frontend_index.html"
