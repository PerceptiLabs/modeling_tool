from django.urls import path, re_path
from django.views.generic import TemplateView
from django_http_exceptions import HTTPExceptions
import os

class TokenView(TemplateView):
    template_name = 'index.html'

    def dispatch(self, request, *args, **kwargs):
        token = request.GET.get("token") or os.getenv("PL_FILE_SERVING_TOKEN")
        ret = super().dispatch(request, *args, **kwargs)
        if token:
            ret.set_cookie("fileserver_token", value=token, samesite="Lax")
        return ret

urlpatterns = [
    re_path('', TokenView.as_view()),
]
