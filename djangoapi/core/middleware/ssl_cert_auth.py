from django.contrib.auth import login
from django.contrib.auth.models import User
from django.http import JsonResponse
import re  


class SSLCertificateMiddleware:
    ALLOWED_SERIALS = {
        '2499690112029': 'mcapelnik',
        '2457881512049': 'scapelnik',
        '1237907114027': 'scapelnik',
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"[SSL] VERIFY: {request.META.get('HTTP_X_SSL_CLIENT_VERIFY', 'NI')}")
        print(f"[SSL] SUBJECT_DN: {request.META.get('HTTP_X_SSL_CLIENT_SUBJECT_DN', 'NI')}")
        print(f"[SSL] USER: {request.user}")

        if request.user.is_authenticated:
            return self.get_response(request)

        verify = request.META.get('HTTP_X_SSL_CLIENT_VERIFY', '')
        dn = request.META.get('HTTP_X_SSL_CLIENT_SUBJECT_DN', '')
        serial = self.get_serial_from_dn(dn)  # ← sprememba

        print(f"[SSL] PARSED SERIAL: {serial}")  # debug

        if verify == 'SUCCESS' and serial in self.ALLOWED_SERIALS:
            username = self.ALLOWED_SERIALS[serial]
            try:
                user = User.objects.get(username=username)
                user.backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user)
                print(f"[SSL] Prijavljen: {username}")  # debug
            except User.DoesNotExist:
                pass

        return self.get_response(request)

    @staticmethod
    def get_serial_from_dn(dn):  # ← nova metoda
        match = re.search(r'serialNumber=(\d+)', dn)
        return match.group(1) if match else ''


# Debug view - začasno!
def debug_ssl_headers(request):
    headers = {k: v for k, v in request.META.items() if k.startswith('HTTP_')}
    ssl_info = {
        'ALL_HTTP_HEADERS': headers,
        'SSL_specific': {k: v for k, v in request.META.items() if 'SSL' in k}
    }
    return JsonResponse(ssl_info, json_dumps_params={'indent': 2})