from django.views.generic import TemplateView
from django.shortcuts import render


class HomePage(TemplateView):
    template_name = 'pages/about.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class RulesPage(TemplateView):
    template_name = 'pages/rules.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


def page_not_found(request, exception=None):
    return render(request, 'pages/404.html', {}, status=404)


def server_error(request):
    return render(request, 'pages/500.html', status=500)


def csrf_failure(request, reason="",
                 template_name="pages/403csrf.html", exception=None):
    return render(request, template_name, {"reason": reason}, status=403)
