from django.views.generic import TemplateView


class FrontendView(TemplateView):
    template_name = "frontend_index.html"
