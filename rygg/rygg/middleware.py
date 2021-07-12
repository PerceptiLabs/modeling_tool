from rygg import settings
from django.http import HttpResponseBadRequest

def token_middleware(get_response):
    def check_token(request):
        if settings.DEBUG or settings.IS_CONTAINERIZED:
            return None

        passed_token = request.GET.get("token") or request.POST.get("token")

        if not passed_token:
            return HttpResponseBadRequest(f"Missing token parameter")
        if not passed_token == settings.API_TOKEN:
            return HttpResponseBadRequest(f"Token parameter is incorrect")


    def middleware(request):
        return check_token(request) or get_response(request)

    return middleware

