from django.http import HttpResponsePermanentRedirect

try:
    # Try built-in redirect model
    from django.contrib.redirects.models import Redirect
except ImportError:
    Redirect = None


class PageRedirectMiddleware:
    """
    Middleware that checks if the current request.path matches any Redirect.old_path
    and automatically redirects to Redirect.new_path.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only handle 404 responses
        if response.status_code != 404:
            return response

        if not Redirect:
            return response

        # Normalize path (remove querystring)
        path = request.path_info.rstrip("/")

        # Try exact match first
        redirect = Redirect.objects.filter(old_path=path).first()

        # Try with trailing slash (Django redirects often include one)
        if not redirect and not path.endswith("/"):
            redirect = Redirect.objects.filter(old_path=f"{path}/").first()

        if redirect:
            new_url = redirect.new_path
            # Preserve querystring if exists
            if request.META.get("QUERY_STRING"):
                new_url += f"?{request.META['QUERY_STRING']}"
            return HttpResponsePermanentRedirect(new_url)

        return response
